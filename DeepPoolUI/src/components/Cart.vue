<template>
  <div class="cart">
    <span class="icon" @click="open = !open">&#x1f6d2;
      <span v-if="ids.length > 0" class="count-icon">{{ ids.length }}</span>
    </span>
    <div class="list" v-if="open">
      <div v-for="poly in polygons" :key="poly.id" class="element">
        <span class="rm" @click="$store.commit('delFromCart', poly.id)">&#x274C;</span>
        <span class="name">{{ poly.name }}</span>
        <span class="price">{{ poly.price + '$' }}</span>
      </div>
      <router-link to="/checkout" class="element checkout">
        <span class="name">Checkout</span>
        <span class="price">{{ sum + '$' }}</span>
      </router-link>
    </div>
  </div>
</template>
<script>
export default {
  name: 'Cart',
  data () {
    return {
      open: false
    }
  },
  computed: {
    ids () {
      return this.$store.getters.cart
    },
    sum () {
      return Math.round(100 * this.polygons.map(p => p.price).reduce((agg, p) => agg + p, 0)) / 100
    },
    polygons () {
      return this.$store.getters.polygons.filter(p => this.ids.includes(p.id))
    }
  },
  methods: {},
  components: {}
}
</script>
<style>
.cart {
  position: absolute;
  right: 0;
  top: 0;
  user-select: none;
}
.cart > .icon {
  position: relative;
  top: 30px;
  right: 40px;
  font-size: 35px;
  display: block;
  width: 60px;
  height: 60px;
  text-align: center;
  line-height: 60px;
  cursor: pointer;
  background: white;
  border-radius: 50%;
  box-shadow: 0 0 9px 0px rgba(255, 255, 255, 0.6);
}
.cart > .icon > .count-icon {
  position: absolute;
  display: block;
  color: white;
  right: -10px;
  bottom: -10px;
  width: 20px;
  height: 20px;
  text-align: center;
  padding: 5px;
  font-size: 16px;
  background: #f63737;
  border-radius: 50%;
  line-height: 20px;
  font-weight: bold;
}
.cart > .list {
  position: absolute;
  top: 120px;
  right: 40px;
  padding: 20px 10px;
  min-width: 150px;
  background: white;
  box-shadow: 0 0 9px 9 rgba(255, 255, 255, 0.6);
}
.cart > .list > .element {
  position: relative;
  padding: 10px 30px;
  padding-right: 50px;
  display: block;
  text-decoration: none;
}
.cart > .list > .element:hover {
  background: #eee;
}
.cart > .list > .element > .rm {
  position: absolute;
  left: 5px;
  cursor: pointer;
}
.cart > .list > .element > .name {
  white-space: nowrap;
}
.cart > .list > .element > .price {
  position: absolute;
  right: 5px;
  color: #555;
}
.cart > .list > .checkout {
  border-top: 1px solid #ccc;
  cursor: pointer;
  margin-top: 10px;
  color: #4378bf;
}
</style>
