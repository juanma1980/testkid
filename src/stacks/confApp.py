#!/usr/bin/python3
import sys
import os
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,QLineEdit,QHBoxLayout,QComboBox,QCheckBox
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
import gettext
from libAppRun import appRun

_ = gettext.gettext

class confApp(QWidget):
	def __init__(self):
		super().__init__()
		self.dbg=True
		self.menu_description=(_("Choose the app behaviour"))
		self.description=(_("Set app behaviour"))
		self.icon=('dialog-password')
		self.tooltip=(_("From here you can set the behaviour of the app"))
		self.index=1
		self.runner=appRun()
		self._load_screen()
		self.enabled=True
		self.level='user'
		self.sw_changes=False
	#def __init__
	
	def _debug(self,msg):
		if self.dbg:
			print("ConfApp: %s"%msg)
	#def _debug
	
	def set_textDomain(self,textDomain):
		gettext.textdomain(textDomain)
	#def set_textDomain
	
	def get_config(self):
		data=self.runner.get_default_config()
		self.level=data['system']['config']
		self.close=data['system'].get('close',None)
		self.startup=data['system'].get('startup',None)
	#def get_config

	def _load_screen(self):
		def _change_osh():
			txt=self.cmb_level.currentText()
			if txt=='User':
				lbl_help.setText(_("The config will be applied per user"))
			elif txt=='System':
				lbl_help.setText(_("The config will be applied to all users"))
			elif txt=='N4d':
				lbl_help.setText(_("The config will be applied to all users and clients"))
			self.sw_changes=True
		box=QVBoxLayout()
		lbl_txt=QLabel(_("Choose the config level that should use the app"))
		lbl_txt.setAlignment(Qt.AlignTop)
		box.addWidget(lbl_txt)
		self.cmb_level=QComboBox()
		self.cmb_level.addItem("User")
		self.cmb_level.addItem("System")
		self.cmb_level.addItem("N4d")
		self.cmb_level.activated.connect(_change_osh)
		box.addWidget(self.cmb_level)
		lbl_help=QLabel(_(""))
		_change_osh()
		box.addWidget(lbl_help)
		self.chk_startup=QCheckBox("Launch at startup")
		box.addWidget(self.chk_startup)
		self.chk_close=QCheckBox("Close session when application exits")
		box.addWidget(self.chk_close)

		box_btns=QHBoxLayout()
		btn_ok=QPushButton(_("Apply"))
		btn_ok.clicked.connect(self.write_config)
		btn_cancel=QPushButton(_("Cancel"))
		box_btns.addWidget(btn_ok)
		box_btns.addWidget(btn_cancel)
		box.addLayout(box_btns)
		self.setLayout(box)
		self.update_screen()
	#def _load_screen
	
	def update_screen(self):
		self.get_config()
		if self.level:
			idx=0
			if self.level.lower()=='system':
				idx=1
			elif self.level.lower()=='n4d':
				idx=2
			self.cmb_level.setCurrentIndex(idx)
			self.cmb_level.activated.emit(idx)
		if self.close:
			if self.close=='true':
				self.chk_close.setChecked(True)
		if self.startup:
			if self.startup=='true':
				self.chk_startup.setChecked(True)
	#def _udpate_screen
	
	def write_config(self):
		configLevel=self.cmb_level.currentText().lower()
		startup=self.chk_startup.isChecked()
		close=self.chk_close.isChecked()
		self.runner.write_config(configLevel,key='config',level='system')
		self.runner.write_config(startup,key='startup',level='system')
		self.runner.write_config(close,key='close',level='system')
	#def write_config

	def get_changes(self):
		return (self.sw_changes)
