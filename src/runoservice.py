#!/usr/bin/env python3
import os
from appconfig.appConfig import appConfig

#First check system config
config=appConfig()
config.set_configFile("runomatic.conf")
config.set_baseDirs({'system':'/usr/share/runomatic'})
n4d=True
data={}
if os.path.isfile('/usr/share/runomatic/runomatic.conf'):
	conf=config.getConfig('system')
	level=conf['system'].get("config",None)
	if level=='n4d':
		conf=config.getConfig('n4d')
		data=conf['n4d'].copy()
	elif level=='user';
		conf=config.getConfig('user')
		data=conf['n4d'].copy()
	else:
		data=conf['system'].copy()

startup=data.get('startup','')
if str(startup).lower()=='true':
	with open ("/etc/xdg/autostart/runomatic.desktop","w") as f:
		f.write("[Desktop Entry]\n")
		f.write("Encoding=UTF-8\n")
		f.write("Name=runomatic\n")
		f.write("Comment=runomatic autostart\n")
		f.write("Exec=/usr/bin/runomatic\n")
		f.write("Terminal=false\n")
		f.write("Type=Application\n")
else:
	if os.path.isfile("/etc/xdg/autostart/runomatic.desktop"):
		os.remove("/etc/xdg/autostart/runomatic.desktop")
		
