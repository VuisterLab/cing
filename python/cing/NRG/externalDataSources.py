from __future__ import division, print_function, absolute_import, unicode_literals

import os
import errno
from urllib2 import urlopen
import re
import time
import datetime
import abc
import urllib
import subprocess
import time

from pandas import DataFrame
from pandas import to_datetime
from pandas import notnull

__author__ = 'TJ Ragan (tjr22@le.ac.uk)'


VALIDATION_REPORT_LOCATION = '/mnt/data/D/NRG-CING'
CING_HOME = '~/workspace/cing/python/cing/'
PYTHON_EXECUTABLE = 'python'
VALIDATION_SCRIPT_LOCATION = os.path.join(CING_HOME, 'Scripts', 'validateEntry.py')


class ExternalDataSource( object ):
    __metaclass__ = abc.ABCMeta

    CODE_STORAGE_FILE_LOCATION = 'data'

    def __init__(self, codeFileLocation=CODE_STORAGE_FILE_LOCATION,
                 storageMode='file',
                 cingDebugLevel=3):
        self.pdbCodesDatesStorageFileLocation = codeFileLocation
        self.storageMode = storageMode
        # self.cingDebugLevel = cingDebugLevel

        self.entryCodes = self.convertCodesDatesToDF( [(None, None)] )
        self.queuedEntryCodes = []
        self.validateEntryPy_Parameters ={'pythonExecutable': PYTHON_EXECUTABLE,
                                          'validationScriptLocation': VALIDATION_SCRIPT_LOCATION,
                                          'cingDebugLevel': str(cingDebugLevel),
                                          'sourceDataLocation': os.path.join(VALIDATION_REPORT_LOCATION,
                                                                             'data'),
                                          'reportDestinationLocation': VALIDATION_REPORT_LOCATION,
                                          'pdbConvention': '.',# Currently unused placeholder
                                          'restraintsConvention': '.',# Currently unused placeholder
                                          'sourceDataDirectoryStructure': 'BY_CH23_BY_ENTRY',
                                          'sourceDataType': None,
                                          'storeToDB': '1',
                                          'validationRange': 'auto',# 'None' == 'all', auto, all, cv, '1-4,5,7-10'
                                          'filterByTop': '0',
                                          'filterByVasco': '0',
                                          'singleCore': 'True',
                                         }




    @abc.abstractmethod
    def retrieveFullEntryList( self ):
        pass


    @abc.abstractmethod
    def make_validateEntryPy_Commands( self ):
        pass


    def prepareEntriesInQueue( self ):
        pass


    def loadEntryCodes(self, overwrite=False):
        projectsDF = DataFrame.from_csv(os.path.join( self.pdbCodesDatesStorageFileLocation,
                                                          self.CODE_STORAGE_FILE_NAME))
        projectsDF[ 'date' ] = to_datetime( projectsDF[ 'date' ] )
        projectsDF = projectsDF.copy().dropna()
        self.entryCodes = projectsDF


    def saveEntryCodes( self ):
        if self.storageMode == 'file':
            self._writeCSV()
        else:
            raise NotImplementedError("Planning on adding database and / or queue.")

    def _writeCSV( self ):
        self._makePathIfNotExists( self.pdbCodesDatesStorageFileLocation )
        with open(os.path.join( self.pdbCodesDatesStorageFileLocation,
                                self.CODE_STORAGE_FILE_NAME ), 'w') as f:
            self.entryCodes.to_csv(f)

    @staticmethod
    def _makePathIfNotExists( pathLocation ):
        try:
            os.makedirs( pathLocation )
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise


    def findValidatedProjects( self ):
        d = self.getPDBCodesWithValidationReportDirectories( )
        existingValidationPDBsAndDates = [(None, None),]
        for c in d:
            htmlIndexFile = os.path.join( VALIDATION_REPORT_LOCATION, 'data',
                                        c[1:3], c, c + '.cing', 'index.html')
            try:
                existingValidationPDBsAndDates.append((c, time.ctime(os.path.getmtime(htmlIndexFile))))
            except OSError:
                pass
        return self.convertCodesDatesToDF( existingValidationPDBsAndDates )

    def getPDBCodesWithValidationReportDirectories( self ):
        dirEntries = os.listdir( os.path.join( VALIDATION_REPORT_LOCATION, 'data') )
        twoLetterDirs = [d for d in dirEntries if os.path.isdir(os.path.join(
                                                                VALIDATION_REPORT_LOCATION,
                                                                'data',
                                                                d))]
        validationReportDirectories = [ ]
        for twoLetterDir in twoLetterDirs:
            subDir = os.path.join( VALIDATION_REPORT_LOCATION, 'data', twoLetterDir )
            validationReportDirectories += os.listdir( subDir )
        pdbCodesWithValidationDirectories = [ d for d in validationReportDirectories
                                              if re.match( '[0-9][0-9a-z]{3}', d ) ]
        return pdbCodesWithValidationDirectories


    def convertCodesDatesToDF( self, pdbsAndDates ):
        df = DataFrame( pdbsAndDates, columns=[ 'pdb', 'date' ] )
        df[ 'date' ] = to_datetime( df[ 'date' ] )
        df = df[ notnull(df[ 'pdb' ]) ]
        df = df.drop_duplicates()
        return df


    def filterEntryCodesByDates(self, startDate, endDate):
        if startDate >= endDate:
            raise ValueError("endDate should be after startDate.")
        if startDate is not None:
            self.entryCodes = self.entryCodes[self.entryCodes.date > startDate]
        if endDate is not None:
            self.entryCodes = self.entryCodes[self.entryCodes.date < endDate]


    def _findProjectsNewerThan( self, codesDatesDF ):
        comparisonDF = self.entryCodes.merge( codesDatesDF, on='pdb', how='right', suffixes=('', 'local'))
        comparisonDF.dropna(inplace=True)
        newerProjects = comparisonDF[ comparisonDF.date > comparisonDF.datelocal ]
        return newerProjects[['pdb', 'date']]


    def _findProjectsNotIn( self, codesDatesDF ):
        comparisonDF = self.entryCodes.merge( codesDatesDF, on='pdb', how='left', suffixes=('', 'local'))
        newProjects = comparisonDF[comparisonDF.datelocal.isnull()]
        return newProjects[['pdb', 'date']]


    def addEntriesToQueue( self, newerEntries ):
        newerEntries.sort( 'date', inplace=True )
        newerEntriesToQueue = newerEntries[ 'pdb' ].tolist( )
        newerEntriesToQueue = [ x for x in newerEntriesToQueue if x not in self.queuedEntryCodes ]
        self.queuedEntryCodes += newerEntriesToQueue


    def addAllEntriesToQueue( self ):
        self.addEntriesToQueue( self.entryCodes )


    def addNewEntriesToQueue( self ):
        alreadyValidatedProjects = self.findValidatedProjects()
        newerEntries = self._findProjectsNotIn( alreadyValidatedProjects )
        self.addEntriesToQueue( newerEntries )


    def addUpdatedEntriesToQueue( self ):
        alreadyValidatedProjects = self.findValidatedProjects()
        newerEntries = self._findProjectsNewerThan( alreadyValidatedProjects )
        self.addEntriesToQueue( newerEntries )

    @classmethod
    def makeEntryValidationReportLocation( cls, e ):
        p = os.path.join(VALIDATION_REPORT_LOCATION, 'data', e[1:3], e)
        cls._makePathIfNotExists( p )


    @staticmethod
    def setDataTimestamp( pdbCode, timestamp ):
        fileLocation = os.path.join( VALIDATION_REPORT_LOCATION, 'data', pdbCode[1:3],
                                         pdbCode , pdbCode + '.tgz')
        ts = time.mktime(timestamp.timetuple())

        os.utime(fileLocation, ( time.time(), ts ))


    def make_validateEntryPy_Commands(self, pdbCodes=None):
        if pdbCodes is None:
            pdbCodes = self.queuedEntryCodes

        validationCommand = "{pythonExecutable} "\
                            "{validationScriptLocation} " \
                            "{{}} " \
                            "{cingDebugLevel} " \
                            "{sourceDataLocation} " \
                            "{reportDestinationLocation} " \
                            "{pdbConvention} " \
                            "{restraintsConvention} " \
                            "{sourceDataDirectoryStructure} " \
                            "{sourceDataType} " \
                            "{storeToDB} " \
                            "{validationRange} " \
                            "{filterByTop} " \
                            "{filterByVasco} " \
                            "{singleCore}" \
                            .format(**self.validateEntryPy_Parameters)

        return [validationCommand.format(pdbCode) for pdbCode in pdbCodes]



