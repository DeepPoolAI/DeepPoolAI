import json
import random
import time
from copy import deepcopy
from urllib.request import urlopen

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from tqdm import tqdm

from .utils import coverTerrain, _PixelXYToLatLong, _LatLongToPixelXY
from ..PoolDetector.object import PoolDetector

from .utils import  coverTerrain, _PixelXYToLatLong, _LatLongToPixelXY, coverPolygon
from ..PoolDetector.object import PoolDetector
from tqdm import tqdm
import numpy as np
import random
import time
from ..PoolDatabase.object import PoolDatabase
from bson.objectid import ObjectId
from ..PoolAddressParser.object import PoolAddressParser
from ..PoolPolygonsFinder.object import PoolPolygonsFinder

class SquareAerialImage:

    def __init__(self, key, zoomLevel):
        """Square Aerial Image
        Wrapper for Bing api

        Parameters
        ----------
        key : string
            Bing Api key
        zoomLevel : integer
            integer between [1,21], amount of zoom in the picture

        Returns
        -------
        SquareAerialImage object that stores information about key and zoom of an image
        """

        self.key = key
        self.zoomLevel = zoomLevel

        return

    def get_square_photo(self, lat, long):
        """ Get Square Photo
        Gets square 256x256 photo of area given the long and lat.
        Uses zoom level and key from the object.

        Parameters
        ----------
        lat : double
            latitude
        long : double
            longitude

        Returns
        -------
        Square photo without label on lower bound
        """
        request = urlopen("https://dev.virtualearth.net/REST/V1/Imagery/Metadata/Aerial/"
                          f"{lat},{long}?zl={self.zoomLevel}"
                          "&o&"  # json
                          f"key={self.key}")

        json_request = json.loads(request.read())
        image_url = json_request['resourceSets'][0]['resources'][0]['imageUrl']
        image = Image.open(urlopen(image_url))

        return image


class AerialImage(SquareAerialImage):
    """Square Aerial Image
      Wrapper for Bing api. Extension for square aerial image.
      It is possible to get rectangle images via width and height
      parameters.

      Parameters
      ----------
      key : string
          Bing Api key
      zoomLevel : integer
          integer between [1,21], amount of zoom in the picture
      height : integer
          height of an aerial map in pixels. Does not work with square

      width : integer
          width of an aerial map in pixels

      Returns
      -------
      AerialImage object that stores information about key, zoom, height and width of an image
    """

    def __init__(self, key, zoomLevel, width=1080, height=720):
        super().__init__(key, zoomLevel)
        self.height = height
        self.width = width

    def get_photo(self, lat, long):
        """ Get Photo
        Gets photo of area given the long, lat.
        Uses zoom level, width, height and key from the object.

        Parameters
        ----------
        lat : double
            latitude
        long : double
            longitude


        Returns
        -------
        Photo of custom size

        """

        request = f"https://dev.virtualearth.net/REST/v1/Imagery/Map/Aerial/{lat},{long}/{self.zoomLevel}?" \
                  f"mapSize={self.width},{self.height}&key={self.key}"

        image = Image.open(urlopen(request))

        return image

    def get_coords(self, lat1, long1, lat2, long2):
        """
        Get coords between 2 rectangle points. They can be then
        iterated and plotted.

        Return:
            np.ndarray
        """

        coords = coverTerrain(lat1, lat2, long1, long2, self.zoomLevel, self.width, self.height)
        return coords

    def get_grid_photos(self, lat1, long1, lat2, long2):
        """
        Returns a tuple (array_of_photos, plt)
        """

        coords = self.get_coords(lat1, long1, lat2, long2)
        if len(list(coords.shape)) != 3:
            raise Exception("You should bet a bit bigger terrain, grid should be at least 2x2 to work")
        coords_shape = coords.shape[0:2]

        f, axarr = plt.subplots(coords_shape[1],
                                coords_shape[0], squeeze=True)
        photos = []
        for i in range(coords_shape[0]):
            for j in range(coords_shape[1]):
                photo = self.get_photo(coords[i][j][0], coords[i][j][1])
                photos.append(photo)
                axarr[j, i].axis("off")
                axarr[j, i].imshow(photo, aspect='auto')

        plt.subplots_adjust(hspace=0, wspace=0)
        return photos, plt


