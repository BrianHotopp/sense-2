<script setup>
import { ref, watchEffect, computed, onMounted } from 'vue'
import {store} from '../../store.js';
import NearestNeighborsList from './NearestNeighborsList.vue';
import NearestNeighborsPlot from './NearestNeighborsPlot.vue';
const props = defineProps(
    ["al"]
)
const target_word = ref(null);
const first = ref("true");
const num_neighbors = ref(10);
const displaydata = ref(null);
const formdata = ref({
    num_neighbors: 10,
    target_word: null,
});
// called when the alignment id changes
const firstctx = computed(() => {
    if (first.value == "true") {
        return store.selectedPlaintexts.elements[0].name;
    } else {
        return store.selectedPlaintexts.elements[1].name;
    }
})
const secondctx = computed(() => {
    if (first.value == "true") {
        return store.selectedPlaintexts.elements[1].name;
    } else {
        return store.selectedPlaintexts.elements[0].name;
    }
})
async function getContext(al, word, first, neighbors) {
    return await fetch("/api/getContext", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
         a_id: al.id,
        word: word,
        first: first,
        neighbors: neighbors
          }),
  }).then((res) => res.json()).then((data) => {
    // error handling
    if (data.error) {
    console.log("Failed to get the context from the api")
    console.log(data.error);
    return [];
    }
    return data;
  })
}

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
// called on mount
onMounted(() => {
    // get the first most shifted word
    if (store.selectedWord != null) {
        target_word.value = store.selectedWord;
        formdata.value.target_word = store.selectedWord;
    } else {
        getSingleMostShiftedWord(props.al).then((word) => {
            target_word.value = word;
            formdata.value.target_word = word;
        })
    }
    // get the context for chosen word
    getContext(props.al, target_word.value, first.value, num_neighbors.value).then((data) => {
        displaydata.value = data;
    })
})
function swapContext(){
    // fetch the new context
    let nfirst = first.value;
    if (nfirst == "true") {
        nfirst = "false";
    } else {
        nfirst = "true";
    }
     getContext(props.al, target_word.value, nfirst, num_neighbors.value).then((data) => {
        // error handling
        if (data.error) {
        console.log("Failed to get the context from the api")
        console.log(data.error);
        return [];
        }
        // update the data
        displaydata.value = data;
        first.value = nfirst;
    })

}
function fetchNewContext(){
    // fetch the new context
    getContext(props.al, target_word.value, first.value, num_neighbors.value).then((data) => {
        // error handling
        if (data.error) {
        console.log("Failed to get the context from the api")
        console.log(data.error);
        return [];
        }
        // update the data
        displaydata.value = data;
    })
}

function updateSettings(new_settings){
    // update the settings
    getContext(props.al, new_settings.target_word, first.value, new_settings.num_neighbors).then((data) => {
        // error handling
        if (data.error) {
        console.log("Failed to get the context from the api")
        console.log(data.error);
        return [];
        }
        // update the data
        displaydata.value = data;
        target_word.value = new_settings.target_word;
        num_neighbors.value = data.neighbors.length-1;
    })
}
function nnWordClick(word){
    target_word.value = word;
    formdata.value.target_word = word;
    fetchNewContext();
}
</script>

<template>
<div class="card p-3 mb-3">
    <div class="row mb-3 ">
        <div class="col">
        <h5 class="text-start">Alignment type: <b>{{al.name}}</b></h5>
        </div>
    </div>
    <div class="row">
        <div class="col">
            <p>
                Viewing words from {{secondctx}} that are most similar in meaning to <b>{{target_word}}</b> from {{firstctx}}.
                </p>

                    <button class="btn btn-primary mb-3" @click="swapContext">Swap Context</button>
                <!--form  -->
                <div class="card mb-3">
                <div class="form-group row p-3">
                    <label for="num_neighbors" class="col-sm-2 col-form-label">Number of neighbors</label>
                    <div class="col-sm-2">
                    <input type="number" class="form-control" id="num_neighbors" v-model="formdata.num_neighbors" min="1" max="100">
                    </div>
                    <div class="col-sm-2">
                        <!-- input to set custom target word -->
                        <input type="text" class="form-control" id="target_word" v-model="formdata.target_word" placeholder="Target word">
                    </div>
                    <div class="col-sm-2">
                    <button class="btn btn-primary" @click="updateSettings(formdata)">Update Settings</button>
                    </div>

                </div>
                </div> 
            </div>
    </div>
    <div class="row">
        <div class="col-6">
        <NearestNeighborsList v-if="displaydata != null" :word="target_word" :neighbor-words="displaydata.neighbors" @select-word="nnWordClick"></NearestNeighborsList>
        </div>
        <div class="col-6">
        <div class="row">
            <div class="col">
            </div>
        </div>
        <div class="row">
            <div class="col">
        <NearestNeighborsPlot v-if="displaydata != null" :word="target_word" :neighbor-words="displaydata.neighbors" :neighbor-coords="displaydata.vectors"></NearestNeighborsPlot>
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
