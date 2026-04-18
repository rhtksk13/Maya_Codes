import maya.OpenMaya as om
import maya.OpenMayaMPx as ompx
import maya.cmds as cmds
import sys
import math

deformerName = "StretchDeformer"
nodeId = om.MTypeId(0x00000)

class stretchDeformer(ompx.MPxDeformerNode):
    mObj_StretchValue = om.MObject()
    mObj_Volume = om.MObject()
    mObj_StretchAxis = om.MObject()
    
    def __init__(self):
        ompx.MPxDeformerNode.__init__(self)

    def deform(self, dataBlock, geoIterator, matrix, geoIndex):
        input = ompx.cvar.MPxGeometryFilter_input
        inputArrayDataHandle = dataBlock.outputArrayValue(input)
        inputArrayDataHandle.jumpToElement(geoIndex)
        inputElementDataHandle = inputArrayDataHandle.outputValue()

        inputGeo = ompx.cvar.MPxGeometryFilter_inputGeom
        inputGeoDataHandle = inputElementDataHandle.child(inputGeo)
        inMesh = inputGeoDataHandle.asMesh()
        

        envelope = ompx.cvar.MPxGeometryFilter_envelope
        envelopeDataHandle = dataBlock.inputValue(envelope)
        envelopeVal = envelopeDataHandle.asFloat()

        stretchDataHandle = dataBlock.inputValue(self.mObj_StretchValue)
        stretchVal = stretchDataHandle.asFloat()

        volumeDataHandle = dataBlock.inputValue(self.mObj_Volume)
        volumeVal = volumeDataHandle.asFloat()

        stretchAxisDataHandle = dataBlock.inputValue(self.mObj_StretchAxis)
        stretchAxisVal = stretchAxisDataHandle.asInt()

        mfnMesh = om.MFnMesh(inMesh)
        #mFloatVectorArray = om.MFloatVectorArray()
        mFloatVectorArray = om.MFloatPointArray()
        #mfnMesh.getVertexNormals(False, mFloatVectorArray, om.MSpace.kObject)
        mfnMesh.getPoints(mFloatVectorArray, om.MSpace.kObject)

        mpointArray = om.MPointArray()
        
        volume = 1.0/((1.0+stretchVal) ** 0.5)
        while not geoIterator.isDone():
            pointPosition = geoIterator.position()
                            
            weight = self.weightValue(dataBlock, geoIndex, geoIterator.index())
            if stretchAxisVal == 0:
                pointPosition.x += ((stretchVal * mFloatVectorArray[geoIterator.index()].x)) * envelopeVal * weight
                #pointPosition.y += ((mFloatVectorArray[geoIterator.index()].y) * (volumeVal)) * ((volume) - 1.0) * envelopeVal * weight 
                pointPosition.y += ((mFloatVectorArray[geoIterator.index()].y) * (volumeVal)) * (-1.0*(1.0-(volume))) * envelopeVal * weight
                #pointPosition.z += ((mFloatVectorArray[geoIterator.index()].z) * (volumeVal)) * ((volume) - 1.0) * envelopeVal * weight
                pointPosition.z += ((mFloatVectorArray[geoIterator.index()].z) * (volumeVal)) * (-1.0*(1.0-(volume))) * envelopeVal * weight
                                            
            if stretchAxisVal == 1:
                pointPosition.y += ((stretchVal * mFloatVectorArray[geoIterator.index()].y)) * envelopeVal * weight
                pointPosition.x += ((volumeVal)  * (mFloatVectorArray[geoIterator.index()].x)) * (-1.0*(1.0-(volume))) * envelopeVal * weight
                pointPosition.z += ((volumeVal)  * (mFloatVectorArray[geoIterator.index()].z)) * (-1.0*(1.0-(volume))) * envelopeVal * weight
                
            if stretchAxisVal == 2:                
                pointPosition.z += ((stretchVal * mFloatVectorArray[geoIterator.index()].z)) * envelopeVal * weight
                pointPosition.y += (volumeVal)  * (mFloatVectorArray[geoIterator.index()].y) * (-1.0*(1.0-(volume))) * envelopeVal * weight
                pointPosition.x += (volumeVal)  * (mFloatVectorArray[geoIterator.index()].x) * (-1.0*(1.0-(volume))) * envelopeVal * weight

            mpointArray.append(pointPosition)
            geoIterator.next()
        geoIterator.setAllPositions(mpointArray)

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
