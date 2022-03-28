import os 
from typing import Tuple
from black import out
import laspy
from matplotlib.pyplot import sca
import numpy as np
import random
import sys
from varname.helpers import debug
from typing import Tuple

from PIL import Image

# OpenGL library doesn't support absolute import for gl, glu, glut, or arrays
import OpenGL.GL as gl 
import OpenGL.GLU as glu 
import OpenGL.GLUT as glut 

from vbo_provider import VBO_Provider

import tools_n_helpers

import cv2

np.set_printoptions(formatter={"float": "{: 0.3f}".format})

# Skip debugging for speedup
#OpenGL.ERROR_CHECKING = False

# Skip logging for speedup 
#OpenGL.ERROR_LOGGING = False


class pcl_image():
    def __init__(self, file_object, mode, dim, outpath=None):
        self.file_object = file_object
        self.read_data(mode, dim)
        self.movement_granularity = .5
        self.look_granularity = 16.0
        self.outpath = outpath
        if self.outpath is not None:
            self.outpath = os.path.join(outpath, tools_n_helpers.curDateTime())
            os.makedirs(self.outpath, exist_ok=True)
        self.frame_number = -1
        
    
    def visualize(self):
        print('VIEWER: RUN')
        self.main()

    def main(self):
        self.location = np.array([0.0,0.0,100.0])
        self.focus = np.array([0.0,0.0,0.0])
        self.up = np.array([1.0,0.0,0.0])

        self.mousex = 0
        self.mousey = 0
        self.mouse_drag = gl.GL_FALSE


        # Wire up GL
        glut.glutInit(sys.argv)
        glut.glutInitContextFlags(glut.GLUT_FORWARD_COMPATIBLE);

        glut.glutInitDisplayMode(glut.GLUT_RGB | glut.GLUT_DOUBLE | glut.GLUT_DEPTH)
        glut.glutInitWindowSize(1024,1024)
        glut.glutInitWindowPosition(10,10)
        glut.glutCreateWindow("GLVIEWER_MODIFIED")
        glut.glutDisplayFunc(self.display)
        glut.glutReshapeFunc(self.reshape)
        glut.glutMouseFunc(self.mouse)
        glut.glutMotionFunc(self.mouse_motion)
        glut.glutKeyboardFunc(self.keyboard)
        gl.glClearColor(0.0,0.0,0.0,1.0)
        glut.glutTimerFunc(10,self.timerEvent,1)
        glut.glutReshapeWindow(1024, 1024);
        self.screenshot_mode = False
        if self.screenshot_mode:
            glut.glutHideWindow()
        glut.glutMainLoop()
        return 0
 
    def read_data(self, mode, dim):
        if (np.max(self.file_object.x) - np.min(self.file_object.x)) < 1:
            self.means = np.array([np.mean(self.file_object.X, dtype = np.float64), 
                          np.mean(self.file_object.Y, dtype = np.float64), 
                          np.mean(self.file_object.Z, dtype = np.float64),
                          0,0,0])
            self.scaled = False
        else:
            self.means = np.array([np.mean(self.file_object.x, dtype = np.float64), 
                    np.mean(self.file_object.y, dtype = np.float64), 
                    np.mean(self.file_object.z, dtype = np.float64),
                    0,0,0])
            self.scaled = True
        
        self.N = len(self.file_object)
        self.data_buffer = VBO_Provider(self.file_object, 1000000, self.means, mode, dim, self.scaled) 
 
    def reshape(self, w, h):
        # print("Reshape " + str(w) + ", " + str(h))
        ratio = w if h == 0 else float(w)/h
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glViewport(0,0,w,h)
        gl.glLoadIdentity()
        glu.gluPerspective(90,float(ratio),0.001,3000);

        gl.glMatrixMode(gl.GL_MODELVIEW)
        
    def timerEvent(self, arg):
        # Do stuff
        glut.glutPostRedisplay()
        glut.glutTimerFunc(10,self.timerEvent,1)

    def draw_points(self, num):
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glEnableClientState(gl.GL_COLOR_ARRAY)
        self.data_buffer.draw()
        gl.glDisableClientState(gl.GL_COLOR_ARRAY)
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
         
        
            
    def rotate_vector(self, vec_rot, vec_about, theta):
        d = np.sqrt(vec_about.dot(vec_about))
        L = np.array((0,vec_about[2], -vec_about[1], 
                    -vec_about[2], 0, vec_about[0],
                    vec_about[1], -vec_about[0], 0))
        L.shape = (3,3)
        try:
           R = (np.identity(3) + np.sin(theta)/d*L +
                    (1-np.cos(theta))/(d*d)*(L.dot(L)))
        except:
            print("Error in rotation.")
            return()
        return(vec_rot.dot(R))

    def display(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glLoadIdentity()
        glu.gluLookAt(self.location[0], self.location[1], self.location[2], 
                      self.focus[0],self.focus[1], self.focus[2] ,
                      self.up[0], self.up[1], self.up[2])
        self.draw_points(self.N)
        glut.glutSwapBuffers()
        gl.glReadBuffer(gl.GL_FRONT)
        self.height = 1024
        self.width = 1024
        glut.glutReshapeWindow(self.height, self.width)
        img = gl.glReadPixels(
            0, 
            0, 
            self.height, 
            self.width, 
            gl.GL_BGR, 
            gl.GL_UNSIGNED_BYTE
        )
        image = Image.frombytes('RGB', (self.width, self.height), img)
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        im = np.array(image.getdata(), np.uint8).reshape(
            self.height,
            self.width, 
            3
        )
        loc_info = f'loc::{self.location}'
        focus_info = f'focus::{self.focus}'
        up_info = f'up::{self.up}'
        tools_n_helpers.putTexts(
            im,
            [loc_info, focus_info, up_info],
            (10, 10),
            20,
            0,
            (0,200,0),
            1.0
        )
        # print('...preparing screenshot')
        self.frame_number += 1
        if self.outpath is not None:
            img_outpath = os.path.join(self.outpath, '{:08d}.png'.format(self.frame_number))
            cv2.imwrite(img_outpath, im)
            print(f'img written to {img_outpath}')
        # cv2.waitKey(1)
        
        # print(img)
        
    def reset_rotation(self):
        self.up = np.array([0,0,1])
        self.focus = np.array([0,0,0])

    def camera_reset(self):
        self.location = np.array([0.0,0.0,1500.0])
        self.focus = np.array([0.0,0.0,0.0])
        self.up = np.array([1.0,0.0,0.0])

    def camera_move(self,ammount, axis = 1):
        if axis == 1:
            pointing = self.focus - self.location
            pnorm = np.sqrt(pointing.dot(pointing))
            pointing /= pnorm
            self.location = self.location + ammount*pointing
            self.focus = self.location + pnorm*pointing
        elif axis == 2:
            pointing = self.focus - self.location
            direction = np.cross(self.up, pointing)
            direction /= np.sqrt(direction.dot(direction))
            self.location = self.location + ammount * direction
            self.focus = self.location + pointing
            
  
    def camera_set_yaw(self, theta):
        pointing = self.focus - self.location
        newpointing = self.rotate_vector(pointing, self.up, theta)
        self.focus = newpointing + self.location
    
    def camera_yaw(self, theta):
        pointing = self.focus - self.location
        newpointing = self.rotate_vector(pointing, self.up, theta)
        self.focus = newpointing + self.location

    def camera_roll(self, theta):
        self.up = self.rotate_vector(self.up, self.focus-self.location, theta)

    def camera_pitch(self,theta):
        pointing = self.focus - self.location
        axis = np.cross(self.up, pointing)
        newpointing = self.rotate_vector(pointing, axis, theta)
        self.focus = newpointing + self.location
        self.up = np.cross(newpointing, axis)
        self.up /= np.sqrt(self.up.dot(self.up))

    def mouse(self, button, state, x, y):
        if button == glut.GLUT_LEFT_BUTTON:
            if state == glut.GLUT_DOWN:
                self.mouse_drag = gl.GL_TRUE
                self.mousex = x
                self.mousey = y
            elif state == glut.GLUT_UP and self.mouse_drag:
                self.mouse_drag = gl.GL_FALSE
        elif button == 3:
            #Scoll up
            pass
        elif button == 4:
            #Scroll down
            pass

    def mouse_motion(self,x,y):
        if self.mouse_drag:
            self.mousex = x
            self.mousey = y

    def keyboard(self,key, x, y):
        ## Looking
        if key == b"a":
            self.camera_yaw(np.pi/(self.look_granularity))
        elif key == b"d":
            self.camera_yaw(-np.pi/self.look_granularity)
        elif key == b"w":
            self.camera_pitch(-np.pi/self.look_granularity)
        elif key == b"s":
            self.camera_pitch(np.pi/self.look_granularity)
        elif key == b"e":
            self.camera_roll(np.pi/self.look_granularity)
        elif key == b"q":
            self.camera_roll(-np.pi/self.look_granularity)
        ## Moving
        elif key == b"W":
            self.camera_move(self.movement_granularity * 100.0)
        elif key == b"S":
            self.camera_move(self.movement_granularity *-100.0)
        elif key == b"A":
            self.camera_move(self.movement_granularity * 100.0, axis = 2)
        elif key == b"D":
            self.camera_move(self.movement_granularity * -100.0, axis = 2)

        elif key in (b"R", b"r"):
            self.camera_reset()


        elif key == b"+":
            self.movement_granularity *= 0.8
            self.look_granularity /= 0.8
        elif key == b"-":
            self.movement_granularity /= 0.8
            self.look_granularity *= 0.8
        elif key in (b"x", b"y", b"z"):
            self.set_up_axis(key)
        print(key)
        pass

    def set_up_axis(self, key):
        if key == b"x":
            self.up = np.array([1.0, 0.0001, 0.0001])
            self.focus[0] = self.location[0]
        elif key == b"y":
            self.up = np.array([0.0001, 1.0, 0.0001])
            self.focus[1] = self.location[1]
        elif key == b"z":
            self.up = np.array([0.0001, 0.0001, 1.0])
            self.focus[2] = self.location[2]
        if all(self.focus == self.location):
            self.focus[{"x":1, "y":2, "z":0}[key]] += 1500

