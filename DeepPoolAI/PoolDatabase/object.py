from IPython.display import clear_output
import pymongo

class PoolDatabase:

    def __init__(self, init_app=True):
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.client["pools"]
