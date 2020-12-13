import Vue from 'vue'
import Vuex from 'vuex'
// import pools from '@/assets/pools.json'
import polygons from '@/assets/polygons.json'
Vue.use(Vuex)

const searchParams = new URLSearchParams(window.location.search)

const state = {
  pools: [],
  polygons,
  mapboxAuth: 'pk.eyJ1IjoicGlvdHJwaWF0eXN6ZWsiLCJhIjoiY2tpZG5uYjVhMHRsejJ5bzVhazIxeGl3YSJ9.Q8ak3Y5QYlif8U85VBPVwA',
  cart: [],
  server: searchParams.get('server'),
  batches: []
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
  },
  server (state) {
    if (!state.server) return null
    return state.server.replace(/\/$/, '') + '/'
  },
  batches (state) {
    return state.batches
  }
}

const mutations = {
  addToCart (state, id) {
    Vue.set(state, 'cart', [...state.cart.filter(c => c !== id), id])
  },
  delFromCart (state, id) {
    Vue.set(state, 'cart', state.cart.filter(c => c !== id))
  },
  setBatches (state, batches) {
    Vue.set(state, 'batches', batches)
  }
}

const actions = {
  update ({ getters, commit }) {
    if (getters.server) {
      Vue.http.get(getters.server + 'batches').then(response => {
        commit('setBatches', response.body)
      }).catch(e => {
        commit('setBatches', [])
      })
    }
  },
  init ({ dispatch }) {
    setInterval(() => {
      dispatch('update')
    }, 5000)
    dispatch('update')
  },
  addBatch ({ getters }, batch) {
    if (!getters.server) {
      return
    }
    Vue.http.post(getters.server + 'batches', batch)
  },
  runBatch ({ getters }, { batchId, options }) {
    if (!getters.server) {
      return
    }
    Vue.http.post(getters.server + 'batches/' + batchId + '/run', options)
  },
  batchRunOsm ({ getters }, batchId) {
    if (!getters.server) {
      return
    }
    Vue.http.post(getters.server + 'batches/' + batchId + '/osm')
  }
}

export default new Vuex.Store({
  state, mutations, actions, getters
})
