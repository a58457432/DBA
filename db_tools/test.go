package main

import (
	"fmt"
)

type SliceInt []int

func (s SliceInt) Sum() int {
    sum := 0
    for _, i := range s {
        sum += i
    }
    return sum
}

func SliceInt_Sum(s SliceInt) int {
    sum := 0
    for _, i := range s {
        sum += i
    }
    return sum
}

func main(){

    var s SliceInt = []int{1, 2, 3, 4}
    fmt.Println(s.Sum())

    fmt.Println(SliceInt_Sum(s))

}
