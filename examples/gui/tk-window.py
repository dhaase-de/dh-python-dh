#!/usr/bin/python3

import tkinter
import tkinter.ttk

import dh.data
import dh.gui.tk


###
#%% main
###


class Application(dh.gui.tk.Application):
    def initWidgets(self):
        self.windowFrame = tkinter.ttk.Frame(self)
        self.windowFrame.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)

        ##
        ## menu
        ##

        menuItems = [
            {"label": "Quit", "command": self.destroy},
            {"label": "Print", "command": lambda: print("Hello world!")},
            {"label": "Window", "items": [
                    {"label": "Enter fullscreen", "command": self.enterFullscreen},
                    {"label": "Leave fullscreen", "command": self.leaveFullscreen},
                    None,
                    {"label": "Maximized", "items": [
                            {"label": "on", "command": self.enterMaximized},
                            {"label": "off", "command": self.leaveMaximized},
                        ]
                    },
                ],
            },
            {"label": "No-op"},
        ]
        self.menu = dh.gui.tk.Menu(self, items=menuItems)
        self.menu.apack()

        ##
        ## toolbar
        ##

        def click(n):
            def f():
                self.statusbar.setText("Clicked toolbar button #{}".format(n))
            return f

        self.toolbar = dh.gui.tk.Toolbar(self.windowFrame)
        self.toolbar.addButton(dh.data.ionfn("document"), text="New", compound="top", command=click(1))
        self.toolbar.addButton(dh.data.ionfn("clipboard"), text="Copy", compound="top", command=click(2))
        self.toolbar.addButton(dh.data.ionfn("folder"), text="Open", compound="top", command=click(3))
        self.toolbar.apack()

        ##
        ## frames
        ##

        self.leftFrame = tkinter.ttk.Frame(self.windowFrame)
        dh.gui.tk.fepack(self.leftFrame, "left", expand=False)

        self.radioVar = tkinter.StringVar()
        self.radioVar.set("A")
        self.radioButtons = []
        for value in ("A", "B", "C"):
            radioButton = dh.gui.tk.ImageRadiobutton(self.leftFrame, dh.data.ionfn("document"), imageSize=(32, 32), text=value, compound="left", variable=self.radioVar, value=value, indicatoron=0)
            dh.gui.tk.fepack(radioButton, "top")
            self.radioButtons.append(radioButton)

        self.mainFrame = tkinter.ttk.Frame(self.windowFrame)
        dh.gui.tk.fepack(self.mainFrame, "left")

        self.imageFrame = dh.gui.tk.ImageCanvas(self.mainFrame)
        self.imageFrame.apack()
        I = dh.data.pal()
        self.imageFrame.setImage(I)

        self.rightFrame = tkinter.ttk.Frame(self.windowFrame)
        dh.gui.tk.fepack(self.rightFrame, "left", expand=False)

        ##
        ## status bar
        ##

        self.statusbar = dh.gui.tk.StatusBar(self.windowFrame)
        self.statusbar.apack()
        self.statusbar.setText("Initialized widgets")


def main():
    A = Application("Window Name", (400, 300), True, True)
    A.run()


if __name__ == "__main__":
    main()
