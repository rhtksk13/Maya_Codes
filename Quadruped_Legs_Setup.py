import maya.cmds as mc

"""
ADD TYPE = Back LEG, Front Leg, Human Leg, Human Arm

ADD Reverse Foot

ADD Hand Roll Setup

ADD IK Stretch Setup

ADD heel_Loc, inner_Loc and outer_Loc in template
"""
def vfxQuadrupedLegIkSetup(startJoint, endEffector):
    dupStartJnt = mc.duplicate(startJoint, name = startJoint+"_IK")

    ikChain = mc.listRelatives(dupStartJnt[0], ad = True, f = True, type = "joint")
    #ikChain.append(dupStartJnt[0])
    print(ikChain)
    
    suffix = "_IK"
    
    mainChain =  mc.listRelatives(startJoint, ad = True, f = False, type = "joint")
    print(mainChain)

    # Renaming joints

    for i in range(len(mainChain)):
        mc.rename(ikChain[i], mainChain[i]+suffix)
        #print(each)

    #ikChain.clear() #supported in Later maya
    newikChain = mc.listRelatives(dupStartJnt[0], ad = True, f = False, type = "joint")
    newikChain.append(dupStartJnt[0])
    newikChain.reverse()
    print(newikChain,"-------------new_IK_Chain")
    print(len(newikChain))

    mainChain.append(startJoint)
    mainChain.reverse()
    print(mainChain,"------------main_Chain")
    # Creating pole Vector --------------------------------------------------------

    tempLoc = mc.spaceLocator( p = (0, 0, 0), name = "Temp_Loc" )
    tempGrp = mc.group(tempLoc, name = "Temp_Loc_Grp")

    tempPoleLoc = mc.spaceLocator( p = (0, 0, 0), name = "Temp_Pole_Loc" )
    tempPoleGrp = mc.group(tempPoleLoc, name = "Temp_Pole_Loc_Grp")

# Calculating the pole vector position --------------------------------------------------
    # Pole Vector Visualiser ---------------------------------------------
        
    mc.pointConstraint(newikChain[0], newikChain[2], tempGrp, maintainOffset = False)
    mc.aimConstraint(newikChain[0], tempGrp, worldUpType = "scene", maintainOffset = False	, aimVector = (0, 1, 0), upVector = (0, 1, 0))
    mc.pointConstraint(newikChain[1], tempLoc, maintainOffset = False, skip = ["x", "z"])

    mc.pointConstraint(newikChain[1], tempPoleGrp, maintainOffset = False)
    mc.aimConstraint(tempLoc, tempPoleGrp, worldUpType = "scene", maintainOffset = False, aimVector = (0, 1, 0), upVector = (0, 1, 0))

    tempDistanceNode = mc.shadingNode("distanceBetween", asUtility = True, name = "TempDistance")
    mc.connectAttr(newikChain[0]+".translate", tempDistanceNode+".point1")
    mc.connectAttr(newikChain[1]+".translate", tempDistanceNode+".point2")
    distance = mc.getAttr(tempDistanceNode+".distance")
    mc.setAttr(tempPoleLoc[0]+".translateY", -(distance/2))

    mc.delete(tempDistanceNode)
    
    poleVectorPosition = mc.xform(tempPoleLoc[0], query = True, translation	= True, worldSpace = True)
    print(poleVectorPosition)
    poleVectorJoint = mc.joint(p = (poleVectorPosition), name = "pole_Vector")# later add Body Part

    # Creating Pole Vector Control --------------------------------------------

    poleVectorCtrl = createCtrl(ctrlName = poleVectorJoint, addGrp = True, ctrlShape = "Cone", attach = False, type = "Normal", parentName = "None")
    #mc.parent(poleVectorJoint, poleVectorJoint+"_Ctrl")
    mc.parent(poleVectorJoint, poleVectorCtrl)

    # Creating IK Controls -----------------------------------------------------

    LegIKCtrl = createIKCtrl(ctrlName = "Leg_IK", ctrlShape = "Box", worldOrient = True, positionObject = newikChain[3])
    
    ik_Handle = mc.ikHandle(startJoint = newikChain[0], endEffector = newikChain[2], solver = "ikRPsolver", name = "Leg_IK_Handle")
    # mc.parentConstraint("Leg_IK_Ctrl", ik_Handle[0], maintainOffset = True)-----------earlier do not use
    #mc.poleVectorConstraint(poleVectorJoint+"_Ctrl", ik_Handle[0])
    mc.poleVectorConstraint(poleVectorCtrl, ik_Handle[0])

    # Adding ctrl for start Joint --------------------------------------------
    thighIKCtrl = createIKCtrl(ctrlName = newikChain[0], ctrlShape = "Box", worldOrient = True, positionObject = newikChain[0])
    #mc.parentConstraint(newikChain[0]+"_Ctrl", newikChain[0])
    mc.parentConstraint(thighIKCtrl, newikChain[0])

