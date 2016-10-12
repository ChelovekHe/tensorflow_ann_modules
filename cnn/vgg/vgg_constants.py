'''
Created on Oct 12, 2016
Constant parameters for VGG network implementation
@author: Levan Tsinadze
'''

trainable_scopes = 'vgg_16/fc6,vgg_16/fc7,vgg_16/fc8'
checkpoint_exclude_scopes = trainable_scopes
checkpoint_file = 'vgg_16'
checkpoint_url = 'vgg_16_2016_08_28'