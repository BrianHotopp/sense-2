<script setup>
import { ref, computed } from "vue";
import { availableAlignments} from "../../alignmentConfigs.js";	
</script>

<template>
<div class="card p-3">
<!-- form to configure the settings for an alignment-->
<form >
<!-- true/false checkbox for is_soft -->
<div class="form-group">
<div class="form-check">
  <input class="form-check-input" type="checkbox" value="" v-model="availableAlignments['noise-aware'].is_soft" id="flexCheckDefault">
  <label class="form-check-label" for="flexCheckDefault">
Use soft expectation maximization instead of hard expectation maximization: {{availableAlignments['noise-aware'].is_soft}}
  </label>
</div>
</div>
</form>
</div>
</template>

<style scoped>

</style>
