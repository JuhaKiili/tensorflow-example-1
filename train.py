import argparse
import json
import os

import numpy as np
import tensorflow as tf


# Read parameters from Valohai
# This enables Valohai to version your parameters,
# run quick iterations and do hyperparameter optimization

parser = argparse.ArgumentParser()
parser.add_argument('--epochs', type=int, default=5)
parser.add_argument('--learning_rate', type=float, default=0.001)
parser.add_argument('--batch_size', type=int, default=1024)
args = parser.parse_args()


# Read input files from Valohai inputs directory
# This enables Valohai to version your training data
# and cache the data for quick experimentation

input_path = os.getenv('VH_INPUTS_DIR', './inputs')
f = os.path.join(input_path, 'preprocessed_mnist/preprocessed_mnist.npz')

with np.load(f, allow_pickle=True) as f:
    x_train, y_train = f['x_train'], f['y_train']
    x_test, y_test = f['x_test'], f['y_test']

model = tf.keras.models.Sequential([
  tf.keras.layers.Conv2D(32, kernel_size=(3, 3), activation='relu', input_shape=(1, 28, 28)),
  tf.keras.layers.Conv2D(64, kernel_size=(3, 3), activation='relu'),
  tf.keras.layers.MaxPooling2D(pool_size=(2, 2)),
  tf.keras.layers.Flatten(),
  tf.keras.layers.Dense(128, activation='relu'),
  tf.keras.layers.Dropout(0.2),
  tf.keras.layers.Dense(10, activation='softmax')
])

# model = Sequential()
# model.add(Conv2D(32, kernel_size=(3, 3),
#                  activation='relu',
#                  input_shape=input_shape))
# model.add(Conv2D(64, (3, 3), activation='relu'))
# model.add(MaxPooling2D(pool_size=(2, 2)))
# model.add(Dropout(0.25))
# model.add(Flatten())
# model.add(Dense(128, activation='relu'))
# model.add(Dropout(0.5))
# model.add(Dense(num_classes, activation='softmax'))

model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=args.learning_rate),
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])


# Print metrics out as JSON
# This enables Valohai to version your metadata
# and for you to use it to compare experiments

def log(epoch, logs):
    print()
    print(json.dumps({
        'epoch': epoch,
        'loss': str(logs['loss']),
        'acc': str(logs['acc']),
    }))

cb = tf.keras.callbacks.LambdaCallback(on_epoch_end=log)

model.fit(x_train, y_train, epochs=args.epochs, batch_size=args.batch_size, callbacks=[cb])


# Evaluate the model and print out the test metrics as JSON

test_loss, test_acc = model.evaluate(x_test,  y_test, verbose=2)
print(json.dumps({
    'test_loss': str(test_loss),
    'test_acc': str(test_acc),
}))


# Write output files to Valohai outputs directory
# This enables Valohai to version your data 
# and upload output it to the default data store

path = os.getenv('VH_OUTPUTS_DIR', './outputs')
model.save(os.path.join(path, 'model.h5'))
