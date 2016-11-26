import tensorflow as tf
import numpy as np
from ops import *

batch_size = 100
sample_size = 100

z_dim = 100
gf_dim = 64
df_dim = 64

g_bn0 = batch_norm(name='g_bn0')
g_bn1 = batch_norm(name='g_bn1')
g_bn2 = batch_norm(name='g_bn2')
g_bn3 = batch_norm(name='g_bn3')
  
def discriminator(image, reuse=False):
    if reuse:
        tf.get_variable_scope().reuse_variables()
    im0 = tf.reshape(image, [-1, 32*32*3])
    drop0 =  tf.nn.dropout(im0, 0.2)
    im1 = tf.reshape(drop0, [-1, 32, 32, 3])
    h0 = lrelu(conv2d(image, df_dim, stride_vert=1,stride_horiz=1,name='d_h0_conv'))
    h1 = lrelu(conv2d(h0, df_dim, stride_vert=1,stride_horiz=1,name='d_h1_conv'))
    h2 = lrelu(conv2d(h1, df_dim, name='d_h2_conv'))
    h2_2 = tf.nn.dropout(h2, 0.5)
    h3 = lrelu(conv2d(h2_2, df_dim*2,stride_vert=1,stride_horiz=1,name='d_h3_conv'))
    h4 = lrelu(conv2d(h3, df_dim*2,stride_vert=1,stride_horiz=1, name='d_h4_conv'))
    h5 = lrelu(conv2d(h4, df_dim*2,name='d_h5_conv'))
    h5_2 = tf.nn.dropout(h5,0.5)
    h6 = lrelu(conv2d(h5_2, df_dim*2, name='d_h6_conv'))
    #h6_2 = tf.nn.avg_pool(h6,ksize=[1, 2, 2, 1],strides=[1, 2, 2, 1], padding='VALID') 
    h6_2 = tf.reduce_mean(h6, reduction_indices=[3], keep_dims=True)
    #h6_2 = tf.nn.avg_pool(h6,ksize=[1,2,2,1],strides=[1,2,2,1],padding="SAME")
    #h6_3 = lrelu(linear(tf.reshape(h6_2, [batch_size, -1]), 1024, 'd_h2_lin'))
    #h6_4 = tf.nn.dropout(h6_3,0.5)
   # h7 = linear(h6_3,10, 'd_h3_lin')
    h7 = linear(tf.reshape(h6_2, [batch_size, -1]), 10, 'd_h3_lin')
    Z = tf.reduce_sum(tf.exp(h7),1)
    feat_mat = h6_2
    return tf.nn.sigmoid(Z/(Z+1)), Z, tf.nn.softmax(h7), feat_mat

def generator(z):
    z_ = linear(z, gf_dim*8*4*4, 'g_h0_lin')
    h0 = g_bn0(tf.nn.relu(tf.reshape(z_, [-1, 4, 4, gf_dim * 8])))
    h1 = g_bn1(tf.nn.relu(deconv2d(h0, [batch_size, 8, 8, gf_dim*4], name='g_h1')))
    h2 = g_bn2(tf.nn.relu(deconv2d(h1, [batch_size, 16, 16, gf_dim*2], name='g_h2')))
    h4 = deconv2d(h2, [batch_size, 32, 32, 3], name='g_h3')
    return tf.nn.tanh(h4)
