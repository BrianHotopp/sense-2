<script setup>
import { ref, onMounted } from 'vue';
import {store} from '../../store.js';
import {shiftPush} from '../../Queue.js';
const ptexts = ref(null);
function getPlainTexts(){
fetch("/api/getPlainTexts", {
    method: "GET",
    headers: {},
  })
    .then((res) => res.json())
    .then((data) => {
      // set the plaintexts to the data
    ptexts.value = data;
    });
};
onMounted(() => {
    getPlainTexts();
  });
function ptClick(pt_id, pt_name) {
  shiftPush(store.selectedPlaintexts, {id: pt_id, name: pt_name}, 2)
  // deselect embeddings and alignments
  store.selectedEmbeddings.elements = [];
  store.selectedAlignments.elements = [];
  store.selectedWord = null;
}
</script>

<template>
        <div class="container-xl">
          <div class="row">
            <div class="col-12 mb-2">
              <div class="d-flex justify-content-start">
                <h5>Select a dataset:</h5>
              </div>
            </div>
          </div>
          <div class="row">
            <div class="col mb-4" v-for="pt in ptexts" :key="pt.id">
              <a
                href="#"
                class="list-group-item-action"
                style="text-decoration: none"
              >
                <div
                  class="card"
                  :class="{
                    'text-white': store.selectedPlaintexts.map(
                      (pt) => pt.id
                    ).includes(pt.id),
                    'bg-primary': store.selectedPlaintexts.map(
                      (pt) => pt.id
                    ).includes(pt.id),
                  }"
                  @click.prevent="ptClick(pt.id, pt.name)"
                >
                  <div class="card-header">
                    <h6>
                      <b>{{ pt.name }}</b>
                    </h6>
                  </div>
                  <div class="card-body">
                    <p>{{ pt.description }}</p>
                  </div>
                </div>
              </a>
            </div>
          </div>
        </div>
</template>

<style scoped>
</style>
