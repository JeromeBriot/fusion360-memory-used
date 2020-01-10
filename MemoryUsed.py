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

process = []

mem_min = 10000000000000000000
mem_max = 0

handlers = []
stopFlag = None
myCustomEvent = 'MyCustomEventId'
customEvent = None

this_addin_name = 'MemoryUsed'
this_addin_version = '0.4.0'
this_addin_author = 'Jerome Briot'
this_addin_contact = 'jbtechlab@gmail.com'

# The event handler that responds to the custom event being fired.
class ThreadEventHandler(adsk.core.CustomEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        global palette
        global process
        global mem_max, mem_min
        global customEvent, handlers, stopFlag, app, myCustomEvent

        try:

            meminfo = process.memory_full_info()

            if (meminfo.uss < mem_min):
                mem_min = meminfo.uss

            if (meminfo.uss > mem_max):
                mem_max = meminfo.uss

            if palette:
                #TODO check returned value
                palette.sendInfoToHTML('send','{{"uss":{}, "min":{}, "max":{}}}'.format(meminfo.uss, mem_min, mem_max))

        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()), this_addin_name, 0, 0)

            if handlers.count:
                customEvent.remove(handlers[0])
            stopFlag.set()
            app.unregisterCustomEvent(myCustomEvent)


# The class for the new thread.
class MyThread(threading.Thread):
    def __init__(self, event):
        threading.Thread.__init__(self)
        self.stopped = event

    def run(self):
        global app, palette

        # Every second fire a custom event, passing a random number.
        while not self.stopped.wait(1):
            app.fireCustomEvent(myCustomEvent)

# Event handler for the commandExecuted event.
class ShowPaletteCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        global palette, ui
        try:

            cmdDef = ui.commandDefinitions.itemById('showMemoryMonitor')
            if palette.isVisible:
                palette.isVisible = False
                ctrl.commandDefinition.name = 'Show memory monitor'
                cmdDef.name = 'Show memory monitor'
            else:
                palette.isVisible = True
                ctrl.commandDefinition.name = 'Hide memory monitor'
                cmdDef.name = 'Hide memory monitor'

        except:
            ui.messageBox('Command executed failed: {}'.format(traceback.format_exc()), this_addin_name, 0, 0)

# Event handler for the commandCreated event.
class ShowPaletteCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            command = args.command
            onExecute = ShowPaletteCommandExecuteHandler()
            command.execute.add(onExecute)
            handlers.append(onExecute)
        except:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()), this_addin_name, 0, 0)

def run(context):

    global ui, app, palette, ctrl
    global process
    global customEvent, stopFlag

    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        qatRToolbar = ui.toolbars.itemById('QATRight')

        showPaletteCmdDef = ui.commandDefinitions.addButtonDefinition('showMemoryMonitor', 'Show memory monitor', 'Display memory used by Fusion 360', './resources')

        # Connect to Command Created event.
        onCommandCreated = ShowPaletteCommandCreatedHandler()
        showPaletteCmdDef.commandCreated.add(onCommandCreated)
        handlers.append(onCommandCreated)

        ctrl = qatRToolbar.controls.addCommand(showPaletteCmdDef, 'HealthStatusCommand', False)

        palette = ui.palettes.add('MemoryUsedPalette', 'Memory used', 'MUPalette.html', False, True, True, 300, 215)
        palette.setPosition(400,400)
        palette.isVisible = False

        process = psutil.Process()

        # Register the custom event and connect the handler.
        customEvent = app.registerCustomEvent(myCustomEvent)
        onThreadEvent = ThreadEventHandler()
        customEvent.add(onThreadEvent)
        handlers.append(onThreadEvent)

        # Create a new thread for the other processing.
        stopFlag = threading.Event()
        myThread = MyThread(stopFlag)
        myThread.start()

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()), this_addin_name, 0, 0)


def stop(context):

    global palette

    try:
        if handlers.count:
            customEvent.remove(handlers[0])
        stopFlag.set()
        app.unregisterCustomEvent(myCustomEvent)

        cmdDef = ui.commandDefinitions.itemById('showMemoryMonitor')
        if cmdDef:
            cmdDef.deleteMe()

        qatRToolbar = ui.toolbars.itemById('QATRight')
        cmd = qatRToolbar.controls.itemById('showMemoryMonitor')
        if cmd:
            cmd.deleteMe()

        palette = ui.palettes.itemById('MemoryUsedPalette')
        if palette:
            palette.deleteMe()

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()), this_addin_name, 0, 0)