from IPython.display import clear_output
from bson.objectid import ObjectId
import pymongo

class PoolDatabase:

    def __init__(self, init_app=True):
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.client["pools"]

    def map_to_geo(self, points):
        return list(map(lambda p: { 'type': 'Point', 'coordinates': p }, points))

    def map_from_geo(self, points):
        return list(map(lambda p: [p['coordinates'][0], p['coordinates'][1]], points))

    def set_batch(self, batch, geo_fields=[]):
        obj = { k: batch.get(k) if k not in geo_fields else self.map_to_geo(batch.get(k)) for k in batch.keys() }
        if self.db['batches'].find_one({ '_id': obj['_id'] }) is None:
            self.db['batches'].insert_one(obj)
        else:
            self.db['batches'].replace_one({ '_id': obj['_id'] }, obj)

    def get_batch(self, _id, geo_fields=[]):
        obj = self.db['batches'].find_one(ObjectId(_id))
        return { k: obj.get(k) if k not in geo_fields else self.map_from_geo(obj.get(k)) for k in obj.keys() }

    def summary_batches(self):
        keys = ['width', 'height', 'zoomLevel', 'is_working', 'progress', 'todo', 'done', 'nodes', '_id', 'name', 'osm_done', 'pools_detected']
        len_keys = ['todo', 'done']
        geo_keys = ['nodes']
        stream = self.db['batches'].find({})
        def map(obj):
            return { k: len(obj.get(k)) if k in len_keys else (self.map_from_geo(obj.get(k)) if k in geo_keys else obj.get(k)) for k in obj.keys() if k in keys}
        return [map(obj) for obj in stream]
    
    def set_point(self, point):
        point['coordinates'] = self.map_to_geo([point['coordinates']])[0]
        if self.db['pools'].find_one({ '_id': point['_id'] }) is None:
            self.db['pools'].insert_one(point)
        else:
            self.db['pools'].replace_one({ '_id': point['_id'] }, point)

    def get_pools_for_batch(self, batch_id):
        batch_id = ObjectId(batch_id)
        return list(self.db['pools'].find({ 'batch': batch_id }))

    def close_tasks_for_machine(self, machine_id):
        self.db['batches'].update_many({ 'working_machine': machine_id }, { '$set': { 'is_working': False } })

    def delete_batch(self, batch_id):
        if not self.get_batch(batch_id).get('is_working'):
            batch_id = ObjectId(batch_id)
            self.db['pools'].delete_many({ 'batch': batch_id })
            self.db['batches'].delete_one({ '_id': batch_id })
        else:
            raise Exception('Cannot remove working batch')
