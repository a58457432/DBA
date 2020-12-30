/**
coding=utf-8
Creator: sjh
UpdateTime:2020.12.29
**/
package main

import (
    "fmt"
    "os/exec"
    "log"
    "io/ioutil"
    "syscall"
    "os"
    "strings"
    "bufio"
    "io"
)


type PGer struct {
    PGHOME  string
    PGDATA  string
    PGUSER  string
    PGPASSWD    string
    PGPROFILE   string
    PGINIT_CMD  string
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

func findstr(textfile string, search_str string)  (error,int){
    file, err := os.Open(textfile)
        if err != nil {
            fmt.Println(err)
            return err, 0
        }

    defer file.Close()

    count := 0
    reader := bufio.NewReader(file)
    for {
        line,_,end := reader.ReadLine()
        if end == io.EOF {
            break
        }
        str := string(line)
        if strings.Contains(str, search_str){
            count++
        }
    }
    return nil, count
}


/**
init_sys_postgresql
**/

func (pger *PGer) init_sys_pg(){
    if Exists(pger.PGDATA) {
        fmt.Println(pger.PGDATA + " exists !")
    }else{
        MKdir(pger.PGDATA)
    }

    groupadd_cmd :=  "groupadd " + pger.PGUSER
    useradd_cmd := "useradd -g " + pger.PGUSER + " " + pger.PGUSER
    chg_passwd_cmd := "echo " + pger.PGPASSWD + "  | passwd --stdin " + pger.PGUSER
    chg_data_dir := "chown -R " + pger.PGUSER + ":" + pger.PGUSER + "  " + pger.PGDATA
    chg_soft_dir := "chown -R " + pger.PGUSER + ":" + pger.PGUSER + "  " + pger.PGHOME
    
    _, res := runCmd(groupadd_cmd)
    if res == 0 {
        fmt.Printf("groupadd %s success\n", pger.PGUSER)
    }else {
        fmt.Printf("groupadd %s fail\n", pger.PGUSER)
    } 

    _, res1 := runCmd(useradd_cmd)
    if res1 == 0 {
        fmt.Printf("useradd %s success\n", pger.PGUSER)
    }else {
        fmt.Printf("useradd %s fail\n", pger.PGUSER)
    }

    _, res2 := runCmd(chg_passwd_cmd)
    if res2 == 0 {
        fmt.Printf("change %s passwd success\n", pger.PGUSER)
    }else {
        fmt.Printf("change %s passwd fail\n", pger.PGUSER)
    }

    _, res3 := runCmd(chg_data_dir)
    if res3 == 0 {
        fmt.Printf("chown %s  success\n", pger.PGDATA)
    }else {
        fmt.Printf("chown %s  fail\n", pger.PGDATA)
    }

    _, res4 := runCmd(chg_soft_dir)
    if res4 == 0 {
        fmt.Printf("chown %s success\n", pger.PGHOME)
    }else {
        fmt.Printf("chown %s fail\n", pger.PGHOME)
    }

}

/**
write profile files
**/

func (pger *PGer) write_pro_file(){
    pro_file := pger.PGPROFILE
    pro_filed := `/etc/profile`
    pro_file_cmd := ". " + pro_file
    
    pro_new1 := "export PGHOME=" + pger.PGHOME
    pro_new2 := "export PGDATA=" + pger.PGDATA
    pro_new3 := "export PATH=$PGHOME/bin:$PATH"
    pro_new4 := "export LD_LIBRARY_PATH=$PGHOME/lib:$LD_LIBRARY_PATH"

    _, num := findstr(pro_file, "PGHOME")
    _, num1 := findstr(pro_file, "PGDATA")

    if (num > 0 || num1 > 0) {
        fmt.Println("ProFile: PGHOME or PGDATA exists !")
    }else {
        file2, _ := os.OpenFile(pro_filed, os.O_WRONLY|os.O_APPEND, 0666)
        _, _ = file2.Write([]byte("\n" + pro_new1))
        _, _ = file2.Write([]byte("\n" + pro_new2))
        _, _ = file2.Write([]byte("\n" + pro_new3))
        _, _ = file2.Write([]byte("\n" + pro_new4))

    }

//    file, err := os.Open(pro_file)
//    if err != nil {
//        fmt.Println("file open fail ", err)
//    }

//    defer file.Close()
//    content, _ := ioutil.ReadAll(file)
//    fmt.Println(string(content))

    fmt.Println(pro_file_cmd)
    _, res := runCmd(pro_file_cmd)

    if res == 0 {
        fmt.Println("source " + pro_file + " success !")
    }else {
        fmt.Println("source " + pro_file + "fail !")
    }
}

//init pg
func (pger *PGer) init_pg(){
    dirname := pger.PGDATA
    init_pg_cmd := "su postgres -c " + "'" + pger.PGINIT_CMD + " -D " + pger.PGDATA + "'"
    dir, _ := ioutil.ReadDir(dirname)
    if len(dir) == 0 {
        fmt.Println(dirname + " is empty dir! , can init it !")
        _, res := runCmd(init_pg_cmd)
        if res == 0 {
            fmt.Println("init pg file success !")
        } else {
            fmt.Println("init pg file fail !")
        }
    } else {
        fmt.Println(dirname + " is not empty dir, please delete it !")
    }
}

// update postgresql.conf
func (pger *PGer) update_pg_conf(){

}

// start pg
func (pger *PGer) start_pg_server(){

}
// stop pg
func (pger *PGer) stop_pg_server(){

}

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
        PGPASSWD :  "postgres",
        PGPROFILE : "/etc/profile",
        PGINIT_CMD : "/usr/local/pgsql/bin/initdb",
    }

//    myPGer.init_sys_pg()
//    myPGer.write_pro_file()
    myPGer.init_pg()
}

