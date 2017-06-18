"""
Tools for logging.
"""

import abc
import os.path
import pprint

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
#%% logger
###


class PendingLoggerMessage():
    def __init__(self, logger, text):
        self.logger = logger
        self.text = text

    def log(self, logFunc, extraText=""):
        text = self.text
        if extraText is not None:
            text += "\n" + extraText
        logFunc(text)

    def ok(self, *args, **kwargs):
        self.log(self.logger.ok, *args, **kwargs)

    def failed(self, *args, **kwargs):
        self.log(self.logger.failed, *args, **kwargs)


class LoggerFormatter(abc.ABC):
    def __init__(self):
        pass

    def getLevelColor(self, level):
        if level >= Logger.LEVEL_CRITICAL:
            return FG_WHITE + BG_RED
        elif level >= Logger.LEVEL_ERROR:
            return FG_RED + BG_RESET
        elif level >= Logger.LEVEL_WARNING:
            return FG_YELLOW + BG_RESET
        elif level >= Logger.LEVEL_SUCCESS:
            return FG_GREEN + BG_RESET
        elif level >= Logger.LEVEL_INFO:
            return FG_RESET + BG_RESET
        else:
            return FG_CYAN + BG_RESET

    def getLevelName(self, level):
        if level >= Logger.LEVEL_CRITICAL:
            return "CRITICAL"
        elif level >= Logger.LEVEL_ERROR:
            return "ERROR"
        elif level >= Logger.LEVEL_WARNING:
            return "WARNING"
        elif level >= Logger.LEVEL_SUCCESS:
            return "SUCCESS"
        elif level >= Logger.LEVEL_INFO:
            return "INFO"
        else:
            return "DEBUG"

    @abc.abstractmethod
    def apply(self, level):
        """
        Must return a tuple `(pre1, pre2, post1, post2)`.
        """
        pass


class LongLoggerFormatter(LoggerFormatter):
    def apply(self, level):
        # color and level name
        color = self.getLevelColor(level)
        name = self.getLevelName(level)[0]
        dtstr = dh.utils.dtstr(compact=False)

        pre1 = color + "[" + dtstr + "]" + "  " + name + "  "
        pre2 = color + " " * (len(dtstr) + len(name) + 6)
        post1 = FG_RESET + BG_RESET
        post2 = FG_RESET + BG_RESET
        return (pre1, pre2, post1, post2)


class ShortLoggerFormatter(LoggerFormatter):
    def apply(self, level):
        # color and level name
        color = self.getLevelColor(level)
        name = self.getLevelName(level)
        if name == "DEBUG":
            name = "DBUG"
        elif name == "SUCCESS":
            name = " OK "
        elif name == "ERROR":
            name = "FAIL"
        name = name[:4]

        pre1 = FG_RESET + "[" + color + name + FG_RESET + BG_RESET + "]  "
        pre2 = " " * 8
        post1 = FG_RESET + BG_RESET
        post2 = FG_RESET + BG_RESET
        return (pre1, pre2, post1, post2)


class Logger():
    # levels
    LEVEL_DEBUG    = 10
    LEVEL_INFO     = 20
    LEVEL_SUCCESS  = 25
    LEVEL_WARNING  = 30
    LEVEL_ERROR    = 40
    LEVEL_CRITICAL = 50

    def __init__(self, printFormatter="long", filename=None, printMinLevel=None, fileMinLevel=None, fileFormatter=None):
        #if minLevel is not None:
        #    self.setMinLevel(minLevel)
        #else:
        #    self.setMinLevel(Logger.LEVEL_DEBUG)

        if filename is None:
            self.filename = None
        elif isinstance(filename, str):
            if os.path.isdir(filename):
                self.filename = "{}.log".format(dh.utils.dtstr(compact=True))
            else:
                self.filename = filename

        # get formatters for printing and saving
        self.printFormatter = self.getFormatter(printFormatter)
        if fileFormatter is None:
            self.fileFormatter = self.printFormatter
        else:
            self.fileFormatter = self.getFormatter(fileFormatter)

        #self.fileFormat = fileFormat

        #self.colored = colored
        #self.inspect = inspect
        #if self.colored:
        #    cinit()

    #def setMinLevel(self, level):
    #    self.minLevel = level

    @staticmethod
    def getFormatter(formatter):
        if isinstance(formatter, str):
            formatter = formatter.lower()
            if formatter == "long":
                return LongLoggerFormatter()
            elif formatter == "short":
                return ShortLoggerFormatter()
            else:
                raise ValueError("Invalid formatter '{}'".format(formatter))
        elif isinstance(formatter, LoggerFormatter):
            return formatter
        else:
            raise ValueError("Invalid formatter '{}'".format(formatter))

    def log(self, text, level):
        # print log message
        if level >= self.printMinLevel:
            (pre1, pre2, post1, post2) = self.printFormatter.apply(level)
            for (nLine, line) in enumerate(text.splitlines()):
                if nLine == 0:
                    s = pre1 + line + post1
                else:
                    s = pre2 + line + post2
                print(s)

        # write log message to file
        if (self.filename is not None) and (level >= self.fileMinLevel):
            with open(self.filename, "a") as f:
                ### TODO: un-colorize before writing to file
                f.write(s + "\n")

    ###
    #%% basic log types
    ###

    def debug(self, text):
        self.log(text=text, level=Logger.LEVEL_DEBUG)

    def info(self, text):
        self.log(text=text, level=Logger.LEVEL_INFO)

    def success(self, text):
        self.log(text=text, level=Logger.LEVEL_SUCCESS)

    def warning(self, text):
        self.log(text=text, level=Logger.LEVEL_WARNING)

    def error(self, text):
        self.log(text=text, level=Logger.LEVEL_ERROR)

    def critical(self, text):
        self.log(text=text, level=Logger.LEVEL_CRITICAL)

    ###
    #%% aliases
    ###

    def ok(self, text):
        self.success(text=text)

    def fail(self, text):
        self.error(text=text)

    def failed(self, text):
        self.error(text=text)

    ###
    #%% extended log functionality
    ###

    def pending(self, text):
        return PendingLoggerMessage(logger=self, text=text)

    def pprint(self, x, name=None, **kwargs):
        text = pprint.pformat(x, **kwargs)
        if name is not None:
            text = str(name) + " = " + text
        self.debug(text)
