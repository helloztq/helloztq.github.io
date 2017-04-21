#coding:utf-8

import os, sys, json, hashlib
import stat
import time
import collections

sys.setrecursionlimit(1000000)

    # 设置当前目录
toolsdir = os.path.split(os.path.realpath(__file__))[0]
os.chdir(toolsdir)

g_files_maps = collections.OrderedDict()

# 最新版本信息的文件的path
RES_PATH = "Resources"

MANIFEST_PATH = "../" + RES_PATH + "/manifest/project.manifest"
VERSION_PATH = "../" + RES_PATH + "/manifest/version.manifest"

packageUrl = "http://koe.oxgame.cn/"
remoteManifestUrl = "manifest/project.manifest"
remoteVersionUrl = "manifest/version.manifest"
version = "0.0.0"
engineVersion = "3.2"
platform = "IOS"

fileNum = 0

# 生成文件的md5值
def genmd5(file_path):
    res_file = open(file_path, "rb")
    file_content = res_file.read(os.path.getsize(file_path))
    res_file.close()
    return hashlib.md5(file_content).hexdigest().upper()

def rewrite_null_file(file_path):
    res_file = open(file_path, "a")
    if file_path[-9:].lower() == ".property":
        res_file.write("//\r\n")
    else:
        res_file.write("--\r\n")
    res_file.close()

# 根据文件名生成 key值，格式为：[path_filename]
def genkey(file_path):
    file_key = file_path
    begin_pos = file_key.find(RES_PATH + "/")
    strlen = len(RES_PATH + "/")
    
    # 从res后面开始截取文件路径
    if begin_pos >= 0:
        begin_pos = begin_pos + strlen
        file_key = file_key[begin_pos:]
    file_key = file_key.replace("\\", "/")

    return file_key

def filecount(file_path):
    global fileNum
    for item in os.listdir(file_path):
        sub_path = os.path.join(file_path, item)

        if os.path.isdir(sub_path):
            filecount(sub_path)
        else:
            if item[0] != '.':
                fileNum = fileNum + 1
            else:
                if item == ".DS_Store":
                    os.remove(sub_path)

#需要更新的文件类型
extname = {
    ".png": True,
    ".jpg": True,
    ".plist": True,
    ".mp3": True,
    ".ttf": True,
    ".ccz": True,
    ".exportjson": True,
    ".csb": True,
    ".json": True,
    ".csv": True,
    ".lua": True,
    ".property": True,
    ".bin": True,
    ".fnt": True
}

#需要忽略的特殊文件
ignorefiless = {
    "boot.oxgame": True,
    "config.plist": True
}

# 文件夹遍历
def traverse(file_path):
    global g_files_maps

    for item in os.listdir(file_path):
        sub_path = os.path.join(file_path, item)

        # 如果是文件夹，递归遍历
        if os.path.isdir(sub_path):
            traverse(sub_path)
        else:
            # 根据后缀过滤文件
            pathinfo = os.path.splitext(item)
            if extname.has_key(pathinfo[1].lower()) and ignorefiless.has_key(item) == False:
                if sub_path.find(' ') >= 0:
                    print("      error: " + sub_path + "有空格")
                file_key = genkey(sub_path)
                file_md5 = genmd5(sub_path)
                file_size = os.stat(sub_path).st_size
           
                g_files_maps[file_key] = {}
                g_files_maps[file_key]["md5"] = file_md5
                g_files_maps[file_key]["size"] = file_size

                if file_size == 0:
                    print("************************File size 0:", item)
                    rewrite_null_file(sub_path)
            else:
                print "skip: "+ item


def gettimestr():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))


# 开始
def start():

    # 文件映射【名称:md5】
    global g_files_maps

    # 遍历目录
    traverse("../" + RES_PATH)

    # 生成json字符串
    json_str = json.dumps({
        "packageUrl": packageUrl,
        "remoteManifestUrl": remoteManifestUrl,
        "remoteVersionUrl": remoteVersionUrl,
        "engineVersion": engineVersion,
        "time": gettimestr(),                # 生成时间
        "assets": g_files_maps,                # 文件映射
        "version": version           # 版本号   
    }, sort_keys=False, indent=4)

    version_dict = collections.OrderedDict()
    version_dict["packageUrl"] = packageUrl
    version_dict["remoteManifestUrl"] = remoteManifestUrl
    version_dict["remoteVersionUrl"] = remoteVersionUrl
    version_dict["engineVersion"] = engineVersion
    version_dict["time"] = gettimestr()
    version_dict["version"] = version
    version_str = json.dumps(version_dict, sort_keys=False, indent=4)

    try:
        # 写入最新版本信息文件
        f = open(MANIFEST_PATH, "w")
        f.write(json_str)
        f.close()

        f = open(VERSION_PATH, "w")
        f.write(version_str)
        f.close()

    except Exception, e:
        print e
    finally:
        print u'All record files : %d' % len(g_files_maps)



def main():
    allFileNum = 0
    global fileNum
    global packageUrl
    global remoteManifestUrl
    global remoteVersionUrl
    packageUrl = packageUrl + platform + "/" + version + "/"
    remoteManifestUrl = packageUrl + "manifest/project.manifest"
    remoteVersionUrl = packageUrl + "manifest/version.manifest"

    start()
    filecount("../" + RES_PATH)
    allFileNum = allFileNum + fileNum
    print u'All Res Files : %d' % fileNum

    print u'All Files : %d' % allFileNum
        

if __name__ == '__main__':
    # global version
    if len(sys.argv) >= 3:
        version = sys.argv[1]
        platform = sys.argv[2]
        main()
    else:
        print 'Please input version and platform!!' 

    
    print("------- over --------")