class GridPhotos:

    def __init__(self, lat1, long1, lat2, long2, key, zoomLevel, width, height, coverage=1, sleep_range=[0, 0]):

        ai = AerialImage(key, zoomLevel, width, height)
        self.ai = ai

        self.width = width
        self.height = height
        self.zoomLevel = zoomLevel
        self.photos = None
        self.pool_coords = None
        self.cleanness = np.array([])  # starts with none
        self.lat1 = lat1
        self.long1 = long1
        self.lat2 = lat2
        self.long2 = long2
        self.coords = coverTerrain(lat1, lat2, long1, long2, zoomLevel, width, height)
        self.coverage = coverage
        self.sleep_range = sleep_range

    def fit(self):
        coords = self.coords
        # no matter the grid
        coords = deepcopy(coords.flatten().reshape(1, coords.shape[0] * coords.shape[1], 2)[0])

        pool_coordinates = []
        for coord in tqdm(list(filter(lambda c: random.random() < self.coverage, coords))):
            time.sleep(random.uniform(self.sleep_range[0], self.sleep_range[1]))
            pd = PoolDetector(self.ai.get_photo(coord[0], coord[1]))
            pd.get_pools()
            self.cleanness = np.append(self.cleanness, np.where(np.array(pd.mean_colors)[:, 1] - 15 >
                                        np.array(pd.mean_colors)[:, 2],
                                         'not-clean', 'clean'))

            middle_x = self.width // 2
            middle_y = self.height // 2
            if pd.pixel_coords is not None:
                for pool_coord in np.floor(pd.pixel_coords):
                    x, y = _LatLongToPixelXY(coord[0], coord[1], self.zoomLevel)
                    diff_x = pool_coord[0] - middle_x
                    diff_y = pool_coord[1] - middle_y
                    lat, long = _PixelXYToLatLong(x + diff_x, y + diff_y, self.zoomLevel)
                    pool_coordinates.append([lat, long])
            pd = None

        self.pool_coords = pool_coordinates

        return

    def get_grid(self):
        """
               Saves all grid photos within object array.
               Prints whole grid.
        """
        self.ai.get_grid_photos(self.lat1, self.long1, self.lat2, self.long2)

    def get_grid_photo(self, i):
        """
        Gets particular photo from saved grid

        Parameters
        ----------
        i : double
            photo index

        Returns
        -------
        Grid photo of given index
        """
        if self.photos is None:
            raise Exception("No photos found - you need to load grid by get_grid() first")
        return self.photos[i]


class Pool:
    exportable_fields = ['coordinates', '_id', 'color', 'clean', 'address', 'osm', 'batch']
    def __init__(self, lat, lng, batch):
        self.coordinates = [lat, lng]
        self.batch = batch
        self.color = None
        self.clean = None
        self.address = None
        self.osm = None
        self._id = None

    def find_address(self, key):
        if self.address is None:
            parser = PoolAddressParser(key)
            try:
                self.address = parser.get_addresses([self.coordinates], verbose=False)[0]
            except:
                pass

    def export_to_db(self, db):
        if self._id is None:
            self._id = ObjectId()
        if db is None:
            db = PoolDatabase()
        data = {}
        for field in self.exportable_fields:
            data[field] = self.__getattribute__(field)
        db.set_point(data)

    @staticmethod
    def import_obj(obj):
        coordinates = obj.get('coordinates').get('coordinates')
        pool = Pool(coordinates[0], coordinates[1], obj.get('batch'))
        for k in ['color', 'clean', 'address', 'osm', '_id']:
            pool.__setattr__(k, obj.get(k))
        return pool

