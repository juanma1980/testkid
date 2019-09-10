#!/usr/bin/python3
import sys
import os
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,QLineEdit,QHBoxLayout
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from appconfig.appConfigStack import appConfigStack as confStack
import gettext
_ = gettext.gettext

class confN4d(confStack):
	def __init_stack__(self):
		self.dbg=True
		self.menu_description=(_("Configure N4d server"))
		self.description=(_("Configure n4d settings"))
		self.icon=('dialog-password')
		self.tooltip=(_("From here you can set the n4d settings"))
		self.enabled=True
		self.index=6
		self.sw_changes=False
		self.level='n4d'
#		self._load_screen()

	def _debug(self,msg):
		if self.dbg:
			print("ConfN4d: %s"%msg)
	#def _debug

	def _load_screen(self):
		box=QVBoxLayout()
		lbl_txt=QLabel(_("Apply n4d policies"))
		lbl_txt.setAlignment(Qt.AlignTop)
		box.addWidget(lbl_txt)
		box_btns=QHBoxLayout()
		btn_ok=QPushButton(_("Apply"))
		btn_ok.clicked.connect(self.writeConfig)
		btn_cancel=QPushButton(_("Cancel"))
		box_btns.addWidget(btn_ok)
		box_btns.addWidget(btn_cancel)
		box.addLayout(box_btns)
		self.setLayout(box)

	def writeConfig(self):
		pass
