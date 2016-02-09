## FollowingRobot
### Description
FollowingRobot is a class. It inherits from the Robot class of the Pypot package
from the poppy project. The main goal is to add the ability for a FollowingRobot
instance to follow another FollowingRobot instance.

A FollowingRobot  instance can't follow a Robot intance, the leader need to be a
FollowingRobot instance too !

Useful from_vrep and from_config function have been integrated to Following
Robot as method used during the initialization.

To define a robot as leader, its config needs to match the following robot
config in terms of motors orientation, angle_limit, offset and type.

### Usage
1. Instanciate two FollowingRobots, either real or simulated :

   ```python
   #Simulated robot
   robot1 = FollowingRobot(config = "/path/to/config", simulator = vrep, scene =  "/path/to/scene")
   #Real robot
   robot2 = FollowingRobot(config = "/path/to/config")
   ```

2. Set the robot1 as robot2 leader (make sure the configs match)

   ```python
   robot1.setLeader(robot2)
   ```

3. Start the following loop

   ```python
   robot1.startFollowing()
   ```

4. You can pause it at any moment with

   ```python
   robot1.stopFollowing()
   ```

5. To prevent a momentary blocking of your USB port, make sure to close the
   robot with this command (it's a pypot.Robot method)

   ```python
   robot1.close()
   ```

## DataPositionGenerator
### Description
This class generates a parallelepiped dataset. First, it creates K points
uniformly in the given area. Then, it links each of this points with their
neighbors.

For the initialization it takes 4 vectors :
* u0 is the "origin" vertex of the parallelepiped
* u1, u2, u3 are three vectors representing the three edges originating in the
  u0 vertex.

The output is a JSON file following this pattern :
``` json
{
  "K":1000,
  "L":10,
  "dataset":[
    {
      "point": [0,0,0],
      "linking_points_1": [
        [0.1, 0.1, 0.1],
        [0.5, 0.5, 0.5],
        [0.5, 0.5, 0.5],
        [0.5, 0.5, 0.5],
        [0.5, 0.5, 0.5],
      ],
      "linking_points_2":[

      ]
    },
    {
      "point": [0,0,0.5],
      "linking_points_1":[

      ]
    }
  ]
}
```
### Usage
``` python
gen = DataPositionGenerator(
    [0,0,0],
    [0,0,1],
    [0,1,0],
    [1,0,0],
    10,
    4
)

gen.generate_file(filename)
```
## GoalBabblingTrainer
### Description
Only two specific place : the g function in arguments and the compute_triplet
method. 
