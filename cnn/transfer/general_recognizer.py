'''
Created on Jun 28, 2016

Runs retrained neural network for recognition

@author: Levan Tsinadze
'''

import numpy as np
import tensorflow as tf


RESULT_KEY = 'final_result:0'
DECODE_KEY = 'DecodeJpeg/contents:0'

class retrained_recognizer(object):
  """Class to run recognition on trained set"""
  
  def __init__(self, tr_file):
    self.tr_file = tr_file
    self.path_funct = tr_file.get_or_init_test_dir
    

  def create_graph(self, model_path):
    """Creates a graph from saved GraphDef file and returns a saver.
      Args:
        model_path - path to graph model
    """
    # Creates graph from saved graph_def.pb.
    with tf.gfile.FastGFile(model_path, 'rb') as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
        _ = tf.import_graph_def(graph_def, name='')
  
  def print_answers(self, prediction_patrameters):
    """Prints recognition answer
      Args:
        prediction_patrameters - parameters to run recognition
    """
    
    (top_k, labels, predictions) = prediction_patrameters
    for node_id in top_k:
        human_string = labels[node_id]
        score = predictions[node_id]
        print('%s (score = %.5f)' % (human_string, score))
        
  def predict_answer(self, sess, image_parameter):
    """Runs prediction on trained / fine tuned network
      Args:
        sess - TensorFlow session
        image_parameter - image for prediction
      Return:
        predictions - recognition result on image
    """
    
    (image_data, _) = image_parameter
    softmax_tensor = sess.graph.get_tensor_by_name(RESULT_KEY)
    # Runs recognition thru net
    imege_tensor = {DECODE_KEY: image_data}
    predictions = sess.run(softmax_tensor, imege_tensor)
    # Decorates predictions
    predictions = np.squeeze(predictions)
    
    return predictions
  
  def recognize_image(self, sess, image_parameter):
    """Runs and refines prediction on trained / fine tuned network
      Args:
        sess - TensorFlow session
        image_parameter - image for prediction
      Return:
        answer - refined top recognition result on image
    """
    # Decorates predictions
    predictions = self.predict_answer(sess, image_parameter)
    # Gets top prediction (top matchs)s
    top_k = predictions.argsort()[-5:][::-1]  # Getting top 5 predictions
    (_, labels_path) = image_parameter
    f = open(labels_path, 'rb')
    lines = f.readlines()
    labels = [str(w).replace("\n", "") for w in lines]
    prediction_parameters = (top_k, labels, predictions)
    self.print_answers(prediction_parameters)
    answer = labels[top_k[0]]
  
    return answer
  
  def init_image_path(self, sys_params):
    """Initializes image path to recognize
      Args:
        sys_params - runtime parameters
      Return:
        image file full path
    """
    
    if len(sys_params) >= 2:
      test_image_path = self.tr_file.join_path(self.path_funct, sys_params[1])
    else:
      test_image_path = self.tr_file.get_or_init_test_path()
      
    return test_image_path
  
  def run_inference_on_image(self, sys_params=None):
    """Runs network interface on image
      Args:
        sys_parameters - parameters
      Return:
        answer - top predicted data
    """
    # Gets test image path
    test_image_path = self.init_image_path(sys_params)
    if tf.gfile.Exists(test_image_path):
    # Reads image to recognize
      image_data = tf.gfile.FastGFile(test_image_path, 'rb').read()
  
      # Creates graph from saved GraphDef
      model_path = self.tr_file.get_or_init_files_path()
      # Initializes and loads netural network
      self.create_graph(model_path)
      # initializes labels path
      labels_path = self.tr_file.get_or_init_labels_path()
      image_parameter = (image_data, labels_path)
      with tf.Session() as sess:
        answer = self.recognize_image(sess, image_parameter)
    else:
      tf.logging.fatal('File does not exist %s', test_image_path)
      answer = None
      
    return answer
