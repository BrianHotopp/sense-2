<script setup>
import { onMounted, ref } from 'vue'
import {store } from '../../store.js';
import {shiftPush} from '../../Queue.js';

const embeddings_for_pt1 = ref(null);
const embeddings_for_pt2 = ref(null);

function getEmbeddings(){
fetch("/api/getEmbeddings", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      pt_id: store.selectedPlaintexts.elements[0].id,
    }),
  })
    .then((res) => res.json())
    .then((data) => {
      // set the embeddings to the data
      embeddings_for_pt1.value = data;
    });
  fetch("/api/getEmbeddings", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      pt_id: store.selectedPlaintexts.elements[1].id,
    }),
  })
    .then((res) => res.json())
    .then((data) => {
      // set the embeddings to the data
      embeddings_for_pt2.value = data;
    });

}
function embeddingClick(tg, pl, sz){
  shiftPush(tg, pl, sz);
  // clear the selected alignments and word
  store.selectedAlignments.elements = [];
  store.selectedWord = null;


}
onMounted(() => {
  getEmbeddings();
});
</script>

<template>
<div class="container-xl mb-3">
            <div class="row">
              <div class="col-6 text-start">
                <h5>Embeddings for {{ store.selectedPlaintexts.elements[0].name}}</h5>
              </div>
              <div class="col-6 text-start">
                <h5>Embeddings for {{ store.selectedPlaintexts.elements[1].name}}</h5>
              </div>
            </div>
            <div class="row">
              <div class="col-6">
                <div class="list-group">
                  <a
                    v-for="e in embeddings_for_pt1"
                    :key="e.id"
                    class="list-group-item list-group-item-action"
                    @click.prevent="embeddingClick(store.selectedEmbeddings.forPt1, {id: e.id, name: e.name}, 1)"
                    :class="{ active: store.selectedEmbeddings.forPt1.map((e) => e.id).includes(e.id) }"
                    href="#"
                  >
                    <b>{{ e.name }}</b>
                    {{ e.description }}
                  </a>
                </div>
              </div>
              <div class="col-6">
                <div class="list-group">
                  <a
                    class="list-group-item list-group-item-action"
                    v-for="e in embeddings_for_pt2"
                    :key="e.id"
                    @click.prevent="embeddingClick(store.selectedEmbeddings.forPt2, {id: e.id, name: e.name}, 1)"
                    :class="{ active: store.selectedEmbeddings.forPt2.map((e) => e.id).includes(e.id) }"
                    href="#"
                  >
                    <b>{{ e.name }}</b>
                    {{ e.description }}
                  </a>
                </div>
              </div>
            </div>
            <div class="row">
              <!-- <div class="col-6">
                <button type="button" class="btn btn-success">Success</button>
              </div>
              <div class="col-6">
                <button type="button" class="btn btn-success">Success</button>
              </div> -->
            </div>
          </div>

</template>

<style scoped>
</style>

