<template>
  <div class="map" ref="outer">
    <div class="map-inner" ref="map"></div>
  </div>
</template>
<script>
import mapboxgl from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'

export default {
  name: 'Map',
  data () {
    return {
      level: 6
    }
  },
  watch: {
    level () {
      this.displayPolygons()
    }
  },
  computed: {
    poolsMarkers () {
      return this.$store.getters.pools.map(p => new mapboxgl.Marker().setLngLat([p[1], p[0]]))
    },
    polygons () {
      return this.$store.getters.polygons
    },
    polygonsGeoJSON () {
      return this.$store.getters.polygons.map(p => {
        return {
          name: p.name,
          id: p.id + '',
          price: p.price,
          pools: p.pools,
          geojson: {
            type: 'geojson',
            data: {
              type: 'FeatureCollection',
              features: p.nodes.map(part => {
                return {
                  type: 'Feature',
                  geometry: {
                    type: 'Polygon',
                    coordinates: [
                      part.map(p => ([p[1], p[0]]))
                    ]
                  }
                }
              })
            }
          }
        }
      })
    },
    poolsRangeForLevel () {
      return this.polygons.reduce((agg, p) => {
        if (!agg[p.level]) {
          agg[p.level] = [p.pools, p.pools]
        }
        agg[p.level][0] = Math.min(agg[p.level][0], p.pools)
        agg[p.level][1] = Math.max(agg[p.level][1], p.pools)
        return agg
      }, {})
    }
  },
  methods: {
    getPoygonOpacity (p) {
      const range = this.poolsRangeForLevel[p.level]
      const logRange = [Math.log(range[0]), Math.log(range[1])]
      const logV = Math.log(p.pools)
      const normalised = (logV - logRange[0]) / (logRange[1] - logRange[0])
      const outputRange = [0.2, 0.7]
      return outputRange[0] + (normalised * (outputRange[1] - outputRange[0]))
    },
    loadPools () {
      this.poolsMarkers.forEach(m => m.addTo(this.map))
    },
    loadPolygonsSources () {
      this.polygonsGeoJSON.forEach(p => {
        this.map.addSource(p.id + '', p.geojson)
        this.map.on('click', p.id + '', e => {
          new mapboxgl.Popup()
            .setLngLat(e.lngLat)
            .setHTML('<b>' + p.name + '</b><p>Pools: ' + p.pools + '<br>' + 'Price: ' + p.price + '$</p>' + '<button onclick="add_to_cart(' + p.id + ')">Add to cart</button>')
            .addTo(this.map)
        })
      })
    },
    onMapLoad () {
      this.loadPolygonsSources()
      this.displayPolygons()
      // this.loadPools()
    },
    displayPolygons () {
      // const colors = ['#088', '#880', '#808', '#800', '#080', '#008', '#888']
      this.polygons.forEach(p => {
        if (this.map.getLayer(p.id + '')) {
          this.map.removeLayer(p.id + '')
        }
        if (this.map.getLayer(p.id + '_outline')) {
          this.map.removeLayer(p.id + '_outline')
        }
      })
      this.polygons.filter(p => p.level === this.level + '').forEach((p, index) => {
        this.map.addLayer({
          id: p.id + '',
          type: 'fill',
          source: p.id + '',
          layout: {},
          paint: {
            // 'fill-color': colors[index % colors.length],
            'fill-color': '#4dc9eb',
            'fill-opacity': this.getPoygonOpacity(p)
          }
        })
        this.map.addLayer({
          id: p.id + '_outline',
          type: 'line',
          source: p.id + '',
          layout: {},
          paint: {
            'line-color': '#007994',
            'line-width': 3
          }
        })
      })
    },
    onMapZoom () {
      const zoom = this.map.getZoom()
      if (zoom > 9) this.level = 8
      else if (zoom > 7) this.level = 6
      else this.level = 4
    }
  },
  components: {},
  mounted () {
    mapboxgl.accessToken = this.$store.getters.mapboxAuth
    this.map = new mapboxgl.Map({
      container: this.$refs.map,
      style: 'mapbox://styles/mapbox/dark-v10', // stylesheet location
      center: [-118.30438613891602, 33.984501619979994], // starting position [lng, lat]
      zoom: 9 // starting zoom
    })
    this.map.on('load', this.onMapLoad)
    this.map.on('zoom', this.onMapZoom)
    window.add_to_cart = (id) => this.$store.commit('addToCart', id)
  }
}
</script>
<style>
.map .map-inner {
  position: absolute;
  width: 100%;
  height: 100%;
}
</style>
