from ROOT import TCanvas, TPad, TFile, TPaveLabel, TPaveText
from ROOT import TTree, TBranch, TLeaf, TH1, TH2, TF1, TH1F, TH2F, TGraph, TGraphErrors
from pyLCIO import EVENT, IMPL, IOIMPL, UTIL
import numpy as np
import sys, os

# MakeRawCaloHits.py
# Takes a root file hits and converts them to RawCalorimeterHits, then output to an LCIO file.
# Warning - this process can take several hours!


#this function is the main workhorse...
def getinfo(inputfilename, outputfilename) :
    #Set up the LCIO output file
    writer = IOIMPL.LCFactory.getInstance().createLCWriter()
    writer.open( outputfilename, EVENT.LCIO.WRITE_NEW )

    #Get the file and the tree in the file:
    file = TFile(inputfilename, "read")
    tree = file.Get("Frames")

    #iterator for progress bar...
    q = int(0)

    #loop over all entries in the tree...
    for i in range (0, tree.GetEntries()) :
        tree.GetEntry(i)
        Lane = tree.lane           #vector
        Row =  tree.row            #vector
        Column = tree.column       #vector
        Event =  tree.eventNumber
        File =  tree.fileNumber
        Run =  tree.runNumber

        # ++ Lane, Row and Column should be the same length. Let's just check that they are:
        if (len(Lane) != len(Row)) or (len(Lane) != len(Column)) :
            print "ERROR +++++++++++++++++++++++++++++++++++++          Row vector length", len(Row), ", Column vector length", len(Column), "and Lane vector length", len(Lane), "aren't equal!"
        
        
        # ++ create an event
        LCEvent = IMPL.LCEventImpl()
        LCEvent.setEventNumber( Event )
        LCEvent.setRunNumber( Run )

        # ++ create a raw calorimeter hit collection
        RawCaloHits = IMPL.LCCollectionVec( EVENT.LCIO.RAWCALORIMETERHIT )

        # ++ create an IDEncoder to store hit IDs
        # ++ defines the tags and the number of bits for the different bit fields
        encodingString = str("lane:7,row:11,column:11")    
        idEncoder = UTIL.CellIDEncoder( IMPL.RawCalorimeterHitImpl )( encodingString, RawCaloHits )

        
        for j in range (0, len(Lane)):
            # ++ build the raw calorimeter hit
            Hit = IMPL.RawCalorimeterHitImpl()

            # ++ set the cell ID
            idEncoder.reset()
            idEncoder['lane'] = Lane[j]
            idEncoder['row'] = Row[j]
            idEncoder['column'] = Column[j]          
            idEncoder.setCellID( Hit )

            # ++ add the hit to the collection
            RawCaloHits.addElement( Hit )

            # ++ end of hit loop
            

        # ++ add the collection to the event
        LCEvent.addCollection( RawCaloHits, 'RawCalorimeterHits' )

        # ++ write the event to the output file
        writer.writeEvent( LCEvent )      

        # ++ print percentage of progress (but not too often!)
        p = int((float(i)/float(tree.GetEntries()))*100)
        progress = str(p)+'%'
        if (p != q) :
            print "Progress:", progress
            q = int(p)

        # ++ end of event loop

    # ++ close the writer        
    writer.flush()
    writer.close()

#end of function
    
#check that you have the right number of arguments
if (len(sys.argv) != 3):
    print "Script has the format 'python MakeRawCaloHits.py >inputfile.root< >outputfile.slcio<'"
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
            
#run the conversion to RawCalorimeterHits
getinfo(str(sys.argv[1]), str(sys.argv[2]))

print "Done!"
    
print "Press ENTER to exit"
input()
