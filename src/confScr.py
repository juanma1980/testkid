#!/usr/bin/env python3
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,\
				QDialog,QGridLayout,QHBoxLayout,QFormLayout,QLineEdit,QComboBox,\
				QStatusBar,QFileDialog,QDialogButtonBox,QScrollBar,QScrollArea,QListWidget,\
				QListWidgetItem,QStackedWidget,QButtonGroup,QComboBox,QTableWidget,QTableWidgetItem,\
				QHeaderView
from PyQt5 import QtGui
from PyQt5.QtCore import QSize,pyqtSlot,Qt, QPropertyAnimation,QThread,QRect,QTimer,pyqtSignal,QSignalMapper,QProcess,QEvent
import gettext
from app2menu import App2Menu
from libAppRun import appRun
from libAppConfig import appConfig

gettext.textdomain('testConfig')
_ = gettext.gettext

class confScr(QWidget):
	def __init__(self):
		super().__init__()
		self.setStyleSheet(self._define_css())
		self.dbg=True
		self.runner=appRun()
		self.tbl_cat=QTableWidget(1,2)
		header=self.tbl_cat.horizontalHeader()
		header.setSectionResizeMode(0,QHeaderView.Stretch)
		self.tbl_cat.horizontalHeader().hide()
		self.tbl_cat.verticalHeader().hide()
		self.tbl_cat.setShowGrid(False)
		self.tbl_cat.setSelectionBehavior(QTableWidget.SelectRows)
		self.tbl_cat.setSelectionMode(QTableWidget.SingleSelection)
		self.tbl_cat.setEditTriggers(QTableWidget.NoEditTriggers)
		self.tbl_app=QTableWidget(1,2)
		header=self.tbl_app.horizontalHeader()
		header.setSectionResizeMode(0,QHeaderView.Stretch)
		self.tbl_app.horizontalHeader().hide()
		self.tbl_app.verticalHeader().hide()
		self.tbl_app.setShowGrid(False)
		self.tbl_app.setSelectionBehavior(QTableWidget.SelectRows)
		self.tbl_app.setSelectionMode(QTableWidget.SingleSelection)
		self.tbl_app.setEditTriggers(QTableWidget.NoEditTriggers)
		self.visible_categories=[]
		self.menu=App2Menu.app2menu()
		self.categories=[]
		self._load_screen()
	#def __init__

	def _debug(self,msg):
		if self.dbg:
			print("ConfScr: %s"%msg)
	#def _debug

	def _load_screen(self):
		box=QGridLayout()
		stk_widget=QStackedWidget()
		lbl_txt=QLabel(_("From here you can set visible Launchers"))
		lbl_txt.setAlignment(Qt.AlignTop)
		box.addWidget(lbl_txt,0,0,1,2)
		btn_cat=QPushButton()
		btn_cat.setObjectName("menu")
		btn_cat.setCheckable(True)
		btn_cat.setChecked(True)
		btn_cat.setText(_("Categories"))
		box.addWidget(btn_cat,1,0,1,1)
		btn_dsk=QPushButton()
		btn_dsk.setObjectName("menu")
		btn_dsk.setCheckable(True)
		btn_dsk.setText(_("Applications"))
		btn_cat.clicked.connect(lambda:self._show_stack(btn_cat,btn_dsk,stk_widget,0))
		btn_dsk.clicked.connect(lambda:self._show_stack(btn_dsk,btn_cat,stk_widget,1))
		box.addWidget(btn_dsk,1,1,1,1)
		#Categories
		stk_categories=QWidget()
		cat_box=QVBoxLayout()
		cat_box.addWidget(self.tbl_cat)
		btn_save_cat=QPushButton(_("Apply"))
		btn_save_cat.setMaximumSize(QSize(128,48))
		btn_save_cat.clicked.connect(self._save_categories)
		cat_box.addWidget(btn_save_cat)
		stk_categories.setLayout(cat_box)
		stk_widget.addWidget(stk_categories)
		#Desktops
		stk_desktops=QWidget()
		app_box=QVBoxLayout()
		app_box.addWidget(self.tbl_app)
		btn_save_app=QPushButton(_("Apply"))
		btn_save_app.setMaximumSize(QSize(128,48))
		btn_save_app.clicked.connect(self._save_apps)
		app_box.addWidget(btn_save_app)
		stk_desktops.setLayout(app_box)
		stk_widget.addWidget(stk_desktops)
		box.addWidget(stk_widget,2,0,1,2)
		self._update_categories()
		self._udpate_desktops()

		self.setLayout(box)
	#def load_screen

	def _show_stack(self,btn_to,btn_from,stk,index):
		btn_from.setChecked(False)
		btn_to.setChecked(True)
		stk.setCurrentIndex(index)

	def _update_apps_data(self):
		data=self.runner.get_apps()
		self.visible_categories=data['categories']
		self._debug("Visible: %s"%self.visible_categories)

	def _update_categories(self):
		row=0
		col=0
		self._update_apps_data()
		self.tbl_cat.clear()
		self.tbl_cat.setRowCount(1)
		self.categories=self.menu.get_categories()
		icn_showOn=QtGui.QIcon.fromTheme("password-show-on")
		icn_showOff=QtGui.QIcon.fromTheme("password-show-off")
		for cat in self.categories:
			if cat:
				self._debug("Loading %s"%cat)
				item=QTableWidgetItem(cat)
				self.tbl_cat.setItem(row,col,item)
				btn_showOn=QPushButton()
				btn_showOn.setCheckable(True)
				btn_showOn.setChecked(False)
				btn_showOn.setIcon(icn_showOff)
				if cat.replace(" ","-") in self.visible_categories:
					btn_showOn.setChecked(True)
					btn_showOn.setIcon(icn_showOn)
				self.tbl_cat.setCellWidget(row,1,btn_showOn)
				row+=1
				self.tbl_cat.insertRow(row)
		self.tbl_cat.removeRow(row)

	def _udpate_desktops(self):
		row=0
		col=0
		self.tbl_app.clear()
		self.tbl_app.setRowCount(1)
		icn_showOn=QtGui.QIcon.fromTheme("password-show-on")
		icn_showOff=QtGui.QIcon.fromTheme("password-show-off")
		for cat in self.categories:
			for desk in self.menu.get_apps_from_category(cat):
				item=QTableWidgetItem(desk)
				self.tbl_app.setItem(row,col,item)
				btn_showOn=QPushButton()
				btn_showOn.setObjectName("showbtn")
				btn_showOn.setCheckable(True)
				btn_showOn.setChecked(False)
				btn_showOn.setIcon(icn_showOff)
				if cat.replace(" ","-") in self.visible_categories:
					btn_showOn.setChecked(True)
					btn_showOn.setIcon(icn_showOn)
				self.tbl_app.setCellWidget(row,1,btn_showOn)
				row+=1
				self.tbl_app.insertRow(row)
		self.tbl_app.removeRow(row)

	def _save_categories(self):
		categories=[]
		for row in range(0,self.tbl_cat.rowCount()):

			btn_visible=self.tbl_cat.cellWidget(row,1)
			self._debug("Item at %s: %s"%(row,btn_visible))
			if btn_visible and btn_visible.isChecked():
				item=self.tbl_cat.item(row,0)
				categories.append(item.text())
		self._debug("Categories: %s"%categories)
		self.visible_categories=categories
	#def _save_categories(self):

	def _save_apps(self):
		desktops=[]
		hidden=[]
		for row in range(0,self.tbl_app.rowCount()):
			btn_visible=self.tbl_app.cellWidget(row,1)
			self._debug("Item at %s: %s"%(row,btn_visible))
			item=self.tbl_app.item(row,0)
			if btn_visible and btn_visible.isChecked():
				desktops.append(item.text())
			elif btn_visible: 
				info=self.menu.get_desktop_info("/usr/share/applications/%s"%item.text())
				for cat in info['Categories']:
					if cat.lower() in self.visible_categories:
						hidden.append(item.text())
		self._debug("Desktops: %s"%desktops)
		self._debug("Hidden: %s"%hidden)
	#def _save_apps

	def _define_css(self):
		css="""
		QPushButton#menu{
			padding: 6px;
			margin:6px;
			font: 14px Roboto;
		}
		"""
		return(css)
		#def _define_css
