<template>
  <div class="admin-panel">
    <AdminMap @selection="draw=$event" :enableAdd="!draw && !openedBatch" @open="openedBatchId = $event" @centered="center = null" :center="centerLoc"/>
    <NewBatch v-if="draw" :selection="draw" @close="draw = null"/>
    <Batch v-else-if="openedBatch" :batch="openedBatch" @close="openedBatchId = null"/>
    <BatchList v-else @open="openedBatchId = $event;center = $event"/>
  </div>
</template>
<script>
import AdminMap from '@/components/AdminMap.vue'
import NewBatch from '@/components/NewBatch.vue'
import Batch from '@/components/Batch.vue'
import BatchList from '@/components/BatchList.vue'

export default {
  name: 'AdminPanel',
  data () {
    return {
      draw: null,
      openedBatchId: null,
      center: null
    }
  },
  computed: {
    openedBatch () {
      if (!this.openedBatchId) {
        return null
      }
      return this.$store.getters.batches.find(b => b.batch_id === this.openedBatchId)
    },
    centerLoc () {
      if (!this.center) return null
      const batch = this.$store.getters.batches.find(b => b.batch_id === this.center)
      const lat = batch.nodes.map(n => n[0]).reduce((agg, x) => agg + x) / batch.nodes.length
      const lon = batch.nodes.map(n => n[1]).reduce((agg, x) => agg + x) / batch.nodes.length
      return { lat, lon }
    }
  },
  components: {
    AdminMap, NewBatch, Batch, BatchList
  }
}
</script>
