import os
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from sentiment import getSentiments
app = Flask(__name__)
cors = CORS(app)

@app.route('/', methods=['GET', 'POST']) ##defining route/end point, methods?
@cross_origin()
def SetValues(): ##function to return floating point representation to front end
    subreddit = request.form['subreddit']
    start = request.form['start']
    end = request.form['end']
    
    return jsonify({"sentiments": getSentiments(subreddit, start, end)})#ValueArray

if __name__ == "__main__":
    app.run(debug = True)