package main

import (
	"fmt"
	"io/ioutil"
	"os"
	"strconv"
	"strings"
)

// Transform turns the Oxy format of classes into the RPI format

func main() {
	semestersFile, err := os.OpenFile("semesters.json", os.O_APPEND|os.O_RDWR, os.ModeAppend)
	if err != nil {
		panic("Could not read semesters.json: " + err.Error())
	}
	defer semestersFile.Close()

	oxySemesters, err := ioutil.ReadAll(semestersFile)
	if err != nil {
		panic("Error reading from semesters: " + err.Error())
	}

	var rpiFormatSemesters string

	for _, semester := range strings.Split(string(oxySemesters), "\n") {
		// Skip blank lines
		if len(semester) == 0 {
			continue
		}

		year, err := strconv.Atoi(semester[:4])
		if err != nil {
			panic(fmt.Errorf("Error converting %v to int: %v", semester[:4], err))
		}

		// The last two digits determine what kind of semester it is
		semCode := semester[len(semester)-2:]
		switch semCode {
		case "01": // Fall
			rpiFormatSemesters += strconv.Itoa(year-1) + "09"
		case "02": // Spring
			rpiFormatSemesters += strconv.Itoa(year) + "01"
		case "03": // Summer
			rpiFormatSemesters += strconv.Itoa(year) + "05"
		}

		rpiFormatSemesters += "\n"
	}

	// Write the data back into the file
	semestersFile.Truncate(0)
	_, err = semestersFile.Seek(0, 0)
	if err != nil {
		panic("Error seeking to end of file: " + err.Error())
	}
	fmt.Println(rpiFormatSemesters)
	_, err = semestersFile.WriteString(rpiFormatSemesters)
	if err != nil {
		panic("Error writing to file: " + err.Error())
	}
}
