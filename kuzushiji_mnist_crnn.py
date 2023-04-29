# -*- coding: utf-8 -*-
"""Kuzushiji_MNIST_CRNN.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Rht_FyImeVvldwd7NhrEBJ9C9AxhrNzo
"""

import tensorflow as tf
import time
import matplotlib.pyplot as plt
import numpy as np
from tensorflow.keras import layers
from sklearn.datasets import fetch_openml
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

tic = time.perf_counter()
X,y = fetch_openml(data_id=41982,as_frame=False,return_X_y=True)
toc = time.perf_counter()

print('It took',(toc-tic)/60,' minutes to import the file.')

plt.figure(figsize=(18,9))

for i in range(10):
    plt.subplot(1, 10, i+1)
    plt.imshow(X[i].reshape(28,28))
    plt.title(y[i])
    
plt.show()

print(len(X))
print(len(y))

X_train, X_test, y_train, y_test = train_test_split(X,y)

from sklearn.neighbors import KNeighborsClassifier

X_train.shape
y_train.shape
#nsamples, nx, ny, channel = X_train.shape
#d2_train_dataset = X_train.reshape((nsamples,nx*ny))

knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(X_train, y_train)

from sklearn.model_selection import cross_val_score

tic = time.perf_counter()
#print(f"The CV scores are {cross_val_score(knn, X_train, y_train_2, cv=5, scoring='accuracy')}")
print(f"The CV scores are {cross_val_score(knn, X_train, y_train, cv=5, scoring='accuracy')}")
toc = time.perf_counter()
print(f"The CV took {toc-tic} seconds. Yikes, better keep this in mind!")

from sklearn.model_selection import cross_val_predict
from sklearn.metrics import roc_auc_score, roc_curve, confusion_matrix, precision_recall_curve

y_train_pred = knn.predict(X_train)
cm = confusion_matrix(y_train,y_train_pred)
np.fill_diagonal(cm, 0)
plt.imshow(cm,cmap='Blues')
plt.colorbar()
plt.xlabel('Predicted')
plt.ylabel('True')
plt.title('Confusion Matrix')
plt.show()

from sklearn.metrics import classification_report

report = classification_report(y_train, y_train_pred)
print(report)

# y_train_score = knn.predict_proba(X_train)
# fpr, tpr, threshold = roc_curve(y_train, y_train_score[:,1])
# roc_auc = roc_auc_score(y_train,y_train_score[:,1])
# plt.plot(fpr, tpr, label='ROC (AUC = %0.2f)' % roc_auc)
# plt.xlabel('False Positive Rate')
# plt.ylabel('False Negative Rate')
# plt.title('ROC Curve')
# plt.legend()
# plt.show()

#precision, recall, thresholds = precision_recall_curve(y_train,y_train_score[:,1])
#plt.plot(recall,precision,label='Precision-Recall')
#plt.xlabel('Recall')
#plt.ylabel('Precision')
#plt.legend()
#plt.show()

"""Simple developed CRNN model"""

import numpy as np
from sklearn.model_selection import train_test_split
from keras.utils import to_categorical
from keras.models import Sequential, Model
from keras.layers import Dense, Dropout, Activation, Conv2D, MaxPooling2D, Flatten, LSTM, TimeDistributed, Input, Reshape

# Load the data
X, y = fetch_openml(data_id=41982, as_frame=False, return_X_y=True)

# Convert data to float32 and normalize it between 0 and 1
X = X.astype('float32') / 255.

# Reshape the data to a 4D tensor
X = X.reshape(X.shape[0], 28, 28, 1)

# Convert labels to one-hot encoded vectors
y = to_categorical(y)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)

# Define the model
inputs = Input(shape=(28, 28, 1))
conv1 = Conv2D(32, (3, 3), activation='relu')(inputs)
pool1 = MaxPooling2D(pool_size=(2, 2))(conv1)
conv2 = Conv2D(64, (3, 3), activation='relu')(pool1)
pool2 = MaxPooling2D(pool_size=(2, 2))(conv2)
flatten = Flatten()(pool2)
dense1 = Dense(128, activation='relu')(flatten)
reshape = Reshape((1, 128))(dense1)
lstm = LSTM(32, return_sequences=False)(reshape)
output = Dense(10, activation='softmax')(lstm)

model = Model(inputs=inputs, outputs=output)

# Compile the model
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# Train the model
history = model.fit(X_train, y_train, batch_size=32, epochs=10, validation_data=(X_test, y_test))

