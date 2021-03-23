<template>
  <div id="app">
    <Map v-if="$route.name !== 'AdminPanel'"/>
    <router-view/>
  </div>
</template>
<script>
import Map from '@/components/Map.vue'
export default {
  name: 'App',
  mounted () {
    this.$store.dispatch('init')
  },
  components: {
    Map
  }
}
</script>
<style>
body {
  margin: 0;
  padding: 0;
}
</style>
