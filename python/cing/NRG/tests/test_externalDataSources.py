from __future__ import print_function, absolute_import

import datetime
import errno
import os
import time

from unittest import TestCase
from mock import patch
from mock import Mock

import pandas as pd
from pandas.util.testing import assert_frame_equal

__author__ = 'TJ Ragan (tjr22@le.ac.uk)'

import cing.NRG.externalDataSources as edc

class TestExternalDataSource_UnitTests( TestCase ):

    def concreter(self, abclass):
        if not "__abstractmethods__" in abclass.__dict__:
            return abclass
        new_dict = abclass.__dict__.copy()
        for abstractmethod in abclass.__abstractmethods__:
            #replace each abc method or property with an identity function:
            new_dict[abstractmethod] = lambda x, *args, **kw: (x, args, kw)
        #creates a new class, with the overriden ABCs:
        return type(str("dummy_concrete_%s") % abclass.__name__, (abclass,), new_dict)


    def setUp(self):
        self.externalDataSource = self.concreter(edc.ExternalDataSource)()


class TestExternalDataSource( TestExternalDataSource_UnitTests ):

    @patch.object(edc, 'VALIDATION_REPORT_LOCATION', 'test')
    def test_setDataTimestamp(self):
        currentTime = time.mktime( [2000,1,1, 0,0,0, 0,0,0] )
        modifiedDateTime = datetime.datetime( 2010,06,26, 05,23 )
        modifiedTime = time.mktime( modifiedDateTime.timetuple() )

        with patch('cing.NRG.externalDataSources.os.utime') as mock_utime, \
             patch('cing.NRG.externalDataSources.time.time') as mock_time:
            mock_time.return_value = currentTime

            edc.ExternalDataSource.setDataTimestamp('1nor', modifiedDateTime)

            mock_utime.assert_called_with( 'test/data/no/1nor/1nor.tgz', ( currentTime, modifiedTime) )

    def _test_findValidatedProjects(self):
        with patch.object(self.externalDataSource, 'getPDBCodesWithValidationReportDirectories') \
                                                                                  as mock_gPDBs, \
             patch('cing.NRG.externalDataSources.time') as mock_time:
            mock_gPDBs.return_value = ['2k86']
            mock_time.ctime.return_value = 'Tue Nov 11 09:55:22 2014'
            avp = self.externalDataSource.convertCodesDatesToDF( [('2k86', 'Tue Nov 11 09:55:22 2014'),] )

            fvp = self.externalDataSource.findValidatedProjects()

            self.assertEquals( avp['pdb'].tolist(), fvp['pdb'].tolist() )
            self.assertEquals( avp['date'].tolist(), fvp['date'].tolist() )

    def test_getPDBCodesWithValidationReportDirectories(self):
        pass



