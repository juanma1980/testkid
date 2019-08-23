#!/usr/bin/python3

import sys
import os
import subprocess
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,QLineEdit,QHBoxLayout,QGridLayout,QComboBox,QFileDialog
from PyQt5 import QtGui
from PyQt5.QtCore import Qt,pyqtSignal,QSignalMapper,QProcess,QEvent,QSize
import gettext
from libAppRun import appRun
import gettext
from app2menu import App2Menu
from libAppRun import appRun

gettext.textdomain('testConfig')
_ = gettext.gettext

class confDesktops(QWidget):
	def __init__(self):
		super().__init__()
		self.dbg=True
		self.runner=appRun()
		self.menu=App2Menu.app2menu()
		home=os.environ['HOME']
		self.menu.desktoppath="%s/.local/share/applications/"%home
		self.icon='shell'
		self._load_screen()
	#def __init__
		
	def _debug(self,msg):
		if self.dbg:
			print("ConfDesktops: %s"%msg)
	#def _debug

	def _load_screen(self):
		def _save_desktop():
			if not os.path.isdir(self.menu.desktoppath):
				os.makedirs(self.menu.desktoppath)
			categories=[]
			desktop={}
			desktop['Name']=inp_name.text()
			desktop['Exec']=inp_exec.text()
			desktop['Categories']='run-o-matic;'
			desktop['Icon']=self.icon
			desktop['Comment']=inp_desc.text()
			desktop['NoDisplay']='True'
			self._debug("Saving %s"%desktop)
			try:
				self.menu.write_custom_desktop(desktop,self.menu.desktoppath)
			except Exception as e:
				self._debug(e)
		#def _save_desktop

		box=QGridLayout()
		lbl_txt=QLabel(_("From here you can add Launchers"))
		box.addWidget(lbl_txt)
		lbl_icon=QLabel(_("Icon: "))
		box.addWidget(lbl_icon,1,2,1,1)
		btn_icon=QPushButton()
		btn_icon.setObjectName("btnIcon")
		icn_desktop=QtGui.QIcon.fromTheme("shell")
		btn_icon.setIcon(icn_desktop)
		btn_icon.setIconSize(QSize(64,64))
		btn_icon.setToolTip(_("Push to change icon"))
		btn_icon.clicked.connect(lambda:self._file_chooser(widget=btn_icon,path="/usr/share/icons",imgDialog=True))
		box.addWidget(btn_icon,2,2,3,1,Qt.AlignTop)
		lbl_name=QLabel(_("Name: "))
		box.addWidget(lbl_name,1,0,1,2)
		inp_name=QLineEdit()
		inp_name.setPlaceholderText(_("Desktop name"))
		inp_name.setToolTip(_("Insert desktop name"))
		box.addWidget(inp_name,2,0,1,2)
		lbl_exec=QLabel(_("Executable: "))
		box.addWidget(lbl_exec,3,0,1,2)
		inp_exec=QLineEdit()
		inp_exec.setPlaceholderText(_("Executable path"))
		inp_exec.setToolTip(_("Insert path to the executable"))
		box.addWidget(inp_exec,4,0,1,1,Qt.Alignment(0))
		btn_exec=QPushButton("...")
		btn_exec.setObjectName("btnFile")
		btn_exec.setToolTip(_("Press button to select an executable"))
		btn_exec.clicked.connect(lambda:self._file_chooser(widget=inp_exec,path="/usr/bin"))
		box.addWidget(btn_exec,4,1,1,1,Qt.Alignment(1))
		lbl_desc=QLabel(_("Description: "))
		box.addWidget(lbl_desc,5,0,1,2)
		inp_desc=QLineEdit()
		inp_desc.setPlaceholderText(_("Description"))
		inp_desc.setToolTip(_("Insert a description for the app"))
		box.addWidget(inp_desc,6,0,1,3)
#		lbl_cat=QLabel(_("Category: "))
#		box.addWidget(lbl_cat,7,0,1,2)
#		cmb_cat=QComboBox()
#		data=self.runner.get_apps()
#		for cat in data['categories']:
#			cmb_cat.addItem(cat)
#		box.addWidget(cmb_cat,8,0,1,2,Qt.AlignLeft)
		btn_apply=QPushButton(_("Apply"))
		btn_apply.setToolTip(_("Save desktop"))
		btn_apply.setIconSize(QSize(48,48))
		btn_apply.clicked.connect(_save_desktop)
		box.addWidget(btn_apply,9,2,1,1,Qt.Alignment(2))
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
					self.icon=fdia.selectedFiles()[0]
					icn=QtGui.QIcon(self.icon)
					widget.setIcon(icn)
				else:
					widget.setText(fchoosed)
			return(fchoosed)
