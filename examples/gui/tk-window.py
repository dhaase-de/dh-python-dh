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

        self.toolbar = dh.gui.tk.Toolbar(self.windowFrame)
        self.toolbar.addButton(dh.data.ionfn("document"), command=self.destroy)
        self.toolbar.addButton(dh.data.ionfn("clipboard"), command=self.destroy)
        self.toolbar.addButton(dh.data.ionfn("folder"), command=self.destroy)
        self.toolbar.apack()

        self.mainFrame = tkinter.ttk.Frame(self.windowFrame)
        dh.gui.tk.fepack(self.mainFrame, "top")

        self.statusbar = dh.gui.tk.StatusBar(self.windowFrame)
        self.statusbar.apack()
        self.statusbar.setText("Initialized widgets")


def main():
    A = Application("Window Name", (400, 300))
    A.run()


if __name__ == "__main__":
    main()
