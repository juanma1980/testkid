#!/usr/bin/env python3
import sys
import os
import json

try:
	import xmlrpc.client as n4d
except ImportError:
	raise ImportError("xmlrpc not available. Disabling server queries")
import ssl

class appConfig():
	def __init__(self):
		self.dbg=True
		self.home=os.environ['HOME']
		self.baseDirs={"user":"%s/.config"%self.home}
		self.confFile="app.conf"
		self.passFile="app.pwd"
		self.config={}
		self.n4d=None
	#def __init__

	def _debug(self,msg):
		if self.dbg:
			print("Config: %s"%msg)
	#def _debug

	def set_baseDirs(self,dirs):
		self.baseDirs=dirs.copy()
		self._debug("baseDirs: %s"%self.baseDirs)
	#def set_baseDirs

	def set_configFile(self,confFile):
		self.confFile=confFile
		self._debug("ConfFile: %s"%self.confFile)
	#def set_confFile

	def set_defaultConfig(self,config):
		self.config.update({'default':config})
		self._debug(self.config)
	#def set_defaultConfig

	def get_config(self,level=None):
		self._read_config_from_system(level)
		self._read_config_from_n4d()
		return (self.config)

	def _read_config_from_system(self,level):
		def _read_file(confFile):
			data={}
			if os.path.isfile(confFile):
				self._debug("Reading %s"%confFile)
				try:
					data=json.loads(open(confFile).read())
				except Exception as e:
					self._debug("Error opening %s: %s"%(confFile,e))
			if data:
				self.config[confFile]=data
		#def _read_file

		if level and level in self.baseDirs[level]:
			confFile=("%s/%s"%(confDir,self.confFile))
			_read_file(confFile)
		else:
			for conflevel,confDir in self.baseDirs.items():
				confFile=("%s/%s"%(confDir,self.confFile))
				_read_file(confFile)
	#def read_config_from_system

	def write_config(self,data,level=None,key=None):
		self._debug("Writing key %s to %s"%(key,level))
		oldConf=self.get_config(level)
		print("Old: %s"%oldConf)
		newConf=oldConf.copy()
		if key:
			newConf[key]=data
		else:
			newConf=data
		self._write_config_to_system(newConf,level)
		self._write_config_to_n4d(newConf)

	def _write_config_to_system(self,conf,level=None):
		data={}
		if level and level in self.baseDirs.keys():
			confDir=self.baseDirs[level]
		else:
			confDir=self.defaultDir
		confFile=("%s/%s"%(confDir,self.confFile))
		self.config[confFile]=conf
		print(self.config[confFile])
	#def read_config_from_system

	def set_class_for_n4d(self,n4dclass):
		self.n4dclass=n4dclass
		self._debug("N4d Class: %s"%self.n4dclass)
	#def set_class_for_n4d(self,n4dclass):

	def set_method_for_n4d(self,n4dmethod,n4dclass=None,parms=None):
		self.n4dmethod=n4dmethod
		if parms:
			self.n4dparms[n4dmethod]={'parms':parms}
		if n4dclass:
			self.n4dparms[n4dmethod]={'class':n4dclass}
		else:
			self.n4dparms[n4dmethod]={'class':self.n4dclass}
		self._debug("N4d Method: %s"%self.n4dmethod)
	#def set_method_for_n4d(self,n4dmethod):

	def _read_config_from_n4d(self):
		sw=True
		if self.n4d:
			query="self.n4d.%s(self,credentials,%s"%(self.n4dmethod,self.n4dclass)
			self.config['n4d']=self._execute_n4d_query(query)
		return (self.config)
	#def read_config_from_n4d

	def _write_config_to_n4d(self,conf):
		pass
	def _execute_n4d_query(self):
		retval={}
		try:
			data=eval(query)
		except Exception as e:
			self._debug("Error accessing n4d: %s"%e)
			sw=False
		if 'status' and 'data' in data.keys():
			retval=data
			if data['status']!=True:
				self._debug("Call to method %s of class %s failed,"%(self.n4dmethod,self.n4dclass))
		elif sw:
			self._debug("Unable to get status or data from n4d method. Please update your method")
		return(retval)

	def set_credentials(self,user,pwd,server):
		self.credentials=[user,pwd]
		if server!='localhost':
			self._debug("Connecting to server %s"%server)						
			self.n4d=self._n4d_connect(server)
		else:
			try:
				server_ip=socket.gethostbyname("server")
				self.n4d=self._n4d_connect("server")
			except:
				self.n4d=None
	#def set_credentials
	
	def _n4d_connect(self,server):
		#Setup SSL
		context=ssl._create_unverified_context()
		n4dclient = n4d.ServerProxy("https://"+server+":9779",context=context,allow_none=True)
		return(n4dclient)
	#def _n4d_connect
