<script setup>
import { ref } from 'vue'

const props = defineProps(
    ["words"]
)

const count = ref(0)
</script>

<template>
<div>
    <h5 style="text-align: left">
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
      <td><a href="#!" @click="$emit('selectWord', word[0])">{{word[0]}}</a></td>
      <td>{{word[1].toFixed(2)}}</td>
    </tr>
  </tbody>
</table>
</div>
</template>

<style scoped>
</style>
