from flask import Blueprint, request, abort, jsonify, render_template, Response, send_from_directory

from app import redis_client

bp = Blueprint('misc', __name__)

@bp.route("/geometry")
def queue_count():
    geo = redis_client.get("geometry") 
    if geo:
        geo = geo.decode()
    else:
        geo = {}
    return Response(geo, mimetype="application/json")
