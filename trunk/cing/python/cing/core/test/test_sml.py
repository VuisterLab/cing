from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.core.sml import * #@UnusedWildImport
from unittest import TestCase
import unittest


class TestObject( NTdict ):
    def __init__(self):
        NTdict.__init__(self)
        self.a = 0
#    #end def
#end class
class SMLTestObjectHandler( SMLNTdictHandler ):
    def __init__(self):
        SMLhandler.__init__( self, name = 'TestObject' )
    #end def
    def handle(self, line, fp, project=None):
#        nTdebug("Now in SMLTestObjectHandler#handle at line: %s" % str(line))
        return SMLNTdictHandler.handle(self, line, fp, project)
#    end def
#    def toSML(self, rl, fp):
#        fprintf( fp, "%s\n", self.beginTag )
#        rl.toSML( fp ) # NTlist with same tag as the above self.startTag but no problem.
#        rl.vascoResults.toSML( fp )
#        fprintf( fp, "%s\n", self.endTag )
#    #end def
#end class
TestObject.SMLhandler = SMLTestObjectHandler()


class AllChecks(TestCase):

    cingDirTmpTest = os.path.join( cingDirTmp, 'test_sml' )
    mkdirs( cingDirTmpTest )
    os.chdir(cingDirTmpTest)

    def testSml(self):
        fn = 'testObject.sml'
        a = NTdict(aap=1,noot=2)
        e = NTdict() # empty fails?
        b = NTdict(dd=a, kess=4, ee=e)
#        print "Dicts: ", repr(a), repr(b), repr(e)

        obj2SML( b, fn)
        c = SML2obj( fn)
        self.failIf( len(c.keys()) != 3 )
        self.failIf( len(c.dd.keys()) != 2 )
#        print "Dict restored: ", repr(c), repr(c.dd)

    def testSml_2(self):
        fn = 'testObject_2.sml'
        a = NTlist(1,False,'testje')
        obj2SML( a, fn)
        c = SML2obj( fn)
        self.failIf( len(c) != 3 )
#        self.failIf( len(c.dd.keys()) != 2 )
#        print "Dict restored: ", repr(c), repr(c.dd)

    def testSml_3(self):
        fn = 'testObject_3.sml'
        a = NTlist(1,False,'testje')
        b = NTdict(aap=1,noot=2)
        testObject = NTlist(a,b)
        obj2SML( testObject, fn)
        c = SML2obj( fn)
        self.failIf( len(c) != 2 )
#        self.failIf( len(c.dd.keys()) != 2 )
#        print "Dict restored: ", repr(c), repr(c.dd)

    def testSml_4(self):
        fn = 'testObject_4.sml'
#        SMLhandler.debug = True
        a = NTlist(1,False,'testje')
        b = NTdict(aap=1,noot=2)
        testObject = NTdict(aa=a,bb=b)
        obj2SML( testObject, fn)
        c = SML2obj( fn)
        self.failIf( len(c) != 2 )
        self.failIf( getDeepByKeysOrAttributes(c, 'bb', 'noot') != 2 )
#        self.failIf( len(c.dd.keys()) != 2 )
#        print "Dict restored: ", repr(c), repr(c.dd)

    def testSml_5(self):
        fn = 'testObject_5.sml'
#        SMLhandler.debug = True
#        a = NTlist(1,False,'testje')
#        b = NTdict(aap=1,noot=2)
#        testObject = NTdict(aa=a,bb=b)
        testObject = TestObject()
        obj2SML( testObject, fn)
        c = SML2obj( fn)
#        nTdebug("Restored to: %r" % c)
        self.failIf( len(c.keys()) != 1 )
        self.failIf( getDeepByKeysOrAttributes(c, 'a') != 0 )
#        self.failIf( len(c.dd.keys()) != 2 )
#        print "Dict restored: ", repr(c), repr(c.dd)

    def testSml_6(self):
        SMLhandler.debug = cing.verbosity == cing.verbosityDebug
        fn = 'testObject_6.sml'
#        p = Project.open('testObject6', status = 'new')
        molecule = Molecule(name='moleculeName')
#        p.appendMolecule(molecule) # Needed for html.
        testObject = molecule.newResonances()
#        testObject.append(Resonance(value=-999.9))
        testObject.vascoApplied = True
        if os.path.exists(fn):
            os.unlink(fn)
        savedObject = obj2SML( molecule, fn)
        self.failIf( savedObject == None)
        nTdebug("Written to: %r" % fn)
        testObjectRead = SML2obj( fn )
        nTdebug("Restored to: %s" % str(testObjectRead))
#        self.failIf( len(testObjectRead) != 0 )
        self.failIf( getDeepByKeysOrAttributes(testObjectRead, RESONANCE_SOURCES_STR, 0, VASCO_APPLIED_STR) != True )
    # end def
# end class

if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
