import os, sys

import cing

from memops.gui.Button          import Button #@UnresolvedImport
from memops.gui.RadioButtons    import RadioButtons #@UnresolvedImport
from memops.gui.CheckButton     import CheckButton #@UnresolvedImport
from memops.gui.ButtonList      import ButtonList #@UnresolvedImport
from memops.gui.Entry           import Entry #@UnresolvedImport
from memops.gui.FileSelect      import FileType #@UnresolvedImport
from memops.gui.FileSelectPopup import FileSelectPopup #@UnresolvedImport
from memops.gui.Frame           import Frame #@UnusedImport @UnresolvedImport
from memops.gui.Label           import Label #@UnresolvedImport
from memops.gui.Menu            import Menu #@UnresolvedImport
#from memops.gui.LabelFrame      import LabelFrame
from memops.gui.MessageReporter import showWarning, showOkCancel #@UnusedImport @UnresolvedImport
from memops.gui.PulldownMenu    import PulldownMenu #@UnusedImport @UnresolvedImport
from memops.gui.ScrolledText    import ScrolledText #@UnresolvedImport
from memops.gui.ScrolledText    import Text #@UnresolvedImport

from memops.editor.BasePopup    import BasePopup #@UnresolvedImport
from memops.editor.Util         import createDismissHelpButtonList #@UnusedImport @UnresolvedImport

from cing.Libs.NTutils          import nTpath, nTerror, nTmessage, sprintf


largeFont = 'Helvetica 14 bold'
medFont   = 'Helvetica 12 bold'
buttonBackgroundColor = '#90D0FF'

actionButtonAttributes = dict(
    bd = 1,
#    bg = 'darkgreen',
#    fg = 'white'
    bg = '#90D0FF'
)

labelFrameAttributes = dict(
#    bd = 2,
#    relief = 'raised',
    foreground = 'steelblue'
)

import Tkinter

class LabelFrame(Tkinter.LabelFrame):
    """Replacement for CCPN stuff that does not allow textcolor ed to be changed
    """

    def __init__( self, parent, *args, **kw ):
        Tkinter.LabelFrame.__init__(self)

        kw.setdefault( 'bg', 'grey90' )
        kw.setdefault( 'relief', 'groove' )

        kw.setdefault( 'padx', 10 )
        kw.setdefault( 'pady', 10 )
#    kw.setdefault( 'borderwidth',    2 )
        kw.setdefault( 'bd', 2 )
        kw.setdefault( 'bg', 'grey90' )

        apply( Tkinter.LabelFrame.__init__, ( self, parent ) + args, kw )

        self.parent = parent
    # end def __init__

    def open( self ):

        if ( hasattr( self.parent, 'open' ) ): # intended use: parent is a BasePopup
            self.parent.open()
        # end if
    # end def open

    def close( self ):

        if ( hasattr( self.parent, 'close' ) ): # intended use: parent is a BasePopup
            self.parent.close()
        # end if
    # end def close

    def setText( self, text ):
        self.configure( text=text )
    # end def setText

    def grid( self, **kw ):
        kw.setdefault( 'padx', 10 )
        kw.setdefault( 'pady', 10 )
        Tkinter.LabelFrame.grid( self, kw )
    # end def grid
# end class LabelFrame

#stdin  = sys.stdin
stdout = sys.stdout
stderr = sys.stderr

class TextPipe:

    def __init__(self,textArea):

        self.textArea = textArea
    # end def __init__

    def write(self, text):

        self.textArea.append(text)
    # end def write

    def flush(self):
        pass
    # end def flush

#end class



class CingGui(BasePopup):

    def __init__(self, parent, options, *args, **kw):


        # Fill in below variable once run generates some results
        self.haveResults = None
        # store the options
        self.options = options

        BasePopup.__init__(self, parent=parent, title='CING Setup', **kw)

#    self.setGeometry(850, 750, 50, 50)

        self.project = None

#    self.tk_strictMotif( True)

        self.updateGui()
    # end def __init__

    def body(self, guiFrame):

        row = 0
        col =0
