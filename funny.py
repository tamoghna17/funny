
from google.colab import drive
import os

drive.mount('/content/drive')

def load_text_data_from_drive_folder(folder_path):
    text_data_list = []


    full_folder_path = '/content/drive/My Drive/' + folder_path

    file_list = os.listdir(full_folder_path)
    i = 0

    for filename in file_list:
        i=i+1
        file_path = os.path.join(full_folder_path, filename)

        with open(file_path, 'r', encoding='utf-8') as file:
            text_data = file.read()
            text_data_list.append(text_data)

    return text_data_list


folder_path = 'funnytext'
text_data_list = load_text_data_from_drive_folder(folder_path)

import numpy
import re
import pandas as pd
import numpy as np
import keras
import string
import nltk

from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import LSTM
from keras.layers import Embedding
from keras.callbacks import ModelCheckpoint
from keras.utils import np_utils
from sklearn.model_selection import train_test_split
from keras.preprocessing.text import Tokenizer
from keras.utils import pad_sequences

string.punctuation = string.punctuation +'“'+'”'+'-'+'’'+'‘'+'—'
string.punctuation = string.punctuation.replace('.', '')

import nltk
nltk.download('punkt')

from nltk import word_tokenize,sent_tokenize



file_nl_removed = ""
for line in text_data_list:
  line_nl_removed = line.replace("\n", " ")

  file_nl_removed += line_nl_removed

file_p = "".join([char for char in file_nl_removed if char not in string.punctuation])

sents = nltk.sent_tokenize(file_p)
print("The number of sentences is", len(sents))


string.punctuation = string.punctuation + '.'
file_q = "".join([char for char in file_p if char not in string.punctuation])
words = nltk.word_tokenize(file_q)
print("The number of tokens is", len(words))


average_tokens = round(len(words)/len(sents))
print("The average number of tokens per sentence is", average_tokens)

unique_tokens = set(words)
print("The number of unique tokens are", len(unique_tokens))


preprocessed_text = file_p.lower()

vocab_size = 9312 #chosen based on statistics of the model


oov_tok = '<OOV>'
embedding_dim = 100


tokenizer = Tokenizer(num_words = vocab_size, oov_token=oov_tok)
tokenizer.fit_on_texts([preprocessed_text])
word_index = tokenizer.word_index

seq_length = 100
tokens = tokenizer.texts_to_sequences([preprocessed_text])[0]

dataX = []
dataY = []

for i in range(0, len(tokens) - seq_length-1 , 1):
  seq_in = tokens[i:i + seq_length]
  seq_out = tokens[i + seq_length]

  if seq_out==1:
    continue

  dataX.append(seq_in)
  dataY.append(seq_out)

N = len(dataX)
print ("Total training data size is -", N)
X = numpy.array(dataX)

y = numpy.array(dataY)
y = np_utils.to_categorical(dataY)

import pickle

with open('tokenizer.pkl', 'wb') as f:
    pickle.dump(tokenizer, f)

model = keras.Sequential([
    keras.layers.Embedding(vocab_size, embedding_dim, input_length=seq_length),
    keras.layers.Bidirectional(keras.layers.LSTM(64, input_shape=(X.shape[1], embedding_dim),return_sequences=True)),
    keras.layers.Dropout(0.2),
    keras.layers.LSTM(64),
    keras.layers.Dropout(0.2),
    keras.layers.Dense(vocab_size, activation='softmax')

])


model.compile(loss='categorical_crossentropy',
              optimizer='adam',
              metrics=['accuracy'])

# model summary
model.summary()

num_epochs = 4
history = model.fit(X, y, epochs=num_epochs, batch_size = 128, verbose=1, validation_split=0.2)

import os

import tensorflow as tf
from tensorflow import keras

model = tf.keras.models.load_model('my_model.keras')

model.save('my_model.keras')

reverse_word_map = dict(map(reversed, tokenizer.word_index.items()))


def next_tokens(input_str, n):
    print ("Seed -",  input_str, sep = '\n\n')
    final_string = ''
    for i in range(n):
        token = tokenizer.texts_to_sequences([input_str])[0]

        prediction = model.predict([token], verbose=0)
        lista = list(range(0,9312))
        word = reverse_word_map[numpy.random.choice(a = lista, p = prediction[0])]
        final_string = final_string + word + ' '
        input_str = input_str + ' ' + word
        input_str = ' '.join(input_str.split(' ')[1:])
    return final_string

start = numpy.random.randint(0, len(dataX)-1)
pattern = dataX[start]
input_str = ' '.join([reverse_word_map[value] for value in pattern])

output = next_tokens(input_str, 50)
print("\nGenerated string -\n\n", output)
