import numpy as np


def cube():
    vertices = np.array([[0,0,0],[10,0,0],[10,10,0],[0,10,0],
                         [0,0,10],[10,0,10],[10,10,10],[0,10,10]], dtype=float)
    triangles = np.array([[0,2,1],[0,3,2],[4,5,6],[4,6,7],
                          [0,1,5],[0,5,4],[1,2,6],[1,6,5],
                          [2,3,7],[2,7,6],[3,0,4],[3,4,7]])
    return vertices, triangles