#    frame = Frame( guiFrame )
#    frame.grid(row=row, column=col, sticky='news')
        self.menuBar = Menu( guiFrame)
        self.menuBar.grid( row=row, column=col, sticky='ew')

        #----------------------------------------------------------------------------------
        # Project frame
        #----------------------------------------------------------------------------------

#    guiFrame.grid_columnconfigure(row, weight=1)
#    frame = LabelFrame(guiFrame, text='Project', font=medFont)
        row = +1
        col =0
        frame = LabelFrame(guiFrame, text='Project', **labelFrameAttributes )
        print '>', frame.keys()
        frame.grid(row=row, column=col, sticky='nsew' )
        frame.grid_columnconfigure(2, weight=1)
#    frame.grid_rowconfigure(0, weight=1)

        srow = 0
        self.projectOptions = ['old','new from PDB','new from CCPN','new from CYANA']
        self.projOptionsSelect = RadioButtons(frame, selected_index=0, entries=self.projectOptions, direction='vertical',
                                              select_callback=self.updateGui
                                             )
        self.projOptionsSelect.grid(row=srow,column=0,rowspan=len(self.projectOptions),columnspan=2, sticky='w')

        if self.options.name: 
            text = self.options.name
        else: 
            text=''
        # end if
        self.projEntry = Entry(frame, bd=1, text=text, returnCallback=self.updateGui)
        self.projEntry.grid(row=srow,column=2,columnspan=2,sticky='ew')
#    self.projEntry.bind('<Key>', self.updateGui)
        self.projEntry.bind('<Leave>', self.updateGui)

        projButton = Button(frame, bd=1,command=self.chooseOldProjectFile, text='browse')
        projButton.grid(row=srow,column=3,sticky='ew')

        srow += 1
        self.pdbEntry = Entry(frame, bd=1, text='')
        self.pdbEntry.grid(row=srow,column=2,sticky='ew')
        self.pdbEntry.bind('<Leave>', self.updateGui)

        pdbButton = Button(frame, bd=1,command=self.choosePdbFile, text='browse')
        pdbButton.grid(row=srow,column=3,sticky='ew')

        srow += 1
        self.ccpnEntry = Entry(frame, bd=1, text='')
        self.ccpnEntry.grid(row=srow,column=2,sticky='ew')
        self.ccpnEntry.bind('<Leave>', self.updateGui)

        ccpnButton = Button(frame, bd=1,command=self.chooseCcpnFile, text='browse')
        ccpnButton.grid(row=srow,column=3,sticky='ew')

        srow += 1
        self.cyanaEntry = Entry(frame, bd=1, text='')
        self.cyanaEntry.grid(row=srow,column=2,sticky='ew')
        self.cyanaEntry.bind('<Leave>', self.updateGui)

        cyanaButton = Button(frame, bd=1,command=self.chooseCyanaFile, text='browse')
        cyanaButton.grid(row=srow,column=3,sticky='ew')

        #Empty row
        srow += 1
        label = Label(frame, text='')
        label.grid(row=srow,column=0,sticky='nw')

        srow += 1
        label = Label(frame, text='Project name:')
        label.grid(row=srow,column=0,sticky='nw')
        self.nameEntry = Entry(frame, bd=1, text='')
        self.nameEntry.grid(row=srow,column=2,sticky='w')

        #Empty row
        srow += 1
        label = Label(frame, text='')
        label.grid(row=srow,column=0,sticky='nw')

        srow += 1
        self.openProjectButton = Button(frame, command=self.openProject, text='Open Project', **actionButtonAttributes )
        self.openProjectButton.grid(row=srow,column=0, columnspan=4, sticky='ew')


        #----------------------------------------------------------------------------------
        # status
        #----------------------------------------------------------------------------------
