from flask import Flask, request, jsonify, render_template
from flask_cors import CORS, cross_origin


app = Flask(__name__)
CORS(app)  # Enable CORS for the entire application

@app.route('/')
@cross_origin()  # Enable CORS for this specific route
def index():
    # do something...
    return 'Surf API flask app'


@app.route('/test', methods=['POST'])
@cross_origin()  # Enable CORS for this specific route
def test():
    message = request.json['message']
    response = '[Port: /test] success'
    print('Prot: /test, Get: ', message)
    tag = 'test'
    return jsonify({'res': response, 'tag': tag})


if __name__ == '__main__':
    app.run(debug=True)