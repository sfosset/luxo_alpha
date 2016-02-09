class VrepInterface():
    """Gives a framework to produce movements examples for a given vrep
    simulated pypot.robot instance.
    Why the need to add it to the existing vrep implementation in pypot.robot ?
    Because 1)pure kinematic mode 2)collision handler
    """
    #Add an abstract class tester to implement here
    def __init__(self, robot):
        self.robot = robot
        self.vrep_io = robot._controllers[0].io
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
            #print('ok\n')
            print(self.read_collision(collision))
            #if self.read_collision(collision) == True

    def stop_sim(self):
        self.vrep_io.stop_simulation()
        
