import os
import sys

# Ensure backend directory is in sys.path
current_dir = os.path.dirname(os.path.abspath(__file__)) # .../backend/app/models/emotion
backend_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "..")) # .../backend

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dense, Dropout, Flatten

def build_reference_model():
    """
    Builds the exact CNN architecture used by Emotion-detection reference repo.
    Conv2D(32, (3,3)) -> Conv2D(64, (3,3)) -> MaxPool -> Dropout(0.25)
    Conv2D(128, (3,3)) -> MaxPool -> Conv2D(128, (3,3)) -> MaxPool -> Dropout(0.25)
    Flatten -> Dense(1024) -> Dropout(0.5) -> Dense(7, softmax)
    """
    model = Sequential([
        Conv2D(32, (3, 3), activation='relu', input_shape=(48, 48, 1)),
        Conv2D(64, (3, 3), activation='relu'),
        MaxPooling2D((2, 2)),
        Dropout(0.25),

        Conv2D(128, (3, 3), activation='relu'),
        MaxPooling2D((2, 2)),
        Conv2D(128, (3, 3), activation='relu'),
        MaxPooling2D((2, 2)),
        Dropout(0.25),

        Flatten(),
        Dense(1024, activation='relu'),
        Dropout(0.5),
        Dense(7, activation='softmax')
    ])

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    return model

if __name__ == "__main__":
    nndl_root = os.path.abspath(os.path.join(backend_dir, ".."))
    weights_path = os.path.join(nndl_root, "Emotion-detection", "src", "model.weights.h5")
    output_path = os.path.join(current_dir, "moodtunes_emotion_cnn.keras")

    print(f"Building MoodTunes CNN architecture matching reference weights...")
    model = build_reference_model()

    if os.path.exists(weights_path):
        print(f"Loading weights from reference model at '{weights_path}'...")
        model.load_weights(weights_path)
        print("Weights loaded successfully!")
    else:
        print(f"Warning: Weights file not found at '{weights_path}'. Saving architecture with initialized weights.")

    model.save(output_path)
    print(f"Saved complete model artifact to '{output_path}'!")
