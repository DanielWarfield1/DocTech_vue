import docTech
from flask import Flask, jsonify, request
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route("/")
def index():
    return app.send_static_file(filename='index.html')

@app.route("/query")
def query():
  query = request.args.get('query')
  page = int(request.args.get('current_page'))
  try:
    result = docTech.handle_query(query, {'current_page': page})
    if result['non_determ']:
        raise Exception('could not determine action')
    return jsonify(result)
  except Exception as e:
    print(e)
    return jsonify({ 'error': 'could not determine action!' })

if __name__ == "__main__":
  app.run(host='0.0.0.0')
