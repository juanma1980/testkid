#!/usr/bin/env python3
import getpass
import sys
import os
from PyQt5.QtCore import QSize,pyqtSlot,Qt, QPropertyAnimation,QThread,QRect,QTimer,pyqtSignal,QSignalMapper,QProcess
import subprocess
import signal
import time
import tempfile
from appconfig.appConfig import appConfig 
from app2menu import App2Menu
QString=type("")


class th_runApp(QThread):
	processRun=pyqtSignal("PyQt_PyObject")
	processEnd=pyqtSignal("PyQt_PyObject")
	def __init__(self,app,display,parent=None):
		QThread.__init__(self,parent)
		self.display=display
		self.app=app.split(" ")
		self.menu=App2Menu.app2menu()
		self.dbg=False
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
			dsp=os.environ['DISPLAY']
			os.environ['DISPLAY']=self.display
			if "/usr/bin/resources-launcher.sh" in self.app:
				self._run_resource()
			elif 'pysycache' in self.app:
				self.app.append("-nf")
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
			p_pid=subprocess.Popen(self.app,stdin=None,stdout=None,stderr=None,shell=False)
			os.environ['DISPLAY']=dsp
			retval=[p_pid,tmp_file]
		except Exception as e:
			print("Error running: %s"%e)
		self.processRun.emit(retval)
		print("PROCESS FINISHED")
	#def run
#class th_runApp