# Adding Reverse Foot Setup ---------------------------------------------

    ankle_IkHandle = mc.ikHandle(startJoint = newikChain[2], endEffector = newikChain[3], solver = "ikSCsolver", name = "Ankle_IK_Handle")
    ball_IkHandle = mc.ikHandle(startJoint = newikChain[3], endEffector = newikChain[4], solver = "ikSCsolver", name = "Ball_IK_Handle")
    toe_IkHandle = mc.ikHandle(startJoint = newikChain[4], endEffector = newikChain[5], solver = "ikSCsolver", name = "Toe_IK_Handle")
    
    # Adding grps for reverse foot --------------------------------------------

    ankleGrp = mc.group(name = "ankle_IK_Grp", empty = True)
    mc.matchTransform(ankleGrp, newikChain[2] ,pivots = True)

    ballGrp = mc.group(name = "ball_IK_Grp", empty = True)
    mc.matchTransform(ballGrp, newikChain[3] ,pivots = True)
    
    legRollAimGrp = mc.group(name = "legRollAim_Grp", empty = True)
    mc.matchTransform(legRollAimGrp, newikChain[3] ,pivots = True)
    
    toeGrp = mc.group(name = "toe_IK_Grp", empty = True)
    mc.matchTransform(toeGrp, newikChain[4] ,pivots = True)
    
    toeBendGrp = mc.group(name = "toe_bend_Grp", empty = True)
    mc.matchTransform(toeBendGrp, newikChain[4] ,pivots = True)
    
    toeTipGrp = mc.group(name = "toe_tip_IK_Grp", empty = True)
    mc.matchTransform(toeTipGrp, newikChain[5] ,pivots = True)

    heelGrp = mc.group(name = "heel_Grp", empty = True)
    mc.matchTransform(heelGrp, "heel_Loc") # need a locator for heel grp, inner and outer grp

    innerGrp = mc.group(name = "inner_Grp", empty = True)
    mc.matchTransform(innerGrp, "inner_Loc")

    outerGrp = mc.group(name = "outer_Grp", empty = True)
    mc.matchTransform(outerGrp, "outer_Loc")

    legModifyGrp = mc.group(name = "Leg_Modify_Grp", empty = True)
    mc.matchTransform(legModifyGrp, ankleGrp)

    legOffsetGrp = mc.group(name = "Leg_Offset_Grp", empty = True)
    mc.matchTransform(legOffsetGrp, ankleGrp)

    # Parenting of Group ----------------------------------------

    mc.parent(ankleGrp, ballGrp)
    mc.parent(legRollAimGrp, toeGrp)
    mc.parent(ballGrp, legRollAimGrp)

    mc.parent(toeGrp, toeTipGrp)
    mc.parent(toeBendGrp, toeTipGrp)

    mc.parent(toeTipGrp, heelGrp)
    mc.parent(heelGrp, innerGrp)
    mc.parent(innerGrp, outerGrp)
    mc.parent(outerGrp, legModifyGrp)
    mc.parent(legModifyGrp, legOffsetGrp)

    # mc.parent(ik_Handle[0], legRollAimGrp)
    mc.parent(ik_Handle[0], ballGrp)
    mc.parent(ankle_IkHandle[0], ankleGrp)
    mc.parent(ball_IkHandle[0], toeGrp)
    mc.parent(toe_IkHandle[0], toeBendGrp)
    """
    mc.parentConstraint("Leg_IK_Ctrl", legModifyGrp, maintainOffset = True)

    mc.addAttr("Leg_IK_Ctrl", longName = "Foot_Roll", keyable = True, attributeType = "float", defaultValue = 0, minValue = -90, maxValue = 90)
    mc.addAttr("Leg_IK_Ctrl", longName = "Side_Roll", keyable = True, attributeType = "float", defaultValue = 0, minValue = -90, maxValue = 90)
    mc.addAttr("Leg_IK_Ctrl", longName = "Toe_Twist", keyable = True, attributeType = "float")
    mc.addAttr("Leg_IK_Ctrl", longName = "Toe_Wiggle", keyable = True, attributeType = "float")

    mc.addAttr("Leg_IK_Ctrl", longName = "Stretch", keyable = False)
    mc.setAttr("Leg_IK_Ctrl.Stretch", edit = True, channelBox = True)

    mc.addAttr("Leg_IK_Ctrl", longName = "Auto_Stretch", keyable = True, attributeType = "float", defaultValue = 0)
    mc.addAttr("Leg_IK_Ctrl", longName = "Thigh_Stretch", keyable = True, attributeType = "float", defaultValue = 0)
    mc.addAttr("Leg_IK_Ctrl", longName = "Knee_Stretch", keyable = True, attributeType = "float")
    mc.addAttr("Leg_IK_Ctrl", longName = "Ankle_Stretch", keyable = True, attributeType = "float")
    """
    mc.parentConstraint(LegIKCtrl, legModifyGrp, maintainOffset = True)

    mc.addAttr(LegIKCtrl, longName = "Foot_Roll", keyable = True, attributeType = "float", defaultValue = 0, minValue = -90, maxValue = 90)
    mc.addAttr(LegIKCtrl, longName = "Side_Roll", keyable = True, attributeType = "float", defaultValue = 0, minValue = -90, maxValue = 90)
    mc.addAttr(LegIKCtrl, longName = "Toe_Twist", keyable = True, attributeType = "float")
    mc.addAttr(LegIKCtrl, longName = "Toe_Wiggle", keyable = True, attributeType = "float")

    mc.addAttr(LegIKCtrl, longName = "Stretch", keyable = False)
    mc.setAttr(LegIKCtrl+".Stretch", edit = True, channelBox = True)

    mc.addAttr(LegIKCtrl, longName = "Auto_Stretch", keyable = True, attributeType = "float", defaultValue = 0, maxValue = 1.0, minValue = 0.0)
    mc.addAttr(LegIKCtrl, longName = "Thigh_Stretch", keyable = True, attributeType = "float", defaultValue = 0)
    mc.addAttr(LegIKCtrl, longName = "Knee_Stretch", keyable = True, attributeType = "float", defaultValue = 0)
    mc.addAttr(LegIKCtrl, longName = "Ankle_Stretch", keyable = True, attributeType = "float", defaultValue = 0)
    # Foot Roll ----------------------------------------------------

    

