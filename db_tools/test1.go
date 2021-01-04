package main

import (
    "os"
    "io/ioutil"
    "path"
)


func main(){
    dir, err := ioutil.ReadDir("/data/postgresql/data")
    if err != nil {
        panic(err)
    }
    for _, d := range dir {
        os.RemoveAll(path.Join([]string{"/data/postgresql/data", d.Name()}...))
    }


}
