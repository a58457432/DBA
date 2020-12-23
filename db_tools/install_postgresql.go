package main

import (
    "fmt"
    "os/exec"
    "log"
    "io/ioutil"
    "syscall"
    "os"
)


type PGer struct {
    PGHOME  string
    PGDATA  string
    PGUSER  string
//    PATH    string
//    LANG    string
//    DATE    string
//    LD_LIBRARY_PATH string
}

func runCmd(cmdStr string) (string, int) {
    cmd := exec.Command("sh","-c",cmdStr)
    stdout, _ := cmd.StdoutPipe()
    defer stdout.Close()
    if err := cmd.Start(); err != nil {
        log.Fatalf("cmd.Start: %v")
    }
    result, _ := ioutil.ReadAll(stdout)
    resdata := string(result)
    var res int
    if err := cmd.Wait(); err != nil {
        if ex, ok := err.(*exec.ExitError); ok {
            fmt.Println("cmd exit status")
            res = ex.Sys().(syscall.WaitStatus).ExitStatus()
        }
    }
    return resdata, res
}


func Exists(path string) bool {
    _, err := os.Stat(path)
    if err != nil {
        if os.IsExist(err){
            return true
        }
        return false
    }
    return true
}

func MKdir(path string) {
    err := os.MkdirAll(path, os.ModePerm)
    if err != nil {
        fmt.Println(err)
    }
}


/**
init_sys_postgresql
**/

func (pger *PGer) init_sys_pg(){
    if Exists(pger.PGDATA) {
        fmt.Println(pger.PGDATA + "exists !")
    }else{
        MKdir(pger.PGDATA)
    }

    groupadd_cmd :=  "groupadd " + pger.PGUSER
    useradd_cmd := "useradd -g " + pger.PGUSER + " " + pger.PGUSER
    fmt.Println(groupadd_cmd)
    fmt.Println(useradd_cmd)

}

/**
su - postgres
**/




func main() {
//    resdata, res := runCmd("date +%Y-%m-%d") 
//    fmt.Println(res)
//    fmt.Println(resdata)
//    flag := Exists("/usr/local/webserver/DBA/db_tools/hello")
//    fmt.Println(flag)
//    MKdir("/data/postgresql/data") 
    
    myPGer := &PGer{
        PGHOME : "/usr/local/pgsql",
        PGDATA : "/data/postgresql/data",
        PGUSER : "postgres",
    }

    myPGer.init_sys_pg()
}

