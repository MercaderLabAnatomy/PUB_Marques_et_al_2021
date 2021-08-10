"""The Converter_6D

6D_processor
This Plugin for FIJI is made to facilitate browsing through XYTCZL .lif datasets (T: frames C:Channels Z:slices, L: loops) datasets, using the virtual stack function. 
The ImageJ programming tutorial "https://www.ini.uzh.ch/~acardona/fiji-tutorial/" was taken as template to create an interactive controller for these 
complex datasets. The dialogs are non-blocking and with this the roi-manager can be used to perform some preliminary analysis. 
Principle:
The .lif-files are opened with the bioformats importer as normal virtualstack, not hyperstack. 
The properties are read from the metadata and subsequently Channels and Slices are set to 1, while all dimensions
are put into the slices (T=T*C*Z*loops). A dialog is opened and the controller window based on an AdjustmentListener, will enable you to 
navigate through the datasets.  The windows are kept separate, as our microscope is recording the two channels individually and in this sense the channels are not aligned. 

Application: 
The bioformats-importer does a great job with opening different datasets, but will not show more than 5 dimensions. 
This Plugin is made for the specific purpose of helping the users of the Leica DLS XYTZL mode to quickly browse their datasets.  
These files are usually large, for this reason the virtualstack function is used. Future versions will offer more processing functionalites.
 
Testdata can be provided on request, as the files are between 500 - 1500 gb big. 

Alexander Ernst
Institute of anatomy, University of Bern
Programmed in Jython, tested on FIJI: IJ.getVersion: 2.0.0-rc-69/1.52p   and java.version: 1.8.0_172
"""
from ij import IJ, ImagePlus, ImageStack, CompositeImage    
from ij.plugin import HyperStackConverter
import ij.plugin
from ij import WindowManager as WM

from ij.macro import Interpreter as IJ1 
from ij.gui import GenericDialog, NonBlockingGenericDialog 
from ij.io import OpenDialog, DirectoryChooser

import math
import os  
from os import path 
import re
from re import sub

def XYTCZL(directory_load,directory_save,chl,frames,z_planes,loops,total,pat,title):
	
	def pattern_closer(pat):
		impopen = [WM.getImage(id) for id in WM.getIDList()]  
		for wind in impopen:  
				imp2close=wind
				if ""+ pat +"_R" in str(wind):
					imp2close.close()			

	def hyperSC(num,istr):
			imp2=impl[num]
			imp2 = HyperStackConverter.toHyperStack(imp2, 2, 1, 50,"xytcz", "Color");
			if (num-2) < 10:
				numstr= "000" + str(num-2)
			elif (num-2) < 100 :
				numstr= "00" + str(num-2)
			elif (num-2) > 99:
				numstr= "0" + str(num-2)
			IJ.saveAs(imp2, "Tiff",""+ directory_save + title +"_R" + istr +"_Z"+ numstr +".tif")
	
	IJ.run("Close All", "")
	#Calculated variables
	range_rep=total/loops
	rangeDef=loops + 1
	
	IJ1.batchMode = True 
	imp=IJ.run("Bio-Formats", "open="+ directory_load +" color_mode=Default rois_import=[ROI manager] view=[Standard ImageJ] stack_order=Default use_virtual_stack series_2")
	
	for i in range(loops):
		start=str(1+i*range_rep)
		end=str(range_rep + i*range_rep)
		
		if i < 10:
			istr= "000" + str(i)
		elif i < 100 :
			istr= "00" + str(i)
		elif i > 99:
			istr= "0" + str(i)
		
		impDup=IJ.run(imp, "Duplicate...", "title="+ title + "_R"+ istr +" duplicate range="+ start +"-"+ end +"")
	
		IJ.run(impDup,"Stack Splitter", "number="+ str(z_planes) +"")
		
	
		impl = [WM.getImage(id) for id in WM.getIDList()]  
		
			
		a=[hyperSC(num,istr) for num in range(2,z_planes+2)]
		pattern_closer(pat)	
	IJ1.batchMode = False 

def SubsetL(directory_load,directory_save,chl,frames,z_planes,loops,total,pat,title,slider_subd1,slider_subd2):
	
	def pattern_closer(pat):
		impopen = [WM.getImage(id) for id in WM.getIDList()]  
		for wind in impopen:  
				imp2close=wind
				if ""+ pat +"" in str(wind):
					imp2close.close()			

	def hyperSC(num,istr):
			imp2=impl[num]
			imp2 = HyperStackConverter.toHyperStack(imp2, chl, 1, z_planes,"xytcz", "Color");
			if (num-2) < 10:
				numstr= "000" + str(num-2)
			elif (num-2) < 100 :
				numstr= "00" + str(num-2)
			elif (num-2) > 99:
				numstr= "0" + str(num-2)
			IJ.saveAs(imp2, "Tiff",""+ directory_save + title +"_R" + istr +"_Z"+ numstr +".tif")
	
	IJ.run("Close All", "")
	#Calculated variables
	range_rep=total/loops
	rangeDef=loops + 1
	
	IJ1.batchMode = True 
	imp=IJ.run("Bio-Formats", "open="+ directory_load +" color_mode=Default rois_import=[ROI manager] view=[Standard ImageJ] stack_order=Default use_virtual_stack series_2")

	loopDup= range(slider_subd1,slider_subd2 + 1)
	
	for i in loopDup:
		start=str(1+i*range_rep)
		end=str(range_rep + i*range_rep)
		
		if i < 10:
			istr= "000" + str(i)
		elif i < 100 :
			istr= "00" + str(i)
		elif i > 99:
			istr= "0" + str(i)
		
		impDup=IJ.run(imp, "Duplicate...", "title="+ title +"_R"+ istr +" duplicate range="+ start +"-"+ end +"")
	
		IJ.run(impDup,"Stack Splitter", "number="+ str(z_planes) +"")
		
	
		impl = [WM.getImage(id) for id in WM.getIDList()]  
		
			
		a=[hyperSC(num,istr) for num in range(2,z_planes+2)]
		pattern_closer(pat)	
	IJ1.batchMode = False 


def MakeSubset(directory_load,directory_save,chl,frames,z_planes,loops,total,pat,title,imp2):
	subd = NonBlockingGenericDialog("Make subset")  
	subd.addCheckbox("Duplicate only the current frames", False)  
	subd.addCheckbox("Export XYTC of a subset of loops", False)  
	
	subd.addSlider("Subset from loop number", 0, loops-1, 0)
	subd.addSlider("Subset to loop number", 0, loops-1, 0)
	subd.showDialog() 
	
	slider_subd1 = subd.getSliders().get(0).getValue()
	slider_subd2 = subd.getSliders().get(1).getValue()
	checkbox_subd1 = subd.getNextBoolean()
	checkbox_subd2 = subd.getNextBoolean()
	
	
	
	if checkbox_subd1==True:
		SliceNum=imp2.getCurrentSlice()
		FloorSlice50=float(SliceNum)/frames
		S50=(math.floor(FloorSlice50)*frames)+1
		S100=S50+(frames-1)
		print("Slice"+ str(SliceNum) +"_FloorSlice_"+ str(FloorSlice50) +"_frames_"+ str(S50) +"-"+ str(S100) +"")
		IJ.run("Duplicate...","title=Image_DUP duplicate range="+ str(S50) +"-"+ str(S100) +"") 
		impDup=WM.getImage("Image_DUP")
	if checkbox_subd2==True:
		SubsetL(directory_load,directory_save,chl,frames,z_planes,loops,total,pat,title,slider_subd1,slider_subd2)