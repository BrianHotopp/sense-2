<script setup>
import { ref, onMounted } from "vue";
import MostShifted from "./MostShifted.vue";
import NearestNeighborsList from "./NearestNeighborsList.vue";
import NearestNeighborsPlot from "./NearestNeighborsPlot.vue"
const props = defineProps(["a"]);
//const a_id = ref(props.alignment)
const top_n = ref(20);
const top_n_words = ref(null);
const selected_word = ref(null);
const n_neighbors = ref(20);
const first = ref(true);
const neighbor_words = ref(null);
const neighbor_coords = ref(null);

onMounted(() => {
  console.log("im here");
  // log that we mounted tab 3 and are fetching the top top_n words
  console.log("mounted tab 3, fetching top n");
  // fetch the top top_n words
  fetch("/api/getTopShiftedWords", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      id: props.a.id,
      num_words: top_n.value,
    }),
  })
    .then((res) => res.json())
    .then((data) => {
      // set the embeddings to the data
      top_n_words.value = data.shifted_words;
      selected_word.value = data.shifted_words[0][0];
    })
    .then(() => {
      // fetch the neighbors of the selected word
      fetch("/api/getContext", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          a_id: props.a.id,
          word: selected_word.value,
          first: first.value,
          neighbors: n_neighbors.value,
        }),
      })
        .then((res) => res.json())
        .then((data) => {
          // set the embeddings to the data
          neighbor_words.value = data.neighbors;
          neighbor_coords.value = data.vectors;
        })
        .catch((err) => {
          console.log(err);
        });
    })
    .catch((err) => {
      console.log(err);
    });
});
</script>

<template>
  <div>
    <!-- container for alignment metadata -->
    <div class="container-xl mt-3">
      <div class="row">
        <div class="col-12">
          <h2>{{ a.name }}</h2>
          {{ a.description }}
        </div>
      </div>
      <div class="row">
        <div class="col-6">
          <MostShifted v-if="top_n_words != null" :words="top_n_words" />
        </div>
        <div class="col-6">
          <div class="row">
          <NearestNeighborsList
            v-if="selected_word != null && neighbor_words != null"
            :word="selected_word"
            :neighbor-words="neighbor_words"
          />
          </div>
          <div class="row">
          <NearestNeighborsPlot
            v-if="selected_word != null && neighbor_words != null && neighbor_coords != null"
            :word="selected_word"
            :neighbor-words="neighbor_words"
            :neighbor-coords="neighbor_coords"
           />
           </div>
        </div>
      </div>
      <!-- {{ alignment.id }} -->
      Examples here
    </div>
  </div>
</template>

<style scoped>
a {
  color: #42b983;
}
</style>
