<script setup>
import { ref } from 'vue'

const props = defineProps(
    ["word", "neighborWords"]
)
</script>

<template>
    <div>
    <h5>
           Nearest Neighbors 
    </h5>
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
      <td>{{word[0]}}</td>
      <td>{{word[1]}}</td>
    </tr>
  </tbody>
</table>
</div>
</template>

<style scoped>
</style>
