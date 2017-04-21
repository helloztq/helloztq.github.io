#coding:utf-8

import os, sys, io
import shutil
import struct
import zipfile

import compile_lua
import encrypt


_DELTA = 0x9E3779B9
toolsdir = os.path.split(os.path.realpath(__file__))[0]
os.chdir(toolsdir)

src_path = "../Resources_bk/script"
dst_path = "../encrypt_out/script"
out_path = "../encrypt_out"

if os.path.exists(dst_path):
    shutil.rmtree(dst_path)
shutil.copytree(src_path, dst_path)

suffix = ""
#这些需要提前加载，不用更新，放在一个zip中
preloadfiles = {
    "debug": True,
    "init": True,
    "config": True,
    "i18nConfig": True,
    "device_com": True,
    "channel_id": True,
    "game_configuration": True,
    "gameversion": True,
    "getuid": True,
    "update_layer": True,
    "loading_node": True,
    "logo_scene": True,
    "update_ctrl": True,
    "game": True,
    "main": True,
    "DeprecatedEnum": True,
    "DeprecatedClass": True,
    "Deprecated": True,
    "functions": True,
    "json": True,
    "extern": True,
    "transition": True,
    "device": True,
    "display": True,
    "Cocos2dConstants": True,
    "OpenglConstants": True,
    "StudioConstants": True,
    "GuiConstants": True,
    "Cocos2d": True,
    "CocoStudio": True,
    "loc": True,
    "lj": True,
    "update_finish": True
}

spec = "message.protocol." #处理lua 通过module定义模块的问题
filecount1 = 0
filecount2 = 0
def encrypt_file(filepath):
    f = io.open(filepath, "rb")
    s = f.read()
    f.close()

    if s[:len(sign)] == sign:
        print("[ERROR:]" + filepath)
    else:
        f = io.open(filepath, "wb")
        f.write(sign + encrypt(s, key))
        f.close()

# 文件夹遍历
def traverse(file_path, ext, bootstrapzip, gamezip):
    global filecount1, filecount2
    for item in os.listdir(file_path):
        if item[0] != '.':
            sub_path = os.path.join(file_path, item)
            if os.path.isdir(sub_path):
                traverse(sub_path, ext, bootstrapzip, gamezip)
            else:

                pathinfo = os.path.splitext(item)
                if pathinfo[1] == ext:
                    filename = sub_path[len(dst_path) + 1:-len(ext)].replace(os.path.sep, ".")
                    if filename[:len(spec)] == spec:
                        filename = filename[len(spec):]

                    if preloadfiles.has_key(pathinfo[0]):
                        bootstrapzip.write(sub_path, filename)
                        filecount1 = filecount1 + 1
                    else:
                        gamezip.write(sub_path, filename)
                        filecount2 = filecount2 + 1
        else:
            pass#print("ignore: " + item)        
                
 
def compress_by_ext(extname, outname):
    global filecount1, filecount2

    print("|      *  === %s ===" % outname)
    filecount1 = 0
    filecount2 = 0

    out_boot_path = out_path + '/boot.oxgame.' + outname
    out_game_path = out_path + '/game.bin.' + outname
    

    bootzip = zipfile.ZipFile(out_boot_path, 'w', zipfile.ZIP_DEFLATED)
    gamezip = zipfile.ZipFile(out_game_path, 'w', zipfile.ZIP_DEFLATED)

    traverse(dst_path, extname, bootzip, gamezip)
    gamezip.close()
    bootzip.close()

    encrypt.encrypt_file(out_boot_path)
    encrypt.encrypt_file(out_game_path)

    if len(preloadfiles) != filecount1:
        print("====================================== error ======================================")
        print("====================================== error ======================================")
        print("====================================== error ======================================")
        print("====================================== error ======================================")
        print("====================================== error ======================================")
        print("====================================== error ======================================")
    print("|      *  %s || count: %d" % (out_boot_path, filecount1))
    print("|      *  %s || count: %d" % (out_game_path, filecount2))

if __name__ == '__main__':
    #编译lua字节码
    compile_lua.compile_lua(dst_path)
    #压缩加密
    print("------------------------------------------- 2.compress --------------------------------------------")
    compress_by_ext(".lua", "ios")
    compress_by_ext(".bytes", "android")
    print("------------------------------------------- end compress --------------------------------------------")



