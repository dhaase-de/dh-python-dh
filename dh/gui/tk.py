"""
GUI-related functions for the Tcl/Tk framework.
"""

import tkinter
import tkinter.ttk

# optional image support, only needed for ImageCanvas
try:
    import numpy as np
    import PIL
    import PIL.ImageTk
    import dh.image
except ImportError as e:
    _IMAGECANVAS_ERROR=e
else:
    _IMAGECANVAS_ERROR=None


def fepack(widget, side, fill=tkinter.BOTH, expand=True, **kwargs):
    widget.pack(side=side, fill=fill, expand=expand, **kwargs)


class Application(tkinter.Tk):
    def __init__(self, title=None, minSize=None):
        super().__init__()

        if title is not None:
            self.title(title)

        if minSize is not None:
            self.minsize(*minSize)

        self.initWidgets()

    def initWidgets(self):
        pass

    def run(self):
        self.mainloop()


class ImageButton(tkinter.ttk.Button):
    def __init__(self, master, imageFilename, imageSize=None, **kwargs):
        I = PIL.Image.open(imageFilename)
        if imageSize is not None:
            I = I.resize(imageSize, PIL.Image.ANTIALIAS)
        self.image = PIL.ImageTk.PhotoImage(I)
        super().__init__(master=master, image=self.image, **kwargs)


class Toolbar(tkinter.ttk.Frame):
    def __init__(self, master, imageSize=(32, 32), **kwargs):
        super().__init__(master=master, **kwargs)
        self.imageSize = imageSize
        self.buttons = []

    def addButton(self, iconFilename, **kwargs):
        button = ImageButton(master=self, imageFilename=iconFilename, imageSize=self.imageSize, **kwargs)
        button.pack(side=tkinter.LEFT, fill=tkinter.NONE, expand=False)
        self.buttons.append(button)

    def apack(self):
        """
        Auto-pack this widget.
        """
        self.pack(side=tkinter.TOP, fill=tkinter.X, expand=False)


class StatusBar(tkinter.ttk.Label):
    """
    Status bar label.
    """

    def __init__(self, master, anchor=tkinter.W):
        self.variable = tkinter.StringVar()
        super().__init__(master=master, textvariable=self.variable, anchor=anchor, relief=tkinter.SUNKEN)

    def getText(self):
        return self.variable.get()

    def setText(self, text):
        self.variable.set(text)

    def apack(self):
        self.pack(side=tkinter.BOTTOM, fill=tkinter.X)


class ImageCanvas(tkinter.Canvas):
    """
    Canvas which can display one image represented by a NumPy array.

    The image is always resized to match the canvas size, but keeps the
    original aspect ratio.
    """

    def __init__(self, parent, **kwargs):
        # check if all required modules were imported
        if _IMAGECANVAS_ERROR is not None:
            raise _IMAGECANVAS_ERROR

        # parent class init
        super().__init__(parent, **kwargs)

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
