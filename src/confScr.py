#!/usr/bin/env python3
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,\
				QDialog,QGridLayout,QHBoxLayout,QFormLayout,QLineEdit,QComboBox,\
				QStatusBar,QFileDialog,QDialogButtonBox,QScrollBar,QScrollArea,QListWidget,\
				QListWidgetItem,QStackedWidget,QButtonGroup,QComboBox,QTableWidget,QTableWidgetItem,\
				QHeaderView,QMenu
from PyQt5 import QtGui
from PyQt5.QtCore import QSize,pyqtSlot,Qt, QPropertyAnimation,QThread,QRect,QTimer,pyqtSignal,QSignalMapper,QProcess,QEvent,QMimeData
import gettext
from app2menu import App2Menu
from libAppRun import appRun

gettext.textdomain('testConfig')
_ = gettext.gettext

BTN_SIZE_FULL=128
BTN_SIZE=32


class dropButton(QPushButton):
	signal=pyqtSignal("PyQt_PyObject")
	def __init__(self,title,parent):
		super (dropButton,self).__init__("",parent)
		self.title=title
		self.parent=parent
		self.img=None
		self.icon=None
		self.setAcceptDrops(True)
		self.setMaximumWidth(BTN_SIZE)
		self.position=0
	#def __init__(self,title,parent):

	def dragEnterEvent(self,e):
		e.accept()
	#def dragEnterEvent
	
	def mousePressEvent(self,e):
		self.signal.emit({"drag":self})
		self.position=e.pos()
		mimedata=QMimeData()
		drag=QtGui.QDrag(self)
		drag.setMimeData(mimedata)
		dropAction=drag.exec_(Qt.MoveAction)
	#def mousePressEvent

	def dropEvent(self,e):
		position=e.pos()
		e.setDropAction(Qt.MoveAction)
		e.accept()
		self.signal.emit({"drop":self})
	#def dropEvent

	def set_image(self,img,state='show'):
		self.img=img
		if QtGui.QIcon.hasThemeIcon(self.img):
			self.icon=QtGui.QIcon.fromTheme(self.img)
			if state!='show':
				print("Bg %s"%self.title)
				pixmap=self.icon.pixmap(QSize(32,32))
				image=pixmap.toImage().convertToFormat(QtGui.QImage.Format_Mono)
				bg_pixmap=QtGui.QPixmap.fromImage(image)
				self.icon=QtGui.QIcon(bg_pixmap)
		else:
			return None
		self.setIcon(self.icon)
		self.setIconSize(QSize(BTN_SIZE,BTN_SIZE))
		return True
	#def set_image

	def clone(self):
		btn=dropButton(self.title,self.parent)
		btn.set_image(self.img)
		btn.setMenu(self.menu())
		return(btn)
	#def clone
#class dropButton


