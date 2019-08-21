#!/usr/bin/python3
import sys
import os
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,QLineEdit,QHBoxLayout,QGridLayout
from PyQt5 import QtGui
from PyQt5.QtCore import Qt,pyqtSignal,QSignalMapper,QProcess,QEvent,QSize
import gettext
from libAppRun import appRun
import gettext
from app2menu import App2Menu
from libAppRun import appRun

gettext.textdomain('testConfig')
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
		self._load_screen()
	#def __init__
	
	def _load_screen(self):
		def _grab_alt_keys(*args):
			self.btn_tab.setText("")
			self.grabKeyboard()
			try:
				self.keybind_signal.disconnect(_set_close_key)
			except:
				pass
			self.keybind_signal.connect(_set_tab_key)
		def _grab_close_keys(*args):
			self.btn_close.setText("")
			self.grabKeyboard()
			try:
				self.keybind_signal.disconnect(_set_tab_key)
			except:
				pass
			self.keybind_signal.connect(_set_close_key)
		def _set_tab_key(keypress):
			self.btn_tab.setText(keypress)
		def _set_close_key(keypress):
			self.btn_close.setText(keypress)
		self.installEventFilter(self)
		box=QGridLayout()
		lbl_txt=QLabel(_("From here you can define the keybindings"))
		box.addWidget(lbl_txt,0,0,1,2,Qt.AlignTop)
		inp_tab=QLabel("Navigation between tabs")
		self.btn_tab=QPushButton(_("Tab"))
		self.btn_tab.clicked.connect(_grab_alt_keys)
		self.btn_tab.setFixedSize(QSize(96,48))
		box.addWidget(inp_tab,1,0,1,1)
		box.addWidget(self.btn_tab,1,1,1,1,Qt.Alignment(1))
		inp_close=QLabel("Close app")
		self.btn_close=QPushButton(_("Alt+F4"))
		self.btn_close.setFixedSize(QSize(96,48))
		self.btn_close.clicked.connect(_grab_close_keys)
		box.addWidget(inp_close,2,0,1,1,Qt.AlignLeft)
		box.addWidget(self.btn_close,2,1,1,1,Qt.AlignLeft)
		btn_ok=QPushButton(_("Apply"))
		btn_ok.clicked.connect(self._save_keys)
		btn_cancel=QPushButton(_("Cancel"))
		box.addWidget(btn_ok,3,0,1,1,Qt.AlignLeft)
		box.addWidget(btn_cancel,3,1,1,1,Qt.AlignRight)

		self.setLayout(box)
		return(self)
	#def _load_screen

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
	
	def _save_keys(self):
		keysDict={'nav':"",'close':""}
		keysDict['nav']=self.btn_tab.text()
		keysDict['close']=self.btn_close.text()
		self.runner.write_config(keysDict,key='keybinds',level='user')
	#def _save_keys
