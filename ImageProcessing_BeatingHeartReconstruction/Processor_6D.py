"""6D_processor
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



from ij import IJ, ImagePlus
from ij.gui import GenericDialog, NonBlockingGenericDialog 
from ij import WindowManager as WM  
from java.awt.event import AdjustmentListener 
from ij.plugin import ImageInfo
from ij.io import OpenDialog, DirectoryChooser 
from ij.text import TextPanel as TP
#required module 6D_converter
from Converter_6D import XYTCZL, MakeSubset
import math
import re

# Control Channel dimension
	  
class ControllerC(AdjustmentListener):  
	def __init__(self,imp, slider1):  	 
		self.imp = imp  
		self.slider = slider1 
		
	def adjustmentValueChanged(self,event):  
		if event.getValueIsAdjusting():  
			return 
			slider4_feedback = gd.getSliders().get(3).getValue()
			slider3_feedback = gd.getSliders().get(2).getValue()
			slider2_feedback = gd.getSliders().get(1).getValue()
			imp=IJ.getImage()
			chd= slider2_feedback*frames + slider3_feedback + slider4_feedback*z_planes*frames*ch
			imp.setPosition(1,chd,1)


# Control Z-dimension
class ControllerZ(AdjustmentListener):  
	def __init__(self,imp, slider2):  	 
		self.imp = imp  
		self.slider = slider2 
	
	def adjustmentValueChanged(self,event):  
		if event.getValueIsAdjusting():  
			return # there are more scrollbar adjustment events queued already  
		slider4_feedback = gd.getSliders().get(3).getValue()
		slider3_feedback = gd.getSliders().get(2).getValue()
		slider1_feedback = gd.getSliders().get(0).getValue()
		imp=WM.getImage("green_" + title)
		imp2=WM.getImage("red_" + title)
		evt=event.getValue()
		if slider1_feedback==1:
			imp.show()
			sp=slider3_feedback + 1 + evt *(ch*frames) + slider4_feedback*(zplanes*ch* frames)
			imp.setPosition(1,sp,1)
		else:
			sp=frames+ slider3_feedback + 1 + evt *(ch*frames) + slider4_feedback*(zplanes*ch* frames)
			imp2.setPosition(1,sp,1)
		
# Control T-dimension which are the frames in the loop	
			
class ControllerT(AdjustmentListener):  
	def __init__(self,imp, slider3):  	 
		self.imp = imp  
		self.slider = slider3 
	
	
	def adjustmentValueChanged(self,event):  
		if event.getValueIsAdjusting():  
			return # there are more scrollbar adjustment events queued already  
		slider1_feedback = gd.getSliders().get(0).getValue()
		slider2_feedback = gd.getSliders().get(1).getValue()
		slider4_feedback = gd.getSliders().get(3).getValue()
		imp=WM.getImage("green_" + title)
		imp2=WM.getImage("red_" + title)
		evt=event.getValue()
		if slider1_feedback==1:
			eventOutT= 1 + slider2_feedback *(ch*frames) + slider4_feedback*(zplanes*ch* frames)+evt
			imp.setPosition(1,eventOutT,1)	
			
		else:
			eventOutT=frames + 1 + slider2_feedback *(ch*frames) + slider4_feedback*(zplanes*ch* frames)+evt
			imp2.setPosition(1,eventOutT,1)	
		
	
# Control loop-dimension which are the loops every N min
class ControllerL(AdjustmentListener):  
	def __init__(self,imp, slider4):  	 
		self.imp = imp  
		self.slider = slider4
	
	def adjustmentValueChanged(self,event):  
		
		if event.getValueIsAdjusting():  
			return # there are more scrollbar adjustment events queued already  
		slider1_feedback = gd.getSliders().get(0).getValue()
		slider2_feedback = gd.getSliders().get(1).getValue()
		slider3_feedback = gd.getSliders().get(2).getValue()
		imp=WM.getImage("green_" + title)
		imp2=WM.getImage("red_" + title)
		evt=event.getValue()
		
		if slider1_feedback==1:
			eventOutL= slider3_feedback + 1 + slider2_feedback *(ch*frames) + evt*(zplanes*ch* frames)
			imp.setPosition(1,eventOutL,1)	
		else:
			eventOutL=frames + slider3_feedback+ 1 + slider2_feedback *(ch*frames) + evt*(zplanes*ch* frames)
			imp2.setPosition(1,eventOutL,1)	
				
# Define the pre-conditions for loading the data, default values represent my normal acquisition parameters only the loop has to be set, the rest is read from metadata

psgd = GenericDialog("Pre-Set")  
psgd.addCheckbox("Images open?", False) # if your images  are already open as a virtual stack, you can avoid to load again
psgd.showDialog() 

if psgd.wasOKed(): 
	choiceIm=psgd.getCheckboxes().get(0).getState()	
	
	# load data as virtual stack, simple image stack
	if choiceIm==False: 
		IJ.run("Close All", "")
		impDir = OpenDialog("Select the 6D dataset").getPath()
		impDir =impDir.replace("\\","/") 
	
		IJ.run("Bio-Formats", "open="+ impDir +" color_mode=Default display_metadata rois_import=[ROI manager] view=[Standard ImageJ] stack_order=Default use_virtual_stack")
		
		#define ImagePlus to variable and remove path from title
		imp = WM.getCurrentImage()  
		directoryTitle = IJ.getDirectory("current")
		directoryTitle =directoryTitle.replace("\\","/") 
		title=imp.getTitle()
		title=re.sub(directoryTitle, "", title)
		
		#read loops from metadata, don't close textwindow
		nonImaWindow=WM.getNonImageTitles()
		metaName= "Original Metadata - " + title +""
		if metaName in  nonImaWindow:
			metadata=WM.getWindow(metaName)
		elif nonImaWindow[0]==u'Recorder':
			metadata=WM.getWindow(nonImaWindow[1])
		else:
			metadata=WM.getWindow(nonImaWindow[0])
		meta=metadata.getTextPanel()
		searchText="Image|DimensionDescription|NumberOfElements\t"
		loops=int(meta.getText().split(searchText)[1].split("\n")[0])
		imp.setTitle("green_" + title)
		
		#check whether there are two channels
		ChCheck = imp.getNChannels() 
		if ChCheck > 1:
			IJ.run("Bio-Formats", "open="+ impDir +" color_mode=Default rois_import=[ROI manager] view=[Standard ImageJ] stack_order=Default use_virtual_stack")
			imp2 = WM.getCurrentImage() 
			imp2.setTitle("red_" + title)
		
		
	# Avoid loading data, as already open and just assign variables
	elif choiceIm==True: 	
		
		retitle=WM.getImageTitles()
		for j in retitle:
			if "green_" in j:
				greentitle=j
			if "red_" in j:
				redtitle=j
		title=re.sub("green_", "", greentitle)
		imp=WM.getImage(greentitle)
		# check whether two channels are present
		ChCheck = imp.getNChannels() 
		if ChCheck > 1:
			imp2=WM.getImage(redtitle)
		#load loops from metadata-textwindow
		nonImaWindow=WM.getNonImageTitles()
		metaName= "Original Metadata - " + title +""
		
		if metaName in  nonImaWindow:
			metadata=WM.getWindow(metaName)
		if nonImaWindow[0]==u'Recorder':
			metadata=WM.getWindow(nonImaWindow[1])
		else:
			metadata=WM.getWindow(nonImaWindow[0])
		meta=metadata.getTextPanel()
		searchText="Image|DimensionDescription|NumberOfElements\t"
		loops=int(meta.getText().split(searchText)[1].split("\n")[0])
		
	# Get all the metadata, required
	infoFrames=imp.getNFrames() 
	infoZ=imp.getNSlices()
	ch=imp.getNChannels() 
	frames=int(infoFrames)/ int(loops)
	zplanes=infoZ
	total=ch*zplanes*frames*loops
	
	
	# properties need to be set to get a continous stack without dimensions
	IJ.run(imp, "Properties...", "channels=1 slices="+ str(total) +" frames=1 unit=micron pixel_width=2.3140 pixel_height=2.3140 voxel_depth=2.5005 frame=[0.02 sec]")
	if ChCheck > 1:
		IJ.run(imp2, "Properties...", "channels=1 slices="+ str(total) +" frames=1 unit=micron pixel_width=2.3140 pixel_height=2.3140 voxel_depth=2.5005 frame=[0.02 sec]")
	
	# The dialag has to be non-blocking to interact with the data, this dialog will access the controller classes and handle your images
	# The dialag needs to be out of a function to get global variables
	gd = NonBlockingGenericDialog("6D_processor")  
	gd.addSlider("C", 1, ch, 1)  
	gd.addSlider("Z", 0, zplanes-1, 0)
	gd.addSlider("T", 0, frames-1, 0)
	gd.addSlider("L", 0, loops-1, 0)
	# Make checkboxes for output functions
	gd.addCheckbox("Make subset", False)  
	gd.addCheckbox("Split into XYTC", False)  
	gd.addCheckbox("Arg. csv BeatSync", False)  	
	# The UI elements for the above two inputs  
	slider1 = gd.getSliders().get(0) # the only one  
	slider2 = gd.getSliders().get(1)
	slider3 = gd.getSliders().get(2)
	slider4 = gd.getSliders().get(3)
	
	
	# Set initial position for the two channels
	if ChCheck > 1:
		imp2.setPosition(1,51,1)
	 
	
	#Access controller classes
	previewer1 = ControllerC(imp,slider1)
	previewer2 = ControllerZ(imp,slider2)  
	previewer3 = ControllerT(imp,slider3)  
	previewer4 = ControllerL(imp,slider4)    
	
	#Get adjustment listeners for scrollbars
	slider1.addAdjustmentListener(previewer1)
	slider2.addAdjustmentListener(previewer2)  
	slider3.addAdjustmentListener(previewer3)
	slider4.addAdjustmentListener(previewer4)
	
	#Finally show the non-blocking dialog	
	gd.showDialog()  
	
	#get status of checkboxes
	checkbox1 = gd.getNextBoolean()
	checkbox2 = gd.getNextBoolean()
	checkbox3 = gd.getNextBoolean()
	
	#Reset the properties to re-open the data with the viewer, an error will appear as the metadata are not read correctly
	if gd.wasCanceled(): 
		IJ.run(imp, "Properties...", "channels="+ str(ch) +" slices="+ str(zplanes) +" frames="+ str(frames*loops) +" unit=micron pixel_width=2.3140 pixel_height=2.3140 voxel_depth=2.5005 frame=[0.02 sec]")
		IJ.run(imp2, "Properties...", "channels="+ str(ch) +" slices="+ str(zplanes) +" frames="+ str(frames*loops) +" unit=micron pixel_width=2.3140 pixel_height=2.3140 voxel_depth=2.5005 frame=[0.02 sec]")
		imp.setTitle("green_" + title)
		imp2.setTitle("red_" + title)
	
	#If okay was clicked in the 6D_processor dialog the checkboxes are read and an output is created  	
	if gd.wasOKed():
		if checkbox1 == True or checkbox3 == True or checkbox2==True:  
			#Output option 1 is making a subset of loops, that are then exported as XYTC.tiff
			if checkbox1 == True:
				if choiceIm==True: 
					greenwindow=WM.getWindow("green_" + title)
					WM.setCurrentWindow(greenwindow)
					impDir = IJ.getDirectory("current")
					impDir = impDir.replace("\\","/") 
					impDir = impDir + title
				pat=title
				directory_save_subset = DirectoryChooser("Select the directory to save the files").getDirectory() 
				directory_save_subset = directory_save_subset.replace("\\","/") 
				MakeSubset(impDir,directory_save_subset,ch,frames,zplanes,loops,total,pat,title,imp2)
			#Output option 2 is exporting all the dataset to XYTC.tiff
			if checkbox2 == True or checkbox3 == True:
				directory_save_xytc = DirectoryChooser("Select the directory to save the files").getDirectory() 
				directory_save_xytc =directory_save_xytc.replace("\\","/") 
				pat=title
				XYTCZL(impDir,directory_save_xytc,ch,frames,zplanes,loops,total,pat,title)
			#Output option 3 is additionally creating a csv-file with information for matlab BeatSync 
			if checkbox3 == True:
				directory_save = DirectoryChooser("Select the directory to save the files").getDirectory() 
							
				f = open(""+directory_save + title +"Matlab_export.csv", "a")
				f.write("Path,L,Zi,T,C\n"+ directory_save_xytc +","+ str(loops) +"," + str(slider2.getValue()) +","+ str(frames) +","+ str(ch)  + "\n")
				f.close()
		# reset the image properties, to restart the 6D_processor without reopening the files
		else: 
			imp.setTitle("green_" + title)
			imp2.setTitle("red_" + title)
			IJ.run(imp, "Properties...", "channels="+ str(ch) +" slices="+ str(zplanes) +" frames="+ str(frames*loops) +" unit=micron pixel_width=2.3140 pixel_height=2.3140 voxel_depth=2.5005 frame=[0.02 sec]")
		
		if ChCheck > 1:
			IJ.run(imp2, "Properties...", "channels="+ str(ch) +" slices="+ str(zplanes) +" frames="+ str(frames*loops) +" unit=micron pixel_width=2.3140 pixel_height=2.3140 voxel_depth=2.5005 frame=[0.02 sec]")
	