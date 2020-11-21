import json
from urllib.request import urlopen

from PIL import Image
import matplotlib.pyplot as plt
from .utils import  coverTerrain

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
                  f"_MapSize={self.width},{self.height}&key={self.key}"

        image = Image.open(urlopen(request))

        return image

    def get_coords(self, lat1, long1, lat2, long2):
        """
        Get coords between 2 rectangle points. They can be then
        iterated and plotted.

        Return:
            np.ndarray
        """

        coords = coverTerrain(lat1, lat2, long1, long2, self.zoomLevel, 256, 256)
        return coords

    def get_grid_photos(self, lat1, long1, lat2,long2):
        """
        Returns a tuple (array_of_photos, plt)
        """

        coords = self.get_coords(lat1, long1, lat2,long2)
        if len(list(coords.shape)) != 3:
            raise Exception("You should bet a bit bigger terrain, grid should be at least 2x2 to work")
        coords_shape = coords.shape[0:2]

        f, axarr = plt.subplots(coords_shape[1],
                                coords_shape[0], squeeze=True)
        photos = []
        for i in range(coords_shape[0]):
            for j in range(coords_shape[1]):
                photo = self.get_square_photo(coords[i][j][0], coords[i][j][1])
                photos.append(photo)
                axarr[j, i].axis("off")
                axarr[j, i].imshow(photo, aspect='auto')

        plt.subplots_adjust(hspace=0, wspace=0)
        return photos, plt

class GridPhotos(AerialImage):

    def __init__(self, lat1, long1, lat2, long2, key, zoomLevel, width, height):
        super().__init__(key, zoomLevel, width, height)
        self.photos = None
        self.key = key
        self.lat1 = lat1
        self.long1 = long1
        self.lat2 = lat2
        self.long2 = long2

    def get_grid(self):
        """
               Saves all grid photos within object array.
               Prints whole grid.
        """
        arr, plt = self.get_grid_photos(self.lat1, self.long1, self.lat2, self.long2)
        self.photos = arr
        return

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



