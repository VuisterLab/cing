from cing.Libs.NTutils import ExecuteProgram
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTerror
from cing.core.parameters import cingPaths
import os

def convertImageMagick(inputPath,outputPath,options,extraOptions=None):
    convert = ExecuteProgram(cingPaths.convert, redirectOutput=False) # No output expected
    cmd = options
    if extraOptions:
        cmd += " " + extraOptions
    cmd += " " + inputPath + " " + outputPath
    if convert( cmd ):
        NTerror("Failed to run convertImageMagick: " + cmd)
        return True

def convertGhostScript(inputPath,options,extraOptions=None):
    # GS has rather verbose output
    # just to make sure we report back on on error let's have caller check results. 
    gs = ExecuteProgram(cingPaths.ghostscript, redirectOutputToFile='/dev/null') 
    cmd = options
    if extraOptions:
        cmd += " " + extraOptions
    cmd += " " + inputPath
    if gs( cmd ):
        NTerror("Failed to run convertGhostScript: " + cmd)
        return True

def convertPs2Pdf(inputPath,outputPath,options,extraOptions=None):
    convert = ExecuteProgram(cingPaths.ps2pdf, redirectOutput=False) # No output expected
    cmd = options
    if extraOptions:
        cmd += " " + extraOptions
    cmd += " " + inputPath + " " + outputPath
    if convert( cmd ):
        NTerror("Failed to run conversion: " + cmd)
        return True
        
def joinPdfPagesByConvert( inputFileList, outputPath):
    """Rasterizes which reduces the quality in general"""
    # convert -adjoin -delay 200 residuePlotSet001.png residuePlotSet002.png residuePlotSetAll.gif    
    options = '-adjoin -delay 200'
    if convertImageMagick(' '.join(inputFileList), outputPath, options):
        NTerror("Failed to joinPdfPagesByConvert to output: " + outputPath)
        return True
    
def joinPdfPagesByGhostScript( inputFileList, outputPath):
    # gs -dNOPAUSE -sDEVICE=pdfwrite -sOUTPUTFILE=Merged.pdf -dBATCH residuePlotSet000.pdf residuePlotSet001.pdf
    options = '-dNOPAUSE -sDEVICE=pdfwrite -sOUTPUTFILE=%s -dBATCH ' % \
        outputPath
    if convertGhostScript(' '.join(inputFileList), options):
        NTerror("Failed to joinPdfPagesByGhostScript to output: " + outputPath)
        return True
    if not os.path.isfile(outputPath):
        # just to make sure we report back on on error let's have caller check results. 
        NTerror("Failed joinPdfPagesByGhostScript because no output: " + outputPath)
        return True
# Perhaps configurable to convert
#joinPdfPages = joinPdfPagesByConvert
joinPdfPages = joinPdfPagesByGhostScript
    
def convert2Web(path, outputDir=None):
    """Using the system convert from ImageMagick several pieces of imagery will be created:
        a- pinup (smallish gif usable as an preview; 100 width by 1xx for A4 aspect ratio)
        b- full size 1(gif of 1000 width )
        c- printable version (pdf)

       The output file names are automatically generated. If the outputDir is set it will be
       used.
       Returns None for error and list of output files otherwise. A None in the list means\
       the plot was not generated.
       Gif files are multipaged with 2 second intervals.
       Input can be anything ImageMagick reads, e.g. Postscript produced by Procheck_NMR.
       The input path can be with or without directory and can be
       an absolute or relative path.
    """
    optionsPinUp = "-delay 200 -geometry 102" # geometry's first argument is width
    optionsFull  = "-delay 200 -geometry 1024"
    optionsPrint = ""

    doPinUp = True
    doFull  = True
    doPrint = True

    if not os.path.exists(path):
        NTerror("Failed to find input")
        return True
    # Next time use: NTpath for this.
#    path = "/Users/jd/t.pdf"
    head, tail = os.path.split(path)             # split is on last /
    root, extension = os.path.splitext(tail)     # splitext is on last .

    if outputDir:
        if os.path.exists(outputDir) and os.path.isdir(outputDir):
            head = outputDir
        else:
            NTerror("Given output directory: " + outputDir + " is absent or is not a dir")
            return None

    if extension == "pdf":
        NTdebug("Will skip generating printable version as input is also a pdf")
        doPrint = False

    if extension == "gif":
        NTdebug("Will skip generating full size gif version as input is also a gif")
        doFull = False

    pinupPath = None
    fullPath  = None
    printPath = None
    # Algorithm below can be speeded up by not rereading the input but scripting the
    #     generation of 3 outputs.
    if doPinUp:
        pinupPath = os.path.join( head, root+"_pin.gif")
        if convertImageMagick(path, pinupPath, optionsPinUp):
            NTerror("Failed to generated pinup")
            pinupPath = None
    if doFull:
        fullPath  = os.path.join( head, root+".gif")
        if convertImageMagick(path, fullPath, optionsFull):
            NTerror("Failed to generated full gif")
            fullPath = None
    if doPrint:
        printPath = os.path.join( head, root+".pdf")
        if convertPs2Pdf( path, printPath, optionsPrint):
            NTerror("Failed to generated print")
            printPath = None
    result = ( pinupPath, fullPath, printPath )
    if  pinupPath or fullPath or printPath:
        return result
    return None
