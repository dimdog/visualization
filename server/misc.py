from flask import Blueprint, request, abort, jsonify, render_template, Response, send_from_directory

from app import redis_client

bp = Blueprint('misc', __name__)

@bp.route("/vertex_list")
def queue_count():
    return Response(redis_client.get("vertex_list").decode(), mimetype="application/json")

@bp.route("/")
def index():
    return render_template('index.html')

@bp.route('/js/<path:path>')
def send_js(path):
    print(path)
    return send_from_directory('templates/js', path)

