<script setup>

import { ref, onMounted, watchEffect, computed } from 'vue'
import MostShifted from "./MostShifted.vue"
const display = ref([]);
const numWords = ref(20);
const props = defineProps(['selectedAlignments']);

function chunkArray(myArray, chunk_size) {
  var index = 0;
  var arrayLength = myArray.length;
  var tempArray = [];
  for (index = 0; index < arrayLength; index += chunk_size) {
    var myChunk = myArray.slice(index, index + chunk_size);
    // Do something if you want with the group
    tempArray.push(myChunk);
  }
  return tempArray;
}
const chunkedArray = computed(() => {
  return chunkArray(display.value, 3);
});
watchEffect(async () => {
  const promises = props.selectedAlignments.map(async (al) => {
    const ret = await fetch("/api/getTopShiftedWords", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      id: al.id,
      num_words: numWords.value, 
    }),
  }).then((res) => res.json());
  // error handling
  if (ret.error) {
    console.log(ret.error);
    return [];
  }
  return ret;
})
const data = await Promise.all(promises)
display.value = props.selectedAlignments.map((al, i) => {
  return {
    id: al.id,
    name: al.name,
    words: data[i].shifted_words,
  }
})
})


</script>

<template>

<div class="container-xl mb-3">
  <div class="row mb-3 text-start">
    <div class="col">
  <form >
    <div class="form-group">
      <label class="mb-3" for="numWords">Number of words to display:</label>
      <input
        type="number"
        class="form-control"
        id="numWords"
        v-model="numWords"
        @click.prevent
      />
    </div>
    </form>
    </div>
  </div>
    <div v-for="triple in chunkedArray" class="row mb-3">
  <div v-for="alignment in triple" class="col-4">
    <MostShifted :alignmentName="alignment.name" :words="alignment.words"/>
  </div>
</div>
</div>
</template>

<style scoped>
</style>
