<script setup>
import { ref, computed } from "vue";
import { availableAlignments, selectedAlignment } from "../../alignmentConfigs.js";	
import GlobalAlignSettings from "./GlobalAlignSettings.vue";
import NoiseAwareAlignSettings from "./NoiseAwareAlignSettings.vue";
import S4AlignSettings from "./S4AlignSettings.vue";
const alignmentTypeOptions = computed(() => {
// the options are the keys of availableEmbeddings
return Object.keys(availableAlignments);
});

</script>

<template>
<div>
<!-- form to configure the settings for an alignment-->
<form >
<!-- dropdown to select the alignment object to edit -->
<label class="d-flex justify-content-start" for="alignmentTypeSelect">Select Alignment Type</label>
<select class="form-select mb-3" id="alignmentTypeSelect" v-model="selectedAlignment.alignmentType">
<option v-for="type in alignmentTypeOptions" :value="type">{{type}}</option>
</select>
<!-- form to configure the embedding, changes depending on which embedding type is selected -->
<div v-if="selectedAlignment.alignmentType!= null">
<div v-if="selectedAlignment.alignmentType === 'global'">
<!-- <GlobalAlignSettings/> -->
</div>
<div v-if="selectedAlignment.alignmentType === 'noise-aware'">
<NoiseAwareAlignSettings/>
</div>
<div v-if="selectedAlignment.alignmentType === 's4'">
<S4AlignSettings/>
</div>

</div>

</form>

</div>
</template>

<style scoped>

</style>
