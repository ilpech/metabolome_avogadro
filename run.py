import os
import numpy as np
import cv2
from typing import List
import re

np.set_printoptions(suppress=True)

class Frame:
    def __init__(self, frame_number, x, y, z, roll, pitch, yaw):
        self.frame_number = frame_number
        self.x = float(x) 
        self.y = float(y) 
        self.z = float(z)
        self.roll = float(roll)
        self.pitch = float(pitch)
        self.yaw = float(yaw)
    
    def xyz(self):
        return np.array([self.x, self.y, self.z])
    def xy(self):
        return np.array([self.x, self.y])
    def xyzrgb(self):
        return np.array([self.x, self.y, self.z, 0.0, 0.0, 0.0])

class Run:
    def __init__(self, run_number, run_directory):
        self.run_number = run_number
        self.run_directory = run_directory
        self.frames: List[Frame] = []