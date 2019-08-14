#!/usr/bin/env python3
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,\
				QDialog,QGridLayout,QHBoxLayout,QFormLayout,QLineEdit,QComboBox,\
				QStatusBar,QFileDialog,QDialogButtonBox,QScrollBar,QScrollArea,QListWidget,\
				QListWidgetItem,QStackedWidget,QButtonGroup,QComboBox,QTableWidget,QTableWidgetItem,\
				QHeaderView
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
		self.setAcceptDrops(True)
		self.setMaximumWidth(BTN_SIZE)

	def dragEnterEvent(self,e):
		print (e.accept())
	
	def mousePressEvent(self,e):
		print("Press %s"%self)
		print("Press %s"%self.title)
		self.signal.emit({"drag":self})
		mimedata=QMimeData()
		drag=QtGui.QDrag(self)
		drag.setMimeData(mimedata)
#		drag.setHotSpot(e.pos()-self.rect().topLeft())
		dropAction=drag.exec_(Qt.MoveAction)

	def dropEvent(self,e):
		print("OK %s"%self)
		position=e.pos()
#		self.button.move(position)
		e.setDropAction(Qt.MoveAction)
		e.accept()
		self.signal.emit({"drop":self})

	def set_image(self,img):
		self.img=img
		if QtGui.QIcon.hasThemeIcon(self.img):
			icnApp=QtGui.QIcon.fromTheme(self.img)
		else:
			return None
		self.setIcon(icnApp)
		self.setIconSize(QSize(BTN_SIZE,BTN_SIZE))
		return True

	def clone(self):
		btn=dropButton(self.title,self.parent)
		btn.set_image(self.img)
		return(btn)
#	def mouseMoveEvent(self,e):
#		if e.button()!=Qt.RightButton:
#			return
#		mimedata=QtCore.QMimeData()
#		drag=QDrag(self)
#		drag.setMimeData(mimedata)
#		drag.setHotSpot(e.pos()-self.rect().topLeft())
#		dropAction=drag.start(Qt.MoveAction)

class dropTable(QTableWidget):
	def __init__(self,rows,columns,parent):
		super (dropTable,self).__init__(rows,columns,parent)
		self.setAcceptDrops(True)

	def dragEnterEvent(self,e):
		print (e.accept())

	def dropEvent(self,e):
		print("OK")
		position=e.pos()
		self.button.move(position)
		e.setDropAction(Qt.MoveAction)
		e.accept()

class confScr(QWidget):
	dragdrop_signal=pyqtSignal("PyQt_PyObject")
	def __init__(self,app):
		super().__init__()
		self.dbg=True
		self.app=app
		self.setStyleSheet(self._define_css())
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
#		self.tbl_app=QTableWidget(1,2)
		self.tbl_app=dropTable(1,2,self)
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
		box=QHBoxLayout()
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
		self._update_categories(maxCol)

		scr=self.app.primaryScreen()
		scrollArea.setWidget(self.tbl_app)
		scrollArea.alignment()
		scrollArea.setGeometry(QRect(0,0,w,h))
		box.addWidget(self.tbl_app)
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
		self.desktops=data['desktops']

	def _update_categories(self,maxCol=1):
		row=0
		col=0
		self._update_apps_data()
		self.tbl_app.clear()
		self.tbl_app.setRowCount(1)
		self.tbl_app.setColumnCount(maxCol)
		for desktop in self.desktops:
			deskInfo=self.runner.get_desktop_app(desktop)
			print(deskInfo)
			for appName,appIcon in deskInfo.items():
#				btn_desktop=QPushButton()
				btn_desktop=dropButton(appName,self.tbl_app)
				if not btn_desktop.set_image(appIcon):
					print("Discard: %s"%appName)
					btn_desktop.deleteLater()
					continue
				self.btn_grid[btn_desktop]={"row":row,"col":col}
				btn_desktop.signal.connect(self._dragDropEvent)
				self._debug("Adding %s at %s %s"%(appName,row,col))
				self.tbl_app.setCellWidget(row,col,btn_desktop)
				col+=1
				if col>=maxCol:
					col=0
					row+=1
					self.tbl_app.insertRow(row)
					print("Insert row %s"%self.tbl_app.rowCount())
#		self.tbl_app.removeRow(row)
		self.tbl_app.resizeColumnsToContents()

	def _dragDropEvent(self,btnEv):
		if 'drag' in btnEv.keys():
			self.btn_drag=btnEv['drag']
		else:
			if btnEv['drop']==self.btn_drag:
				return False
			btn=btnEv['drop']
			rowTo=self.btn_grid[btn]['row']
			colTo=self.btn_grid[btn]['col']
			print("To %s at %s %s"%(btn,rowTo,colTo))
			rowFrom=self.btn_grid[self.btn_drag]['row']
			colFrom=self.btn_grid[self.btn_drag]['col']
			print("From %s at %s %s"%(self.btn_drag,rowFrom,colFrom))
			btnTo=btn.clone()
			btnTo.signal.connect(self._dragDropEvent)
			self.btn_grid[btnTo]=self.btn_grid[self.btn_drag]
			print(self.btn_grid[btnTo])
			btnFrom=self.btn_drag.clone()
			btnFrom.signal.connect(self._dragDropEvent)
			self.btn_grid[btnFrom]=self.btn_grid[btn]
			print("%s - %s"%(btnFrom,self.btn_drag))
			del self.btn_grid[btn] 
			del self.btn_grid[self.btn_drag] 
			self.tbl_app.setCellWidget(rowFrom,colFrom,btnTo)
			self.tbl_app.setCellWidget(rowTo,colTo,btnFrom)

	def _save_categories(self):
		categories=[]
		for row in range(0,self.tbl_cat.rowCount()):

			btn_visible=self.tbl_cat.cellWidget(row,1)
			self._debug("Item at %s: %s"%(row,btn_visible))
			if btn_visible and btn_visible.isChecked():
				item=self.tbl_cat.item(row,0)
				categories.append(item.text())
		self._debug("Categories: %s"%categories)
		self.runner.write_config(categories,key='categories',level='user')
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
		self.runner.write_config(desktops,key='desktops',level='user')
		self._debug("Hidden: %s"%hidden)
		self.runner.write_config(hidden,key='hidden',level='user')
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
