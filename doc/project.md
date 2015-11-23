## The project
### Our goal
The initial idea was to create a robot able to move in a Luxo-style. Luxo is
the lamp in the famous 1986 Pixar's short-film *Luxo Jr.*, where two lamps
are playing with a ball. At some point in the film, the lamp seems to follow
the ball with head movements in a very *human*-way.

We would like to reproduce such a behavior with a robotic arm, equipped with a
camera as an effector, following a red ball. If we copy exactly Luxo's design,
the robotic arm would have 5 degree of freedom (5 revolute joints precisely).
This number is high enough to meet redundancy issues, and to quickly forget the
idea of an analytical solution due to its complexity.

So, we decide to head toward a machine learning of inverse kinematics.
Especially, we would like to apply the Matthias Rolf's goal babbling method,
which should have the advantage to be efficient in a 5-ish DOF case, and to
solve the redundancy issues with very efficient (an so *natural*) movements.
A description of this solution is given in the "Goal babbling permits direct
learning of inverse kinematics." section.


### Lamp design
The lamp design still have to be define. (A copy of Luxo with 5 DOF or another
design ?)

### "Goal babbling permits direct learning of inverse kinematics."


### Benchmarking for the simulations method
A quick order of magnitude calculus show that about ten millions of examples
are needed for the learning phase. Such a number could only be reach with
simulation method. So, we need to know which one to use to be both efficient
and accurate. Pure kinematics ? Dynamics ? Which level of abstraction for the
simulator (home-made, v-rep ?) ?
