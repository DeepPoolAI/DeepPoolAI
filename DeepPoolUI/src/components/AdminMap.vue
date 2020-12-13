<template>
  <div class="admin-map" ref="outer">
    <div class="map-inner" ref="map"></div>
    <div class="buttons" v-if="loaded && enableAdd">
      <div v-if="!modeDraw" class="draw" @click="modeDraw=true">&#10133;</div>
      <div v-if="modeDraw" @click="modeDraw=false" class="close">&#x274C;</div>
      <div v-if="selection && modeDraw" @click="saveDraw" class="save">&#10003;</div>
    </div>
  </div>
</template>
<script>
import mapboxgl from 'mapbox-gl'
import MapboxDraw from 'mapbox-gl-draw'
import 'mapbox-gl/dist/mapbox-gl.css'
import 'mapbox-gl-draw/dist/mapbox-gl-draw.css'

export default {
  name: 'AdminMap',
  props: {
    enableAdd: Boolean,
    center: Object
  },
  data () {
    return {
      modeDraw: false,
      draw: null,
      map: null,
      selection: null,
      loaded: false,
      lastPolygons: []
    }
  },
  watch: {
    center (newValue, oldValue) {
      if (!newValue || !this.loaded) return
      this.map.setCenter(this.center)
      this.$emit('centered')
    },
    modeDraw () {
      if (this.modeDraw) {
        this.draw.changeMode('draw_polygon')
      } else {
        this.draw.changeMode('static')
        this.draw.deleteAll()
      }
    },
    polygonsGeoJSON () {
      if (this.loaded) {
        this.loadPolygonsSources()
        this.displayPolygons()
      }
    }
  },
  computed: {
    batches () {
      return this.$store.getters.batches
    },
    polygonsGeoJSON () {
      return this.batches.map(p => {
        return {
          name: p.name || '',
          id: p.batch_id,
          geojson: {
            type: 'geojson',
            data: {
              type: 'Feature',
              geometry: {
                type: 'Polygon',
                coordinates: [p.nodes.map(x => ([x[1], x[0]]))]
              }
            }
          }
        }
      })
    }
  },
  methods: {
    loadPolygonsSources () {
      this.polygonsGeoJSON.filter(p => !this.map.getSource(p.id)).forEach(p => {
        this.map.addSource(p.id, p.geojson)
        this.map.on('click', p.id, e => {
          this.$emit('open', p.id)
        })
      })
    },
    displayPolygons () {
      this.lastPolygons.filter(id => !this.polygonsGeoJSON.find(g => g.id === id)).forEach(id => {
        if (this.map.getLayer(id)) {
          this.map.removeLayer(id)
        }
        if (this.map.getLayer(id + '_outline')) {
          this.map.removeLayer(id + '_outline')
        }
      })
      this.polygonsGeoJSON.filter(g => !this.lastPolygons.includes(g.id)).forEach((p, index) => {
        this.map.addLayer({
          id: p.id,
          type: 'fill',
          source: p.id,
          layout: {},
          paint: {
            'fill-color': '#4dc9eb',
            'fill-opacity': 0.6
          }
        })
        this.map.addLayer({
          id: p.id + '_outline',
          type: 'line',
          source: p.id,
          layout: {},
          paint: {
            'line-color': '#007994',
            'line-width': 3
          }
        })
      })
      this.lastPolygons = this.polygonsGeoJSON.map(p => p.id)
    },
    saveDraw () {
      this.$emit('selection', this.selection)
      this.modeDraw = false
    },
    updateSelection () {
      const result = this.draw.getAll()
      try {
        this.selection = result.features[0].geometry.coordinates[0].map(p => ([p[1], p[0]]))
      } catch (e) {
        this.selection = null
      }
    },
    onMapLoad () {
      this.loaded = true
      this.draw = new MapboxDraw({
        displayControlsDefault: false,
        controls: {}
      })
      this.map.addControl(this.draw)
      this.map.on('draw.create', this.updateSelection)
      this.map.on('draw.update', this.updateSelection)
      this.loadPolygonsSources()
      this.displayPolygons()
    }
  },
  mounted () {
    mapboxgl.accessToken = this.$store.getters.mapboxAuth
    this.map = new mapboxgl.Map({
      container: this.$refs.map,
      style: 'mapbox://styles/mapbox/dark-v10', // stylesheet location
      center: [-118.30438613891602, 33.984501619979994], // starting position [lng, lat]
      zoom: 7 // starting zoom
    })
    this.map.on('load', this.onMapLoad)
  }
}
</script>
<style>
.admin-map .map-inner {
  position: absolute;
  width: 100%;
  height: 100%;
}
.admin-map > .buttons {
  position: absolute;
  bottom: 20px;
  left: 20px;
  font-size: 30px;
  line-height: 50px;
  text-align: center;
  color: #555;
  user-select: none;
}
.admin-map > .buttons > div {
  display: inline-block;
  width: 50px;
  height: 50px;
  background: white;
  box-shadow: 0 0 9px 0 rgba(255, 255, 255, 0.6);
  cursor: pointer;
  border-radius: 50%;
  margin: 20px;
}
.admin-map > .buttons > div:hover {
  box-shadow: 0 0 15px 3px rgba(255, 255, 255, 0.8);
}
.admin-map > .buttons > div.save {
  color: green;
}
.admin-map > .buttons > div.close {
  color: #f63737;
  font-size: 20px;
}
</style>
