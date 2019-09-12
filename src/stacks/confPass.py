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
		self.level='user'
	
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
		self.setLayout(box)
	
	def writeConfig(self):
		pwd=self.txt_pass.text()
		if pwd==self.txt_pass2.text() and pwd.replace(' ','')!='':
			pwd=hashpwd.hash(pwd)
			key='password'
			self.saveChanges(key,pwd)
		elif pwd==self.txt_pass2.text:
			self._debug("Password don't match")
			self.showMsg(_("Passwords don't match"))
		else:
			self._debug("Blank Password")
			self.showMsg(_("Password is empty"))
	#def _save_apps

	def updateScreen(self):
		self.txt_pass.setText('')
		self.txt_pass2.setText('')
	#def updateScreen
