import Vue from 'vue'
import Vuex from 'vuex'
// import pools from '@/assets/pools.json'
import polygons from '@/assets/polygons.json'
Vue.use(Vuex)

const state = {
  pools: [],
  polygons,
  mapboxAuth: 'pk.eyJ1IjoicGlvdHJwaWF0eXN6ZWsiLCJhIjoiY2tpZG5uYjVhMHRsejJ5bzVhazIxeGl3YSJ9.Q8ak3Y5QYlif8U85VBPVwA',
  cart: []
}

const getters = {
  pools (state) {
    return state.pools
  },
  polygons (state) {
    return state.polygons.map(p => ({ ...p, price: Math.round((p.pools * 0.02) * 100) / 100 }))
  },
  mapboxAuth (state) {
    return state.mapboxAuth
  },
  cart (state) {
    return state.cart
  }
}

const mutations = {
  addToCart (state, id) {
    Vue.set(state, 'cart', [...state.cart.filter(c => c !== id), id])
  },
  delFromCart (state, id) {
    Vue.set(state, 'cart', state.cart.filter(c => c !== id))
  }
}

const actions = {
}

export default new Vuex.Store({
  state, mutations, actions, getters
})
