import os
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from sentiment import getSentiment
import json
from tqdm import tqdm
app = Flask(__name__)
cors = CORS(app)

class DataStore():
    def __init__(self):
        self.data = {}
        for idx in tqdm(list(range(28))):
            with open('stubs/{}.json'.format(idx)) as f:
                self.data[idx] = json.load(f)
        print('done loading stub')
req_data = DataStore()

@app.route('/', methods=['GET', 'POST']) ##defining route/end point, methods?
@cross_origin()
def SetValues(): ##function to return floating point representation to front end
    idx = int(request.form['idx'])
    print(idx)
    data = req_data.data[idx]
    
    comments = data['comments']
    links = data['links']
    """comments = request.form.getlist('comments[]')
    links = request.form.getlist('links[]')

    data = {}
    data['comments'] = comments
    data['links'] = links

    with open('stubs/{}.json'.format(idx.val), 'w') as outfile:
        json.dump(data, outfile)
    
    idx.val+=1"""

    return jsonify({"data": getSentiment(comments, links)})#ValueArray

if __name__ == "__main__":
    app.run(debug = True)