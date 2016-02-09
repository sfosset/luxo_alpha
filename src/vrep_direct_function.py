
class VrepDirectFunction():
    def __init__(self, robot):

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

    def compute(self, control):
        """
        Note :
            * The object serving as effector must be called "effector"
            * Motor are acessed in name order
        """
        names = []
        for motor in self.robot.motors:
            names.append(motor.name)

        names.sort()

        for i in range(len(names)):
            self.set_motor_position(names[i], control[i])

        if self.check_for_collisions()==True:
            w_ext = 0
        else:
            w_ext = 1

        return [self.get_object_position("effector"), w_ext]


    def set_motor_position(self, motor_name, position):
        """Sets the motor position"""
        self.vrep_io.call_remote_api('simxSetJointPosition',
                                     self.vrep_io.get_object_handle(motor_name),
                                     position)
        #Don't precise sending=true make it using the normal mode

    def get_object_position(self, object_name, relative_to_object=None):
        """ Gets the object position. """
        #Taken from pypot.vrep.io

        h = self.vrep_io.get_object_handle(object_name)
        relative_handle = (-1 if relative_to_object is None
                           else self.get_object_handle(relative_to_object))

        return self.vrep_io.call_remote_api('simxGetObjectPosition',
                                    h,
                                    relative_handle)

    def read_collision(self, collision_name):
        """Gives the collision state for the given collision object"""
        h = self.vrep_io.call_remote_api('simxGetCollisionHandle',
                                     collision_name)
        print(h)
        return self.vrep_io.call_remote_api('simxReadCollision', h)

    def check_for_collisions(self):
        """Checks for collision among all the collision objects."""
        for collision in self.collision_list:
            if self.read_collision(collision) == True
                return True

        return False

    def stop_sim(self):
        self.vrep_io.stop_simulation()