# Creating Joint for Leg Aim ------------------------------------------------------
    mc.select(clear = True)
    ankleIKPos = mc.xform(newikChain[3] ,query = True, worldSpace = True, translation = True)
    thighIKPos = mc.xform(newikChain[0] ,query = True, worldSpace = True, translation = True)
    print(ankleIKPos,"----------------------ankleIKPos")
    print(thighIKPos,"----------------------thighIKPos")
    legIKAimStartJnt = mc.joint(name = "leg_IK_Aim", position = ankleIKPos)
    legIKAimEndJnt = mc.joint(name = "leg_IK_AimEnd", position = thighIKPos)
  
    print(legIKAimStartJnt, "--------------------------------legAimIK----------")
    print(legIKAimEndJnt, "--------------------------------legAimIKEnd----------")

    legAimIKHandle = mc.ikHandle(startJoint = legIKAimStartJnt, endEffector = legIKAimEndJnt, solver = "ikRPsolver", name = "Leg_Aim_IK_Handle")
    #mc.poleVectorConstraint(poleVectorJoint+"_Ctrl", legAimIKHandle[0])
    mc.poleVectorConstraint(poleVectorCtrl, legAimIKHandle[0])
    #mc.pointConstraint("Leg_IK_Ctrl", legIKAimStartJnt)
    mc.pointConstraint(LegIKCtrl, legIKAimStartJnt)
    
    legAimCtrl = createIKCtrl(ctrlName = legIKAimStartJnt, ctrlShape = "Box", worldOrient = True, positionObject = legIKAimStartJnt)
    #mc.addAttr(legIKAimStartJnt+"_Ctrl", longName = "Aim_Active", keyable = True, attributeType = "float", defaultValue = 0, maxValue = 10.0, minValue = 0.0)
    mc.addAttr(legAimCtrl, longName = "Aim_Active", keyable = True, attributeType = "float", defaultValue = 0, maxValue = 10.0, minValue = 0.0)

    mc.parentConstraint(newikChain[2], legIKAimStartJnt+"_Modify_Grp", maintainOffset = True)

    #legAimConst = mc.parentConstraint("Leg_IK_Ctrl", legIKAimStartJnt, legRollAimGrp, maintainOffset = True, skipTranslate = ["x", "y", "z"])
    legAimConst = mc.parentConstraint(LegIKCtrl, legIKAimStartJnt, legRollAimGrp, maintainOffset = True, skipTranslate = ["x", "y", "z"])
    print(legAimConst,"-------------------------------leg Aim Constraint")

    # setAttr "legRollAim_Grp_parentConstraint1.leg_IK_AimW1" 1;
    # setAttr "legRollAim_Grp_parentConstraint1.Leg_IK_CtrlW0" 1;
    legAimUnitConvert = mc.shadingNode("unitConversion", asUtility = True, name = "legAim_UnitConversion")
    print(legAimUnitConvert,"---------------------------------------Leg aim unit conversion")

    # mc.connectAttr(legIKAimStartJnt+"_Ctrl.Aim_Active" , legAimConst[0]+"."+legIKAimStartJnt+"W1")
    #mc.connectAttr(legIKAimStartJnt+"_Ctrl.Aim_Active" , legAimUnitConvert+".input")
    mc.connectAttr(legAimCtrl+".Aim_Active" , legAimUnitConvert+".input")
    mc.setAttr(legAimUnitConvert+".conversionFactor", 0.1) # conversionFactor" 0.1
    mc.connectAttr(legAimUnitConvert+".output" , legAimConst[0]+"."+legIKAimStartJnt+"W1")

    legAimReverse = mc.shadingNode("reverse" ,asUtility = True, name = "leg_Aim_Active_Reverse")
    #print(legAimReverse,"-----------------------------------Reverse")
    # mc.connectAttr(legIKAimStartJnt+"_Ctrl.Aim_Active" , legAimReverse+".inputX")
    mc.connectAttr(legAimUnitConvert+".output" , legAimReverse+".inputX")
    #mc.connectAttr(legAimReverse+".outputX" , legAimConst[0]+".Leg_IK_CtrlW0")
    mc.connectAttr(legAimReverse+".outputX" , legAimConst[0]+"."+LegIKCtrl+"W0")

    #mc.connectAttr(legIKAimStartJnt+"_Ctrl.rotate", ballGrp+".rotate")
    mc.connectAttr(legAimCtrl+".rotate", ballGrp+".rotate")

