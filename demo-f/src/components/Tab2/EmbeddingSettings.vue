<script setup>
import { ref, computed } from "vue";
import { availableEmbeddings, selectedEmbedding} from "../../embeddingConfigs.js";	
import Word2VecSettings from "./Word2VecSettings.vue";
const embeddingTypeOptions = computed(() => {
// the options are the keys of availableEmbeddings
return Object.keys(availableEmbeddings);
});

</script>

<template>
<div>
<!-- form to configure the settings for an embedding -->
<form >
<!-- dropdown to select the embedding object to edit -->
<label class="d-flex justify-content-start" for="embeddingTypeSelect">Select Embedding Type</label>
<select class="form-select mb-3" id="embeddingTypeSelect" v-model="selectedEmbedding.embedding">
<option v-for="type in embeddingTypeOptions" :value="type">{{type}}</option>
</select>
<!-- form to configure the embedding, changes depending on which embedding type is selected -->
<div v-if="selectedEmbedding.embedding != null">
<div v-if="selectedEmbedding.embedding === 'word2vec'">
<Word2VecSettings/>
</div>
</div>

</form>

</div>
</template>

<style scoped>

</style>
