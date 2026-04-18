import maya.OpenMaya as om
import maya.OpenMayaMPx as ompx
import maya.cmds as cmds
import sys
import math
"""
Created by - Rohit Kumar Singh Kushwaha
Email - rhtksk13@gmail.com

This custom created plugin creates a deformer which performs stretch and squash on a Poly Mesh.

--
Example:

Select the Poly Mesh

cmds.deformer(type = "StretchDeformer") to create deformer

"""
deformerName = "StretchDeformer" # Name of the deformer
nodeId = om.MTypeId(0x00000) # Temp Id for tesitng deformer locally
# deformer Class Creation
class stretchDeformer(ompx.MPxDeformerNode):
    mObj_StretchValue = om.MObject()
    mObj_Volume = om.MObject()
    mObj_StretchAxis = om.MObject()
    # Constructor
    def __init__(self):
        ompx.MPxDeformerNode.__init__(self)
    # deform function - All Calculations
    def deform(self, dataBlock, geoIterator, matrix, geoIndex):
        
        input = ompx.cvar.MPxGeometryFilter_input
        inputArrayDataHandle = dataBlock.outputArrayValue(input)
        inputArrayDataHandle.jumpToElement(geoIndex)
        inputElementDataHandle = inputArrayDataHandle.outputValue()
        # Taking Geometry in which operations are performed
        inputGeo = ompx.cvar.MPxGeometryFilter_inputGeom
        inputGeoDataHandle = inputElementDataHandle.child(inputGeo)
        inMesh = inputGeoDataHandle.asMesh()
        
        # Envelope Value for deformer
        envelope = ompx.cvar.MPxGeometryFilter_envelope
        envelopeDataHandle = dataBlock.inputValue(envelope)
        envelopeVal = envelopeDataHandle.asFloat()
        # Stretch Value
        stretchDataHandle = dataBlock.inputValue(self.mObj_StretchValue)
        stretchVal = stretchDataHandle.asFloat()
        # Volume Preservation Value
        volumeDataHandle = dataBlock.inputValue(self.mObj_Volume)
        volumeVal = volumeDataHandle.asFloat()
        # Direction for stretching
        stretchAxisDataHandle = dataBlock.inputValue(self.mObj_StretchAxis)
        stretchAxisVal = stretchAxisDataHandle.asInt()

        mfnMesh = om.MFnMesh(inMesh) # Taking shape of the Geometry
        
        mFloatVectorArray = om.MFloatPointArray() # Array for each points position of the geometry
        
        mfnMesh.getPoints(mFloatVectorArray, om.MSpace.kObject) # getting points 

        mpointArray = om.MPointArray()
        
        volume = 1.0/((1.0+stretchVal) ** 0.5) # Volume Preservation Formula
        while not geoIterator.isDone():
            pointPosition = geoIterator.position()
                            
            weight = self.weightValue(dataBlock, geoIndex, geoIterator.index())
            # Implementation of the stretch and Squash formula on each point when Stretch Axis is X
            if stretchAxisVal == 0:
                pointPosition.x += ((stretchVal * mFloatVectorArray[geoIterator.index()].x)) * envelopeVal * weight # Stretching on X
                
                pointPosition.y += ((mFloatVectorArray[geoIterator.index()].y) * (volumeVal)) * (-1.0*(1.0-(volume))) * envelopeVal * weight # Squashing on Y
                
                pointPosition.z += ((mFloatVectorArray[geoIterator.index()].z) * (volumeVal)) * (-1.0*(1.0-(volume))) * envelopeVal * weight # Squashing on Z
            # Implementation of the stretch and Squash formula on each point when Stretch Axis is Y
            if stretchAxisVal == 1:
                pointPosition.y += ((stretchVal * mFloatVectorArray[geoIterator.index()].y)) * envelopeVal * weight # Stretching on Y
                pointPosition.x += ((volumeVal)  * (mFloatVectorArray[geoIterator.index()].x)) * (-1.0*(1.0-(volume))) * envelopeVal * weight # Squashing on X
                pointPosition.z += ((volumeVal)  * (mFloatVectorArray[geoIterator.index()].z)) * (-1.0*(1.0-(volume))) * envelopeVal * weight # Squashing on Z
            # Implementation of the stretch and Squash formula on each point when Stretch Axis is Z
            if stretchAxisVal == 2:                
                pointPosition.z += ((stretchVal * mFloatVectorArray[geoIterator.index()].z)) * envelopeVal * weight # Stretching on Z
                pointPosition.y += (volumeVal)  * (mFloatVectorArray[geoIterator.index()].y) * (-1.0*(1.0-(volume))) * envelopeVal * weight # Squashing on Y
                pointPosition.x += (volumeVal)  * (mFloatVectorArray[geoIterator.index()].x) * (-1.0*(1.0-(volume))) * envelopeVal * weight # Squashing on X

            mpointArray.append(pointPosition)
            geoIterator.next()
        geoIterator.setAllPositions(mpointArray) # Setting all the calculated positions of each point

