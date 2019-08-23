#!/usr/bin/python3
import sys
import os
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,QLineEdit,QHBoxLayout
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from passlib.hash import pbkdf2_sha256 as hashpwd
import gettext
from libAppRun import appRun
import gettext
from app2menu import App2Menu
from libAppRun import appRun

gettext.textdomain('testConfig')
_ = gettext.gettext

class confPass(QWidget):
	def __init__(self):
		super().__init__()
		self.dbg=True
		self.runner=appRun()
		self.txt_pass=QLineEdit()
		self.txt_pass.setPlaceholderText(_("Password"))
		self.txt_pass2=QLineEdit()
		self.txt_pass2.setPlaceholderText(_("Repeat password"))
		self._load_screen()

	def _load_screen(self):
		box=QVBoxLayout()
		lbl_txt=QLabel(_("If a master password is set then the app will prompt for it to exit"))
		lbl_txt.setAlignment(Qt.AlignTop)
		box.addWidget(lbl_txt)
		box.addWidget(self.txt_pass)
		box.addWidget(self.txt_pass2)
		box_btns=QHBoxLayout()
		btn_ok=QPushButton(_("Apply"))
		btn_ok.clicked.connect(self._save_pass)
		btn_cancel=QPushButton(_("Cancel"))
		box_btns.addWidget(btn_ok)
		box_btns.addWidget(btn_cancel)
		box.addLayout(box_btns)
		self.setLayout(box)
	
	def _save_pass(self):
		pwd=self.txt_pass.text()
		pwd=hashpwd.hash(pwd)
		self.runner.write_config(pwd,key='password',level='user')
	#def _save_apps
