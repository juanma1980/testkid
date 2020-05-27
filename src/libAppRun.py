#!/usr/bin/python3
import getpass
import sys
import os
from PyQt5.QtCore import QSize,pyqtSlot,Qt, QPropertyAnimation,QThread,QRect,QTimer,pyqtSignal,QSignalMapper,QProcess
import subprocess
import base64
import signal
import time
import tempfile
import tarfile
import shutil
import psutil
from appconfig.appConfig import appConfig 
from app2menu import App2Menu
QString=type("")

class th_procMon(QThread):
#	processEnd=pyqtSignal("PyQt_PyObject")
	def __init__(self,pid,parent=None):
		QThread.__init__(self,parent)
		self.pid=pid
		self.monitor=True
		self.timer=2
		self.retCode=0

	def run(self):
		self.retCode=self.pid.wait()

#class th_procMon

class th_runApp(QThread):
	processRun=pyqtSignal("PyQt_PyObject")
	def __init__(self,app,display,parent=None):
		QThread.__init__(self,parent)
		self.display=display
		self.app=app.split(" ")
		self.menu=App2Menu.app2menu()
		self.dbg=True
		self.pid=''
	#def __init__

	def _debug(self,msg):
		if self.dbg:
			print("th_runApp: %s"%msg)
	#def _debug(self,msg):

	def __del__(self):
		self.wait()
	#def __del__

	def _run_firefox(self):
		newProfile=tempfile.mkdtemp()
		self.app=["firefox","-profile",newProfile,"--no-remote",self.app[-1]]
		os.makedirs("%s/chrome"%newProfile)
		css_content=[
					"@namespace url(\"http://www.mozilla.org/keymaster/gatekeeper/there.is.only.xul\");",
					"#TabsToolbar {visibility: collapse;}",
					"#navigator-toolbox {visibility: collapse;}",
					"browser {margin-right: -14px; margin-bottom: -14px;}"
					]
		with open ("%s/chrome/userChrome.css"%newProfile,'w') as f:
			f.writelines(css_content)
		self._debug("Firefox Launch: %s"%self.app)
	#def _run_firefox

	def _run_chromium(self):
		self.app=[self.app[0],"--temp-profile","--start-fullscreen","--app=%s"%self.app[-1]]
		self._debug("Chromium Launch: %s"%self.app)
	#def _run_chromium

	def _run_resource(self):
		subprocess.run(["flash-java-insecure-perms","install"],stdin=None,stderr=None,stdout=None,shell=False)
		app=" ".join(self.app)
		app=app.replace("/usr/bin/resources-launcher.sh",self.menu.get_default_app_for_file(app.split(" ")[-1]))
		self.app=app.split(" ")
	#def _run_resource

	def run(self):
		retval=[False,None]
		p_pid=''
		tmp_file=""
		self._debug("Launching thread...")
		try:
			env=os.environ.copy()
			env['DISPLAY']=self.display
			if "/usr/bin/resources-launcher.sh" in self.app:
				self._run_resource()
			elif 'pysycache' in self.app:
				self.app.append("-nf")
#			elif 'childsplay' in self.app:
#				self.app.append("--fullscreen")
			elif 'firefox' in self.app:
				self._run_firefox()
			elif (('chromium' in self.app) or ('chrome' in self.app)):
				self._run_chromium()
			elif 'loffice' in self.app:
				self.app.append("--display %s"%self.display)

			app=" ".join(self.app)
			if '%' in app:
				if '%s' in app.lower():
					app=app.replace("%s","")
					self.app=app.replace("%S","").split(" ")
				if '%u' in app.lower():
					app=app.replace("%u","")
					self.app=app.replace("%U","").split(" ")
				if '%f' in app.lower():
					app=app.replace("%f","")
					self.app=app.replace("%F","").split(" ")
			self.pid=subprocess.Popen(self.app,stdin=None,stdout=None,stderr=None,shell=False,env=env)
			self._debug("Launched %s"%self.app)
			#If process launch a child, get the child's pid
			parent=psutil.Process(self.pid.pid)
			for child in parent.children():
				self.pid=child
				break
			retval=[self.pid,tmp_file]
		except Exception as e:
			print("Error running: %s"%e)
			os.kill(os.getpid(),signal.SIGUSR2)
		self.processRun.emit(retval)
		self._debug("PROCESS FINISHED")
	#def run

