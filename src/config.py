#!/usr/bin/env python3
import sys
import os
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,\
				QDialog,QGridLayout,QHBoxLayout,QFormLayout,QLineEdit,QComboBox,\
				QStatusBar,QFileDialog,QDialogButtonBox,QScrollBar,QScrollArea,QListWidget,\
				QListWidgetItem,QStackedWidget,QButtonGroup,QComboBox,QTableWidget,QTableWidgetItem,\
				QHeaderView
from PyQt5 import QtGui
from PyQt5.QtCore import QSize,pyqtSlot,Qt, QPropertyAnimation,QThread,QRect,QTimer,pyqtSignal,QSignalMapper,QProcess,QEvent
import gettext
from libAppRun import appRun
from edupals.ui import QAnimatedStatusBar
from confLaunchers import confLaunchers  
from confPass import confPass
from confKeys import confKeys
from confDesktops import confDesktops

gettext.textdomain('testConfig')
_ = gettext.gettext

QString=type("")
QInt=type(0)

RSRC="/home/lliurex/git/testkid/rsrc"
BTN_MENU_SIZE=24

class confKid(QWidget):
	keybind_signal=pyqtSignal("PyQt_PyObject")
	update_signal=pyqtSignal("PyQt_PyObject")
	def __init__(self):
		super().__init__()
		self.dbg=True
		self.categories={}
		self.desktops={}
		self.app_icons={}
		self.icon='shell'
		self.sigmap_tabSelect=QSignalMapper(self)
		self.runner=appRun()
		self._render_gui()
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
	#def init
	
	def _debug(self,msg):
		if self.dbg:
			print("%s"%msg)
	#def _debug
	
	def _render_gui(self):
		box=QGridLayout()
		img_banner=QLabel()
		img=QtGui.QPixmap("%s/banner.png"%RSRC)
		img_banner.setPixmap(img)
		img_banner.setAlignment(Qt.AlignCenter)
		self.statusBar=QAnimatedStatusBar.QAnimatedStatusBar()
		self.statusBar.setStateCss("success","background-color:qlineargradient(x1:0 y1:0,x2:0 y2:1,stop:0 rgba(0,0,255,1), stop:1 rgba(0,0,255,0.6));color:white;")
		self.lst_options=QListWidget()
		self.stk_widget=QStackedWidget()
		box.addWidget(self.statusBar,0,0,1,1)
		box.addWidget(img_banner,0,0,1,2)
		l_panel=self._left_panel()
		box.addWidget(l_panel,1,0,1,1,Qt.Alignment(1))
		r_panel=self._right_panel()
		box.addWidget(r_panel,1,1,1,1)
		self.setLayout(box)
		self.show()
	#def _render_gui

	def _left_panel(self):
		panel=QWidget()
		box=QVBoxLayout()
		btn_menu=QPushButton()
		icn=QtGui.QIcon.fromTheme("application-menu")
		btn_menu.setIcon(icn)
		btn_menu.setIconSize(QSize(BTN_MENU_SIZE,BTN_MENU_SIZE))
		btn_menu.setMaximumWidth(BTN_MENU_SIZE)
		btn_menu.setMaximumHeight(BTN_MENU_SIZE)
		btn_menu.setToolTip(_("Options"))
		btn_menu.setObjectName("menuButton")
		box.addWidget(btn_menu,Qt.Alignment(1))
		options={
				1:{'name':"Options",'icon':'icon'},
				2:{'name':"Modify launchers",'icon':'edit-group','tooltip':_("From here you can modify the launchers")},
				3:{'name':"Add custom launcher",'icon':'org.kde.plasma.quicklaunch','tooltip':_("From here you can add a custom launcher")},
				4:{'name':"Modify keybindings",'icon':'configure-shortcuts','tooltip':_("From here you can modify the keybinding")},
				5:{'name':"Set master password",'icon':'dialog-password','tooltip':_("From here you can set the master password")}
				}
		for index,option in options.items():
			lst_widget=QListWidgetItem(self.lst_options)
			lst_widget.setText(option['name'])
			if index==1:
				pass
			else:
				icn=QtGui.QIcon.fromTheme(option['icon'])
				lst_widget.setIcon(icn)
				if 'tooltip' in option.keys():
					lst_widget.setToolTip(option['tooltip'])
			self.lst_options.addItem(lst_widget)

		box.addWidget(self.lst_options)
		self.lst_options.itemClicked.connect(self._show_stack)
		panel.setLayout(box)
		return(panel)

	def _right_panel(self):
		panel=QWidget()
		box=QVBoxLayout()
		for i in range(0,5):
			if i==0:
				stack=QWidget()
				stack.setObjectName("panel")
				s_box=QVBoxLayout()
				lbl_txt=QLabel(_("Welcome to Run-O-Matic config.\nFrom here you can:\n * Configure visible launchers\n * Add new launchers\n\
* Set keybindings for close and navigation\n * Set a master password"))
				lbl_txt.setAlignment(Qt.AlignTop)
				s_box.addWidget(lbl_txt,Qt.Alignment(1))
				stack.setLayout(s_box)
			elif i==1:
				stack=self._render_config()
			elif i==2:
				stack=self._render_add()
			elif i==3:
				stack=self._render_keys()
			elif i==4:
				stack=self._render_pass()

			self.stk_widget.addWidget(stack)
		box.addWidget(self.stk_widget)
		panel.setLayout(box)
		return(panel)

	def _render_config(self):
		widget=confLaunchers(app)
		return(widget)
	
	def _render_add(self):
		widget=confDesktops()
		return(widget)
	
	def _render_keys(self):
		widget=confKeys()
		return(widget)
	#def _render_keys
	
	def _render_pass(self):
		widget=confPass()
		return(widget)
	#def _render_pass

	def _show_stack(self):
		self.stk_widget.setCurrentIndex(self.lst_options.currentRow())
	#def _show_stack

	def _show_message(self,msg,status=None):
		self.statusBar.setText(msg)
		if status:
			self.statusBar.show(status)
		else:
			self.statusBar.show()
	#def _show_message

def _define_css():
	css="""
	QPushButton{
		padding: 6px;
		margin:6px;
		font: 14px Roboto;
	}
	QPushButton#menu:active{
		background:none;
	}
	QStatusBar{
		background:red;
		color:white;
		font: 14px Roboto bold;
	}
	QLabel{
		padding:6px;
		margin:6px;
	}

	#dlgLabel{
		font:12px Roboto;
		margin:0px;
		border:0px;
		padding:3px;
	}
	
	QLineEdit{
		border:0px;
		border-bottom:1px solid grey;
		padding:1px;
		font:14px Roboto;
		margin-right:6px;
	}
	#panel{
		background-image:url("../rsrc/background.png");
		background-repeat:no-repeat;
		background-position:center;
	}
	"""
	return(css)
	#def _define_css

app=QApplication(["Test Kid Config"])
testConfLauncher=confKid()
app.instance().setStyleSheet(_define_css())
app.exec_()
