#!/usr/bin/python3
import sys
import os
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,QLineEdit,QHBoxLayout
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from passlib.hash import pbkdf2_sha256 as hashpwd
from appconfig.appConfigStack import appConfigStack as confStack
import gettext
_ = gettext.gettext

class confPass(confStack):
	def __init_stack__(self):
		self.dbg=True
		self.txt_pass=QLineEdit()
		self.txt_pass.setPlaceholderText(_("Password"))
		self.txt_pass2=QLineEdit()
		self.txt_pass2.setPlaceholderText(_("Repeat password"))
		self.menu_description=(_("Set a master password"))
		self.description=(_("Set master password"))
		self.icon=('dialog-password')
		self.tooltip=(_("From here you can set the master password"))
		self.enabled=True
		self.index=5
		self.sw_changes=False
		self.level='user'
#		self._load_screen()
	
	def _debug(self,msg):
		if self.dbg:
			print("ConfPass: %s"%msg)
	#def _debug

	def _load_screen(self):
		box=QVBoxLayout()
		lbl_txt=QLabel(_("If a master password is set then the app will prompt for it to exit"))
		lbl_txt.setAlignment(Qt.AlignTop)
		box.addWidget(lbl_txt)
		box.addWidget(self.txt_pass)
		box.addWidget(self.txt_pass2)
		box_btns=QHBoxLayout()
		btn_ok=QPushButton(_("Apply"))
		btn_ok.clicked.connect(self.writeConfig)
		btn_cancel=QPushButton(_("Cancel"))
		box_btns.addWidget(btn_ok)
		box_btns.addWidget(btn_cancel)
		box.addLayout(box_btns)
		self.setLayout(box)
	
	def writeConfig(self):
		pwd=self.txt_pass.text()
		if pwd==self.txt_pass2.text():
			pwd=hashpwd.hash(pwd)
			key='password'
			self.saveChanges(key,pwd)
		else:
			self._debug("Pâssword don't match")
	#def _save_apps
	
