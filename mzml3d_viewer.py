# use https://github.com/OpenMS/OpenMS cpp code to find headers of pyopenms
import os
from tkinter import E
from graphviz import view
import pyopenms as ms
import numpy as np

from varname.helpers import debug

from opengl3d_viewer import opengl_viewer

import OpenGL.GL as gl
import OpenGL.GLU as glu
import OpenGL.GLUT as glut
from OpenGL.arrays import vbo
import device_sync_parser

import laspy

if __name__ == '__main__':
    viewer = opengl_viewer('out')
    seq = ms.AASequence.fromString("FPIANGDER") # create AASequence object from string representation
    prefix = seq.getPrefix(4) # extract prefix of length 4
    suffix = seq.getSuffix(5) # extract suffix of length 5
    concat = seq + seq # concatenate two sequences
    print(seq.getMonoWeight())

    # print string representation of sequences
    print("Sequence:", seq)
    print("Prefix:", prefix)
    print("Suffix:", suffix)
    print("Concatenated:", concat)
    print(concat.getMonoWeight())
    print(seq.getMZ(2))
    for aa in seq:
        # print(aa)
        print(aa.getName(), aa.getFormula())
    print(seq.getFormula())
    # exit()
    exp = ms.MSExperiment()
    ms.MzMLFile().load(
        # os.path.join('testdata', '02_PM_30102018_1.mzML'), 
        os.path.join('data', '59_PM_30102018_3.mzML'), 
        exp
    )
    debug(exp.getMSLevels())
    debug(exp.getNrSpectra())
    debug(exp.getNrChromatograms())
    for i in range(exp.getNrSpectra()):
        spectrum = exp.getSpectrum(i)
        mz, intensity = spectrum.get_peaks()

        print('spectr', i, mz.shape, intensity.shape)
        debug(mz.min())
        debug(mz.max())
        debug(intensity.min())
        debug(intensity.max())
    first_chr_mz, first_chr_intensity = exp.getSpectrum(0).get_peaks()
    debug(first_chr_mz.shape)    
    debug(first_chr_intensity.shape)    
    debug(exp.getNrSpectra())
    batch_samples = 1000
    batch_samples = len(first_chr_intensity)
    bathcs2draw = exp.getNrSpectra()
    bathcs2draw = 2
    # data_pts_cnt = exp.getNrSpectra() * len(first_chr_intensity) * 2
    data_pts_cnt = bathcs2draw * len(first_chr_intensity) * 2 * 2
    print(data_pts_cnt)
    dat = np.zeros(shape=(data_pts_cnt, 6))
    print(dat.shape)
    # exit()    
    from_batch_id = 0
    dat_id = -1
    for i in range(exp.getNrSpectra()):
        # if batch_samples == len(first_chr_intensity):
        #     from_batch_id = 0
        #     to_batch_id = batch_samples
        # else:
        #     to_batch_id = from_batch_id + batch_samples
        mz_spec = exp.getSpectrum(i)
        mz, intensity = mz_spec.get_peaks()
        # print(mz)
        for j in range(len(mz)):
            dat_id += 1
            dat[dat_id] = np.array([
                i * 1000,
                mz[j],
                intensity[j]/100,
                np.abs(1-i),
                np.abs(np.cos(i)),
                i*2
            ])
            dat_id += 1
            dat[dat_id] = np.array([
                i * 1000 + 500,
                mz[j],
                np.log(intensity[j]+1) * 10,
                np.abs(1-i),
                np.abs(np.cos(i)),
                i*2
                # 255,
                # 255,
                # 255
            ])
        if i == bathcs2draw:
            break
    print(dat)
    # exit()
    # dat -= dat.mean()
    ms_vbo = (
            vbo.VBO(
                data = np.array(dat, dtype = np.float32),
                usage = gl.GL_DYNAMIC_DRAW,
                target = gl.GL_ARRAY_BUFFER
            ),
            len(dat)
        )
    # viewer.data_buffer.drawVBOPts(ms_vbo)
    print(dat)
    print(dat.shape)
    print(dat[0])
    # exit()
    viewer.visualize(ms_vbo)

    