class BMRBData( ExternalDataSource ):
    DATA_URL_BASE = 'http://www.bmrb.wisc.edu/ftp/pub/bmrb/nmr_pdb_integrated_data/coordinates_restraints_chemshifts/all/ccpn/'
    CODES_DATES_REGEX_STRING = '([0-9][a-z0-9]{3}).+([0-3][0-9]-[A-Z][a-z]{2}-[0-9]{4} [0-9]{2}:[0-9]{2})'
    CODE_STORAGE_FILE_NAME = 'bmrbEntryList.csv'

    def __init__( self, *arg, **kwargs ):
        super(BMRBData, self).__init__(*arg, **kwargs)
        self.validateEntryPy_Parameters['sourceDataType'] = 'CCPN'


    def retrieveFullEntryList( self ):
        ftpDirectoryListing = self._getFTPDirectoryListing()
        datesCodes = self._extractCodesDatesFromFTPListing( ftpDirectoryListing )
        self.entryCodes = self.convertCodesDatesToDF( datesCodes )

    def _getFTPDirectoryListing( self ):
        response = urlopen( self.DATA_URL_BASE )
        return response.read()

    def _extractCodesDatesFromFTPListing( self, ftpListingText ):
        return re.findall( self.CODES_DATES_REGEX_STRING, ftpListingText )


    def prepareEntriesInQueue( self , force=False):
        qll = len( self.queuedEntryCodes )
        for entry in self.queuedEntryCodes:
            qll -= 1
            downloadLocation = os.path.join( VALIDATION_REPORT_LOCATION, 'data', entry[1:3],
                                         entry , entry + '.tgz')
            shouldDownload = True
            try:
                t = time.ctime( os.path.getctime( downloadLocation ) )
                assert (t >= self.entryCodes[self.entryCodes['pdb'] == entry]['date'].item())
                shouldDownload = False
            except:
                pass
            if force or shouldDownload:
                print('    Downloading {} from BMRB... '.format( entry ))
                self.retrieveProjectFromBMRBbyPDBCode( entry )
                ts = self.entryCodes[self.entryCodes['pdb'] == entry]['date'].tolist()[0]
                ExternalDataSource.setDataTimestamp( entry, ts )
                print('    done.  {} remaining.'.format( qll ))



    @classmethod
    def retrieveProjectFromBMRBbyPDBCode( cls, pdbCode ):
        projectLocation = cls.DATA_URL_BASE + pdbCode + '/' + pdbCode + '.tgz'
        downloadLocation = os.path.join( VALIDATION_REPORT_LOCATION, 'data', pdbCode[1:3],
                                         pdbCode , pdbCode + '.tgz')
        cls.makeEntryValidationReportLocation( pdbCode )
        urllib.urlretrieve(projectLocation, downloadLocation)



