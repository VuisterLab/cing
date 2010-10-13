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

cing.verbosity = cing.verbosityOutput
#cing.verbosity = cing.verbosityNothing
#wattosVerbosity = 0 # The codes are exactly parallel.
wattosVerbosity = cing.verbosity
wattosProg = "java -Djava.awt.headless=true -Xmx1500m Wattos.CloneWars.UserInterface -at -verbosity %s" % wattosVerbosity

NTmessage("PYTHONPATH:        %s" % os.getenv('PYTHONPATH'))
NTmessage("CLASSPATH:         %s" % os.getenv('CLASSPATH'))
NTmessage("wattosProg:        %s" % wattosProg)

class processNrgCing(Lister):
    """Main class for running CING reports on NRG and maintaining the statistics."""
    def __init__(self,
                 max_entries_todo = 1,
                 max_time_to_wait = 20,
                 processes_max = 2,
                 writeWhyNot = False,
                 writeTheManyFiles = False,
                 updateIndices = False,
                 isProduction = False
                ):

        self.writeWhyNot = writeWhyNot
        "Write the info for the WhyNot database"
        self.writeTheManyFiles = writeTheManyFiles
        "Write the info for the WhyNot database in files per entry; too verbose and not used anymore?"
        self.updateIndices = updateIndices
        self.isProduction = isProduction
        "Only during production we do a write to WHY_NOT"

        # Dir as base in which all info and scripts like this one resides
#        self.base_dir = os.path.join(cingPythonCing/Dir, "NRG")

        self.results_base = 'NRG-CING'
        self.results_dir = os.path.join('/Library/WebServer/Documents', self.results_base)
        self.data_dir = os.path.join(self.results_dir, 'data')
        self.results_host = 'localhost'
        if self.isProduction:
            # Needed for php script.
            self.results_host = 'nmr.cmbi.ru.nl'
        self.results_url = 'http://' + self.results_host + '/' + self.results_base # NEW without trailing slash.

        # The csv file name for indexing pdb
        self.index_pdb_file_name = self.results_dir + "/index/index_pdb.csv"
        self.why_not_db_comments_dir = os.path.join(self.results_dir, "cmbi8", "comments")
        self.why_not_db_raw_dir = os.path.join(self.results_dir, "cmbi8", "raw")
        self.why_not_db_comments_file = 'NRG-CING.txt_done'

        self.max_entries_todo = max_entries_todo
        self.max_time_to_wait = max_time_to_wait
        self.processes_max = processes_max

        ## How long to wait between submitting individual jobs when on the cluster.
        ##self.delay_between_submitting_jobs = 5
        self.delay_between_submitting_jobs = 5
        ## Total number of child processes to be done if all scheduled to be done
        ## are indeed to be done. This is set later on and perhaps adjusted
        ## when the user interrupts the process by ctrl-c.
        self.url_redirecter = self.results_url + '/redirect.php'
        self.url_csv_file_link_base = 'http://www.bmrb.wisc.edu/servlet_data/viavia/bmrb_pdb_match'
        ## Dictionary with matches pdb to bmrb
        self.matches_many2one = {}
        ## Dictionary with matches bmrb to pdb
        self.matches_one2many = {}
        ## Dictionary with matches bmrb to pdb
        self.matches_one2many_inv = {}
        ## Replace %b in the below for the real link.
        self.bmrb_link_template = 'http://www.bmrb.wisc.edu/cgi-bin/explore.cgi?bmrbId=%b'
        self.pdb_link_template = 'http://www.rcsb.org/pdb/explore/explore.do?structureId=%s'
        self.cing_link_template = self.results_url + '/data/%t/%s/%s.cing/%s/HTML/index.html'

        ##No changes required below this line
        ###############################################################################

        os.chdir(self.results_dir)

        ## List of 'new' entries for which hits were found
        self.new_hits_entry_list = NTlist()
        self.entry_list_pdb = NTlist()
        self.entry_list_nmr = NTlist()
        self.entry_list_nmr_exp = NTlist()
        self.entry_list_nrg = NTlist()          # should be the same as self.entry_list_nmr_exp
        self.entry_list_nrg_docr = NTlist()

        # From disk.
        self.entry_list_tried = NTlist()      # .cing directory and .log file present so it was tried to start but might not have finished
        self.entry_list_crashed = NTlist()    # has a stack trace
        self.entry_list_stopped = NTlist()    # was stopped by time out or by user or by system (any other type of stop but stack trace)
        self.entry_list_done = NTlist()       # finished to completion of the cing run.
        self.entry_list_todo = NTlist()
        self.timeTakenDict = NTdict()
        self.entry_list_obsolete = NTlist()
        self.ENTRY_DELETED_COUNT_MAX = 2


