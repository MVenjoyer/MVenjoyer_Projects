package homework

import (
	"encoding/json"
	"errors"
	"fmt"
	"reflect"
	"strconv"
	"strings"
)

var (
	ErrNotStruct                   = errors.New("wrong argument given, should be a struct")
	ErrInvalidValidatorSyntax      = errors.New("invalid validator syntax")
	ErrValidateForUnexportedFields = errors.New("validation for unexported field is not allowed")
	ErrLenValidationFailed         = errors.New("len validation failed")
	ErrInValidationFailed          = errors.New("in validation failed")
	ErrMaxValidationFailed         = errors.New("max validation failed")
	ErrMinValidationFailed         = errors.New("min validation failed")
)

type ValidationError struct {
	field string
	err   error
}

func NewValidationError(err error, field string) error {
	return &ValidationError{
		field: field,
		err:   err,
	}
}

func (e *ValidationError) Error() string {
	return fmt.Sprintf("%s: %s", e.field, e.err)
}

func (e *ValidationError) Unwrap() error {
	return e.err
}

func Validate(v any) error {
	t := reflect.TypeOf(v)
	value := reflect.ValueOf(v)
	if t.Kind() != reflect.Struct {
		return ErrNotStruct
	}
	zeroFields := 0
	var errs []error
	for i := 0; i < t.NumField(); i++ {
		field := t.Field(i)
		fieldValue := value.Field(i)
		tag := field.Tag.Get("validate")
		if tag == "" {
			continue
		}
		if fieldValue.IsZero() {
			zeroFields++
		}
		err := startValidation(tag, fieldValue)
		if err != nil {
			errs = append(errs, NewValidationError(err, field.Name))
		}
	}
	if zeroFields == t.NumField() && zeroFields != 0 {
		errs = append(errs, ErrValidateForUnexportedFields)
	}
	if len(errs) == 0 {
		return nil
	}
	return errors.Join(errs...)
}

func startValidation(tag string, field reflect.Value) error {
	ops := strings.Split(tag, ":")
	switch ops[0] {
	case "len":
		if length, err := strconv.Atoi(ops[1]); err == nil && length >= 0 {
			return lenValidator(field, length)
		}
		return ErrInvalidValidatorSyntax
	case "in":
		return inValidator(field, ops[1])
	case "min":
		if length, err := strconv.Atoi(ops[1]); err == nil {
			return minValidator(field, length)
		}
		return ErrInvalidValidatorSyntax
	case "max":
		if length, err := strconv.Atoi(ops[1]); err == nil {
			return maxValidator(field, length)
		}
		return ErrInvalidValidatorSyntax
	default:
		return ErrInvalidValidatorSyntax
	}
}

func maxValidator(v reflect.Value, length int) error {
	if sizableField(v.Kind()) && v.Len() <= length || v.Kind() == reflect.Int && v.Int() <= int64(length) {
		return nil
	}
	return ErrMaxValidationFailed
}

func minValidator(v reflect.Value, length int) error {
	if sizableField(v.Kind()) && v.Len() >= length || v.Kind() == reflect.Int && v.Int() >= int64(length) {
		return nil
	}

	return ErrMinValidationFailed
}

func inValidator(v reflect.Value, seq string) error {
	if seq == "" {
		return ErrInvalidValidatorSyntax
	}
	if v.Kind() == reflect.Slice {
		tag := "in:" + seq
		for i := 0; i < v.Len(); i++ {
			err := startValidation(tag, v.Index(i))
			if err != nil {
				return err
			}
		}
		return nil
	} else if v.Kind() == reflect.String {
		return contains(strings.Split(seq, ","), v.String())
	}
	jsonStr := "[" + seq + "]"
	var result []int64
	err := json.Unmarshal([]byte(jsonStr), &result)
	if err != nil {
		return ErrInValidationFailed
	}
	return contains(result, v.Int())
}

type Requirements interface {
	string | int | int64
}

func contains[T Requirements](arr []T, v T) error {
	for _, a := range arr {
		if a == v {
			return nil
		}
	}
	return ErrInValidationFailed
}

func sizableField(k reflect.Kind) bool {
	return k == reflect.String ||
		k == reflect.Slice ||
		k == reflect.Map ||
		k == reflect.Array ||
		k == reflect.Chan
}

func lenValidator(v reflect.Value, length int) error {
	if sizableField(v.Kind()) && v.Len() == length {
		return nil
	}
	return ErrLenValidationFailed
}