#    guiFrame.grid_columnconfigure(1, weight=0)
        srow = 0
        frame = LabelFrame(guiFrame, text='Status', **labelFrameAttributes)
        frame.grid( row=srow, column=1, sticky='wnes')
        self.projectStatus = Text(frame, height=11, width=70, borderwidth=0, relief='flat')
        self.projectStatus.grid(row=0, column=0, sticky='wen')

        #Empty row
        srow += 1
        label = Label(frame, text='')
        label.grid(row=srow,column=0,sticky='nw')

        srow += 1
        self.closeProjectButton = Button(frame, command=self.closeProject, text='Close Project', **actionButtonAttributes)
        self.closeProjectButton.grid(row=srow,column=0, columnspan=4, sticky='ew')

        #----------------------------------------------------------------------------------
        # Validate frame
        #----------------------------------------------------------------------------------

        row +=1
        col=0
        frame = LabelFrame(guiFrame, text='Validate', **labelFrameAttributes)
#    frame = LabelFrame(guiFrame, text='Validate', font=medFont)
        frame.grid(row=row, column=col, sticky='nsew')
#    frame.grid_columnconfigure(2, weight=1)
        frame.grid_rowconfigure(0, weight=1)

        srow = 0
#    label = Label(frame, text='validation')
#    label.grid(row=srow,column=0,sticky='nw')
#
#    self.selectDoValidation = CheckButton(frame)
#    self.selectDoValidation.grid(row=srow, column=1,sticky='nw' )
#    self.selectDoValidation.set(True)
#
#    srow += 1
#    label = Label(frame, text='')
#    label.grid(row=srow,column=0,sticky='nw')
#
#    srow += 1
        label = Label(frame, text='checks')
        label.grid(row=srow,column=0,sticky='nw')

        self.selectCheckAssign = CheckButton(frame)
        self.selectCheckAssign.grid(row=srow, column=1,sticky='nw' )
        self.selectCheckAssign.set(True)
        label = Label(frame, text='assignments and shifts')
        label.grid(row=srow,column=2,sticky='nw')


#    srow += 1
#    self.selectCheckQueen = CheckButton(frame)
#    self.selectCheckQueen.grid(row=srow, column=4,sticky='nw' )
#    self.selectCheckQueen.set(False)
#    label = Label(frame, text='QUEEN')
#    label.grid(row=srow,column=5,sticky='nw')
#
#    queenButton = Button(frame, bd=1,command=None, text='setup')
#    queenButton.grid(row=srow,column=6,sticky='ew')


        srow += 1
        self.selectCheckResraint = CheckButton(frame)
        self.selectCheckResraint.grid(row=srow, column=1,sticky='nw' )
        self.selectCheckResraint.set(True)
        label = Label(frame, text='restraints')
        label.grid(row=srow,column=2,sticky='nw')

        srow += 1
        self.selectCheckStructure = CheckButton(frame)
        self.selectCheckStructure.grid(row=srow, column=1,sticky='nw' )
        self.selectCheckStructure.set(True)
        label = Label(frame, text='structural')
        label.grid(row=srow,column=2,sticky='nw')

        srow += 1
        self.selectMakeHtml = CheckButton(frame)
        self.selectMakeHtml.grid(row=srow, column=1,sticky='nw' )
        self.selectMakeHtml.set(True)
        label = Label(frame, text='generate HTML')
        label.grid(row=srow,column=2,sticky='nw')

        srow += 1
        self.selectCheckScript = CheckButton(frame)
        self.selectCheckScript.grid(row=srow, column=1,sticky='nw' )
        self.selectCheckScript.set(False)
        label = Label(frame, text='user script')
        label.grid(row=srow,column=0,sticky='nw')

        self.validScriptEntry = Entry(frame, bd=1, text='')
        self.validScriptEntry.grid(row=srow,column=2,columnspan=3, sticky='ew')

        scriptButton = Button(frame, bd=1,command=self.chooseValidScript, text='browse')
        scriptButton.grid(row=srow,column=5,sticky='ew')

        srow += 1
        label = Label(frame, text='ranges')
        label.grid(row=srow,column=0,sticky='nw')
        self.rangesEntry = Entry( frame, text='' )
        self.rangesEntry.grid( row=srow, column=2, columnspan=3, sticky='ew')

