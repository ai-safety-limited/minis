import pybullet as p, os, sys, numpy as np, time

print("***************** Please test FPS with p.DIRECT! **********************")
N,STEPS,PROFILE,INTERFACE = 2,1000,True,p.DIRECT 
# N,STEPS,PROFILE,INTERFACE = 2,1000,True,p.DIRECT
# N,STEPS,PROFILE,INTERFACE = 2,1000,False,p.DIRECT

org = p.connect(INTERFACE)
p.setAdditionalSearchPath("data")

#set physics parameters
p.setGravity(0,0,-9.8)

# NOTE: 
# with fewer than numSolverIterations=32, numSubSteps=4
# some of the minis-es will fall -> physics is broken
p.setTimeStep(0.033)
p.setPhysicsEngineParameter(numSolverIterations=32, numSubSteps=4)
p.setPhysicsEngineParameter(enableConeFriction=0)


plane = p.loadURDF("plane.urdf")
p.loadURDF("plane.urdf",[0,0,0], useMaximalCoordinates=True)
for x in range(-N, N):
    for y in range(-N, N):
        orientation = p.getQuaternionFromEuler([3.14157 / 2, 0.1 * x, 0.1 * y])
        minis = p.loadURDF("minis.urdf", (x,y,.282), orientation,
                   flags = p.URDF_USE_INERTIA_FROM_FILE)
        
        # activate servos (to hold pos = 0).
        for i in range(p.getNumJoints(minis)):
            motor_id, joint_name, joint_type = p.getJointInfo(minis, i)[:3]            
            if joint_type == p.JOINT_REVOLUTE:
                p.resetJointState(minis, motor_id, targetValue=0, targetVelocity=0)
    
                p.setJointMotorControl2(
                    bodyIndex=minis, jointIndex=motor_id, controlMode=p.POSITION_CONTROL,
                    targetPosition=0, positionGain=1.0, velocityGain=0.1,
                    force=1.2748, maxVelocity=2.083)




#step the simulation for STEPS steps
time_start = time.time()
for i in range(STEPS):
    if PROFILE and i == 30: logId=p.startStateLogging(p.STATE_LOGGING_PROFILE_TIMINGS, "stepTimings")
    p.stepSimulation()
    if PROFILE and i == 40: p.stopStateLogging(logId)

time_end = time.time()

print("FPS TOTAL = ", 4*N*N*STEPS / (time_end - time_start), "STEP = ", (time_end - time_start) * 1000 / STEPS, "ms")
