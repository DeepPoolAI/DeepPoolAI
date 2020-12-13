from DeepPoolAI import PoolPolygonsFinder, PoolDatabase
pd = PoolDatabase()
db = pd.db

# find pools with assigned osm polygons
pools = list(db['pools'].find({ 'osm': { '$type': 'object' } }))

# get polygons ids
ids = [x for p in pools for x in p.get('osm').values()]

# export webpage data file
ppf = PoolPolygonsFinder()
ppf.save_ui_polygons(ids, 'ui-polygons.json')