# Plot training & validation accuracy values
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('Model accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['Train', 'Validation'], loc='upper left')
plt.show()

# Plot training & validation loss values
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Model loss')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(['Train', 'Validation'], loc='upper left')
plt.show()

from sklearn.metrics import classification_report

# Evaluate the model on the test set
y_pred = model.predict(X_test)
y_pred_classes = np.argmax(y_pred, axis=1)
y_test_classes = np.argmax(y_test, axis=1)

# Calculate precision, recall, and f1-score for each class
report = classification_report(y_test_classes, y_pred_classes, output_dict=True)

# Plot the precision, recall, and f1-score for each class
for class_name, metrics in report.items():
    if class_name.isdigit():
        precision = metrics['precision']
        recall = metrics['recall']
        f1_score = metrics['f1-score']
        print(f"Class {class_name} - Precision: {precision:.3f}, Recall: {recall:.3f}, F1-score: {f1_score:.3f}")

import matplotlib.pyplot as plt
from sklearn.metrics import precision_recall_curve, average_precision_score

# Make predictions on the test data
y_pred = model.predict(X_test)

# Calculate the average precision score
average_precision = average_precision_score(y_test, y_pred, average='weighted')

# Calculate precision and recall for different probability thresholds
precision, recall, _ = precision_recall_curve(y_test.ravel(), y_pred.ravel())

# Plot the precision-recall curve
plt.plot(recall, precision)
plt.xlabel('Recall')
plt.ylabel('Precision')
plt.title('Precision-Recall Curve (AP = {:.2f})'.format(average_precision))
plt.show()

from sklearn.metrics import roc_curve, roc_auc_score
import matplotlib.pyplot as plt

# Get predicted probabilities for the test set
y_pred_proba = model.predict(X_test)

# Calculate false positive rate and true positive rate at different thresholds
fpr, tpr, thresholds = roc_curve(y_test[:,1], y_pred_proba[:,1])

# Calculate area under the ROC curve
roc_auc = roc_auc_score(y_test[:,1], y_pred_proba[:,1])

# Plot the ROC curve
plt.plot(fpr, tpr, label='ROC curve (area = %0.2f)' % roc_auc)
plt.plot([0, 1], [0, 1], 'k--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver operating characteristic')
plt.legend(loc="lower right")
plt.show()

"""New model with PCA"""

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.decomposition import PCA
from keras.utils import to_categorical
from keras.models import Sequential, Model
from keras.layers import Dense, Dropout, Activation, Conv2D, MaxPooling2D, Flatten, LSTM, TimeDistributed, Input, Reshape

# Apply PCA to reduce dimensionality to 50 features 
pca = PCA(n_components=50)
X = pca.fit_transform(X.reshape(X.shape[0], -1))
X = X.reshape(X.shape[0], 5, 10, 1)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)

# Define the model
inputs = Input(shape=(5, 10, 1))
conv1 = Conv2D(32, (3, 3), padding='same', activation='relu')(inputs)
pool1 = MaxPooling2D(pool_size=(2, 2))(conv1)
conv2 = Conv2D(64, (3, 3), padding='same', activation='relu')(pool1)
pool2 = MaxPooling2D(pool_size=(2, 2))(conv2)
flatten = Flatten()(pool2)
dense1 = Dense(128, activation='relu')(flatten)
reshape = Reshape((1, 128))(dense1)
lstm = LSTM(32, return_sequences=False)(reshape)
output = Dense(10, activation='softmax')(lstm)

model = Model(inputs=inputs, outputs=output)

# Compile the model
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# Train the model
history = model.fit(X_train, y_train, batch_size=32, epochs=10, validation_data=(X_test, y_test))

# Load the data
X, y = fetch_openml(data_id=41982, as_frame=False, return_X_y=True)

# Convert data to float32 and normalize it between 0 and 1
X = X.astype('float32') / 255.


# Apply PCA to reduce the number of components to 200
pca = PCA(n_components=200)
X = pca.fit_transform(X)

# Reshape the data to a 4D tensor
X = X.reshape(X.shape[0], 10, 20, 1)

# Convert labels to one-hot encoded vectors
y = to_categorical(y)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)

# Define the model
inputs = Input(shape=(10, 20, 1))
conv1 = Conv2D(32, (3, 3), padding='same', activation='relu')(inputs)
pool1 = MaxPooling2D(pool_size=(2, 2))(conv1)
conv2 = Conv2D(64, (3, 3), padding='same', activation='relu')(pool1)
pool2 = MaxPooling2D(pool_size=(2, 2))(conv2)
flatten = Flatten()(pool2)
dense1 = Dense(128, activation='relu')(flatten)
reshape = Reshape((1, 128))(dense1)
lstm = LSTM(32, return_sequences=False)(reshape)
output = Dense(10, activation='softmax')(lstm)

model = Model(inputs=inputs, outputs=output)

# Compile the model
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# Train the model
history = model.fit(X_train, y_train, batch_size=32, epochs=10, validation_data=(X_test, y_test))

