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
from confScr import confScr

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
#		self.sigmap_tabSelect.mapped[QInt].connect(self._on_tabSelect)
#		self.sigmap_tabRemove=QSignalMapper(self)
#		self.sigmap_tabRemove.mapped[QInt].connect(self._on_tabRemove)
		self.runner=appRun()
#		self._read_config()
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
		widget=confScr(app)
		return(widget)
	
	def _render_add(self):
		def _save_desktop():
			categories=[]
			desktop={}
			desktop['Categories']=cmb_cat.currentText()+";"
			desktop['Name']=inp_name.text()
			desktop['Exec']=inp_exec.text()
			desktop['Icon']=self.icon
			desktop['Comment']=inp_desc.text()
			self._debug("Saving %s"%desktop)
			try:
				subprocess.check_call(["pkexec","/usr/share/deskedit/bin/deskedit-helper.py",desktop['Name'],desktop['Icon'],desktop['Comment'],desktop['Categories'],desktop['Exec']])
				self._show_message(_("Added %s"%desktop['Name']),"success")
			except:
				self._show_message(_("Error adding %s"%desktop['Name']))
		#def _save_desktop

		widget=QWidget()
		box=QGridLayout()
		lbl_txt=QLabel(_("From here you can add Launchers"))
		box.addWidget(lbl_txt)
		lbl_icon=QLabel(_("Icon: "))
		box.addWidget(lbl_icon,1,2,1,1)
		btn_icon=QPushButton()
		btn_icon.setObjectName("btnIcon")
		icn_desktop=QtGui.QIcon.fromTheme("shell")
		btn_icon.setIcon(icn_desktop)
		btn_icon.setIconSize(QSize(64,64))
		btn_icon.setToolTip(_("Push to change icon"))
		btn_icon.clicked.connect(lambda:self._file_chooser(widget=btn_icon,imgDialog=True))
		box.addWidget(btn_icon,2,2,3,1,Qt.AlignTop)
		lbl_name=QLabel(_("Name: "))
		box.addWidget(lbl_name,1,0,1,2)
		inp_name=QLineEdit()
		inp_name.setPlaceholderText(_("Desktop name"))
		inp_name.setToolTip(_("Insert desktop name"))
		box.addWidget(inp_name,2,0,1,2)
		lbl_exec=QLabel(_("Executable: "))
		box.addWidget(lbl_exec,3,0,1,2)
		inp_exec=QLineEdit()
		inp_exec.setPlaceholderText(_("Executable path"))
		inp_exec.setToolTip(_("Insert path to the executable"))
		box.addWidget(inp_exec,4,0,1,1,Qt.Alignment(0))
		btn_exec=QPushButton("...")
		btn_exec.setObjectName("btnFile")
		btn_exec.setToolTip(_("Press button to select an executable"))
		btn_exec.clicked.connect(lambda:self._file_chooser(widget=inp_exec))
		box.addWidget(btn_exec,4,1,1,1,Qt.Alignment(1))
		lbl_desc=QLabel(_("Description: "))
		box.addWidget(lbl_desc,5,0,1,2)
		inp_desc=QLineEdit()
		inp_desc.setPlaceholderText(_("Description"))
		inp_desc.setToolTip(_("Insert a description for the app"))
		box.addWidget(inp_desc,6,0,1,3)
		lbl_cat=QLabel(_("Category: "))
		box.addWidget(lbl_cat,7,0,1,2)
		cmb_cat=QComboBox()
		data=self.runner.get_apps()
		for cat in data['categories']:
			cmb_cat.addItem(cat)
		box.addWidget(cmb_cat,8,0,1,2,Qt.AlignLeft)
		btn_apply=QPushButton(_("Apply"))
		btn_apply.setToolTip(_("Save desktop"))
		btn_apply.setIconSize(QSize(48,48))
		btn_apply.clicked.connect(_save_desktop)
		box.addWidget(btn_apply,9,2,1,1,Qt.Alignment(2))
		widget.setLayout(box)
		return(widget)
	
	def _file_chooser(self,widget=None,path=None,imgDialog=None):
		fdia=QFileDialog()
		fchoosed=''
		fdia.setFileMode(QFileDialog.AnyFile)
		if imgDialog:
			fdia.setNameFilter(_("images(*.png *.xpm *jpg)"))
		else:
			fdia.setNameFilter(_("All files(*.*)"))
		if path:
			self._debug("Set path to %s"%path)
			fdia.setDirectory(path)
		if (fdia.exec_()):
			fchoosed=fdia.selectedFiles()[0]
			if widget:
				if imgDialog:
					self.icon=fdia.selectedFiles()[0]
					icn=QtGui.QIcon(self.icon)
					widget.setIcon(icn)
				else:
					widget.setText(fchoosed)
			return(fchoosed)
	
	def _render_keys(self):
		def _grab_alt_keys(*args):
			btn_tab.setText("")
			self.grabKeyboard()
			try:
				self.keybind_signal.disconnect(_set_close_key)
			except:
				pass
			self.keybind_signal.connect(_set_tab_key)
		def _grab_close_keys(*args):
			btn_close.setText("")
			self.grabKeyboard()
			try:
				self.keybind_signal.disconnect(_set_tab_key)
			except:
				pass
			self.keybind_signal.connect(_set_close_key)
		def _set_tab_key(keypress):
			btn_tab.setText(keypress)
		def _set_close_key(keypress):
			btn_close.setText(keypress)
		self.installEventFilter(self)
		widget=QWidget()
		box=QGridLayout()
		lbl_txt=QLabel(_("From here you can define the keybindings"))
		box.addWidget(lbl_txt,0,0,1,2,Qt.AlignTop)
		inp_tab=QLabel("Navigation between tabs")
		btn_tab=QPushButton(_("Tab"))
		btn_tab.clicked.connect(_grab_alt_keys)
		btn_tab.setFixedSize(QSize(96,48))
		box.addWidget(inp_tab,1,0,1,1)
		box.addWidget(btn_tab,1,1,1,1,Qt.Alignment(1))
		inp_close=QLabel("Close app")
		btn_close=QPushButton(_("Alt+F4"))
		btn_close.setFixedSize(QSize(96,48))
		btn_close.clicked.connect(_grab_close_keys)
		box.addWidget(inp_close,2,0,1,1,Qt.AlignLeft)
		box.addWidget(btn_close,2,1,1,1,Qt.AlignLeft)
		btn_Ok=QPushButton(_("Apply"))
		btn_Cancel=QPushButton(_("Cancel"))
		box.addWidget(btn_Ok,3,0,1,1,Qt.AlignLeft)
		box.addWidget(btn_Cancel,3,1,1,1,Qt.AlignRight)

		widget.setLayout(box)
		return(widget)

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
	
	def _render_pass(self):
		widget=QWidget()
		box=QVBoxLayout()
		lbl_txt=QLabel(_("If a master password is set then the app will prompt for it to exit"))
		lbl_txt.setAlignment(Qt.AlignTop)
		box.addWidget(lbl_txt)
		txt_pass=QLineEdit()
		txt_pass.setPlaceholderText(_("Password"))
		box.addWidget(txt_pass)
		txt_pass2=QLineEdit()
		txt_pass2.setPlaceholderText(_("Repeat password"))
		box.addWidget(txt_pass2)
		box_btns=QHBoxLayout()
		btn_Ok=QPushButton(_("Apply"))
		btn_Cancel=QPushButton(_("Cancel"))
		box_btns.addWidget(btn_Ok)
		box_btns.addWidget(btn_Cancel)
		box.addLayout(box_btns)
		widget.setLayout(box)
		return(widget)

	def _show_stack(self):
		self.stk_widget.setCurrentIndex(self.lst_options.currentRow())
		

	def _show_message(self,msg,status=None):
		self.statusBar.setText(msg)
		if status:
			self.statusBar.show(status)
		else:
			self.statusBar.show()

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