#    self.validScriptEntry = Entry(frame, bd=1, text='')
#    self.validScriptEntry.grid(row=srow,column=3,sticky='ew')
#
#    scriptButton = Button(frame, bd=1,command=self.chooseValidScript, text='browse')
#    scriptButton.grid(row=srow,column=4,sticky='ew')


        srow += 1
        texts    = ['Run Validation','View Results','Setup QUEEN']
        commands = [self.runCing, None, None]
        buttonBar = ButtonList(frame, texts=texts, commands=commands,expands=True)
        buttonBar.grid(row=srow, column=0, columnspan=6, sticky='ew')
        for button in buttonBar.buttons:
            button.config(**actionButtonAttributes)
        # end for
        self.runButton = buttonBar.buttons[0]
        self.viewResultButton = buttonBar.buttons[1]
        self.queenButton = buttonBar.buttons[2]

        #----------------------------------------------------------------------------------
        # Miscellaneous frame
        #----------------------------------------------------------------------------------

        row +=0
        col=1
#    frame = LabelFrame(guiFrame, text='Miscellaneous', font=medFont)
        frame = LabelFrame(guiFrame, text='Miscellaneous', **labelFrameAttributes)
        frame.grid(row=row, column=col, sticky='news')
        frame.grid_columnconfigure(2, weight=1)
        frame.grid_columnconfigure(4, weight=1,minsize=30)
        frame.grid_rowconfigure(0, weight=1)

        # Exports

        srow = 0
        label = Label(frame, text='export to')
        label.grid(row=srow,column=0,sticky='nw')

        self.selectExportXeasy = CheckButton(frame)
        self.selectExportXeasy.grid(row=srow, column=1,sticky='nw' )
        self.selectExportXeasy.set(True)
        label = Label(frame, text='Xeasy, Sparky, TALOS, ...')
        label.grid(row=srow,column=2,sticky='nw')

        srow += 1
        self.selectExportCcpn = CheckButton(frame)
        self.selectExportCcpn.grid(row=srow, column=1,sticky='nw' )
        self.selectExportCcpn.set(True)
        label = Label(frame, text='CCPN')
        label.grid(row=srow,column=2,sticky='nw')

        srow += 1
        self.selectExportQueen = CheckButton(frame)
        self.selectExportQueen.grid(row=srow, column=1,sticky='nw' )
        self.selectExportQueen.set(True)
        label = Label(frame, text='QUEEN')
        label.grid(row=srow,column=2,sticky='nw')

        srow += 1
        self.selectExportRefine = CheckButton(frame)
        self.selectExportRefine.grid(row=srow, column=1,sticky='nw' )
        self.selectExportRefine.set(True)
        label = Label(frame, text='refine')
        label.grid(row=srow,column=2,sticky='nw')

        srow += 1
        label = Label(frame, text='')
        label.grid(row=srow,column=0,sticky='nw')

        # User script

        srow += 1
        label = Label(frame, text='user script')
        label.grid(row=srow,column=0,sticky='nw')

        self.selectMiscScript = CheckButton(frame)
        self.selectMiscScript.grid(row=srow, column=1,sticky='nw' )
        self.selectMiscScript.set(False)

        self.miscScriptEntry = Entry(frame, bd=1, text='')
        self.miscScriptEntry.grid(row=srow,column=3,sticky='ew')

        script2Button = Button(frame, bd=1,command=self.chooseMiscScript, text='browse')
        script2Button.grid(row=srow,column=4,sticky='ew')

        srow += 1
        texts    = ['Export','Run Script']
        commands = [None, None]
        buttonBar = ButtonList(frame, texts=texts, commands=commands,expands=True)
        buttonBar.grid(row=srow, column=0, columnspan=5, sticky='ew')
        for button in buttonBar.buttons:
            button.config(**actionButtonAttributes)
        # end for
        self.exportButton = buttonBar.buttons[0]
        self.scriptButton = buttonBar.buttons[1]

        #----------------------------------------------------------------------------------
        # Textarea
        #----------------------------------------------------------------------------------
        row +=1
        guiFrame.grid_rowconfigure(row, weight=1)
        self.outputTextBox = ScrolledText(guiFrame)
        self.outputTextBox.grid(row=row, column=0, columnspan=2, sticky='nsew')

        self.redirectConsole()

        #----------------------------------------------------------------------------------
        # Buttons
        #----------------------------------------------------------------------------------
        row +=1
        col=0
        texts    = ['Quit', 'Help']
        commands = [self.close, None]
        self.buttonBar = ButtonList(guiFrame, texts=texts, commands=commands,expands=True)
        self.buttonBar.grid(row=row, column=col, columnspan=2, sticky='ew')

