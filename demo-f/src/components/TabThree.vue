<script setup>

import { ref, onMounted } from 'vue'
import AlignmentViewer from './AlignmentViewer.vue'
defineProps(["alignments"]);
onMounted(() => {
  console.log("mounted tab 3");
});

</script>

<template>
<div>
<div v-for="alignment in alignments" :key="alignment.id">
  <AlignmentViewer :a="alignment" />
</div>
</div>
</template>

<style scoped>
a {
  color: #42b983;
}
</style>
