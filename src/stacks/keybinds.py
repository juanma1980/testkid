#!/usr/bin/python3
import sys
import os
from PySide2.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,QLineEdit,QHBoxLayout,QGridLayout
from PySide2 import QtGui
from PySide2.QtCore import Qt,Signal,QSignalMapper,QProcess,QEvent,QSize
from appconfig.appConfigStack import appConfigStack as confStack
import gettext
_ = gettext.gettext

class keybinds(confStack):
	keybind_signal=Signal("PyQt_PyObject")

	def __init_stack__(self):
		self.dbg=False
		self._debug("confKeys Load")
		self.keymap={}
		for key,value in vars(Qt).items():
			if isinstance(value, Qt.Key):
				self.keymap[value]=key.partition('_')[2]
		self.modmap={
					Qt.ControlModifier: self.keymap[Qt.Key_Control],
					Qt.AltModifier: self.keymap[Qt.Key_Alt],
					Qt.ShiftModifier: self.keymap[Qt.Key_Shift],
					Qt.MetaModifier: self.keymap[Qt.Key_Meta],
					Qt.GroupSwitchModifier: self.keymap[Qt.Key_AltGr],
					Qt.KeypadModifier: self.keymap[Qt.Key_NumLock]
					}
		self.menu_description=(_("Set keybindings for launch the configuration from Run-O-Matic"))
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
		def _grab_alt_keys(*args):
			self.lbl_info.show()
			self.btn_conf.setText("")
			self.grabKeyboard()
			self.keybind_signal.connect(_set_config_key)
		def _set_config_key(keypress):
			self.lbl_info.hide()
			self.btn_conf.setText(keypress)
			if keypress!=self.keytext:
				self.changes=True
				self.setChanged(self.btn_conf)
		self.installEventFilter(self)
		box=QGridLayout()
		lbl_txt=QLabel(_("From here you can define the keybindings"))
		box.addWidget(lbl_txt,0,0,1,2,Qt.AlignTop)
		inp_conf=QLabel(_("Launch configuration"))
		self.lbl_info=QLabel(_("Press a key"))
		box.addWidget(self.lbl_info,1,0,1,2,Qt.AlignTop)
		self.lbl_info.hide()
		self.btn_conf=QPushButton("")
		self.btn_conf.clicked.connect(_grab_alt_keys)
		self.btn_conf.setFixedSize(QSize(96,48))
		box.addWidget(inp_conf,2,0,1,1,Qt.AlignTop)
		box.addWidget(self.btn_conf,2,1,1,1,Qt.AlignTop)
		box.setRowStretch(1,2)
		box.setRowStretch(2,4)
		box.setColumnStretch(2,3)
		self.setLayout(box)
		self.updateScreen()
		return(self)
	#def _load_screen

	def updateScreen(self):
		config=self.getConfig()
		self.keytext=''
		if config:
			keybinds=config[self.level].get('keybinds',None)
			if keybinds:
				self.keytext=keybinds.get('conf',None)
		self.btn_conf.setText(self.keytext)
	#def updateScreen

	def eventFilter(self,source,event):
		sw_mod=False
		keypressed=[]
		if (event.type()==QEvent.KeyPress):
			for modifier,text in self.modmap.items():
				if event.modifiers() & modifier:
					sw_mod=True
					keypressed.append(text)
			key=self.keymap.get(event.key(),event.text())
			if key not in keypressed:
				if sw_mod==True:
					sw_mod=False
				keypressed.append(key)
			if sw_mod==False:
				self.keybind_signal.emit("+".join(keypressed))
		if (event.type()==QEvent.KeyRelease):
			self.releaseKeyboard()

		return False
	#def eventFilter

	def getData(self):
		key='keybinds'
		data={'conf':self.btn_conf.text()}
		return({key:data})

	def writeConfig(self):
		key='keybinds'
		data={'conf':self.btn_conf.text()}
		self.saveChanges(key,data)
