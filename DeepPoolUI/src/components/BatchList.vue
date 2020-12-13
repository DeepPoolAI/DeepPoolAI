<template>
  <div class="batch-list">
    <div v-for="b in batches" :key="b.batch_id" class="batch-element" @click="$emit('open', b.batch_id)">
      <Loading v-if="b.is_working" :progress="b.progress" />
      <span class="name">{{ b.name || b.batch_id }}</span>
      <span class="scanned">Done: {{ b.done }} / {{ b.todo + b.done }}</span>
    </div>
  </div>
</template>
<script>
import Loading from '@/components/Loading.vue'

export default {
  name: 'BetchList',
  data () {
    return {
    }
  },
  computed: {
    batches () {
      return this.$store.getters.batches
    }
  },
  methods: {},
  components: {
    Loading
  }
}
</script>
<style>
.batch-list {
  width: 300px;
  background: white;
  box-shadow: 0 0 5px 0 rgba(255, 255, 255, 0.6);
  position: absolute;
  top: 50px;
  right: 50px;
  padding: 10px 0px;
}
.batch-list > .batch-element {
  height: 60px;
  background: white;
  cursor: pointer;
  padding: 10px 20px 10px 85px;
  position: relative;
  border-bottom: 1px solid #ddd;
}
.batch-list > .batch-element:last-child {
  border-bottom: none;
}
.batch-list > .batch-element:hover {
  background: #eee;
}
.batch-list > .batch-element > .loading {
  position: absolute;
  top: 10px;
  left: 10px;
}
.batch-list > .batch-element > .name {
  display: block;
  width: 100%;
  height: 20px;
  overflow-x: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 18px;
  font-weight: 600;
  margin-top: 9px;
}
.batch-list > .batch-element > .scanned {
  font-size: 16px;
  margin-top: 3px;
}
</style>
