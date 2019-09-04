#!/usr/bin/env python3
import sys
import os
from PyQt5.QtWidgets import QApplication
from appconfig.appConfigScreen import appConfig

app=QApplication(["Test Kid Config"])
config=appConfig({'app':app})
config.rsrc="/home/lliurex/git/testkid/rsrc"
config.appName="Run-O-Matic"
config.load_stacks()

app.exec_()
