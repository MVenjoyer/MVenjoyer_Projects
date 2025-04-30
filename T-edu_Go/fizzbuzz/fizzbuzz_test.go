package fizzbuzz

import (
	"testing"
)

func TestFizzBuzz(t *testing.T) {
	type args struct {
		i int
	}
	type test struct {
		name string
		args args
		want string
	}

	tests := []test{
		{
			"case: 7",
			args{i: 7},
			"7",
		},
		{
			"case: Fizz",
			args{i: 27},
			"Fizz",
		},
		{
			"case: Buzz",
			args{i: 100},
			"Buzz",
		},
		{
			"case: FizzBuzz",
			args{i: 120},
			"FizzBuzz",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := FizzBuzz(tt.args.i); got != tt.want {
				t.Errorf("FizzBuzz(%d) = %v, want %v", tt.args.i, got, tt.want)
			}
		})
	}
}
