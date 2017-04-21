package main

import (
	"archive/zip"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"path"
	"path/filepath"
	"strings"
)

//CompressConfig ..
type CompressConfig struct {
	BackupPath string `json:"bkpath"`
	LuaPath    string `json:"luapath"`
	RarPath    string `json:"rarpath"`
}

func (c *CompressConfig) String() (str string) {
	return fmt.Sprintf(`
    BackupPath : %s
    LuaPath: %s
    RarPath: %s
    `, c.BackupPath, c.LuaPath, c.RarPath)
}

//LoadConfig 加载配置信息
func LoadConfig(c *CompressConfig) {
	cf, err := os.Open("./config.json")
	if err != nil {
		log.Fatalln(err.Error())
	}
	defer cf.Close()

	configDecoder := json.NewDecoder(cf)
	err = configDecoder.Decode(c)
	if err != nil {
		log.Fatalln(err.Error())
	}

	if len(c.LuaPath) > 0 && c.LuaPath[len(c.LuaPath)-1:] != "/" {
		c.LuaPath += "/"
	}

	fmt.Println("----------------load config------------------")
	fmt.Println("\033[32;1m" + c.String() + "\033[0m")
	fmt.Println("---------------------------------------------")
}

//CompressLua ..
func CompressLua(c *CompressConfig) {
	// buf := new(bytes.Buffer)
	zipFile, err := os.Create("tmp.zip")
	if err != nil {
		log.Fatal(err)
	}
	zipWriter := zip.NewWriter(zipFile)
	filepath.Walk(c.LuaPath, func(filePath string, info os.FileInfo, err error) (ret error) {
		if !info.IsDir() && (path.Ext(info.Name()) == ".lua") {
			buff, err := ioutil.ReadFile(filePath)
			if err != nil {
				log.Fatal(err)
			}
			tmpName := strings.Replace(filePath[len(c.LuaPath):], "/", ".", -1)
			fileWirter, err := zipWriter.Create(tmpName)
			if err != nil {
				log.Fatal(err)
			}
			_, err = fileWirter.Write(buff)
			if err != nil {
				log.Fatal(err)
			}
			// fmt.Println(strings.Replace(filePath[len(c.LuaPath):], "/", ".", -1))
		}
		return
	})

	// Make sure to check the error on Close.
	err = zipWriter.Close()
	if err != nil {
		log.Fatal(err)
	}
}

func main() {
	fmt.Println("hello")
	var conf CompressConfig
	LoadConfig(&conf)

	err := os.Remove(conf.LuaPath)
	if err != nil {
		//log.Fatal(err)
		fmt.Println(err)
	}
	// CompressLua(&conf)
}
