package main

import (
	"crypto/md5"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"log"
	"os"
	"path"
	"path/filepath"
	"strings"
	"time"
)

const (
	usage = "\n参数错误 -p 平台标示，-v 版本号 \t\nusage: -p ios -v 0.0.1"
)

//ManifestConfig 读取config.json文件
type ManifestConfig struct {
	Path     string          `json:"path"`
	URL      string          `json:"url"`
	Ignore   map[string]bool `json:"ignore"`
	Extname  map[string]bool `json:"extname"`
	Outdir   string          `json:"outdir"`
	Version  string
	Platform string
}

func (c *ManifestConfig) String() (str string) {
	return fmt.Sprintf(`
    version : %s
    platform: %s
    `, c.Version, c.Platform)
}

type asset struct {
	Size int64  `json:"size"`
	Md5  string `json:"md5"`
}

//LoadConfig 加载配置信息
func LoadConfig(c *ManifestConfig) {
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

	if len(c.Outdir) > 0 && c.Outdir[len(c.Outdir)-1:] != "/" {
		c.Outdir += "/"
	}

	fmt.Println("----------------load config------------------")
	fmt.Println("\033[32;1m" + c.String() + "\033[0m")
	fmt.Println("---------------------------------------------")
}

//GenProjManifest 生成project.mainifest
func GenProjManifest(conf *ManifestConfig) {
	projectInfo := new(struct {
		PackageURL        string           `json:"packageUrl"`
		Assets            map[string]asset `json:"assets"`
		RemoteVersionURL  string           `json:"remoteVersionUrl"`
		Time              string           `json:"time"`
		Version           string           `json:"version"`
		EngineVersion     string           `json:"engineVersion"`
		RemoteManifestURL string           `json:"remoteManifestUrl"`
	})
	projectInfo.Assets = make(map[string]asset)
	projectInfo.Time = time.Now().String()
	projectInfo.Version = conf.Version
	projectInfo.EngineVersion = "3.2"
	projectInfo.PackageURL = conf.URL + conf.Platform + "/" + conf.Version + "/"
	projectInfo.RemoteVersionURL = projectInfo.PackageURL + "manifest/version.manifest"
	projectInfo.RemoteManifestURL = projectInfo.PackageURL + "manifest/project.manifest"

	filepath.Walk(conf.Path, func(filePath string, info os.FileInfo, err error) (e error) {

		if !info.IsDir() {
			ok1, _ := conf.Ignore[strings.ToLower(info.Name())]
			ok2, _ := conf.Extname[strings.ToLower(path.Ext(info.Name()))]
			if !ok1 && ok2 {
				tmpF, err := os.Open(filePath)
				if err != nil {
					log.Fatal(err)
				}
				defer tmpF.Close()

				h := md5.New()
				if _, err := io.Copy(h, tmpF); err != nil {
					log.Fatal(err)
				}

				// fmt.Println(fmt.Sprintf("%x", h.Sum(nil)))
				projectInfo.Assets[filePath[len(conf.Path):]] = asset{info.Size(), fmt.Sprintf("%x", h.Sum(nil))}
			} else {
				fmt.Println("    \033[32;1mignore: \033[0m", filePath)
			}
		}
		return
	})

	projFile, _ := os.Create(conf.Outdir + "project.manifest")
	defer projFile.Close()
	encode := json.NewEncoder(projFile)
	encode.SetIndent("", "    ")
	encode.Encode(projectInfo)
}

//GenVersionMainfest 生成version.mainifest
func GenVersionMainfest(conf *ManifestConfig) {
	versionInfo := new(struct {
		PackageURL        string `json:"packageUrl"`
		RemoteVersionURL  string `json:"remoteVersionUrl"`
		Time              string `json:"time"`
		Version           string `json:"version"`
		EngineVersion     string `json:"engineVersion"`
		RemoteManifestURL string `json:"remoteManifestUrl"`
	})
	versionInfo.Time = time.Now().String()
	versionInfo.Version = conf.Version
	versionInfo.EngineVersion = "3.2"
	versionInfo.PackageURL = conf.URL + conf.Platform + "/" + conf.Version + "/"
	versionInfo.RemoteVersionURL = versionInfo.PackageURL + "manifest/version.manifest"
	versionInfo.RemoteManifestURL = versionInfo.PackageURL + "manifest/project.manifest"

	versionFile, _ := os.Create(conf.Outdir + "version.manifest")
	defer versionFile.Close()
	encode := json.NewEncoder(versionFile)
	encode.SetIndent("", "    ")
	encode.Encode(versionInfo)
}

func _main() {
	var conf ManifestConfig
	flag.StringVar(&conf.Platform, "p", "", usage)
	flag.StringVar(&conf.Version, "v", "", usage)
	flag.Parse()

	if len(conf.Platform) == 0 || len(conf.Version) == 0 {
		log.Fatalln(usage)
	}
	LoadConfig(&conf)

	// fmt.Printf("%s\n", conf.String())
	GenProjManifest(&conf)
	GenVersionMainfest(&conf)
}
