package main

import (
    "fmt"
//    "os"
    "os/exec"
    "log"
    "io/ioutil"
    "syscall"
)

func main() {
        cmd := exec.Command("ls" ,"-al")  //不加第一个第二个参数会报错
                     
        stdout, _ := cmd.StdoutPipe()   //创建输出管道
        defer stdout.Close()
        if err := cmd.Start(); err != nil {
            log.Fatalf("cmd.Start: %v")
        }
                                             
//        fmt.Println(cmd.Args) //查看当前执行命令
                                                 
//        cmdPid := cmd.Process.Pid //查看命令pid
//        fmt.Println(cmdPid)
                                                         
        result, _ := ioutil.ReadAll(stdout) // 读取输出结果
        resdata := string(result)
        fmt.Println(resdata)
                                                                     
        var res int
        if err := cmd.Wait(); err != nil {
            if ex, ok := err.(*exec.ExitError); ok {
                fmt.Println("cmd exit status")
                res = ex.Sys().(syscall.WaitStatus).ExitStatus() //获取命令执行返回状态，相当于shell: echo $?
            }
        }
                                                                                                                         
        fmt.Println(res)
}

