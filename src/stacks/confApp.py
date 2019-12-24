#!/usr/bin/python3
import sys
import os
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,QLineEdit,QHBoxLayout,QComboBox,QCheckBox,QFileDialog
from PyQt5 import QtGui
from PyQt5.QtCore import Qt,QSize
from appconfig.appConfigStack import appConfigStack as confStack

import gettext
_ = gettext.gettext

class confApp(confStack):
	def __init_stack__(self):
		self.dbg=True
		self._debug("confApp Load")
		self.menu_description=(_("Choose the app behaviour"))
		self.description=(_("Set app behaviour"))
		self.icon=('dialog-password')
		self.tooltip=(_("From here you can set the behaviour of the app"))
		self.bg="/usr/share/runomatic/rsrc/background2.png"
		self.defaultBg="/usr/share/runomatic/rsrc/background2.png"
		self.index=1
		self.enabled=True
		self.level=''
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
			self.fakeUpdate()
		box=QVBoxLayout()
		lbl_txt=QLabel(_("Choose the config level that should use the app"))
		lbl_txt.setAlignment(Qt.AlignTop)
		box.addWidget(lbl_txt,0)
		wdg_level=QWidget()
		hbox=QHBoxLayout()
		self.cmb_level=QComboBox()
		self.cmb_level.addItem("User")
		self.cmb_level.addItem("System")
		self.cmb_level.addItem("N4d")
		self.cmb_level.activated.connect(_change_osh)
		self.cmb_level.setFixedWidth(100)
		hbox.addWidget(self.cmb_level,1,Qt.AlignLeft)
		lbl_help=QLabel(_(""))
		hbox.addWidget(lbl_help,1,Qt.AlignTop)
		wdg_level.setLayout(hbox)
		box.addWidget(wdg_level,1,Qt.AlignLeft)
		box.addWidget(QLabel(_("Session settings")),1,Qt.AlignTop)
		self.chk_startup=QCheckBox("Launch at startup")
		box.addWidget(self.chk_startup,1,Qt.AlignTop)
		self.chk_close=QCheckBox("Close session when application exits")
		box.addWidget(self.chk_close,2,Qt.AlignTop)
		lbl_img=QLabel(_("Choose the background image"))
		box.addWidget(lbl_img,Qt.AlignTop)
		icn=QtGui.QIcon(self.bg)
		self.btn_img=QPushButton()
		self.btn_img.setStyleSheet("border:1px solid black;")
		self.btn_img.clicked.connect(self._setBg)
		self.btn_img.setIcon(icn)
		self.btn_img.setIconSize(QSize(102,76))
		box.addWidget(self.btn_img,Qt.AlignTop)
		self.setLayout(box)
		_change_osh()
		self.updateScreen()
		return(self)
	#def _load_screen

	def fakeUpdate(self):
		level=self.cmb_level.currentText().lower()
		print("*****")
		print(level)
		config=self.getConfig(level)
		print(config)
		print("*****")
		close=False
		if level in config.keys():
			close=config[level].get('close',False)
		if close:
			if str(close).lower()=='true':
				close=True
			else:
				close=False
		try:
			self.chk_close.setChecked(close)
		except:
			pass
		startup=config[level].get('startup',False)
		if startup:
			if str(startup).lower()=='true':
				startup=True
			else:
				startup=False
		try:
			self.chk_startup.setChecked(startup)
		except:
			pass
		bg=config[level].get('background',self.defaultBg)
		if bg:
			if os.path.isfile(bg):
				icon=QtGui.QIcon(bg)
				self.btn_img.setIcon(icon)
	#def fakeUpdate

	def updateScreen(self):
		print(self.level)
		config=self.getConfig()
		print("++++++++++++++++++")
		print(self.level)
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
			if str(close).lower()=='true':
				close=True
			else:
				close=False
		self.chk_close.setChecked(close)
		startup=config[self.level].get('startup',False)
		if startup:
			if str(startup).lower()=='true':
				startup=True
			else:
				startup=False
		self.chk_startup.setChecked(startup)
		bg=config[self.level].get('background',self.defaultBg)
		if bg:
			if os.path.isfile(bg):
				icon=QtGui.QIcon(bg)
				self.btn_img.setIcon(icon)
	#def _udpate_screen

	def _setBg(self):
		self._debug("Changing background")
		fdia=QFileDialog()
		fchoosed=''
		fdia.setFileMode(QFileDialog.AnyFile)
		fdia.setNameFilter(_("images(*.png *.svg *jpg *bmp)"))
		if (fdia.exec_()):
			fchoosed=fdia.selectedFiles()[0]
			self.bg=fdia.selectedFiles()[0]
			icn=QtGui.QIcon(self.bg)
			self.btn_img.setIcon(icn)
			return(fchoosed)
	#def _setBg(self)
	
	def writeConfig(self):
		level=self.level
		configLevel=self.cmb_level.currentText().lower()
		if configLevel!=level:
			if not self.saveChanges('config',configLevel,'system'):
				self.saveChanges('config',level,'system')
			else:
				return()
		startup=self.chk_startup.isChecked()
		self.saveChanges('startup',startup)
		close=self.chk_close.isChecked()
		self.saveChanges('close',close)
		self.saveChanges('background',self.bg)
	#def writeConfig

