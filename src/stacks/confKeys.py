#!/usr/bin/python3
import sys
import os
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,QLineEdit,QHBoxLayout,QGridLayout
from PyQt5 import QtGui
from PyQt5.QtCore import Qt,pyqtSignal,QSignalMapper,QProcess,QEvent,QSize
import gettext
from libAppRun import appRun
from app2menu import App2Menu

_ = gettext.gettext

class confKeys(QWidget):
	keybind_signal=pyqtSignal("PyQt_PyObject")
	def __init__(self):
		super().__init__()
		self.runner=appRun()
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
		self.sw_changes=False
		self.level='user'
		self.keys={}
		self._load_screen()
	#def __init__
	
	def _debug(self,msg):
		if self.dbg:
			print("ConfKeys: %s"%msg)
	#def _debug

	def set_textDomain(self,textDomain):
		gettext.textdomain(textDomain)
	#def set_textDomain

	def set_configLevel(self,level):
		self.level=level
	#def set_configLevel
	
	def get_config(self):
		data=self.runner.get_default_config()
		self.level=data['system']['config']
		if self.level!='system':
			data=self.runner.get_config(self.level)
		self.keys=data[self.level].get('keybinds',{})
	#def get_config
	
	def _load_screen(self):
		def _grab_alt_keys(*args):
			self.btn_conf.setText("")
			self.grabKeyboard()
			self.keybind_signal.connect(_set_config_key)
		def _set_config_key(keypress):
			self.btn_conf.setText(keypress)
		self.installEventFilter(self)
		box=QGridLayout()
		lbl_txt=QLabel(_("From here you can define the keybindings"))
		box.addWidget(lbl_txt,0,0,1,2,Qt.AlignTop)
		inp_conf=QLabel("Launch configuration")
		self.btn_conf=QPushButton(_(""))
		self.btn_conf.clicked.connect(_grab_alt_keys)
		self.btn_conf.setFixedSize(QSize(96,48))
		box.addWidget(inp_conf,1,0,1,1)
		box.addWidget(self.btn_conf,1,1,1,1,Qt.Alignment(1))
		btn_ok=QPushButton(_("Apply"))
		btn_ok.clicked.connect(self.write_config)
		btn_cancel=QPushButton(_("Cancel"))
		box.addWidget(btn_ok,3,0,1,1,Qt.AlignLeft)
		box.addWidget(btn_cancel,3,1,1,1,Qt.AlignRight)

		self.setLayout(box)
		self.update_screen()
		return(self)
	#def _load_screen

	def update_screen(self):
		self.get_config()
		confKey=self.keys.get('conf',None)
		if confKey:
			self.btn_conf.setText(confKey)
	#def update_screen

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
	
	def write_config(self):
		keysDict={}
		keysDict['conf']=self.btn_conf.text()
		self.runner.write_config(keysDict,key='keybinds',level=self.level)
	#def write_config
	
	def get_changes(self):
		return (self.sw_changes)
