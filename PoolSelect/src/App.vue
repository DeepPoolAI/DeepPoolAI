<template>
  <div id="app">
    <button @click="$refs.fileinput.click()">📂</button>
    <input type="file" style="display: none" ref="fileinput" @change="loadFiles">
    <ImgViewer :img="img" />
  </div>
</template>
<script>
import ImgViewer from '@/components/ImgViewer.vue'

export default {
  name: 'App',
  components: { ImgViewer },
  data () {
    return {
      img: null
    }
  },
  methods: {
    loadFiles (event) {
      for (var file of event.target.files) this.loadFile(file)
    },
    loadFile (file) {
      var reader = new FileReader()
      reader.onload = e => {
        this.img = e.target.result
      }
      reader.readAsDataURL(file)
    }
  }
}
</script>

<style lang="scss">
</style>
