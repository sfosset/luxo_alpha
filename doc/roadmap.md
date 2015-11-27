## Roadmap
Here is a very detailed list of little tasks I worked on during the project.
Mainly for a personal use, you'll find more information about the project
progression in project.md

* Downloading v-rep [here](http://www.coppeliarobotics.com/downloads.html)
  * It's just a tar.gz to extract. No installation. Launch vrep.sh to launch
    v-rep
* Installing pip to manage python package. (via pacman)
* Installing pypot via pip.
  * Warning : with my linux distribution (Arch-like) the Sci-Py dependency
    failed. I had to install blas, gcc-fortran and lapack via pacman to make
    it work. The compilation time is very long.
* Installing ipython via pip to use ipython notebook. (Ipython project
  structure change short after and I needed to install jupyter to use the
  ipython notebook)
* Reading ipython notebook tutorials about poppy and his v-rep simulation
  * Had to install matplotlib via pip to fully do it
* Can't acess the USB port. Had to add the user to the right group to do so.
  ```bash
  usermod -aG additional_groups username
  ```

* Downloading CAD models of the bioloids [here](http://en.robotis.com/BlueAD/board.php?bbs_id=downloads&mode=view&bbs_no=26324&page=1&key=&keyword=&sort=&scate=DRAWING).
Converting them to mesh (.stl) files with FreeCAD (by writing a FreeCAD macro)
  * The CAD model of the motor itself is in multiple part. Had to do
  make compound, then shape to mesh to convert it.
* Designing a first two-motor robot for the tests.
  * Writing the corresponding config_1.json
  * Making a v-rep scene scene_1.ttt to simulate the robot. Based on the
    existing Poppy scene. (Warning : make sure to copy force and timer)
* Writing of FollowingRobot, a pypot.Robot implementation that allow a robot to
  follow another robot (real or simulated)
  * Note on the compliance : compliant = true for a robot make it compliant but
    you can't control it anymore. If the goal is to manually move the leader
    and see the follower mimic the movements, make sure to set leader
    compliance to true and follower compliance to false.
* Reading a first article about a method for learning inverse kinematics
  * Rolf, Matthias, and Minoru Asada. "Learning Inverse Models in High Dimensions with Goal Babbling and Reward-Weighted Averaging." *Workshop on Advances in Machine Learning for Sensorimotor Control.* 2013.
* Reading a more detailed article about goal babbling
  * Rolf, Matthias, Jochen J. Steil, and Michael Gienger. "Goal babbling permits direct learning of inverse kinematics." *Autonomous Mental Development, IEEE Transactions on* 2.3 (2010): 216-229.
* Adding a lot of documentation to the project
* [TODO] Designing the arm
* [TODO] Benchmarking simulation method. Make a choice.
* [TODO] Choose g function, and optimization method.
