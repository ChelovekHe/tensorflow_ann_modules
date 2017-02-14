"""
Created on Feb 14, 2017

Compares two faces by dlib library

@author: Levan Tsinadze
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import math

from skimage import io

from cnn.faces.cnn_files import training_file
import dlib


LANDMARKS_WEIGHTS = 'shape_predictor_68_face_landmarks.dat'
RESNET_WEIGHTS = 'dlib_face_recognition_resnet_model_v1.dat'

def load_model():
  """Loads network model weights
    Returns:
      tuple of -
        detector - face descriptor
        sp - shape detector
        facerec - face recognizer
  """
  
  _files = training_file()
  
  predictor_path = _files.model_file(LANDMARKS_WEIGHTS)
  face_rec_model_path = _files.model_file(RESNET_WEIGHTS)
  
  # Load all the models we need: a detector to find the faces, a shape predictor
  # to find face landmarks so we can precisely localize the face, and finally the
  # face recognition model.
  detector = dlib.get_frontal_face_detector()
  sp = dlib.shape_predictor(predictor_path)
  facerec = dlib.face_recognition_model_v1(face_rec_model_path)
  
  return (detector, sp, facerec)

def calculate_embedding(img, _network):
  """Calculates embedding from image
    Args:
      img - face image
      _network - pre-trained network module
    Returns:
      face_descriptor - embedding vector
  """
  
  (detector, sp, facerec) = _network
  # Ask the detector to find the bounding boxes of each face. The 1 in the
  # second argument indicates that we should upsample the image 1 time. This
  # will make everything bigger and allow us to detect more faces.
  dets = detector(img, 1)
  print("Number of faces detected: {}".format(len(dets)))
  # Now process each face we found.
  for k, d in enumerate(dets):
      
    print("Detection {}: Left: {} Top: {} Right: {} Bottom: {}".format(
        k, d.left(), d.top(), d.right(), d.bottom()))
    # Get the landmarks/parts for the face in box d.
    shape = sp(img, d)
    
    # Compute the 128D vector that describes the face in img identified by
    # shape.  In general, if two face descriptor vectors have a Euclidean
    # distance between them less than 0.6 then they are from the same
    # person, otherwise they are from different people.  He we just print
    # the vector to the screen.
    face_descriptor = facerec.compute_face_descriptor(img, shape)
    
    return face_descriptor
# Now process all the images
def compare_files(_image1, _image2, _network):
  """Compares two faces from images
    Args:
      _image1 - first image
      _image2 - second image
      _network - pre-trained network module
    Returns:
      face_dst - distance between embeddings
  """
    
  print("Processing files: {} {}".format(_image1, _image2))
  img1 = io.imread(_image1)
  img2 = io.imread(_image2)

  emb1 = calculate_embedding(img1, _network)
  emb2 = calculate_embedding(img2, _network)
  print(type(emb1), type(emb2))
  for i in range(128):
    print(math.pow(emb1[i] - emb2[i], 2))
  
def _parse_arguments():
  """Parses command line arguments
    Returns:
      args - parsed command line arguments
  """
  parser = argparse.ArgumentParser()
  parser.add_argument('--image1',
                      type=str,
                      help='Path to first image')
  parser.add_argument('--image2',
                      type=str,
                      help='Path to second image')
  parser.add_argument('--include_gui',
                      dest='include_gui',
                      action='store_true',
                      help='Include top layers')
  (args, _) = parser.parse_known_args()
  
  return args
  
if __name__ == '__main__':
  """Compare face images"""
  
  args = _parse_arguments()
  if args.image1 and args.image2:
    _network = load_model()
    compare_files(args.image1, args.image2, _network)
  else:
    print('No images to be compared')