#class th_runApp

class appRun():
	def __init__(self):
		self.dbg=True
		exePath=sys.argv[0]
		if os.path.islink(sys.argv[0]):
			exePath=os.path.realpath(sys.argv[0])
		self.baseDir=os.path.abspath(os.path.dirname(exePath))
		self.baseDir="/usr/share/runomatic/"
		self.runoapps="/usr/share/runomatic/applications"
		self.userRunoapps="%s/.config/runomatic/applications"%(os.environ['HOME'])
		self.bg="%s/rsrc/background2.png"%self.baseDir
		self.pid=0
		self.procMons=[]
		self.deadProcesses=[]
		self.confFile="runomatic.conf"
		self.config=appConfig()
		self.__init__config()
		self.xephyr_servers={}
		self.username=getpass.getuser()
		self.main_display=os.environ['DISPLAY']
		self.topBarHeight=116
		self.categories={}
		self.desktops={}
		self.threads_pid={}
		self.threads_tmp={}
		self.level='system'
		self.menu=App2Menu.app2menu()
		self.main_wid=0
		self.ratpoisonConf=''
	#def __init__

	def _debug(self,msg):
		if self.dbg:
			print("appRun: %s"%msg)
	#def _debug

	def setBg(self,bg):
		self.bg=bg

	def __init__config(self):
		self.config.set_baseDirs({'system':'/usr/share/runomatic','user':'%s/.config'%os.environ['HOME']})
		self.config.set_configFile(self.confFile)
	#def __init__config

	def set_topBarHeight(self,h):
		self.topBarHeight=h+20
	#def set_topBarHeight(self,h):

	def get_wid(self,search="Xephyr on",display=":13"):
		wid=None
		count=0
		if display in self.xephyr_servers.keys():
			self._debug("Search WID for server at display %s"%display)
			self._debug("PID searched: %s"%self.xephyr_servers[display])
			self._debug("User searched: %s"%self.username)
			while not wid and count<=100:
				p_wid=self._run_cmd_on_display(["xdotool","search","--any","--name","%s %s"%(search,display)],self.main_display)
				wid=p_wid.stdout.decode()
				time.sleep(0.1)
				count+=1
			if not wid:
				self._debug("Searching WID for active window")
		self._debug("WID %s"%wid)
		return(wid)
	#def get_wid

	def new_Xephyr(self,qwidget,display=":13"):
		return(self.init_Xephyr(qwidget,display,True))
	#def new_Xephyr

	def init_Xephyr(self,qwidget,display=":13",create_new=False):
			#		env=os.environ.copy()
		#env["HOME"]="/home/%s"%self.username
		#env["XAUTHORITY"]="/home/%s/.Xauthority"%self.username
		if display not in self.xephyr_servers.keys() or create_new:
			display=self._find_free_display(display)
			self._debug("Display is set to %s"%display)
			if display==":-1":
				self._debug("No free display found")
				self.xephyr_servers[display]=-1
			if self.pid>=0:
				args=[]
				self._debug("Width: %s Height: %s"%(qwidget.width(),qwidget.height()))
				xephyr_cmd=["Xephyr",
				"-br",
				"-ac",
#				"-nocursor",
#				"-softCursor",
				"-screen",
				"%sx%s"%(qwidget.width()-10,qwidget.height()-(self.topBarHeight+30)),
#				"800x600",
				"-resizeable",
				"-fullscreen",
				"%s"%display]

				
				#vnc_cmd=["Xtightvnc",
				vnc_cmd=["tigervncserver",
				"%s"%display,
				"-localhost",
				"-name",
				"\"Xephyr on %s\""%display,
				"-geometry",
				"800x600",
				#"%sx%s"%(qwidget.width()-10,qwidget.height()-(self.topBarHeight+30)),
				"-nevershared",
				"-SecurityTypes",
				"None",
				"-autokill"]
				#print("Launch %s"%vnc_cmd)
				subprocess.run(vnc_cmd)

				xephyr_cmd=["vinagre",
				"--vnc-scale",
				"-f",
				"-n",
#				"--gtk-vnc-debug",
				"%s"%display]
				#xephyr_cmd=["gvncviewer",
				#"localhost%s"%display]
				
				if self.main_wid==0:
					v_proc=subprocess.run(["pidof","vinagre"],stdout=subprocess.PIPE)
					if v_proc.returncode:
						v_cmd=["vinagre"]
						v_pid=subprocess.Popen(v_cmd,stderr=subprocess.DEVNULL).pid
						#v_pid=self._run_cmd_on_display(v_cmd,"%s"%display)
					else:
						v_pid=v_proc.stdout.decode().split()[0]
				#xephyr_cmd=["gvncviewer",
				#"localhost%s"%display]
					main_wid=subprocess.run(["xdotool","search","--sync","--pid","%s"%(v_pid)],stdout=subprocess.PIPE)
					wid=main_wid.stdout.decode().split()
					if len(wid)<=1:
						self.main_wid=wid[-1]
					else:
						self.main_wid=wid[1]
				self._debug("UNMAP: %s"%self.main_wid)
				p_pid=subprocess.Popen(xephyr_cmd,stderr=subprocess.DEVNULL)
