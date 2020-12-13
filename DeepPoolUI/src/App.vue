<template>
  <div id="app">
    <!--
    <div id="nav">
      <router-link to="/">Map</router-link>
    </div>
    -->
    <router-view/>
  </div>
</template>
<script>
export default {
  name: 'App',
  mounted () {
    this.$store.dispatch('init')
  }
}
</script>
<style>
body {
  margin: 0;
  padding: 0;
}
</style>
