import numpy as np


from device_sync_parser import Ry, Rz, Rx  


def xyz_to_xyzrgb(xyzs):
    out = np.zeros(shape=(len(xyzs),6))
    out[:,:3,] = xyzs
    return out

class Bbox3D:
    def __init__(self, x, y, z, x_shift, y_shift, z_shift, roll, pitch, yaw):
        self.center = np.array([x,y,z]).T
        self.shifts = np.array([x_shift, y_shift, z_shift]).T
        self.R_angles_rpy = np.array([roll, pitch, yaw]).T
        self.getCube2DrawLines()
        # self.getCube()
        self.yaw(yaw)
        self.roll(roll)
        # тут не уверен, в статье нашел, что обычно преобразование идет Z(yaw)X(roll)Z(yaw)
        # (если будут ошибки с проекциями)
        self.yaw(pitch)
        # self.pitch(pitch)
        self.pts += self.center

    def ptsToDraw(self,color):
        cube = xyz_to_xyzrgb(self.pts)
        cube[:,-3:] = color 
        return cube

    def roll(self, angle): 
        for i in range(len(self.pts)):
           self.pts[i] = (Ry(angle) @self.pts[i])[0]
        return self.pts

    def yaw(self, angle): 
        for i in range(len(self.pts)):
            self.pts[i] = (Rz(angle) @ self.pts[i])[0]
        return self.pts

    def pitch(self, angle): 
        for i in range(len(self.pts)):
             self.pts[i] = (Rx(angle) @  self.pts[i])[0]
        return  self.pts
    

    def getCube(self):
        self.pts =  np.array(
            [
                np.array([-self.shifts[0], self.shifts[1], -self.shifts[2]]), # 1
                np.array([-self.shifts[0], -self.shifts[1], -self.shifts[2]]), # 2
                np.array([self.shifts[0], -self.shifts[1], -self.shifts[2]]), # 3
                np.array([self.shifts[0], self.shifts[1], -self.shifts[2]]), # 4
                np.array([self.shifts[0], self.shifts[1], self.shifts[2]]), # 5
                np.array([self.shifts[0], -self.shifts[1], self.shifts[2]]), # 6
                np.array([-self.shifts[0], -self.shifts[1], self.shifts[2]]), # 7
                np.array([-self.shifts[0], self.shifts[1], self.shifts[2]]), # 8
            ], dtype=np.float32
        )

    def getCube2DrawLines(self):
        self.pts = np.array(
            [
                # bottom
                np.array([-self.shifts[0], self.shifts[1], -self.shifts[2]]), # 1
                np.array([-self.shifts[0], -self.shifts[1], -self.shifts[2]]), # 2
                np.array([-self.shifts[0], -self.shifts[1], -self.shifts[2]]), # 2
                np.array([self.shifts[0], -self.shifts[1], -self.shifts[2]]), # 3
                np.array([self.shifts[0], -self.shifts[1], -self.shifts[2]]), # 3
                np.array([self.shifts[0], self.shifts[1], -self.shifts[2]]), # 4
                np.array([self.shifts[0], self.shifts[1], -self.shifts[2]]), # 4
                np.array([-self.shifts[0], self.shifts[1], -self.shifts[2]]), # 1
                # top
                np.array([self.shifts[0], self.shifts[1], self.shifts[2]]), # 5
                np.array([self.shifts[0], -self.shifts[1], self.shifts[2]]), # 6
                np.array([self.shifts[0], -self.shifts[1], self.shifts[2]]), # 6
                np.array([-self.shifts[0], -self.shifts[1], self.shifts[2]]), # 7
                np.array([-self.shifts[0], -self.shifts[1], self.shifts[2]]), # 7
                np.array([-self.shifts[0], self.shifts[1], self.shifts[2]]), # 8
                np.array([-self.shifts[0], self.shifts[1], self.shifts[2]]), # 8
                np.array([self.shifts[0], self.shifts[1], self.shifts[2]]), # 5
                # sides
                np.array([self.shifts[0], self.shifts[1], -self.shifts[2]]), # 4
                np.array([self.shifts[0], self.shifts[1], self.shifts[2]]), # 5
                np.array([self.shifts[0], -self.shifts[1], self.shifts[2]]), # 6
                np.array([self.shifts[0], -self.shifts[1], -self.shifts[2]]), # 3
                np.array([-self.shifts[0], -self.shifts[1], self.shifts[2]]), # 7
                np.array([-self.shifts[0], -self.shifts[1], -self.shifts[2]]), # 2
                np.array([-self.shifts[0], self.shifts[1], -self.shifts[2]]), # 1
                np.array([-self.shifts[0], self.shifts[1], self.shifts[2]]), # 8
                # front X
                np.array([-self.shifts[0], self.shifts[1], self.shifts[2]]), # 8 
                np.array([-self.shifts[0], -self.shifts[1], -self.shifts[2]]), # 2
                np.array([-self.shifts[0], -self.shifts[1], self.shifts[2]]), # 7
                np.array([-self.shifts[0], self.shifts[1], -self.shifts[2]]), # 1
            ], dtype=np.float32
        )