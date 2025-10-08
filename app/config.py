import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    JSON_AS_ASCII = False
    MODEL_PRICE_UNIT = "crore"  # your model outputs crores