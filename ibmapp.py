import numpy as np
from flask import Flask, request, jsonify, render_template
import pickle

app = Flask(__name__)
import requests
import json

# NOTE: you must manually set API_KEY below using information retrieved from your IBM Cloud account.
API_KEY = "RSrVCqHB3B6aTTlj7qv2uOit18LGBYoyoO3D3MBfOCsw"
token_response = requests.post('https://iam.cloud.ibm.com/identity/token', data={"apikey":
 API_KEY, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'})
mltoken = token_response.json()["access_token"]

header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken}
model = pickle.load(open("university.pkl", "rb"))

@app.route("/")
def home():
    return render_template('Demo2.html')

@app.route("/y_predict", methods = ["POST","GET"])
def y_predict():
    min1 = [290.0, 92.0, 1.0, 1.0, 1.0, 6.8, 1]
    max1 = [340.0, 120.0, 5.0, 5.0, 5.0, 9.92, 2]
    k = [float(x) for x in request.form.values()]
    print(k)
    p = []
    for i in range(7):
        l = (k[i]-min1[i])/(max1[i]-min1[i])
        p.append(l)
    prediction = model.predict([p])
    print(prediction)
    output = prediction[0]
    payload_scoring = {"input_data": [{"field": ['GRE Score','TOEFL Score',	'University Rating','SOP','LOR','CGPA',	'Research'],
                                       "values": [p]}]}

    response_scoring = requests.post(
        'https://us-south.ml.cloud.ibm.com/ml/v4/deployments/eb229ed6-7445-43de-9a43-efb01234d8b4/predictions?version=2022-07-30',
        json=payload_scoring,
        headers={'Authorization': 'Bearer ' + mltoken})
    print("Scoring response")
    prediction=response_scoring.json()
    print(prediction)
    output = prediction["predictions"][0]["values"][0][0]

    if output== False:
        return render_template("noChance.html", prediction_text="you dont have a chance")
    else:
        return render_template("chance.html", prediction_text="you have a chance")

if __name__ == "__main__":
    app.run(debug=True)