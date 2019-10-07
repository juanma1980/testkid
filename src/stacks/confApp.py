#!/usr/bin/python3
import sys
import os
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,QLineEdit,QHBoxLayout,QComboBox,QCheckBox
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from appconfig.appConfigStack import appConfigStack as confStack

import gettext
_ = gettext.gettext

class confApp(confStack):
	def __init_stack__(self):
		self.dbg=False
		self._debug("confApp Load")
		self.menu_description=(_("Choose the app behaviour"))
		self.description=(_("Set app behaviour"))
		self.icon=('dialog-password')
		self.tooltip=(_("From here you can set the behaviour of the app"))
		self.index=1
		self.enabled=True
		self.level='user'
	#def __init__
	
	def _load_screen(self):
		def _change_osh():
			txt=self.cmb_level.currentText()
			if txt=='User':
				lbl_help.setText(_("The config will be applied per user"))
			elif txt=='System':
				lbl_help.setText(_("The config will be applied to all users"))
			elif txt=='N4d':
				lbl_help.setText(_("The config will be applied to all users and clients"))
		box=QVBoxLayout()
		lbl_txt=QLabel(_("Choose the config level that should use the app"))
		lbl_txt.setAlignment(Qt.AlignTop)
		box.addWidget(lbl_txt,0)
		self.cmb_level=QComboBox()
		self.cmb_level.addItem("User")
		self.cmb_level.addItem("System")
		self.cmb_level.addItem("N4d")
		self.cmb_level.activated.connect(_change_osh)
		self.cmb_level.setFixedWidth(100)
		box.addWidget(self.cmb_level,1,Qt.AlignLeft)
		lbl_help=QLabel(_(""))
		_change_osh()
		box.addWidget(lbl_help,1,Qt.AlignTop)
		self.chk_startup=QCheckBox("Launch at startup")
		box.addWidget(self.chk_startup,1,Qt.AlignTop)
		self.chk_close=QCheckBox("Close session when application exits")
		box.addWidget(self.chk_close,2,Qt.AlignTop)

		self.setLayout(box)
		self.updateScreen()
		return(self)
	#def _load_screen

	def updateScreen(self):
		config=self.getConfig()
		if self.level:
			idx=0
			if self.level.lower()=='system':
				idx=1
			elif self.level.lower()=='n4d':
				idx=2
			self.cmb_level.setCurrentIndex(idx)
			self.cmb_level.activated.emit(idx)
		close=config[self.level].get('close',False)
		if close:
			if close.lower()=='true':
				close=True
			else:
				close=False
		self.chk_close.setChecked(close)
		startup=config[self.level].get('startup',False)
		if startup:
			if startup.lower()=='true':
				startup=True
			else:
				startup=False
		self.chk_startup.setChecked(startup)
	#def _udpate_screen
	
	def writeConfig(self):
		sw_ko=False
		level=self.level
		configLevel=self.cmb_level.currentText().lower()
		if configLevel!=level:
			if not self.saveChanges('config',configLevel,'system'):
				self.saveChanges('config',level,'system')
				sw_ko=True
		if sw_ko==False:
			startup=self.chk_startup.isChecked()
			if self.saveChanges('startup',startup):
				close=self.chk_close.isChecked()
				if not self.saveChanges('close',close):
					sw_ko=True
			else:
				sw_ko=True
		else:
			sw_ko=True
	#def writeConfig

