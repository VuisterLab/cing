#@PydevCodeAnalysisIgnore
import sys

from memops.editor.BasePopup import BasePopup

from nijmegen.cing.CingFrame import CingFrame

def testCingPopup(argServer):

  project = argServer.getProject()
  popup = CingPopup(argServer.parent)
  popup.open()


class CingPopup(BasePopup):

  def __init__(self, parent, **kw):

    self.parent = parent

    BasePopup.__init__(self, parent=parent, title='CING Setup', **kw)

  def body(self, guiFrame):

    self.geometry('800x700')

    guiFrame.grid_rowconfigure(0, weight=1)
    guiFrame.grid_columnconfigure(0, weight=1)

    self.frame = CingFrame(guiFrame, self.parent)
    self.frame.grid(row=0, column=0, sticky='nsew')
    self.frame.updateAll()

  def open(self):

    #self.frame.redirectConsole()
    BasePopup.open(self)


  def close(self):

    #self.frame.resetConsole()
    BasePopup.close(self)

    #sys.exit(0) # remove later


  def destroy(self):

    #self.frame.resetConsole()
    BasePopup.destroy(self)

    #sys.exit(0) # remove later


if __name__ == '__main__':

  print "Run testCingPopup() as a CcpNmr Analysis macro"
