from flask import Flask, json, request, render_template
import controllerclient
import time
import threading

app = Flask(__name__)

controller = controllerclient.ControllerClient()

@app.route("/api/get_config", methods=["GET"])
def get_config():
    result = controller.get_config()

    response = app.response_class(
        response=json.dumps(result),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route("/api/set_config", methods=["POST"])
def set_config():
    result = controller.set_config(request.get_json()["config"])

    response = app.response_class(
        response=json.dumps(result),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route("/api/save_config", methods=["POST"])
def save_config():
    result = controller.save_config(request.get_json()["config"])

    response = app.response_class(
        response=json.dumps(result),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route("/api/get_state", methods=["GET"])
def get_state():
    result = controller.get_state()

    response = app.response_class(
        response=json.dumps(result),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route("/api/input_event", methods=["POST"])
def input_event():
    result = controller.send_input_event(request.get_json()["inputEvent"])

    response = app.response_class(
        response=json.dumps(result),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route("/settings")
def settings():
    config_data = controller.get_config()
    title = config_data.get("config", {}).get("settings", {}).get("title", "LED Display")
    return render_template('settings.html', title=title)

@app.route("/")
def index():
    config_data = controller.get_config()
    title = config_data.get("config", {}).get("settings", {}).get("title", "LED Display")
    return render_template('index.html', title=title)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
