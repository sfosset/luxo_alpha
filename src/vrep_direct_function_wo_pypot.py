import vrep
import time

class VrepDirectFunctionWoPypot():
    def __init__(self, robot):
        self.ip = '127.0.0.1'
        self.port = 19997
        self.scene = '../model_1/luxo_1_kinematic.ttt'

        self.robot = robot
        self.collision_list = ['Collision0#',
                               'Collision1#',
                               'Collision5#',
                               'Collision8#',
                               'Collision9#',
                               'Collision10#',
                               'Collision11#',
                               'Collision14#',
                               'Collision15#']
        # It sucks the collision had to be defined here but the used collision
        # calculation module can't be fully accessed via the API and so it
        # is impossible to retrieve the list of collision defined in the vrep
        # scene.
        self.motor_handlers = []
        self.init_vrep_connection()


    def init_vrep_connection(self):
        vrep.simxFinish(-1) # just in case, close all opened connections
        self.client_id=vrep.simxStart(self.ip,self.port,True,True,5000,5) # Connect to V-REP

        if self.client_id!=-1:
            print ('Connected to remote API server on %s:%s' % (self.ip, self.port))
            res = vrep.simxLoadScene(self.client_id, self.scene, 1, vrep.simx_opmode_oneshot_wait)

            #get motor handler
            self.motor_handlers = []
            for motor in self.robot.motors:
                res, motor_handler = vrep.simxGetObjectHandle(
                    self.client_id,
                    motor.name,
                    vrep.simx_opmode_oneshot_wait
                )
                self.motor_handlers.append(motor_handler)
            self.motor_handlers.sort()
            print(self.motor_handlers)

            #get effector handler
            res, self.effector_handler = vrep.simxGetObjectHandle(
                self.client_id,
                'effector',
                vrep.simx_opmode_oneshot_wait
            )

            #get collision handler
            self.collision_handlers = []
            for collision in self.collision_list:
                res, collision_handler = vrep.simxGetObjectHandle(
                    self.client_id,
                    collision,
                    vrep.simx_opmode_oneshot_wait
                )
                self.collision_handlers.append(collision_handler)

            vrep.simxStartSimulation(self.client_id, vrep.simx_opmode_oneshot_wait)

    def compute(self, control):
        """
        Note :
            * The object serving as effector must be called "effector"
            * Motor are acessed in name order
        """
        for i in range(len(self.motor_handlers)):
            self.set_motor_position(self.motor_handlers[i], control[i])

        if self.check_for_collisions()==True:
            w_ext = 0
        else:
            w_ext = 1

        return [self.get_effector_position(), w_ext]


    def set_motor_position(self, motor_handler, position):
        """Sets the motor position"""
        #debut = time.time()
        vrep.simxSetJointPosition(self.client_id, motor_handler, position, vrep.simx_opmode_oneshot_wait)
        #dt = time.time()-debut
        #print(dt)

    def get_effector_position(self):
        """ Gets the object position. """
        res, tmp = vrep.simxGetObjectPosition(self.client_id, self.effector_handler, -1, vrep.simx_opmode_oneshot_wait)

        return tmp


    def check_for_collisions(self):
        """Checks for collision among all the collision objects."""
        for collision_handler in self.collision_handlers:
            res, tmp = vrep.simxReadCollision(self.client_id, collision_handler, vrep.simx_opmode_oneshot_wait)
            if tmp == True:
                return True

        return False
