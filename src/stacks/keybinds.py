#!/usr/bin/python3
import sys
import os
from PySide2.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,QLineEdit,QHBoxLayout,QGridLayout,QComboBox
from PySide2 import QtGui
from PySide2.QtCore import Qt,Signal,QSignalMapper,QProcess,QEvent,QSize
from appconfig.appConfigStack import appConfigStack as confStack
from appconfig.appconfigControls import QHotkeyButton
import gettext
_ = gettext.gettext

class keybinds(confStack):
	keybind_signal=Signal("PyObject")

	def __init_stack__(self):
		self.dbg=False
		self._debug("confKeys Load")
		self.menu_description=(_("Keybind for launching configuration from Run-O-Matic"))
		self.description=(_("Modify keybindings"))
		self.icon=('configure-shortcuts')
		self.tooltip=(_("From here you can modify the keybinding"))
		self.index=4
		self.enabled=True
		self.keytext=''
		self.keys={}
#		self._load_screen()
	#def __init__
	
	def _load_screen(self):
		vbox=QVBoxLayout()
		wdg=QWidget()
		hbox=QGridLayout()
		inp_conf=QLabel(_("Launch configuration"))
		self.cmb_keys=QComboBox()
		self.cmb_keys.addItem(" ")
		for key in range(1,13):
			self.cmb_keys.addItem("F{}".format(key))
		self.cmb_keys.adjustSize()
		self.lbl_info=QLabel(_("Select a F key for launch runoconfig from runomatic"))
		self.lbl_info.setWordWrap(True)
		hbox.addWidget(self.lbl_info,1,0,1,1,Qt.AlignRight)
		hbox.addWidget(self.cmb_keys,1,1,1,1,Qt.AlignLeft)
		wdg.setLayout(hbox)
		vbox.addWidget(wdg)
		self.setLayout(vbox)
#		self.updateScreen()
		return(self)
	#def _load_screen

	def updateScreen(self):
		self.force_change=False
		config=self.getConfig()
		self.keytext=''
		if config:
			keybinds=config[self.level].get('keybinds',None)
			if keybinds:
				self.keytext=keybinds.get('conf',None)
		self.cmb_keys.setCurrentText(self.keytext)
	#def updateScreen

	def writeConfig(self):
		key='keybinds'
		data={'conf':self.cmb_keys.currentText()}
		self.saveChanges(key,data)
	#def writeConfig
