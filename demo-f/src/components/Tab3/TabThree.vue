<script setup>
import { ref, onMounted, reactive } from "vue";
import { store } from "../../store.js";
import { togglePush } from "../../Queue.js";
const alignments = ref(null);

function getAlignments() {
  fetch("/api/getAlignments", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      e1_id: store.selectedPlaintexts.elements[0].id,
      e2_id: store.selectedPlaintexts.elements[1].id,
    }),
  })
    .then((res) => res.json())
    .then((data) => {
      // set the alignments to the data alignments
      alignments.value = data.alignments;
    });
}
onMounted(() => {
  getAlignments();
});
</script>

<template>
  <div class="container-xl mt-4">
    <div class="row">
      <div class="col-12 mb-2">
        <div class="d-flex justify-content-start">
          <h5>Select Alignments to Compare:</h5>
        </div>
      </div>
    </div>
    <div class="row">
      <div class="col mb-4" v-for="a in alignments" :key="a.id">
        <a
          href="#"
          class="list-group-item-action"
          style="text-decoration: none"
        >
          <div
            class="card"
            :class="{
              'text-white': store.selectedAlignments
                .map((a) => a.id)
                .includes(a.id),
              'bg-primary': store.selectedAlignments
                .map((a) => a.id)
                .includes(a.id),
            }"
            @click.prevent="
              togglePush(store.selectedAlignments, { id: a.id, name: a.name })
            "
          >
            <div class="card-header">
              <h6>
                <b>{{ a.name }}</b>
              </h6>
            </div>
            <div class="card-body">
              <p>{{ a.description }}</p>
            </div>
          </div>
        </a>
      </div>
    </div>
  </div>
</template>

<style scoped>
a {
}
</style>
