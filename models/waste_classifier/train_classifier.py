"""Transfer-learning trainer (MobileNetV2) for the 3-class waste model.

Usage:  python models/waste_classifier/train_classifier.py --data dataset --epochs 8
Expected layout:  dataset/train/<Class>/*.jpg   dataset/val/<Class>/*.jpg
Model input: raw 0-255 RGB 224x224 (preprocessing is embedded in the model).
"""
import argparse
import json
from pathlib import Path

import tensorflow as tf

OUT = Path(__file__).parent

ap = argparse.ArgumentParser()
ap.add_argument("--data", required=True)
ap.add_argument("--epochs", type=int, default=8)
args = ap.parse_args()

train = tf.keras.utils.image_dataset_from_directory(Path(args.data) / "train", image_size=(224, 224), batch_size=32)
val = tf.keras.utils.image_dataset_from_directory(Path(args.data) / "val", image_size=(224, 224), batch_size=32)
classes = train.class_names
print("Classes:", classes)

base = tf.keras.applications.MobileNetV2(input_shape=(224, 224, 3), include_top=False, weights="imagenet")
base.trainable = False
aug = tf.keras.Sequential([tf.keras.layers.RandomFlip("horizontal"), tf.keras.layers.RandomRotation(0.1),
                           tf.keras.layers.RandomZoom(0.1)])
inputs = tf.keras.Input((224, 224, 3))
x = aug(inputs)
x = tf.keras.applications.mobilenet_v2.preprocess_input(x)
x = base(x, training=False)
x = tf.keras.layers.GlobalAveragePooling2D()(x)
x = tf.keras.layers.Dropout(0.3)(x)
outputs = tf.keras.layers.Dense(len(classes), activation="softmax")(x)
model = tf.keras.Model(inputs, outputs)
model.compile("adam", "sparse_categorical_crossentropy", metrics=["accuracy"])
model.fit(train, validation_data=val, epochs=args.epochs)
model.save(OUT / "model.keras")
(OUT / "labels.json").write_text(json.dumps(classes))
print("Saved model.keras and labels.json")
