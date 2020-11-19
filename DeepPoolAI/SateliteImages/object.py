import json
from urllib.request import urlopen

from PIL import Image


class SquareAerialImage:

    def __init__(self, key, zoomLevel):
        """Square Aerial Image
        Wrapper for Bing api

        Parameters
        ----------
        key : string
            Bing Api key
        zoomlevel : integer
            integer between [1,21], amount of zoom in the picture

        Returns
        -------
        AerialImage object that stores information about key, zoom height and width of an image
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
            longtitude

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
      long: double
          longitude
      lat : double
          latitude
      zoomlevel : integer
          integer between [1,21], amount of zoom in the picture
      height : integer
          height of an aerial map in pixels. Does not work with square

      width : integer
          width of an aerial map in pixels

      Returns
      -------
      AerialImage object that stores information about key, zoom height and width of an image
    """



    def __init__(self,key, zoomLevel, width = 1080, height = 720):

        super().__init__(key, zoomLevel)
        self.height = height
        self.width = width

    def get_photo(self, lat, long):
        """ Get Photo
        Gets square 256x256 photo of area given the long and lat.
        Uses zoom level and key from the object.

        Parameters
        ----------
        lat : double
            latitude
        long : double
            longtitude


        Returns
        -------
        Square photo without label on lower bound

        """

        request = f"https://dev.virtualearth.net/REST/v1/Imagery/Map/Aerial/{lat},{long}/{self.zoomLevel}?" \
                  f"mapSize={self.width},{self.height}&key={self.key}"

        image = Image.open(urlopen(request))

        return image

