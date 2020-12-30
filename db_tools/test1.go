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



func main() {
    config := InitConfig("/data/postgresql/data/postgresql.conf")
//    ip := config["ip"]
//    port := config["port"]
//    name := config["name"]
//    new02 := config["new02"]

    fmt.Println(config)

//    fmt.Println("ip=" + string(ip)," port=" + string(port), " name=" + string(name), " new2=" + string(new02))

}
