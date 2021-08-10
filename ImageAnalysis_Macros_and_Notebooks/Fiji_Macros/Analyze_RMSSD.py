""" Analyze_heartbeat
 This ImageJ plugin was developed to analyze the heart rhythm of zebrafish larvae from time series of images in which you can follow the heart motions of ventricle and atrium.
 The input here are RGB image series from the nikon fluorescence stereoscope.
 The output files from this plugin can be analyzed using the RMSSD jupyter-notebook.

 Alexander Ernst

 Jython code, tested on Fiji with ImageJ 1.52p Java 1.8.9_211

 !!! the plugin serves as documentation and needs to be modified and adapted to your computer before running it!!!
"""

from ij import IJ, ImagePlus, ImageStack
import ij.plugin
from ij import WindowManager as WM

from ij.gui import GenericDialog, NonBlockingGenericDialog , WaitForUserDialog as WFU
from ij import WindowManager as WM  
from java.awt.event import AdjustmentListener, ItemListener 
from ij.measure import Measurements
from ij.macro import Functions
from ij.plugin import ImageInfo
from ij.io import OpenDialog
from ij.measure import ResultsTable as RT
from ij.text import TextWindow as TW
from ij.plugin.frame import RoiManager as RM

# preparation to run the loop
rm=RM.getRoiManager()
IJ.run("Clear Results", "");
IJ.run("Close All", "");
rm.reset()
# choose the directory with the image files 
directory_load = OpenDialog("Select the 6D dataset").getDirectory()
#make a list of input files
dList=os.listdir(directory_load)
# start the loop to go through all image sin the folder
for i in dList:
	IJ.run("Clear Results", "");
	IJ.run("Close All", "");
	rm.reset()
	dL= directory_load + "/" + str(i)
	#open the nd2 files with bioformats
	IJ.run("Bio-Formats", "open="+ dL +" color_mode=Default rois_import=[ROI manager] specify_range view=Hyperstack stack_order=XYCZT")
	imp=WM.getCurrentImage()
	#apply a gaussian blur to improve the automatic detection
	IJ.run(imp, "Gaussian Blur...", "sigma=10 stack")
	#get title for results
	title=imp.getShortTitle();
	# draw a line to measure the beating
	IJ.setTool("line")
	wfu= WFU("Add a line to the ventricle")
	wfu.show()
	rm.runCommand("Add")
	# create a kymograph of the ventricle to detect the maxima and therewith each heartbeat over time 
	IJ.run(imp, "Multi Kymograph", "linewidth=1")
	Kymo_ventricle=WM.getImage("Kymograph")
	Kymo_ventricle.setTitle("Kymograph_ventricle");
	IJ.run(Kymo_ventricle, "Find Maxima...", "prominence=8 output=[Point Selection]")
	wfu_check1= WFU("Are the maxima okay?")
	wfu_check1.show()
	rm.runCommand("Add")
	IJ.run(Kymo_ventricle, "Measure", "")
	# save the results
	IJ.saveAs("Results", "C:/Users/aernst/Desktop/Heartbeat analysis/Result_tables/"+title+"_result_table_ventricle.csv")
	IJ.saveAs(Kymo_ventricle, "Tiff", "C:/Users/aernst/Desktop/Heartbeat analysis/Result_kymographs/"+title+"_kymograph_ventricle.tif")
	IJ.run("Clear Results", "");
	# draw a line to measure the beating of the atrium
	IJ.setTool("line")
	wfu2= WFU("Add a line to the atrium")
	wfu2.show()
	wfu3= WFU("Are you sure?")
	wfu3.show()
	rm.runCommand("Add")
	# create a kymograph of the atrium to detect the maxima and therewith each heartbeat over time 
	IJ.run(imp, "Multi Kymograph", "linewidth=1")
	
	Kymo_atrium=WM.getImage("Kymograph");
	IJ.run(Kymo_atrium, "Find Maxima...", "prominence=8 output=[Point Selection]")
	Kymo_atrium.setTitle("Kymograph_atrium");	
	wfu_check2= WFU("Are the maxima okay?")
	wfu_check2.show()
	rm.runCommand("Add")
	IJ.run(Kymo_atrium, "Measure", "")
	# save the results
	IJ.saveAs("Results", "C:/Users/aernst/Desktop/Heartbeat analysis/Result_tables/"+title+"_result_table_atrium.csv")
	IJ.saveAs(imp, "Tiff", "C:/Users/aernst/Desktop/Heartbeat analysis/Result_images/"+title+"_blurred.tif")
	IJ.saveAs(Kymo_atrium, "Tiff", "C:/Users/aernst/Desktop/Heartbeat analysis/Result_kymographs/"+title+"_kymograph_atrium.tif")
	rm.runCommand("Deselect")
	rm.runCommand("Save", "C:/Users/aernst/Desktop/Heartbeat analysis/Result_RoiSets/"+title+"_Rois.zip")
	