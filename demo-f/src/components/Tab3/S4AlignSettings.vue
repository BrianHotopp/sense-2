<script setup>
import { ref, computed } from "vue";
import { availableAlignments, cls} from "../../alignmentConfigs.js";	
</script>

<template>
<div class="card p-3">
<!-- form to configure the settings for an alignment
	"s4":{
		"cls_model": "nn",
		"iters": 100,
		"n_targets": 10,
		"n_negatives": 10,
		"fast": true,
		"rate": 0,
		"t": 0.5,
		"t_overlap": 0.5
	}
-->
<form >
<!-- true/false checkbox for is_soft -->
<div class="form-group">
<label class="d-flex justify-content-start" for="clsModelType">Classification Model Type</label>
<select class="form-select mb-3" id="clsModelType" v-model="availableAlignments['s4'].cls_model">
<option v-for="type in cls.modelTypes" :value="type">{{type}}</option>
</select>
</div>
<div class="form-group">
<label for="iterations" class="me-3 d-flex justify-content-start">Iterations: {{availableAlignments['s4'].iters}}</label>
<input type="range" class="form-range" id="iterations" min="10" max="1000" v-model="availableAlignments['s4'].iters" step="1">
</div>
<div class="form-group">
<label for="ntargets" class="me-3 d-flex justify-content-start">Number of target words: {{availableAlignments['s4'].n_targets}}</label>
<input type="range" class="form-range" id="ntargets" min="1" max="100" v-model="availableAlignments['s4'].n_targets" step="1">
</div>
<div class="form-group">
<label for="nnegs" class="me-3 d-flex justify-content-start">Number of words to use as negative samples: {{availableAlignments['s4'].n_negatives}}</label>
<input type="range" class="form-range" id="nnegs" min="1" max="100" v-model="availableAlignments['s4'].n_negatives" step="1">
</div>
<div class="form-group">
<div class="form-check">
<label class="form-check-label" for="flexCheckDefault">
Use fast semantic change injection: {{availableAlignments['s4'].fast}}
</label>
  <input class="form-check-input" type="checkbox" value="" v-model="availableAlignments['noise-aware'].is_soft" id="flexCheckDefault">
</div>
</div>
<div class="form-group">
<label for="rate" class="me-3 d-flex justify-content-start">Rate of semantic change injection: {{availableAlignments['s4'].rate}}</label>
<input type="range" class="form-range" id="rate" min="0" max="1" v-model="availableAlignments['s4'].rate" step="0.01">
</div>
<div class="form-group">
<label for="cthresh" class="me-3 d-flex justify-content-start">Classification Threshold: {{availableAlignments['s4'].t}}</label>
<input type="range" class="form-range" id="cthresh" min="0" max="1" v-model="availableAlignments['s4'].t" step="0.01">
</div>
<div class="form-group">
<label for="toverlap" class="me-3 d-flex justify-content-start">Overlap Threshold: {{availableAlignments['s4'].t_overlap}}</label>
<input type="range" class="form-range" id="toverlap" min="0" max="1" v-model="availableAlignments['s4'].t_overlap" step="0.01">
</div>
</form>
</div>
</template>

<style scoped>

</style>
