from cing.Libs.NTutils import * #@UnusedWildImport
from cing.core.parameters import cingPaths

def convertImageMagick(inputPath,outputPath,options,extraOptions=None):
    if not cingPaths.convert:
        NTerror("No cingPaths.convert in convertImageMagick")
        return True
    if inputPath == None: # happened for entry 2k1n after convert failed.
        NTerror("In convertImageMagick: got None for inputPath")
        return True
    if outputPath == None:
        NTerror("In convertImageMagick: got None for outputPath")
        return True
    convert = ExecuteProgram(cingPaths.convert, redirectOutput=False) # No output expected
    cmd = options
    if extraOptions:
        cmd += " " + extraOptions
    cmd += " " + inputPath + " " + outputPath
    if convert( cmd ):
        NTerror("Failed to run convert from ImageMagick with command: " + cmd)
        return True

def montageImageMagick(inputPath,outputPath,options,extraOptions=None):
    if not cingPaths.montage:
        NTerror("No cingPaths.montage in montageImageMagick")
        return True
    if not cingPaths.montage:
        return True
    if inputPath == None:
        NTerror("In montageImageMagick: got None for inputPath")
        return True
    if outputPath == None:
        NTerror("In montageImageMagick: got None for outputPath")
        return True

    convert = ExecuteProgram(cingPaths.montage, redirectOutput=False) # No output expected
    cmd = options
    if extraOptions:
        cmd += " " + extraOptions
    cmd += " " + inputPath + " " + outputPath
    if convert( cmd ):
        NTerror("Failed to run montage from ImageMagick with command: " + cmd)
        return True


def convertGhostScript(inputPath,options,extraOptions=None):
    # GS has rather verbose output
    # just to make sure we report back on on error let's have caller check results.
    if not cingPaths.ghostscript:
        NTerror("No cingPaths.ghostscript in montageImageMagick")
        return True
    if inputPath == None:
        NTerror("In convertGhostScript: got None for inputPath")
        return True
    gs = ExecuteProgram(cingPaths.ghostscript, redirectOutputToFile='/dev/null')
    cmd = options
    if extraOptions:
        cmd += " " + extraOptions
    cmd += " " + inputPath
    if gs( cmd ):
        NTerror("Failed to run convertGhostScript: " + cmd)
        return True

def convertPs2Pdf(inputPath,outputPath,options,extraOptions=None):
    if not cingPaths.ps2pdf:
        NTerror("No cingPaths.ps2pdf in convertPs2Pdf")
        return True
    if inputPath == None: # happened for entry 2k1n after convert failed.
        NTerror("In convertPs2Pdf: got None for inputPath")
        return True
    if outputPath == None:
        NTerror("In convertPs2Pdf: got None for outputPath")
        return True

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

def convert2Web(path, outputDir=None, doFull=True, doPrint=True, doMontage=False):
    """Using the system convert from ImageMagick several pieces of imagery will be created:
        a- pinup (smallish gif usable as an preview; 100 width by 1xx for A4 aspect ratio)
        b- full size 1(gif of 1000 width or montaged png of 1000 width for each page)
        c- printable version (pdf)

       The output file names are automatically generated. If the outputDir is set it will be
       used. If not set, the same directory as the input will be used.

       Returns None for error and list of output files otherwise. A None in the list means\
       the plot was not generated.
       Gif files are multipaged with 2 second intervals.
       Input can be anything ImageMagick reads, e.g. Postscript produced by Procheck_NMR.

       The input path can be with or without directory and can be
       an absolute or relative path. It may also be a list of images.

       If the input is a list then the output file names will be tried to shorten by the
       "%03d" formatting assumed if possible.
       E.g. residuePlotSetAll001.gif as the first filename will give a:
            residuePlotSetAll.gif and residuePlotSetAll_pin.gif output.
    """
    if not cingPaths.montage:
        NTerror("No cingPaths.montage in convert2Web")
        return True
    if not cingPaths.convert:
        NTerror("No cingPaths.convert in convert2Web")
        return True
    if not cingPaths.ghostscript:
        NTerror("No cingPaths.ghostscript in convert2Web")
        return True


    optionsPinUp = "-delay 200 -geometry 102" # geometry's first argument is width
    optionsFull  = "-delay 200 -geometry 1024"
    optionsPrint = ""

    doPinUp = True

    if isinstance(path, list):
        if path == None or len(path) == 0:
            NTerror("Failed to find valid input path list")
            return True
        for p in path:
            if not os.path.exists(p):
                NTerror("Failed to find input path: " + p)
                return True
        pathStr = ' '.join(path)
        pathFirst = path[0]

    else:
        if not os.path.exists(path):
            NTerror("Failed to find input: " + path)
            return True
        pathStr = path
        pathFirst = pathStr

    # Next time use: NTpath for this.
