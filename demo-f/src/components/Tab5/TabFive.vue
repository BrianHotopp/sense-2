<script setup>
import NNViewer from "./NNViewer.vue";
import { ref, onMounted, watchEffect, computed } from "vue";
const props = defineProps(["selectedAlignments"]);
console.log("tabfive got", props.selectedAlignments);
</script>

<template>
  <div class="container-xl mb-3">
    <div class="row mb-3 text-start">
      <div class="col">
        <NNViewer
          v-for="alignment in selectedAlignments.elements"
          :al="alignment"
        ></NNViewer>
      </div>
    </div>
  </div>
</template>

<style scoped></style>
