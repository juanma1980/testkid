#!/usr/bin/python3
import sys
import os
from PySide2.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,QLineEdit,QHBoxLayout,QGridLayout
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
		box=QGridLayout()
		lbl_txt=QLabel(_("From here you can define the keybindings"))
		box.addWidget(lbl_txt,0,0,1,2,Qt.AlignTop)
		inp_conf=QLabel(_("Launch configuration"))
		self.lbl_info=QLabel(_("Press a key"))
		box.addWidget(self.lbl_info,1,0,1,2,Qt.AlignTop)
		self.lbl_info.hide()
		self.btn_conf=QHotkeyButton("")
		self.btn_conf.hotkeyAssigned.connect(self._set_config_key)
		box.addWidget(inp_conf,2,0,1,1,Qt.AlignTop)
		box.addWidget(self.btn_conf,2,1,1,1,Qt.AlignTop)
		box.setRowStretch(1,2)
		box.setRowStretch(2,4)
		box.setColumnStretch(2,3)
		self.setLayout(box)
		self.updateScreen()
		return(self)
	#def _load_screen

	def _set_config_key(self,*args):
		self.lbl_info.hide()
		self.changes=True
		self.setChanged(True)
	#def _set_config_key(keypress):

	def updateScreen(self):
		self.force_change=False
		config=self.getConfig()
		self.keytext=''
		if config:
			keybinds=config[self.level].get('keybinds',None)
			if keybinds:
				self.keytext=keybinds.get('conf',None)
		self.btn_conf.setText(self.keytext)
	#def updateScreen

	def getData(self):
		key='keybinds'
		data={'conf':self.btn_conf.text()}
		return({key:data})
	#def getData

	def writeConfig(self):
		key='keybinds'
		data={'conf':self.btn_conf.text()}
		self.saveChanges(key,data)
	#def writeConfig
