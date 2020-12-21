from DeepPoolAI import PoolPolygonsFinder, PoolDatabase
from sortedcontainers import SortedList
from bson.objectid import ObjectId
from tqdm import tqdm
pd = PoolDatabase()
db = pd.db

# remove unwanted pools from db
all_pools = list(db['pools'].find({}))
to_leave = SortedList([])
to_remove = []
for p in tqdm(all_pools):
    if p is None:
        continue
    address = (p.get('address') or {}).get('address')
    if address is None or address.get('addressLine') is None or address.get('formattedAddress') is None:
        to_remove.append(p)
        continue
    if address.get('formattedAddress') in to_leave:
        to_remove.append(p)
    else:
        to_leave.add(address.get('formattedAddress'))

batches = {}
for p in tqdm(to_remove):
    if batches.get(str(p.get('batch'))) is None:
        batches[str(p.get('batch'))] = 1
    else:
        batches[str(p.get('batch'))] += 1
    db['pools'].delete_one({ '_id': p.get('_id') })

for b in tqdm(batches.keys()):
    db['batches'].update_many({ '_id': ObjectId(b) }, { '$inc': { 'pools_detected': -1 * batches.get(b) } })

# find pools with assigned osm polygons
pools = list(db['pools'].find({ 'osm': { '$type': 'object' } }))

# get polygons ids
ids = [x for p in pools for x in p.get('osm').values()]

# export webpage data file
ppf = PoolPolygonsFinder()
ppf.save_ui_polygons(ids, 'ui-polygons.json')
