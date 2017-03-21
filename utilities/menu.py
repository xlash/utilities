import copy
import re
import os
import sys
from utilities import utils


logGod = utils.Logger(__name__)
logger = logGod.logger()

MENU_LENGTH = 80

# Retro compatibility for Python 2.
if utils.pythonVersionMin(majorVersion=2, minorVersion=0, raiseIfNotMet=False,
                          majorVersionMustMatch=True):
    input = raw_input

class Menu(object):
    """
    Example :
        def main(app):
            try:
                logger.debug('ANTSParser starting')
                parser = Parser(app=app)
                while parser.displayMenu and not app.args.is_batchMode:
                    app.menu.items = []
                    app.menu.addItem(description='Modify files= %s'
                                     % (parser.app.settings.fileregex),
                                     callback=parser.setFiles,
                                     returnToMenu=False)
                    app.menu.addItem(description='Modify regexp Filters= %s'
                                     % (parser.app.settings.extractRegexp),
                                     callback=parser.setRegexp,
                                     returnToMenu=False)
                    app.menu.addItem(description='Modify regexp testsCasesName= %s'
                                     % (parser.app.settings.testsCasesName),
                                     callback=parser.setTestcaseFilter,
                                     returnToMenu=False)
                    app.menu.addItem(description='Modify Directory= %s'
                                     % (parser.app.settings.directory),
                                     callback=parser.setDirectory,
                                     returnToMenu=False)
                    app.menu.addItem(description='Export to fileName= %s'
                                     % (parser.app.settings.outFileName),
                                     callback=parser.setOutFileName,
                                     returnToMenu=False)
                    app.menu.addSpacer()
                    app.menu.addItem(description='List tests cases name!', callback=parser.listTC,
                                     returnToMenu=False,
                                     menuSelector='t')
                    app.menu.addItem(description='Run that shit!', callback=parser.run,
                                     returnToMenu=False,
                                     menuSelector='R')
                    app.menu.addSpacer()
                    app.menu.addItem(description='Shitty print it',
                                     callback=parser.export,
                                     kwargs={'exportType': 'print'},
                                     returnToMenu=False,
                                     menuSelector='P')
                    app.menu.addSpacer()
                    app.menu.addItem(description='Load previous settings',
                                     callback=parser.app.loadSettings,
                                     returnToMenu=False,
                                     menuSelector='L')
                    app.menu.addItem(description='Save settings',
                                     callback=parser.app.saveSettings,
                                     returnToMenu=False,
                                     menuSelector='S')
                    app.menu.display(debugLocals=locals())
                    logger.debug('Menu is refreshed')
            except (KeyboardInterrupt, SystemExit):
                raiseOWED_ATTRIBUTES = ['name', 'description', 'prompt', 'initialPrompt',
                                  'app', 'locals', 'stdout', 'quitMessage']
    """

    def __init__(self, **kwargs):
        """
        Supports     ALLOWED_ATTRIBUTES = ['name','description','prompt',
                                           'initialPrompt','app','stdout',
                                           'quitMessage', 'locals']
        """
        self.items = []
        self.spacers = []
        self.name = "Noname"
        self.description = "No description"
        self.initialPrompt = 'Please select an option:'
        self.prompt = 'Please select an other option:'
        self.stdout = sys.stdout
        self.quitMessage = 'Quit'
        self.inputMethod = input
        self.locals = locals
        for key, value in kwargs.items():
            if key in Menu.ALLOWED_ATTRIBUTES:
                setattr(self, key, value)

    def addItem(self, menuItem=None, callback=None,
                description='No description', context=None, **kwargs):
        """
        Supports kwargs    'args',
                           'kwargs',
                           'description',
                           'menuSelector',
                           'returnToMenu'
        """
        if not menuItem and callback:
            menuItem = MenuItem(callback, description, context, **kwargs)
        if not menuItem and not callback:
            raise(MenuItemException("""menuItem or (callback & description)
                                    must be passed at minimal"""))
        # Verify that menuItem menuSelector is unique
        if menuItem.menuSelector:
            for i in self.items:
                if not i:
                    continue
                if i.menuSelector and\
                  (i.menuSelector.lower() == menuItem.menuSelector.lower()):
                    raise MenuItemException('Menu Selector Already used ==> %s. Please change to another letter.'
                                            % (menuItem.menuSelector.lower()))
        try:
            self.items.append(copy.copy(menuItem))
        except:
            if utils.Logger.is_debug():
                logger.exception("""Unable to add this item to this
                                    Menu kwargs=""" % (kwargs))
            else:
                logger.error('Unable to add this item to this Menu kwargs='
                             % (kwargs))

    def addSpacer(self):
        """
        Add a Menu spacer item
        """
        if len(self.items) > 0:
            # Add last iterm as the spacer limit
            self.spacers.append(self.items[-1])

    def display(self, debugLocals=None, inputMethod=None):
        """
        Input values
            inputMethod : Stub for Unittests, to replace input()
            debugLocals : for debug console, overwrite this menu locals()
        return
            returnValues [('selection',
                          MenuItem.description,callbackReturnValue)]
        """
        if debugLocals is None:
            debugLocals = locals()
        o = self.stdout
        if not inputMethod:
            inputMethod = input
        returnValues = []
        while True:
            # Clear screen
            os.system('cls' if os.name == 'nt' else 'clear')
            # FIXME GuillaumeNM Prints weird char [3;J
            o.write("\n%sMENU%s\n" % ('=' * int((MENU_LENGTH - 4) / 2),
                                      '=' * int((MENU_LENGTH - 4) / 2)))
            i = 0
            for item in self.items:
                menuSelector = i
                if item.menuSelector:
                    menuSelector = item.menuSelector
                o.write("%s- %s\n" % (menuSelector, item.description))
                # Add contextual information to menu
                if item.context is not None:
                    for line in str(item.context).splitlines():
                        o.write("\t\t %s\n" % (line)),
                i += 1
                # Display a spacer after this item if in the spacer list.
                for spaceAfterItem in self.spacers:
                    if item == spaceAfterItem:
                        o.write("%s\n" % ("-" * MENU_LENGTH))
            o.write("\n%sDEBUG%s\n" % ('=' * int((MENU_LENGTH - 5) / 2),
                                       '=' * int((MENU_LENGTH - 5) / 2)))
            o.write("d-  Debug \n")
            o.write("dp- .... Debug - Performance\n")
            o.write("dc- .... Python Console - Do not use unless"
                    "you come from Montreal\n")
            o.write("%s\n" % ("-" * MENU_LENGTH))
            o.write("q- %s\n" % (self.quitMessage))
            o.write("%s\n" % ("=" * MENU_LENGTH))
            o.flush()
            try:
                selection = inputMethod(self.initialPrompt)
                selection = selection.lower()
                logger.debug('MENU:: received selection=%s' % (selection))
                item = None
                skipCallback = False
                if re.match(r'\d+', selection):
                    if int(selection) in range(0, i):
                        item = self.items[int(selection)]
                elif selection == 'q':
                    returnValues.append(('q',))
                    raise SystemExit(0)
                elif selection == 'd':
                    utils.Logger.toggle_debug_all(10)
                    skipCallback = True
                elif selection == 'dc':
                    import code
                    skipCallback = True
                    # for live debugging , with local and global namespace.
                    code.interact(local=dict(globals(), **debugLocals))
                else:
                    for i in self.items:
                        if (i.menuSelector and
                           i.menuSelector.lower() == selection.lower()):
                            item = i
            except KeyboardInterrupt:
                print ("\nOh... I asked you what you want,"
                       "and you didn`t answer... :-(")
                stay_in_main_menu = False
                raise
            except SystemExit:
                raise
            except:
                if utils.Logger.is_debug():
                    logger.exception('Unable to pick correct selection.')
                else:
                    logger.error('Unable to pick correct selection.')
            if skipCallback:
                continue
            elif not item:
                logger.warning('Invalid menu option :%s'
                               % (selection))
                continue
            try:
                logger.debug('args=%s kwargs=%s' % (item.args, item.kwargs))
                if item.args == ():
                    returnValues.append((selection.lower(),
                                         item.description,
                                         item.callback(**item.kwargs)))
                else:
                    returnValues.append((selection.lower(),
                                         item.description,
                                         item.callback(args=item.args,
                                                       **item.kwargs)))
            except:
                if utils.Logger.is_debug():
                    logger.exception('Error in callback method=%s of menu =%s'
                                     % (item.callback, item.description))
                else:
                    logger.error('Error in callback method=%s of menuItem =%s'
                                 % (item.callback, item.description))
            if not item.returnToMenu:
                break
        return returnValues


class MenuItem(object):
    """
    This is a Menu Item. It's pretty explicit isn't it?
    Menu selector are case insensitive
    """

    ALLOWED_ATTRIBUTES = ['args', 'kwargs', 'menuSelector', 'returnToMenu']

    def __init__(self, callback, description, context, **kwargs):
        """
         Supports kwargs    'args', 'kwargs','menuSelector','returnToMenu'
        """
        self.callback = callback
        self.args = ()
        self.kwargs = {}
        self.context = context
        self.description = description
        self.menuSelector = None
        self.returnToMenu = False
        for key, value in kwargs.items():
            if key in MenuItem.ALLOWED_ATTRIBUTES:
                setattr(self, key, value)


class MenuItemException(Exception):
    pass
