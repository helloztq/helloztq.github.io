#-*- coding:utf-8 -*-
from xml.etree import ElementTree
import os
import base64
import struct


ROOT_PATH = os.path.dirname(os.path.realpath(__file__))

CSV_PATH = ROOT_PATH + "/../Resources/json/"

def package_csv():
    out_path = os.path.join(CSV_PATH, "config.bin")
    f = open(out_path, "w")
    for name in os.listdir(CSV_PATH):
        if name[-4:] == ".csv":
            filepath = os.path.join(CSV_PATH, name)
            namekey = "json/" + name
            f.write("%d" % len(namekey))
            f.write("&")
            f.write(namekey)
            f.write("&")
            f.write("%d" % os.path.getsize(filepath))
            f.write("&")

            csvf = open(filepath, "r")
            for line in csvf.readlines():
                line = line.strip('\x00')
                if len(line) > 20:
                    f.write(line)
            csvf.close()    
            f.write("&")

    f.close()        

if __name__ == '__main__':
    package_csv()
    print("----- over -----")
    
     

