import sys
import tempfile
import fnmatch
import os
import shutil
import signal
import json
from utilities.application import *


django = None
# This file requires at least python 2.5
if sys.version_info[0] != 2 or sys.version_info[1] < 5:
    # "This script requires Python version 2.5"
    raise Exception("Requires Python 2.5+ to load utils2_5.py")

try:
    import django
    from django.template import Template, Context
    from django.conf import settings
    # We have to do this to use django templates standalone - see
    # http://stackoverflow.com/questions/98135/how-do-i-use-django-templates-without-the-rest-of-django
    settings.configure(
        TEMPLATE_DEBUG=True,
        TEMPLATE_DIRS=(
            '',
        ),
        TEMPLATE_LOADERS=('django.template.loaders.filesystem.Loader',)
    )
    django.setup()
except:
    # Might have already been configured.
    pass


def template(myTemplate, myDict):
    """
    Will use Django templating system to apply the myDict context
    to myTemplate
    Currenlty being used by AutomaticNetworkTesting
    """
    if not django:
        raise Exception('Django module required for utils2_5::template method')
    if not isinstance(myTemplate, str) or myTemplate == '':
        raise Exception('myTemplate must be str and not empty')
    if not isinstance(myDict, dict) or myDict == {}:
        raise Exception('myDict must be dict and not empty')
    t = Template(myTemplate)
    c = Context(myDict)
    return t.render(c)


def replace(file_path, pattern, subst):
    # Create temp file
    fh, abs_path = tempfile.mkstemp()
    with open(abs_path, 'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                new_file.write(line.replace(pattern, subst))
    os.close(fh)
    # Remove original file
    os.remove(file_path)
    # Move new file
    shutil.move(abs_path, file_path)


def parse_alerting_parameters(alerting_string):
    """
    related to SMARTS alerting parse Alerting system string into hash.
    Or string can be a single number representing severity.
    """
    # JSON does not support single quotes for object attributes and names
    alerting_string = alerting_string.replace('\'', '"')
    try:
        if alerting_string.count('{') > 0:
            attributes = json.loads(alerting_string)
        else:
            attributes = {'severity': alerting_string}
    except:
        attributes = {'severity': alerting_string}
    return attributes


class timeout:
    """
    Non-multithreaded / processes method with_statement:
    http://stackoverflow.com/questions/2281850/
    timeout-function-if-it-takes-too-long-to-finish
    """
    def __init__(self, seconds=1, error_message='Timeout'):
        self.seconds = seconds
        self.error_message = error_message

    def handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)

    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)

    def __exit__(self, type, value, traceback):
        signal.alarm(0)


class TimeoutError(Exception):
    pass


class Ignore(object):
    """
    Class for ignore filesname based on gitignore
    format or pattern list
    """
    ignorePatternLists = []

    def __init__(self, strOrFileName):
        self.__class__.load(strOrFileName)

    @classmethod
    def isAllowed(cls, fileName):
        """
        Verify if filename should be ignored or not.
        Ala .gitignore
        http://stackoverflow.com/questions/25229592/python-how-to-implement-something-like-gitignore-behavior
        """
        for ignorePattern in cls.ignorePatternLists:
            try:
                # Whitelisting
                # if ignorePattern[0] == '!':
                #     if fnmatch(self.filename, ignorePattern)]:
                #         return True
                # else:
                if fnmatch.fnmatch(fileName, ignorePattern):
                    return False
            except Exception:
                print('ERROR::Problem with Ignorename filter=%s on file=%s'
                      % (ignorePattern, fileName))
        return True

    @classmethod
    def isIgnored(cls, fileName):
        return not cls.isAllowed(fileName)

    @classmethod
    def load(cls, strOrFileName):
        """
        use to find a list of patterns for ignoring files.
        Similar to .gitignore format
        """
        ignorePatternList = []
        ignorePatternListCandidate = []
        try:
            ignore = os.path.abspath(str(strOrFileName))
            if os.path.isfile(ignore):
                with open(ignore) as o:
                    ignorePatternListCandidate = o.read().splitlines()
        except Exception:
            try:
                ignorePatternListCandidate = str(strOrFileName).split(',')
            except Exception:
                raise Exception('GitIgnoreFileLoad: strOrFileName is neither a .gitignore type like file nor exclusion list')
        ignorePatternListCandidate
        for pattern in ignorePatternListCandidate:
            if len(pattern) > 0 and pattern[0] not in ['#', ' ', '!']:
                ignorePatternList.append(pattern)

        # Assigns to cls
        cls.ignorePatternLists = ignorePatternList