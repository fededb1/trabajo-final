# -*- coding: utf-8 -*-
"""Untitled2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1MkSKiUTc_FZymcDHA4ChSb3irJMvBuEt
"""

#Crear las carpetas para subir las imagenes
!mkdir plastico 
!mkdir vidrio
!mkdir latas
!mkdir organicos

# Commented out IPython magic to ensure Python compatibility.
#Entrar en cada carpeta y descomprimir el archivo zip
# %cd plastico
!unzip plastico.zip
# %cd ..

# %cd latas
!unzip lata.zip
# %cd ..

# %cd organicos
!unzip organico.zip
# %cd ..

# %cd vidrio
!unzip vidrio.zip
# %cd ..

#Borrar los archivo ZIP
!rm -rf /content/latas/lata.zip
!rm -rf /content/organicos/organico.zip
!rm -rf /content/plastico/plastico.zip
!rm -rf /content/vidrio/vidrio.zip

#Mostrar cuantas imagenes tengo de cada categoria
!ls /content/latas/lata | wc -l #206
!ls /content/organicos/organico | wc -l #227
!ls /content/plastico/plastico | wc -l #223
!ls /content/vidrio/vidrio  | wc -l #269

#Mostrar algunas imagenes con pyplot
import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

plt.figure(figsize=(15,15))

carpeta = '/content/latas/lata'
imagenes = os.listdir(carpeta)

for i, nombreimg in enumerate(imagenes[:25]):
  plt.subplot(5,5,i+1)
  imagen = mpimg.imread(carpeta + '/' + nombreimg)
  plt.imshow(imagen)

"""COMENTARIO: Tensorflow tiene formas oficiales para hacer set de datos y que puedan ser tan grandes como sea necesario sin que se cargen todos en memoria a la vez """

#Crear carpetas para hacer el set de datos
# 
!mkdir dataset
!mkdir dataset/latas
!mkdir dataset/organico
!mkdir dataset/plastico
!mkdir dataset/vidrio

#Copiar imagenes que subimos a carpetas del dataset
#Limitar para que todos tengan la misma cantidad de imagenes
#maximo 206 (el num. menor de imagenes que subi) **LATAS**
import shutil
carpeta_fuente = '/content/latas/lata'
carpeta_destino = '/content/dataset/latas'

imagenes = os.listdir(carpeta_fuente)

for i, nombreimg in enumerate(imagenes):
  if i < 206:
    #Copia de la carpeta fuente a la destino
    shutil.copy(carpeta_fuente + '/' + nombreimg, carpeta_destino + '/' + nombreimg)

#**ORGANICOS**
carpeta_fuente = '/content/organicos/organico'
carpeta_destino = '/content/dataset/organico'

imagenes = os.listdir(carpeta_fuente)

for i, nombreimg in enumerate(imagenes):
  if i < 206:
    #Copia de la carpeta fuente a la destino
    shutil.copy(carpeta_fuente + '/' + nombreimg, carpeta_destino + '/' + nombreimg)

#**PLASTICO**
carpeta_fuente = '/content/plastico/plastico'
carpeta_destino = '/content/dataset/plastico'

imagenes = os.listdir(carpeta_fuente)

for i, nombreimg in enumerate(imagenes):
  if i < 206:
    #Copia de la carpeta fuente a la destino
    shutil.copy(carpeta_fuente + '/' + nombreimg, carpeta_destino + '/' + nombreimg)

#**VIDRIO**
carpeta_fuente = '/content/vidrio/vidrio'
carpeta_destino = '/content/dataset/vidrio'

imagenes = os.listdir(carpeta_fuente)

for i, nombreimg in enumerate(imagenes):
  if i < 206:
    #Copia de la carpeta fuente a la destino
    shutil.copy(carpeta_fuente + '/' + nombreimg, carpeta_destino + '/' + nombreimg)

#Mostrar cuantas imagenes tengo de cada categoria
!ls /content/dataset/latas | wc -l #206
!ls /content/dataset/organico | wc -l #227
!ls /content/dataset/plastico | wc -l #206
!ls /content/dataset/vidrio | wc -l #206

#Aumento de datos con ImageDataGenerator
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import numpy as np

