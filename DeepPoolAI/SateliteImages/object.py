import json
from urllib.request import urlopen

from PIL import Image

import math
import numpy as np

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

def coverTerrain(fromLat, toLat, fromLon, toLon, zoomLevel, height, width):
        """
    Cover area by given Lon, Lat boundaries
    by calculating Lat and Lon of every photo
    present in given area

    Uses zoom level, width, height for one photo.


    Parameters
    ----------
    fromLat : double
        latitude
    fromLong : double
        longitude
    toLat : double
        latitude
    toLong : double
        longitude

    zoomLevel : integer
        integer between [1,21], amount of zoom in the picture
    height : integer
        height of single aerial map in pixels.
    width : integer
        width of single aerial map in pixels


    Returns
    -------
    Matrix with 
    """

    _, py1 = _LatLongToPixelXY(fromLat, fromLon, zoomLevel)
    _, py2 = _LatLongToPixelXY(toLat, fromLon, zoomLevel)
    yInter = math.ceil(abs(py1-py2)/height) + 1

    px1, _ = _LatLongToPixelXY(fromLat, fromLon, zoomLevel)
    px2, _ = _LatLongToPixelXY(fromLat, toLon, zoomLevel)

    xInter = math.ceil(abs(px1-px2)/width) + 1

    pxStart = min(px1, px2)
    pyStart = min(py1, py2)

    cov = np.zeros((xInter, yInter, 2))
    print(cov)
    for i in range(yInter):
        for j in range(xInter):
            # not yet download photo, but rather return matrix
            # add margin for watermark
            lat_i, lon_i = _PixelXYToLatLong(pxStart + j*width, pyStart + i*height - 16, zoomLevel)
            cov[j,i] = [lat_i, lon_i]

    return cov


EarthRadius = 6378137
MinLatitude = -85.05112878
MaxLatitude = 85.05112878
MinLongitude = -180
MaxLongitude = 180
  
#
# Clips a number to the specified minimum and maximum values.
def _Clip(n, minValue, maxValue):
    return min(max(n, minValue), maxValue)  

#
#Determines the map width and height (in pixels) at a specified level  
#of detail.  
#
#"levelOfDetail" - Level of detail, from 1 (lowest detail) to 23 (highest detail).    
#The map width and height in pixels.
def _MapSize(levelOfDetail):
    return 256 << levelOfDetail    


  
# Determines the ground resolution (in meters per pixel) at a specified  
# latitude and level of detail.  
#    
#  "latitude" - Latitude (in degrees) at which to measure the  
# ground resolution.    
#  "levelOfDetail" - Level of detail, from 1 (lowest detail)  
# to 23 (highest detail).    
#  The ground resolution, in meters per pixel.  

def _GroundResolution(latitude, levelOfDetail):
    latitude = _Clip(latitude, MinLatitude, MaxLatitude)    
    return math.cos(latitude * math.pi / 180) * 2 * math.pi * EarthRadius / _MapSize(levelOfDetail)
  
    

#    
# Determines the map scale at a specified latitude, level of detail,  
# and screen resolution.  
#    
#  "latitude" - Latitude (in degrees) at which to measure the  
# map scale.    
#  "levelOfDetail" - Level of detail, from 1 (lowest detail)  
# to 23 (highest detail).    
#  "screenDpi" - Resolution of the screen, in dots per inch.    
#  The map scale, expressed as the denominator N of the ratio 1 : N.  
def _MapScale(latitude, levelOfDetail, screenDpi):
    return _GroundResolution(latitude, levelOfDetail) * screenDpi / 0.0254  
  
    
    
    
#    
# Converts a point from latitude/longitude WGS-84 coordinates (in degrees)  
# into pixel XY coordinates at a specified level of detail.  
#    
#  "latitude" - Latitude of the point, in degrees.    
#  "longitude" - Longitude of the point, in degrees.    
#  "levelOfDetail" - Level of detail, from 1 (lowest detail)  
# to 23 (highest detail).    
#  "pixelX" - Output parameter receiving the X coordinate in pixels.    
#  "pixelY" - Output parameter receiving the Y coordinate in pixels.    
def _LatLongToPixelXY(latitude, longitude, levelOfDetail):

    latitude = _Clip(latitude, MinLatitude, MaxLatitude) 
    longitude = _Clip(longitude, MinLongitude, MaxLongitude)

    x = (longitude + 180) / 360
    sinLatitude = math.sin(latitude * math.pi / 180)
    y = 0.5 - math.log((1 + sinLatitude) / (1 - sinLatitude)) / (4 * math.pi)
    MapSize = _MapSize(levelOfDetail)

    pixelX = int(_Clip(x * MapSize + 0.5, 0, MapSize - 1))
    pixelY = int(_Clip(y * MapSize + 0.5, 0, MapSize - 1))
    
    return pixelX, pixelY

  
#    
# Converts a pixel from pixel XY coordinates at a specified level of detail  
# into latitude/longitude WGS-84 coordinates (in degrees).  
#    
#  "pixelX" - X coordinate of the point, in pixels.    
#  "pixelY" - Y coordinates of the point, in pixels.    
#  "levelOfDetail" - Level of detail, from 1 (lowest detail)  
# to 23 (highest detail).    
#  "latitude" - Output parameter receiving the latitude in degrees.    
#  "longitude" - Output parameter receiving the longitude in degrees.    
def _PixelXYToLatLong(pixelX, pixelY, levelOfDetail):
    MapSize = _MapSize(levelOfDetail)    
    x = (_Clip(pixelX, 0, MapSize - 1) / MapSize) - 0.5    
    y = 0.5 - (_Clip(pixelY, 0, MapSize - 1) / MapSize)    

    latitude = 90 - 360 * math.atan(math.exp(-y * 2 * math.pi)) / math.pi    
    longitude = 360 * x    
 
    return latitude, longitude
  
    
#    
# Converts pixel XY coordinates into tile XY coordinates of the tile containing  
# the specified pixel.  
#    
#  "pixelX" - Pixel X coordinate.    
#  "pixelY" - Pixel Y coordinate.    
#  "tileX" - Output parameter receiving the tile X coordinate.    
#  "tileY" - Output parameter receiving the tile Y coordinate.    
def _PixelXYToTileXY(pixelX, pixelY): 
    tileX = pixelX / 256    
    tileY = pixelY / 256    
    
    return tileX, tileY

  
#    
# Converts tile XY coordinates into pixel XY coordinates of the upper-left pixel  
# of the specified tile.  
#    
#  "tileX" - Tile X coordinate.    
#  "tileY" - Tile Y coordinate.    
#  "pixelX" - Output parameter receiving the pixel X coordinate.    
#  "pixelY" - Output parameter receiving the pixel Y coordinate.    
def _TileXYToPixelXY(tileX, tileY):
    pixelX = tileX * 256    
    pixelY = tileY * 256    

    return pixelX, pixelY
  