import os 
from typing import Tuple, List
import numpy as np
import random
import sys
from varname.helpers import debug
from typing import Tuple


import OpenGL.GL as gl 
import OpenGL.GLU as glu 
import OpenGL.GLUT as glut 
from OpenGL.arrays import vbo

import tools_n_helpers


from device_sync_parser import Frame
from bbox3d import Bbox3D

import pyopenms as ms

np.set_printoptions(formatter={"float": "{: 0.3f}".format})

from opengl3d_viewer import opengl_viewer

class BioViewer(opengl_viewer):
    def __init__(self, outpath, mzml_path):
        super(BioViewer, self).__init__(outpath)
        self.mzFilePath = mzml_path
        self.mzFile = ms.MSExperiment()
        ms.MzMLFile().load(
            mzml_path,
            self.mzFile
        )
        self.msMzCount = len(self.mzFile.getSpectrum(0).get_peaks()[0])
        self.drawMzml(3)

    
    def drawSpectra(
        self, 
        mz_spec, 
        sample_indx
    ):
        data_pts_cnt = self.loadedSamples * self.msMzCount * 2 * 2
        dat = np.zeros(shape=(data_pts_cnt, 6))
        dat_id = -1
        mz, intensity = mz_spec.get_peaks()
        for j in range(len(mz)):
            dat_id += 1
            dat[dat_id] = np.array([
                sample_indx * 1000,
                mz[j],
                intensity[j]/100,
                np.abs(1-sample_indx),
                np.abs(np.cos(sample_indx)),
                sample_indx*2
            ])
            dat_id += 1
            dat[dat_id] = np.array([
                sample_indx * 1000 + 500,
                mz[j],
                np.log(intensity[j]+1) * 10,
                np.abs(1-sample_indx),
                np.abs(np.cos(sample_indx)),
                sample_indx*2
            ])
        return dat
        

    def draw_points(self):
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glEnableClientState(gl.GL_COLOR_ARRAY)
        self.data_buffer.draw()
        self.data_buffer.drawVBOPts(self.mzml_vbo)
        self.data_buffer.drawVBOLines(self.bazis_vbo)
        gl.glDisableClientState(gl.GL_COLOR_ARRAY)
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
    
    def drawMzml(self, samples_cnt):
        if samples_cnt > self.mzFile.getNrSpectra():
            samples_cnt = self.mzFile.getNrSpectra()
        self.loadedSamples = samples_cnt
        data = []
        for i in range(self.loadedSamples):
            mz_spec = self.mzFile.getSpectrum(i)
            ms_pts = self.drawSpectra(mz_spec, i)
            data.append(ms_pts)
        dat = np.concatenate(data, axis=0)
        ms_vbo = (
            vbo.VBO(
                data = np.array(dat, dtype = np.float32),
                usage = gl.GL_DYNAMIC_DRAW,
                target = gl.GL_ARRAY_BUFFER
            ),
            len(dat)
        )
        self.mzml_vbo = ms_vbo
            

    