def nodeInitializer():
    """
    Requirements:
        1. Stretch Attribute
        2. Volume Attribute - 0 - Disabled -1 Enable 
            formula - if scale X is n then scale Y = (n)^-(1/2) and scale Z = (n)^-(1/2) 
        3. Ouput Mesh
        4. Stretch Axis - x, y, z
    """

    mfnAttr = om.MFnNumericAttribute()
    stretchDeformer.mObj_StretchValue = mfnAttr.create("Stretch", "str", om.MFnNumericData.kFloat, 0.0)
    mfnAttr.setMin(-0.99999)
    mfnAttr.setKeyable(1)
    mfnAttr.setStorable(1)

    stretchDeformer.mObj_Volume = mfnAttr.create("Volume_Preservation", "volPreserve", om.MFnNumericData.kFloat)
    mfnAttr.setMin(0.0)
    mfnAttr.setMax(1.0)
    mfnAttr.setKeyable(1)
    mfnAttr.setStorable(1)

    mfnEnumAttr = om.MFnEnumAttribute()
    stretchDeformer.mObj_StretchAxis = mfnEnumAttr.create("Stretch_Axis", "StrAxis")

    mfnEnumAttr.addField("X",0)
    mfnEnumAttr.addField("Y",1)
    mfnEnumAttr.addField("Z",2)
    mfnEnumAttr.setKeyable(1)
    mfnEnumAttr.setStorable(1)

    outGeo = ompx.cvar.MPxGeometryFilter_outputGeom

    stretchDeformer.addAttribute(stretchDeformer.mObj_StretchValue)
    stretchDeformer.addAttribute(stretchDeformer.mObj_Volume)
    stretchDeformer.addAttribute(stretchDeformer.mObj_StretchAxis)

    stretchDeformer.attributeAffects(stretchDeformer.mObj_StretchValue, outGeo)
    stretchDeformer.attributeAffects(stretchDeformer.mObj_Volume, outGeo)
    stretchDeformer.attributeAffects(stretchDeformer.mObj_StretchAxis, outGeo)
    

def deformerCreator():
    return ompx.asMPxPtr(stretchDeformer())

def initializePlugin(MObject):
    mPlugin = ompx.MFnPlugin(MObject)
    try:
        mPlugin.registerNode(deformerName, nodeId, deformerCreator, nodeInitializer, ompx.MPxNode.kDeformerNode)
        cmds.makePaintable(deformerName, "weights", attrType = "multiFloat", shapeMode = "deformer")
    except:
        sys.stderr.write("Failed to Register Deformer: "+deformerName)

def uninitializePlugin(MObject):
    mPlugin = ompx.MFnPlugin(MObject)
    try:
        mPlugin.deregisterNode(deformerName)
    except:
        sys.stderr.write("Failed to De-Register Deformer: "+deformerName)