# ------------------------------Connecting the Attributes to the values ---------------------------------
    mc.setDrivenKeyframe(outerGrp+".rotateZ", currentDriver = LegIKCtrl+".Side_Roll", driverValue = 0, value = 0)
    mc.setDrivenKeyframe(innerGrp+".rotateZ", currentDriver = LegIKCtrl+".Side_Roll", driverValue = 0, value = 0)
    mc.setDrivenKeyframe(outerGrp+".rotateZ", currentDriver = LegIKCtrl+".Side_Roll", driverValue = 90, value = -90)
    mc.setDrivenKeyframe(innerGrp+".rotateZ", currentDriver = LegIKCtrl+".Side_Roll", driverValue = -90, value = 90)


    mc.connectAttr(LegIKCtrl+".Toe_Wiggle", toeBendGrp+".rotateX")
    mc.connectAttr(LegIKCtrl+".Toe_Twist", toeTipGrp+".rotateY")
    
    mc.setDrivenKeyframe(heelGrp+".rotateX", currentDriver = LegIKCtrl+".Foot_Roll", driverValue = 0, value = 0)
    mc.setDrivenKeyframe(toeGrp+".rotateX", currentDriver = LegIKCtrl+".Foot_Roll", driverValue = 0, value = 0)
    mc.setDrivenKeyframe(toeTipGrp+".rotateX", currentDriver = LegIKCtrl+".Foot_Roll", driverValue = 0, value = 0)
    
    mc.setDrivenKeyframe(toeGrp+".rotateX", currentDriver = LegIKCtrl+".Foot_Roll", driverValue = 45, value = 45)
    mc.setDrivenKeyframe(toeTipGrp+".rotateX", currentDriver = LegIKCtrl+".Foot_Roll", driverValue = 45, value = 0)
    
    mc.setDrivenKeyframe(toeGrp+".rotateX", currentDriver = LegIKCtrl+".Foot_Roll", driverValue = 90, value = 0)
    mc.setDrivenKeyframe(toeTipGrp+".rotateX", currentDriver = LegIKCtrl+".Foot_Roll", driverValue = 90, value = 45)
    
    mc.setDrivenKeyframe(heelGrp+".rotateX", currentDriver = LegIKCtrl+".Foot_Roll", driverValue = -90, value = -90)

