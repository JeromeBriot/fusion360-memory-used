#Author-Jerome Briot
#Description-Display memory used by Fusion 360

import adsk.core, adsk.fusion, adsk.cam, traceback
import threading
import platform

if platform.system()=='Windows':
    from .Modules import psutil_win as psutil
else:
    from .Modules import psutil_mac as psutil

app = adsk.core.Application.cast(None)
ui = adsk.core.UserInterface.cast(None)
palette = adsk.core.Palette.cast(None)
ctrl = adsk.core.CommandControl.cast(None)

process = None

memoryMin = 10000000000000000000
memoryMax = 0

handlers = []
stopFlag = None
myCustomEvent = 'MyCustomEventId'
customEvent = None

thisAddinName = 'MemoryUsed'
thisAddinVersion = '0.5.0'
thisAddinAuthor = 'Jerome Briot'
thisAddinContact = 'jbtechlab@gmail.com'


class ThreadEventHandler(adsk.core.CustomEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):

        global memoryMax, memoryMin

        try:

            meminfo = process.memory_full_info()

            if (meminfo.uss < memoryMin):
                memoryMin = meminfo.uss

            if (meminfo.uss > memoryMax):
                memoryMax = meminfo.uss

            palette = ui.palettes.itemById(thisAddinName + 'Palette')

            if palette:
                palette.sendInfoToHTML('send','{{"uss":{}, "min":{}, "max":{}}}'.format(meminfo.uss, memoryMin, memoryMax))

        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()), thisAddinName, 0, 0)


class MyThread(threading.Thread):
    def __init__(self, event):
        threading.Thread.__init__(self)
        self.stopped = event

    def run(self):

        while not self.stopped.wait(1):
            app.fireCustomEvent(myCustomEvent)


class ShowPaletteCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):

        try:

            palette = ui.palettes.itemById(thisAddinName + 'Palette')
            if not palette:
                palette = ui.palettes.add(thisAddinName + 'Palette', 'Memory used', 'MUPalette.html', True, True, True, 300, 215)
            else:
                palette.isVisible = True

        except:
            ui.messageBox('Command executed failed: {}'.format(traceback.format_exc()), thisAddinName, 0, 0)


class ShowPaletteCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        global handlers
        try:
            command = args.command
            onExecute = ShowPaletteCommandExecuteHandler()
            command.execute.add(onExecute)
            handlers.append(onExecute)
        except:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()), thisAddinName, 0, 0)

def run(context):

    global ui, app, ctrl
    global process
    global customEvent, stopFlag

    ui = None

    try:

        app = adsk.core.Application.get()
        ui  = app.userInterface

        customEvent = app.registerCustomEvent(myCustomEvent)
        onThreadEvent = ThreadEventHandler()
        customEvent.add(onThreadEvent)
        handlers.append(onThreadEvent)

        stopFlag = threading.Event()
        myThread = MyThread(stopFlag)
        myThread.start()

        qatRToolbar = ui.toolbars.itemById('QATRight')

        showPaletteCmdDef = ui.commandDefinitions.addButtonDefinition('showMemoryUsed', 'Memory used', 'Display memory used by Fusion 360', './resources')

        onCommandCreated = ShowPaletteCommandCreatedHandler()
        showPaletteCmdDef.commandCreated.add(onCommandCreated)
        handlers.append(onCommandCreated)

        ctrl = qatRToolbar.controls.addCommand(showPaletteCmdDef, 'HealthStatusCommand', False)

        process = psutil.Process()

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()), thisAddinName, 0, 0)


def stop(context):

    try:

        palette = ui.palettes.itemById(thisAddinName + 'Palette')
        if palette:
            palette.deleteMe()

        if handlers.count:
            customEvent.remove(handlers[0])
        stopFlag.set()
        app.unregisterCustomEvent(myCustomEvent)

        cmdDef = ui.commandDefinitions.itemById('showMemoryUsed')
        if cmdDef:
            cmdDef.deleteMe()

        qatRToolbar = ui.toolbars.itemById('QATRight')
        cmd = qatRToolbar.controls.itemById('showMemoryUsed')
        if cmd:
            cmd.deleteMe()

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()), thisAddinName, 0, 0)
