'''
Created on Jul 8, 2010

@author: jd
'''
from cing import cingDirScripts
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.disk import mkdirs
from cing.NRG.settings import * #@UnusedWildImport
from cing.Scripts.FC.convertStar2Ccpn import importFullStarProjects
from shutil import rmtree
import time

doReadMmCif         = 1
doStar2Ccpn         = 0 # Actually linking by FC.
doInteractive       = 1 # DEFAULT 0 to do production run but 1 for a very fast run.

wattosProg = "java -Djava.awt.headless=true -Xmx1500m Wattos.CloneWars.UserInterface -at"

NTmessage("interactive        interactive run is fast use zero for production                          %s" % doInteractive)
NTmessage("doReadMmCif        Converts PDB mmCIF to NMR-STAR with Wattos        -> XXXX_wattos.str     %s" % doReadMmCif)
NTmessage("doStar2Ccpn            Converts STAR to STAR with linkNmrStarData.py -> XXXX_star2Ccpn.str  %s" % doStar2Ccpn)
NTmessage("PYTHONPATH:        %s" % os.getenv('PYTHONPATH'))
NTmessage("CLASSPATH:         %s" % os.getenv('CLASSPATH'))
NTmessage("wattosProg:        %s" % wattosProg)

def processEntry(pdb_id):
    "Return True on error."
    NTmessage("Doing              %s" % pdb_id)
    entryCodeChar2and3 = pdb_id[1:3]

    star_sub_entry_dir  = os.path.join( dir_star, entryCodeChar2and3 )
    star_entry_dir      = os.path.join( star_sub_entry_dir, pdb_id )
    link_sub_entry_dir  = os.path.join( dir_link, entryCodeChar2and3 )
    link_entry_dir      = os.path.join( link_sub_entry_dir, pdb_id )

    if doReadMmCif:
        NTmessage("  mmCIF")
        script_file     = '%s/ReadMmCifWriteNmrStar.wcf' % wcf_dir
        inputMmCifFile  = os.path.join( CIFZ2, entryCodeChar2and3, '%s.cif.gz' % pdb_id)
        outputStarFile  = "%s_wattos.str" % pdb_id
        script_file_new = "%s.wcf" % pdb_id
        log_file        = "%s.log" % pdb_id

        if not os.path.exists(star_entry_dir):
            mkdirs(dir_star)
        os.chdir( star_sub_entry_dir )
        if os.path.exists( pdb_id ):
            rmtree(pdb_id)
        os.mkdir( pdb_id )
        os.chdir( pdb_id )

        if not os.path.exists( inputMmCifFile ):
            NTerror("%s No input mmCIF file: %s" % ( pdb_id, inputMmCifFile))
            return True

        maxModels = '999'
        if doInteractive:
            maxModels = '2'

        script_str = readTextFromFile(script_file)
        script_str = script_str.replace('INPUT_MMCIF_FILE', inputMmCifFile)
        script_str = script_str.replace('MAX_MODELS', maxModels)
        script_str = script_str.replace('OUTPUT_STAR_FILE', outputStarFile)
        writeTextToFile(script_file_new, script_str)


#        wattos < $script_file_new >& $log_file
#        wattosPath = "java -Xmx512m -Djava.awt.headless=true Wattos.CloneWars.UserInterface -at"
#        logFileName = "wattos_compl.log"
        wattosProgram = ExecuteProgram(wattosProg, #rootPath = wattosDir,
                                 redirectOutputToFile = log_file,
                                 redirectInputFromFile = script_file_new)
        # The last argument becomes a necessary redirection into fouling Wattos into
        # thinking it's running interactively.
        now = time.time()
        wattosExitCode = wattosProgram()
        difTime = time.time() - now
        NTmessage("Took number of seconds: %8.1f" % difTime )
        if wattosExitCode:
            NTerror("%s Failed wattos script %s with exit code: " %(pdb_id, script_file_new, str(wattosExitCode)))
            return True

        resultList = []
        status = grep(log_file, 'ERROR', resultList=resultList, doQuiet=True)
        if status == 0:
            NTerror("%s found errors in log file; aborting."%pdb_id)
            NTmessage('\n'.join(resultList))
            return True

        os.unlink(script_file_new)

        if not os.path.exists( outputStarFile ):
            NTerror("%s found no output star file %s" % (pdb_id,outputStarFile))
            return True
        # end if
    # end if doReadMmCif

    if doStar2Ccpn:
        NTmessage("  star2Ccpn")
        log_file            = "%s_star2Ccpn.log" % pdb_id
        inputStarFile       = "%s_wattos.str" % pdb_id
        inputStarFileFull   = os.path.join(star_entry_dir, inputStarFile)
        fcScript            = os.path.join(cingDirScripts,'FC', 'convertStar2Ccpn.py')
        doConversionDirectly = False

        if not os.path.exists(link_entry_dir):
            mkdirs(dir_link)
        os.chdir( star_sub_entry_dir )
        if os.path.exists( pdb_id ):
            rmtree(pdb_id)
        os.mkdir( pdb_id )
        os.chdir( pdb_id )

        if not os.path.exists( inputStarFileFull ):
            NTerror("%s previous step produced no star file." % pdb_id)
            return True

        # Will save a copy to disk as well.
        if doConversionDirectly:
            ccpnProject = importFullStarProjects(inputStarFile, projectName=pdb_id, inputDir=star_entry_dir)
            if not ccpnProject:
                NTerror("%s failed importFullStarProjects" % pdb_id)
                return True
            # end if
        else:
            convertProgram = ExecuteProgram("python -u %s" % fcScript, redirectOutputToFile = log_file)
            NTmessage("    Running Wim Vranken's FormatConverter from script %s" % fcScript )
            exitCode = convertProgram("%s %s %s" % (inputStarFile, pdb_id, star_entry_dir))
            if exitCode:
                NTerror("Failed convertProgram with exit code: %s" % str(exitCode))
                return True
            resultList = []
            status = grep(log_file, 'ERROR', resultList=resultList, doQuiet=True, doCaseSensitive=False)
            if status == 0:
                NTerror("%s found errors in log file; aborting."%pdb_id)
                NTmessage('\n'.join(resultList))
                return True
    # end if doStar2Ccpn
    NTmessage("Done with %s" % pdb_id)


if __name__ == '__main__':
#    pdbList = '1a4d 1a24 1afp 1ai0 1b4y 1brv 1bus 1cjg 1d3z 1hkt 1hue 1ieh 1iv6 1jwe 1kr8 2hgh 2k0e'.split()
#    pdbList = '1ai0 1b4y 1brv 1bus 1cjg 1d3z 1hkt 1hue 1ieh 1iv6 1jwe 1kr8 2hgh 2k0e'.split()
    pdbList = '1brv'.split()
#    pdbList = ['1brv']
#1afp
    for pdb_id in pdbList:
        if processEntry(pdb_id):
            NTerror("Failed to process entry: %s" % pdb_id)
