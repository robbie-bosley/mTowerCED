from ROOT import TCanvas, TPad, TFile, TPaveLabel, TPaveText
from ROOT import TTree, TBranch, TLeaf, TH1, TH2, TF1, TH1F, TH2F, TGraph, TGraphErrors, TVector3
from pyLCIO import EVENT, IMPL, IOIMPL, UTIL
import pyLCIO
from pyLCIO.io.LcioReader import LcioReader
import numpy as np
import sys

# MakeCaloHitsFromRaw.py
# Takes an LCIO file of RawCalorimeterHits and converts them to CalorimeterHits, then output to a separate LCIO file.
# Warning - this process can take several hours!


#Initialise the layer and lane look up tables (lut) from scratch, based on myEventDisplay.cxx, using the chipID to find the corresponding layer/lane
layer_lut = [22, 22, 20, 20, 18, 18, 16, 16, 14, 14, 12, 12, 10, 10, 8, 8, 6, 6, 4, 4, 0, 0, 2, 2, 23, 23, 21, 21, 19, 19, 17, 17, 15, 15, 13, 13, 11, 11, 9, 9, 7, 7, 5, 5, 1, 1, 3, 3]
lane_lut = [40, 39, 42, 41, 44, 43, 46, 45, 48, 47, 50, 49, 52, 51, 54, 53, 38, 55, 36, 37, 32, 35, 34, 33, 64, 63, 66, 65, 68, 67, 70, 69, 72, 71, 74, 73, 76, 75, 78, 77, 62, 79, 60, 61, 56, 59, 58, 57]

#Use lane_lut to initialise a lut to find the chipID when given the lane
inverse_lane_lut = [0]*80
for i in range(0, len(lane_lut)):
    inverse_lane_lut[lane_lut[i]] = i

#Create table used for determining whether or not the chip is inverted or not
IsInv = 24*[0] + 24*[1]

#Create a table determining whether or not the chip is on the left side of the stack (when seen from the front)
IsLeft = []
for i in range (0, len(IsInv)) :
    l = abs(IsInv[i]-i%2)
    IsLeft.append(l)
    
#POSSIBLY DELETE THIS
PadID = []
for i in range (0, len(IsLeft)) :
    l = (2*layer_lut[i])+IsLeft[i]
    PadID.append(l)

#Create look up tables for whether or not x and y in the chip need to be inverted
XInv = IsLeft
YInv = []
for i in range (0, len(IsLeft)) :
    l = abs(IsLeft[i]-1)
    YInv.append(l)


bump = 0.014 #mm      #Addition of half the pixel size in order to start in the middle of the first pixel.
pixelsize = 0.028 #mm

#column goes from 0 to 1023
#row goes from 0 to 511

Row2X_lut_left = []
Row2X_lut_right = []
Column2Y_lut_left = []
Column2Y_lut_right = []

#Column is on X axis, Row is on Y axis.
#So that's:
#|Row
#|
#|
#|
#|
#|
#|
#|
#|
#^---------------------> Column

#Get full width and height of the stack:
xw = 512*pixelsize
yw = 1024*pixelsize


#Create look up tables for x, both for chips on the left and right
for i in range (512) :
    x = (i*pixelsize)+bump
    Row2X_lut_left.append(x - xw)
    Row2X_lut_right.append(xw - x)

#Create look up tables for y, both
for i in range (1024) :
    y = (i*pixelsize)+bump
    Column2Y_lut_left.append((yw/2) - y)
    Column2Y_lut_right.append(y - (yw/2))

#Initialise z look up table using layer and 
W_thickness = 3.5 #mm
Z_lut = []
zw = W_thickness*24
for i in range (len(layer_lut)) :
    z = (layer_lut[i])*W_thickness
    Z_lut.append(z - (zw/2))

