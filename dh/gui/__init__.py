"""
GUI-related functions.
"""

import numpy as np
import PIL
import PIL.ImageTk
import tkinter
import tkinter.ttk

import dh.image


class ImageCanvas(tkinter.Canvas):
    """
    Canvas which can display one image represented by a NumPy array.

    The image is always resized to match the canvas size, but keeps the
    original aspect ratio.
    """

    def __init__(self, parent, **kwargs):
        # parent class init
        tkinter.Canvas.__init__(self, parent, **kwargs)

        # object holding the actual image (will be created on the first draw)
        self.canvasImage = None

        # width, height, and scale will always be updated after resizing
        self.width = self.winfo_reqwidth()
        self.height = self.winfo_reqheight()
        self.scale = None
        self.bind("<Configure>", self.onResize)

        # image data (original image, resized image, ...)
        self.imageData = {}

    def onResize(self, event):
        """
        Update size and redraw image.
        """

        self.width = event.width
        self.height = event.height
        self.redraw()

    def redraw(self):
        """
        Redraw the last image, taking the current canvas size into account.
        """

        try:
            self.draw(self.imageData["original"])
        except KeyError:
            pass

    def draw(self, I):
        """
        Draws the image `I` represented by a NumPy array on the canvas.
        """

        # convert to 8 bit NumPy image
        if I.dtype == "uint8":
            J = I.copy()
        elif I.dtype == "uint8":
            J = (I.astype("float32") / 257.0).astype("uint8")
        elif np.issubdtype(I.dtype, "float"):
            J = (I * 255.0).astype("uint8")
        else:
            raise ValueError("Invalid image type '{dtype}'".format(dtype=I.dtype))

        # convert to PIL image
        L = PIL.Image.fromarray(J)

        # resize to fit canvas (but keep original aspect ratio)
        originalImageSize = (I.shape[1], I.shape[0])
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

        # keep original image (for later resizing/redrawing) and a reference to the PhotoImage (to avoid garbage collection)
        self.imageData = {
            "original": I,
            "drawn": P,
        }
