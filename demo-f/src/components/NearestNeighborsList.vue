<script setup>
import { ref } from 'vue'

const props = defineProps(
    ["word", "neighborWords"]
)
</script>

<template>
    <div>
    <h5 style="text-align: left">
           Nearest Neighbors of {{word}}
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
    <tr v-for="(word, index) in neighborWords.slice(0, -1)" :key="index">
      <th scope="row">{{index+1}}</th>
      <td><a href="#!" @click="$emit('selectWord', word[0])">{{word[0]}}</a></td>
      <td>{{word[1]}}</td>
    </tr>
  </tbody>
</table>
</div>
</template>

<style scoped>
</style>
