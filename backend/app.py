import os
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from sentiment import getSentiment
app = Flask(__name__)
cors = CORS(app)

@app.route('/', methods=['GET', 'POST']) ##defining route/end point, methods?
@cross_origin()
def SetValues(): ##function to return floating point representation to front end
    comments = request.form.getlist('comments[]')
    links = request.form.getlist('links[]')
    return jsonify({"data": getSentiment(comments, links)})#ValueArray

if __name__ == "__main__":
    app.run(debug = True)