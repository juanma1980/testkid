#!/usr/bin/env python3
import os
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,\
				QDialog,QGridLayout,QHBoxLayout,QFormLayout,QLineEdit,QComboBox,\
				QStatusBar,QFileDialog,QDialogButtonBox,QScrollBar,QScrollArea,QListWidget,\
				QListWidgetItem,QStackedWidget,QButtonGroup,QComboBox,QTableWidget,QTableWidgetItem,\
				QHeaderView,QMenu,QAction
from PyQt5 import QtGui
from PyQt5.QtCore import QSize,pyqtSlot,Qt, QPropertyAnimation,QThread,QRect,QTimer,pyqtSignal,QSignalMapper,QProcess,QEvent,QMimeData
import gettext
from app2menu import App2Menu
from libAppRun import appRun

gettext.textdomain('testConfig')
_ = gettext.gettext

QString=type("")
QBool=type(True)
BTN_SIZE_FULL=128
BTN_SIZE=32


class dropTable(QTableWidget):
	drop=pyqtSignal("PyQt_PyObject")
	def __init__(self,parent,row,col):
		super (dropTable,self).__init__(row,col,parent)
		self.parent=parent
		self.setAcceptDrops(True)
		self.setDragEnabled(True)
		Hheader=self.horizontalHeader()
		Vheader=self.verticalHeader()
		self.setShowGrid(False)
		self.horizontalHeader().hide()
		self.verticalHeader().hide()
	
	def dragEnterEvent(self,e):
		e.accept()
	#def dragEnterEvent
	
	def dragMoveEvent(self,e):
		e.accept()
	#def dragEnterEvent
	
	def dropEvent(self,e):
		path=None
		e.setDropAction(Qt.MoveAction)
		e.accept()
		if e.mimeData().hasUrls():
			path=e.mimeData().urls()[0].path()
		self.drop.emit(path)

class dropButton(QPushButton):
	drop=pyqtSignal("PyQt_PyObject")
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
		self.drop.emit({"drag":self})
		self.position=e.pos()
		mimedata=QMimeData()
		drag=QtGui.QDrag(self)
		drag.setMimeData(mimedata)
		pixmap=self.icon.pixmap(QSize(BTN_SIZE,BTN_SIZE))
		drag.setPixmap(pixmap)
		dropAction=drag.exec_(Qt.MoveAction)
	#def mousePressEvent

	def dropEvent(self,e):
		position=e.pos()
		e.setDropAction(Qt.MoveAction)
		e.accept()
		path=None
		if e.mimeData().hasUrls():
			path=e.mimeData().urls()[0].path()
		self.drop.emit({"drop":self,'path':path})
	#def dropEvent

	def set_image(self,img,state='show'):
		self.img=img
		if QtGui.QIcon.hasThemeIcon(self.img):
			self.icon=QtGui.QIcon.fromTheme(self.img)
			if state!='show':
				pixmap=self.icon.pixmap(QSize(BTN_SIZE,BTN_SIZE))
				image=pixmap.toImage().convertToFormat(QtGui.QImage.Format_Grayscale8)
				bg_pixmap=QtGui.QPixmap.fromImage(image)
				self.icon=QtGui.QIcon(bg_pixmap)
		else:
			if os.path.isfile(self.img):
				self.icon=QtGui.QIcon(self.img)
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

class confLaunchers(QWidget):
	dragdrop_signal=pyqtSignal("PyQt_PyObject")
	def __init__(self,app):
		super().__init__()
		self.dbg=True
		self.app=app
		self.setStyleSheet(self._define_css())
		self.runner=appRun()
		self.tbl_app=dropTable(self,1,2)
		self.tbl_app.drop.connect(self._tbl_DropEvent)
		self.btn_grid={}
		self.btn_drag=None
		self.visible_categories=[]
		self.menu=App2Menu.app2menu()
		self.categories=[]
		(self.columns,self.width,self.height)=self._get_screen_size()
		self._load_screen()
		self.setStyleSheet(self._define_css())
	#def __init__

	def _debug(self,msg):
		if self.dbg:
			print("ConfLaunchers: %s"%msg)
	#def _debug

	def _get_screen_size(self):
		row=0
		col=0
		scr=self.app.primaryScreen()
		w=scr.size().width()-BTN_SIZE_FULL
		h=scr.size().height()-(2*BTN_SIZE_FULL)
		columns=int(w/BTN_SIZE_FULL)-3
		return (columns,w,h)
	#def _get_screen_size

	def _load_screen(self):
		def _update_categories(cat):
			if cat in self.visible_categories:
				self.visible_categories.remove(cat)
			else:
				self.visible_categories.append(cat)
			apps=self.runner.get_apps(self.visible_categories,False)
			self._update_screen(apps)
		
		def _update_desktops():
			fdia=QFileDialog()
			fchoosed=''
			fdia.setFileMode(QFileDialog.AnyFile)
			fdia.setNameFilter(_("desktops(*.desktop)"))
			fdia.setDirectory("/usr/share/applications")
			if (fdia.exec_()):
				fchoosed=fdia.selectedFiles()[0]
				apps['desktops'].append(fchoosed)
				self._update_screen(apps)

		apps=self._update_apps_data()
		sigmap_catSelect=QSignalMapper(self)
		sigmap_catSelect.mapped[QString].connect(_update_categories)
		box=QVBoxLayout()
		btnBox=QHBoxLayout()
		btn_cat=QPushButton(_("Categories"))
		menu_cat=QMenu()
		for cat in self._get_all_categories():
			act=QAction(cat,menu_cat)
			act.setCheckable(True)
			if cat in self.visible_categories:
				act.setChecked(True)
			menu_cat.addAction(act)
			sigmap_catSelect.setMapping(act,cat)
			act.triggered.connect(sigmap_catSelect.map)
		btn_cat.setMenu(menu_cat)
		btn_add=QPushButton(_("Add launcher"))
		btn_add.setToolTip(_("Add Launcher"))
