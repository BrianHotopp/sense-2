<script setup>
import { ref } from 'vue'

const props = defineProps(
    ["words"]
)

const count = ref(0)
</script>

<template>
<div>
    <h5>
        Most Shifted Words
    </h5>
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
      <td>{{word[0]}}</td>
      <td>{{word[1]}}</td>
    </tr>
  </tbody>
</table>
</div>
</template>

<style scoped>
</style>
