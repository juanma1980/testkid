#!/usr/bin/env python3
import getpass
import sys
import os
from PyQt5.QtCore import QSize,pyqtSlot,Qt, QPropertyAnimation,QThread,QRect,QTimer,pyqtSignal,QSignalMapper,QProcess
import subprocess
import signal
import time
import tempfile
from app2menu import App2Menu
QString=type("")


class th_runApp(QThread):
	signal=pyqtSignal("PyQt_PyObject")
	def __init__(self,app,display,parent=None):
		QThread.__init__(self,parent)
		self.display=display
		self.app=app.split(" ")
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
		app=app.replace("/usr/bin/resources-launcher.sh",App2Menu.app2menu().get_default_app_for_file(app.split(" ")[-1]))
		self.app=app.split(" ")
	#def _run_resource

	def run(self):
		retval=[False,None]
		tmp_file=""
		self._debug("Launching thread...")
		try:
			dsp=os.environ['DISPLAY']
			os.environ['DISPLAY']=self.display
			if "/usr/bin/resources-launcher.sh" in self.app:
				self._run_resource()
			if 'firefox' in self.app:
				self._run_firefox()
			elif (('chromium' in self.app) or ('chrome' in self.app)):
				self._run_chromium()
			p_pid=subprocess.Popen(self.app,stdin=None,stdout=None,stderr=None,shell=False)
			os.environ['DISPLAY']=dsp
			retval=[p_pid.pid,tmp_file]
		except Exception as e:
			print("Error running: %s"%e)
		self.signal.emit(retval)
	#def run
#class th_runApp


class appRun():
	signal=pyqtSignal("PyQt_PyObject")
	def __init__(self):
		self.dbg=True
		self.pid=0
		self.xephyr_servers={}
		self.username=getpass.getuser()
		self.main_display=os.environ['DISPLAY']
		self.topBarHeight=116
		self.categories={"lliurex-infantil":"applications-games","education":"applications-education"}
		self.threads_pid={}
		self.threads_tmp={}
	#def __init__

	def _debug(self,msg):
		if self.dbg:
			print("appRun: %s"%msg)
	#def _debug

	def set_topBarHeight(self,h):
		self.topBarHeight=h+20
	#def set_topBarHeight(self,h):

	def get_wid(self,search="Xephyr on",display=":13"):
		wid=0
		count=0
		if display in self.xephyr_servers.keys():
			self._debug("Search WID for server at display %s"%display)
			self._debug("PID searched: %s"%self.xephyr_servers[display])
			self._debug("User searched: %s"%self.username)
			while not wid and count<=150:
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
		self._debug("Send signal: %s"%s_signal)
		retval=False
		sig={'kill':signal.SIGKILL,'term':signal.SIGTERM,'stop':signal.SIGSTOP,'cont':signal.SIGCONT}
		if thread in self.threads_pid.keys():			
			try:
				os.kill(self.threads_pid[thread],sig[s_signal])
				retval=True
			except:
				self._debug("%s failed on thread %s with pid %s"%(s_signal,thread,self.threads_pid[thread]))

		elif (signal=='kill' or signal=='term'):
			if (type(thread)==type(0)):
				try:
					os.kill(self.threads_pid[thread],sig[s_signal])
					retval=True
				except:
					self._debug("%s failed on pid %s"%(s_signal,self.threads_pid[thread]))

		return(retval)

	def launch(self,app,display=":13"):
		def _get_th_pid(pid_info):
			self.threads_pid[th_run]=pid_info[0]
			self.threads_tmp[th_run]=pid_info[1]
		#launch wm
		self._debug("Launching WM for display %s"%display)
		th_run=th_runApp("ratpoison",display)
		th_run.start()
		th_run=th_runApp(app,display)
		th_run.start()
		th_run.signal.connect(_get_th_pid)
		return(th_run)
	#def launch
	
	def _find_free_display(self,display=":13"):
		count=int(display.replace(":",""))
		self._debug("Search %s"%count)
		while(os.path.isfile('/tmp/.X%s-lock'%count)):
				count+=1
		try:
				display=":%s"%count
		except Exception as e:
			print ("Err: %s"%e)
			display=":-1"
		return("%s"%display)
	#def _find_free_display
	
	def get_category_apps(self,category):
		apps={}
		applist=App2Menu.app2menu().get_apps_from_category(category)
		for key,app in applist.items():
			if 'xdg-open' in app['exe']:
				app['exe']=app['exe'].replace("xdg-open",App2Menu.app2menu().get_default_app_for_file(app['exe'].split(" ")[-1]))
			apps[app['exe']]=app['icon']
		return (apps)
	#def get_category_apps