#		icnAdd=QtGui.QIcon.fromTheme("list-add")
#		btn_add.setIcon(icnAdd)
		btn_add.clicked.connect(_update_desktops)
		btnBox.addWidget(btn_cat)
		btnBox.addWidget(btn_add)
		box.addLayout(btnBox)
		tabScroll=QWidget()
		tabScroll.setFocusPolicy(Qt.NoFocus)
		scrollArea=QScrollArea(tabScroll)
		scrollArea.setFocusPolicy(Qt.NoFocus)
		self._update_screen(apps)
		scr=self.app.primaryScreen()
		scrollArea.setWidget(self.tbl_app)
		scrollArea.alignment()
		scrollArea.setGeometry(QRect(0,0,self.width,self.height))
		box.addWidget(self.tbl_app)
		btn_apply=QPushButton("Apply")
		btn_apply.clicked.connect(self._save_apps)
		box.addWidget(btn_apply)
		self.setLayout(box)
	#def load_screen
	
	def _tbl_DropEvent(self,path):
		if path.endswith('desktop'):
			if os.path.isfile(path):
				apps=self._get_table_apps()
				apps['desktops'].append(path)
				self._update_screen(apps)

	#def _tbl_DropEvent

	def _update_apps_data(self):
		apps=self.runner.get_apps()
		self.visible_categories=apps['categories']
		self._debug("Visible: %s"%self.visible_categories)
		return apps
	#def _update_apps_data

	def _update_screen(self,apps):
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
					btnMenu.triggered.connect(lambda:self._changeBtnState(apps,state))
					btn_desktop.setToolTip(desktop)
					btn_desktop.setMenu(btnMenu)
					btn_desktop.setObjectName("confBtn")
					self.btn_grid[btn_desktop]={"row":row,"col":col,"state":state}
					btn_desktop.drop.connect(self._btn_dragDropEvent)
					self._debug("Adding %s at %s %s"%(appName,row,col))
					self.tbl_app.setCellWidget(row,col,btn_desktop)
					col+=1
					if col>=self.columns:
						col=0
						row+=1
						self.tbl_app.insertRow(row)
						self._debug("Insert row %s"%self.tbl_app.rowCount())

		self.tbl_app.clear()
		self.tbl_app.setRowCount(1)
		self.tbl_app.setColumnCount(self.columns)
		_add_desktop(apps['desktops'])
		_add_desktop(apps['hidden'],"hidden")
		self.tbl_app.resizeColumnsToContents()

	def _changeBtnState(self,apps,state='show'):
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
		self._update_screen(apps)
	#def _changeBtnState

	def _btn_dragDropEvent(self,btnEv):
		if 'drag' in btnEv.keys():
			self.btn_drag=btnEv['drag']
		else:
			if btnEv.get('drop')==self.btn_drag:
				self.btn_drag.showMenu()
				self.btn_drag=None
				return False
			btn=btnEv.get('drop')
			if self.btn_grid.get(btn,{}).get('state')=='hidden' or self.btn_grid.get(self.btn_drag,{}).get('state')=='hidden':
				self.btn_drag=None
				return False

			if self.btn_drag==None and btnEv.get('path',None)==None:
				return False
			replace=False
			if replace:
				rowTo=self.btn_grid[btn]['row']
				colTo=self.btn_grid[btn]['col']
				rowFrom=self.btn_grid[self.btn_drag]['row']
				colFrom=self.btn_grid[self.btn_drag]['col']
				btnTo=btn.clone()
				btnTo.drop.connect(self._btn_dragDropEvent)
				self.btn_grid[btnTo]=self.btn_grid[self.btn_drag]
				btnFrom=self.btn_drag.clone()
				btnFrom.drop.connect(self._btn_dragDropEvent)
				self.btn_grid[btnFrom]=self.btn_grid[btn]
				del self.btn_grid[btn] 
				del self.btn_grid[self.btn_drag] 
				self.tbl_app.setCellWidget(rowFrom,colFrom,btnTo)
				self.tbl_app.setCellWidget(rowTo,colTo,btnFrom)
				self.btn_drag=None
			else:
				#Build desktops array
				apps=self._get_table_apps()
				position=apps['desktops'].index(btn.title)
				self._debug("Btn at pos: %s"%position)
				if btnEv.get('path',None):
					apps['desktops'].insert(position,btnEv['path'])
				else:
					apps['desktops'].remove(self.btn_drag.title)
					apps['desktops'].insert(position,self.btn_drag.title)
				self._update_screen(apps)
				self.btn_drag=None
	#def _btn_dragDropEvent

	def _save_apps(self):
		apps=self._get_table_apps()
		self._debug("Apps: %s"%apps)
		for key,data in apps.items():
			self.runner.write_config(data,key=key,level='system')
		self.runner.write_config(self.visible_categories,key='categories',level='system')
	#def _save_apps

	def _get_table_apps(self):
		apps={'desktops':[],'hidden':[]}
		for row in range(0,self.tbl_app.rowCount()):
			for col in range(0,self.tbl_app.columnCount()):
				btn=self.tbl_app.cellWidget(row,col)
				if btn:
					self._debug("Item at %s: %s"%(row,btn))
					if self.btn_grid[btn]['state']=='show':
						apps['desktops'].append(btn.title)
					else:
						apps['hidden'].append(btn.title)
		return apps

	def _get_all_categories(self):
		categories=[]
		categories=self.menu.get_categories()
		categories.insert(0,'run-o-matic')
		return categories

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
