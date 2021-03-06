"""
Created on Jun 18, 2016

Initializes convolutional and pooling layers for network

@author: Levan Tsinadze
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from cnn.mnist import network_parameters as pr
from cnn.mnist.network_parameters import cnn_weights
import tensorflow as tf


STRIDE = 'SAME'

class cnn_functions(object):
  """CNN network model for MNIST classification"""
    
  def __init__(self, decay=None, for_training=True):
    self.x = tf.placeholder(tf.float32, [None, pr.N_INPUT])
    self.y = tf.placeholder(tf.float32, [None, pr.N_CLASSES])
    self.weights = cnn_weights()
    self.weights.init_weights(wdc=decay)
    self._for_training = for_training
    self.keep_prob = tf.placeholder(tf.float32)  # dropout (keep probability)

  def conv2d(self, x, W, b, strides=1):
    """ Conv2D wrapper, with bias add and ReLu activation function
      Args:
        x - input
        W - weights
        b - biases
        strides - strides for convolution
    """
    net = tf.nn.conv2d(x, W, strides=[1, strides, strides, 1], padding=STRIDE)
    net = tf.nn.bias_add(net, b)
    net = tf.nn.relu(net)
    
    return net
  
  def maxpool2d(self, x, k=2):
    """ MaxPool2D wrapper
      Args:
        x - input
        k - pooling parameter
    """
    return tf.nn.max_pool(x, ksize=[1, k, k, 1], strides=[1, k, k, 1],
                          padding=STRIDE)
    
  def conv_layers(self):
    """Convolutional network interface
      Args:
        x - input tensor
        ksize - kernel size
        strides - strides for convolve and pooling
      Returns:
        out - output from network
    """  
    
    reshaped = tf.reshape(self.x, shape=[-1, 28, 28, 1])
    conv1 = self.conv2d(reshaped, self.weights.wc1, self.weights.bc1)
    conv1 = self.maxpool2d(conv1, k=2)
    conv2 = self.conv2d(conv1, self.weights.wc2, self.weights.bc2)
    conv2 = self.maxpool2d(conv2, k=2)
    
    return conv2
  
  def conv_net(self):
    """Full network interface
      Returns:
        out - output from network
    """
  
    net = self.conv_layers()

    # Fully connected layer
    # Reshape conv2 output to fit fully connected layer input
    net = tf.reshape(net, [-1, self.weights.wd1.get_shape().as_list()[0]])
    net = tf.add(tf.matmul(net, self.weights.wd1), self.weights.bd1)
    net = tf.nn.relu(net)
    # Apply Dropout
    if self._for_training:
      net = tf.nn.dropout(net, self.keep_prob)

    # Output, class prediction
    out = tf.add(tf.matmul(net, self.weights.wout), self.weights.bout)
    
    return out
  
  def regularizer(self):
    """Generates L2 regularization for fully connected layers
      Returns:
        regularizers - regularization functions
    """
    
    # L2 regularization for the fully connected parameters.
    regularizers = (tf.nn.l2_loss(self.weights.wd1) + tf.nn.l2_loss(self.weights.bd1) + 
                    tf.nn.l2_loss(self.weights.wout) + tf.nn.l2_loss(self.weights.bout))
    return regularizers
  
  def cnn_pred(self):
    """Prediction function for network interface
      Returns: 
        tuple of - prediction, correct prediction, accuracy
    """
      
    # Construct model
    pred = self.conv_net()
    
    # Evaluate model
    correct_pred = tf.equal(tf.argmax(pred, 1), tf.argmax(self.y, 1))
    accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))
    
    return (pred, correct_pred, accuracy)
