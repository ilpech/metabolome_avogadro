# use https://github.com/OpenMS/OpenMS cpp code to find headers of pyopenms
import os
from tkinter import E
from graphviz import view
import pyopenms as ms
import numpy as np

from varname.helpers import debug

from bioviewer import BioViewer

import OpenGL.GL as gl
import OpenGL.GLU as glu
import OpenGL.GLUT as glut
from OpenGL.arrays import vbo


if __name__ == '__main__':
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

    mzml_path = os.path.join('testdata', '02_PM_30102018_1.mzML') 
    # mzml_path = os.path.join('data', '59_PM_30102018_3.mzML'), 
    viewer = BioViewer('out', mzml_path=mzml_path)
    viewer.visualize()