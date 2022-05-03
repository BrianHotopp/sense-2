<script setup>
import { ref, watchEffect } from "vue";
import SentenceViewer from "./SentenceViewer.vue";
const props = defineProps(["selectedAlignments"]);
</script>

<template>
  <div class="container-xl mb-3">
    <div class="row mb-3 text-start">
      <div class="col">
        <SentenceViewer
          v-for="alignment in selectedAlignments.elements"
          :al="alignment"
        ></SentenceViewer>
      </div>
    </div>
  </div>
</template>

<style scoped>
a {
  color: #42b983;
}
</style>