#    self.openProjectButton = self.buttonBar.buttons[0]
#    self.closeProjectButton = self.buttonBar.buttons[1]
#    self.runButton = self.buttonBar.buttons[0]
#    self.viewResultButton = self.buttonBar.buttons[1]

        for button in self.buttonBar.buttons:
            button.config(**actionButtonAttributes)
        # end for
    # end def body


    def getGuiOptions(self):

        projectName = self.projEntry.get()

        index = self.projOptionsSelect.getIndex()

        if index > 0:
            makeNewProject = True
            projectImport  = None

            if index > 1:
                i = index-2
                format = ['PDB','CCPN','CYANA'][i]
                file   = [self.pdbEntry, self.ccpnEntry, self.cyanaEntry][i].get()

                if not file:
                    showWarning('Failure','No %s file selected' % format)
                    return
                # end if

                projectImport  = (format, file)
            # end if

        else:
            # Chould also check that any old project file exists

            makeNewProject = False
            projectImport  = None
        # end if

        doValidation = self.selectDoValidation.get()
        checks = []

        if doValidation:
            if self.selectCheckAssign.get():
                checks.append('assignments')
            # end if

            if self.selectCheckResraint.get():
                checks.append('restraints')
            # end if

            if self.selectCheckStructure.get():
                checks.append('structural')
            # end if

            if self.selectMakeHtml.get():
                checks.append('HTML')
            # end if

            if self.selectCheckScript.get():
                script = self.validScriptEntry.get()

                if script:
                    checks.append( ('script',script) )
                # end if
            # end if

            if self.selectCheckQueen.get():
                checks.append('queen')
            # end if
        # end if

        exports = []

        if self.selectExportXeasy.get():
            exports.append('Xeasy')
        # end if

        if self.selectExportCcpn.get():
            exports.append('CCPN')
        # end if

        if self.selectExportQueen.get():
            exports.append('QUEEN')
        # end if

        if self.selectExportRefine.get():
            exports.append('refine')
        # end if

        miscScript = None

        if self.selectMiscScript.get():
            script = self.miscScriptEntry.get()

            if script:
                miscScript = script
            # end if
        # end if

        return projectName, makeNewProject, projectImport, doValidation, checks, exports, miscScript
    # end def getGuiOptions


    def runCing(self):

        options = self.getGuiOptions()

        if options:

            projectName, makeNewProject, projectImport, doValidation, checks, exports, miscScript = options

            print 'Project name:', projectName
            print 'Make new project?', makeNewProject
            print 'Import source:', projectImport
            print 'Do vailidation?', doValidation
            print 'Validation checks:', ','.join(checks)
            print 'Export to:', ','.join(exports)
            print 'User script:', miscScript
        # end if
    # end def runCing

        # else there was already an error message

    def chooseOldProjectFile(self):

        fileTypes = [  FileType('CING', ['project.xml']),
                       FileType('All',  ['*'])
                    ]
        popup = FileSelectPopup(self, file_types = fileTypes,
                                title = 'Select CING project file', dismiss_text = 'Cancel',
                                selected_file_must_exist = True)

        fileName = popup.getFile()
