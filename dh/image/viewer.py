import tkinter
import tkinter.ttk

import dh.gui.tk
import dh.image
#import dh.utils


class _ViewerWindow(dh.gui.tk.Window):
    def __init__(self):
        super(_ViewerWindow, self).__init__(
            title="Viewer",
            minSize=(250, 250),
        )

    def initWidgets(self):
        # key bindings
        self.bind("<Escape>", lambda _: self.close())
        self.bind("<q>", lambda _: self.close())

        # main frame
        self.mainFrame = tkinter.ttk.Frame(self)
        self.mainFrame.pack(fill=tkinter.BOTH, expand=tkinter.YES)

        # filter frame
        self.filterFrame = tkinter.ttk.Frame(self.mainFrame)
        self.filterFrame.pack(side=tkinter.LEFT, anchor=tkinter.N, padx = 10, pady = 10)
        tkinter.ttk.Button(self.filterFrame, text="+").pack()

        # image canvas
        self.imageCanvas = dh.gui.tk.ImageCanvas(self.mainFrame)
        self.imageCanvas.pack(side=tkinter.LEFT, anchor=tkinter.N, fill=tkinter.BOTH, expand=tkinter.YES)

    def draw(self, I):
        self.imageCanvas.draw(I)


class Viewer():
    def __init__(self):
        self.gui = None

    def initGui(self):
        """
        Constructs the main window with all elements.
        """

        # main window
        self.gui = _ViewerWindow()

    def showGui(self):
        """
        Enters GUI event loop and returns when the window is destroyed.
        """

        self.gui.show()
        del self.gui

    def view(self, I):
        self.initGui()
        self.gui.draw(I)
        self.showGui()

    def close(self):
        self.gui.close()
