#! /usr/bin/python3
import os
from appconfig.appConfig import appConfig

#First check system config
confFile="runomatic.conf"
baseDirs={'system':'/usr/share/runomatic','user':'%s/.config'%os.environ['HOME']}
config=appConfig()
config.set_configFile(confFile)
config.set_baseDirs(baseDirs)
data={}
if os.path.isfile("%s/%s"%(baseDirs['system'],confFile)):
	conf=config.getConfig('system')
	level=conf['system'].get("config",None)
	if level=='n4d':
		conf=config.getConfig('n4d')
		data=conf['n4d'].copy()
	elif level=='user':
		#If there's no user's config set the n4d config as default
		if os.path.isfile('%s/%s'%(baseDirs['user'],confFile)):
			conf=config.getConfig('user')
		else:
			conf=config.getConfig('n4d')
			level=conf['n4d'].get("config",None)
		data=conf[level].copy()
	else:
		data=conf['system'].copy()

startup=data.get('startup','')
if str(startup).lower()=='true':
	os.execv("%s/runomatic.py"%baseDirs['system'],["1"])
