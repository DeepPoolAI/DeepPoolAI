<template>
  <div class="img-viewer">
    <div class="buttons">
      <button @click="addSize(1)">+</button>
      <button @click="addSize(-1)">-</button>
    </div>
    <img v-if="img" :src="img" @click.self="addPoint" ref="img">
    <div v-if="point" class="point" :style="pointStyle"></div>
    <div>{{ meanColor }}</div>
  </div>
</template>
<script>
export default {
  name: 'ImgViewer',
  props: {
    img: String
  },
  data () {
    return {
      point: null,
      radius: 6
    }
  },
  computed: {
    pointStyle () {
      if (!this.point) return null
      return {
        left: this.point[0] + 'px',
        top: this.point[1] + 'px',
        width: 2 * this.radius + 'px',
        height: 2 * this.radius + 'px'
      }
    },
    pixelCoords () {
      if (!this.point) return null
      const coords = []
      for (let x = -1 * this.radius; x <= this.radius; x++) {
        for (let y = -1 * this.radius; y <= this.radius; y++) {
          if ((x * x) + (y * y) <= this.radius * this.radius) coords.push([x + this.point[0], y + this.point[1]])
        }
      }
      return coords
    },
    colors () {
      if (!this.point) return []
      const canvas = document.createElement('canvas')
      const img = this.$refs.img
      canvas.width = img.width
      canvas.height = img.height
      const ctx = canvas.getContext('2d')
      ctx.drawImage(img, 0, 0, img.width, img.height)
      return this.pixelCoords.map(([x, y]) => {
        const d = ctx.getImageData(x, y, 1, 1).data
        return [d[0], d[1], d[2]]
      })
    },
    hsvColors () {
      if (!this.colors) return []
      return this.colors.map(c => this.rgb2hsv(c[0] / 255, c[1] / 255, c[2] / 255))
    },
    meanColor () {
      if (!this.hsvColors) return ''
      return this.hsvColors.reduce((acu, color) => {
        return acu.map((c, i) => c + (color[i] / this.colors.length))
      }, [0, 0, 0])
    }
  },
  methods: {
    addSize (v) {
      this.radius = Math.min(30, Math.max(2, this.radius + v))
    },
    addPoint (event) {
      this.point = [event.layerX, event.layerY]
    },
    // input: r,g,b in [0,1], out: h in [0,180) and s,v in [0, 255]
    rgb2hsv (r, g, b) {
      const v = Math.max(r, g, b)
      const c = v - Math.min(r, g, b)
      const h = c && ((v === r) ? (g - b) / c : ((v === g) ? 2 + (b - r) / c : 4 + (r - g) / c))
      return [30 * (h < 0 ? h + 6 : h), 255 * (v && c / v), 255 * v]
    }
  },
  components: {}
}
</script>
<style lang="sass">
.img-viewer
  position: relative
.point
  position: absolute
  transform: translate(-50%, -50%)
  border-radius: 50%
  background: #ff000050
  pointer-events: none
img
  position: relative
.buttons
  position: absolute
  z-index: 10
</style>
