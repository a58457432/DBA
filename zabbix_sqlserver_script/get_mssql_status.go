package main

import (
    "database/sql"
    "fmt"
    "strings"
)

import (
    _ "github.com/mattn/go-adodb"
)

type Mssql struct {
    *sql.DB
    dataSource  string
    database    string
    windows     bool
    sa          SA
}

type SA struct {
    user    string
    passwd  string
    port    int
}

func (m *Mssql) Open() (err error) {
    var conf []string
    conf = append(conf, "Provider=SQLOLEDB")
    conf = append(conf, "Data Source=" + m.dataSource)
    conf = append(conf, "Initial Catalog=" + m.sa.user)
    conf = append(conf, "password=" + m.sa.passwd)
    conf = append(conf, "port" + fmt.Sprint(m.sa.port))

    m.DB, err = sql.Open("adodb", strings.Join(conf, ";"))
    if err != nil {
        return err
    }

    return nil
}


func main(){
    db := Mssql{
        dataSource: "172.21.107.4\\OA-DB01",
        database:   "admin",
        windows: false,
        sa: SA{
            user: "db_reader",
            passwd: "vHmWDCzi6iXCW3jC",
            port:   1433,
        },
    }

    fmt.Println(db)

    err := db.Open()
    if err != nil {
        fmt.Println("sql open:", err)
        return
    }
    defer db.Close()

    rows, err := db.Query("select 1*10;")
    if err != nil {
        fmt.Println("query: ", err)
        return
    }
    
    for rows.Next(){
        var num int
        rows.Scan(&num)
        fmt.Printf("number: %d\n", num)
    }
}