#				subprocess.run(["xdotool","windowmap","--sync",self.main_wid],stderr=subprocess.PIPE)
				subprocess.run(["xdotool","windowunmap","--sync",self.main_wid],stderr=subprocess.DEVNULL)
				self.xephyr_servers[display]=p_pid.pid
				self._debug("Xephyr PID: %s"%p_pid.pid)

		return (display,self.xephyr_servers[display],p_pid.pid)
	#def init_Xephyr

	def _run_cmd_on_display(self,cmd=[],display=":13"):
		env=os.environ.copy()
		env["HOME"]="/home/%s"%self.username
		env["XAUTHORITY"]="/home/%s/.Xauthority"%self.username
		env['DISPLAY']=display
		self._debug("Running cmd on %s"%display)
		self._debug("CMD %s"%cmd)
		#prc=subprocess.run(cmd,stdout=subprocess.PIPE)
		prc=subprocess.run(cmd,stdout=subprocess.PIPE,env=env)
		return(prc)
	#def _run_cmd_on_display

	def stop_display(self,wid,display):
		#if not wid:
		windoWid=subprocess.run(["xdotool","getwindowfocus"],stdout=subprocess.PIPE)
		if (windoWid.stdout):
			widTree=subprocess.run(["xwininfo -tree -root"],shell=True,stdout=subprocess.PIPE)
			hexWid=""
			for widWindow in widTree.stdout.decode().split("\n"):
				if "Xephyr on %s"%display in widWindow:
					wid=widWindow.split()[0]
					break
		if wid:
			self._debug("CLOSING WINDOW %s"%wid)
			a=subprocess.run(["xdotool", "windowclose" ,"%s"%wid])
		if display:
			self._debug("KILLING DISPLAY %s"%display)
			subprocess.run(["vncserver","--kill","%s"%display])

	def send_signal_to_thread(self,s_signal,thread):
		self._debug("Send signal: %s to %s"%(s_signal,thread))
		retval=False
		sig={'kill':signal.SIGKILL,'term':signal.SIGTERM,'stop':signal.SIGSTOP,'cont':signal.SIGCONT}
		if thread in self.threads_pid.keys():			
			self._debug("Sending %s to thread %s with pid %s"%(s_signal,thread,self.threads_pid[thread]))
			try:
				if self.threads_pid[thread]:
					os.kill(self.threads_pid[thread],sig[s_signal])
				if (s_signal=='kill' or s_signal=='term'):
					thread.wait()
				retval=True
			except:
				self._debug("%s failed on thread %s with pid %s"%(s_signal,thread,self.threads_pid[thread]))
				thread.wait()

		elif (s_signal=='kill' or s_signal=='term'):
			if (type(thread)==type(0)):
				self._debug("Killing PID: %s"%thread)
				try:
					os.kill(thread,sig[s_signal])
					retval=True
				except:
					self._debug("%s failed on pid %s"%(s_signal,thread))

		return(retval)
	#def send_signal_to_thread

	def launch(self,app,display=":13"):
		def _get_th_pid(pid_info):
			if isinstance(pid_info[0],bool):
				#Thread failed
				self._end_process(th_run,-1)
			else:
				self.threads_pid[th_run]=pid_info[0].pid
				self.threads_tmp[th_run]=pid_info[1]
				self.threads_tmp[th_run]=pid_info[1]
				self._debug("Add %s to procMon"%pid_info[0].pid)
				procMon=th_procMon(pid_info[0])
				procMon.start()
				procMon.finished.connect(lambda:self._end_process(th_run,procMon.retCode))
				self.procMons.append(procMon)
		#launch wm
		self._debug("Launching WM for display %s"%display)
		#Generate ratposionrc
		if self.ratpoisonConf=='':
			self.ratpoisonConf=tempfile.mkstemp()[-1]
		with open(self.ratpoisonConf,'w') as f:
			f.write("exec wmname LG3D\n")
			f.write("startup_message off\n")
			f.write("set border 0\n")
			f.write("set bgcolor black\n")
			f.write("set fgcolor black\n")
			f.write("exec xsetroot -cursor_name left_ptr\n")
			f.write("exec xloadimage -tile -onroot %s\n"%self.bg)
		if os.path.isfile("%s/.ratpoisonrc"%os.environ['HOME']):
			shutil.copy("%s/.ratpoisonrc"%os.environ['HOME'],"%s/.ratpoisonrc2"%os.environ['HOME'])
		shutil.copy("%s"%self.ratpoisonConf,"%s/.ratpoisonrc"%os.environ['HOME'])
		th_runApp("ratpoison -f %s"%self.ratpoisonConf,display).start()
		if os.path.isfile("%s/.ratpoisonrc2"%os.environ['HOME']):
			shutil.copy("%s/.ratpoisonrc2"%os.environ['HOME'],"%s/.ratpoisonrc"%os.environ['HOME'])
			os.remove("%s/.ratpoisonrc2"%os.environ['HOME'])
		th_run=th_runApp(app,display)
		th_run.start()
		th_run.processRun.connect(_get_th_pid)
		return(th_run)
	#def launch
	
	def _end_process(self,th_run,retCode=0):
		self._debug("Ending process %s with retCode %s"%(th_run,retCode))
		th_run.wait()
		#self.processEnd.emit()
		self.deadProcesses.append(th_run)
		if retCode==-1:
			os.kill(os.getpid(),signal.SIGUSR2)
			os.kill(os.getpid(),signal.SIGUSR1)
		else:
			os.kill(os.getpid(),signal.SIGUSR1)
	#def _end_process

	def getDeadProcesses(self):
		deads=self.deadProcesses
		self.deadProcesses=[]
		return(deads)
	#def getDeadProcesses

	def _find_free_display(self,display=":13"):
		count=int(display.replace(":",""))
		self._debug("Search %s"%count)
		ret=subprocess.run(["xdpyinfo","-display",display],stderr=subprocess.DEVNULL,stdout=subprocess.DEVNULL).returncode
		while (ret!=1):
			count+=1
			try:
				display=":%s"%count
				ret=subprocess.run(["xdpyinfo","-display",display],stderr=subprocess.DEVNULL,stdout=subprocess.DEVNULL).returncode
			except Exception as e:
				print ("Err: %s"%e)
				display=":-1"
				break
		return("%s"%display)
	#def _find_free_display

	def get_default_config(self,exclude=[]):
		data={}
		data=self.config.getConfig('system',exclude=exclude)
		level=data['system'].get('config','n4d')
		if level=='user':
			if os.path.isfile('%s/.config/%s'%(os.environ['HOME'],self.confFile)):
				data['system']['config']='user'
			else:
				self._debug("User config not available. Reading n4d config")
				data['system']['config']='n4d'
		self.level=data['system']['config']
		self._debug("Read level from default config: %s"%self.level)
		return (data)
	#def get_config(self,level):

	def get_config(self,level):
		data={}
		data=self.config.getConfig(level)
		self._debug("Read level from config: %s"%level)
		return (data)
	#def get_config(self,level):

	def get_apps(self,categories=[],load_categories=True,exclude=[]):
		#First read system config
		sysconfig=self.get_default_config(exclude=['background64'])
		self._debug("Getting apps for level %s"%self.level)
		apps={'categories':[],'desktops':[],'hidden':[],'banned':[]}
		default={'categories':[],'desktops':[],'hidden':[],'banned':[]}
		
		if categories:
			apps['categories']=categories

		if self.level=='system':
			data=sysconfig.copy()
		else:
			data=self.config.getConfig(self.level,exclude=['background64'])

		self._debug("Read Data: %s"%data)
		level=self.level
		if not self.level in data.keys():
			if 'default' in data.keys():
				level='default'
			else:
				level=''

		if level:
			self._debug("Read file %s"%level)
			apps['hidden']=data[level].get('hidden',[])
			apps['banned']=data[level].get('banned',[])
			if categories==[] and load_categories:
				apps['categories']=data[level].get('categories',[])
				apps['desktops']=data[level].get('desktops',[])

			self._debug("Readed %s"%apps)

		if not apps['categories'] and not apps['desktops'] and load_categories:
			apps=default
		categories=apps.get('categories',[])
		runoapps={}
		if 'run-o-matic' not in categories:
			for runoapp in self.get_category_desktops("run-o-matic"):
				runoapps[(os.path.basename(runoapp))]=runoapp
		else:
			self._generate_runodesktops(data[level].get('runotar',""))

		filteredApps=self._filter_category_apps(apps['categories'],apps['desktops'],apps['banned'],apps['hidden'],runoapps)
		apps['desktops']=filteredApps.get('desktops',[])
		apps['banned']=filteredApps.get('banned',[])
		apps['hidden']=filteredApps.get('hidden',[])
		self._debug("Banned; %s"%apps['banned'])
		apps['keybinds']=data[level].get('keybinds')
		apps['password']=data[level].get('password')
		apps['close']=data[level].get('close')
		apps['startup']=data[level].get('startup')
		bg=data[level].get('background',"")
		bg64=data[level].get('background64',"")
		data[level]['background']=self._fix_background_path(bg,bg64,level)
		apps['background']=data[level].get('background')
		return(apps)
	#def get_apps

	def _generate_runodesktops(self,runotar):
		deskPath="%s/.config/runomatic/applications/"%(os.environ['HOME'])
		self._debug("Generating runodesktops")
		if not os.path.isdir(deskPath):
			os.makedirs(deskPath)
		for oldFile in os.listdir(deskPath):
			if oldFile.endswith(".desktop"):
				os.remove("%s/%s"%(deskPath,oldFile))
		if runotar:
			tmpTar=tempfile.mkstemp(suffix=".tar.gz")[1]
			with open(tmpTar,"wb") as f:
				f.write(base64.decodebytes(runotar.encode("utf-8")))
			tar64=tarfile.open(tmpTar,"r:gz")
			for runoapp in tar64:
				runoapp.name=os.path.basename(runoapp.name)
				tar64.extract(runoapp,deskPath)
	#def _generate_runodesktops

	def _filter_category_apps(self,categories,desktops,banned,hidden,runoapps):
		result={}
		for category in categories:
			cat_apps=self.get_category_desktops(category.lower())
			for app in cat_apps:
				if ((app not in desktops) and (app not in banned)):
					desktops.append(app)
				if app in hidden and app in desktops:
					if runoapps.get(os.path.basename(app),False):
						idx=desktops.index(app)
						self._debug("Banned app: %s"%app)
						banned.append(app)
						if (runapps[os.path.basename(app)] not in desktops):
							desktops.insert(idx,runoapps[os.path.basename(app)])
					desktops.remove(app)
		result={'desktops':desktops,'banned':banned,'hidden':hidden}
		return(result)
	#def _filter_category_apps
	
	def _fix_background_path(self,bg,bg64,level):
		imgName=bg
		if not os.path.isfile(bg):
			if bg:
				imgName="%s/.config/runomatic/backgrounds/%s"%(os.environ['HOME'],os.path.basename(bg))
			else:
				imgName="%s/.config/runomatic/backgrounds/generic.png"%(os.environ['HOME'])
			if not os.path.isfile(imgName):
				if bg64=="":
					dataBg=self.config.getConfig(level)
					bg64=dataBg[level].get('background64',"")
				if bg64:
					if not os.path.isdir("%s/.config/runomatic/backgrounds"%os.environ['HOME']):
						os.makedirs("%s/.config/runomatic/backgrounds"%os.environ['HOME'])
					with open(imgName,"wb") as f:
						f.write(base64.decodebytes(bg64.encode("utf-8")))
		return imgName
	#def _fix_background_path(self,bg,bg64):

	def get_category_desktops(self,category):
		apps=[]
		tmp_apps=[]
		if category=="run-o-matic":
				#			if os.path.isdir(self.runoapps):
