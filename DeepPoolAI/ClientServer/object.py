from flask import Flask, request, abort, Response
from flask_cors import CORS
import numpy as np
import logging
import sys
import json
from ..PoolDatabase.object import PoolDatabase
from ..SateliteImages.object import PolygonPhotos
from bson.objectid import ObjectId

def convert(o):
    if isinstance(o, np.generic):
        return o.item()
    if isinstance(o, ObjectId):
        return str(o)
    raise TypeError

class ClientServer:
    def __init__(self):
        self.db = PoolDatabase(init_app=False)

    def start_server(self, host, port, disable_logs):
        cli = sys.modules['flask.cli']
        cli.show_server_banner = lambda *x: None
        app = Flask(__name__)
        CORS(app)
        
        log = logging.getLogger('werkzeug')
        log.disabled = disable_logs
        app.logger.disabled = disable_logs
    
    
        @app.route("/", methods=['GET'])
        def main():
            result = {
                'ok': True
            }
            return Response(json.dumps(result, default=convert), content_type='application/json')

        @app.route("/polygon/<int:polygon_id>", methods=['GET'])
        def get_polygon(polygon_id):
            result = self.db.get_pools_for_polygon(polygon_id)
            result = [{ 'clean': r.get('clean'), 'address': (r.get('address') or {}).get('address') } for r in result]
            return Response(json.dumps(result, default=convert), content_type='application/json')

        app.run(host=host, port=port)
