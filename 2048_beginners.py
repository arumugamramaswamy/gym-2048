import os

import tensorflow as tf
import numpy as np

import training_data

# Load data
input_folder = 'less_data'
t = training_data.training_data()
t.read(input_folder)
#t2 = training_data.training_data()
#t2.read('more_data')
#print("Data points: {}".format(t.size()))
#t.merge(t2)
#print("Data points: {}".format(t.size()))
#t.augment()
#print("Data points: {}".format(t.size()))

x_training = t.get_x()
y_training = t.get_y()

# Flatten boards out to 1 dimension
number_of_items = t.size()
x_training = np.reshape(x_training, (number_of_items, 16)).astype(np.float32)
#print(x_training)
#print(x_training.shape)
#print(x_training.dtype)

y_training = y_training.astype(np.float32)
#print(y_training)
#print(y_training.shape)
#print(y_training.dtype)

# Create tensorflow data from loaded numpy arrays
dataset = tf.data.Dataset.from_tensor_slices({"x": x_training, "y": y_training})
#dataset = dataset.shuffle(10000)
dataset = dataset.batch(1)
#dataset = dataset.repeat(10)
new_iterator = tf.data.Iterator.from_structure(dataset.output_types,
                                           dataset.output_shapes)
next_element = new_iterator.get_next()

training_init = new_iterator.make_initializer(dataset)
#print(X)
#print(Y)
sess = tf.InteractiveSession()
sess.run(training_init)
while True:
    try:
        print(sess.run([next_element['x'], next_element['y']]))
    except tf.errors.OutOfRangeError:
        print("End of dataset")
        break


# Model
x = tf.placeholder(tf.float32, [None, 16])
W = tf.Variable(tf.truncated_normal((16, 4), stddev=0.1))
b = tf.Variable(tf.zeros([4]))
y = tf.nn.softmax(tf.matmul(next_element['x'], W) + b)
#y_ = tf.placeholder(tf.float32, [None, 4])

# Trainer
cross_entropy = tf.reduce_mean(-tf.reduce_sum(next_element['y'] * tf.log(y), reduction_indices=[1]))
train_step = tf.train.GradientDescentOptimizer(0.01).minimize(cross_entropy)
tf.global_variables_initializer().run()

sess.run(training_init)

(thisW, thisb, thisy) = sess.run([W, b, y])
print("Initial gradients: {}".format(thisW))
print("Initial biases: {}".format(thisb))
print("Initial output: {}".format(thisy))

sess.run(training_init)
while True:
    try:
        (ts, my_y) = sess.run([train_step, y])
    except tf.errors.OutOfRangeError:
        print("End of dataset")
        break
    #print(sess.run([next_element['x'], next_element['y']]))
    #sess.run(train_step)

sess.run(training_init)
(thisW, thisb, thisy) = sess.run([W, b, y])
print("Trained gradients: {}".format(thisW))
print("Trained biases: {}".format(thisb))
print("Trained output: {}".format(thisy))

print y.shape
#print y_.shape

iterator = dataset.make_one_shot_iterator()
next_element = iterator.get_next()
correct_prediction = tf.equal(tf.argmax(y, 1), tf.argmax(next_element['y'], 1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
print(sess.run(accuracy))