# Stretch Setup ------------------------------
#def ikStretchSetup(startJoint, endJoint, limbname, IKCtrl):
    startPos = mc.xform(newikChain[0], query = True, translation = True, worldSpace = True)
    print(startPos)

    endPos = mc.xform(newikChain[3], query = True, translation = True, worldSpace = True)
    print(endPos)

    # Creating the Locators -------------------------
    limbname = "Leg"
    #startLoc = mc.spaceLocator(position = (startPos[0], startPos[1], startPos[2]) , name = limbname+"_Stretch_Start_Loc")
    startLoc = mc.spaceLocator(name = limbname+"_Stretch_Start_Loc")
    #endLoc = mc.spaceLocator(position = (endPos[0], endPos[1], endPos[2]), name = limbname+"_Stretch_End_Loc")
    endLoc = mc.spaceLocator(name = limbname+"_Stretch_End_Loc")

    print(startLoc)
    print(endLoc)

    mc.matchTransform(startLoc, newikChain[0], position = True)
    #startLocConstraint = mc.parentConstraint(startJoint, startLoc, maintainOffset = True)
    startLocConstraint = mc.parentConstraint(thighIKCtrl, startLoc, maintainOffset = True)# thighIKCtrl
    print(startLocConstraint)
    #mc.matchTransform(endLoc, endJoint, position = True)
    mc.matchTransform(endLoc, LegIKCtrl, position = True)
    endLocConstraint = mc.parentConstraint(LegIKCtrl, endLoc, maintainOffset = True)
    print(endLocConstraint)

# Distance node creation ------------------------
    distanceNode = mc.shadingNode("distanceBetween", asUtility = True, name = limbname+"_Stretch_Distance")

    mc.connectAttr(startLoc[0]+".translate", distanceNode+".point1")
    mc.connectAttr(endLoc[0]+".translate", distanceNode+".point2")

# Condition node creation -----------------------
    conditionNode = mc.shadingNode("condition", asUtility = True, name = limbname+"_Stretch_condition")

    mc.connectAttr(distanceNode+".distance", conditionNode+".firstTerm")
    distanceValue = mc.getAttr(distanceNode+".distance")
    print(distanceValue)

    mc.setAttr(conditionNode+".secondTerm", distanceValue)
    mc.setAttr(conditionNode+".operation", 2)

