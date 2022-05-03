<script setup>
import { onMounted, ref } from "vue";
import { store } from "../../store.js";
import { shiftPush } from "../../Queue.js";

const embeddings_for_pt1 = ref(null);
const embeddings_for_pt2 = ref(null);

const pt1embeddingForm = ref({
 id: store.selectedPlaintexts.elements[0].id,
 name: null,
 description: null,
 settings: null
});

const pt2embeddingForm = ref({
 id: store.selectedPlaintexts.elements[1].id,
 name: null,
 description: null,
 settings: null
});

function generateEmbedding(embeddingForm) {
// hits the api to generate an embedding
// returns the embedding id
fetch("/api/generateEmbedding", {
 method: "POST",
 headers: {
  "Content-Type": "application/json"
 },
 body: JSON.stringify(embeddingForm)
}).then(response => response.json()).then(data => {
 if (data.error) {
  alert(data.error);
 } else {
 // re-fetch the embeddings
 getEmbeddings();
 }
});
}

function getEmbeddings() {
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
function embeddingClick(tg, pl, sz) {
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
        <h5>Embeddings for {{ store.selectedPlaintexts.elements[0].name }}</h5>
      </div>
      <div class="col-6 text-start">
        <h5>Embeddings for {{ store.selectedPlaintexts.elements[1].name }}</h5>
      </div>
    </div>
    <div class="row mb-3">
      <div class="col-6">
        <div class="list-group">
          <a
            v-for="e in embeddings_for_pt1"
            :key="e.id"
            class="list-group-item list-group-item-action"
            @click.prevent="
              embeddingClick(
                store.selectedEmbeddings.forPt1,
                { id: e.id, name: e.name },
                1
              )
            "
            :class="{
              active: store.selectedEmbeddings.forPt1
                .map((e) => e.id)
                .includes(e.id),
            }"
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
            @click.prevent="
              embeddingClick(
                store.selectedEmbeddings.forPt2,
                { id: e.id, name: e.name },
                1
              )
            "
            :class="{
              active: store.selectedEmbeddings.forPt2
                .map((e) => e.id)
                .includes(e.id),
            }"
            href="#"
          >
            <b>{{ e.name }}</b>
            {{ e.description }}
          </a>
        </div>
      </div>
    </div>
    <div class="row">
      <div class="col-6">
        <!-- modal for adding embedding for embedding 1 -->
        <div class="d-flex justify-content-start">
          <!-- Button trigger modal -->
          <button
            type="button"
            class="btn btn-success"
            data-bs-toggle="modal"
            data-bs-target="#addEmbeddingModal1"
          >
            Add Embedding for {{ store.selectedPlaintexts.elements[0].name }}
          </button>

          <!-- Modal -->
          <div
            class="modal fade"
            id="addEmbeddingModal1"
            tabindex="-1"
            aria-labelledby="addEmbeddingModal1Label"
            aria-hidden="true"
          >
            <div class="modal-dialog">
              <div class="modal-content">
                <div class="modal-header">
                  <h5 class="modal-title" id="addEmbeddingModal1Label">
                    Generate Embedding
                  </h5>
                  <button
                    type="button"
                    class="btn-close"
                    data-bs-dismiss="modal"
                    aria-label="Close"
                  ></button>
                </div>
                <div class="modal-body">
		  <form>
		    <div class="form-group mb-3">
		      <label for="name">Name</label>
		      <input
			type="text"
			class="form-control"
			id="name"
			v-model="pt1embeddingForm.name"
		      />
		    </div>
		    <div class="form-group mb-3">
		      <label for="description">Description</label>
		      <input
			type="text"
			class="form-control"
			id="description"
			v-model="pt1embeddingForm.description"
		      />
		    </div>
		  </form>
		</div>
                <div class="modal-footer">
                  <button
                    type="button"
                    class="btn btn-secondary"
                    data-bs-dismiss="modal"
                  >
                    Close
                  </button>
                  <button
                    type="button"
                    class="btn btn-primary"
                    data-bs-dismiss="modal"
		    @click="generateEmbedding(pt1embeddingForm)"	
                  >
                    Generate
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="col-6">
        <!-- modal for adding embedding for embedding 1 -->
        <div class="d-flex justify-content-start">
          <!-- Button trigger modal -->
          <button
            type="button"
            class="btn btn-success"
            data-bs-toggle="modal"
            data-bs-target="#addEmbeddingModal2"
          >
            Add Embedding for {{ store.selectedPlaintexts.elements[1].name }}
          </button>

          <!-- Modal -->
          <div
            class="modal fade"
            id="addEmbeddingModal2"
            tabindex="-1"
            aria-labelledby="addEmbeddingModal2Label"
            aria-hidden="true"
          >
            <div class="modal-dialog">
              <div class="modal-content">
                <div class="modal-header">
                  <h5 class="modal-title" id="addEmbeddingModal2Label">
                    Generate Embedding
                  </h5>
                  <button
                    type="button"
                    class="btn-close"
                    data-bs-dismiss="modal"
                    aria-label="Close"
                  ></button>
                </div>
                <div class="modal-body">
		<form>
		    <div class="form-group mb-3">
		      <label for="name">Name</label>
		      <input
			type="text"
			class="form-control"
			id="name"
			v-model="pt2embeddingForm.name"
		      />
		    </div>
		    <div class="form-group mb-3">
		      <label for="description">Description</label>
		      <input
			type="text"
			class="form-control"
			id="description"
			v-model="pt2embeddingForm.description"
		      />
		    </div>
		  </form>
		</div>
                <div class="modal-footer">
                  <button
                    type="button"
                    class="btn btn-secondary"
                    data-bs-dismiss="modal"
                  >
                    Close
                  </button>
                  <button
                    type="button"
                    class="btn btn-primary"
                    data-bs-dismiss="modal"
		    @click="generateEmbedding(pt2embeddingForm)"
                  >
                    Generate
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped></style>
