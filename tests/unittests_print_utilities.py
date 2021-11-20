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


class TestPrint(object):
    def  __init__(self, attribute1, attribute2, attribute3, attribute4):
        self.attribute1 = attribute1
        self.attribute2 = attribute2
        self.attribute3 = attribute3
        self.attribute4 = attribute4

obj1 = TestPrint(1,2,3,4)
obj2 = TestPrint('object2.attribute1',2,3,4)
obj3 = TestPrint(1,2,'object3.attribute3',4)
obj4 = TestPrint(1,None,3,'object4.attribute4')

printTable([obj1, obj2, obj3, obj4], ['attribute1', 'attribute2', 'attribute3', 'attribute4'])