# Mulitply divide node creation ---------------------
    stretchMultnode = mc.shadingNode("multiplyDivide", asUtility = True, name = limbname+"_Stretch_Multi")

    mc.connectAttr(distanceNode+".distance", stretchMultnode+".input1X")
    mc.setAttr(stretchMultnode+".input2X", distanceValue)
    mc.setAttr(stretchMultnode+".operation", 2)

    mc.connectAttr(stretchMultnode+".outputX", conditionNode+".colorIfTrueR")
    mc.connectAttr(stretchMultnode+".outputX", conditionNode+".colorIfTrueG")
    mc.connectAttr(stretchMultnode+".outputX", conditionNode+".colorIfTrueB")

# Connecting the stretch Values with the joint scale ----------------------

    jointChain = mc.listRelatives(newikChain[0], allDescendents = True, type = "joint")
    jointChain.append(newikChain[0])
    jointChain.reverse()
    print(jointChain)

# Creating the Plus minus Average node -------------------------

    pmaNode = mc.shadingNode("plusMinusAverage", asUtility = True , name = limbname+"_Stretch_PMA")

    mc.connectAttr(conditionNode+".outColorR", pmaNode+".input3D[0].input3Dx")
    mc.connectAttr(conditionNode+".outColorG", pmaNode+".input3D[0].input3Dy")
    mc.connectAttr(conditionNode+".outColorB", pmaNode+".input3D[0].input3Dz")

# Creating multiply divide node -----------------
    stretchFactor = mc.shadingNode("multiplyDivide", asUtility = True ,name = limbname+"_Individual_Stretch_Multi")
    mc.setAttr(stretchFactor+".operation", 2)
    
    mc.connectAttr(LegIKCtrl+".Thigh_Stretch", stretchFactor+".input1X")
    mc.connectAttr(LegIKCtrl+".Knee_Stretch", stretchFactor+".input1Y")
    mc.connectAttr(LegIKCtrl+".Ankle_Stretch", stretchFactor+".input1Z")

    mc.setAttr(stretchFactor+".input2X", 10)
    mc.setAttr(stretchFactor+".input2Y", 10)
    mc.setAttr(stretchFactor+".input2Z", 10)

    mc.connectAttr(stretchFactor+".outputX", pmaNode+".input3D[1].input3Dx")
    mc.connectAttr(stretchFactor+".outputY", pmaNode+".input3D[1].input3Dy")
    mc.connectAttr(stretchFactor+".outputZ", pmaNode+".input3D[1].input3Dz")

    mc.connectAttr(pmaNode+".output3Dx", jointChain[0]+".scaleX")
    mc.connectAttr(pmaNode+".output3Dy", jointChain[1]+".scaleX")
    mc.connectAttr(pmaNode+".output3Dz", jointChain[2]+".scaleX")

    mc.connectAttr(LegIKCtrl+".Auto_Stretch", startLocConstraint[0]+"."+thighIKCtrl+"W0")
    mc.connectAttr(LegIKCtrl+".Auto_Stretch", endLocConstraint[0]+"."+LegIKCtrl+"W0")

