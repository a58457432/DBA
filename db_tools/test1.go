package main

import (
	"fmt"
    "bufio"
    "io"
    "os"
    "strings"
)

// read kv conf
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
    config["shared_buffers"] = "1G"
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



func main() {
//    config := InitConfig("/tmp/postgresql.conf")

    config := CreateFile("/opt/1.sql")
    fmt.Println(config)



//    fmt.Println("ip=" + string(ip)," port=" + string(port), " name=" + string(name), " new2=" + string(new02))

}
