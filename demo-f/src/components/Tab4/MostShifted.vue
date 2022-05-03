<script setup>
import { ref, computed } from "vue";

const props = defineProps([
  "alignmentName",
  "words",
  "filterType",
  "commonWords",
  "unionWords",
]);

// computed for filtered words
const filteredWords = computed(() => {
  if (props.filterType === "common") {
    return props.words.filter((word) => {
      return props.commonWords.includes(word[0]);
    });
  } else if (props.filterType === "unique") {
    // get words that are unique to this alignment
    return props.words.filter((word) => {
      return !props.unionWords.includes(word[0]);
    });
  } else {
    return props.words;
  }
});
// computed for active color
const activeColor = computed(() => {
  if (props.filterType === "common") {
    return "#fff0c4";
  } else if (props.filterType === "unique") {
    return "#e4f7ee";
  } else {
    return "white";
  }
});
</script>

<template>
  <div class="card p-2">
    <h5 style="text-align: left">
      Alignment type: <b>{{ alignmentName }}</b>
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
        <tr
          v-for="(word, index) in filteredWords"
          :key="index"
          :style="{ background: activeColor }"
        >
          <th scope="row">{{ index + 1 }}</th>
          <td>
            <a href="#!" @click="$emit('selectWord', word[0])">{{ word[0] }}</a>
          </td>
          <td>{{ word[1].toFixed(2) }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped></style>
