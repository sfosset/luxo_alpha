from pypot.vrep import from_vrep, close_all_connections
from polynomial_model import PolynomialModel
from vrep_direct_function_wo_pypot import VrepDirectFunctionWoPypot
from goal_babbling_trainer import GoalBabblingTrainer
import math
import time

def main():
    x_home = [0.05988241732120514, -0.004997074604034424, 0.2619549632072449]
    q_home = [-math.pi/4, math.pi/2, -math.pi/4, 0, 0]

    robot = from_vrep(scene = '../model_1/luxo_1_kinematic.ttt',
        config = '../model_1/config_luxo_1.json'
    )
    robot.stop_simulation()
    robot._controllers[0].io.call_remote_api('simxCloseScene')
    close_all_connections()

    # robot = {
    #     "motors":{
    #         "foot":{
    #             "id":12,
    #             "orientation":"direct",
    #             "type":"AX-12",
    #             "offset":0.0
    #         },
    #         "body_bottom":{
    #             "id":13,
    #             "orientation":"direct",
    #             "type":"AX-12",
    #             "angle_limit":[-90.0, 90.0],
    #             "offset":0.0
    #         },
    #         "body_middle":{
    #             "id":14,
    #             "orientation":"direct",
    #             "type":"AX-12",
    #             "angle_limit":[-130.0, 130.0],
    #             "offset":0.0
    #         },
    #         "body_top":{
    #             "id":15,
    #             "orientation":"direct",
    #             "type":"AX-12",
    #             "angle_limit":[-130.0, 130.0],
    #             "offset":0.0
    #         },
    #         "head":{
    #             "id":16,
    #             "orientation":"direct",
    #             "type":"AX-12",
    #             "offset":0.0
    #         }
    #     }
    # }

    f = VrepDirectFunctionWoPypot(robot)
    g = PolynomialModel(3,5,4,q_home)
    trainer = GoalBabblingTrainer(g,f,q_home,x_home, '../model_1/luxo_1_data_1.json')
    trainer.train(100,4,0.6)

if __name__ == '__main__':
    main()
