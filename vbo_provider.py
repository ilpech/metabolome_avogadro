import OpenGL.GL as gl 
import OpenGL.GLU as glu 
import OpenGL.GLUT as glut 
from OpenGL.arrays import vbo
import numpy as np

from typing import Tuple

from varname.helpers import debug

np.set_printoptions(formatter={"float": "{: 0.3f}".format})

class VBO_Provider():
    def __init__(self):
        self.vbos = []
        self.allcolor = False # pichugin: ?
    
    def slice_file(self,start_idx, end_idx, means, scaled):
        if scaled:
            return(
                np.array(
                    np.vstack(
                        (
                            self.file_object.x[start_idx:end_idx], 
                            self.file_object.y[start_idx:end_idx], 
                            self.file_object.z[start_idx:end_idx], 
                            np.zeros(end_idx - start_idx),
                            np.zeros(end_idx - start_idx),
                            np.zeros(end_idx - start_idx)
                        )
                    ).T
                ) - means
            )
        else:
            scale = np.array(self.file_object.header.scale + [0,0,0], dtype = np.float64)
            dat = (np.array(np.vstack((self.file_object.X[start_idx:end_idx], self.file_object.Y[start_idx:end_idx], self.file_object.Z[start_idx:end_idx], 
                                  np.zeros(end_idx - start_idx),np.zeros(end_idx - start_idx),np.zeros(end_idx - start_idx))).T) - means)
            dat *= (scale*100)
            return(dat)

    def bind(self):
        for _vbo in self.vbos:
            _vbo[0].bind()

    def unbind(self):
        for _vbo in self.vbos:
            _vbo[0].unbind()

    def drawVBOLines(self, _vbo:Tuple[vbo.VBO, int]):
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glEnableClientState(gl.GL_COLOR_ARRAY)
        _vbo[0].bind()
        gl.glVertexPointer(3, gl.GL_FLOAT, 24,_vbo[0])
        gl.glColorPointer(3, gl.GL_FLOAT, 24, _vbo[0] + 12)
        gl.glDrawArrays(gl.GL_LINES, 0, _vbo[1]) 
        _vbo[0].unbind()
        gl.glDisableClientState(gl.GL_COLOR_ARRAY)
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)

    def drawVBOPts(self, _vbo:Tuple[vbo.VBO, int]):
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glEnableClientState(gl.GL_COLOR_ARRAY)
        _vbo[0].bind()
        gl.glVertexPointer(3, gl.GL_FLOAT, 24,_vbo[0])
        gl.glColorPointer(3, gl.GL_FLOAT, 24, _vbo[0] + 12)
        gl.glDrawArrays(gl.GL_POINTS, 0, _vbo[1]) 
        _vbo[0].unbind()
        gl.glDisableClientState(gl.GL_COLOR_ARRAY)
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)

    def drawVBOTriangles(self, _vbo:Tuple[vbo.VBO, int]):
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glEnableClientState(gl.GL_COLOR_ARRAY)
        _vbo[0].bind()
        gl.glVertexPointer(3, gl.GL_FLOAT, 24,_vbo[0])
        gl.glColorPointer(3, gl.GL_FLOAT, 24, _vbo[0] + 12)
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, _vbo[1]) 
        _vbo[0].unbind()
        gl.glDisableClientState(gl.GL_COLOR_ARRAY)
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)

    def draw(self):
        for _vbo in self.vbos:
            _vbo[0].bind()
            gl.glVertexPointer(3, gl.GL_FLOAT, 24,_vbo[0])
            gl.glColorPointer(3, gl.GL_FLOAT, 24, _vbo[0] + 12)
            gl.glDrawArrays(gl.GL_POINTS, 0, _vbo[1]) 
            _vbo[0].unbind()
    
    def set_color_mode(self, mode, dim,start_idx, end_idx, data): 
        if (mode == "default"):
            if (all([x in self.file_object.point_format.lookup for x in ("red", "green", "blue")])):
                idx_step = max(int((len(self.file_object)/1000)), 1)
                if ((all(self.file_object.red[0:len(self.file_object):idx_step] == 0)) and
                    (all(self.file_object.green[0:len(self.file_object):idx_step] == 0)) and
                    (all(self.file_object.blue[0:len(self.file_object):idx_step] == 0))):
                    print("Warning: Color data appears empty, using intensity mode. Specify -mode=rgb to override")
                    mode = "intensity"
                else:
                    mode="rgb"
            else:
                mode = "intensity" 
        if mode == "rgb" and not "red" in self.file_object.point_format.lookup:
            print("Color data not found in file, using intensity")
            mode = "intensity"
        if mode in ["grey", "greyscale", "intensity"]:
            if type(self.allcolor) == bool:
                self.allcolor = self.file_object.reader.get_dimension(dim)/float(np.max(self.file_object.reader.get_dimension(dim)))
            scaled = self.allcolor[start_idx:end_idx] + 0.1
            col = np.array((np.vstack((scaled, scaled, scaled)).T), dtype = np.float32)
            data[:,3:6] += col
            return(data)
        elif (mode == "elevation" or (mode == "heatmap" and dim == "z")):
            if type(self.allcolor) == bool:
                self.allcolor = self.heatmap(self.file_object.z)
            col = self.allcolor[start_idx:end_idx]
            data[:,3:6] += col
            return(data)
        elif (mode == "heatmap" and dim != "z"):
            if type(self.allcolor) == bool:
                self.allcolor = self.heatmap(self.file_object.reader.get_dimension(dim))
            col = self.allcolor[start_idx:end_idx]
            data[:,3:6] += col
            return(data)
        elif mode == "rgb":
            _max = max(np.max(self.file_object.red), np.max(self.file_object.green), np.max(self.file_object.blue))
            _min = min(np.min(self.file_object.red), np.min(self.file_object.green), np.min(self.file_object.blue))
            diff = _max - _min
            col = np.array(np.vstack((self.file_object.red[start_idx:end_idx], self.file_object.green[start_idx:end_idx], self.file_object.blue[start_idx:end_idx])).T, dtype = np.float32)
            col -= _min
            col /= diff
            data[:,3:6] += col
            return(data)

    def heatmap(self, vec, mode = 1):
        _max = np.max(vec)
        _min = np.min(vec)
        diff = _max-_min
        red = (vec-_min)/float(diff) 
        if mode == 1:
            col = np.array(np.vstack((red**4, np.sqrt(0.0625-(0.5-red)**4) , (1-red)**4)),dtype = np.float32).T 
        else:
            col = np.array(np.vstack((red**4, np.zeros(self.N) , (1-red)**4)),dtype = np.float32).T 
        return(col)
