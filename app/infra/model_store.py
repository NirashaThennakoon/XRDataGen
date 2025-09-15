from __future__ import annotations
import joblib
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model

def squeeze_axis1(x):
    return tf.squeeze(x, axis=1)

class ModelStore:
    def __init__(self, scaler_file: str, label_file: str, model_files: dict[str,str]):
        self.scaler = joblib.load(scaler_file)
        self.label_encoder = joblib.load(label_file)
        self._models: dict[str, tf.keras.Model] = {}
        self._model_files = model_files

    def model_for(self, sensor_id: str) -> tf.keras.Model:
        key = sensor_id if sensor_id in self._model_files else "default"
        if key not in self._models:
            m = load_model(self._model_files[key], compile=False,
                           custom_objects={"squeeze_axis1": squeeze_axis1})
            m.compile(optimizer="adam", loss="mse")
            self._models[key] = m
        return self._models[key]

    def scale(self, arr: np.ndarray) -> np.ndarray:
        return self.scaler.transform(arr)

    def inverse_scale(self, arr: np.ndarray) -> np.ndarray:
        return self.scaler.inverse_transform(arr)

    def encode_sensor(self, sensor_id: str) -> int:
        try:
            return int(self.label_encoder.transform([sensor_id])[0])
        except Exception:
            return int(self.label_encoder.transform([self.label_encoder.classes_[0]])[0])