class confScr(QWidget):
	dragdrop_signal=pyqtSignal("PyQt_PyObject")
	def __init__(self,app):
		super().__init__()
		self.dbg=True
		self.app=app
		self.setStyleSheet(self._define_css())
		self.runner=appRun()
		self.tbl_app=QTableWidget(1,2)
		self.tbl_app.setAcceptDrops(True)
		self.tbl_app.setDragEnabled(True)
		header=self.tbl_app.horizontalHeader()
		header.setSectionResizeMode(0,QHeaderView.Stretch)
		self.tbl_app.setShowGrid(False)
		self.tbl_app.horizontalHeader().hide()
		self.tbl_app.verticalHeader().hide()
		self.btn_grid={}
		self.btn_drag=None
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
		box=QVBoxLayout()
		btnBox=QHBoxLayout()
		btn_cat=QPushButton(_("Categories"))
		btn_add=QPushButton()
		btn_add.setToolTip(_("Add Launcher"))
		icnAdd=QtGui.QIcon.fromTheme("list-add")
		btn_add.setIcon(icnAdd)
		btnBox.addWidget(btn_cat)
		btnBox.addWidget(btn_add)
		box.addLayout(btnBox)
		row=0
		col=0
		scr=self.app.primaryScreen()
		w=scr.size().width()-BTN_SIZE_FULL
		h=scr.size().height()-(2*BTN_SIZE_FULL)
		maxCol=int(w/BTN_SIZE_FULL)-3
		tabScroll=QWidget()
		tabScroll.setFocusPolicy(Qt.NoFocus)
		scrollArea=QScrollArea(tabScroll)
		scrollArea.setFocusPolicy(Qt.NoFocus)
		apps=self._update_apps_data()
		self._update_categories(apps,maxCol)

		scr=self.app.primaryScreen()
		scrollArea.setWidget(self.tbl_app)
		scrollArea.alignment()
		scrollArea.setGeometry(QRect(0,0,w,h))
		box.addWidget(self.tbl_app)
		btn_apply=QPushButton("Apply")
		btn_apply.clicked.connect(self._save_apps)
		box.addWidget(btn_apply)
		self.setLayout(box)
	#def load_screen

	def _update_apps_data(self):
		apps=self.runner.get_apps()
		self.visible_categories=apps['categories']
		self._debug("Visible: %s"%self.visible_categories)
		return apps

	def _update_categories(self,apps,maxCol=1):
		row=0
		col=0
		def _add_desktop(desktops,state="show"):
			nonlocal row
			nonlocal col
			for desktop in desktops:
				deskInfo=self.runner.get_desktop_app(desktop)
				for appName,appIcon in deskInfo.items():
					btn_desktop=dropButton(desktop,self.tbl_app)
					if not btn_desktop.set_image(appIcon,state):
						self._debug("Discard: %s"%appName)
						btn_desktop.deleteLater()
						continue
					btnMenu=QMenu()
					action=_("Show button")
					if state=="show":
						action=_("Hide button")
					btnMenu.addAction(action)
					btnMenu.triggered.connect(lambda:self._changeBtnState(apps,maxCol,state))
					btn_desktop.setToolTip(desktop)
					btn_desktop.setMenu(btnMenu)
					btn_desktop.setObjectName("confBtn")
					self.btn_grid[btn_desktop]={"row":row,"col":col,"state":state}
					btn_desktop.signal.connect(self._dragDropEvent)
					self._debug("Adding %s at %s %s"%(appName,row,col))
					self.tbl_app.setCellWidget(row,col,btn_desktop)
					col+=1
					if col>=maxCol:
						col=0
						row+=1
						self.tbl_app.insertRow(row)
						self._debug("Insert row %s"%self.tbl_app.rowCount())

		self.tbl_app.clear()
		self.tbl_app.setRowCount(1)
		self.tbl_app.setColumnCount(maxCol)
		_add_desktop(apps['desktops'])
		_add_desktop(apps['hidden'],"hidden")
		self.tbl_app.resizeColumnsToContents()

	def _changeBtnState(self,apps,maxCol,state='show'):
		row=self.tbl_app.currentRow()
		col=self.tbl_app.currentColumn()
		btn=self.tbl_app.cellWidget(row,col)
		if state=='show':
			state='hidden'
			apps['desktops'].remove(btn.title)
			apps['hidden'].append(btn.title)
		else:
			state='show'
			apps['desktops'].append(btn.title)
			apps['hidden'].remove(btn.title)
		self.btn_grid['state']=state
		self._update_categories(apps,maxCol)

	def _dragDropEvent(self,btnEv):
		if 'drag' in btnEv.keys():
			self.btn_drag=btnEv['drag']
		else:
			if btnEv['drop']==self.btn_drag:
				self.btn_drag.showMenu()
				return False
			btn=btnEv['drop']
			if self.btn_grid[btn]['state']=='hidden' or self.btn_grid[self.btn_drag]['state']=='hidden':
				return False
			rowTo=self.btn_grid[btn]['row']
			colTo=self.btn_grid[btn]['col']
			rowFrom=self.btn_grid[self.btn_drag]['row']
			colFrom=self.btn_grid[self.btn_drag]['col']
			btnTo=btn.clone()
			btnTo.signal.connect(self._dragDropEvent)
			self.btn_grid[btnTo]=self.btn_grid[self.btn_drag]
			btnFrom=self.btn_drag.clone()
			btnFrom.signal.connect(self._dragDropEvent)
			self.btn_grid[btnFrom]=self.btn_grid[btn]
			del self.btn_grid[btn] 
			del self.btn_grid[self.btn_drag] 
			self.tbl_app.setCellWidget(rowFrom,colFrom,btnTo)
			self.tbl_app.setCellWidget(rowTo,colTo,btnFrom)

	def _save_apps(self):
		desktops=[]
		hidden=[]
		for row in range(0,self.tbl_app.rowCount()):
			for col in range(0,self.tbl_app.columnCount()):
				btn=self.tbl_app.cellWidget(row,col)
				if btn:
					self._debug("Item at %s: %s"%(row,btn))
					desktops.append(btn.title)
#			if btn_visible and btn_visible.isChecked():
#				desktops.append(item.text())
#			elif btn_visible: 
#				info=self.menu.get_desktop_info("/usr/share/applications/%s"%item.text())
#				for cat in info['Categories']:
#					if cat.lower() in self.visible_categories:
#						hidden.append(item.text())
		self._debug("Desktops: %s"%desktops)
		self.runner.write_config(desktops,key='desktops',level='user')
		self._debug("Hidden: %s"%hidden)
		self.runner.write_config(hidden,key='hidden',level='user')
	#def _save_apps

	def _define_css(self):
		css="""
		#confBtn{
			background:red;
			padding: 6px;
			margin:6px;
			border:solid black 10px;
			font: 14px Roboto;
		}
		"""
		return(css)
		#def _define_css
