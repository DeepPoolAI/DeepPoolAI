<template>
  <div class="home">
    <Map />
    <Cart />
  </div>
</template>
<script>
import Map from '@/components/Map.vue'
import Cart from '@/components/Cart.vue'

export default {
  name: 'Home',
  components: {
    Map,
    Cart
  }
}
</script>
