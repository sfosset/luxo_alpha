from pypot.robot import Robot
from pypot.vrep import vrep_time
import json
import time
import threading

# import for from_vrep
from functools import partial

from pypot.vrep.io import VrepIO

from pypot.vrep.controller import VrepController, VrepObjectTracker
from pypot.vrep.controller import VrepCollisionTracker, VrepCollisionDetector

from pypot.robot.sensor import ObjectTracker
from pypot.robot.config import motor_from_confignode, make_alias

import pypot.utils.pypot_time as pypot_time
import time as sys_time

# import for from_config
import pypot.sensor
import pypot.dynamixel
import pypot.dynamixel.io
import pypot.dynamixel.error
import pypot.dynamixel.motor
import pypot.dynamixel.syncloop

from pypot.robot.controller import DummyController
from pypot.robot.config import dxl_io_from_confignode, sensor_from_confignode, check_motor_limits, _motor_extractor

class FollowingRobot(Robot):
    # Check les configs
    # Change le controller
    """This class allow to create a new robot that can follow another leader
    robot.

    It is based on AbstractPoppyCreature class from the Poppy project

    Attribute:

    """

    def __init__(self, config, simulator=None,
                 vrep_host='127.0.0.1', vrep_port=19997, scene=None,
                 tracked_objects=[], tracked_collisions=[],
                 strict=True, sync=True, use_dummy_io=False,
                 leader=None, following_freq=20):
        """ Initialisation

        Args:
            sync (bool): choose if automatically starts the synchronization
                loops
            leader (FollowingRobot): the leading robot
        """

        if isinstance(config, str):
            with open(config) as f:
                config = json.load(f)

        if simulator is not None:
            if simulator == 'vrep':
                if scene is None:
                    raise ValueError('You must specify a scene to launch a vrep'
                                     ' simulation')

                # from_vrep call super().__init__
                self.from_vrep(config, vrep_host, vrep_port, scene,
                               tracked_objects, tracked_collisions)

            else:
                raise ValueError('Only vrep simulation is supported')

        else:
            # from_config call super().__init__
            self.from_config(config, strict, sync, use_dummy_io)

        self.config = config  # We need the config to later compare with the
                              # leader robot
        self.following = False
        self.leader = None
        self.following_freq = following_freq

        if leader is not None:
            self.set_leader(leader)

    def set_leader(self, leader):
        """ Set the leader robot.

        Args:
            leader (FollowingRobot): the leading robot
        """

        for sm in self.config['motors']:
            try:
                params = {'orientation', 'angle_limit', 'offset', 'type'}
                for param in params:
                    if (self.config['motors'][sm][param] !=
                        leader.config['motors'][sm][param]):

                        raise Exception('The robot can follow another robot'
                                        'only if their configs match')
            except KeyError:
                raise Exception('The robot can follow another robot only if'
                                'their configs match')

                # We could look directly for this motor param :
                # direct, lower_limit, upper_limit, offset, model
                # Problem : link between lower and upper limit is not
                # implemented for a V-REP simulation
        self.leader = leader

    def start_following(self):
        if self.following:
            self.stop_following()

        self.thread = threading.Thread(target=self.sync_loop)
        self.following = True
        self.thread.start()

    def stop_following(self):
        self.following = False

    def sync_loop(self):
        while self.following:

            start = time.time()
            # loop
            for motor in self.motors:
                motor.goal_position = getattr(self.leader,
                                              motor.name).present_position
            end = time.time()

            period = 1/self.following_freq
            dt = period - (end - start)
            if dt > 0:
                time.sleep(dt)

        self.following = False

    def from_vrep(self, config, vrep_host='127.0.0.1', vrep_port=19997,
                  scene=None, tracked_objects=[], tracked_collisions=[]):

        # This is a copy of the from_vrep function of pypot package
        # IMHO, it shouldn't be a stand-alone function but a pypot.Robot method
        # If that was the case, we wouldn't need to copy it here, and maintain it updated...

        """ Create a robot from a V-REP instance.

        :param config: robot configuration (either the path to the json or directly the dictionary)
        :type config: str or dict
        :param str vrep_host: host of the V-REP server
        :param int vrep_port: port of the V-REP server
        :param str scene: path to the V-REP scene to load and start
        :param list tracked_objects: list of V-REP dummy object to track
        :param list tracked_collisions: list of V-REP collision to track

        This function tries to connect to a V-REP instance and expects to find motors with names corresponding as the ones found in the config.

        .. note:: The :class:`~pypot.robot.robot.Robot` returned will also provide a convenience reset_simulation method which resets the simulation and the robot position to its intial stance.

        .. note:: Using the same configuration, you should be able to switch from a real to a simulated robot just by switching from :func:`~pypot.robot.config.from_config` to :func:`~pypot.vrep.from_vrep`.
            For instance::

                import json

                with open('my_config.json') as f:
                    config = json.load(f)

                from pypot.robot import from_config
                from pypot.vrep import from_vrep

                real_robot = from_config(config)
                simulated_robot = from_vrep(config, '127.0.0.1', 19997, 'poppy.ttt')

        """
        vrep_io = VrepIO(vrep_host, vrep_port)

        vreptime = vrep_time(vrep_io)
        pypot_time.time = vreptime.get_time
        pypot_time.sleep = vreptime.sleep

        if isinstance(config, str):
            with open(config) as f:
                config = json.load(f)

        motors = [motor_from_confignode(config, name)
                  for name in list(config['motors'].keys())]

        vc = VrepController(vrep_io, scene, motors)
        vc._init_vrep_streaming()

        sensor_controllers = []

        if tracked_objects:
            sensors = [ObjectTracker(name) for name in tracked_objects]
            vot = VrepObjectTracker(vrep_io, sensors)
            sensor_controllers.append(vot)

        if tracked_collisions:
            sensors = [VrepCollisionDetector(name) for name in tracked_collisions]
            vct = VrepCollisionTracker(vrep_io, sensors)
            sensor_controllers.append(vct)

        super().__init__(motor_controllers=[vc],
                         sensor_controllers=sensor_controllers)

        for m in self.motors:
            m.goto_behavior = 'minjerk'

        init_pos = {m: m.goal_position for m in self.motors}

        make_alias(config, self)

        def start_simu():
            vrep_io.start_simulation()

            for m, p in init_pos.items():
                m.goal_position = p

            vc.start()

            if tracked_objects:
                vot.start()

            if tracked_collisions:
                vct.start()

            while vrep_io.get_simulation_current_time() < 1.:
                sys_time.sleep(0.1)

        def stop_simu():
            if tracked_objects:
                vot.stop()

            if tracked_collisions:
                vct.stop()

            vc.stop()
            vrep_io.stop_simulation()

        def reset_simu():
            stop_simu()
            sys_time.sleep(0.5)
            start_simu()

        self.start_simulation = start_simu
        self.stop_simulation = stop_simu
        self.reset_simulation = reset_simu

        def current_simulation_time(robot):
            return robot._controllers[0].io.get_simulation_current_time()

        Robot.current_simulation_time = property(lambda robot: current_simulation_time(robot))

        def get_object_position(robot, object, relative_to_object=None):
            return vrep_io.get_object_position(object, relative_to_object)

        Robot.get_object_position = partial(get_object_position, self)

        def get_object_orientation(robot, object, relative_to_object=None):
            return vrep_io.get_object_orientation(object, relative_to_object)

        Robot.get_object_orientation = partial(get_object_orientation, self)



    def from_config(self, config, strict=True, sync=True, use_dummy_io=False):
        """ Returns a :class:`~pypot.robot.robot.Robot` instance created from a configuration dictionnary.

            :param dict config: robot configuration dictionary
            :param bool strict: make sure that all ports, motors are availaible.
            :param bool sync: choose if automatically starts the synchronization loops

            For details on how to write such a configuration dictionnary, you should refer to the section :ref:`config_file`.

            """

        alias = config['motorgroups']

        # Instantiate the different motor controllers
        controllers = []
        for c_name, c_params in list(config['controllers'].items()):
            motor_names = sum([_motor_extractor(alias, name)
                               for name in c_params['attached_motors']], [])

            attached_motors = [motor_from_confignode(config, name)
                               for name in motor_names]

            # at least one of the motor is set as broken
            if [m for m in attached_motors if m._broken]:
                strict = False

            attached_ids = [m.id for m in attached_motors]
            if not use_dummy_io:
                dxl_io = dxl_io_from_confignode(config, c_params, attached_ids, strict)

                check_motor_limits(config, dxl_io, motor_names)

                syncloop = (c_params['syncloop'] if 'syncloop' in c_params
                            else 'BaseDxlController')
                SyncLoopCls = getattr(pypot.dynamixel.syncloop, syncloop)

                c = SyncLoopCls(dxl_io, attached_motors)
                controllers.append(c)
            else:
                controllers.append(DummyController(attached_motors))

        super().__init__(motor_controllers=controllers, sync=sync)

        make_alias(config, self)

        # Create all sensors and attached them
        if 'sensors' in config and not use_dummy_io:
            sensors = []
            for s_name in list(config['sensors'].keys()):
                sensor = sensor_from_confignode(config, s_name, self)
                setattr(self, s_name, sensor)
                sensors.append(sensor)

            self.sensors.extend(sensors)
            [s.start() for s in sensors if hasattr(s, 'start')]
