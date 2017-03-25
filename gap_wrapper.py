from __future__ import print_function
import subprocess
import os
import re
import numpy as np


float_re = r'([+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?)'
tuple_re = r'\(\s*{0}\s*{0}\s*{0}\s*\)'.format(float_re)
bbox_regex = re.compile(r'.*BBox\s*=\s*{0}\s*{0}.*'.format(tuple_re),
                        flags=re.DOTALL)


def _parse_bbox_extents(string):
    result = bbox_regex.match(string)
    result = result.group(*range(1, 22, 4))
    result = list(map(float, result))
    return np.array(result[:3]), np.array(result[3:])


def run_command(command):
    result = subprocess.run(command, shell=True, check=True,
                            stdout=subprocess.PIPE)
    return result.stdout.decode()


class SceneObject(object):
    def __init__(self, folder):
        self.init_dir = os.getcwd()
        self.folder = folder.rstrip('/')
        self.name = os.path.basename(self.folder)

        self._fetch_info()
        self._guess_good_cam()

    def _guess_good_cam(self):

        os.chdir(self.folder)
        extents = np.abs(np.maximum(self.bbox1, self.bbox2))
        coords = np.zeros(3)
        coords[1] = extents[1]
        coords[2] = np.max(extents)*4
        ox, oy, oz = coords
        tx, ty, tz = -coords

        ty += extents[1]/2

        camera_str = ('{ox} {oy} {oz} {tx} {ty} {tz} 0 1 0'.
                      format(ox=ox, oy=oy, oz=oz, tx=tx, ty=ty, tz=tz))
        self.camera_str = camera_str

    def view(self):

        command = ('scnview {name}.obj -camera {cam}'.
                   format(name=self.name, cam=self.camera_str))
        run_command(command)

    def _fetch_info(self):
        os.chdir(self.folder)
        result = run_command('scninfo %s.obj' % self.name)
        self.bbox1, self.bbox2 = _parse_bbox_extents(result)

    def transform_view(self, tx=0, ty=0, tz=0, rx=0, ry=0, rz=0):

        os.chdir(self.folder)
        src_obj = '%s.obj' % self.name
        dst_obj = '__t__%s.obj' % self.name
        command = ('scn2scn {src_path} {dst_path} -rx {rx} -ry {ry} -rz {rz} '
                   .format(src_path=src_obj, dst_path=dst_obj,
                           rx=rx, ry=ry, rz=rz))

        print(command)
        run_command(command)
        command = ('scnview {obj} -camera {cam}'.
                   format(obj=dst_obj, cam=self.camera_str))
        run_command(command)


obj = SceneObject('/home/vighnesh/data/suncg_data/object/40/')

#obj.view()
obj.transform_view(rx=45)
