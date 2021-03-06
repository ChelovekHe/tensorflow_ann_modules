"""
Created on Jan 12, 2017

Compares faces throw FaceNet model
Performs face alignment and calculates L2 distance between the embeddings of two images.

@author: Levan Tsinadze

MIT License
# 
# Copyright (c) 2016 David Sandberg
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import os

from tensorflow.python.platform import gfile

from cnn.faces import face_utils as utils
from cnn.faces import network_interface as interface
from cnn.faces.cnn_files import training_file
from cnn.faces.face_utils import INPUT_NAME, TRAIN_LAYER, EMBEDDINGS_LAYER, INPUT_LAYER
import numpy as np
import tensorflow as tf


def calculate_embeddings_with_graph(sess, images):
  """Calculates embeddings for images
    Args:
      sess - current TensorFlow session
      images - image files
    Returns:
      emb - embeddings for images
  """  
  
  # Get input and output tensors
  images_placeholder = tf.get_default_graph().get_tensor_by_name(INPUT_LAYER)
  embeddings = tf.get_default_graph().get_tensor_by_name(EMBEDDINGS_LAYER)

  # Run forward pass to calculate embeddings
  feed_dict = { images_placeholder: images }
  emb = sess.run(embeddings, feed_dict=feed_dict)
  
  return emb

def load_model_graph(args):
  """Loads graph from file
    Args:
      args - command line arguments
    Returns:
      tuple of - 
        images_placeholder - input image placeholder
        phase_train_placeholder - input image phaze placeholder
        embeddings - network layer for feed-forward call
  """
  
  images_placeholder = tf.placeholder(tf.float32, shape=(None, args.image_size, args.image_size, 3), name=INPUT_NAME)
  with gfile.FastGFile(os.path.expanduser(args.model_file), 'rb') as f:
    graph_def = tf.GraphDef()
    graph_def.ParseFromString(f.read())
    return_elements = [TRAIN_LAYER, EMBEDDINGS_LAYER]
    phase_train_placeholder, embeddings = tf.import_graph_def(graph_def, input_map={INPUT_NAME:images_placeholder},
        return_elements=return_elements, name=INPUT_NAME)
    
    return (images_placeholder, phase_train_placeholder, embeddings)

def compare_faces(args):
  """Generates many face embeddings from files and calculates L2 distances
    Args:
      args - command line arguments
  """

  images = utils.load_and_align_data(args.image_files, args.image_size, args.margin, args.gpu_memory_fraction, _files)
  emb = interface.calculate_embeddings(args.model_dir, images)
          
  nrof_images = len(args.image_files)

  print('Images:')
  for i in range(nrof_images):
    print('%1d: %s' % (i, args.image_files[i]))
  print('')
  
  # Print distance matrix
  print('Distance matrix')
  print('    ', end='')
  
  return (emb, nrof_images)

def compare_many_faces(args):
  """Generates many face embeddings from files and calculates L2 distances
    Args:
      args - command line arguments
  """

  (emb, nrof_images) = compare_faces(args)
  for i in range(nrof_images):
    print('    %1d     ' % i, end='')
  print('')
  for i in range(nrof_images):
    print('%1d  ' % i, end='')
    for j in range(nrof_images):
      dist = np.sqrt(np.sum(np.square(np.subtract(emb[i, :], emb[j, :]))))
      print('  %1.4f  ' % dist, end='')
    print('')
      
def compare_two_faces(args):
  """Generates two face embeddings from files and calculates L2 distances
    Args:
      args - command line arguments
  """

  (emb, _) = compare_faces(args)
  print('')
  dist = np.sqrt(np.sum(np.square(np.subtract(emb[0, :], emb[1, :]))))
  print('  %1.4f  ' % dist, end='')
  print('')

def parse_arguments():
  """Parses command line arguments
    Returns:
      argument_flags - retrieved arguments
  """
  global _files
  _files = training_file()
  parser = argparse.ArgumentParser()
  parser.add_argument('--many_faces',
                       dest='many_faces',
                       action='store_true',
                       help='Flag to compare only two faces.')
  parser.add_argument('--two_faces',
                       dest='many_faces',
                       action='store_false',
                       help='Do not print data set file names and labels.')
  parser.add_argument('--model_dir',
                      type=str,
                      default=_files.model_dir,
                      help='Directory containing the meta_file and ckpt_file')
  parser.add_argument('--graph_file',
                      type=str,
                      default=_files.graph_file,
                      help='Filename for the exported graphdef protobuf (.pb)')
  parser.add_argument('--image_files',
                      type=str,
                      nargs='+',
                      help='Images to compare')
  parser.add_argument('--image_size',
                      type=int,
                      default=160,
                      help='Image size (height, width) in pixels.')
  parser.add_argument('--margin',
                      type=int,
                      default=44,
                      help='Margin for the crop around the bounding box (height, width) in pixels.')
  parser.add_argument('--gpu_memory_fraction',
                      type=float,
                      default=1.0,
                      help='Upper bound on the amount of GPU memory that will be used by the process.')
  parser.add_argument('--result_file',
                      type=str,
                      help='Upper bound on the amount of GPU memory that will be used by the process.')
  (argument_flags, _) = parser.parse_known_args()
  
  return argument_flags

if __name__ == '__main__':
  """Compares face embeddings from image files"""
  
  argument_flags = parse_arguments()
  if argument_flags.many_faces:
    compare_many_faces(argument_flags)
  else:
    compare_two_faces(argument_flags)
