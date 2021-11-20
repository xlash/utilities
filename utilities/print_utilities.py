import sys
from pprint import pprint, pformat

import logging
logger = logging.getLogger()


def printTable(arrOfDict, colList=None, streamhandler=sys.stdout, width=240, compact=True):
    """
    Pretty print a list of dictionaries (arrOfDict) as a dynamically sized table.
    If column names (colList) aren't specified, they will show in random order.
    Author: Thierry Husson - Use it as you want but don't blame me.
            Modified, enhanced, pimped up by GNM
    
    arrOfDict :: list of dicts

    colList :: array of string
        Will print only the following keys from the dictionairies in arrOfDict
        ==>if colList is [], will print a list of columns name. Returns nothing.

    streamhandler :: stream object for output. Defaults to sys.stdout

    width :: default print width (if you want to avoid multiline splits, put this high)

    Returns :
        Nothing
    """
    if not isinstance(arrOfDict, list):
        raise TypeError("arrOfDict is not a list")
    i = 0
    for line in arrOfDict:
        i += 1
        if not isinstance(line, dict):
            raise TypeError("line %s is not a dict" % (i))
    if len(arrOfDict) == 0:
        return
    printColList = colList == []
    # Define headers
    # Bug-2018-09-2 headers loses order
    # u.printTable([{'a':True},{'a':False,'betwertertgerterg':2819738964987326423804}])
    # 'betwertertgerterg      | a    '
    # '---------------------- | -----'
    # '                       | True '
    # '2819738964987326423804 | False'

    if not colList or colList == []:
        for i in arrOfDict:
            newColList = list(i.keys())
            # Keep unique values
            if not colList:
                colList = newColList
            elif colList != newColList:
                colList = list(set(newColList + colList))
    if printColList:
        pprint(colList, stream=streamhandler, width=width)
        return

    # 1st row = header
    myList = [colList]
    for item in arrOfDict:
        if compact:
            # Calculate number of line maximum for columns
            maxLine = 1
            for col in colList:
                try:
                    x = pformat(item[col]).splitlines()
                    # Avoiding ternary operator for Python <2.5 compatibility
                    if len(x) > maxLine:
                        maxLine = len(x)
                except Exception:
                    pass
            # Print each column's lines
            for i in range(0, maxLine):
                itemToAdd = []
                for col in colList:
                    if col not in colList:
                        # Display empty on the middle column Line. A 5 maximum line column, should display on the 3rd.
                        if i == round(maxLine/2) + 1:
                            itemToAdd.append('---')
                        else:
                            itemToAdd.append('')
                    else:
                        try:
                            x = pformat(item[col]).splitlines()
                            if len(x) > i:
                                itemToAdd.append(x[i])
                            else:
                                itemToAdd.append('')
                        except Exception:
                            # Display empty on the middle column Line. A 5 maximum line column, should display on the 3rd.
                            if i == round(maxLine/2) + 1:
                                itemToAdd.append('=ERR=')
                            else:
                                itemToAdd.append('')
                myList.append(itemToAdd)
        else:
            itemToAdd = []
            for col in colList:
                try:
                    itemToAdd.append(str(item[col] or ''))
                except Exception:
                    itemToAdd.append('---')
            myList.append(itemToAdd)
    if len(myList) == 0:
        return
    colSize = [max(map(len, col)) for col in zip(*myList)]
    formatStr = ' | '.join(["{{:<{}}}".format(i) for i in colSize])
    # Seperating line
    myList.insert(1, ['-' * i for i in colSize])
    for item in myList:
        pprint(formatStr.format(*item), stream=streamhandler, width=width)
