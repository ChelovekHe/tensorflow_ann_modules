"""
Created on Jan 24, 2017

Full network model implementation

@author: Levan Tsinadze
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os.path

from cnn.tpe.bottleneck import Bottleneck
from cnn.tpe.conv_network import init_cnn
from cnn.tpe.preprocessing import FaceDetector, FaceAligner, clip_to_range
from cnn.tpe.tpe_network import init_tpe
import numpy as np


GREATER_THAN = 32
BATCH_SIZE = 128
IMSIZE = 217
IMBORDER = 5


class FaceVerificatorError (Exception):
  pass


class FileNotFoundError (FaceVerificatorError):
  pass


class FaceVerificator:
    
  def __init__(self, model_dir):
    self._model_dir = model_dir
    self._model_files = {
      'shape_predictor': os.path.join(model_dir, 'shape_predictor_68_face_landmarks.dat'),
      'face_template': os.path.join(model_dir, 'face_template.npy'),
      'mean': os.path.join(model_dir, 'mean.npy'),
      'stddev': os.path.join(model_dir, 'stddev.npy'),
      'cnn_weights': os.path.join(model_dir, 'weights_cnn.h5'),
      'tpe_weights': os.path.join(model_dir, 'weights_tpe.h5'),
    }

    for model_file in self._model_files.values():
      if not os.path.exists(model_file):
        raise FileNotFoundError(model_file)

  def initialize_model(self):
    """Initializes network models"""
    
    self._mean = np.load(self._model_files['mean'])
    self._stddev = np.load(self._model_files['stddev'])
    self._fd = FaceDetector()
    self._fa = FaceAligner(self._model_files['shape_predictor'],
                           self._model_files['face_template'])
    cnn = init_cnn(227, 266)
    cnn.load_weights(self._model_files['cnn_weights'])
    self._cnn = Bottleneck(cnn, ~1)
    _, tpe = init_tpe(256, 256)
    tpe.load_weights(self._model_files['tpe_weights'])
    self._tpe = tpe

  def normalize(self, img):
    
    img = clip_to_range(img)
    norm_result = (img - self._mean) / self._stddev
    
    return norm_result

  def process_image(self, img):
    
    face_rects = self._fd.detect_faces(img, upscale_factor=2, greater_than=GREATER_THAN)

    if face_rects:
      faces = self._fa.align_faces(img, face_rects, dim=IMSIZE, border=IMBORDER)
      faces = list(map(self.normalize, faces))
  
      faces_y = self._cnn.predict(faces, batch_size=BATCH_SIZE)
      faces_y = self._tpe.predict(faces_y, batch_size=BATCH_SIZE)
  
      result = list(zip(face_rects, faces_y))
    else:
      result = []
    
    return result
