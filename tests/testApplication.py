# If launched manually, not via unittest or nose
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from utilities import utils3_5 as u



def main(app):
    pass


def testApplication():
    app = u.Application(preserveArgs=True)

    app = u.Application()
    app.parser.add_argument("-r", "--reset", dest='reset', action='store_true',
                        help="Reset the previously acquired information")
    app.parser.add_argument("mandatoryArg1", type=str, help="command to execute a bit more intelligently")
    app.parser.add_argument("mandatoryArg2", type=str, help="Information stored in the following file.")
    app.parser.add_argument("mandatoryArg3", type=str, help="Filename to read")
    app.start()
    main(app)


class testApplication2(object):
    def __init__(self):
        self.app = u.Application(preserveArgs=True)
        self.app = u.Application()
        self.app.start()
        self.main()

    def main(self):
        pass
