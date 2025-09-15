import os

class Config:
    API_BASE = os.getenv("API_BASE", "https://query-backend-sensor-data-modeling.2.rahtiapp.fi")
    API_EMAIL = os.getenv("SCDM_EMAIL")
    API_PASSWORD = os.getenv("SCDM_PASSWORD")

    # ML files (override per env if needed)
    SCALER_FILE = os.getenv("SCALER_FILE", "scaler_gru_tuned.pkl")
    LABEL_ENCODER_FILE = os.getenv("LABEL_ENCODER_FILE", "label_encoder_gru.pkl")
    MODEL_FILES = {
        "A81758FFFE03101B": os.getenv("MODEL_SENSOR_A", "trained_model_sensor_A.keras"),
        "default": os.getenv("MODEL_DEFAULT", "trained_model.keras"),
    }

    SEQ_LEN = int(os.getenv("SEQ_LEN", "50"))
    PRED_HORIZON = int(os.getenv("PRED_HORIZON", "60"))
    LOCAL_TZ = os.getenv("LOCAL_TZ", "Europe/Helsinki")
