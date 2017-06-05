"""
Tools for logging.
"""

import inspect

import dh.utils
import dh.thirdparty.colorama


###
#%% colorama
###


# foreground colors
FG_RESET   = dh.thirdparty.colorama.Fore.RESET
FG_BLACK   = dh.thirdparty.colorama.Fore.BLACK
FG_RED     = dh.thirdparty.colorama.Fore.RED
FG_GREEN   = dh.thirdparty.colorama.Fore.GREEN
FG_YELLOW  = dh.thirdparty.colorama.Fore.YELLOW
FG_BLUE    = dh.thirdparty.colorama.Fore.BLUE
FG_MAGENTA = dh.thirdparty.colorama.Fore.MAGENTA
FG_CYAN    = dh.thirdparty.colorama.Fore.CYAN
FG_WHITE   = dh.thirdparty.colorama.Fore.WHITE

# background colors
BG_RESET   = dh.thirdparty.colorama.Back.RESET
BG_BLACK   = dh.thirdparty.colorama.Back.BLACK
BG_RED     = dh.thirdparty.colorama.Back.RED
BG_GREEN   = dh.thirdparty.colorama.Back.GREEN
BG_YELLOW  = dh.thirdparty.colorama.Back.YELLOW
BG_BLUE    = dh.thirdparty.colorama.Back.BLUE
BG_MAGENTA = dh.thirdparty.colorama.Back.MAGENTA
BG_CYAN    = dh.thirdparty.colorama.Back.CYAN
BG_WHITE   = dh.thirdparty.colorama.Back.WHITE


def cinit():
    """
    Initialize colorama.
    """
    dh.thirdparty.colorama.init(autoreset=True)


def cdeinit():
    """
    De-initialize colorama.
    """
    dh.thirdparty.colorama.deinit()


###
#%%
###


class Logger():
    LEVEL_DEBUG    = {"value": 10, "name": "DEBUG",    "color": None}
    LEVEL_INFO     = {"value": 20, "name": "INFO",     "color": None}
    LEVEL_WARNING  = {"value": 30, "name": "WARNING",  "color": FG_YELLOW}
    LEVEL_ERROR    = {"value": 40, "name": "ERROR",    "color": FG_RED}
    LEVEL_CRITICAL = {"value": 50, "name": "CRITICAL", "color": FG_WHITE + BG_RED}

    def __init__(self, minLevel=None, colored=True, inspect=True):
        if minLevel is not None:
            self.setMinLevel(minLevel)
        else:
            self.setMinLevel(Logger.LEVEL_DEBUG)
        self.colored = colored
        self.inspect = inspect
        if self.colored:
            cinit()

    def setMinLevel(self, level):
        self.minLevel = level

    def _message(self, text, level):
        # skip if the level is below the min level
        if level["value"] < self.minLevel["value"]:
            return

        # get info about caller
        if self.inspect:
            (_, filename, nLine, _, _, _) = inspect.getouterframes(inspect.currentframe())[2]
        else:
            filename = None
            nLine = None

        # construct and print text
        sPre = "{C}[{D}]  {L}  ".format(
            C=level["color"] if (self.colored and (level["color"] is not None)) else "",
            D=dh.utils.dtstr(compact=False),
            L=level["name"][0],
        )
        sPost = "{I}".format(
            I="  ({}:{})".format(filename, nLine) if self.inspect else "",
        )
        s = sPre + str(text) + sPost
        print(s)

    def debug(self, text):
        self._message(text=text, level=Logger.LEVEL_DEBUG)

    def info(self, text):
        self._message(text=text, level=Logger.LEVEL_INFO)

    def warning(self, text):
        self._message(text=text, level=Logger.LEVEL_WARNING)

    def error(self, text):
        self._message(text=text, level=Logger.LEVEL_ERROR)

    def critical(self, text):
        self._message(text=text, level=Logger.LEVEL_CRITICAL)
