<!DOCTYPE html>
<html>
<head>
Image pre- and post- processing tools for timelapse creation of beating zebrafish heart 
<br>
<b>!! This repository does not contain BeatSync for 3D reconstruction of the heart, see material and methods of Marques, et al. 2021 !! <\b>
</head>
<body>

<h1> Processor_6D / Converter_6D </h1>
<p>

This Plugin for FIJI is made to facilitate browsing through <br> XYTCZL .lif datasets (T: frames C:Channels Z:slices, L: loops) datasets, using the virtual stack function. 
The ImageJ programming tutorial "https://www.ini.uzh.ch/~acardona/fiji-tutorial/" was taken as template to create an interactive controller for these 
complex datasets. The dialogs are non-blocking and with this the roi-manager can be used to perform some preliminary analysis.
</p>
<p> 
Principle:
The .lif-files are opened with the bioformats importer as normal virtualstack, not hyperstack. 
The properties are read from the metadata and subsequently Channels and Slices are set to 1, while all dimensions
are put into the slices (T=T*C*Z*loops). A dialog is opened and the controller window based on an AdjustmentListener, will enable you to browse through the datasets.  The windows are kept separate, as our microscope is recording the two channels individually and in this sense the channels are not aligned. 
</p>
<p> 
Application: 
The bioformats-importer does a great job with opening different datasets, but will not show more than 5 dimensions. 
This Plugin is made for the specific purpose of helping the users of the Leica DLS XYTZL mode to quickly browse their datasets.  
These files are usually large, for this reason the virtualstack function is used. Future versions will offer more processing functionalites.
</p>
<p> 
<h1> Make_timelapse </h1>

This tool was made in context of 6D-imaging of the beating heart and is made to assemble a time lapse from individual movies of a beating heart at different time points to follow the development of the zebrafish heart. Either you select the same frame for each time point or you provide a table, which allows to choose a different frame for each time point.

The table can be created in excel with one column "Frame selected" which sequentially lists the desired frame per loop, it should be saved as tab-separated .txt-file.

</p>
<p>
Testdata can be provided on request, as the files are between 500 - 1500 gb big. 
</p>

<h1> Installations </h1>
<h2> Processor_6D  </h2>
<p>
1. Simply copy Converter_6D and Processor_6D to your "FIJI/Plugins/" directory and restart FIJI. 
2. Start Processor_6D from inside FIJI in the Plugins tab.   
</p>
  
<h2> Make_timelapse </h2>
<p>
1. Simply copy Make_timelapse to your "FIJI/Plugins/" directory and restart FIJI. 
2. Start Make_timelapse from inside FIJI in the Plugins tab.   
</p>
<h2> Tested on Fiji:</h2>

<p> 
IJ.getVersion: 2.0.0-rc-69/1.52p   and java.version: 1.8.0_172
</p>
</body>
</html>
