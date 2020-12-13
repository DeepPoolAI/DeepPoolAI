<template>
  <div class="batch">
    <span class="close" @click="$emit('close')">&#x274C;</span>
    <span class="title">{{ batch.name }}</span>
    <span class="prop"><b>Image width:</b> {{ batch.width }}</span>
    <span class="prop"><b>Image height:</b> {{ batch.height }}</span>
    <span class="prop"><b>Zoom level:</b> {{ batch.zoomLevel }}</span>
    <span class="prop"><b>Scanned images:</b> {{ batch.done }}</span>
    <span class="prop"><b>Not scanned images:</b> {{ batch.todo }}</span>
    <span class="prop"><b>OSM Polygons assigned:</b> {{ batch.osm_done }}</span>
    <span class="prop"><b>Pools detected:</b> {{ batch.pools_detected }}</span>
    <hr>
    <span class="title">Scanning</span>
    <form @submit.prevent="save" v-if="!batch.is_working && batch.todo > 0">
      <div v-for="inp in formInputs" :key="inp.name" class="row" :class="{ error: inp.errors }">
        <label :for="inp.name">{{ inp.label }}</label>
        <input v-if="inp.type === 'text'" type='text' :name="inp.name" @change="updateValue(inp.name, $event.target.value)" :value="values[inp.name]"/>
        <input v-if="inp.type === 'number'" type='number' :name="inp.name" @change="updateValue(inp.name, $event.target.valueAsNumber)" :value="values[inp.name]" :step="inp.step"/>
        <span class="error" v-for="e in inp.errors" :key="e">{{ e }}</span>
      </div>
      <button class="green button">Run task</button>
    </form>
    <Loading v-else-if="batch.is_working" :progress="batch.progress" />
    <button v-if="!batch.is_working && !batch.osm_done" class="button" @click="doOsm">Assign OSM polygons</button>
    <button v-if="!batch.is_working" class="red button" @click="delBatch">Delete batch</button>
  </div>
</template>
<script>
import form from '@/lib/BatchForm.js'
import validate from 'validate.js'
import Loading from '@/components/Loading.vue'

export default {
  name: 'Batch',
  data () {
    return {
      values: form.reduce((agg, f) => ({ ...agg, [f.name]: f.default }), {}),
      errors: {}
    }
  },
  props: {
    batch: Object
  },
  computed: {
    formInputs () {
      return form.map(f => ({ label: f.fullName || f.name, name: f.name, errors: this.errors[f.name], type: f.type, step: f.step }))
    },
    constraintsSimple () {
      return form.reduce((agg, f) => ({ ...agg, [f.name]: { ...f.constraints, presence: false } }), {})
    },
    constraintsFull () {
      return form.reduce((agg, f) => ({ ...agg, [f.name]: { ...f.constraints, presence: true } }), {})
    }
  },
  methods: {
    validate (full = false) {
      const con = full ? this.constraintsFull : this.constraintsSimple
      this.errors = validate(this.values, con) || {}
    },
    updateValue (name, v) {
      this.values[name] = v
      this.validate()
    },
    save () {
      this.validate(true)
      if (Object.keys(this.errors).length === 0) {
        this.$store.dispatch('runBatch', { options: this.values, batchId: this.batch.batch_id })
        this.$emit('close')
      }
    },
    doOsm () {
      this.$store.dispatch('batchRunOsm', this.batch.batch_id)
      this.$emit('close')
    },
    delBatch () {
      this.$store.dispatch('deleteBatch', this.batch.batch_id)
      this.$emit('close')
    }
  },
  components: {
    Loading
  }
}
</script>
<style>
.batch {
  width: 300px;
  background: white;
  box-shadow: 0 0 5px 0 rgba(255, 255, 255, 0.6);
  position: absolute;
  top: 50px;
  right: 50px;
  padding: 10px 0px;
}
.batch .button {
  width: calc(100% - 40px);
  height: 30px;
  border: 2px solid blue;
  background: white;
  cursor: pointer;
  font-weight: 600;
  color: blue;
  margin: 10px 20px;
}
.batch > .close {
  position: absolute;
  font-size: 16;
  color: #f63737;
  right: 15px;
  top: 15px;
  cursor: pointer;
}
.batch > .title {
  font-size: 24px;
  text-align: center;
  width: 100%;
  display: block;
  margin-bottom: 10px;
}
.batch > form > .row {
  padding: 10px 20px;
}
.batch > form > .row > input {
  border: 1px solid #ccc;
  padding: 10px;
  border-radius: 3px;
  width: calc(100% - 20px);
}
.batch > form > .row.error {
  background: rgba(255, 0, 0, 0.2);
}
.batch > form > .row > span.error {
  font-weight: 600;
  color: red;
  display: block;
}
.batch > span.prop {
  display: block;
  font-size: 18px;
  padding: 2px 20px;
}
.batch > hr {
  color: #eee;
  margin: 20px 0;
}
.batch > .loading {
  left: 50%;
  transform: translateX(-50%);
}
.batch button.green {
  color: green;
  border-color: green;
}
.batch button.red {
  border-color: red;
  color: red;
}
</style>
