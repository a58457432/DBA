package main

import (
	"fmt"
    "os"
    "io/ioutil"
    "strings"
//    "log"
    "bufio"
    "io"
)


func write() string{
    itfile := "/opt/1.sql"
    itfiled := `/opt/1.sql`

    file2, _ := os.OpenFile(itfiled, os.O_WRONLY|os.O_APPEND, 0666)
    new1 := "this new messages, old news still on"
    new2 := "bbbbbb"
    new3 := "CCCCCCCCCC"

    _, _ = file2.Write([]byte("\n" + new1))
    _, _ = file2.Write([]byte("\n" + new2))
    _, _ = file2.Write([]byte("\n" + new3))

    file, err := os.Open(itfile)
    if err != nil {
        fmt.Println("file open fail ", err)
    }

    defer file.Close()
    content, _ := ioutil.ReadAll(file)
    fmt.Println(string(content))

    return ""

}


func findstr(textfile string, search_str string)  (error,int){
    file, err := os.Open(textfile)
    if err != nil {
//        log.Printf("Cannot open text file: %s, err: [%v]", textfile, err)
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
    fmt.Println("一共有", count, "个oceanstar")
    return nil, count
}

func main() {

//     t1 := write()    
//     fmt.Println(t1)
    _, num := findstr("/opt/1.sql","oceanstar")
    fmt.Println(num)

}
