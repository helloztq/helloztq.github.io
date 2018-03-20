#coding=utf-8

import os
import json
import shutil

realpath = os.path.realpath(".")


def parseConfig():
	f = open("simulator.json")
	appConfig = json.loads(f.read())
	f.close()
	return appConfig


def genSimulators():
	appConfig = parseConfig()
	for i in range(len(appConfig["sims"])):
		width = appConfig["sims"][i]["width"]
		height = appConfig["sims"][i]["height"]
		appname = "Sim_%d@%d.app" % (width, height)
		
		try:
			shutil.rmtree(appname)
		except OSError, e:
			pass

		shutil.copytree("Simulator.app", appname)

		f = open(appname + "/Contents/Resources/config.json")
		configStr = f.read()
		f.close()

		config = json.loads(configStr)
		config["init_cfg"]["workdir"] = appConfig["workdir"]
		config["init_cfg"]["entry"] = appConfig["entry"]
		config["init_cfg"]["width"] = width
		config["init_cfg"]["height"] = height
		config["init_cfg"]["name"] = "%d@%d" % (width, height)
		config["init_cfg"]["writablepath"] = realpath + "/sim_%d_%d" % (width, height)
		configStr = json.dumps(config, sort_keys=True, indent=4)

		f = open(appname + "/Contents/Resources/config.json", "wb")
		f.write(configStr)
		f.close()


if __name__ == '__main__':
	genSimulators()