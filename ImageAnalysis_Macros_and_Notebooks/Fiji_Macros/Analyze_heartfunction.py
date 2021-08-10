""" Analyze_heartbeat
 This ImageJ plugin was developed to analyze the heart function of zebrafish larvae from time series of images in which you can follow the heart motions of ventricle and atrium.
 The input here are RGB image series from the nikon fluorescence stereoscope with 100 frames or more.
 The output files from this plugin can be analyzed using the Analyze_heartbeat jupyter-notebook.

 Alexander Ernst

 Jython code, tested on FIJI with ImageJ 1.52p Java 1.8.9_211

 !!! the plugin serves as documentation and needs to be modified and adapted to your computer before running it!!!
"""
from ij import IJ, ImagePlus, ImageStack
import ij.plugin
from ij import WindowManager as WM
import os  
from os import path 
import re
from ij.gui import GenericDialog as GD, NonBlockingGenericDialog as NBD , WaitForUserDialog as WFU
from ij import WindowManager as WM  
from java.awt.event import AdjustmentListener, ItemListener 
from ij.measure import Measurements
from ij.macro import Functions
from ij.plugin import ImageInfo
from ij.io import OpenDialog,DirectoryChooser
from ij.measure import ResultsTable as RT
from ij.text import TextWindow as TW
from ij.plugin.frame import RoiManager as RM
from ij.text import TextWindow, TextPanel
from java.util import ArrayList


# Define function to handle dialogs 
def wfuDial(text):
	wfu= WFU(text)
	wfu.show()
	rm.runCommand("Add")
	IJ.run(imp, "Select None", "")
# Define function to show the right dialogs for the current measurement, measure and name the current measurement
def area_measures(No, phase):
	IJ.setTool("line")
	wfuDial(""+ phase +"_"+ No +"Ventricle, draw line short axis")

	IJ.setTool("line")
	wfuDial(""+ phase +"_"+ No +"Ventricle, draw line long axis")
	
	IJ.setTool("line")
	wfuDial(""+ phase +"_"+ No +"Atrium, draw line short axis")
		
	IJ.setTool("line")
	wfuDial(""+ phase +"_"+ No +"Atrium, draw line long axis")
	#save in which frame you measured
	frame=imp.getFrame()
	
	IJ.run("Set Measurements...", "area centroid redirect=None decimal=3")
	rm.runCommand("Deselect")
	rm.runCommand(imp, "Measure")
	# store the measurements in variables
	Results=RT.getResultsTable()
	longVen=RT.getValue(Results,"Length",1)
	shortVen=RT.getValue(Results,"Length",0)
	longAt=RT.getValue(Results,"Length",3)
	shortAt=RT.getValue(Results,"Length",2)
	# get title of the image
	title=imp.getShortTitle()
	# make an array of the measurement
	A=ArrayList([shortVen,longVen,shortAt,longAt,frame])
	# reset the results window and roi manager 
	IJ.run("Clear Results", "");
	rm.reset()
	# return the array with the measurements
	return A
	
# preparation to run the functions
rm=RM.getRoiManager()
IJ.run("Clear Results", "");
IJ.run("Close All", "");
rm.reset()
# open a dialog to get the input folder
directory_load = OpenDialog("Select the heartbeat movie").getDirectory()
directory_save = DirectoryChooser("Folder to save").getDirectory()
# make a list of the files in the folder
dList=os.listdir(directory_load)

