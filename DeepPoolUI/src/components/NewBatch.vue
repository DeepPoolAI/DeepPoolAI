<template>
  <div class="new-batch">
    <span class="close" @click="$emit('close')">&#x274C;</span>
    <span class="title">Add new batch</span>
    <form @submit.prevent="save">
      <div v-for="inp in formInputs" :key="inp.name" class="row" :class="{ error: inp.errors }">
        <label :for="inp.name">{{ inp.label }}</label>
        <input v-if="inp.type === 'text'" type='text' :name="inp.name" @change="updateValue(inp.name, $event.target.value)" :value="values[inp.name]"/>
        <input v-if="inp.type === 'number'" type='number' :name="inp.name" @change="updateValue(inp.name, $event.target.valueAsNumber)" :value="values[inp.name]"/>
        <span class="error" v-for="e in inp.errors" :key="e">{{ e }}</span>
      </div>
      <button class="save">Add</button>
    </form>
  </div>
</template>
<script>
import form from '@/lib/NewBatchForm.js'
import validate from 'validate.js'

export default {
  name: 'NewBatch',
  data () {
    return {
      values: form.reduce((agg, f) => ({ ...agg, [f.name]: f.default }), {}),
      errors: {}
    }
  },
  props: {
    selection: Array
  },
  computed: {
    formInputs () {
      return form.map(f => ({ label: f.fullName || f.name, name: f.name, errors: this.errors[f.name], type: f.type }))
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
        this.$store.dispatch('addBatch', { ...this.values, nodes: this.selection })
        this.$emit('close')
      }
    }
  },
  components: {}
}
</script>
<style>
.new-batch {
  width: 300px;
  background: white;
  box-shadow: 0 0 5px 0 rgba(255, 255, 255, 0.6);
  position: absolute;
  top: 50px;
  right: 50px;
  padding: 10px 0px;
}
.new-batch > .close {
  position: absolute;
  font-size: 16;
  color: #f63737;
  right: 15px;
  top: 15px;
  cursor: pointer;
}
.new-batch > .title {
  font-size: 24px;
  text-align: center;
  width: 100%;
  display: block;
}
.new-batch > form > .row {
  padding: 10px 20px;
}
.new-batch > form > .row > input {
  border: 1px solid #ccc;
  padding: 10px;
  border-radius: 3px;
  width: calc(100% - 20px);
}
.new-batch > form > .row.error {
  background: rgba(255, 0, 0, 0.2);
}
.new-batch > form > .row > span.error {
  font-weight: 600;
  color: red;
  display: block;
}
.new-batch > form > .save {
  width: calc(100% - 20px);
  height: 30px;
  border: 3px solid #555;
  background: white;
  cursor: pointer;
  color: #555;
  margin: 10px;
}
</style>
