

import sys
from PyQt5.QtWidgets import QMainWindow, QDialog, QApplication, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QWidget, QInputDialog, QLineEdit, QFileDialog, QAction, QTextEdit, QLabel, QTabWidget
from PyQt5.QtGui import QIcon
from PyQt5 import QtGui

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

import numpy as np
import math
import pandas as pd
import seaborn as sns

import os
import re
import math

#temp data storage
import temp_df as dfdat

def plot_zoom(h5Axis):
	h5Axis.set_title(hdat.filename)
	h5data = hdat.data[hdat.scanY,:,:]
	h5Axis.imshow(h5data, cmap = h5_cmap)
		
	dfdat.canvas.draw()

def onclick(event):
	dfdat.zoom_axis.clear()
	ax = event.inaxes
	if ax is None:
		return
	
	xdata = []
	ydata = []	
	if ((event.dblclick is False) and (event.button == 1)):
		for line in ax.get_lines():
			if line is not None:
				xdata.append(line.get_xdata())
				ydata.append(line.get_ydata())
				for X, Y in zip(xdata, ydata):
					dfdat.zoom_axis.plot(X, Y, linestyle = 'None', marker = 'o', 
										 markersize = 2)
#			else:
			    #get data
			    #objs = []
			    #for obj in ax.get_children():
					#objs.append(obj)
				#colNames.index(objs[0]._label)
			    
			    
			    #dfdat.zoom_axis.hist(gotten data)			
		dfdat.zoom_axis.spines['right'].set_visible(False)
		dfdat.zoom_axis.spines['top'].set_visible(False)		
		dfdat.canvas.draw()	
		
class QPlotter(QWidget):
	def __init__(self, parent=None):		
		super(QPlotter, self).__init__(parent)

		dfdat.fig = plt.figure()
		dfdat.canvas = FigureCanvas(dfdat.fig)
		cid = dfdat.canvas.mpl_connect('button_press_event', onclick)	

		self.toolbar1 = NavigationToolbar(dfdat.canvas, self)

		self.button1 = QPushButton('Clear Plot')
		self.button1.clicked.connect(self.clear_plot)

		buttons = QHBoxLayout()
		buttons.addStretch(1)
		buttons.addWidget(self.button1)
		
		controls = QHBoxLayout()
		controls.addStretch(1)
		controls.addLayout(buttons)

		layout = QVBoxLayout()
		layout.addWidget(self.toolbar1)
		layout.addWidget(dfdat.canvas)
		layout.addLayout(controls)
		self.setLayout(layout)

#		self.setMouseTracking(True)

	def clear_plot(self):
		dfdat.fig.clear()
		dfdat.canvas.draw()
		
	def plot(self):

		[rows, cols] = np.shape(dfdat.dataFrame)
		gs = gridspec.GridSpec(cols-2,2*(cols-2))

		dfdat.axes = np.empty([cols-2,cols-2], dtype = 'object')
		dfdat.zoom_axis = dfdat.fig.add_subplot(gs[:, cols-2:])
		
		for i in np.arange(cols-2):
			for j in np.arange(cols-2):
				dfdat.axes[i,j] = dfdat.fig.add_subplot(gs[i, j])
				dfdat.axes[i,j].spines['right'].set_visible(False)
				dfdat.axes[i,j].spines['top'].set_visible(False)
				xlab = dfdat.colNames[j+1]
				ylab = dfdat.colNames[i+1]
				if (j!=0): 
					ylab = ' '
					dfdat.axes[i,j].tick_params(axis='y', which='both', 
												left=False, right=False, 
												labelleft=False)
					if (i != cols-3):
						dfdat.axes[i,j].tick_params(axis='x', which='both', 
													bottom=False, top=False, 
													labelbottom=False)
						xlab = ' ' 
				elif (i != cols -3):
					xlab = ' '
					dfdat.axes[i,j].tick_params(axis='x', which='both', 
												bottom=False, top=False, 
												labelbottom=False)
				if (i == j):
					dfdat.axes[i,j].hist(dfdat.dataFrame.iloc[:,j+1])
				else:
					dfdat.axes[i,j].plot(dfdat.dataFrame.iloc[:,j+1], 
										 dfdat.dataFrame.iloc[:,i+1], 
										 linestyle = 'None', marker = 'o', 
										 markersize = 1)
				dfdat.axes[i,j].set(xlabel = xlab, ylabel = ylab)

	
		#for i in np.arange(cols-2):
			#for j in np.arange(cols-2):
				#dfdat.axes[i,j] = dfdat.fig.add_subplot(gs[i, j])
				#if (i == j):
					#dfdat.axes[i,j].hist(dfdat.dataFrame.iloc[:,i+1])
				#else:
					#dfdat.axes[i,j].plot(dfdat.dataFrame.iloc[:,i+1], 
										 #dfdat.dataFrame.iloc[:,j+1], marker = 'o',
										 #markersize = 1, linestyle = 'None')
#		corr_plots = sns.pairplot(dfdat.dataFrame)
#		dfdat.pg = corr_plots
#		dfdat.fig = corr_plots.fig
#		dfdat.axes = corr_plots.axes



		print('Shape of axes object array: ',np.shape(dfdat.axes))
#		dfdat.canvas = FigureCanvas(dfdat.fig)

		# refresh canvas
		dfdat.canvas.draw()	
#dfdat.canvas.update()

class App(QMainWindow):
	def __init__(self, parent=None):
		super().__init__()
		self.title = 'Data Correlation Explorer'
		self.default_dir = '/'
		self.left = 10
		self.top = 10
		self.width = 1250
		self.height = 750
		self.initUI()
 
	def initUI(self):
		self.setWindowTitle(self.title)
		self.setGeometry(self.left, self.top, self.width, self.height)

		self.plotter = QPlotter()
		self.setCentralWidget(self.plotter)

	
		mainMenu = self.menuBar()
		fileMenu = mainMenu.addMenu('&File')
		helpMenu = mainMenu.addMenu('Help')

		openFile = QAction("&Open Dataset", self)
		openFile.setShortcut("Ctrl+O")
		openFile.setStatusTip('Open Dataset')
		openFile.triggered.connect(self.choose_dataset)
		fileMenu.addAction(openFile)

		extractAction = QAction("&Quit", self)
		extractAction.setShortcut("Ctrl+Q")
		extractAction.setStatusTip('Leave The App')
		extractAction.triggered.connect(self.close_application)
		fileMenu.addAction(extractAction)

		self.show()

	def choose_dataset(self):
		#irs data: https://vincentarelbundock.github.io/Rdatasets/csv/datasets/iris.csv
		#mtcars data: https://vincentarelbundock.github.io/Rdatasets/csv/datasets/mtcars.csv
		df = pd.read_csv('https://vincentarelbundock.github.io/Rdatasets/csv/datasets/iris.csv')
		dfdat.dataFrame = df
		dfdat.colNames = list(df)
		

		print('Data frame columns',list(df))
		#Later make a dialog with list of files that then opens another datalog
		#where the user can choose which columns to compare
		
		self.plotter.plot()

	def close_application(self):
		sys.exit()
			

if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = App()
	sys.exit(app.exec_())
