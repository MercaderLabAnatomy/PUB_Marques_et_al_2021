"""Make_timelapse.py
This tool was made in context of 6D-imaging of the beating heart and is made to assemble a time lapse from individual movies of a beating heart at different time points to follow the development of the zebrafish heart. 
Either you select the same frame for each time point or you provide a table, which allows to choose a different frame for each time point. 

The table can be created in excel with one column "Frame selected" which sequentially lists the desired frame per loop, it should be saved as tab-separated .txt-file.

Testdata can be provided on request, as the files are between 500 - 1500 gb big. 

Alexander Ernst
Institute of anatomy, University of Bern
Programmed in Jython, tested on FIJI: IJ.getVersion: 2.0.0-rc-69/1.52p   and java.version: 1.8.0_172

"""

from ij import IJ, ImagePlus, ImageStack, CompositeImage    
from ij.plugin import HyperStackConverter
import ij.plugin
from ij import WindowManager as WM
import os  
from os import path 
import re
from re import sub
from ij.plugin import Concatenator
from ij.io import OpenDialog, DirectoryChooser 
from ij.gui import GenericDialog,NonBlockingGenericDialog 
from ij.text import TextPanel as TP
from ij.measure import ResultsTable as RT
# Create a non-blocking dialog to enter the metadata 
psgd = NonBlockingGenericDialog("Choose the frame that shows the right conformation of the heart?")  
psgd.addNumericField("Which frame to choose?", 1, 0)
psgd.addCheckbox("Use table of selected frames?", False) 
psgd.showDialog() 
choose = psgd.getNextNumber()
choice=psgd.getCheckboxes().get(0).getState()  

#open a tab separated txt file with one column Frame selected
if choice==1:
	choose=0
	IJ.run("Table... ", "open=")
	frametable=WM.getWindow("selected_frames.txt")
	meta=frametable.getTextPanel()
	metaRT=TP.getResultsTable(meta)

# Choose a directory
directory_load= DirectoryChooser("Select the directory of your files").getDirectory() 
directory_load= directory_load.replace("\\","/") 

# get a list of all files in the directory
dList=os.listdir(directory_load)
# set a counter to 1
n=1

for i in dList:
	dL= directory_load + "/" + str(i)
	
	#consider only files with .ome file ending
	if ".ome" in dL:
		#open the images as virtual stack 
		imp=IJ.run("Bio-Formats", "open=["+dL+"] color_mode=Default rois_import=[ROI manager] view=Hyperstack stack_order=XYCZT use_virtual_stack")
		imp=IJ.getImage()
		#get right name for duplication of the desired frame
		if n < 10:
				numstr= "000" + str(n)
		elif n < 100 :
				numstr= "00" + str(n)
		elif n > 99:
				numstr= "0" + str(n)
		if choice==1:
			choose=RT.getValue(metaRT,"Frame selected",n-1)
		#duplicate the right frame and give it the right title
		impDup=IJ.run("Duplicate...", "title=Image_R"+ str(numstr) +" duplicate frames="+ str(choose) +"")
		imp.close()
		# add 1 to the counter
		n=n+1

#get list imageplus objects of all open images
impl = [WM.getImage(id) for id in WM.getIDList()] 	
end=len(impl)

imp2=impl[0]
ti=0
#concatenate all the frames to a time lapse
for t in impl:
	if ti > 0:
		imp2 = Concatenator.run(imp2, t)
	print t
	ti=ti+1
imp2.show()
