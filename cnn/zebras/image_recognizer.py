"""
Created on Jun 28, 2016

Runs retrained neural network for recognition

@author: Levan Tsinadze
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys

from cnn.transfer.recognizer_interface import retrained_recognizer
from cnn.zebras.cnn_files import training_file


class image_recognizer(retrained_recognizer):
  """Recognizes image thru trained neural networks"""
  
  def __init__(self):
    super(image_recognizer, self).__init__(training_file)

if __name__ == '__main__':
  """Runs image recognition"""
  img_recognizer = image_recognizer()
  img_recognizer.run_inference_on_image(sys.argv)
