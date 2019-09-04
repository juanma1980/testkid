#!/usr/bin/python3
import sys
import os
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,QLineEdit,QHBoxLayout,QComboBox
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from passlib.hash import pbkdf2_sha256 as hashpwd
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
		self.sw_changes=False
	
	def _debug(self,msg):
		if self.dbg:
			print("ConfApp: %s"%msg)
	#def _debug
	
	def set_textDomain(self,textDomain):
		gettext.textdomain(textDomain)
	#def set_textDomain

	def _load_screen(self):
		def _change_osh():
			txt=cmb_level.currentText()
			if txt=='User':
				lbl_help.setText(_("The config will be applied per user"))
			elif txt=='System':
				lbl_help.setText(_("The config will be applied to all users"))
			elif txt=='N4d':
				lbl_help.setText(_("The config will be applied to all users and clients"))
		box=QVBoxLayout()
		lbl_txt=QLabel(_("Choose the config level that should use the app"))
		lbl_txt.setAlignment(Qt.AlignTop)
		box.addWidget(lbl_txt)
		cmb_level=QComboBox()
		cmb_level.addItem("User")
		cmb_level.addItem("System")
		cmb_level.addItem("N4d")
		cmb_level.activated.connect(_change_osh)
		box.addWidget(cmb_level)
		lbl_help=QLabel(_(""))
		_change_osh()
		box.addWidget(lbl_help)

		box_btns=QHBoxLayout()
		btn_ok=QPushButton(_("Apply"))
		btn_ok.clicked.connect(self._save_pass)
		btn_cancel=QPushButton(_("Cancel"))
		box_btns.addWidget(btn_ok)
		box_btns.addWidget(btn_cancel)
		box.addLayout(box_btns)
		self.setLayout(box)
	
	def _save_pass(self):
#		pwd=self.txt_pass.text()
#		pwd=hashpwd.hash(pwd)
#		self.runner.write_config(pwd,key='password',level='n4d')
		pass
	#def _save_apps

	def get_changes(self):
		return (self.sw_changes)