# Create Controls Method------------------------------------------------------
def createCtrl(ctrlName, addGrp, ctrlShape, attach, type, parentName):
    mc.file("D:\Others\Maya Auto Rig Tool Mel\Maya-Rigging-Automation-Codes\Controls_Library.ma", reference = True)
    refNamespace = mc.file("D:\Others\Maya Auto Rig Tool Mel\Maya-Rigging-Automation-Codes\Controls_Library.ma", query = True, referenceNode = True)
    
    #print(refNamespace)
    if ctrlShape == "Box":
        ctrl = mc.duplicate("Controls_Library_Box_Ctrl" ,name = ctrlName+"_Ctrl")
    elif ctrlShape == "Sphere":
        ctrl = mc.duplicate("Controls_Library_Sphere_Ctrl" ,name = ctrlName+"_Ctrl")
    elif ctrlShape == "switch":
        ctrl = mc.duplicate("Controls_Library_switch_Ctrl" ,name = ctrlName+"_Ctrl")
    elif ctrlShape == "Arrow":
        ctrl = mc.duplicate("Controls_Library_Arrow_Ctrl" ,name = ctrlName+"_Ctrl")
    elif ctrlShape == "Cone":
        ctrl = mc.duplicate("Controls_Library_Cone_Ctrl" ,name = ctrlName+"_Ctrl")
    elif ctrlShape == "Square":
        ctrl = mc.duplicate("Controls_Library_square_Ctrl" ,name = ctrlName+"_Ctrl")
    elif ctrlShape == "Dual_Arrow":
        ctrl = mc.duplicate("Controls_Library_Dual_Arrow_Ctrl" ,name = ctrlName+"_Ctrl")
    elif ctrlShape == "Trapazoid":
        ctrl = mc.duplicate("Controls_Library_Trapazoid_Ctrl" ,name = ctrlName+"_Ctrl")
    elif ctrlShape == "Plus":
        ctrl = mc.duplicate("Controls_Library_Plus_Ctrl" ,name = ctrlName+"_Ctrl")
    elif ctrlShape == "Circle":
        ctrl = mc.duplicate("Controls_Library_Circle_Ctrl" ,name = ctrlName+"_Ctrl")
    elif ctrlShape == "Quad_Arrow":
        ctrl = mc.duplicate("Controls_Library_Quad_Arrow_Ctrl" ,name = ctrlName+"_Ctrl")
    elif ctrlShape == "Setting":
        ctrl = mc.duplicate("Controls_Library_Setting_Ctrl" ,name = ctrlName+"_Ctrl")
    elif ctrlShape == "Cone_Arrow":
        ctrl = mc.duplicate("Controls_Library_Cone_Arrow_Ctrl" ,name = ctrlName+"_Ctrl")
    elif ctrlShape == "Quad_Cone_Arrow":
        ctrl = mc.duplicate("Controls_Library_Quad_Cone_Arrow_Ctrl" ,name = ctrlName+"_Ctrl")
    else:
        ctrl = mc.duplicate("Circle_Ctrl", name = ctrlName+"_Ctrl")
        
    ctrlOffset = mc.group(empty = True, name = ctrlName+"_Offset_Grp")

    if type == "Normal":
        mc.matchTransform(ctrlOffset, ctrlName, position = True, rotation = True)
        mc.matchTransform(ctrl, ctrlName, position = True, rotation = True)
    elif type == "Spine_Switch":
        mc.matchTransform(ctrlOffset, "Root", position = True, rotation = False)
        mc.matchTransform(ctrl, "Root", position = True, rotation = False)    
    elif type == "Tangent":
        ctrl = mc.rename(ctrl, ctrlName+"_"+type+"_Ctrl")
        print(ctrl)
        print("-------------------------------------")
        ctrlOffset = mc.rename(ctrlOffset, ctrlName+"_"+type+"_Offset_Grp")
        mc.matchTransform(ctrlOffset, ctrlName, position = True, rotation = False)
        mc.matchTransform(ctrl, ctrlName, position = True, rotation = False)
    

    if addGrp == True:        
        if type == "Normal":
            modifyGrp = mc.group(empty = True, name = ctrlName+"_Modify_Grp")
            mc.matchTransform(modifyGrp, ctrlName, position = True, rotation = True)
        elif type == "Spine_Switch":
            modifyGrp = mc.group(empty = True, name = ctrlName+"_Modify_Grp")
            mc.matchTransform(modifyGrp, "Root", position = True, rotation = False)
        elif type == "Tangent":
            modifyGrp = mc.group(empty = True, name = ctrlName+"_"+type+"_Modify_Grp")
            mc.matchTransform(modifyGrp, ctrlName, position = True, rotation = False)

        mc.parent(modifyGrp, ctrlOffset)
        mc.parent(ctrl, modifyGrp)
    else:
        mc.parent(ctrl, ctrlOffset)


    if attach == True:
        mc.parentConstraint(ctrl, ctrlName)
        #mc.parentConstraint(ctrl, attach)#parent

    if parentName != "None":
        mc.parentConstraint(parentName, modifyGrp)

    mc.file("D:\Others\Maya Auto Rig Tool Mel\Maya-Rigging-Automation-Codes\Controls_Library.ma", removeReference = True)
    return ctrlName+"_Ctrl"
#--------------------------------------------------------------------------------

