"""
Created on Mar 17, 2017

Training data preparation

@author: Rudolf Eremian, Levan Tsinadze
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from keras.datasets import imdb
from keras.preprocessing import sequence

from rnn.sentences import data_logger as logger


def init_training_set(flags):
  """Should be implemented
    Returns:
      tuple of -
        tuple for training - 
          X_train - training set
          y_train - training labels
        tuple for testing
          X_test - test set
          y_test - test labels
  """
  
  if flags.train_on_imdb:
    ((X_train_raw, y_train), (X_test_raw, y_test)) = imdb.load_data(num_words=flags.top_words)
    X_train = sequence.pad_sequences(X_train_raw, maxlen=flags.max_review_length)
    X_test = sequence.pad_sequences(X_test_raw, maxlen=flags.max_review_length)
    logger.log_message(flags, 'train_on_imdb')
  else:
    ((X_train, y_train), (X_test, y_test)) = None
    logger.log_message(flags, 'train_on_conversations')
  
  return ((X_train, y_train), (X_test, y_test))