# go through all the files
for i in dList:
	IJ.run("Clear Results", "");
	IJ.run("Close All", "");
	rm.reset()
	dL= directory_load + "/" + str(i)
	# open the nd2 file with bioformats
	IJ.run("Bio-Formats", "open="+ dL +" color_mode=Default rois_import=[ROI manager] specify_range view=Hyperstack stack_order=XYCZT c_begin=2 c_end=2 c_step=1 t_begin=1 t_end=100 t_step=1");
	imp=WM.getCurrentImage()
	# set the image properties,as errors occurred when reading the metadata, needs to be adapted
	IJ.run(imp, "Properties...", "channels=1 slices=1 frames=100 unit=micron pixel_width=0.29 pixel_height=0.29 voxel_depth=1.0000000 frame=[0.06 sec]");
	tot_frames=imp.getNFrames()
	interval=0.06
	# apply a gaussian blur filter to facilitate the measurements
	IJ.run(imp, "Gaussian Blur...", "sigma=10 stack")
	title=imp.getShortTitle()
	# apply the functions to measure the heart diameters
	if "/" in title:
		title=re.sub("/","", title)
	A =area_measures("1 ", "end-diastole")
	B =area_measures("1 ", "end-systole")
	C =area_measures("2 ", "end-diastole")
	D =area_measures("2 ", "end-systole")

	# now we measure the heart rate by drawing a line crossing the border of the ventricle
	IJ.setTool("line")
	wfu= WFU("Add a line to the ventricle")
	wfu.show()
	rm.runCommand("Add")
	rm.reset()
	IJ.run("Clear Results", "")
	# make a kymograph
	IJ.run(imp, "Multi Kymograph", "linewidth=1")
	Kymo_ventricle=WM.getImage("Kymograph")
	Kymo_ventricle.setTitle("Kymograph_ventricle")
	# localize the maxima in the kymograph, each maximum should represent one heartbeat 
	IJ.run(Kymo_ventricle, "Find Maxima...", "prominence=15 output=[Point Selection]")
	# you can now manually check the heart rate
	wfu_check1= GD("Are the maxima okay?")
	wfu_check1.showDialog()
	# cancel the dialog if the maxima are incorrect
	if wfu_check1.wasCanceled(): 
		wfu_check2= GD("Count the heart beats and enter the value here?")  
		wfu_check2.addNumericField("Heart beat count", 6,0) 
		wfu_check2.showDialog()
		heartrate=wfu_check2.getNextNumber()
	# otherwise the measurements will be saved as they are
	else:
		rm.runCommand("Add")
		IJ.run(Kymo_ventricle, "Measure", "")
		rt=RT.getResultsTable()
		heartrate=float(RT.getCounter(rt))
		print(heartrate)
		IJ.saveAs("Results", ""+ directory_save +"/Result_tables/"+title+"_result_table_ventricle.csv")
		IJ.saveAs(Kymo_ventricle, "Tiff", ""+ directory_save +"/Result_kymographs/"+title+"_kymograph_ventricle.tif")
	IJ.run("Clear Results", "")
	hr=heartrate/(interval*tot_frames)
	# now create a common output table for all images, new results will be appended to the .csv-file
	f = open(""+directory_save+"/Result_heart_volume.csv", "a")
		
	f.write("ImgTitle,"\
			"Short_ax_diastole_Ventricle_1,Long_ax_diastole_Ventricle_1,Short_ax_diastole_Atrium_1,Long_ax_diastole_Atrium_1,frame_diastole_1,"\
			"Short_ax_systole_Ventricle_1,Long_ax_systole_Ventricle_1,Short_ax_systole_Ventricle_1,Long_ax_systole_Atrium_1,frame_systole_1,"\
			"Short_ax_diastole_Ventricle_2,Long_ax_diastole_Ventricle_2,Short_ax_diastole_Atrium_2,Long_ax_diastole_Atrium_2,frame_diastole_2,"\
			"Short_ax_systole_Ventricle_2,Long_ax_systole_Ventricle_2,Short_ax_systole_Ventricle_2,Long_ax_systole_Atrium_2,frame_systole_2,"\
			"HR_Bps,Framerate_s_,N_of_frames"\
			"\n")
	f.write(""+ title +","+ str(A[0]) +","+ str(A[1]) +","+ str(A[2]) + ","+ str(A[3]) + ","+ str(A[4]) +","+ str(B[0]) +","+ str(B[1]) +","+ str(B[2]) +","+ str(B[3]) + ","+ str(B[4]) +","+ str(C[0]) +","+ str(C[1]) +","+ str(C[2]) +","+ str(C[3]) + ","+ str(C[4]) +","+ str(D[0]) +","+ str(D[1]) +","+ str(D[2]) +","+ str(D[3]) + ","+ str(D[4]) +","+ str(hr) +","+ str(interval) +","+ str(tot_frames) + "\n")
	
	f.close()
	
