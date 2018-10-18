import pybullet as p, os, sys, numpy as np, time
import pybullet_utils.urdfEditor as urdfEditor

def main():
    N,STEPS = 2,1000
    
    # Load MultiBody from URDF
    org = p.connect(p.DIRECT, options='--width=160 --height=160 --cameraArraySize=16')
    p.setAdditionalSearchPath("data")
    minis = p.loadURDF("minis.urdf", flags = p.URDF_USE_INERTIA_FROM_FILE, physicsClientId=org)
    ed = UrdfEditorExt()
    ed.initializeFromBulletBody(minis, physicsClientId=org)
    p.disconnect()

    # create from MultiBody          
    print("Please test FPS with p.DIRECT!")
    org = p.connect(p.GUI)
    #org = p.connect(p.DIRECT)  
    
    #set physics parameters
    p.setGravity(0,0,-9.8)
    p.setTimeStep(0.033)

    # NOTE: 
    # with fewer than numSolverIterations=32, numSubSteps=4
    # some of the minis-es will fall -> physics is broken!
    p.setPhysicsEngineParameter(numSolverIterations=32, numSubSteps=8)
    p.setPhysicsEngineParameter(enableConeFriction=0)

    p.loadURDF("plane.urdf",[0,0,0])    

    basePositions, baseOrientations = [],[]
    for x in range(-N, N):
        for y in range(-N, N):
            basePositions.append([x,y,282])
            baseOrientations.append( p.getQuaternionFromEuler([3.14157 / 2, 0.1 * x, 0.1 * y]) )

    minises = ed.createMultiBodyArray(physicsClientId=org, basePositions = basePositions, baseOrientations = baseOrientations)
    
    # activate servos (to hold pos = 0), is this broken in MultiBody!?!
    for minis in minises:
        for i in range(p.getNumJoints(minis)):
            motor_id, joint_name, joint_type = p.getJointInfo(minis, i)[:3]     # FIXME: joint_name is invalid!            
            if joint_type == p.JOINT_REVOLUTE:
                p.resetJointState(minis, motor_id, targetValue=0, targetVelocity=0)
        
                p.setJointMotorControl2(
                    bodyIndex=minis, jointIndex=motor_id, controlMode=p.POSITION_CONTROL,
                    targetPosition=0, positionGain=1.0, velocityGain=0.1,
                    force=1.2748, maxVelocity=2.083)

    

    #step the simulation for STEPS steps
    time_start = time.time()
    for i in range(STEPS):
        p.stepSimulation()
    
    time_end = time.time()
    
    print("FPS = ", 4*N*N*STEPS / (time_end - time_start))




