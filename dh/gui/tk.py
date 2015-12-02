"""
GUI-related functions for the Tcl/Tk framework.
"""

import numpy as np
import PIL
import PIL.ImageTk
import tkinter
import tkinter.ttk

import dh.image


class Window(tkinter.Tk):
    def __init__(self, title=None, minSize=None):
        super(Window, self).__init__()

        if title is not None:
            self.title(title)

        if minSize is not None:
            self.minsize(*minSize)

        self.initWidgets()

    def initWidgets(self):
        pass

    def show(self):
        self.mainloop()

    def close(self):
        self.destroy()


class ImageCanvas(tkinter.Canvas):
    """
    Canvas which can display one image represented by a NumPy array.

    The image is always resized to match the canvas size, but keeps the
    original aspect ratio.
    """

    def __init__(self, parent, **kwargs):
        # parent class init
        super(ImageCanvas, self).__init__(parent, **kwargs)

        # object holding the actual image (will be created on the first draw)
        self.canvasImage = None

        # width, height, and scale will always be updated after resizing
        self.width = self.winfo_reqwidth()
        self.height = self.winfo_reqheight()
        self.scale = None
        self.bind("<Configure>", self.onResize)

        # store original and drawn (resized) image
        self.original = None
        self.drawn = None

    def onResize(self, event):
        """
        Save new canvas size and redraw image.
        """

        self.width = event.width
        self.height = event.height
        self.draw()

    def setImage(self, I):
        self.original = I.copy()
        self.draw()

    def draw(self):
        """
        Properly converts and resizes the currently set image and draws it onto
        the canvas.
        """

        # return if no image is set
        if self.original is None:
            return

        # convert to 8 bit NumPy image
        J = dh.image.convert(self.original, "uint8")

        # convert to PIL image
        L = PIL.Image.fromarray(J)

        # resize to fit canvas (but keep original aspect ratio)
        originalImageSize = (self.original.shape[1], self.original.shape[0])
        newCanvasSize = (self.width, self.height)
        scale = np.min(np.array(newCanvasSize) / np.array(originalImageSize))
        newImageSize = dh.image.tir(scale * np.array(originalImageSize))
        L = L.resize(newImageSize)
        self.scale = newImageSize[0] / originalImageSize[0]

        # convert to PhotoImage
        P = PIL.ImageTk.PhotoImage(L)

        # draw PhotoImage
        if self.canvasImage is None:
            self.canvasImage = self.create_image(0, 0, anchor=tkinter.NW, image=P)
        else:
            self.itemconfig(self.canvasImage, image=P)

        # keep reference to the PhotoImage to avoid garbage collection
        self.drawn = P
