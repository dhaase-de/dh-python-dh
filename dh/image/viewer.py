import tkinter
import tkinter.ttk

import dh.gui.tk
import dh.image
#import dh.utils


##
## basic classes
##


class Viewer():
    def __init__(self):
        self.images = []
        self.n = None
        self.pipeline = Pipeline()
        self.pipeline.add("invert")

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
        return self.pipeline(self.selectedImage())


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
        for node in self.viewer.pipeline.nodes:
            #tkinter.ttk.Button(self.filterFrame, text=filter.name).pack()
            node.gui(parent=self.filterFrame, onChangeCallback=self.updateImage).pack(fill="x", padx=1, pady=1, expand=True)

    def updateImage(self, *args, **kwargs):
        self.imageCanvas.setImage(self.viewer.applyPipeline())


##
## pipeline framework
##


class Pipeline():
    def __init__(self):
        self.nodes = []
        self.add("source")

    def __call__(self, I):
        J = I.copy()
        for node in self.nodes:
            J = node(J)
        return J

    def add(self, node, position=None):
        """
        Inserts processing before the `position`-th slot of the pipeline.
        """

        if position is None:
            position = len(self.nodes)
            
        if isinstance(node, str):
            uid = node
            node = Node.instances[uid]
        self.nodes.insert(position, node)

    def remove(self, position):
        del self.nodes[position]

    def save(self, filename):
        raise NotImplementedError()

    def load(self, filename):
        raise NotImplementedError()


class Node():
    """
    Class for a processing pipeline element (node), which automatically
    registers its instances.
    """

    # keeps references to all instances of this class
    instances = {}

    def __init__(self, uid, description=None, tags=None, f=None, parameters=()):
        # register this instance
        if uid not in type(self).instances:
            type(self).instances[uid] = self
        else:
            raise ValueError("Node with uid '{uid}' is already registered".format(uid=uid))

        # other properties
        self.uid = uid
        self.description = description
        self.tags = tags
        self.f = f
        self.parameters = parameters

    def __call__(self, *args, **kwargs):
        kwargs.update(self.parameterValues())
        return self.f(*args, **kwargs)

    def parameterValues(self):
        return {parameter.name: parameter() for parameter in self.parameters}

    def gui(self, parent, onChangeCallback):
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
        tkinter.ttk.Label(header, text=self.uid, font="Sans 10 bold", anchor = tkinter.W, justify = tkinter.LEFT).pack(side = tkinter.LEFT, fill = "x", expand = True)

        # description line
        #details = tkinter.ttk.Frame(innerFrame)
        #details.pack(side = tkinter.TOP, fill = "x", expand = True)
        #tkinter.ttk.Label(details, text="Bla bla " + self.name, font="Sans 8 italic", anchor = tkinter.W, justify = tkinter.LEFT).pack(side = tkinter.LEFT, fill = "x", expand = True)

        # parameter frame
        parameterFrame = tkinter.ttk.Frame(innerFrame)
        parameterFrame.pack(side = tkinter.TOP, fill = "x", expand = True)
        for (row, parameter) in enumerate(self.parameters):
            (labelFrame, valueFrame) = parameter.gui(parent=parameterFrame, onChangeCallback=onChangeCallback)
            labelFrame.grid(row = row, column = 0, padx = 10, sticky = tkinter.W)
            valueFrame.grid(row = row, column = 1, padx = 10, sticky = tkinter.W)
            
            # parameter label
            #tkinter.ttk.Label(parameterFrame, text=parameter["label"], font="Sans 8", anchor = tkinter.W, justify = tkinter.LEFT).grid(row = row, column = 0, sticky = tkinter.W)

            # checkbox
            #if parameter["type"] == "bool":
            #    # create variable
            #    self.parameterValues[parameter["name"]] = tkinter.IntVar()
            #    element = tkinter.ttk.Checkbutton(parameterFrame, text="", variable = self.parameterValues[parameter["name"]], command = updateCallback)
            #elif parameter["type"] == "list":
            #    self.parameterValues[parameter["name"]] = tkinter.StringVar()
            #    element = tkinter.OptionMenu(parameterFrame, self.parameterValues[parameter["name"]], *parameter["values"], command = updateCallback)
            #    element.config(width = 10)
            #else:
            #    raise ValueError("Invalid filter parameter type {type}".format(parameter["type"]))
            #element.grid(row = row, column = 1, padx = 10, sticky = tkinter.W)

            #tkinter.ttk.Scale(parameterFrame, from_=0, to=100).grid(row = n, column = 1)
            #tkinter.ttk.Button(innerFrame, text=self.name).pack()

        return frame


class NodeParameter():
    def __init__(self, name, label=None):
        self.name = name
        if label is not None:
            self.label = label
        else:
            self.label = name

    def guiLabelFrame(self, parent):
        return tkinter.ttk.Label(parent, text=self.label, font="Sans 8", anchor = tkinter.W, justify = tkinter.LEFT)

    def guiValueFrame(self, parent, onChangeCallback):
        raise NotImplementedError("Use a subclass of 'NodeParameter'")

    def gui(self, parent, onChangeCallback):
        return (
            self.guiLabelFrame(parent=parent),
            self.guiValueFrame(parent=parent, onChangeCallback=onChangeCallback),
        )

    def __call__(self):
        raise NotImplementedError("Use a subclass of 'NodeParameter'")


class BoolNodeParameter(NodeParameter):
    def __init__(self, name, label=None, default=True):
        super().__init__(name=name, label=label)
        self.default = default
        self.variable = None

    def guiValueFrame(self, parent, onChangeCallback):
        self.variable = tkinter.IntVar()
        self.variable.set(self.default)
        return tkinter.ttk.Checkbutton(parent, text="", variable=self.variable, command=onChangeCallback)

    def __call__(self):
        if self.variable is not None:
            return bool(self.variable.get())
        else:
            return None

#class SelectNodeParameter(NodeParameter):
#    def __init__(self, name, label=None, default=True):
#        super().__init__(name=name, label=label, default=default)

   
##
## filters
##


Node(
    uid="source",
    f=lambda I: I,
)

Node(
    uid="invert",
    f=lambda I, enabled: dh.image.invert(I) if enabled else I,
    parameters=[
        BoolNodeParameter(
            name="enabled",
            default=True,
        ),
    ],
)

#Node(
#    uid="normalize",
#    f=lambda I, mode: dh.image.normalize(I, mode=mode),
#    parameters=[
#        BoolNodeParameter(
#            name="enable",
#            default=True,
#        ),
#    ],
#)


#ImageToImageFilter(
#    name="normalize",
#    f=lambda I, mode: dh.image.normalize(I, mode=mode),
#    parameters=[
#        {
#            "name": "mode",
#            "label": "mode",
#            "type": "list",
#            "default": "minmax",
#            "values": ("none", "minmax", "percentile"),
#        },
#    ]
#)
