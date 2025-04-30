package fizzbuzz

import "strconv"

func FizzBuzz(a int) string {
	switch {
	case a%15 == 0:
		return "FizzBuzz"
	case a%3 == 0:
		return "Fizz"
	case a%5 == 0:
		return "Buzz"
	default:
		return strconv.Itoa(a)
	}
}
