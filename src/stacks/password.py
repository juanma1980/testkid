#!/usr/bin/python3
import sys
import os
from PySide2.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,QLineEdit,QHBoxLayout
from PySide2 import QtGui
from PySide2.QtCore import Qt
from passlib.hash import pbkdf2_sha256 as hashpwd
from appconfig.appConfigStack import appConfigStack as confStack
import gettext
_ = gettext.gettext

class password(confStack):
	def __init_stack__(self):
		self.dbg=False
		self.txt_pass=QLineEdit()
		self.txt_pass.setEchoMode(QLineEdit.Password)
		self.txt_pass.setPlaceholderText(_("Password"))
		self.txt_pass2=QLineEdit()
		self.txt_pass2.setPlaceholderText(_("Repeat password"))
		self.txt_pass2.setEchoMode(QLineEdit.Password)
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
		box.addWidget(lbl_txt,1)
		box.addWidget(self.txt_pass,1,Qt.AlignBottom)
		box.addWidget(self.txt_pass2,2,Qt.AlignTop)
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