class PolygonPhotos:
    exportable_fields = ['nodes', 'todo', 'done', '_id', 'width', 'height', 'zoomLevel', 'progress', 'is_working', 'name', 'osm_done', 'pools_detected', 'working_machine']

    def __init__(self, nodes, key, zoomLevel, width, height, name='unnamed'):
        ai = AerialImage(key, zoomLevel, width, height)
        self.ai = ai
        self.key = key
        self.width = width
        self.height = height
        self.zoomLevel = zoomLevel
        self.photos = None
        self.pool_coords = []
        self.nodes = nodes
        self.todo = coverPolygon(nodes, zoomLevel, width, height)
        self.done = []
        self.is_working = False
        self.progress = 0
        self.working_machine = None
        self.name = name
        self.pool_buffer = []
        self._id = None
        self.osm_done = False
        self.pools_detected = 0

    def get_osm_data(self, working_machine=None):
        db = PoolDatabase()
        self.update()
        if self.is_working:
            raise Exception('Already running')
        self.working_machine = working_machine
        self.is_working = True
        self.progress = -1 # unncountable progress
        self.export_to_db()

        pools = db.get_pools_for_batch(self._id)
        pools = list(map(lambda x: Pool.import_obj(x), pools))
        coords = list(map(lambda x: x.coordinates, pools))
        ppf = PoolPolygonsFinder()
        levels = [4, 6, 8]
        polygons = ppf.assign_polygons(coords, level=levels)
        for index, pool in enumerate(pools):
            pool.osm = { 'lvl_' + str(k): polygons[i][index] for i, k in enumerate(levels) }
            pool.export_to_db(db)
        self.osm_done = True
        self.is_working = False
        self.export_to_db()

    @staticmethod
    def import_from_db(key, _id):
        db = PoolDatabase()
        batch = db.get_batch(_id, geo_fields=['done', 'todo', 'nodes'])
        obj = PolygonPhotos(batch.get('nodes'), key, batch.get('zoomLevel'), batch.get('width'), batch.get('height'))
        for field in PolygonPhotos.exportable_fields:
            obj.__setattr__(field, batch.get(field))
        return obj

    def update(self):
        if self._id is None:
            return
        db = PoolDatabase()
        batch = db.get_batch(self._id, geo_fields=['done', 'todo', 'nodes'])
        for field in PolygonPhotos.exportable_fields:
            self.__setattr__(field, batch.get(field))

    def export_to_db(self):
        if self._id is None:
            self._id = ObjectId()
        db = PoolDatabase()
        data = {}
        self.pools_detected += len(self.pool_buffer)
        for field in self.exportable_fields:
            data[field] = self.__getattribute__(field)
        db.set_batch(data, geo_fields=['done', 'todo', 'nodes'])
        for pool in self.pool_buffer:
            pool.export_to_db(db)
        self.pool_buffer = []

    def fit(self, coverage=1, sleep_range=[0, 1], working_machine=None):
        self.update()
        if self.is_working:
            raise Exception('Already running')
        self.is_working = True
        self.working_machine = working_machine
        self.progress = 0
        self.osm_done = False
        self.export_to_db()

        todo = list(filter(lambda c: random.random() < coverage, self.todo))
        self.pool_buffer = []
        for index, coord in tqdm(list(enumerate(todo))):
            # update progress at database
            if index % 15 == 0:
                self.progress = index / len(todo)
                self.export_to_db()
            # random sleep
            time.sleep(random.uniform(sleep_range[0], sleep_range[1]))
            # detect pools
            pd = PoolDetector(self.ai.get_photo(coord[0], coord[1]))
            pd.get_pools()
            middle_x = self.width//2
            middle_y = self.height//2
            if pd.pixel_coords is not None:
                for pool_coord in np.floor(pd.pixel_coords):
                    x, y = _LatLongToPixelXY(coord[0],coord[1], self.zoomLevel)
                    diff_x = pool_coord[0] - middle_x
                    diff_y = pool_coord[1] - middle_y
                    lat, long = _PixelXYToLatLong(x + diff_x, y + diff_y, self.zoomLevel)
                    pool = Pool(lat, long, self._id)
                    pool.find_address(self.key)
                    self.pool_buffer.append(pool)
            self.done.append(coord)
            self.todo.remove(coord)
            pd = None
        self.progress = 1
        self.is_working = False
        self.export_to_db()
        return
