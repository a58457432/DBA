package main

import (
	"fmt"
)

func f1(args ...string){
    for _, v := range args {
        fmt.Println(v)
    }

    fmt.Println("********************")
    fmt.Println(args[0])
    fmt.Println(len(args))
}


func main(){
    f1("ls")
    f1("ls","-al")
}
