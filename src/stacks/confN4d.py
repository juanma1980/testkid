#!/usr/bin/python3
import sys
import os
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,QLineEdit,QHBoxLayout
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
import gettext
from libAppRun import appRun

_ = gettext.gettext

class confN4d(QWidget):
	def __init__(self):
		super().__init__()
		self.dbg=True
		self.runner=appRun()
		self.menu_description=(_("Configure N4d server"))
		self.description=(_("Configure n4d settings"))
		self.icon=('dialog-password')
		self.tooltip=(_("From here you can set the n4d settings"))
		self.enabled=True
		self.index=6
		self.sw_changes=False
		self.level='n4d'
		self._load_screen()

	def _debug(self,msg):
		if self.dbg:
			print("ConfN4d: %s"%msg)
	#def _debug

	def set_textDomain(self,textDomain):
		gettext.textdomain(textDomain)
	#def set_textDomain

	def set_configLevel(self,level):
		self.level=level
	#def set_configLevel

	def _load_screen(self):
		box=QVBoxLayout()
		lbl_txt=QLabel(_("Apply n4d policies"))
		lbl_txt.setAlignment(Qt.AlignTop)
		box.addWidget(lbl_txt)
		box_btns=QHBoxLayout()
		btn_ok=QPushButton(_("Apply"))
		btn_ok.clicked.connect(self._save_config)
		btn_cancel=QPushButton(_("Cancel"))
		box_btns.addWidget(btn_ok)
		box_btns.addWidget(btn_cancel)
		box.addLayout(box_btns)
		self.setLayout(box)

	def _save_config(self):
		pwd=self._get_data(self)
		self.runner.write_config(pwd,key='password',level=self.level)
		self.sw_changes=False
	#def _save_apps

	def _get_data(self):
		pwd=self.txt_pass.text()
		pwd=hashpwd.hash(pwd)
		return(pwd)
	
	def get_changes(self):
		return (self.sw_changes)