def processEntry(pdb_id,
                 doInteractive = 0,
                 convertMmCifCoor = 1,
                 convertMrRestraints = 0,
                 convertStarCS = 0,
                 filterCcpnAll = 0,
                 ):

    "Return True on error."
    NTmessage("interactive            interactive run is fast use zero for production                              %s" % doInteractive)
    NTmessage("convertMmCifCoor       Converts PDB mmCIF to NMR-STAR with Wattos        -> C/XXXX_C_FC.xml         %s" % convertMmCifCoor)
    NTmessage("convertMrRestraints    Adds STAR restraints to Ccpn with XXXX            -> R/XXXX_R_FC.xml         %s" % convertMrRestraints)
    NTmessage("convertStarCS          Adds STAR CS to Ccpn with XXXX                    -> S/XXXX_S_FC.xml         %s" % convertStarCS)
    NTmessage("filterCcpnAll          Filter CS and restraints with XXXX                -> F/XXXX_F_FC.xml         %s" % filterCcpnAll)

    NTmessage("Doing              %s" % pdb_id)
    entryCodeChar2and3 = pdb_id[1:3]

    C_sub_entry_dir  = os.path.join( dir_C, entryCodeChar2and3 )
    C_entry_dir      = os.path.join( C_sub_entry_dir, pdb_id )
    link_sub_entry_dir  = os.path.join( dir_link, entryCodeChar2and3 )
    link_entry_dir      = os.path.join( link_sub_entry_dir, pdb_id )

    if convertMmCifCoor:
        NTmessage("  mmCIF")
        convertStarCoor = 0 # DEFAULT 1: TODO: code.

        script_file     = '%s/ReadMmCifWriteNmrStar.wcf' % wcf_dir
        inputMmCifFile  = os.path.join( CIFZ2, entryCodeChar2and3, '%s.cif.gz' % pdb_id)
        outputStarFile  = "%s_C_Wattos.str" % pdb_id
        script_file_new = "%s.wcf" % pdb_id
        log_file        = "%s.log" % pdb_id

        if not os.path.exists(C_entry_dir):
            mkdirs(dir_C)
        if not os.path.exists(C_sub_entry_dir):
            mkdirs(C_sub_entry_dir)
        os.chdir( C_sub_entry_dir )
        if os.path.exists( pdb_id ):
            rmtree(pdb_id)
        os.mkdir( pdb_id )
        os.chdir( pdb_id )

        if not os.path.exists( inputMmCifFile ):
            NTerror("%s No input mmCIF file: %s" % ( pdb_id, inputMmCifFile))
            return True

        maxModels = '999'
        if doInteractive:
            maxModels = '1'

        script_str = readTextFromFile(script_file)
        script_str = script_str.replace('WATTOS_VERBOSITY', str(wattosVerbosity))
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
        NTdebug("Took number of seconds: %8.1f" % difTime )
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

        if convertStarCoor:
            NTmessage("  star2Ccpn")
            log_file            = "%s_star2Ccpn.log" % pdb_id
            inputStarFile       = "%s_wattos.str" % pdb_id
            inputStarFileFull   = os.path.join(C_entry_dir, inputStarFile)
            fcScript            = os.path.join(cingDirScripts,'FC', 'convertStar2Ccpn.py')
            doConversionDirectly = False

            if not os.path.exists(link_entry_dir):
                mkdirs(dir_link)
            os.chdir( C_sub_entry_dir )
            if os.path.exists( pdb_id ):
                rmtree(pdb_id)
            os.mkdir( pdb_id )
            os.chdir( pdb_id )

            if not os.path.exists( inputStarFileFull ):
                NTerror("%s previous step produced no star file." % pdb_id)
                return True

            # Will save a copy to disk as well.
            if doConversionDirectly:
                ccpnProject = importFullStarProjects(inputStarFile, projectName=pdb_id, inputDir=C_entry_dir)
                if not ccpnProject:
                    NTerror("%s failed importFullStarProjects" % pdb_id)
                    return True
                # end if
            else:
                convertProgram = ExecuteProgram("python -u %s" % fcScript, redirectOutputToFile = log_file)
                NTmessage("==> Running Wim Vranken's FormatConverter from script %s" % fcScript )
                exitCode = convertProgram("%s %s %s" % (inputStarFile, pdb_id, C_entry_dir))
                if exitCode:
                    NTerror("Failed convertProgram with exit code: %s" % str(exitCode))
                    return True
                resultList = []
                status = grep(log_file, 'ERROR', resultList=resultList, doQuiet=True, doCaseSensitive=False)
                if status == 0:
                    NTerror("%s found errors in log file; aborting."%pdb_id)
                    NTmessage('\n'.join(resultList))
                    return True
        # end if convertStarCoor
        NTmessage("Done with %s" % pdb_id)
    # end if convertMmCifCoor




