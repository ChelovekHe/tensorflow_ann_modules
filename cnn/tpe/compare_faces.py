"""
Created on Jan 26, 2017

Compares faces by embeddings distance

@author: Levan Tsinadze
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse

from skimage import io

from cnn.tpe import vector_utils as vectors
from cnn.tpe.cnn_files import training_file
from cnn.tpe.network_model import FaceVerificator
from cnn.utils import file_utils


dist = 0.85
_files = training_file()


def init_verificator():
  """Initializes face verificator model
    Returns:
      fv - face verificator model
  """
  
  fv = FaceVerificator(_files.model_dir)
  fv.initialize_model()
  
  return fv

def _compare_found_faces(faces_0, faces_1, flags):
  """Calculates distance between found faces
    Args:
      faces_0 - faces from first image
      faces_1 - faces from second image
  """

  rects_0 = list(map(lambda p: p[0], faces_0))
  rects_1 = list(map(lambda p: p[0], faces_1))
  
  embs_0 = list(map(lambda p: p[1], faces_0))
  embs_1 = list(map(lambda p: p[1], faces_1))
  
  print('Rects on image 0: {}'.format(rects_0))
  print('Rects on image 1: {}'.format(rects_1))
  
  if flags.score:
    (scores, comps) = vectors.compare_many(dist, embs_0, embs_1)
    
    print('Score matrix:')
    print(scores)
    
    print('Decision matrix :')
    print(comps)
    
    return (scores, comps)
  else:
    print('Embeddings of faces on image 0:')
    print(embs_0)
    print('Embeddings of faces on image 1:')
    print(embs_1)
    
def _compare_faces_from_files(image1, image2, fv, flags):
  """Compares two faces
    Args:
      image1 - first image path
      image2 - seconf image path 
      fv - face verification model
  """
  img_0 = io.imread(image1)
  img_1 = io.imread(image2)
  
  faces_0 = fv.process_image(img_0)
  faces_1 = fv.process_image(img_1)
  
  n_faces_0 = len(faces_0)
  n_faces_1 = len(faces_1)
  
  if n_faces_0 == 0 or n_faces_1 == 0:
    print('Error: No faces found on the {}!'.format(image1 if n_faces_0 == 0 else image2))
  else:
    _compare_found_faces(faces_0, faces_1, flags)  
  
def compare_faces(flags, fv):
  """Compares two faces
    Args:
      flags - arguments of images and score
      fv - face verification model
  """
  (image1, image2) = (flags.image1, flags.image2)
  if file_utils.file_exists(image1) and file_utils.file_exists(image2):
    _compare_faces_from_files(image1, image2, fv, flags)
  else:
    print('Error: No file found on path {} / {}!'.format(image1, image2))

def _compare_faces(flags):
  """Compares two faces
    Args:
      flags - arguments of images and score
  """
  fv = init_verificator()
  compare_faces(flags, fv)

if __name__ == '__main__':
  """Generates tensors from images"""
  
  arg_parser = argparse.ArgumentParser()
  arg_parser.add_argument('--image1',
                          type=str,
                          help='First image file name')
  arg_parser.add_argument('--image2',
                          type=str,
                          help='Second image file name')
  arg_parser.add_argument('--score',
                          dest='score',
                          action='store_true',
                          help='Flags for face embedding compare.')
  (flags, _) = arg_parser.parse_known_args()
  if flags.image1 and flags.image2:
    comp_result = _compare_faces(flags)
  else:
    print('No images to compare')
