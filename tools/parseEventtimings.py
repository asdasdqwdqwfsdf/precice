"""
Parses the format that is generated by the EventTimings framework. Sample input:

# Run finished at Tue Nov 10 15:49:40 2015
# Eventname Count Total Max Min Avg T%
"GLOBAL" 1 2658 2658 2658 2658 100
"M2N::acceptMasterConnection" 1 6 6 6 6 0
"advance" 1 0 0 0 0 0
"initialize" 1 2512 2512 2512 2512 94
"receive global mesh" 1 43 43 43 43 1
"send global mesh" 1 0 0 0 0 0

# Run finished at Tue Nov 10 15:52:40 2015
# Eventname Count Total Max Min Avg T%
"GLOBAL" 1 2666 2666 2666 2666 100
"M2N::requestMasterConnection" 1 12 12 12 12 0
"M2N::requestMasterConnection/Publisher::read" 1 0 0 0 0 0
"advance" 1 2474 2474 2474 2474 92
"initialize" 1 43 43 43 43 1
"receive global mesh" 1 8 8 8 8 0
"send global mesh" 1 0 0 0 0 0

This is converted to a data structure:

[
   {
   "timestamp" : "Time of the run, a python datatime object"
   "global"    : "Global timings, a numpy array
   "data"      : { "name of event"         : "timings as numpy array"
                   "name of another event" : "timings as numpy array" }
   }
]

with one list item for timings of each run.
"""


import locale, shlex, time
import numpy as np

def readBlock(f):
    """ Generator that returns one block at a time, each line as list item. """
    lines = []
    with open(f, "r") as f:
        for line in f:
            l = line.strip()
            if l == "" and len(lines) > 2:
                yield lines
                lines = []
            elif l != "":
                lines.append(l)
        if len(lines):
            yield lines
            
    raise StopIteration()

    
def parseTimings(tStr):
    """ Returns event name and timings as a dict. """
    s = shlex.split(tStr)
    return [s[0], np.array(s[1:])]
    

def parseEventlog(file):
    """ Takes a filename, parses the Eventlog and returns the data. """
    locale.setlocale(locale.LC_TIME, "C") # Set the locale, so that strptime words as intended.

    events = []
    
    for i in readBlock("EventTimings.log"):
        timeStamp = time.strptime(i[0][18:], "%a %b %d %H:%M:%S %Y")
        globalTimings = parseTimings(i[2])

        thisEvent = { s[0] : s[1] for s in map(parseTimings, i[3:]) }
        
        events.append( {
            "timestamp" : timeStamp,
            "global" : globalTimings,
            "data" : thisEvent
        } )

    return events
    
