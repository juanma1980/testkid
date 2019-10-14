#!/usr/bin/env python3
import os
from appconfig.appConfig import appConfig

#First check system config
config=appConfig()
config.set_configFile("runomatic.conf")
config.set_baseDirs({'system':'/usr/share/runomatic'})
data={}
if os.path.isfile('/usr/share/runomatic/runomatic.conf'):
	conf=config.getConfig('system')
	level=conf['system'].get("config",None)
	if level=='n4d':
		conf=config.getConfig('n4d')
		data=conf['n4d'].copy()
	elif level=='user':
		conf=config.getConfig('user')
		data=conf['user'].copy()
	else:
		data=conf['system'].copy()

startup=data.get('startup','')
if str(startup).lower()=='true':
	os.execv("%s/runoconfig.py"%self.baseDir,["1"])
