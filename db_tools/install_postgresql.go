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
    "path"
)


type PGer struct {
    PGHOME  string
    PGDATA  string
    PGUSER  string
    PGPASSWD    string
    PGPROFILE   string
    PGINIT_CMD  string
    PGCTL_CMD   string
    PG_CONFIG   string
    PGHBA_CONFIG    string
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


func InitConfig(path string) map[string]string {
    config := make(map[string]string)

    f, err := os.Open(path)
    defer f.Close()
    if err != nil {
        panic(err)
    }

    r := bufio.NewReader(f)
    for {
        b, _, err := r.ReadLine()
        if err != nil {
            if err == io.EOF {
                break        
            }
            panic(err)
        }
        s := strings.TrimSpace(string(b))
        index := strings.Index(s, "=")
        if index < 0 {
            continue
        }
        key := strings.TrimSpace(s[:index])
        if len(key) == 0 {
            continue
        }
        value := strings.TrimSpace(s[index+1:])
        if len(value) == 0 {
            continue
        }
        config[key] = value
    }
    return config
}

func CreateFile(path string) map[string]string {
    config := make(map[string]string)
    config["listen_addresses"] = "'*'"
    config["port"] = "5432"
    config["max_connections"] = "5000"
    config["shared_buffers"] = "1GB"
    config["log_timezone"] = "'Asia/Shanghai'"
    config["datestyle"] = "'iso, mdy'"
    config["timezone"] = "'Asia/Shanghai'"
    config["default_text_search_config"] = "'pg_catalog.english'"

    file, err := os.Create(path)
    if err != nil {
        fmt.Println(" pg.confg file create fail", err)
    }
    defer file.Close()
    for k, v := range config {
        _, _ = file.WriteString(k + "=" + v + "\n")
    }
    return config
}

func AppendFile(path string, istr string) {
    file, _ := os.OpenFile(path, os.O_WRONLY | os.O_APPEND, 0666)
    defer file.Close()
    _, _ = file.Write([]byte(istr))
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

// update postgresql.conf && append pg_hba.conf
func (pger *PGer) update_pg_conf(){
    pg_config := pger.PGDATA + pger.PG_CONFIG
    pg_hba_config := pger.PGDATA + pger.PGHBA_CONFIG 
    config := CreateFile(pg_config)
    if config != nil {
        fmt.Println("create pg.conf success!")
    }
    istr := "\nhost   all     all     0.0.0.0/0   trust"
    _, num := findstr(pg_hba_config, istr[24:31])
    if num > 0 {
        fmt.Println("pg_hba_config Policy already exists!")
    } else {
        AppendFile(pg_hba_config, istr)         
        fmt.Println("pg_hba_config append success!")
    }
}

// start pg
func (pger *PGer) start_pg_server(){
    os.Chdir(pger.PGDATA)
    pg_ctl_cmd := "su postgres -c " + "'" + pger.PGCTL_CMD + " -D " + pger.PGDATA + " -l pg_startup.log start"  +"'"
    _, res := runCmd(pg_ctl_cmd)
    if res == 0 {
        fmt.Println("start pg server success\n")
    }else {
        fmt.Println("start pg server  fail\n")
    }
    
}
// stop pg
func (pger *PGer) stop_pg_server(){
    os.Chdir(pger.PGDATA)
    pg_ctl_cmd := "su postgres -c " + "'" + pger.PGCTL_CMD + " -D " + pger.PGDATA + " -l pg_stop.log stop"  +"'"
    _, res := runCmd(pg_ctl_cmd)
    if res == 0 {
        fmt.Println("stop pg server success\n")
    }else {
        fmt.Println("stop pg server  fail\n")
    }

}

// delete pg file
func (pger *PGer) delete_file(){
    dir, err := ioutil.ReadDir(pger.PGDATA)
    if err != nil {
        panic(err)
    }
    for _, d := range dir {
        os.RemoveAll(path.Join([]string{pger.PGDATA, d.Name()}...))
    }

    fmt.Println("clean postgresql file!")
}


func main() {
    myPGer := &PGer{
        PGHOME : "/usr/local/pgsql",
        PGDATA : "/data/postgresql/data",
        PGUSER : "postgres",
        PGPASSWD :  "postgres",
        PGPROFILE : "/etc/profile",
        PGINIT_CMD : "/usr/local/pgsql/bin/initdb",
        PGCTL_CMD   :   "/usr/local/pgsql/bin/pg_ctl",
        PG_CONFIG   :   "/postgresql.conf",
        PGHBA_CONFIG    :   "/pg_hba.conf",
    }

    finger := os.Args[1]
    switch finger {
    case "start":
        myPGer.start_pg_server()
    case "stop":
        myPGer.stop_pg_server() 
    case "init":
        myPGer.init_sys_pg()
        myPGer.write_pro_file()
        myPGer.init_pg()
        myPGer.update_pg_conf()
        myPGer.start_pg_server()
    case "reInit":
        myPGer.stop_pg_server()
        myPGer.delete_file()
        myPGer.init_sys_pg()
        myPGer.write_pro_file()
        myPGer.init_pg()
        myPGer.update_pg_conf()
        myPGer.start_pg_server()
    case "Uninstall":
        myPGer.stop_pg_server()
        myPGer.delete_file()

    case "help":
        fmt.Println("install_postgresql.go is a tool for postgresql server.\n\n   Usage: install_postgresql.go <command>\n\nThe commands are:\n")
        fmt.Println("       init        init system enverionment and install postgresql")
        fmt.Println("       reInit      reinstall postgresql")
        fmt.Println("       start       start postgresql server ")
        fmt.Println("       stop        stop postgresql server")
        fmt.Println("       Uninstall   uninstall postgresql")
        fmt.Println("eg:    go run install_postgresql.go init")
    
    }
}

