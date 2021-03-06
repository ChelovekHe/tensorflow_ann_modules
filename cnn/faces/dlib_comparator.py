"""
Created on Feb 15, 2017

Faces comparator based on DLIB faces

@author: Levan Tsinadze
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import traceback

from cnn.faces import dlib_faces as comparator


def _parse_arguments():
  """Parses command line arguments
    Returns:
      args - parsed command line arguments
  """
  parser = argparse.ArgumentParser()
  parser.add_argument('--threshold',
                      type=float,
                      default=0.6,
                      help='Threshold for Euclidean distance between face embedding vectors')
  parser.add_argument('--include_gui',
                      dest='include_gui',
                      action='store_true',
                      help='Include top layers')
  parser.add_argument('--verbose',
                      dest='verbose',
                      action='store_true',
                      help='Print additional information')
  (args, _) = parser.parse_known_args()
  
  return args

def _check_on_proceed():
  """Validates application to proceed
    Returns:
      proc_flag - validation result
  """
  
  _proc = raw_input('Would you like to proceed [Y/n]: ')
  if _proc and _proc == 'n':
    proc_flag = False
    print('Application is shutting down')
  else:
    proc_flag = True
  
  return proc_flag

def _run_service(_verbose=False):
  """Face comparator service
    Args:
      _verbose - command line argument for debugging
    Returns:
     proc_flag - validation result
  """
  
  image1 = raw_input('Input image1 path: ')
  image2 = raw_input('Input image2 path: ')
  face_dists = comparator.compare_files(image1, image2, _network, verbose=_verbose)
  comparator.print_faces(face_dists)
  proc_flag = _check_on_proceed()
  
  return proc_flag

if __name__ == '__main__':
  """Starts face comparator service"""
  
  args = _parse_arguments()
  comparator.threshold = args.threshold
  _network = comparator.load_model()
  proc_flag = True
  while proc_flag:
    try:
      proc_flag = _run_service(args.verbose)
    except:
      traceback.print_exc()
      proc_flag = _check_on_proceed()
