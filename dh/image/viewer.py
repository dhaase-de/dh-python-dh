import tkinter
import tkinter.ttk

import dh.gui
import dh.image
#import dh.utils


class Viewer():
    def __init__(self):
        pass

    def initGui(self):
        """
        Constructs the main window with all elements.
        """

        self.gui = {}

        # main window
        self.gui["root"] = tkinter.Tk()
        self.gui["root"].minsize(250, 250)

        # image canvas
        self.gui["imageCanvas"] = dh.gui.ImageCanvas(self.gui["root"])
        self.gui["imageCanvas"].pack(fill=tkinter.BOTH, expand=tkinter.YES)

    def runGui(self):
        """
        Enters GUI event loop and returns when the window is destroyed.
        """

        self.gui["root"].mainloop()
        del self.gui

    def view(self, I):
        # construct GUI
        self.initGui()

        self.gui["imageCanvas"].draw(I)

        self.runGui()