#				for f in os.listdir(self.runoapps):
#					if f not in apps and os.path.isfile("%s"%os.path.join(self.runoapps,f)):
#						apps.append("%s"%os.path.join(self.runoapps,f))
			if os.path.isdir(self.userRunoapps):
				for f in os.listdir(self.userRunoapps):
					if f not in apps and os.path.isfile("%s"%os.path.join(self.userRunoapps,f)):
						apps.append("%s"%os.path.join(self.userRunoapps,f))
		else:
			self.menu.set_desktop_system()
			applist=self.menu.get_apps_from_category(category)
			for app,data in applist.items():
				if data['exe'] not in tmp_apps and app not in tmp_apps:
					apps.append("%s/%s"%(self.menu.desktoppath,app))
					tmp_apps.append(data['exe'])
					tmp_apps.append(app)
		return(apps)
	#def get_category_desktops

	def get_category_apps(self,category):
		apps={}
		if category=="run-o-matic":
				#			if os.path.isdir(self.runoapps):
#				for f in os.listdir(self.runoapps):
#					for key,value in self.get_desktop_app(f).items():
#						apps[key]=value
			if os.path.isdir(self.userRunoapps):
				for f in os.listdir(self.userRunoapps):
					for key,value in self.get_desktop_app("%s/%"%(self.userRunoapps,f)).items():
						apps[key]=value
		else:
			applist=self.menu.get_apps_from_category(category)
			for key,app in applist.items():
				if 'xdg-open' in app['exe']:
					app['exe']=app['exe'].replace("xdg-open",self.menu.get_default_app_for_file(app['exe'].split(" ")[-1]))
				apps[app['exe']]=app['icon']
		return (apps)
	#def get_category_apps

	def get_desktop_app(self,f_desktop,name=None):
		apps={}
		app=self.menu.get_desktop_info(f_desktop)
		if 'xdg-open' in app['Exec']:
			app['Exec']=app['Exec'].replace("xdg-open",self.menu.get_default_app_for_file(app['Exec'].split(" ")[-1]))
		apps[app['Exec']]=app['Icon']
		if name:
			apps[app['Exec']]={'Icon':app['Icon'],'Name':app['Name']}
		return (apps)
	#def get_desktop_app

	def write_config(self,data,key=None,level=None):
		self.config.write_config(data,level=level,key=key)
	#def write_config
