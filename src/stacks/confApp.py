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
		self.menu_description=(_("Choose the app behaviour"))
		self.description=(_("Set app behaviour"))
		self.icon=('dialog-password')
		self.tooltip=(_("From here you can set the behaviour of the app"))
		self.index=1
		self.enabled=True
		self.level='user'
		self.sw_changes=False
		self.close=None
		self.startup=None
#		self._load_screen()
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
		btn_ok.clicked.connect(self.writeConfig)
		btn_cancel=QPushButton(_("Cancel"))
		box_btns.addWidget(btn_ok)
		box_btns.addWidget(btn_cancel)
		box.addLayout(box_btns)
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
		if self.close:
			if self.close=='true':
				self.chk_close.setChecked(True)
		if self.startup:
			if self.startup=='true':
				self.chk_startup.setChecked(True)
	#def _udpate_screen
	
	def writeConfig(self):
		configLevel=self.cmb_level.currentText().lower()
		self.saveChanges('config',configLevel,'system')
		startup=self.chk_startup.isChecked()
		self.saveChanges('startup',startup)
		close=self.chk_close.isChecked()
		self.saveChanges('close',close)
	#def writeConfig

