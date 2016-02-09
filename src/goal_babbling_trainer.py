import json
import math
import random
import time

def cos(a,b):
    res = 0
    for i in range(len(a)):
        res+=a[i]*b[i]
    return res

def norme(a):
    res = 0
    for i in range(len(a)):
        res+=a[i]**2
    return res

class GoalBabblingTrainer():

    def __init__(self, g, f, q_home, x_home, data_position):
        """
        Args:
            g (object): an instance of a class implementing the InverseKinematic
              abstract class
            robot (pypot.robot): the robot to train. Need to correspond to
              vrep_interface
            q_home (vector): the home configuration
            x_home (vector): the home effector position
            data_position (string): the filename of the json file containing the
              training dataset
        """

        self.f = f
        self.g = g
        self.q_home = q_home
        self.x_home = x_home

        with open(data_position) as data_file:
            self.data_position = json.load(data_file)

    def train(self, N, V, R):
        """ The main training function.

        Args:
            N (int): number of iterations
            V (int): number of disturbance functions
            R (float): disturbance range
        """

        self.generate_disturbance_function(V, R)

        home_quadruplet = [self.x_home, self.q_home, 1, self.x_home]
        for i in range(N):
            data_result = []
            for v in range(V):
                data_result.append(home_quadruplet)
                leeen = len(self.data_position["dataset"])
                inc = 0
                for point_obj in self.data_position["dataset"]:
                    inc+=1
                    print('%d\r'%(100*(i/N+v/(V*N)+inc/(V*N*leeen))), end="")
                    point = point_obj["point"]
                    # we don't care about the prev_quadruplet for the first point
                    # since it's used to compute weight and the first point
                    # doesn't have weight (and is not include in the
                    # data_result)
                    prev_quadruplet = self.compute_quadruplet(
                        point,
                        home_quadruplet,
                        v
                    )

                    linking_points=point_obj["linking_points"]
                    for j in range(len(linking_points)):
                        for linking_point in linking_points[j]:
                            prev_quadruplet = self.compute_quadruplet(
                                linking_point,
                                prev_quadruplet,
                                v
                            )
                            data_result.append(prev_quadruplet)

            self.g.update(data_result)


        self.g.store('last_params.json')


    def compute_quadruplet(self, x, prev_quadruplet, v ):
        """ Compute the quadruplet f(g), g, w, x for x (position) and v (disturbance)
        given.

        Note:
            * Since it computes the weights and the weights needs the previous
            quadruplet, it doesn't work for the initial points.
        """
        res = []
        g = self.g.compute(x)
        E_v = self.disturbance(x, v)

        g_v=[]
        for i in range(len(self.q_home)):
            g_v.append(g[i] + E_v[i])

        f, w_ext = self.f.compute(g_v)


        #TODO handle collision
        # via w_ext which is an external weight that could optionally be used

        df=[]
        for i in range(len(self.x_home)):
            df.append(f[i]-prev_quadruplet[0][i])

        dg=[]
        for i in range(len(self.q_home)):
            dg.append(g_v[i]-prev_quadruplet[1][i])

        dx=[]
        for i in range(len(self.x_home)):
            dx.append(x[i]-prev_quadruplet[3][i])

        w_dir = (1/2)*(1+cos(dx, df))
        w_eff = norme(df)/norme(dg)
        w = w_dir*w_eff*w_ext

        return [f, g_v, w, x]

    def generate_disturbance_function(self, V, R):
        """Linear disturbance following this formula :
        E = Ax+b
        """
        self.disturbance_functions = []
        for v in range(V):
            b_vector = []
            A_matrix = []
            for i in range(len(self.q_home)): # target space dimension
                b_vector.append(random.uniform(-R, R))
                A_matrix.append([])
                for j in range(len(self.x_home)): # start space dimension
                    A_matrix[i].append(random.uniform(-R, R))
                    self.disturbance_functions.append([A_matrix, b_vector])

    def disturbance(self, x, v):
        """ Compute the v-th disturbance function for the x vector
        """
        res = []
        A_matrix = self.disturbance_functions[v][0]
        b_vector = self.disturbance_functions[v][1]

        for i in range(len(self.q_home)):
            E = (x[0]*A_matrix[i][0] + x[1]*A_matrix[i][1] + x[2]*A_matrix[i][2] + b_vector[i])
            res.append(E)

        return res