#    path = "/Users/jd/t.pdf"
    head, tail = os.path.split(pathFirst)             # split is on last /
    root, extension = os.path.splitext(tail)     # splitext is on last .

    if isinstance(path, list):
        root = removeTrailingNumbers( root )

    if outputDir:
        if os.path.exists(outputDir) and os.path.isdir(outputDir):
            head = outputDir
        else:
            NTerror("Given output directory: " + outputDir + " is absent or is not a dir")
            return None

    if extension == ".pdf":
#        NTdebug("Will skip generating printable version as input is also a pdf")
        doPrint = False

    if extension == ".gif":
#        NTdebug("Will skip generating full size gif version as input is also a gif")
        doFull = False

    pinupPath = None
    fullPath  = None
    printPath = None

    # AWSS: convert and montage work better with pdf than ps
    # e.g. montaged figs are not trimmed from 2nd page and on as it happens
    # when input is ps.
    if extension == ".ps":
        doPrint = True

    # Algorithm below can be speeded up by not rereading the input but scripting the
    #     generation of 3 outputs.
    if doPrint:
        printPath = os.path.join( head, root+".pdf")
        if convertPs2Pdf( pathStr, printPath, optionsPrint):
            NTerror("Failed to generate print")
            printPath = None # failed for 2k1n_11_rstraints.ps
        pathStr = pathFirst = printPath

    if doPinUp and pathStr:
        pinupPath = os.path.join( head, root+"_pin.gif")
        if convertImageMagick(pathStr+"'[0-8]'", pinupPath, optionsPinUp): # Use only first 9 pages for pinup.
            NTerror("Failed to generate pinup")
            pinupPath = None

    if doFull and pathStr and pathFirst:
        if doMontage:
            # Just do the first 9 as this runs out of memory with 1vnd
            fullPath  = os.path.join( head, root+".png")
            if montage(pathFirst+"'[0-8]'", fullPath, extraOptions = "-density 144" ):
                NTerror('Failed to montage from %s to: %s' % ( pathFirst, fullPath ))
                return True
        else:
            fullPath  = os.path.join( head, root+".gif")
            if convertImageMagick(pathStr+"'[0-8]'", fullPath, optionsFull):
                NTerror("Failed to generated full gif")
                fullPath = None

    result = ( pinupPath, fullPath, printPath )
    if  pinupPath or fullPath or printPath:
        return result
    return None

def removeTrailingNumbers(fileName):
    p = re.compile( '\d+$' ) # I didn't get this to work with string.replace()
    return p.sub('', fileName)

def montage(pathList, outputFileName, extraOptions = None ):
    """Using the system montage from ImageMagick an html file will piece together the given
        imagery in full size:
        a- full size 1(gif of original size)

       Returns None for success.
       Input can be anything ImageMagick reads, e.g. Postscript produced by Procheck_NMR.
       The input pathList may also be a single file such as a multiple page .ps.
    """
    if not cingPaths.montage:
        NTerror("No cingPaths.montage in montageImageMagick")
        return True
#    backgroundColor = '#ede8e2' # default in cing.css
#    optionsPinUp = "-label %f -frame 15 -background %s -geometry +10+10 -geometry 102" % ( backgroundColor )
#    optionsFull  = "-frame 15 -geometry +10+10 -background '#ede8e2'"
    optionsFull  = "-geometry +10+10  "
#    optionsFull +=  backgroundColor
    if extraOptions:
        optionsFull += ' ' + extraOptions

    if isinstance(pathList, list):
        pathStr = ' '.join(pathList)
    else:
        pathStr = pathList

    if montageImageMagick(pathStr, outputFileName, optionsFull):
        NTerror("Failed to generated full html")
