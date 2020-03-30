# mTowerCED

Firstly, you will need to initialise ILCSoft. You can do this either by using the provided initialisation script:
    bash$ source initilcsoft.sh
or by finding the build of ILCSoft you want in cvmfs:
    bash$ source /cvmfs/clicdp.cern.ch/path/to/ilcsoft/initilcsoft.sh
  
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
