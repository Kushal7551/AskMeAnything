import io
import os
import json
import requests

import numpy as np
import tensorflow as tf

import pandas as pd
from flask import Blueprint, jsonify, request
from PIL import Image
from tensorflow.keras.models import load_model
from joblib import load

# from core import mongo_db

home = Blueprint("home", __name__)


def predict_soil_type(image, model):
    """
    Input the image and model, this function outputs the prediction as:
        1. The class with the highest probability
        2. A dictionary containing each class with their corresponding probability
    """

    LABELS = ["Red soil", "Black Soil", "Clay soil", "Alluvial soil"]

    label_encoder = {label: idx for idx, label in enumerate(LABELS)}
    label_decoder = {idx: label for idx, label in enumerate(LABELS)}
    label_encoder, label_decoder
    IMAGE_SIZE = 128
    image = Image.open(io.BytesIO(image))
    if image.mode != "RGB":
        image = image.convert("RGB")
    resized_img = image.resize((IMAGE_SIZE, IMAGE_SIZE))

    resized_img_array = np.array(resized_img)
    resized_img_array = resized_img_array.reshape(-1, IMAGE_SIZE, IMAGE_SIZE, 3)
    probabilities = model.predict(resized_img_array).reshape(-1)
    pred = LABELS[np.argmax(probabilities)]
    return pred


def predict_soil_moisture(image, model):
    LABELS = {
        0: "0",
        1: "10",
        2: "20",
        3: "30",
        4: "40",
        5: "50",
        6: "60",
        7: "70",
        8: "80",
    }

    IMAGE_SIZE = 256
    image = Image.open(io.BytesIO(image))
    if image.mode != "RGB":
        image = image.convert("RGB")

    # # Convert the image to a numpy array
    image_array = np.array(image)
    resize = tf.image.resize(image_array, (256, 256))
    print(type(resize))
    probabilities = model.predict(np.expand_dims(resize / 255, 0)).reshape(-1)
    pred = LABELS[np.argmax(probabilities)]
    return pred


def crop_suggestion(nitrogen, phosphorous, potassium, ph, lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ["temperature_2m", "relative_humidity_2m", "rain"],
        "timezone": "Asia/Singapore",
    }
    response = requests.get(url, params=params)
    data = response.json()

    temp = data["hourly"]["temperature_2m"]
    humidity = data["hourly"]["relative_humidity_2m"]
    rainfall = data["hourly"]["rain"]

    temp_avg = sum(temp) / len(temp)
    humidity_avg = sum(humidity) / len(humidity)
    rainfall_avg = sum(rainfall) / len(rainfall)

    input_data = pd.DataFrame(
        {
            "N": nitrogen,
            "P": phosphorous,
            "K": potassium,
            "temperature": temp_avg,
            "humidity": humidity_avg,
            "ph": ph,
            "rainfall": rainfall_avg,
        },
        index=[0],
    )
    dt_classifier_gini = load("trained_models/crop_pred.pkl")
    if dt_classifier_gini.predict(input_data):
        return {"crop": str(dt_classifier_gini.predict(input_data)[0])}
    else:
        return {"crop": "No crop found"}


# def find_data(collection_name, query):
#     try:
#         collection = mongo_db[collection_name]
#         result = collection.find_one(query)

#         if result:
#             return result
#         else:
#             return None
#     except:
#         pass


@home.route("/api")
def home_latest():
    return jsonify({"message": "Hello Server"})


@home.route("/api/predict", methods=["POST"])
def analyse_soil():
    model_soil_type = load_model("trained_models/soil_classification.h5")
    model_soil_moisture = load_model("trained_models/soil_moisture.h5")

    image = request.files.get("image")
    if image:
        img_bytes = image.read()
        pred_soil_type = predict_soil_type(img_bytes, model_soil_type)
        pred_soil_moisture = predict_soil_moisture(img_bytes, model_soil_moisture)
        return jsonify(
            {"soil_type": pred_soil_type, "soil_moisture": pred_soil_moisture}
        )

    return "no image found"


@home.route("/api/crop_suggest")
def crop_suggest_api():
    nitrogen = request.args.get("nitrogen", default=30)
    phosphorous = request.args.get("phosphorous", default=90)
    potassium = request.args.get("potassium", default=120)
    ph = request.args.get("ph", default=6)
    lat = request.args.get("lat", default=8.88113000)
    lon = request.args.get("lon", default=76.58469000)
    return crop_suggestion(
        nitrogen=nitrogen,
        phosphorous=phosphorous,
        potassium=potassium,
        ph=ph,
        lat=lat,
        lon=lon,
    )


# @home.route("/api/mongo", methods=["GET"])
# def mongo_test():
#     collection = mongo_db["test"]
#     data = {
#         "field1": "value1",
#         "field2": "value2",
#     }

#     # collection.insert_one(data)

#     query = {"field1": "value1"}
#     result = find_data("test", query)

#     if result:
#         return json.loads(json_util.dumps(result))

#     return "Not Found", 404
