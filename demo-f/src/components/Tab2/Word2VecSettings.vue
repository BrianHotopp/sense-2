<script setup>
import { ref, computed } from "vue";
import { availableEmbeddings } from "../../embeddingConfigs.js";	
</script>

<template>
<div class="card p-3">
<!-- form to configure the settings for an embedding -->
<form >
<!-- range inputs for size, window and min count -->
<div class="form-group">
<label for="size" class="me-3 d-flex justify-content-start">Vector Size: {{availableEmbeddings.word2vec.size}}</label>
<input type="range" class="form-range" id="size" min="100" max="1000" v-model="availableEmbeddings.word2vec.size" step="1">
</div>
<div class="form-group">
<label for="window" class="me-3 d-flex justify-content-start">Window Size: {{availableEmbeddings.word2vec.window}}</label>
<input type="range" class="form-range" id="window" min="5" max="50" v-model="availableEmbeddings.word2vec.window" step="1">
</div>

<div class="form-group">
<label for="minCount" class="me-3 d-flex justify-content-start">Min Count: {{availableEmbeddings.word2vec.minCount}}</label>
<input type="range" class="form-range" id="minCount" min="1" max="50" v-model="availableEmbeddings.word2vec.minCount" step="1">
</div>

</form>

</div>
</template>

<style scoped>

</style>
