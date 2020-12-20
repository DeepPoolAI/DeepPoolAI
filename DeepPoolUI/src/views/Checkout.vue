<template>
  <div class="checkout">
    <div class="overlay"></div>
    <div class="container">
      <span class="title">Checkout</span>
      <div class="main">
        <span v-if="cart.length === 0">You need to add items to cart first.</span>
        <button v-else-if="payment === 0" class="payment center" @click="payment=1">Go to payment</button>
        <span v-if="payment === 1">Waiting for transaction completion</span>
        <span v-if="payment === 2 && progress < 1">Downloading</span>
        <Loading v-if="payment > 0 && progress < 1"  :progress="payment === 1 ? undefined : progress" class="center"/>
        <div class="download" v-if="payment === 2 && progress === 1">
          <span>Select format</span>
          <div class="formats">
            <div class="format-option" v-for="f in formats" :key="f">
              <input type="radio" name="format" :value="f" :id="'v' + f" v-model="format">
              <label :for="'v' + f">{{ f }}</label>
            </div>
          </div>
          <span>Download all addresses</span>
          <div class="row first">
            <button @click="save(null, 'all')">All pools</button>
            <button @click="save(null, 'clean')">Clean pools</button>
            <button @click="save(null, 'dirty')">Dirty pools</button>
          </div>
          <span>Download addresses from selected regions</span>
          <div class="row" v-for="d in download" :key="d.id">
            <span class="label">{{ d.name }}</span>
            <button @click="save(d.id, 'all')">All pools</button>
            <button @click="save(d.id, 'clean')">Clean pools</button>
            <button @click="save(d.id, 'dirty')">Dirty pools</button>
          </div>
        </div>
      </div>
      <div class="buttons">
        <router-link to="/">
          <button>Go Back</button>
        </router-link>
      </div>
    </div>
  </div>
</template>
<script>
import Loading from '@/components/Loading.vue'
import { saveAs } from 'file-saver'

export default {
  name: 'Checkout',
  data () {
    return {
      payment: 0,
      download: [],
      format: 'TXT',
      formats: ['TXT', 'JSON']
    }
  },
  watch: {
    payment () {
      if (this.payment === 1) {
        window.setTimeout(() => {
          this.payment = 2
        }, 4000)
      } else if (this.payment === 2) {
        this.polygons.forEach(p => {
          this.$http.get('/api/polygon/' + p.id).then(response => {
            this.download.push({ id: p.id, name: p.name, pools: response.body })
          }).catch(console.error)
        })
      }
    }
  },
  computed: {
    cart () {
      return this.$store.getters.cart
    },
    progress () {
      return (this.download.length / this.cart.length)
    },
    polygons () {
      return this.$store.getters.polygons.filter(p => this.cart.includes(p.id))
    }
  },
  methods: {
    save (region, type) {
      let pools = region === null ? this.download.reduce((acu, x) => ([...acu, ...x.pools]), []) : this.download.find(d => d.id === region).pools
      const name = region === null ? 'pools' : (this.download.find(d => d.id === region).name + '-pools')
      if (type === 'clean') pools = pools.filter(p => p.clean === undefined || p.clean === null || p.clean === true)
      else if (type === 'dirty') pools = pools.filter(p => p.clean === false)
      const addresses = pools.map(p => p.address).filter(x => x)
      if (this.format === 'JSON') {
        const json = JSON.stringify(addresses, null, 2)
        saveAs(new Blob([json], { type: 'application/json', name: name + '.json' }), name + '.json')
      } else if (this.format === 'TXT') {
        const txt = addresses.map(a => a.formattedAddress + ', ' + a.countryRegion).join('\r\n')
        saveAs(new Blob([txt], { type: 'text/plain', name: name + '.txt' }), name + '.txt')
      }
    }
  },
  components: { Loading }
}
</script>
<style>
.checkout .overlay {
  position: fixed;
  width: 100%;
  height: 100%;
}
.checkout > .container {
  width: 600px;
  background: white;
  z-index: 10;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  border-radius: 10px;
}
.checkout > .container > .title {
  padding: 20px;
  display: block;
  font-size: 26px;
  color: #555;
}
.checkout > .container > .main {
  border-top: 1px solid #ccc;
  border-bottom: 1px solid #ccc;
  padding: 0px 20px;
  max-height: 400px;
  overflow-y: auto;
}
.checkout > .container > .main > *:last-child {
  margin-bottom: 60px;
}
.checkout > .container > .main > *:first-child {
  margin-top: 60px;
}
.checkout > .container > .main > span {
  display: block;
  text-align: center;
  padding: 20px 0;
  font-size: 20px;
}
.checkout > .container > .main button.payment {
  padding: 15px 20px;
}
.checkout > .container > .main > .center {
  position: relative;
  left: 50%;
  transform: translateX(-50%);
}
.checkout > .container > .buttons {
  padding: 20px;
}
.checkout > .container > .buttons > a {
  cursor: pointer;
}
.checkout button {
  padding: 8px 12px;
  color: white;
  background: #4378bf;
  border: none;
  box-shadow: 0 0 5px 0 #4378bf80;
  cursor: pointer;
  font-weight: 600;
}
.checkout button:hover {
  box-shadow: 0 0 5px 0 #4378bf;
}
.checkout > .container > .main > .download {
  margin-top: 30px;
  margin-bottom: 30px;
}
.checkout > .container > .main > .download > span {
  display: block;
  text-align: center;
  padding: 10px 0;
  font-size: 18px;
}
.checkout > .container > .main > .download > .row {
  position: relative;
}
.checkout > .container > .main > .download > .row > button {
  margin: 10px;
  position: relative;
  left: 200px;
}
.checkout > .container > .main > .download > .row.first > button {
  left: 0;
}
.checkout > .container > .main > .download > .row.first {
  display: inline-block;
  left: 50%;
  transform: translateX(-50%);
}
.checkout > .container > .main > .download > .row > .label {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  max-width: 200px;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.checkout > .container > .main > .download > .formats {
  position: relative;
  left: 50%;
  transform: translateX(-50%);
  display: inline-block;
}
.checkout > .container > .main > .download > .formats > div {
  margin: 0 20px;
  display: inline-block;
}
</style>