class appRun():
	def __init__(self):
		self.dbg=True
		self.pid=0
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
		self.ratpoisonConf=''
	#def __init__

	def _debug(self,msg):
		if self.dbg:
			print("appRun: %s"%msg)
	#def _debug

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
		os.environ["HOME"]="/home/%s"%self.username
		os.environ["XAUTHORITY"]="/home/%s/.Xauthority"%self.username
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
				"%s"%display]
				p_pid=subprocess.Popen(xephyr_cmd)
				self.xephyr_servers[display]=p_pid.pid
				self._debug("Xephyr PID: %s"%p_pid.pid)
		return (display,self.xephyr_servers[display],p_pid.pid)
	#def init_Xephyr

	def _run_cmd_on_display(self,cmd=[],display=":13"):
		os.environ["HOME"]="/home/%s"%self.username
		os.environ["XAUTHORITY"]="/home/%s/.Xauthority"%self.username
		dsp=os.environ['DISPLAY']
		os.environ['DISPLAY']=display
		self._debug("Running cmd on %s"%display)
		self._debug("CMD %s"%cmd)
		prc=subprocess.run(cmd,stdout=subprocess.PIPE)
		os.environ['DISPLAY']=dsp
		return(prc)
	#def _run_cmd_on_display

	def send_signal_to_thread(self,s_signal,thread):
		self._debug("Send signal: %s to %s"%(s_signal,thread))
		retval=False
		sig={'kill':signal.SIGKILL,'term':signal.SIGTERM,'stop':signal.SIGSTOP,'cont':signal.SIGCONT}
		if thread in self.threads_pid.keys():			
			try:
				if self.threads_pid[thread]:
					os.kill(self.threads_pid[thread],sig[s_signal])
				retval=True
			except:
				self._debug("%s failed on thread %s with pid %s"%(s_signal,thread,self.threads_pid[thread]))

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
			if pid_info[0].pid==False:
				#Thread failed
				pass
			self.threads_pid[th_run]=pid_info[0].pid
			self.threads_tmp[th_run]=pid_info[1]
			self.threads_tmp[th_run]=pid_info[1]
		#launch wm
		self._debug("Launching WM for display %s"%display)
		#Generate ratposionrc
		if self.ratpoisonConf=='':
			self.ratpoisonConf=tempfile.mkstemp()[-1]
		with open(self.ratpoisonConf,'w') as f:
			f.write("exec wmname LG3D\n")
			f.write("set border 0\n")
			f.write("startup message off\n")
			f.write("set bgcolor white\n")
			f.write("set fgcolor white\n")
			f.write("exec xsetroot -cursor_name left_ptr\n")
			f.write("exec xloadimage -fullscreen -onroot /home/lliurex/git/testkid/rsrc/background.jpg\n")
		th_run=th_runApp("ratpoison -f %s"%self.ratpoisonConf,display)
		th_run.start()
		th_run=th_runApp(app,display)
		th_run.start()
		th_run.processRun.connect(_get_th_pid)
		th_run.finished.connect(lambda:self._end_process(th_run))
		return(th_run)
	#def launch
	
	def _end_process(self,th_run):
		#self.processEnd.emit()
		print("End %s"%th_run)

	def _find_free_display(self,display=":13"):
		count=int(display.replace(":",""))
		self._debug("Search %s"%count)
		ret=subprocess.run(["xdpyinfo","-display",display]).returncode
		while (ret!=1):
			count+=1
			try:
				display=":%s"%count
				ret=subprocess.run(["xdpyinfo","-display",display]).returncode
			except Exception as e:
				print ("Err: %s"%e)
				display=":-1"
				break
		return("%s"%display)
	#def _find_free_display

	def get_default_config(self):
		data={}
		data=self.config.getConfig('system')
		if 'config' not in data['system'].keys():
			data['system']['config']='user'
		self.level=data['system']['config']
		self._debug("Read level from config: %s"%self.level)
		return (data)
	#def get_config(self,level):

	def get_config(self,level):
		data={}
		data=self.config.getConfig(level)
		self._debug("Read level from config: %s"%level)
		return (data)
	#def get_config(self,level):

	def get_apps(self,categories=[],load_categories=True):
		#First read system config
		sysconfig=self.get_default_config()
		self._debug("Getting apps for level %s"%self.level)
		apps={'categories':[],'desktops':[],'hidden':[]}
		default={'categories':[],'desktops':[],'hidden':[]}
		
		if categories:
			apps['categories']=categories

		if self.level=='system':
			data=sysconfig.copy()
		else:
			data=self.config.getConfig(self.level)

		self._debug("Read Data: %s"%data)
		level=self.level
		if not self.level in data.keys():
			if 'default' in data.keys():
				level='default'
			else:
				level=''

		if level:
			self._debug("Read file %s"%level)
			if categories==[] and load_categories:
				apps['categories']=data[level].get('categories')
				apps['desktops']=data[level].get('desktops')
				apps['hidden']=data[level].get('hidden')
				apps['keybinds']=data[level].get('keybinds')
				apps['password']=data[level].get('password')
				apps['close']=data[level].get('close')
				apps['startup']=data[level].get('startup')

			self._debug("Readed %s"%apps)

		if not apps['categories'] and not apps['desktops'] and load_categories:
			apps=default
		categories=apps.get('categories',None)
		if categories:
			for category in apps['categories']:
				cat_apps=self.get_category_desktops(category.lower())
				for app in cat_apps:
					if ((app not in apps['desktops']) and (app not in apps['hidden'])):
						apps['desktops'].append(app)
		return(apps)

	def get_category_desktops(self,category):
		apps=[]
		tmp_apps=[]
		self.menu.set_desktop_system()
		applist=self.menu.get_apps_from_category(category)
		for app,data in applist.items():
			if data['exe'] not in tmp_apps and app not in tmp_apps:
				apps.append("%s/%s"%(self.menu.desktoppath,app))
				tmp_apps.append(data['exe'])
				tmp_apps.append(app)
		self.menu.set_desktop_user()
		applist=(self.menu.get_apps_from_category(category))
		for app,data in applist.items():
			if data['exe'] not in tmp_apps and app not in tmp_apps:
				apps.append("%s/%s"%(self.menu.desktoppath,app))
				tmp_apps.append(data['exe'])
				tmp_apps.append(app)
		self.menu.set_desktop_system()
		return(apps)

	def get_category_apps(self,category):
		apps={}
		self.menu.set_desktop_system()
		applist=self.menu.get_apps_from_category(category)
		self.menu.set_desktop_user()
		applist.extend(self.menu.get_apps_from_category(category))
		for key,app in applist.items():
			if 'xdg-open' in app['exe']:
				app['exe']=app['exe'].replace("xdg-open",self.menu.get_default_app_for_file(app['exe'].split(" ")[-1]))
			apps[app['exe']]=app['icon']
		self.menu.set_desktop_system()
		return (apps)
	#def get_category_apps

	def get_desktop_app(self,f_desktop):
		apps={}
		app=self.menu.get_desktop_info(f_desktop)
		if 'xdg-open' in app['Exec']:
			app['Exec']=app['Exec'].replace("xdg-open",self.menu.get_default_app_for_file(app['Exec'].split(" ")[-1]))
		apps[app['Exec']]=app['Icon']
		return (apps)
	#def get_desktop_app

	def write_config(self,data,key=None,level=None):
		self.config.write_config(data,level=level,key=key)
	#def write_config
