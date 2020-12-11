import overpy
import time
import json
import numpy as np
from .utils import join_ways
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from tqdm import tqdm

class PoolPolygonsFinder:
    def __init__(self):
        self.osm = overpy.Overpass()

    def osm_query(self, query):
        """
        This method runs query and waits if too many requests exception is thrown.
        """
        try:
            return self.osm.query(query)
        except overpy.exception.OverpassTooManyRequests:
            time.sleep(60)
            return self.osm_query(query)

    def polygons_query(self, lat, lon, level):
        """
        This method makes QSM query to get administrative relation with specified level.

        Parameters
        ----------
        lat : list
            List with range of latitude
        lon : list
            List with range of longitude
        level : int
            Administrative level of requested polygons
        """
        return self.osm_query("""
        [out:json][timeout:120][bbox:{lat_min},{lon_min},{lat_max},{lon_max}];
        (
          rel["boundary"="administrative"]["admin_level"={level}];
          >;
        );
        out;
        """.format(lat_min=lat[0], lat_max=lat[1], lon_min=lon[0], lon_max=lon[1], level=level))

    def assign_polygons(self, pools, level=[4,6,8]):
        """
        This method assigns administrative relation's (represents polygon) id to each pool.
        Parameters
        ----------
        pools : list
            List of coordinates [lat, lng]
        level : int or list
            Administrative level of requested relations or list of such levels.

        Returns
        ----------
        List of relations' ids or list of such lists for each level
        """
        if type(level) is list:
            return [self.assign_polygons(pools, lev) for lev in tqdm(level)]
        lats = list(map(lambda p: p[0], pools))
        lons = list(map(lambda p: p[1], pools))
        points = list(map(lambda p: Point(p[0], p[1]), pools))
        lat_margin=1
        lon_margin=1
        result = self.polygons_query([min(lats) - lat_margin, max(lats) + lat_margin], [min(lons) - lon_margin, max(lons) + lon_margin], level)
        polygons = [None]*len(pools)
        for rel in result.relations:
            ways = []
            for way in [way.resolve() for way in rel.members if way.role=='outer' and isinstance(way, overpy.RelationWay)]:
                ways.append(list(map(lambda n: (float(n.lat), float(n.lon)), way.nodes)))
            nodes = join_ways(ways)
            for path in nodes:
                if len(path) < 3:
                    continue
                polygon = Polygon(path)
                for index, point in [(index, p) for (index, p) in enumerate(points) if polygon.contains(p)]:
                    polygons[index] = rel.id
        return polygons

    def save_ui_polygons(self, ids, filename):
        """
        Generates data file for UI.

        Parameters
        ----------
        ids : list or numpy.ndarray
            List or matrix of relations ids.
        filename : str
            Path to output file
        """
        if not type(ids) is np.ndarray:
            ids = np.array(ids)
        ids = ids.flatten()
        ids = ids[ids != None]
        ids_f = ','.join(map(str, np.unique(ids)))
        result = self.osm_query("""
        [out:json][timeout:120];
        (
          rel(id:{0});
          >;
        );
        out;
        """.format(ids_f))
        counts = {str(row[0]): float(row[1]) for row in np.asarray(np.unique(ids, return_counts=True)).T}
        polygons = []
        for rel in result.relations:
            ways = []
            for way in [way.resolve() for way in rel.members if way.role=='outer' and isinstance(way, overpy.RelationWay)]:
                ways.append(list(map(lambda n: (float(n.lat), float(n.lon)), way.nodes)))
            polygons.append({
                "id": rel.id,
                "nodes": join_ways(ways),
                "name": rel.tags.get('name'),
                "level": rel.tags.get('admin_level'),
                "pools": counts.get(str(rel.id))
            })
        with open(filename, 'w') as outfile:
            json.dump(polygons, outfile)
