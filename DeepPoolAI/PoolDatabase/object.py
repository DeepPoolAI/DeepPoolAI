import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore as firestore_admin
from google.cloud import firestore
from IPython.display import clear_output

class PoolDatabase:

    def __init__(self):
        cred = credentials.Certificate('DeepPoolAI/PoolDatabase/deeppoolai-8665f3f59207.json')
        firebase_admin.initialize_app(cred)
        self.db = firestore_admin.client()

    def upload_pools(self, pool_data: list, location_id: str = None, verbose: bool = False):
        """ Uploads pool to Firebase Firestore, where data is safely stored.

        Parameters
        ----------
        pool_data: list
            List containing items with at least two fields
            {
                "coordinates": [latitude: float, longitude: float],
                "address": dict
            }

        location_id: str
            Not required
            If specified pools will be mapped to a specific location.

        verbose: bool
            If set to True, progress of upload will be displayed.
            Useful when uploading larger datasets
        -------

        """

        doc_ref = self.db.collection(u'pools')
        n = len(pool_data)

        for i in range(n):
            doc_ref.add({
                u'address': pool_data[i]["address"],
                u'clean': True,
                u'location_id':  location_id,
                u'coordinates': firestore.GeoPoint(pool_data[i]["coordinates"][0], pool_data[i]["coordinates"][1])
            })

            if verbose:
                clear_output(wait=True)
                print(f"Uploading progress {round(((i + 1) / n) * 100, 1)}%  {i + 1}/{n}")
                print("[{:<50}]".format("#" * (round((i + 1) / n * 100) // 2)))

    def update_pools(self, pool_data: list):
        pass

    def get_pools(self, id_list: list, verbose: bool = False):
        pass

    def show_locations(self, return_json: bool = False):
        pass

    def get_pools_from_location(self, location_id: str):
        pass
