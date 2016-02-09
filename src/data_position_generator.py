import os
import math
import json

class DataPositionGenerator():
    """ This class generates a dataset of point in a defined space area.

    The area is a parallelepiped where u1, u2, u3 are three edge vectors and
    u0 the "origin" vertice.

    Points are uniformely generated along an axis. For example, if you want
    1000 points, it doesn't matter the shape of the parallelepiped (cube,
    cuboid, ...), each edge will be divided in 10 points.

    """
    def __init__(self, u0, u1, u2, u3, K, L):
        """
        Args:
            u0 (array): origin vertice
            u1 (array): edge vector
            u2 (array): edge vector
            u3 (array): edge vector
            K (int): desired number of initial points in the dataset
            L (int): desired number of linking points between initial points
        """

        self.u0 = u0
        self.u1 = u1
        self.u2 = u2
        self.u3 = u3
        self.K = K
        self.L = L

    def generate_initial_points(self):
        K_on_edge = int((self.K)**(1/3))+1

        interval_1 = [
            self.u1[0]/K_on_edge,
            self.u1[1]/K_on_edge,
            self.u1[2]/K_on_edge
        ]
        interval_2 = [
            self.u2[0]/K_on_edge,
            self.u2[1]/K_on_edge,
            self.u2[2]/K_on_edge
        ]
        interval_3 = [
            self.u3[0]/K_on_edge,
            self.u3[1]/K_on_edge,
            self.u3[2]/K_on_edge
        ]

        self.initial_points = []

        for i in range(K_on_edge):
            for j in range(K_on_edge):
                for k in range(K_on_edge):
                    self.initial_points.append([
                        self.u0[0]+i*interval_1[0]
                            +j*interval_2[0]
                            +k*interval_3[0],
                        self.u0[1]+i*interval_1[1]
                            +j*interval_2[1]
                            +k*interval_3[1],
                        self.u0[2]+i*interval_1[2]
                            +j*interval_2[2]
                            +k*interval_3[2]
                    ])

    def generate_linking_points(self, point):
        K_on_edge_L = (int((self.K)**(1/3))+1)*(self.L+1)

        interval_1 = [
            self.u1[0]/K_on_edge_L,
            self.u1[1]/K_on_edge_L,
            self.u1[2]/K_on_edge_L
        ]
        interval_2 = [
            self.u2[0]/K_on_edge_L,
            self.u2[1]/K_on_edge_L,
            self.u2[2]/K_on_edge_L
        ]
        interval_3 = [
            self.u3[0]/K_on_edge_L,
            self.u3[1]/K_on_edge_L,
            self.u3[2]/K_on_edge_L
        ]

        linking_points_1 = []
        for i in range(1,self.L+1):
            linking_points_1.append([
                point[0]+i*interval_1[0],
                point[1]+i*interval_1[1],
                point[2]+i*interval_1[2]
            ])

        linking_points_2 = []
        for i in range(1,self.L+1):
            linking_points_2.append([
                point[0]+i*interval_2[0],
                point[1]+i*interval_2[1],
                point[2]+i*interval_2[2]
            ])

        linking_points_3 = []
        for i in range(1,self.L+1):
            linking_points_3.append([
                point[0]+i*interval_3[0],
                point[1]+i*interval_3[1],
                point[2]+i*interval_3[2]
            ])

        return [linking_points_1, linking_points_2, linking_points_3]

    def generate_file(self, filename):
        """ The file looks like this :
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
              ]
            }
          ]
        }
        """
        json_obj = {}
        json_obj["K"] = self.K
        json_obj["L"] = self.L
        json_obj["dataset"] = []

        self.generate_initial_points()
        for point in self.initial_points:
            point_obj = {}
            point_obj["point"] = point
            linking_points = self.generate_linking_points(point)
            point_obj["linking_points"]=[linking_points[0],linking_points[1],
                linking_points[2]]

            json_obj["dataset"].append(point_obj)

        #TODO Check if the file already exists
        with open(filename, 'w') as fp:
            json.dump(json_obj, fp)
