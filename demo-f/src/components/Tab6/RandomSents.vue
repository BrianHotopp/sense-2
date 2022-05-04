<script setup>
import { ref, onMounted, watchEffect, computed } from "vue";
import { store } from "../../store.js";
const props = defineProps(["target_word", "al_id"]);
const first = ref("true");
const displaydata = ref(null);
const target_word = ref(props.target_word);
function highlight(text, word) {
  // highlight the word in the text wherever it occurs, ignoring case but preserving the case of the word
  const highlight = (needle, haystack) =>
    text.replace(
      // either case regex

      new RegExp(`^${word}| ${word}| ${word}[^a-z]$`, "gi"),
      (str) => `<mark><strong>${str}</strong></mark>`
    );
  return highlight(text, word);
}
function getRandomSentence() {
  // hits the api and gets a random sentence for the target word in the desired context
  return fetch("/api/getRandomSentence", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      id: props.al_id,
      word: target_word.value,
      first: first.value,
    }),
  })
    .then((res) => res.json())
    .then((data) => {
      // error handling
      if (data.error) {
        console.log("Failed to get the random sentence from the api");
        console.log(data.error);
      }
      displaydata.value = data;
    });
}
const firstctx = computed(() => {
  if (first.value == "true") {
    return store.selectedPlaintexts.elements[0].name;
  } else {
    return store.selectedPlaintexts.elements[1].name;
  }
});
const secondctx = computed(() => {
  if (first.value == "true") {
    return store.selectedPlaintexts.elements[1].name;
  } else {
    return store.selectedPlaintexts.elements[0].name;
  }
});
function swapContext() {
  // swaps the context
  if (first.value == "true") {
    first.value = "false";
  } else {
    first.value = "true";
  }
  getRandomSentence();
}
// watch if target_word changes or if the context changes
watchEffect(() => {
  if (props.target_word) {
    target_word.value = props.target_word;
  }
});
// get random sentence on mount
onMounted(() => {
  getRandomSentence();
});
</script>

<template>
  <div>
    <div class="row">
      <div class="col-12">
        <h5><u>Random Sentence</u></h5>
      </div>
    </div>
    <div class="row">
      <div class="col-12 mb-3">
        <p>
          <button
            type="button"
            class="btn btn-secondary me-md-2"
            @click.prevent="getRandomSentence()"
          >
            Get New Sentence
          </button>
          <button
            type="button"
            class="btn btn-secondary"
            @click.prevent="swapContext()"
          >
            Swap Context
          </button>
        </p>
      </div>
    </div>
    <div class="row">
      <div class="col-6">
        <div class="row">
          <div class="col-12">
            <h5>
              <u>{{ firstctx }}</u>
            </h5>
          </div>
        </div>
        <div class="row">
          <div class="col-12">
            <div v-if="displaydata != null" class="card">
              <div class="card-body">
                <p
                  v-html="highlight(displaydata.sentences[0], target_word)"
                ></p>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="col-6">
        <div class="row">
          <div class="col-12">
            <h5>
              <u>{{ secondctx }}</u>
            </h5>
          </div>
        </div>
        <div class="row">
          <div class="col-12">
            <div
              v-if="displaydata != null"
              v-for="s in displaydata.sentences[1]"
              class="card mb-1 align-middle"
            >
              <div class="card-body">
                <p v-html="highlight(s, target_word)"></p>
              </div>
            </div>
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
