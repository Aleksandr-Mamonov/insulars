from flask import Flask, url_for, redirect
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app)


@app.route("/")
def index():
    return redirect(url_for("static", filename="index.html"))


@socketio.on("my event")
def handle_my_custom_event(json):
    emit("my event", {1: 10, 2: 20}, broadcast=True)


if __name__ == "__main__":
    socketio.run(app)
