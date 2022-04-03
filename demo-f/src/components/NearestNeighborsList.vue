<script setup>
import { ref } from 'vue'

const props = defineProps(
    ["word", "neighborWords"]
)
</script>

<template>
    <div>
    <h3>
           Nearest Neighbors </h3>
    <table class="table table-striped">
  <thead>
    <tr>
      <th scope="col">#</th>
      <th scope="col">Word</th>
      <th scope="col">Distance (Euclidean)</th>
    </tr>
  </thead>
  <tbody>
    <tr v-for="(word, index) in neighborWords" :key="index">
      <th scope="row">{{index+1}}</th>
      <td>{{word.neighbor}}</td>
      <td>{{word.dist}}</td>
    </tr>
  </tbody>
</table>
</div>
</template>

<style scoped>
</style>
