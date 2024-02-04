from flask import Flask, jsonify

app = Flask(__name__)


@app.route('/')
def hello():
    return "Hello, this is your micro-service!"


@app.route('/metrics')
def metrics():
    # Include some dummy metrics for demonstration
    return jsonify({"metric_name": 42})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