class TestBMRBData( TestExternalDataSource_UnitTests ):

    BMRB_RESPONSE = '''c="/icons/folder.gif" alt="[DIR]"></td><td><a href="1nor/">1nor/</a></td><td align="right">26-Jun-2010 05:23  </td><td align="right">  - </td></tr>
<tr><td valign="top"><img src="/icons/folder.gif" alt="[DIR]"></td><td><a href="1np5/">1np5/</a></td><td align="right">26-Jun-2010 05:24  </td><td align="right">  - </td></tr>
<tr><td valign="top"><img src="/icons/folder.gif" alt="[DIR]"></td><td><a href="2ruk/">2ruk/</a></td><td align="right">13-Oct-2014 16:59  </td><td align="right">  - </td></tr>
<tr><td valign="top"><img src="/icons/folder.gif" alt="[DIR]"></td><td><a href="229d/">229d/</a></td><td align="right">25-Jun-2010 08:31  </td><td align="right">  - </td></tr>
<tr><th colspan="5"><hr></th></tr>
</table>
<address>Apache/2.2.3 (CentOS) Server at www.bmrb.wisc.edu Port 80</address>
</body></html>
'''
    CODES_AND_DATES_FROM_BMRB_RESPONSE = [('1nor', '26-Jun-2010 05:23'), ('1np5', '26-Jun-2010 05:24'), ('2ruk', '13-Oct-2014 16:59'), ('229d', '25-Jun-2010 08:31')]

    def setUp(self):
        super(TestBMRBData, self).setUp()
        self.bmrb = edc.BMRBData()


    @patch('cing.NRG.externalDataSources.urlopen')
    def test__getFTPDirectoryListing( self, mock_urlopen ):
        r = Mock()
        r.read.return_value = self.BMRB_RESPONSE
        mock_urlopen.return_value = r

        response = self.bmrb._getFTPDirectoryListing()
        mock_urlopen.assert_called_with( self.bmrb.DATA_URL_BASE )
        self.assertEquals( response, self.BMRB_RESPONSE )

    def test_extractCodesDatesFromFTPListing( self ):
        pdbCodesAndDates = self.bmrb._extractCodesDatesFromFTPListing( self.BMRB_RESPONSE )
        self.assertEquals( pdbCodesAndDates, self.CODES_AND_DATES_FROM_BMRB_RESPONSE)

    def test__makePathIfNotExists_PathDoesntExist(self):
        PATH = '/home/i/workspace/cing/python/cing/NRG/data'

        with patch('cing.NRG.externalDataSources.os') as mock_os:
            self.externalDataSource._makePathIfNotExists( PATH )
            mock_os.makedirs.assert_called_with( PATH )

    def test__makePathIfNotExists_PathExists(self):
        PATH = '/home/i/workspace/cing/python/cing/NRG/data'

        with patch('cing.NRG.externalDataSources.os') as mock_os:
            e = OSError()
            e.errno = errno.EEXIST
            o = Mock( side_effect = e )
            mock_os.makedirs = o
            self.externalDataSource._makePathIfNotExists( PATH )

    def _test__makePathIfNotExists_OtherOSError(self):
        PATH = '/home/i/workspace/cing/python/cing/NRG/data'

        with patch(     ) as mock_os:
            o = Mock( side_effect = OSError() )
            mock_os.makedirs = o
            self.assertRaises(OSError, self.externalDataSource._makePathIfNotExists, PATH )

    @patch.object(edc, 'VALIDATION_REPORT_LOCATION', 'test')
    def test_makeEntryValidationReportLocation(self):
        with patch('cing.NRG.externalDataSources.os.makedirs') as mock_mkdirs:
            self.externalDataSource.makeEntryValidationReportLocation('1nor')

            mock_mkdirs.assert_called_with( os.path.join('test', 'data', 'no', '1nor') )

    def test_convertCodesDatesToDataFrame(self):
        df = self.externalDataSource.convertCodesDatesToDF(
               self.CODES_AND_DATES_FROM_BMRB_RESPONSE )
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEquals(df.shape, (4, 2))
        self.assertEquals(df.dtypes['date'], 'datetime64[ns]')

    def test_filterEntryCodesByDates_startLaterThanEnd(self):
        self.assertRaises(ValueError, self.externalDataSource.filterEntryCodesByDates,
                                      startDate=datetime.date(2012, 1, 1), endDate=datetime.date(2011, 1, 1))

    def test__findProjectsNewerThan(self):
        alreadyValidatedProjects = self.externalDataSource.convertCodesDatesToDF(
                                            [('1nor', '26-Jun-2010 05:23'),
                                             ('2ruk', '13-Oct-2010 16:59')]
                                           )
        self.externalDataSource.entryCodes = self.externalDataSource.convertCodesDatesToDF(
                                            [('1nor', '26-Jun-2010 05:23'),
                                             ('2ruk', '13-Oct-2014 16:59'),
                                             ('229d', '25-Jun-2010 08:31')]
                                           )
        p = self.externalDataSource.convertCodesDatesToDF(
                                            [('2ruk', '13-Oct-2014 16:59')])

        e = self.externalDataSource._findProjectsNewerThan( alreadyValidatedProjects )

        assert_frame_equal(p.set_index('pdb'), e.set_index('pdb'))

    def test__findProjectsNotI(self):
        alreadyValidatedProjects = self.externalDataSource.convertCodesDatesToDF(
                                            [('1nor', '26-Jun-2010 05:23'),
                                             ('2ruk', '13-Oct-2010 16:59')]
                                           )
        self.externalDataSource.entryCodes = self.externalDataSource.convertCodesDatesToDF(
                                            [('1nor', '26-Jun-2010 05:23'),
                                             ('2ruk', '13-Oct-2014 16:59'),
                                             ('229d', '25-Jun-2010 08:31')]
                                           )
        p = self.externalDataSource.convertCodesDatesToDF(
                                            [('229d', '25-Jun-2010 08:31')])

        e = self.externalDataSource._findProjectsNotIn( alreadyValidatedProjects )

        assert_frame_equal(p.set_index('pdb'), e.set_index('pdb'))

    def test_addEntriesToQueue(self):
        e = self.externalDataSource.convertCodesDatesToDF(
                                            [('1nor', '26-Jun-2010 05:23'),
                                             ('2ruk', '13-Oct-2014 16:59'),
                                             ('229d', '25-Jun-2010 08:31')]
                                           )
        self.externalDataSource.queuedEntryCodes = ['2ruk']

        self.externalDataSource.addEntriesToQueue(e)
        self.assertEquals(self.externalDataSource.queuedEntryCodes, ['2ruk', '229d', '1nor'])

    def _test_retrieveProjectFromBMRBbyPDBCode(self):
        edc.VALIDATION_REPORT_LOCATION = 'data'
        edc.BMRBData.DATA_URL_BASE = 'http://test/'

        with patch('cing.NRG.externalDataSources.urllib.urlretrieve') as mock_urlretrieve, \
             patch('cing.NRG.externalDataSources.ExternalDataSource.makeEntryValidationReportLocation') as mock_mEVRL:

            self.bmrb.retrieveProjectFromBMRBbyPDBCode( '1tst' )

            mock_mEVRL.assert_called_with( '1tst' )
            mock_urlretrieve.assert_called_with('http://test/1tst/1tst.tgz',
                                                 'data/ts/1tst/1tst.tgz')

    def test_prepareEntriesInQueue(self):
        p = self.externalDataSource.convertCodesDatesToDF(
                                            [('1ce3', '13-Oct-2014 16:59')])
        self.bmrb.entryCodes = p
        self.bmrb.addEntriesToQueue(p)
        currentTime = time.mktime( [2000,1,1, 0,0,0, 0,0,0] )

        with patch.object(self.bmrb, 'retrieveProjectFromBMRBbyPDBCode') as mock_rPF, \
             patch.object(edc, 'VALIDATION_REPORT_LOCATION', 'test'), \
             patch.object(edc.os, 'utime') as mock_utime, \
             patch.object(edc.time, 'time') as mock_time:
            mock_time.return_value = currentTime

            self.bmrb.prepareEntriesInQueue()

            mock_rPF.assert_called_once_with('1ce3')
            mock_utime.assert_called_once_with('test/ce/1ce3/1ce3.tgz', (946684800.0, 1413215940.0))

    def test_prepareEntriesInQueue(self):
        self.bmrb.validateEntryPy_Parameters['pythonExecutable'] = 't_1'
        self.bmrb.validateEntryPy_Parameters['validationScriptLocation'] = 't_2'
        self.bmrb.validateEntryPy_Parameters['cingDebugLevel'] = 't_3'
        self.bmrb.validateEntryPy_Parameters['sourceDataLocation'] = 't_4'
        self.bmrb.validateEntryPy_Parameters['reportDestinationLocation'] = 't_5'

        validateEntryPy_cmd = self.bmrb.make_validateEntryPy_Commands(['t_pdb'])
        self.assertEqual(validateEntryPy_cmd,
                         ['t_1 t_2 t_pdb t_3 t_4 t_5 . . BY_CH23_BY_ENTRY CCPN 1 auto 0 0 True'])


    def test_dev(self):
        pdb = '2mum'
        self.bmrb.retrieveProjectFromBMRBbyPDBCode(pdb)
        starCode = self.bmrb.retrieveStarFromBMRBbyPDBCode(pdb)
        self.bmrb.mergePDBStarFiles(pdb, starCode)
        self.bmrb.relocateMergedFiles(pdb)

class TestFileData_UnitTests( TestExternalDataSource_UnitTests ):

    DATA_URL_BASE = 'file:///mnt/data/D/NRG-CING/tj_test/data'

    def setUp(self):
        super(TestBMRBData_UnitTests, self).setUp()
        self.fileSystem = edc.FileSystemData()


class TestFileData_retrieveFullEntryList_UnitTest( TestFileData_UnitTests ):
    pass
