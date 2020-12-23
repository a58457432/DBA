package main

import (
	"fmt"
)

type Person struct {
    name string
    age int
}

func (person *Person) showInfo() {
    fmt.Printf("My name is %s, age is %d", person.name, person.age)
}

func (person *Person) setAge(age int) {
    person.age = age
}

type Student struct {
    Person
    id int
    score int
}

func (student *Student) showInfo(){
    fmt.Println("I am a student ...")
}

func (student *Student) read(){
    fmt.Println("read booK")
}


func main(){
    person := Person{"mike", 18}
    person.showInfo()
    person.setAge(20)
    fmt.Println("\n")
    fmt.Println(person)

    student := Student{Person{"jake",16}, 1001, 99}
    student.showInfo()
    student.setAge(22)
    student.read()
    fmt.Printf("%T\n",student)
    fmt.Println(student.id) 

}
