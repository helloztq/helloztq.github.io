package main

import (
	"archive/zip"
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"os/exec"
	"path"
	"path/filepath"
	"runtime"
	"strings"
	"sync"
	"time"
)

const (
	eZipTypeGame   = iota
	eZipTypeOxgame = iota
	spec           = "message.protocol."
)

var zipName = []string{"game.bin.zip", "boot.oxgame.zip"}

//ZipType ..
type ZipType int

//CompressConfig ..
type CompressConfig struct {
	BackupPath string          `json:"bkpath"`
	LuaPath    string          `json:"luapath"`
	RarPath    string          `json:"rarpath"`
	BootFiles  map[string]bool `json:"bootfiles"`
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
	if len(c.BackupPath) > 0 && c.BackupPath[len(c.BackupPath)-1:] != "/" {
		c.BackupPath += "/"
	}
	// fmt.Println("----------------load config------------------")
	// fmt.Println("\033[32;1m" + c.String() + "\033[0m")
	// fmt.Println("---------------------------------------------")
}

//CopyLuaScript ...
func CopyLuaScript(c *CompressConfig) {
	filepath.Walk(c.BackupPath, func(filePath string, info os.FileInfo, err error) (ret error) {
		if !info.IsDir() && (path.Ext(info.Name()) == ".lua") {

			tmpath := path.Join(c.LuaPath, path.Dir(filePath[len(c.BackupPath):]))
			if _, err := os.Stat(tmpath); os.IsNotExist(err) {
				dirinfo, _ := os.Stat(path.Dir(filePath))
				err = os.MkdirAll(tmpath, dirinfo.Mode())
				if err != nil {
					fmt.Println(err.Error())
				}
			}
			buffer, err := ioutil.ReadFile(filePath)
			if err != nil {
				fmt.Println(err.Error())
			}
			err = ioutil.WriteFile(path.Join(tmpath, info.Name()), buffer, info.Mode())
			if err != nil {
				fmt.Println(err.Error())
			}
		}
		return
	})
}

func saveForAndroid(zipWriter *zip.Writer, filePath string, fileName string, innerName string, wg *sync.WaitGroup) {
	defer wg.Done()
	bytesPath := filepath.Join(path.Dir(filePath), fileName[:len(fileName)-len("lua")]+"bytes")
	cmd := exec.Command("./luajit", "-b", "-s", filePath, bytesPath)
	cmd.Stderr = bytes.NewBuffer(nil)

	if err := cmd.Run(); err != nil {
		log.Fatal(cmd.Stderr)
	}
	buff, err := ioutil.ReadFile(bytesPath)
	if err != nil {
		log.Fatal(err)
	}

	fileWirter, err := zipWriter.Create(innerName)
	if err != nil {
		log.Fatal(err)
	}
	_, err = fileWirter.Write(buff)
	if err != nil {
		log.Fatal(err)
	}
	os.Remove(bytesPath)

}

func saveForIOS(zipWriter *zip.Writer, filePath string, fileName string, innerName string, wg *sync.WaitGroup) {
	defer wg.Done()
	buff, err := ioutil.ReadFile(filePath)
	if err != nil {
		log.Fatal(err)
	}

	fileWirter, err := zipWriter.Create(fileName)
	if err != nil {
		log.Fatal(err)
	}
	_, err = fileWirter.Write(buff)
	if err != nil {
		log.Fatal(err)
	}
	// println("runtime.NumGoroutine(): ", runtime.NumGoroutine())
}

//CompressLua 将代码打包zip
func CompressLua(c *CompressConfig, zt ZipType) {
	var wg sync.WaitGroup
	gameFileIOS, err := os.Create(path.Join(c.RarPath, zipName[zt]+".ios"))
	if err != nil {
		log.Fatal(err)
	}
	defer gameFileIOS.Close()

	gameFileAndroid, err := os.Create(path.Join(c.RarPath, zipName[zt]+".android"))
	if err != nil {
		log.Fatal(err)
	}
	defer gameFileAndroid.Close()

	gameWriterIOS := zip.NewWriter(gameFileIOS)
	gameWriterAndroid := zip.NewWriter(gameFileAndroid)

	count := 0
	filepath.Walk(c.LuaPath, func(filePath string, info os.FileInfo, err error) (ret error) {
		if runtime.NumGoroutine() > 10 {
			time.Sleep(time.Millisecond * 10)
		}
		bPackage := !info.IsDir() && (path.Ext(info.Name()) == ".lua")
		if zt == eZipTypeOxgame {
			_, bExist := c.BootFiles[info.Name()]
			bPackage = bPackage && bExist
		}

		if bPackage {
			tmpName := strings.Replace(filePath[len(c.LuaPath):len(filePath)-len(".lua")], "/", ".", -1)
			if filepath.HasPrefix(tmpName, spec) {
				tmpName = tmpName[len(spec):]
			}

			wg.Add(2)
			go saveForAndroid(gameWriterAndroid, filePath, info.Name(), tmpName, &wg)
			go saveForIOS(gameWriterAndroid, filePath, info.Name(), tmpName, &wg)

			count++
		}
		return
	})
	wg.Wait()
	err = gameWriterIOS.Close()
	if err != nil {
		log.Fatal(err)
	}

	err = gameWriterAndroid.Close()
	if err != nil {
		log.Fatal(err)
	}

	fmt.Printf("\033[32;1msuccess:\033[0m %s   count:%d\n", zipName[zt], count)
}

func main() {
	fmt.Println("hello")
	var conf CompressConfig
	LoadConfig(&conf)

	err := os.RemoveAll(conf.LuaPath)
	if err != nil {
		fmt.Println(err)
	}
	fmt.Println("----------------compress------------------")
	CopyLuaScript(&conf)

	runtime.GOMAXPROCS(runtime.NumCPU())
	// CompressLua(&conf, eZipTypeOxgame)
	CompressLua(&conf, eZipTypeGame)
	fmt.Println("------------------end---------------------")
}
