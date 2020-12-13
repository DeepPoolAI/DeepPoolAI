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

class AdminServer:
    def __init__(self, bing_key, machine_id):
        self.bing_key_file = bing_key
        with open(bing_key, 'r') as f:
            self.bing_key = f.read()
        self.db = PoolDatabase(init_app=False)
        self.machine_id = machine_id
        self.db.close_tasks_for_machine(machine_id)

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

        @app.route("/batches", methods=['GET'])
        def get_batches():
            result = self.db.summary_batches()
            for r in result:
                r['batch_id'] = r.get('_id')
            return Response(json.dumps(result, default=convert), content_type='application/json')
        
        @app.route("/batches", methods=['POST'])
        def add_batch():
            data = request.get_json()
            pp = PolygonPhotos(data.get('nodes'), self.bing_key, data.get('zoomLevel'), data.get('width'), data.get('height'), data.get('name'))
            pp.export_to_db()
            return Response(json.dumps({ 'ok': True }, default=convert), content_type='application/json')

        @app.route("/batches/<string:batch_id>/run", methods=["POST"])
        def run_batch(batch_id):
            data = request.get_json()
            pp = PolygonPhotos.import_from_db(self.bing_key, batch_id)
            if pp is None:
                abort(404)
            pp.fit(data.get('coverage'), [data.get('sleep_min'), data.get('sleep_max')], self.machine_id)
            return Response(json.dumps({ 'ok': True }, default=convert), content_type='application/json')
        
        @app.route("/batches/<string:batch_id>/osm", methods=["POST"])
        def osm_batch(batch_id):
            pp = PolygonPhotos.import_from_db(self.bing_key, batch_id)
            pp.get_osm_data(self.machine_id)
            return Response(json.dumps({ 'ok': True }, default=convert), content_type='application/json')

        app.run(host=host, port=port)
