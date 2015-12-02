import tkinter
import tkinter.ttk

import dh.gui.tk
import dh.image
#import dh.utils


##
## basic classes
##


class _ViewerWindow(dh.gui.tk.Window):
    def __init__(self, viewer):
        super(_ViewerWindow, self).__init__(
            title="Viewer",
            minSize=(250, 250),
        )
        self.viewer = viewer
        self.updateFilterFrame()
        self.updateImage()

    def initWidgets(self):
        # key bindings
        self.bind("<Escape>", lambda _: self.close())
        self.bind("<q>", lambda _: self.close())
        self.bind("<f>", lambda _: print(Filter.instances))

        # main frame
        self.mainFrame = tkinter.ttk.Frame(self)
        self.mainFrame.pack(fill=tkinter.BOTH, expand=tkinter.YES)

        # filter frame
        self.filterFrame = tkinter.ttk.Frame(self.mainFrame)
        self.filterFrame.pack(side=tkinter.LEFT, anchor=tkinter.N)

        # image canvas
        self.imageCanvas = dh.gui.tk.ImageCanvas(self.mainFrame)
        self.imageCanvas.pack(side=tkinter.LEFT, anchor=tkinter.N, fill=tkinter.BOTH, expand=tkinter.YES)

        self.bind("<Left>", lambda _: (self.viewer.prev(), self.updateImage()))
        self.bind("<Right>", lambda _: (self.viewer.next(), self.updateImage()))

    def updateFilterFrame(self):
        for filter in self.viewer.pipeline:
            #tkinter.ttk.Button(self.filterFrame, text=filter.name).pack()
            filter.gui(self.filterFrame).pack(fill="x", expand=True)

    def updateImage(self):
        self.imageCanvas.setImage(self.viewer.applyPipeline())


class Viewer():
    def __init__(self):
        self.images = []
        self.n = None
        self.pipeline = []
        self.pipeline.append(Filter.instances[0])
        self.pipeline.append(Filter.instances[1])
        self.pipeline.append(Filter.instances[2])

    def select(self, n):
        N = len(self.images)
        if N == 0:
            self.n = None
        else:
            self.n = n % N
        return self.n

    def first(self):
        self.select(0)

    def prev(self):
        try:
            self.select(self.n - 1)
        except TypeError:
            pass

    def next(self):
        try:
            self.select(self.n + 1)
        except TypeError:
            pass

    def last(self):
        self.select(-1)

    def add(self, I):
        self.images.append(I.copy())
        self.last()

    def clear(self):
        self.images = []
        self.first()

    def show(self):
        window = _ViewerWindow(self)
        window.show()

    def view(self, I):
        self.add(I)
        self.show()

    def selectedImage(self):
        return self.images[self.n]

    def applyPipeline(self):
        I = self.selectedImage()
        if I is None:
            return None
        else:
            I = I.copy()
        for filter in self.pipeline:
            I = filter.apply(I)
        return I


##
## filters
##


class Filter():
    """
    Base class for viewer filters which automatically registers its instances.
    """

    instances = []

    def __init__(self, name):
        Filter.instances.append(self)
        self.name = name


class ImageToImageFilter(Filter):
    def __init__(self, name, f):
        super(ImageToImageFilter, self).__init__(name)

        self.f = f

    def apply(self, I):
        return self.f(I)

    def gui(self, parent):
        frame = tkinter.ttk.Frame(parent)
        innerFrame = tkinter.ttk.Frame(frame)
        innerFrame.pack(fill="x", expand=True, padx=6, pady=3)
        header = tkinter.ttk.Frame(innerFrame)
        header.pack(side = tkinter.TOP, fill = "x", expand = True)
        tkinter.ttk.Label(header, text=self.name.upper(), font="Sans 10 bold", background = "white", anchor = tkinter.W, justify = tkinter.LEFT).pack(side = tkinter.LEFT, fill = "x", expand = True)

        details = tkinter.ttk.Frame(innerFrame)
        details.pack(side = tkinter.TOP)
        tkinter.ttk.Label(details, text="Bla bla " + self.name, font="Sans 8 italic").pack(side = tkinter.LEFT)

        #tkinter.ttk.Button(innerFrame, text=self.name).pack()
        return frame


ImageToImageFilter(
    name="source",
    f=lambda I: I,
)

ImageToImageFilter(
    name="invert",
    f=lambda I: dh.image.invert(I),
)

ImageToImageFilter(
    name="normalize",
    f=lambda I: dh.image.normalize(I, mode="minmax"),
)
