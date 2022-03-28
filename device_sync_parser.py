import os
import csv
import numpy as np
import math as m
from typing import List

from run import Frame, Run

np.set_printoptions(suppress=True)

def Rx(theta):
    return np.matrix(
        [
            [ 1, 0           , 0           ],
            [ 0, m.cos(theta),-m.sin(theta)],
            [ 0, m.sin(theta), m.cos(theta)]
        ]
    )
  
def Ry(theta):
    return np.matrix(
        [
            [ m.cos(theta), 0, m.sin(theta)],
            [ 0           , 1, 0           ],
            [-m.sin(theta), 0, m.cos(theta)]
        ]
    )
  
def Rz(theta):
    return np.matrix(
        [
            [ m.cos(theta), -m.sin(theta), 0 ],
            [ m.sin(theta), m.cos(theta) , 0 ],
            [ 0           , 0            , 1 ]
        ]
    )

def read_sync_file(file_path, run_numbers=[]):
    directory_path = os.path.dirname(file_path)
    runs: List[Run] = []
    with open(file_path, 'r') as f:
        data = csv.reader(f)
        previous_run_number = None
        header = next(data)
        for row in data:
            try:
                filename, x, y, z, roll, pitch, yaw = row
                splitted = filename.split('_')
                run_number = int(splitted[1])
                if len(run_numbers) and run_number not in run_numbers:
                    continue
                frame_number = int(splitted[-1])
            except Exception as e:
                print('Error while sync file line parsing', str(e))
            if previous_run_number is None or previous_run_number != run_number:
                runs.append(Run(run_number, directory_path))
            current_run = runs[-1] 
            current_run.frames.append(Frame(frame_number, x, y, z, roll, pitch, yaw))
            previous_run_number = run_number
    return runs

def get_runs_distance(runs, run_numbers=[]):
    out_distance = 0
    for run in runs:
        if len(run_numbers):
            if run.run_number in run_numbers:
                continue
        print(f'Run {run.run_number}::')
        run_distance = 0
        previous_frame = None
        for frame in run.frames:
            if previous_frame is None:
                previous_frame = frame
                continue
            dist = np.sqrt(np.sum(np.square(frame.xyz() - previous_frame.xyz()))) * 0.3048
            run_distance += dist
            previous_frame = frame
        out_distance += run_distance
        print('distance {:0.2f} m'.format(run_distance))
    print('Overall distance {:0.2f} m'.format(out_distance))

def plot_runs(runs, run_numbers=[]):
    import pytransform3d.visualizer as pv
    data = []
    first_frame = None
    for run in runs:
        if len(run_numbers):
            if run.run_number in run_numbers:
                continue
        for frame in run.frames:
            if first_frame is None:
                first_frame = frame
            ff_xyz = first_frame.xyz()
            data.append(ff_xyz-frame.xyz())
    data = np.array(data) / 100
    colors = np.empty((len(data), 3))
    colors[:, 0] = np.linspace(0, 1, len(colors))
    fig = pv.figure(window_name='trj', width=4080, height=2040, with_key_callbacks=True)
    fig.scatter(data, c=colors)
    fig.plot_basis(R=np.eye(3))
    fig.view_init()
    fig.save_image("out/__open3d_rendered_image.jpg")
    if "__file__" in globals():
        fig.show()

if __name__ == '__main__':
    runs = read_sync_file('data/dallas/data/reference.csv', [])
    get_runs_distance(runs)
    exit()
    