#Crear el dataset generador
datagen = ImageDataGenerator(
    rescale=1. / 255,          #normalizamos las imagenes para que nos de entre 0 y 1
    rotation_range = 30,
    width_shift_range = 0.25,
    height_shift_range = 0.25,
    shear_range = 15,
    zoom_range = [0.5, 1.5],
    validation_split=0.2 #20% para pruebas y 80% para entrenamiento
)

#Generadores para sets de entrenamiento y pruebas
data_gen_entrenamiento = datagen.flow_from_directory('/content/dataset', target_size=(224,224),    #redimencionamos la imagen en 224 x 224
                                                     batch_size=32, shuffle=True, subset='training')
data_gen_pruebas = datagen.flow_from_directory('/content/dataset', target_size=(224,224),
                                                     batch_size=32, shuffle=True, subset='validation')

#Imprimir 10 imagenes del generador de entrenamiento
for imagen, etiqueta in data_gen_entrenamiento:
  for i in range(10):
    plt.subplot(2,5,i+1)
    plt.xticks([])
    plt.yticks([])
    plt.imshow(imagen[i])
  break
plt.show()
# COMENTARIO: podemos ver que las imagenes estan mescladas y estan giradas o invertidas para tener mas muestras y ahora todas las imagenes son de 224x224

#importamos la red neuronal mobilenet_V2 (es la red sin la ultima capa) en la cual le vamos a cargar nuestas entradas
import tensorflow as tf
import tensorflow_hub as hub

url = "https://tfhub.dev/google/tf2-preview/mobilenet_v2/feature_vector/4"
mobilenetv2 = hub.KerasLayer(url, input_shape=(224,224,3)) #cargamos la forma de entrada que espera el modelo

#antes de modelar necesitamos congelar los sesgos y parametros
#Congelar el modelo descargado
mobilenetv2.trainable = False

#realizamos el modelado
modelo = tf.keras.Sequential([
    mobilenetv2,
    tf.keras.layers.Dense(4, activation='softmax') #cargamos nuestra ultima capa con las 4 opciones posibles
])

modelo.summary()
#COMENTARIO: como podemos observar ahora tenemos un total de 2.263.108 de parametros

#Compilar 
modelo.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

#Entrenar el modelo
EPOCAS = 50

historial = modelo.fit(
    data_gen_entrenamiento, epochs=EPOCAS, batch_size=32,
    validation_data=data_gen_pruebas
)

#Graficas de precisión
acc = historial.history['accuracy']
val_acc = historial.history['val_accuracy']

loss = historial.history['loss']
val_loss = historial.history['val_loss']

rango_epocas = range(50)

plt.figure(figsize=(8,8))
plt.subplot(1,2,1)
plt.plot(rango_epocas, acc, label='Precisión Entrenamiento')
plt.plot(rango_epocas, val_acc, label='Precisión Pruebas')
plt.legend(loc='lower right')
plt.title('Precisión de entrenamiento y pruebas')

plt.subplot(1,2,2)
plt.plot(rango_epocas, loss, label='Pérdida de entrenamiento')
plt.plot(rango_epocas, val_loss, label='Pérdida de pruebas')
plt.legend(loc='upper right')
plt.title('Pérdida de entrenamiento y pruebas')
plt.show()

#Categorizar una imagen de internet
#COMENTARIO: el objetivo es sacar una imagen de internet por URL, pasarla por filtro de normalizacion  
from PIL import Image
import requests
from io import BytesIO
import cv2

def categorizar(url):
  respuesta = requests.get(url)
  img = Image.open(BytesIO(respuesta.content))
  img = np.array(img).astype(float)/255

  img = cv2.resize(img, (224,224))
  prediccion = modelo.predict(img.reshape(-1, 224, 224, 3))
  return np.argmax(prediccion[0], axis=-1)

#COMENTARIO: la funcion recibe el URL , descarga la imagen y le hace las transformaciones necesarias
#0 = lata , 1 = organicos, 2 = plastico, 3=vidrio
url = 'https://th.bing.com/th/id/OIP.UrwQ82UlE8wu3oMw_po7jgHaEe?pid=ImgDet&rs=1' #debe ser 1
prediccion = categorizar (url)
print(prediccion)