#!/usr/bin/env python3
import sys
import os
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,\
				QDialog,QGridLayout,QHBoxLayout,QFormLayout,QLineEdit,QComboBox,\
				QStatusBar,QFileDialog,QDialogButtonBox,QScrollBar,QScrollArea,QListWidget,\
				QListWidgetItem,QStackedWidget
from PyQt5 import QtGui
from PyQt5.QtCore import QSize,pyqtSlot,Qt, QPropertyAnimation,QThread,QRect,QTimer,pyqtSignal,QSignalMapper,QProcess,QEvent
import gettext
from libAppRun import appRun
from edupals.ui import QAnimatedStatusBar

gettext.textdomain('testConfig')
_ = gettext.gettext

QString=type("")
QInt=type(0)

RSRC="/home/lliurex/git/testkid/rsrc"
BTN_MENU_SIZE=24

class confKid(QWidget):
	update_signal=pyqtSignal("PyQt_PyObject")
	def __init__(self):
		super().__init__()
		self.dbg=True
		self.categories={}
		self.desktops={}
		self.app_icons={}
		self.sigmap_tabSelect=QSignalMapper(self)
#		self.sigmap_tabSelect.mapped[QInt].connect(self._on_tabSelect)
#		self.sigmap_tabRemove=QSignalMapper(self)
#		self.sigmap_tabRemove.mapped[QInt].connect(self._on_tabRemove)
		self.runner=appRun()
#		self._read_config()
		self._render_gui()
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
				stack=QLabel(_("From here you can configure TestKid"))
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
		widget=QWidget()
		box=QVBoxLayout()
		lbl_txt=QLabel(_("From here you can configure Launchers"))
		box.addWidget(lbl_txt)
		widget.setLayout(box)
		return(widget)
	
	def _render_add(self):
		widget=QWidget()
		box=QGridLayout()
		lbl_txt=QLabel(_("From here you can add Launchers"))
		box.addWidget(lbl_txt)
		widget.setLayout(box)
		return(widget)
	
	def _render_keys(self):
		def _grab_keys():
			self.grabKeyboard()
		widget=QWidget()
		box=QGridLayout()
		lbl_txt=QLabel(_("Close Window"))
		inp_txt=QLabel()
		btn_txt=QPushButton(_("Grab keys"))
		btn_txt.clicked.connect(_grab_keys)
		box.addWidget(lbl_txt,0,0,1,1)
		box.addWidget(inp_txt,1,0,1,1)
		box.addWidget(btn_txt,1,1,1,1)

		widget.setLayout(box)
		return(widget)
	
	def _render_pass(self):
		widget=QWidget()
		box=QGridLayout()
		lbl_txt=QLabel(_("From here you can set the master password"))
		box.addWidget(lbl_txt)
		widget.setLayout(box)
		return(widget)

	def _show_stack(self):
		self.stk_widget.setCurrentIndex(self.lst_options.currentRow())
		

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
	"""
	return(css)
	#def _define_css

app=QApplication(["Test Kid Config"])
testConfLauncher=confKid()
app.instance().setStyleSheet(_define_css())
app.exec_()
