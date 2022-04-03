<script setup>
import EmbeddingsTable from './EmbeddingsTable.vue'
import { ref } from 'vue'

defineProps({
  msg: String
})

const count = ref(0)
</script>

<template>
<div class="container-xl">
<EmbeddingsTable /> 
</div>
</template>

<style scoped>
a {
  color: #42b983;
}
</style>
