<script setup>
import { ref, watchEffect } from 'vue';

const props = defineProps(["al"]);
const displaydata = ref(null);
const target_word = ref(null);
const formdata = ref({
    target_word: null,
    max_sentences: 10,
});
async function getSingleMostShiftedWord(al) {
    // returns the first most shifted word from the server for the alignment
    return await fetch("/api/getTopShiftedWords", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      id: al.id,
      num_words: 1, 
    }),
  }).then((res) => res.json()).then((data) => {
    // error handling
    if (data.error) {
    console.log("Failed to get the single top shifted word from the api")
    console.log(data.error);
    return ""
    }
    return data.shifted_words[0][0];
})}
async function getExampleSentences(al, word){
    return await fetch("/api/getExampleSentences", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            id: al.id,
            word: word,
        }),
    }).then((res) => res.json()).then((data) => {
        // error handling
        if (data.error) {
            console.log("Failed to get the example sentences from the api")
            console.log(data.error);
            return [];
        }
        return data;
    })
}
function fetchNewSentences(){
    // fetch the new sentences
    getExampleSentences(props.al, target_word.value).then((data) => {
        // error handling
        if (data.error) {
        console.log("Failed to get the example sentences from the api")
        console.log(data.error);
        return [];
        }
        // update the data
        displaydata.value = data;
    })

}
function highlight(text, word){
    // highlight the word in the text wherever it occurs, ignoring case but preserving the case of the word
    const highlight = (needle, haystack) =>
    text.replace(
      // either case regex
      
      new RegExp(`^${word}| ${word}| ${word}[^a-z]$`, 'gi'),
      (str) => `<mark><strong>${str}</strong></mark>`
    );
    return highlight(text, word);
}
function updateSettings(new_settings){
    // update the settings
    getExampleSentences(props.al, new_settings.target_word).then((data) => {
        // error handling
        if (data.error) {
        console.log("Failed to get the example sentences from the api")
        console.log(data.error);
        return [];
        }
        // update the data
        displaydata.value = data;
    })
    target_word.value = new_settings.target_word;
}
watchEffect(async () => {
  target_word.value = await getSingleMostShiftedWord(props.al);
  formdata.value.target_word = target_word.value;
  fetchNewSentences();
});

</script>

<template>
<div class="card mb-3">
  <div class="card-header">
    <h5>Alignment type <b>{{props.al.name}}</b></h5>
  </div>
  <div class="card-body">
    <form class="row mb-3">
      <div class="form-group row">
        <label for="target_word" class="col-sm-2 col-form-label">Target word</label>
        <div class="col-sm-2">
        <input type="text" class="form-control" id="target_word" v-model="formdata.target_word" placeholder="Enter target word">
        </div>
        <div class="col-sm-2">
      <button type="button" class="btn btn-primary" @click="updateSettings(formdata)">Get Sentences</button>
          </div>
      </div>
      </form>
      <div v-if="displaydata != null">
      <div class="row" v-for="sentencepair in displaydata.sentences">
        <div class="col">
          <p v-html="highlight(sentencepair[0], target_word)"></p>
          <p v-html="highlight(sentencepair[1], target_word)"></p>
          <hr>
          </div>
        </div>
        </div>
    </div>

</div>
</template>

<style scoped>

</style>