class CASDData( ExternalDataSource ):
    DATA_URL_BASE = '/mnt/data/D/CASD-NMR-CING/tj_test/submissions/CASD-NMR-CING/data'
    CODE_STORAGE_FILE_NAME = 'casdEntryList.csv'
    VALIDATION_REPORT_LOCATION = '/mnt/data/D/CASD-NMR-CING/tj_test/'


    def __init__( self, *arg, **kwargs ):
        super(CASDData, self).__init__(*arg, **kwargs)
        self.validateEntryPy_Parameters['sourceDataType'] = 'CCPN'
        self.validateEntryPy_Parameters['sourceDataLocation']= os.path.join(VALIDATION_REPORT_LOCATION,
                                                                            'data'),
        self.validateEntryPy_Parameters['reportDestinationLocation'] = VALIDATION_REPORT_LOCATION,


    def retrieveFullEntryList( self ):
        """
        1. go to the data_url_base
        2. get the list of entries - data are organized by 23 code -
            Example: l9/2l9r_Cheshire_131/2l9r_Cheshire_131.tgz
        3. self.entryCodes = self.convertCodesDatesToDF( datesCodes )
        """
        dirEntries = os.listdir( os.path.join( VALIDATION_REPORT_LOCATION, 'data') )
        twoLetterDirs = [d for d in dirEntries if os.path.isdir(os.path.join(
                                                                VALIDATION_REPORT_LOCATION,
                                                                'data',
                                                                d))]


    def make_validateEntryPy_Commands( self ):
        """
        same as BMRB, but change SQL target
        """

        pass




    def prepareEntriesInQueue( self ):
        """
        1. make dirs in report_location
        2. copy tgz files there
        """

        pass
