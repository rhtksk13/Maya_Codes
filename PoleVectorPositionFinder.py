import maya.OpenMaya as om
import maya.OpenMayaMPx as ompx
import maya.cmds as cmds
import sys

"""
Created by - Rohit Kumar Singh Kushwaha
Email - rhtksk13@gmail.com

Example:
cmds.findPoleVector(sj = "start_Jnt", mj = "mid_Jnt", ej = "end_Jnt")

This custom command finds the position for pole vector to be Placed in an ik chain.

- Requirements:

    1. Start Joint Flag
    2. Mid Joint Flag
    3. End Joint Flag
    4. Calculation
    5. A locator created at the position for poleVector
"""
cmdName = "findPoleVector" # command Name - cmds.findPoleVector()
kStartFlag = "-sj" # short name for flag
kStartLongFlag = "-startJoint" # Long name for flag

kMidFlag = "-mj" # short name for flag
kMidLongFlag = "-midJoint" # Long name for flag

kEndFlag = "-ej" # short name for flag
kEndLongFlag = "-endJoint" # Long name for flag

kHelpFlag = "-h" # short name for help flag
kHelpLongFlag = "-help" # Long name for help flag

message = "This command helps in finding the position for Pole Vector to be placed provided three joints of a 3 chain setup." # message shown by help flag
kSuccess = 1
kFail = 0
# Class creation for command
class poleVector(ompx.MPxCommand):
    # setting up variables for joints as values
    startSparse = None
    midSparse = None
    endSparse = None
    # constructor
    def __init__(self):
        ompx.MPxCommand.__init__(self)
    # parsing the arguments
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
        startpos = cmds.xform(self.startSparse, q = True, rp = True, ws = True) # Getting the world position of the start joint
        startVector = om.MVector(startpos[0], startpos[1], startpos[2])
        
        midPos = cmds.xform(self.midSparse, q = True, rp = True, ws = True) # Getting the world position of the mid joint
        midVector = om.MVector(midPos[0], midPos[1], midPos[2])
        
        endPos = cmds.xform(self.endSparse, q = True, rp = True, ws = True) # Getting the world position of the end joint
        endVector = om.MVector(endPos[0], endPos[1], endPos[2])
        
        # Finding the mid Point
        midPointVector = om.MVector()
        midPointVector = (startVector + endVector) / 2
        # Finding the direction
        directionVector = om.MVector()
        directionVector = midVector - midPointVector
        # Finding the destination for pole vector
        destVector = om.MVector()
        destVector = midPointVector + (directionVector * 4)
        # Creating the loacator at the destination
        polelocator = cmds.spaceLocator(n = "Pole_Vector_position_Loc")
        cmds.xform(polelocator, t = (destVector.x, destVector.y, destVector.z), ws = True)
        
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
# Initializing the Plugin
def initializePlugin(MObject):
    mPlugin = ompx.MFnPlugin(MObject)
    try:
        mPlugin.registerCommand(cmdName, cmdCreator, syntaxCreator)
    except:
        sys.stderr.write("Failed to Register Command: "+cmdName)
# UnInitializing the Plugin
def uninitializePlugin(MObject):
    mPlugin = ompx.MFnPlugin(MObject)
    try:
        mPlugin.deregisterCommand(cmdName)
    except:
        sys.stderr.write("Failed to De-Register Command: "+cmdName)
