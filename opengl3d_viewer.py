import os 
from typing import Tuple, List
import numpy as np
import random
import sys
from varname.helpers import debug
from typing import Tuple

from PIL import Image

import OpenGL.GL as gl 
import OpenGL.GLU as glu 
import OpenGL.GLUT as glut 
from OpenGL.arrays import vbo

import tools_n_helpers

import cv2

from device_sync_parser import Frame
from bbox3d import Bbox3D

np.set_printoptions(formatter={"float": "{: 0.3f}".format})

from opengl_base import pcl_image

class opengl_viewer(pcl_image):
    def __init__(self, outpath, winname='MOLE3D'):
        self.winname = winname
        super(opengl_viewer, self).__init__(outpath)
        self.current_GL_image = None
        self.previous_GL_image = None
        self.out_image = None
        self.ffmpeg_frame = 0
        self.height = 1024
        self.width = 1024
        self.drawBazis()

    def main(self):
        self.location = np.array([0.0,0.0,10.0])
        self.focus = np.array([1.0,1.0,0.0])
        self.up = np.array([0.0,0.0,1.0])
        self.mousex = 0
        self.mousey = 0
        self.mouse_drag = gl.GL_FALSE
        glut.glutInit(sys.argv)
        glut.glutInitContextFlags(glut.GLUT_FORWARD_COMPATIBLE);
        glut.glutInitDisplayMode(glut.GLUT_RGB | glut.GLUT_DOUBLE | glut.GLUT_DEPTH)
        glut.glutInitWindowSize(self.height,self.width)
        glut.glutInitWindowPosition(10,10)
        glut.glutCreateWindow(self.winname)
        glut.glutDisplayFunc(self.display)
        glut.glutReshapeFunc(self.reshape)
        glut.glutMouseFunc(self.mouse)
        glut.glutMotionFunc(self.mouse_motion)
        glut.glutKeyboardFunc(self.keyboard)
        # gl.glClearColor(0.0,0.0,0.0,1.0)
        gl.glClearColor(0.3,0.3,0.3,1.0)
        glut.glutTimerFunc(10,self.timerEvent,1)
        glut.glutReshapeWindow(self.height,self.width);
        self.screenshot_mode = False
        if self.screenshot_mode:
            glut.glutHideWindow()
        glut.glutMainLoop()
        return 0

    def framesCnt(self):
        return len(self.run.frames)
        
    def nextFrame(self):
        print('next', self.frame_number)
        self.frame_number += 1
        if self.frame_number >= self.framesCnt()-1:
            self.frame_number = 0
        frame: Frame = [x for x in self.run.frames if x.frame_number == self.frame_number][0]
        self.processFrame(frame)
        
    def previousFrame(self):
        self.frame_number -= 1
        print('prev', self.frame_number)
        if self.frame_number < 0:
            self.frame_number = self.framesCnt()-1
        frame: Frame = [x for x in self.run.frames if x.frame_number == self.frame_number][0]
        self.processFrame(frame)
    
    def processFrame(self, frame: Frame):
        print('processFrame({:03d}'.format(frame.frame_number))
        roll = frame.roll*np.pi/180.0
        pitch = frame.pitch*np.pi/180.0
        yaw = -frame.yaw*np.pi/180.0 + np.pi
        location = frame.xyzrgb() - self.means
        self.location = location[:3]
        pointing = np.array([1,0,0])
        self.up = np.array([0,0,1])
        # yaw
        newpointing = self.rotate_vector(pointing, self.up, yaw)
        self.focus = self.location + newpointing


    def draw_points(self):
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glEnableClientState(gl.GL_COLOR_ARRAY)
        self.data_buffer.draw()
        self.data_buffer.drawVBOLines(self.bazis_vbo)
        gl.glDisableClientState(gl.GL_COLOR_ARRAY)
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
         

    def display(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glLoadIdentity()
        glu.gluLookAt(self.location[0], self.location[1], self.location[2], 
                      self.focus[0],self.focus[1], self.focus[2] ,
                      self.up[0], self.up[1], self.up[2])
        self.draw_points()
        glut.glutSwapBuffers()
        gl.glReadBuffer(gl.GL_FRONT)
        
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
        frame_info = f'frame::{self.frame_number}'
        loc_info = f'loc::{self.location}'
        focus_info = f'focus::{self.focus}'
        up_info = f'up::{self.up}'
        tools_n_helpers.putTexts(
            im,
            [frame_info,loc_info, focus_info, up_info],
            (10, 10),
            20,
            0,
            (0,200,0),
            1.0
        )
        self.previous_GL_image = self.current_GL_image
        self.current_GL_image = im / 255.0
        self.out_image = self.current_GL_image
        img_outpath = os.path.join(self.outpath, '{:08d}.png'.format(self.ffmpeg_frame))
        # out_resized = cv2.resize(self.out_image, None, fx=.25, fy=.25)
        out_resized = self.out_image
        # cv2.imshow('GL2CV', out_resized)
        # cv2.waitKey(1)
        out_resized *= 255.0
        cv2.imwrite(img_outpath, out_resized)
        self.ffmpeg_frame += 1
        print(f'img written to {img_outpath}')

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

        elif key == b"k":
            self.previousFrame()
        elif key == b"l":
            self.nextFrame()
        print(key)
        pass

    def drawTestCubes(self):
        test_cube = Bbox3D(0, 0, 100, 5, 10, 20, 0,0,0)    
        cube_pts = test_cube.ptsToDraw(np.array([1,1,0]))
        test_cube2 = Bbox3D(0, 0, 100, 5, 10, 20, 0,300*np.pi/180.0,0)
        cube_pts2 = test_cube2.ptsToDraw(np.array([0,1,1]))
        cubes_pts = np.concatenate([cube_pts,cube_pts2],axis=0) 
        cube_vbo = (
            vbo.VBO(
                data = np.array(cubes_pts, dtype = np.float32),
                usage = gl.GL_DYNAMIC_DRAW, 
                target = gl.GL_ARRAY_BUFFER
            ),
            len(cubes_pts)
        )
    
    def drawBazis(self):
        xyz_bazis = np.array([
            [0,0,0,1,0,0],
            [19000,0,0,1,0,0],
            [0,0,0,0,0,1],
            [0,10000,0,0,0,1],
            [0,0,0,0,1,0],
            [0,0,10000,0,1,0],
        ])
        self.bazis_vbo = (
            vbo.VBO(
                data = np.array(xyz_bazis, dtype = np.float32),
                usage = gl.GL_DYNAMIC_DRAW, 
                target = gl.GL_ARRAY_BUFFER
            ),
            len(xyz_bazis)
        )

    def visualize(self):
        print('VIEWER: RUN')
        self.main()

