package main

import (
    "fmt"
//    "os"
    "os/exec"
    "log"
    "bytes"
)

func main() {
    cmd := exec.Command("touch", "/opt/3.sql")
    var stdin, stdout, stderr bytes.Buffer
    cmd.Stdout = &stdout
    cmd.Stderr = &stderr
    cmd.Stdin = &stdin
    err := cmd.Run()
    if err != nil {
        log.Fatalf("cmd.Run() failed with %s\n", err)
    }

    outStr, errStr, inStr := string(stdout.Bytes()), string(stderr.Bytes()), string(stdin.Bytes())
    fmt.Printf("out:\n%s\nerr:\n%s\n", outStr, errStr)
    fmt.Printf("in:\n%s",inStr)
}

