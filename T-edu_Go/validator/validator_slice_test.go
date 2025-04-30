package homework

import (
	"errors"
	"slices"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestValidateSlice(t *testing.T) {
	type args struct {
		v any
	}
	tests := []struct {
		name     string
		args     args
		wantErr  bool
		checkErr func(err error) bool
	}{
		{
			name: "valid struct with tagged fields(custom)",
			args: args{
				v: struct {
					SliceInt1 []int    `validate:"len:2"`
					SliceInt2 []int    `validate:"min:1"`
					SliceInt3 []int    `validate:"max:3"`
					SliceInt4 []int    `validate:"in:1,2,3"`
					SliceStr5 []string `validate:"in:str,foo,bar"`
				}{
					SliceInt1: []int{1, 2},
					SliceInt2: []int{1},
					SliceInt3: []int{1, 2, 3},
					SliceInt4: []int{1, 2},
					SliceStr5: []string{"str", "foo"},
				},
			},
			wantErr: false,
		},
		{
			name: "invalid slice(custom)",
			args: args{
				v: struct {
					SliceInt1 []int    `validate:"len:2"`
					SliceInt2 []int    `validate:"min:2"`
					SliceInt3 []int    `validate:"max:1"`
					SliceInt4 []int    `validate:"in:1,2,3"`
					SliceStr5 []string `validate:"in:1"`
				}{
					SliceInt1: []int{1, 2, 3},
					SliceInt2: []int{1},
					SliceInt3: []int{4, 5, 6},
					SliceInt4: []int{4},
					SliceStr5: []string{"10"},
				},
			},
			wantErr: true,
			checkErr: func(err error) bool {
				expectedErrors := []struct {
					err   error
					field string
				}{
					{
						err:   ErrLenValidationFailed,
						field: "SliceInt1",
					},
					{
						err:   ErrMinValidationFailed,
						field: "SliceInt2",
					},
					{
						err:   ErrMaxValidationFailed,
						field: "SliceInt3",
					},
					{
						err:   ErrInValidationFailed,
						field: "SliceInt4",
					},
					{
						err:   ErrInValidationFailed,
						field: "SliceStr5",
					},
				}

				if _, ok := err.(interface{ Unwrap() []error }); !ok {
					assert.Fail(t, "err should be created with errors.Join(err...) function")
					return false
				}

				errorsCollection, ok := err.(interface{ Unwrap() []error })
				if !ok {
					assert.Fail(t, "err should be created with errors.Join(err...) function")
					return false
				}
				errs := errorsCollection.Unwrap()

				assert.Len(t, errs, 5)

				foundErrors := expectedErrors
				for i := range errs {
					actualErr := &ValidationError{}
					if errors.As(errs[i], &actualErr) {
						for ei := range expectedErrors {
							if errors.Is(actualErr, expectedErrors[ei].err) && actualErr.field == expectedErrors[ei].field {
								foundErrors = slices.Delete(foundErrors, ei, ei+1)
							}
						}
					}
				}

				assert.Empty(t, foundErrors, "unexpected errors found")
				return true
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := Validate(tt.args.v)
			if tt.wantErr {
				assert.Error(t, err)
				assert.True(t, tt.checkErr(err), "test expect an error, but got wrong error type")
			} else {
				assert.NoError(t, err)
			}
		})
	}
}
