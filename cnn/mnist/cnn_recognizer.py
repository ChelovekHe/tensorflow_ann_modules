"""
Created on Jun 25, 2016
Recognizes for image
@author: Levan Tsinadze
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from cnn.mnist.cnn_files import training_file
from cnn.mnist.cnn_input_reader import read_input_file
from cnn.mnist.cnn_methods import cnn_functions
import tensorflow as tf


class image_recognizer(object):
  """Recognizer class"""
    
  def recognize_image(self, image_file_path):
    """Recognizes digit from file
      Args:
        image_file_path - path for image file
      Return:
        Recognized digit
    """
  
    cnn_fnc = cnn_functions()
    pred = cnn_fnc.conv2d
    
    # Evaluate model
    recognize_image = tf.argmax(pred, 1)
    # Initializing saver to read trained data
    saver = tf.train.Saver()
    tf.initialize_all_variables()
    tr_files = training_file()
    model_path = tr_files.get_or_init_files_path()
    with tf.Session() as sess:
        print('Start session')
        # Initialize variables
        saver.restore(sess, model_path)
        print("Model restored from file: %s" % model_path)
        image_rec = read_input_file(image_file_path)
        # Recognize image
        resp_dgt = sess.run(recognize_image, feed_dict={self.x: image_rec,
                                          self.keep_prob: 1})
        print("Recognized image:", resp_dgt[0])
    
    return resp_dgt[0]
    
    