#Function to do conversion to calorimeter hits based on look up tables created above
def convert_to_calorimeterevent( inputFileName, outputFileName, Row2X_lut_left, Row2X_lut_right, Column2Y_lut_left, Column2Y_lut_right, Z_lut, lane_lut, IsLeft) :
    #check flag setting, as position won't be written if LCIO::CHBIT_LONG not set...
    flag = IMPL.LCFlagImpl()
    flag.setBit( EVENT.LCIO.CHBIT_LONG )

    #Create a reader to parse the input file
    reader = LcioReader( inputFileName )

    #create a writer to write to the output file
    writer = IOIMPL.LCFactory.getInstance().createLCWriter()
    writer.open( outputFileName, EVENT.LCIO.WRITE_NEW )

    #create indexes for progress tracking...
    index = 0.
    q = int(0)
    
    for oldEvent in reader:
        index += 1.

        #create a new event and copy its parameters
        newEvent = IMPL.LCEventImpl()
        newEvent.setEventNumber( oldEvent.getEventNumber() )
        newEvent.setRunNumber( oldEvent.getRunNumber() )
        
        #Create a new collection to add to the new events, now made from CalorimeterHits.
        CaloHits = IMPL.LCCollectionVec( EVENT.LCIO.CALORIMETERHIT )

        #add flag to CaloHits so we can store positions...
        CaloHits.setFlag(flag.getFlag())

        #Create both an encoder for the new events, and a decoder for the old ones...
        encodingString = str("lane:7,row:11,column:11")
        idEncoder = UTIL.CellIDEncoder( IMPL.CalorimeterHitImpl )( encodingString, CaloHits )
        idDecoder = UTIL.CellIDDecoder( IMPL.RawCalorimeterHitImpl )( encodingString )

        #get the raw calorimeter hits...
        RawCaloHits = oldEvent.getCollection('RawCalorimeterHits')

        #Loop over the RawCalorimeterHits
        for oldHit in RawCaloHits :
            #get the row, column and lane from the raw calorimter hits
            lane = idDecoder( oldHit )["lane"].value()
            row = idDecoder( oldHit )["row"].value()
            column = idDecoder( oldHit )["column"].value()

            #get the chipID from the lane...
            chipID = inverse_lane_lut[lane]

            #get x, y and z.
            if (IsLeft[chipID]) :
                x = Row2X_lut_left[row]
                y = Column2Y_lut_left[column]

            else :
                x = Row2X_lut_right[row]
                y = Column2Y_lut_right[column]
                
            z = Z_lut[chipID]


            #Make new calorimeter hit:
            newHit = IMPL.CalorimeterHitImpl()
            
            #add the lane, column, row to the new collection...
            idEncoder.reset()
            idEncoder['lane'] = lane
            idEncoder['row'] = row  
            idEncoder['column'] = column          
            idEncoder.setCellID( newHit )

            #add x, y, z to the new collection...
            Position = TVector3( x, y, z )
            newHit.setPositionVec( Position )

            #add hits to collection
            CaloHits.addElement( newHit )
            
            #end of hit loop

        #add collection to event
        newEvent.addCollection( CaloHits , 'ECalBarrelCollection' )

        #write the event to the output file
        writer.writeEvent( newEvent )

        #print percentage of progress (but not too often!)
        p = int((float(index)/float(reader.getNumberOfEvents()))*100)
        progress = str(p)+'%'
        if (p != q) :
            print "Progress:", progress
            q = int(p)

        #end of event loop

    #close the writer        
    writer.flush()
    writer.close()

#end of function


#check that you have the right number of arguments
if (len(sys.argv) != 3):
    print "Script has the format 'python MakeCaloHitsFromRaw.py >inputfile.slcio< >outputfile.slcio<'"
    sys.exit(0)

touchcommand = "touch " + str(sys.argv[2])
os.system(touchcommand)
    
#check that all the arguments exist as files
for arg in sys.argv[1:]:
    try :
        f = open(arg, 'r')
    except OSError:
        print "Can't open", arg
    else:
        print "found", arg
        f.close()

#start the conversion function
convert_to_calorimeterevent( sys.argv[1], sys.argv[2], Row2X_lut_left, Row2X_lut_right, Column2Y_lut_left, Column2Y_lut_right, Z_lut, lane_lut, IsLeft)
print "Done!"
