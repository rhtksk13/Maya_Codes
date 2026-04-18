import maya.OpenMaya as om
import maya.OpenMayaMPx as ompx
import maya.cmds as cmds
import sys

"""
- Requirements:

    1. Start Joint
    2. Mid Joint
    3. End Joint
    4. Calculation
    5. A locator created at the position for poleVector
"""
cmdName = "findPoleVector"
kStartFlag = "-sj"
kStartLongFlag = "-startJoint"

kMidFlag = "-mj"
kMidLongFlag = "-midJoint"

kEndFlag = "-ej"
kEndLongFlag = "-endJoint"

kHelpFlag = "-h"
kHelpLongFlag = "-help"

message = "This command helps in finding the position for Pole Vector to be placed provided three joints of a 3 chain setup."
kSuccess = 1
kFail = 0

class poleVector(ompx.MPxCommand):
    startSparse = None
    midSparse = None
    endSparse = None

    def __init__(self):
        ompx.MPxCommand.__init__(self)

    def argumentParse(self, argList):
        syntax = self.syntax()
        mArgDataBase = om.MArgDatabase(syntax, argList)

        if mArgDataBase.isFlagSet(kStartFlag):
            self.startSparse = mArgDataBase.flagArgumentString(kStartFlag, 0)
        if mArgDataBase.isFlagSet(kStartLongFlag):
            self.startSparse = mArgDataBase.flagArgumentString(kStartLongFlag, 0)
        if mArgDataBase.isFlagSet(kMidFlag):
            self.midSparse = mArgDataBase.flagArgumentString(kMidFlag, 0)
        if mArgDataBase.isFlagSet(kMidLongFlag):
            self.midSparse = mArgDataBase.flagArgumentString(kMidLongFlag, 0)
        if mArgDataBase.isFlagSet(kEndFlag):
            self.endSparse = mArgDataBase.flagArgumentString(kEndFlag, 0)
        if mArgDataBase.isFlagSet(kEndLongFlag):
            self.endSparse = mArgDataBase.flagArgumentString(kEndLongFlag, 0)
        if mArgDataBase.isFlagSet(kHelpFlag):
            self.setResult(message)
        if mArgDataBase.isFlagSet(kHelpLongFlag):
            self.setResult(message)

    def redoIt(self):
        startpos = cmds.xform(self.startSparse, q = True, rp = True, ws = True)
        startVector = om.MVector(startpos[0], startpos[1], startpos[2])
        #startVector = cmds.xform(self.startSparse, q = True, t = True, ws = True)
        midPos = cmds.xform(self.midSparse, q = True, rp = True, ws = True)
        midVector = om.MVector(midPos[0], midPos[1], midPos[2])
        #startVector = cmds.xform(self.midSparse, q = True, t = True, ws = True)
        endPos = cmds.xform(self.endSparse, q = True, rp = True, ws = True)
        endVector = om.MVector(endPos[0], endPos[1], endPos[2])
        #startVector = cmds.xform(self.endSparse, q = True, t = True, ws = True)

        midPointVector = om.MVector()
        midPointVector = (startVector + endVector) / 2

        directionVector = om.MVector()
        directionVector = midVector - midPointVector

        destVector = om.MVector()
        destVector = midPointVector + (directionVector * 4)

        polelocator = cmds.spaceLocator(n = "Pole_Vector_position_Loc")
        cmds.xform(polelocator, t = (destVector.x, destVector.y, destVector.z), ws = True)
        #cmds.xform(polelocator, t = destVector, ws = True)
        return kSuccess

    def doIt(self, argList):
        self.argumentParse(argList)
        if self.startSparse != None:
            if (self.midSparse != None) and (self.endSparse != None):
                self.redoIt()
        return kSuccess
    
def syntaxCreator():
    syntax = om.MSyntax()

    syntax.addFlag(kStartFlag, kStartLongFlag, om.MSyntax.kString)
    syntax.addFlag(kMidFlag, kMidLongFlag, om.MSyntax.kString)
    syntax.addFlag(kEndFlag, kEndLongFlag, om.MSyntax.kString)

    return syntax

def cmdCreator():
    return ompx.asMPxPtr(poleVector())

def initializePlugin(MObject):
    mPlugin = ompx.MFnPlugin(MObject)
    try:
        mPlugin.registerCommand(cmdName, cmdCreator, syntaxCreator)
    except:
        sys.stderr.write("Failed to Register Command: "+cmdName)

def uninitializePlugin(MObject):
    mPlugin = ompx.MFnPlugin(MObject)
    try:
        mPlugin.deregisterCommand(cmdName)
    except:
        sys.stderr.write("Failed to De-Register Command: "+cmdName)