class UrdfEditorExt(urdfEditor.UrdfEditor):

    def createMultiBodyArray(self, basePositions=[[0,0,0]], baseOrientations=[[0,0,0,1]], physicsClientId=0):
        #assume link[0] is base
        if (len(self.urdfLinks)==0):
            return -1

        #for i in range (len(self.urdfLinks)):
        #    print("link", i, "=",self.urdfLinks[i].link_name)


        base = self.urdfLinks[0]

        #v.tmp_collision_shape_ids=[]
        baseMass = base.urdf_inertial.mass
        baseCollisionShapeIndex = -1
        baseShapeTypeArray=[]
        baseRadiusArray=[]
        baseHalfExtentsArray=[]
        lengthsArray=[]
        fileNameArray=[]
        meshScaleArray=[]
        basePositionsArray=[]
        baseOrientationsArray=[]

        for v in base.urdf_collision_shapes:
            shapeType = v.geom_type
            baseShapeTypeArray.append(shapeType)
            baseHalfExtentsArray.append([0.5*v.geom_extents[0],0.5*v.geom_extents[1],0.5*v.geom_extents[2]])
            baseRadiusArray.append(v.geom_radius)
            lengthsArray.append(v.geom_length)
            fileNameArray.append(v.geom_meshfilename)
            meshScaleArray.append(v.geom_meshscale)
            basePositionsArray.append(v.origin_xyz)
            orn=p.getQuaternionFromEuler(v.origin_rpy)
            baseOrientationsArray.append(orn)

        if (len(baseShapeTypeArray)):
            #print("fileNameArray=",fileNameArray)
            baseCollisionShapeIndex = p.createCollisionShapeArray(shapeTypes=baseShapeTypeArray,
                    radii=baseRadiusArray,
                    halfExtents=baseHalfExtentsArray,
                    lengths=lengthsArray,
                    fileNames=fileNameArray,
                    meshScales=meshScaleArray,
                    collisionFramePositions=basePositionsArray,
                    collisionFrameOrientations=baseOrientationsArray,
                    physicsClientId=physicsClientId)


        urdfVisuals = base.urdf_visual_shapes
        
        shapeTypes=[v.geom_type for v in urdfVisuals]
        halfExtents=[[ext * 0.5 for ext in v.geom_extents] for v in urdfVisuals]
        radii=[v.geom_radius for v in urdfVisuals]
        lengths=[v.geom_length for v in urdfVisuals]
        fileNames=[v.geom_meshfilename for v in urdfVisuals]
        meshScales=[v.geom_meshscale for v in urdfVisuals]
        rgbaColors=[v.material_rgba for v in urdfVisuals]
        visualFramePositions=[v.origin_xyz for v in urdfVisuals]
        visualFrameOrientations=[p.getQuaternionFromEuler(v.origin_rpy) for v in urdfVisuals]                                                       
        baseVisualShapeIndex = -1

        if (len(shapeTypes)):
            #print("len(shapeTypes)=",len(shapeTypes))
            #print("len(halfExtents)=",len(halfExtents))
            #print("len(radii)=",len(radii))
            #print("len(lengths)=",len(lengths))
            #print("len(fileNames)=",len(fileNames))
            #print("len(meshScales)=",len(meshScales))
            #print("len(rgbaColors)=",len(rgbaColors))
            #print("len(visualFramePositions)=",len(visualFramePositions))
            #print("len(visualFrameOrientations)=",len(visualFrameOrientations))
            
                                                           
            baseVisualShapeIndex = p.createVisualShapeArray(shapeTypes=shapeTypes,
                        halfExtents=halfExtents,radii=radii,lengths=lengths,fileNames=fileNames,
                        meshScales=meshScales,rgbaColors=rgbaColors,visualFramePositions=visualFramePositions,
                        visualFrameOrientations=visualFrameOrientations,physicsClientId=physicsClientId)

        linkMasses=[]
        linkCollisionShapeIndices=[]
        linkVisualShapeIndices=[]
        linkPositions=[]
        linkOrientations=[]
        
        linkInertialFramePositions=[]
        linkInertialFrameOrientations=[]
        linkParentIndices=[]
        linkJointTypes=[]
        linkJointAxis=[]

        for joint in self.urdfJoints:
            link = joint.link
            linkMass = link.urdf_inertial.mass
            linkCollisionShapeIndex=-1
            linkVisualShapeIndex=-1
            linkPosition=[0,0,0]
            linkOrientation=[0,0,0]
            linkInertialFramePosition=[0,0,0]
            linkInertialFrameOrientation=[0,0,0]
            linkParentIndex=self.linkNameToIndex[joint.parent_name]
            linkJointType=joint.joint_type
            linkJointAx = joint.joint_axis_xyz
            linkShapeTypeArray=[]
            linkRadiusArray=[]
            linkHalfExtentsArray=[]
            lengthsArray=[]
            fileNameArray=[]
            linkMeshScaleArray=[]
            linkPositionsArray=[]
            linkOrientationsArray=[]
            
            for v in link.urdf_collision_shapes:
                shapeType = v.geom_type
                linkShapeTypeArray.append(shapeType)
                linkHalfExtentsArray.append([0.5*v.geom_extents[0],0.5*v.geom_extents[1],0.5*v.geom_extents[2]])
                linkRadiusArray.append(v.geom_radius)
                lengthsArray.append(v.geom_length)
                fileNameArray.append(v.geom_meshfilename)
                linkMeshScaleArray.append(v.geom_meshscale)
                linkPositionsArray.append(v.origin_xyz)
                linkOrientationsArray.append(p.getQuaternionFromEuler(v.origin_rpy))

            if (len(linkShapeTypeArray)):
                linkCollisionShapeIndex = p.createCollisionShapeArray(shapeTypes=linkShapeTypeArray,
                    radii=linkRadiusArray,
                    halfExtents=linkHalfExtentsArray,
                    lengths=lengthsArray,
                    fileNames=fileNameArray,
                    meshScales=linkMeshScaleArray,
                    collisionFramePositions=linkPositionsArray,
                    collisionFrameOrientations=linkOrientationsArray,
                    physicsClientId=physicsClientId)
                    
            urdfVisuals = link.urdf_visual_shapes
            linkVisualShapeIndex = -1
            shapeTypes=[v.geom_type for v in urdfVisuals]
            halfExtents=[[ext * 0.5 for ext in v.geom_extents] for v in urdfVisuals]
            radii=[v.geom_radius for v in urdfVisuals]
            lengths=[v.geom_length for v in urdfVisuals]
            fileNames=[v.geom_meshfilename for v in urdfVisuals]
            meshScales=[v.geom_meshscale for v in urdfVisuals]
            rgbaColors=[v.material_rgba for v in urdfVisuals]
            visualFramePositions=[v.origin_xyz for v in urdfVisuals]
            visualFrameOrientations=[p.getQuaternionFromEuler(v.origin_rpy) for v in urdfVisuals]
                
            if (len(shapeTypes)):
                linkVisualShapeIndex = p.createVisualShapeArray(shapeTypes=shapeTypes,
                            halfExtents=halfExtents,radii=radii,lengths=lengths,
                            fileNames=fileNames,meshScales=meshScales,rgbaColors=rgbaColors,
                            visualFramePositions=visualFramePositions,
                            visualFrameOrientations=visualFrameOrientations,
                            physicsClientId=physicsClientId)

            linkMasses.append(linkMass)
            linkCollisionShapeIndices.append(linkCollisionShapeIndex)
            linkVisualShapeIndices.append(linkVisualShapeIndex)
            linkPositions.append(joint.joint_origin_xyz)
            linkOrientations.append(p.getQuaternionFromEuler(joint.joint_origin_rpy))
            linkInertialFramePositions.append(link.urdf_inertial.origin_xyz)
            linkInertialFrameOrientations.append(p.getQuaternionFromEuler(link.urdf_inertial.origin_rpy))
            linkParentIndices.append(linkParentIndex)
            linkJointTypes.append(joint.joint_type)
            linkJointAxis.append(joint.joint_axis_xyz)
        
        obUids = [p.createMultiBody(baseMass,\
                    baseCollisionShapeIndex=baseCollisionShapeIndex,
                                        baseVisualShapeIndex=baseVisualShapeIndex,
                    basePosition=basePosition,
                    baseOrientation=baseOrientation,
                    baseInertialFramePosition=base.urdf_inertial.origin_xyz,
                    baseInertialFrameOrientation=p.getQuaternionFromEuler(base.urdf_inertial.origin_rpy),
                    linkMasses=linkMasses,
                    linkCollisionShapeIndices=linkCollisionShapeIndices,
                    linkVisualShapeIndices=linkVisualShapeIndices,
                    linkPositions=linkPositions,
                    linkOrientations=linkOrientations,
                    linkInertialFramePositions=linkInertialFramePositions,
                    linkInertialFrameOrientations=linkInertialFrameOrientations,
                    linkParentIndices=linkParentIndices,
                    linkJointTypes=linkJointTypes,
                    linkJointAxis=linkJointAxis,
                    physicsClientId=physicsClientId)
                for basePosition, baseOrientation in zip(basePositions, baseOrientations)]
        return obUids


if __name__ == "__main__":
    main()