#    dirName  = popup.getDirectory()

        if len(fileName) > 0:
                # Put text into entry,name widgets
            dummy,name = cing.Project.rootPath(fileName)
            self.projEntry.configure(state='normal')
            self.projEntry.set(fileName)

            self.nameEntry.configure(state='normal')
            self.nameEntry.set(name)
            self.nameEntry.configure(state='disabled')
            # choose the correct radiobutton
            self.projOptionsSelect.setIndex(0)
            self.updateGui()
        # end if
        #nd if

        popup.destroy()
    # end def chooseOldProjectFile

    def choosePdbFile(self):

        fileTypes = [ FileType('PDB', ['*.pdb']),  FileType('All', ['*'])]
        popup = FileSelectPopup(self, file_types = fileTypes,
                                title = 'PDB file', dismiss_text = 'Cancel',
                                selected_file_must_exist = True)

        fileName = popup.getFile()
        if len(fileName)>0:
            # Put text into entry widget
            self.pdbEntry.configure(state='normal')
            self.pdbEntry.set(fileName)
            # Put text into name widget
            dir,name,dummy = nTpath( fileName )
            self.nameEntry.configure(state='normal')
            self.nameEntry.set(name)
            # choose the correct radiobutton
            self.projOptionsSelect.setIndex(1)
            self.updateGui()
        #end if

        popup.destroy()
    # end def choosePdbFile


    def chooseCcpnFile(self):

        fileTypes = [  FileType('XML', ['*.xml']), FileType('All', ['*'])]
        popup = FileSelectPopup(self, file_types = fileTypes,
                                title = 'CCPN project XML file', dismiss_text = 'Cancel',
                                selected_file_must_exist = True)

        fileName = popup.getFile()
        if len(fileName)>0:
            self.pdbEntry.configure(state='normal')
            self.pdbEntry.set(fileName)
            self.projOptionsSelect.setIndex(1)

            dir,name,dummy = nTpath( fileName )
            self.nameEntry.set(name)
        #end if
        self.ccpnEntry.set(fileName)
        self.projOptionsSelect.setIndex(2)

        popup.destroy()
    # end def chooseCcpnFile


    def chooseCyanaFile(self):

        # Prepend default Cyana file extension below
        fileTypes = [  FileType('All', ['*']), ]
        popup = FileSelectPopup(self, file_types = fileTypes,
                                title = 'CYANA fproject file', dismiss_text = 'Cancel',
                                selected_file_must_exist = True)

        fileName = popup.getFile()
        self.cyanaEntry.set(fileName)
        self.projOptionsSelect.setIndex(3)

        popup.destroy()
    # end def chooseCyanaFile

    def chooseValidScript(self):

        # Prepend default Cyana file extension below
        fileTypes = [  FileType('All', ['*']), ]
        popup = FileSelectPopup(self, file_types = fileTypes,
                                title = 'Script file', dismiss_text = 'Cancel',
                                selected_file_must_exist = True)

        fileName = popup.getFile()
        self.validScriptEntry.set(fileName)
        popup.destroy()
    # end def chooseValidScript

    def chooseMiscScript(self):

        # Prepend default Cyana file extension below
        fileTypes = [  FileType('All', ['*']), ]
        popup = FileSelectPopup(self, file_types = fileTypes,
                                title = 'Script file', dismiss_text = 'Cancel',
                                selected_file_must_exist = True)

        fileName = popup.getFile()
        self.miscScriptEntry.set(fileName)
        popup.destroy()
    # end def chooseMiscScript

    def openProject(self ):
        projOption = self.projOptionsSelect.get()
        if projOption == self.projectOptions[0]: 
            self.openOldProject()
        elif projOption == self.projectOptions[1]: 
            self.initPdb()
        # end if

        if self.project: 
            self.project.gui = self
        # end if
        self.updateGui()
    #end def

    def openOldProject(self ):
        """

        """
        fName = self.projEntry.get()
        if not os.path.exists( fName ):
            nTerror('Error: file "%s" does not exist\n', fName)
        #end if

        if self.project: 
            self.closeProject()
        # end if
        self.project = cing.Project.open( name=fName, status='old', verbose=False )
    #end def

    def initPdb(self ):
        """

        """
        fName = self.pdbEntry.get()
        if not os.path.exists( fName ):
            nTerror('Error: file "%s" does not exist\n', fName)
        #end if
        self.project = cing.Project.open( self.nameEntry.get(), status='new' )
        self.project.initPDB( pdbFile=fName, convention = 'PDB' )
    #end def

    def closeProject(self):
        if self.project: 
            self.project.close()
        # end if
        self.project = None
        self.updateGui()
    #end def

    def updateGui(self, event=None):

        projOption = self.projOptionsSelect.get()
        buttons = self.buttonBar.buttons

        # Disable entries
        for e in [self.projEntry, self.pdbEntry, self.ccpnEntry, self.cyanaEntry, self.nameEntry]:
            e.configure(state='disabled')
        #end for

        if projOption == self.projectOptions[0]:
            # Enable entries
            self.projEntry.configure(state='normal')

            if (len(self.projEntry.get()) > 0):
                self.openProjectButton.enable()
                self.runButton.enable()
            else:
                self.openProjectButton.disable()
                self.runButton.disable()
            #end if

        elif projOption == self.projectOptions[1]:
            # Enable entries
            self.pdbEntry.configure(state='normal')
            self.nameEntry.configure(state='normal')

            if (len(self.pdbEntry.get()) > 0 and len(self.nameEntry.get())  > 0):
                buttons[0].enable()
                buttons[1].enable()
            else:
                buttons[0].disable()
                buttons[1].disable()
            #end if
        #end if

        elif projOption == self.projectOptions[2]:
            # Enable entries
            self.ccpnEntry.configure(state='normal')
            self.nameEntry.configure(state='normal')

            if (len(self.ccpnEntry.get()) > 0 and len(self.nameEntry.get())  > 0):
                buttons[0].enable()
                buttons[1].enable()
            else:
                buttons[0].disable()
                buttons[1].disable()
            #end if
        #end if

        elif projOption == self.projectOptions[3]:
            # Enable entries
            self.cyanaEntry.configure(state='normal')
            self.nameEntry.configure(state='normal')

            if (len(self.cyanaEntry.get()) > 0 and len(self.nameEntry.get())  > 0):
                buttons[0].enable()
                buttons[1].enable()
            else:
                buttons[0].disable()
                buttons[1].disable()
            #end if
        #end if

        self.projectStatus.clear()
        if not self.project:
            self.projectStatus.setText('No open project')
            self.closeProjectButton.setText('Close Project')
            self.closeProjectButton.disable()
        else:
            self.projectStatus.setText(self.project.format())
            self.closeProjectButton.enable()
            self.closeProjectButton.setText(sprintf('Close Project "%s"', self.project.name))
        #end if
    #end def

    def redirectConsole(self):

        #pipe = TextPipe(self.inputTextBox.text_area)
        #sys.stdin = pipe

        pipe = TextPipe(self.outputTextBox.text_area)
        sys.stdout = pipe
        nTmessage.stream = pipe
    # end def redirectConsole
#    sys.stderr = pipe

    def resetConsole(self):
        #sys.stdin   = stdin
        nTmessage.stream = stdout
        sys.stdout  = stdout
        sys.stderr  = stderr
    # end def resetConsole

    def open(self):

        self.redirectConsole()
        BasePopup.open(self)
    # end def open

    def close(self):

        geometry = self.getGeometry()
        self.resetConsole()
        BasePopup.close(self)

        print 'close:',geometry
        sys.exit(0) # remove later
    # end def close

    def destroy(self):

        geometry = self.getGeometry()
        self.resetConsole()
        BasePopup.destroy(self)

        print 'destroy:',geometry
        sys.exit(0) # remove later
    # end def destroy
# end class CingGui

if __name__ == '__main__':

#  import Tkinter

    root = Tkinter.Tk()

    popup = CingGui(root)
    popup.open()

    root.withdraw()
    root.mainloop()
# end if



# Fails to run yet on JFD machine giving error:
#Model read finished. Duration 7.61048102379
#Model validity check skipped
#Traceback (most recent call last):
#  File "/Users/jd/workspace/cing/python/cing/core/gui.py", line 800, in <module>
#    popup = CingGui(root)
#TypeError: __init__() takes at least 3 arguments (2 given)