def createIKCtrl(ctrlName, ctrlShape, worldOrient, positionObject):
    mc.file("D:\Others\Maya Auto Rig Tool Mel\Maya-Rigging-Automation-Codes\Controls_Library.ma", reference = True)
    refNamespace = mc.file("D:\Others\Maya Auto Rig Tool Mel\Maya-Rigging-Automation-Codes\Controls_Library.ma", query = True, referenceNode = True)

        #print(refNamespace)
    if ctrlShape == "Box":
        ctrl = mc.duplicate("Controls_Library_Box_Ctrl" ,name = ctrlName+"_Ctrl")
    elif ctrlShape == "Sphere":
        ctrl = mc.duplicate("Controls_Library_Sphere_Ctrl" ,name = ctrlName+"_Ctrl")
    elif ctrlShape == "switch":
        ctrl = mc.duplicate("Controls_Library_switch_Ctrl" ,name = ctrlName+"_Ctrl")
    elif ctrlShape == "Arrow":
        ctrl = mc.duplicate("Controls_Library_Arrow_Ctrl" ,name = ctrlName+"_Ctrl")
    elif ctrlShape == "Cone":
        ctrl = mc.duplicate("Controls_Library_Cone_Ctrl" ,name = ctrlName+"_Ctrl")
    elif ctrlShape == "Square":
        ctrl = mc.duplicate("Controls_Library_square_Ctrl" ,name = ctrlName+"_Ctrl")
    elif ctrlShape == "Dual_Arrow":
        ctrl = mc.duplicate("Controls_Library_Dual_Arrow_Ctrl" ,name = ctrlName+"_Ctrl")
    elif ctrlShape == "Trapazoid":
        ctrl = mc.duplicate("Controls_Library_Trapazoid_Ctrl" ,name = ctrlName+"_Ctrl")
    elif ctrlShape == "Plus":
        ctrl = mc.duplicate("Controls_Library_Plus_Ctrl" ,name = ctrlName+"_Ctrl")
    elif ctrlShape == "Circle":
        ctrl = mc.duplicate("Controls_Library_Circle_Ctrl" ,name = ctrlName+"_Ctrl")
    elif ctrlShape == "Quad_Arrow":
        ctrl = mc.duplicate("Controls_Library_Quad_Arrow_Ctrl" ,name = ctrlName+"_Ctrl")
    elif ctrlShape == "Setting":
        ctrl = mc.duplicate("Controls_Library_Setting_Ctrl" ,name = ctrlName+"_Ctrl")
    elif ctrlShape == "Cone_Arrow":
        ctrl = mc.duplicate("Controls_Library_Cone_Arrow_Ctrl" ,name = ctrlName+"_Ctrl")
    elif ctrlShape == "Quad_Cone_Arrow":
        ctrl = mc.duplicate("Controls_Library_Quad_Cone_Arrow_Ctrl" ,name = ctrlName+"_Ctrl")
    else:
        ctrl = mc.duplicate("Circle_Ctrl", name = ctrlName+"_Ctrl")
        
    ctrlOffset = mc.group(empty = True, name = ctrlName+"_Offset_Grp")
    modifyGrp = mc.group(empty = True, name = ctrlName+"_Modify_Grp")

    mc.parent(modifyGrp, ctrlOffset)
    mc.parent(ctrl, modifyGrp)

    if worldOrient == True:        
        mc.matchTransform(ctrlOffset, positionObject, position = True, rotation = False)
        mc.matchTransform(ctrl, ctrlOffset, position = True, rotation = False)
    else:        
        mc.matchTransform(ctrlOffset, positionObject, position = True, rotation = True)
        mc.matchTransform(ctrl, ctrlOffset, position = True, rotation = True)

    mc.file("D:\Others\Maya Auto Rig Tool Mel\Maya-Rigging-Automation-Codes\Controls_Library.ma", removeReference = True)
    return ctrlName+"_Ctrl"

vfxQuadrupedLegIkSetup(startJoint = "thigh", endEffector = "ankle")
#vfxQuadrupedLegIkSetup(startJoint = "l_thigh", endEffector = "l_ankle")
