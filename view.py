from argparse_io import argparserI
import viz
import laspy

if __name__ == '__main__':
    opt = argparserI()
    inp_path = opt.path
    pc = laspy.file.File(inp_path)
    viewer = viz.pcl_image(pc, mode='default', dim='intensity')
    viewer.visualize()
