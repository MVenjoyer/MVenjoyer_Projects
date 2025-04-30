package main

import (
	"errors"
	"flag"
	"fmt"
	"io"
	"math"
	"os"
	"strings"
)

type Reader interface {
	Read([]byte) (int, error)
	ReadAt([]byte, int64) (int, error)
	Close() error
}

func NewReader(filename string) (Reader, error) {
	if filename == "stdin" {
		return os.Stdin, nil
	}
	_, err := os.Stat(filename)
	if err != nil {
		return nil, fmt.Errorf("error: file does not exist %s", filename)
	}
	file, err := os.Open(filename)
	if err != nil {
		return nil, fmt.Errorf("error: can not open file '%s'", filename)
	}
	return file, err
}

type Writer interface {
	Write([]byte) (int, error)
	Close() error
}

func NewWriter(filename string) (Writer, error) {
	if filename == "stdout" {
		return os.Stdout, nil
	}
	_, err := os.Stat(filename)
	if err == nil {
		return nil, fmt.Errorf("error: file allready exist %s", filename)
	}
	file, err := os.Create(filename)
	if err != nil {
		return nil, fmt.Errorf("error: can not create file '%s'", filename)
	}
	return file, err
}

type Options struct {
	From      string
	To        string
	Offset    int64
	Limit     int64
	BlockSize int64
	Conv      []string
}

func isValidConvString(conv string) bool {
	operations := strings.Split(conv, ",")
	isValid := map[string]bool{
		"upper_case":  false,
		"lower_case":  false,
		"trim_spaces": false,
	}

	var hasUpper, hasLower bool

	for _, op := range operations {
		trimmed := strings.TrimSpace(op)
		if trimmed == "" {
			continue
		}
		if _, exists := isValid[trimmed]; !exists {
			return false
		}
		if trimmed == "upper_case" {
			hasUpper = true
		}
		if trimmed == "lower_case" {
			hasLower = true
		}
	}

	if hasUpper && hasLower {
		return false
	}

	return true
}

func ParseFlags() (*Options, error) {
	var opts Options
	var conv string
	flag.StringVar(&opts.From, "from", "stdin", "file to read. by default - stdin")
	flag.StringVar(&opts.To, "to", "stdout", "file to write. by default - stdout")
	flag.Int64Var(&opts.Offset, "offset", 0, "starting point of reading. by default - 0")
	flag.Int64Var(&opts.Limit, "limit", math.MaxInt64, "limit of reading. by default - 0")
	flag.Int64Var(&opts.BlockSize, "block-size", 128,
		"amount of bytes to read/write at once. by default - 128")
	flag.StringVar(&conv, "conv", "", "operations to perform on input data, no operations by default")
	flag.Parse()
	if !isValidConvString(conv) {
		return nil, errors.New("error: invalid conv string")
	}
	opts.Conv = strings.Split(conv, ",")
	if opts.Offset < 0 {
		return nil, fmt.Errorf("error: invalid offset(must be >= 0, got '%d') ", opts.Offset)
	}
	return &opts, nil
}

func handleConv(in []byte, conv []string) []byte {
	answer := string(in)
	for _, el := range conv {
		switch el {
		case "upper_case":
			answer = strings.ToUpper(answer)
		case "lower_case":
			answer = strings.ToLower(answer)
		case "trim_spaces":
			answer = strings.TrimSpace(answer)
		}
	}
	return []byte(answer)
}

func handleErrors(err error, s string) {
	if err != nil {
		if err.Error() != "EOF" {
			fmt.Fprintln(os.Stderr, s, err)
			os.Exit(1)
		}
	}
}

func main() {
	opts, err := ParseFlags()
	handleErrors(err, "error: Parsing flags error")
	fileReader, err := NewReader(opts.From)
	handleErrors(err, "error: Creating reader error")
	_, err = io.CopyN(io.Discard, fileReader, opts.Offset)
	if err != nil {
		fmt.Fprintln(os.Stderr, "error: offset is bigger, than input file size", err)
		os.Exit(1)
	}
	reader := io.LimitReader(fileReader, opts.Limit)
	handleErrors(err, "error: could not create reader")
	writer, err := NewWriter(opts.To)
	handleErrors(err, "error: could not create writer")
	inBuffer := make([]byte, opts.BlockSize)
	outBuffer := make([]byte, 0)
	n := 0
	for {
		n, err = reader.Read(inBuffer)
		handleErrors(err, fmt.Sprintf("error: could not read file %s", opts.From))

		if n == 0 {
			break
		}
		if int64(n) < opts.BlockSize {
			outBuffer = append(outBuffer, inBuffer[:n]...)
		} else {
			outBuffer = append(outBuffer, inBuffer...)
		}
	}
	outBuffer = handleConv(outBuffer, opts.Conv)
	var l int64
	r := opts.BlockSize
	for r+opts.BlockSize <= int64(len(outBuffer)) {
		_, err = writer.Write(outBuffer[l:r])
		handleErrors(err, fmt.Sprintf("error: could not write to file '%s'", opts.To))
		l += opts.BlockSize
		r += opts.BlockSize
	}
	_, err = writer.Write(outBuffer[l:])
	handleErrors(err, fmt.Sprintf("error: could not write to file '%s'", opts.To))
	err = writer.Close()
	handleErrors(err, "error: could not close writer")
	err = fileReader.Close()
	handleErrors(err, "error: could not close reader")
}
