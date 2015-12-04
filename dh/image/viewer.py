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
        self.filterFrame.pack(side=tkinter.LEFT, anchor=tkinter.N, padx=2, pady=2)

        # image canvas
        self.imageCanvas = dh.gui.tk.ImageCanvas(self.mainFrame)
        self.imageCanvas.pack(side=tkinter.LEFT, anchor=tkinter.N, fill=tkinter.BOTH, expand=tkinter.YES)

        self.bind("<Left>", lambda _: (self.viewer.prev(), self.updateImage()))
        self.bind("<Right>", lambda _: (self.viewer.next(), self.updateImage()))

    def updateFilterFrame(self):
        for filter in self.viewer.pipeline:
            #tkinter.ttk.Button(self.filterFrame, text=filter.name).pack()
            filter.gui(self.filterFrame, self.updateImage).pack(fill="x", padx=1, pady=1, expand=True)

    def updateImage(self, *args, **kwargs):
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
## filter framework
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
    def __init__(self, name, f, parameters = ()):
        super(ImageToImageFilter, self).__init__(name)

        self.f = f
        self.parameters = parameters
        self.parameterValues = {}

    def apply(self, I):
        return self.f(I, **self.getParameterValues())

    def getParameterValues(self):
        return {parameter["name"]: self.parameterValues[parameter["name"]].get() for parameter in self.parameters}

    def gui(self, parent, updateCallback):
        """
        Constructs and returns a GUI frame for this filter.
        """

        # master frame
        frame = tkinter.ttk.Frame(parent, relief="raised")

        # usable part of the frame
        innerFrame = tkinter.ttk.Frame(frame)
        innerFrame.pack(fill="x", expand=True, padx=6, pady=3)

        # header line
        header = tkinter.ttk.Frame(innerFrame)
        header.pack(side = tkinter.TOP, fill = "x", expand = True)
        tkinter.ttk.Label(header, text=self.name.upper(), font="Sans 10 bold", anchor = tkinter.W, justify = tkinter.LEFT).pack(side = tkinter.LEFT, fill = "x", expand = True)

        # description line
        #details = tkinter.ttk.Frame(innerFrame)
        #details.pack(side = tkinter.TOP, fill = "x", expand = True)
        #tkinter.ttk.Label(details, text="Bla bla " + self.name, font="Sans 8 italic", anchor = tkinter.W, justify = tkinter.LEFT).pack(side = tkinter.LEFT, fill = "x", expand = True)

        # parameter frame
        parameterFrame = tkinter.ttk.Frame(innerFrame)
        parameterFrame.pack(side = tkinter.TOP, fill = "x", expand = True)
        for (row, parameter) in enumerate(self.parameters):
            # parameter label
            tkinter.ttk.Label(parameterFrame, text=parameter["label"], font="Sans 8", anchor = tkinter.W, justify = tkinter.LEFT).grid(row = row, column = 0, sticky = tkinter.W)

            # checkbox
            if parameter["type"] == "bool":
                # create variable
                self.parameterValues[parameter["name"]] = tkinter.IntVar()
                element = tkinter.ttk.Checkbutton(parameterFrame, text="", variable = self.parameterValues[parameter["name"]], command = updateCallback)
            elif parameter["type"] == "list":
                self.parameterValues[parameter["name"]] = tkinter.StringVar()
                element = tkinter.OptionMenu(parameterFrame, self.parameterValues[parameter["name"]], *parameter["values"], command = updateCallback)
                element.config(width = 10)
            else:
                raise ValueError("Invalid filter parameter type {type}".format(parameter["type"]))
            element.grid(row = row, column = 1, padx = 10, sticky = tkinter.W)

            # set default value for parameter variable
            if "default" in parameter.keys():
                self.parameterValues[parameter["name"]].set(parameter["default"])

            #tkinter.ttk.Scale(parameterFrame, from_=0, to=100).grid(row = n, column = 1)
            #tkinter.ttk.Button(innerFrame, text=self.name).pack()

        return frame


##
## filters
##


ImageToImageFilter(
    name="source",
    f=lambda I: I,
)

ImageToImageFilter(
    name="invert",
    f=lambda I, enabled: dh.image.invert(I) if enabled else I,
    parameters=[
        {
            "name": "enabled",
            "label": "enabled",
            "type": "bool",
            "default": True,
        },
    ]
)

ImageToImageFilter(
    name="normalize",
    f=lambda I, mode: dh.image.normalize(I, mode=mode),
    parameters=[
        {
            "name": "mode",
            "label": "mode",
            "type": "list",
            "default": "minmax",
            "values": ("none", "minmax", "percentile"),
        },
    ]
)
