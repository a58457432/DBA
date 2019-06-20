package main

import (
	"fmt"
)

func main(){
    slice := make([]int, 1e6)
    slice = foo(slice)

    func foo(slice []int) []int {
        fmt.Println(slice)    
        return slice
    }


	fmt.Println(slice)
}
