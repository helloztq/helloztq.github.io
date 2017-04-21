#coding:utf-8

import os, sys, json, hashlib
import stat
import time
import collections

# 设置当前目录
toolsdir = os.path.split(os.path.realpath(__file__))[0]
os.chdir(toolsdir)

RES_PATH = "../Resources/ui_layout"

# 文件夹遍历
def traverse(dirpath):

    for item in os.listdir(dirpath):
        filepath = os.path.join(dirpath, item)
        if (item[-5:].lower() == ".json"):
            f = open(filepath)
            jsonstr = f.read()
            f.close()
            layout = json.loads(jsonstr)
            # print("    Warning: %s textures: %d" % (item, len(layout["texturesPng"])))
            if len(layout["texturesPng"]) > 3:
                print("    Warning: %s textures: %d" % (item, len(layout["texturesPng"])))

       

if __name__ == '__main__':
    traverse(RES_PATH)