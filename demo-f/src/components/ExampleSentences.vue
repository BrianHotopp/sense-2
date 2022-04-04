<script setup>
import { ref } from 'vue'

const props = defineProps(["sentences","word", "context_1", "context_2"]);

</script>

<template>
<div class="list-group">
  <div v-for="expair, index in sentences" :key="index" class="list-group-item list-group-item-action flex-column align-items-start">
    <div class="d-flex w-100 justify-content-between">
        

   <small><b>Sentence from {{context_1}}</b></small>
    </div>
    <div class="d-flex w-100 justify-content-between">
        
    <p class="mb-1">{{expair[0]}}</p>
    </div>
    <div class="d-flex w-100 justify-content-between">
        
    <small><b>Sentence from {{context_2}}</b></small>
    </div>
    <div class="d-flex w-100 justify-content-between">
        
    <p class="mb-1">{{expair[1]}}</p>
    </div>
</div>
</div>
</template>

<style scoped>

</style>
