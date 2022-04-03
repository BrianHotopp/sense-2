<script setup>
import { ref } from 'vue'

const props = defineProps(
    ["words"]
)

const count = ref(0)
</script>

<template>
<div>
    <h3>
        Most Shifted Words
    </h3>
    <table class="table table-striped">
  <thead>
    <tr>
      <th scope="col">#</th>
      <th scope="col">Word</th>
      <th scope="col">Shift (Cosine Distance)</th>
    </tr>
  </thead>
  <tbody>
    <tr v-for="(word, index) in words" :key="index">
      <th scope="row">{{index+1}}</th>
      <td>{{word.word}}</td>
      <td>{{word.shift}}</td>
    </tr>
  </tbody>
</table>
</div>
</template>

<style scoped>
</style>
