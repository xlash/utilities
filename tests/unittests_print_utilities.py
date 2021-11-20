import os
import sys
import unittest
# If launched manually, not via unittest or nose
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.append(os.path.abspath(os.path.dirname(__file__)))


a = {'attribute1':1}
b = {'attribute2':1}
c = {'attribute3':1}

d = {'attribute1':1, 'attribute2':'dddddddddd', 'attribute4': None }
e = {'attribute1':1, 'attribute2':'dddddddddd', 'attribute3':'Very long phrase.....................................up to here'}

from utilities.print_utilities import printTable

printTable([a,b,c,d,e], ['attribute1', 'attribute2', 'attribute3', 'attribute4'])