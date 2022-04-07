<script setup>
import { ref, onMounted, watch, watchEffect } from "vue";
import MostShifted from "./MostShifted.vue";
import NearestNeighborsList from "./NearestNeighborsList.vue";
import NearestNeighborsPlot from "./NearestNeighborsPlot.vue";
import ExampleSentences from "./ExampleSentences.vue";
const props = defineProps(["a"]);
//const a_id = ref(props.alignment)
const top_n = ref(20);
const top_n_words = ref(null);
const selected_word = ref(null);
const n_neighbors = ref(20);
const first = ref("true");
const neighbor_words = ref(null);
const neighbor_coords = ref(null);
const examples = ref(null);
const context_1 = ref("context 1");
const context_2 = ref("context 2");
function changeSelectedWord(word) {
  selected_word.value = word;
}
watchEffect(async () => {
  // fetch the top shifted words and watch for changes to the alignment id or the top_n value
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
    });
});
watch([first, n_neighbors], async () => {
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
  }).then((res) => res.json()).then((data) => {
      neighbor_words.value = data.neighbors;
      neighbor_coords.value = data.vectors;
      });
});
watch(selected_word, async (newWord, oldWord) => {
  // update the context and examples if the selected word changes
  fetch("/api/getContext", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      a_id: props.a.id,
      word: newWord,
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

  fetch("/api/getExampleSentences", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      id: props.a.id,
      word: selected_word.value,
    }),
  })
    .then((res) => res.json())
    .then((data) => {
      examples.value = data.sentences;
    })
    .catch((err) => {
      console.log(err);
    });
});
onMounted(() => {});
</script>

<template>
  <div>
    <!-- container for alignment metadata -->
    <div class="container-xl mt-3">
      <div class="row">
        <div class="col-12">
          <div class="card">
            <div class="card-body" style="text-align: left">
              <h3 class="card-title">{{ a.name }}</h3>
              <p class="card-text">{{ a.description }}</p>
            </div>
          </div>
        </div>
      </div>
      <div class="row mt-3">
        <div class="col-6">
          <MostShifted
            v-if="top_n_words != null"
            :words="top_n_words"
            @select-word="changeSelectedWord"
          />
        </div>
        <div class="col-6">
          <div class="row">
            <NearestNeighborsList
              v-if="selected_word != null && neighbor_words != null"
              :word="selected_word"
              :neighbor-words="neighbor_words"
              :context_1="context_1"
              :context_2="context_2"
              @select-word="changeSelectedWord"
            />
          </div>
          <div class="row">
            <p v-if="neighbor_coords != null">
              Viewing nearest neighbors as if <b>"{{ selected_word }}"</b> is in the
              <select v-model="first">
                <option value="true">First</option>
                <option value="false">Second</option>
              </select>
              context.
            </p>

            <NearestNeighborsPlot
              v-if="
                selected_word != null &&
                neighbor_words != null &&
                neighbor_coords != null
              "
              :word="selected_word"
              :neighbor-words="neighbor_words"
              :neighbor-coords="neighbor_coords"
            />
          </div>
        </div>
        <div class="row">
          <div class="col-12">
            <ExampleSentences
              v-if="
                examples != null &&
                selected_word != null &&
                context_1 != null &&
                context_2 != null
              "
              :sentences="examples"
              :word="selected_word"
              :context_1="context_1"
              :context_2="context_2"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
a {
  color: #42b983;
}
</style>
