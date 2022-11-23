#!/usr/bin/python3

import os
import shutil
import subprocess
import tarfile
import tempfile
import base64
from PySide2.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,QLineEdit,QHBoxLayout,QGridLayout,QComboBox,QFileDialog
from PySide2 import QtGui
from PySide2.QtCore import Qt,Signal,QSignalMapper,QProcess,QEvent,QSize
from app2menu import App2Menu
from appconfig.appConfigStack import appConfigStack as confStack
from urllib.request import Request,urlopen,urlretrieve
from bs4 import BeautifulSoup
import re
import gettext
_ = gettext.gettext

class launchers(confStack):
	def __init_stack__(self):
		self.dbg=False
		self._debug("confDesktops Load")
		self.menu=App2Menu.app2menu()
		home=os.environ['HOME']
#		self.menu.desktoppath="%s/.local/share/applications/"%home
		self.menu.desktoppath="/usr/share/runomatic/applications"
		if not os.path.isdir(self.menu.desktoppath):
			try:
				os.makedirs(self.menu.desktoppath)
			except:
				print("Failed to create path %s"%self.menu.desktoppath)
		self.userRunoapps="%s/.config/runomatic/applications"%os.environ['HOME']
		if not os.path.isdir(self.userRunoapps):
			os.makedirs(self.userRunoapps)
		self.default_icon='shell'
		self.app_icon='shell'
		self.menu_description=(_("Add new launchers"))
		self.description=(_("Add launcher (expert mode)"))
		self.icon=('org.kde.plasma.quicklaunch')
		self.tooltip=(_("From here you can add a custom launcher"))
		self.defaultName=""
		self.defaultExec=""
		self.defaultDesc=""
		self.index=3
		self.enabled=True
		self.filename=""
		self.level='user'
		self.editBtn=False
	#def __init__
		
	def _debug(self,msg):
		if self.dbg:
			print("ConfDesktops: %s"%msg)
	#def _debug

	def initScreen(self):
		self.default_icon='shell'
		self.defaultName=""
		self.defaultExec=""
		self.defaultDesc=""
		self.filename=""
	#def initScreen


	def _load_screen(self):
		box=QGridLayout()
		lbl_txt=QLabel(_("From here you can add Launchers"))
		box.addWidget(lbl_txt)
		lbl_icon=QLabel(_("Icon: "))
		box.addWidget(lbl_icon,1,2,1,1)
		self.btn_icon=QPushButton()
		self.btn_icon.setObjectName("btnIcon")
		icn_desktop=QtGui.QIcon.fromTheme("shell")
		self.btn_icon.setIcon(icn_desktop)
		self.btn_icon.setIconSize(QSize(64,64))
		self.btn_icon.setToolTip(_("Push to change icon"))
		self.btn_icon.clicked.connect(lambda:self._file_chooser(widget=self.btn_icon,path="/usr/share/icons",imgDialog=True))
		box.addWidget(self.btn_icon,2,2,3,1,Qt.AlignTop)
		lbl_name=QLabel(_("Name: "))
		box.addWidget(lbl_name,1,0,1,2,Qt.AlignBottom)
		self.inp_name=QLineEdit()
		self.inp_name.setPlaceholderText(_("Desktop name"))
		self.inp_name.setToolTip(_("Insert desktop name"))
		box.addWidget(self.inp_name,2,0,1,2,Qt.AlignTop)
		lbl_exec=QLabel(_("Executable: "))
		box.addWidget(lbl_exec,3,0,1,2,Qt.AlignTop)
		wdg=QWidget()
		hbox=QHBoxLayout()
		wdg.setLayout(hbox)
		self.inp_exec=QLineEdit()
		self.inp_exec.editingFinished.connect(self._get_icon)
		self.inp_exec.setPlaceholderText(_("Executable path"))
		self.inp_exec.setToolTip(_("Insert path to the executable"))
		self.inp_exec.setStyleSheet("margin:0px")
		hbox.addWidget(self.inp_exec,Qt.Alignment(0))
		btn_exec=QPushButton("...")
		btn_exec.setObjectName("btnFile")
		btn_exec.setToolTip(_("Press button to select an executable"))
		btn_exec.clicked.connect(lambda:self._file_chooser(widget=self.inp_exec,path="/usr/bin"))
		btn_exec.setStyleSheet("margin:0px")
		hbox.addWidget(btn_exec)
		box.addWidget(wdg,4,0,2,1,Qt.AlignTop)
		lbl_desc=QLabel(_("Description: "))
		box.addWidget(lbl_desc,5,0,1,2,Qt.AlignBottom)
		self.inp_desc=QLineEdit()
		self.inp_desc.setPlaceholderText(_("Description"))
		self.inp_desc.setToolTip(_("Insert a description for the app"))
		box.addWidget(self.inp_desc,6,0,1,Qt.AlignTop)
		self.setLayout(box)
	
	def _file_chooser(self,widget=None,path=None,imgDialog=None):
		fdia=QFileDialog()
		fchoosed=''
		fdia.setFileMode(QFileDialog.AnyFile)
		if imgDialog:
			fdia.setNameFilter(_("images(*.png *.xpm *jpg)"))
		else:
			fdia.setNameFilter(_("All files(*.*)"))
		if path:
			self._debug("Set path to %s"%path)
			fdia.setDirectory(path)
		if (fdia.exec_()):
			fchoosed=fdia.selectedFiles()[0]
			if widget:
				if imgDialog:
					self.app_icon=fdia.selectedFiles()[0]
					icn=QtGui.QIcon(self.app_icon)
					widget.setIcon(icn)
				else:
					widget.setText(fchoosed)
			self.btn_ok.setEnabled(True)
			self.btn_cancel.setEnabled(True)
			return(fchoosed)
	#def _file_chooser

	def _get_icon(self):
		txt=self.inp_exec.text()
		if txt.startswith("http"):
			txt="firefox %s"%txt
		exeLine=txt.split(' ')
		self._debug("Analize {}".format(exeLine))
		if 'firefox' not in exeLine and 'chromium' not in exeLine and 'chrome' not in exeLine :
			return
		path=exeLine[-1]
		path=path.split(" ")[0]
		splitPath=path.split("/")
		if "://" in path:
			path=("%s//%s"%(splitPath[0],splitPath[2]))
		else:
			path=("http://%s"%(splitPath[0]))
		try:
			self._debug("Requesting %s"%path)
			req=Request(path)
		except Exception as e:
			self._debug("Couldn't build url: %s"%(e))
			return
		ico=""
		try:
			content=urlopen(req,timeout=2).read()
			soup=BeautifulSoup(content,'html.parser')
			favicon=soup.head
			for link in favicon.find_all(href=re.compile("favicon")):
				fname=link
				if "favicon" in str(fname):
					self._debug("Favicon {}".format(fname))
					splitName=str(fname).split(" ")
					for splitWord in splitName:
						if splitWord.startswith("href="):
							ico=splitWord.split("\"")[1].split("?")[0]
							outputIco="/tmp/%s.ico"%splitPath[-1]
							self._debug("Favicon {}".format(outputIco))
							try:
								urlretrieve(ico,outputIco)
							except:
								return
							self.app_icon=ico
							icn=QtGui.QIcon(outputIco)
							self.btn_icon.setIcon(icn)
							break
		except Exception as e:
			self._debug("Couldn't open %s: %s"%(req,e))
		finally:
			self._debug("Selected icon: {}".format(self.app_icon))
	#def _get_icon


	def updateScreen(self):
		self.inp_name.setText(self.defaultName)
		self.inp_exec.setText(self.defaultExec)
		self.inp_desc.setText(self.defaultDesc)
		self.app_icon=self.default_icon
		icn=QtGui.QIcon.fromTheme(self.app_icon)
		self.btn_icon.setIcon(icn)
	#def updateScreen

	def writeConfig(self):
		categories=[]
		desktop={}
		desktop['Categories']='run-o-matic;'
		desktop['NoDisplay']='True'
		desktop['Name']=self.inp_name.text()
		txt=self.inp_exec.text()
		if txt.startswith("http"):
			txt="firefox %s"%txt
		desktop['Exec']=txt
		desktop['Icon']=self.app_icon
		desktop['Comment']=self.inp_desc.text()

		if self.level=="user":
			self.menu.desktoppath="{}/.config/runomatic/applications".format(os.environ.get('HOME'))
			if not os.path.isdir(self.menu.desktoppath):
				try:
					os.makedirs(self.menu.desktoppath)
				except:
					print("Failed to create path %s"%self.menu.desktoppath)

		if self.filename:
			filename=os.path.join(self.menu.desktoppath,"%s"%self.filename)
		else:
			filename=os.path.join(self.menu.desktoppath,"%s.desktop"%self.inp_name.text().lower().replace(" ","_"))
		self._debug("File %s"%filename)
		self._debug("Saving %s"%desktop)
		self.changes=False
		try:
			if self.level=="user":
				subprocess.check_call(["/usr/share/app2menu/app2menu-helper.py",desktop['Name'],desktop['Icon'],desktop['Comment'],desktop['Categories'],desktop['Exec'],filename])
			else:
				subprocess.check_call(["pkexec","/usr/share/app2menu/app2menu-helper.py",desktop['Name'],desktop['Icon'],desktop['Comment'],desktop['Categories'],desktop['Exec'],filename])
		except Exception as e:
			print("Error saving desktop %s"%filename)
			self._debug("Error  saving %s: %s"%(filename,e))
		#Copy newd desktop to userRunoapps
		runoName="%s/%s"%(self.userRunoapps,os.path.basename(filename))
		if filename!=runoName:
			shutil.copy(filename,runoName)

		#Save all runomatic desktops as base64
		#self._tar_runodesktops()
			
		self.btn_ok.setEnabled(False)
		self.btn_cancel.setEnabled(False)
		self.refresh=True
		retval=True
		if self.editBtn:
			self._reset_screen(filename)
	#def writeConfig

	def _tar_runodesktops(self):
		tarFile=tempfile.mkstemp(suffix=".tar.gz")[1]
		with tarfile.open(tarFile,"w:gz") as tar:
			for deskFile in os.listdir(self.userRunoapps):
				tar.add("%s/%s"%(self.userRunoapps,deskFile))
		with open(tarFile,"rb") as tar:
			self.saveChanges('runotar',base64.b64encode(tar.read()).decode("utf-8"))

	def _reset_screen(self,filename):
		if "runomatic" not in self.editBtn:
			hidden=self.config[self.level].get("hidden",[])
			hidden.append(self.editBtn)
			self.saveChanges('hidden',hidden)
			desktops=self.config[self.level].get("desktops",[])
			if self.editBtn in desktops:
				idx=desktops.index(self.editBtn)
				desktops.remove(self.editBtn)
				desktops.insert(idx,filename)
				self.saveChanges('desktops',desktops)
		self.default_icon='shell'
		self.defaultName=""
		self.defaultExec=""
		self.defaultDesc=""
		self.editBtn=False
		self.stack.gotoStack(idx=2,parms=self.editBtn)

	def setParms(self,parms):
		self._debug("Loading %s"%parms)
		desktop=self.menu.get_desktop_info(parms)
		self.filename=os.path.basename(parms)
		self.defaultName=desktop['Name']
		self.defaultExec=desktop['Exec']
		self.defaultDesc=desktop['Comment']
		self.default_icon=desktop['Icon']

		self.inp_name.setText(desktop['Name'])
		self.inp_exec.setText(desktop['Exec'])
		self.inp_desc.setText(desktop['Comment'])
		self.app_icon=desktop['Icon']
		if os.path.isfile(desktop['Icon']):
			icn=QtGui.QIcon(desktop['Icon'])
		else:
			icn=QtGui.QIcon.fromTheme(desktop['Icon'])
		self.btn_icon.setIcon(icn)
		self.btn_ok.setEnabled(False)
		self.btn_cancel.setEnabled(False)
		self.editBtn=parms
	#def setParms
