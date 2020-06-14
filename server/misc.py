from flask import Blueprint, request, abort, jsonify, render_template

from app import redis_client

bp = Blueprint('misc', __name__)

@bp.route("/vertex_list")
def queue_count():
    return jsonify(redis_client.get("vertex_list"))

@bp.route("/")
def index():
    return render_template('index.html')

