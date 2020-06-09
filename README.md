# mTowerCED

# Quick Example

Firstly, you will need to initialise ILCSoft. You can do this either by using the provided initialisation script:

    bash$ source initilcsoft.sh
    
or by finding the build of ILCSoft you want in cvmfs:

    bash$ source /cvmfs/clicdp.cern.ch/iLCSoft/builds/2020-02-07/x86_64-slc6-gcc7-opt/init_ilcsoft.sh
    
    
If you already have a converted file of CalorimeterHits (such as calohits.slcio herein) then you may start up CED Viewer immediately, using the ced2go function:

    bash$ ced2go -d mTower_geo/mTower_HEAD_multilayer_no_W.xml calohits.slcio
    
Where -d [xml] gives the path to the detector geometry impementation - in this case, the 24-layer mTower with no implemented Tungsten.

# Custom Event Selection

By default, ced2go does not run the processor 'MyEventSelector' which is used to define a specific event selection. A modified template steering file, ced2go-template-DD4.xml, includes MyEventSelector as part of the executed processors, so you can now define a custom selection. There are two runtime options you will need to add to your execution of ced2go:

-t ./ced2go-template-DD4.xml               This line calls the template file, allowing you to access the MyEventSelector Processor.
--MyEventSelector.EventList==<selection>   This line lets you alter the selection of events you want to view. These must be a list with the format "EventNumber RunNumber EventNumber RunNumber..."

So in order to view only events 3, 6 and 7 from calohits.slcio (which is from Run 1252):

    bash$ ced2go -d mTower_geo/mTwoer_HEAD_multilayer_no_W.xml -t ./ced2go-tmeplate-DD4.xml --MyEventSelector.EventList=='3 1252 6 1252 7 1252'


# Converting from ROOT to LCIO format:

Copy the root file with the data you want to visualise in it.

    bash$ cp /path/to/root/file/input.root ./
 
There are two classes of hit we use in the visualisation:
RawCalorimeterHits contains only a 32-bit ID string to store the Lane, Column and Row as encoded bits, with no information about the cell positions. These hits cannot be visualised
CalorimeterHits stores the 32-bit ID string, but also stores the x, y and z coordinates of each hit - this is the class we need for the visualisation. Currently, the naming convention for these hits is "ECALBarrelHits", in keeping with ILCSoft syntax.
These hits are stored in LCIO files (with the .slcio extension)

We have to convert to CalorimeterHits in order to use the visualisation software. We have two routes available to us:

1) The comprehensive route is to convert to RawCalorimeterHits, store these hits in one LCIO file, then convert to CalorimeterHits from there, so that we don't have to do the conversion again if the geometry structure changes for whatever reason. This is done as follows:

  a) Convert from ROOT to RawCalorimeterHits:
  
    bash$ python MakeRawCaloHits.py input.root rawhits.slcio
    
  b) Convert from RawCalorimeterHits to CalorimeterHits:
  
    bash$ python MakeCaloHitsFromRaw.py rawhits.slcio calohits.slcio

2) The quick route, for if you want to minimise the time needed to do the conversion, is to simply convert straight from ROOT format to CalorimeterHits:

  a) Convert from ROOT to CalorimeterHits:
  
    bash$ python MakeCaloHitsFromROOT.py input.root calohits.slcio
    
WARNING: WHICHEVER OF THE ABOVE ROUTES YOU USE, EXPECT THE CONVERSION TO TAKE SEVERAL HOURS!

Lastly, now that we have the data stored in CalorimeterHit format, we can visualise the hits using CED Viewer. We are required to give the geometry we want to use to the viewer, which will parse a DD4hep xml description of the geometry we want. The top-level geometry file (./mTower_geo/mTower_HEAD.xml) calls the other xml files into the description automatically. So all we need to do is:

    bash$ ced2go -d ./mTower_geo/mTower_HEAD.xml calohits.slcio

This should pop up the CED Viewer, showing us the first event in the slcio file (This isn't random, it starts at EventNumber=0). You can rotate and zoom in and out using a mouse or touchpad, and you can go on to the next event by pressing enter in your terminal window. To quit, type q in the terminal window, followed by enter.

WARNING: CEDVIEWER TENDS TO DEFAULT TO A ZOOMED-OUT PICTURE! YOU MAY NEED TO ZOOM IN TO SEE THE DETECTOR AND HITS IN DETAIL!
