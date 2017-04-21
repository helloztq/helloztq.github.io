#-*- coding:utf-8 -*-

import os
import json

ROOT_PATH = os.path.dirname(os.path.realpath(__file__))
SRC_PATH = ROOT_PATH + "/../../../../doc/最终文档及资源/images/world/erjiditu/erjiditu/Json/erjiditu_1.json"


OUT_LUA_PATH = ROOT_PATH + "/../Resources/script/minimap/minimap.lua"

f = open(SRC_PATH)
jsonstr = f.read()
f.close()
minmap = json.loads(jsonstr)

f = open(OUT_LUA_PATH, "w")
f.write("\n\n----x, y, right-x, right-y, left-x, left-y, res-name")
f.write("\n\nlocal minimap = {\n")
index = 1
f.write("%4swidth = %d, height = %d,\n" % (' ', minmap["designWidth"], minmap["designHeight"]))
for i in range(0, len(minmap["widgetTree"]["children"])):
    child = minmap["widgetTree"]["children"][i]["options"]
    #if child["name"] != "Image_8" and child["name"] != "Image_945":
        
    (filepath, filename) = os.path.split(child["fileNameData"]["path"])
    filename = os.path.splitext(filename)[0]
    f.write("%4s[%s] = {" % (' ', filename))
    f.write("img = \"%s\",\n" % filename)
    f.write("%8sld = {x = %.2f, y = %.2f}, " % (" ", child["x"] - child["width"] / 2.0, child["y"] - child["height"] / 2.0))
    f.write("lt = {x = %.2f, y = %.2f},\n" % (child["x"] - child["width"] / 2.0, child["y"] + child["height"] / 2.0))
    f.write("%8srd = {x = %.2f, y = %.2f}, " % (" ", child["x"] + child["width"] / 2.0, child["y"] - child["height"] / 2.0))
    f.write("rt = {x = %.2f, y = %.2f},\n" % (child["x"] + child["width"] / 2.0, child["y"] + child["height"] / 2.0))
    f.write("%8scp = {x = %.2f, y = %.2f}\n" % (" ", child["x"], child["y"]))
    f.write("%4s},\n" % " ")
    index = index + 1
    
f.write("}\n")
f.write("return minimap\n")  
f.close()  