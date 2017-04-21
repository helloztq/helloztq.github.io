#-*- coding:utf-8 -*-
import os


ROOT_PATH = os.path.dirname(os.path.realpath(__file__))

MINIMAP_PATH = ROOT_PATH + "/../../../../doc/最终文档及资源/images/world/minimap/minimap"
MINIMAP_MASK_PATH = ROOT_PATH + "/../../../../doc/最终文档及资源/images/world/minimap/minimap_mask"
DEST_PATH= ROOT_PATH + "/../../../../doc/最终文档及资源/images/world/minimap/minimapsheet"

for s in os.listdir(MINIMAP_PATH):
    nameinfo = os.path.splitext(s)
    if nameinfo[1] == ".jpg":
        srcpath_1 = os.path.join(MINIMAP_PATH, s)
        srcpath_2 = os.path.join(MINIMAP_MASK_PATH, "mask_" + s)

        if os.path.exists(srcpath_2):
            sheetpath = os.path.join(DEST_PATH, "world_%s.jpg" % nameinfo[0])
            datapath  = os.path.join(DEST_PATH, "world_%s.plist" % nameinfo[0])
            cmd = "TexturePacker %s %s \
                    --sheet %s \
                    --data %s \
                    --allow-free-size \
                    --no-trim \
                    --max-size 1024 \
                    --format cocos2d" % (srcpath_1, srcpath_2, sheetpath, datapath)      
            os.system(cmd)
        else:
            print "ERROR: NOT exists mask %s" % srcpath_2
            exit(1)    

print "OVER............" 