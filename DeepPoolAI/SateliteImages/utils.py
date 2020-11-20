
import math
import numpy as np

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
    yInter = math.ceil(abs(py1 - py2) / height) + 1

    px1, _ = _LatLongToPixelXY(fromLat, fromLon, zoomLevel)
    px2, _ = _LatLongToPixelXY(fromLat, toLon, zoomLevel)

    xInter = math.ceil(abs(px1 - px2) / width) + 1

    pxStart = min(px1, px2)
    pyStart = min(py1, py2)

    cov = np.zeros((xInter, yInter, 2))
    for i in range(yInter):
        for j in range(xInter):
            # not yet download photo, but rather return matrix
            # add margin for watermark
            lat_i, lon_i = _PixelXYToLatLong(pxStart + j * width, pyStart + i * height, zoomLevel)
            cov[j, i] = [lat_i, lon_i]

    return cov

EarthRadius = 6378137
MinLatitude = -85.05112878
MaxLatitude = 85.05112878
MinLongitude = -180
MaxLongitude = 180


def _Clip(n, minValue, maxValue):
    """
     Clips a number to the specified minimum and maximum values.
    """
    return min(max(n, minValue), maxValue)


def _MapSize(levelOfDetail):
    """
    Determines the map width and height (in pixels) at a specified level
    of detail.

    "levelOfDetail" - Level of detail, from 1 (lowest detail) to 23 (highest detail).
    The map width and height in pixels.

    """
    return 256 << levelOfDetail



def _GroundResolution(latitude, levelOfDetail):
    """
    Determines the ground resolution (in meters per pixel) at a specified
    latitude and level of detail.

     "latitude" - Latitude (in degrees) at which to measure the
    ground resolution.
     "levelOfDetail" - Level of detail, from 1 (lowest detail)
    to 23 (highest detail).
     The ground resolution, in meters per pixel.
    """

    latitude = _Clip(latitude, MinLatitude, MaxLatitude)
    return math.cos(latitude * math.pi / 180) * 2 * math.pi * EarthRadius / _MapSize(levelOfDetail)



def _MapScale(latitude, levelOfDetail, screenDpi):
    """
    Determines the map scale at a specified latitude, level of detail,
    and screen resolution.

     "latitude" - Latitude (in degrees) at which to measure the
    map scale.
     "levelOfDetail" - Level of detail, from 1 (lowest detail)
    to 23 (highest detail).
     "screenDpi" - Resolution of the screen, in dots per inch.
     The map scale, expressed as the denominator N of the ratio 1 : N.

    """
    return _GroundResolution(latitude, levelOfDetail) * screenDpi / 0.0254


def _LatLongToPixelXY(latitude, longitude, levelOfDetail):
    """
    Converts a point from latitude/longitude WGS-84 coordinates (in degrees)
    into pixel XY coordinates at a specified level of detail.

     "latitude" - Latitude of the point, in degrees.
     "longitude" - Longitude of the point, in degrees.
     "levelOfDetail" - Level of detail, from 1 (lowest detail)
    to 23 (highest detail).
     "pixelX" - Output parameter receiving the X coordinate in pixels.
     "pixelY" - Output parameter receiving the Y coordinate in pixels.

    """

    latitude = _Clip(latitude, MinLatitude, MaxLatitude)
    longitude = _Clip(longitude, MinLongitude, MaxLongitude)

    x = (longitude + 180) / 360
    sinLatitude = math.sin(latitude * math.pi / 180)
    y = 0.5 - math.log((1 + sinLatitude) / (1 - sinLatitude)) / (4 * math.pi)
    MapSize = _MapSize(levelOfDetail)

    pixelX = int(_Clip(x * MapSize + 0.5, 0, MapSize - 1))
    pixelY = int(_Clip(y * MapSize + 0.5, 0, MapSize - 1))

    return pixelX, pixelY


def _PixelXYToLatLong(pixelX, pixelY, levelOfDetail):
    """
    Converts a pixel from pixel XY coordinates at a specified level of detail
    into latitude/longitude WGS-84 coordinates (in degrees).

     "pixelX" - X coordinate of the point, in pixels.
     "pixelY" - Y coordinates of the point, in pixels.
     "levelOfDetail" - Level of detail, from 1 (lowest detail)
    to 23 (highest detail).
     "latitude" - Output parameter receiving the latitude in degrees.
     "longitude" - Output parameter receiving the longitude in degrees.

    """

    MapSize = _MapSize(levelOfDetail)
    x = (_Clip(pixelX, 0, MapSize - 1) / MapSize) - 0.5
    y = 0.5 - (_Clip(pixelY, 0, MapSize - 1) / MapSize)

    latitude = 90 - 360 * math.atan(math.exp(-y * 2 * math.pi)) / math.pi
    longitude = 360 * x

    return latitude, longitude


def _PixelXYToTileXY(pixelX, pixelY):
    """
    Converts pixel XY coordinates into tile XY coordinates of the tile containing
    the specified pixel.

     "pixelX" - Pixel X coordinate.
     "pixelY" - Pixel Y coordinate.
     "tileX" - Output parameter receiving the tile X coordinate.
     "tileY" - Output parameter receiving the tile Y coordinate.

    """

    tileX = pixelX / 256
    tileY = pixelY / 256

    return tileX, tileY


def _TileXYToPixelXY(tileX, tileY):
    """
    Converts tile XY coordinates into pixel XY coordinates of the upper-left pixel
    of the specified tile.

     "tileX" - Tile X coordinate.
     "tileY" - Tile Y coordinate.
     "pixelX" - Output parameter receiving the pixel X coordinate.
     "pixelY" - Output parameter receiving the pixel Y coordinate.

    """

    pixelX = tileX * 256
    pixelY = tileY * 256

    return pixelX, pixelY