<script setup>
import { ref, onMounted } from "vue";
import { store } from "../../store.js";
import { shiftPush } from "../../Queue.js";
const ptexts = ref(null);
const file_is_uploading = ref(false);
const upload_succeeded = ref(false);
function getPlainTexts() {
  fetch("/api/getPlainTexts", {
    method: "GET",
    headers: {},
  })
    .then((res) => res.json())
    .then((data) => {
      // set the plaintexts to the data
      ptexts.value = data;
    });
}
onMounted(() => {
  getPlainTexts();
});
function ptClick(pt_id, pt_name) {
  shiftPush(store.selectedPlaintexts, { id: pt_id, name: pt_name }, 2);
  // deselect embeddings and alignments
  store.selectedEmbeddings.elements = [];
  store.selectedAlignments.elements = [];
  store.selectedWord = null;
}
const chosenFile = ref(null);
const newPtData = ref({ name: null, description: null });
function onFileChange(e) {
  var files = e.target.files || e.dataTransfer.files;
  if (!files.length) return;
  chosenFile.value = files[0];
}
async function setFalseAfterDelay(item, delay) {
  setTimeout(() => {
    item.value = false;
  }, delay);
}
async function fileUpload() {
  var formData = new FormData();
  formData.append("file", chosenFile.value);
  formData.append("data", JSON.stringify(newPtData.value));
  file_is_uploading.value = true;
  await fetch("/api/uploadFile", {
    method: "POST",
    body: formData,
  })
    .then((res) => res.json())
    .then((data) => {
      // error handling
      if (data.error) {
        console.log("Failed to upload the file");
        console.log(data.error);
        return;
      }
    });
  file_is_uploading.value = false;
  getPlainTexts();
  upload_succeeded.value = true;
  setFalseAfterDelay(upload_succeeded, 3000);
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
              'text-white': store.selectedPlaintexts
                .map((pt) => pt.id)
                .includes(pt.id),
              'bg-primary': store.selectedPlaintexts
                .map((pt) => pt.id)
                .includes(pt.id),
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
    <div class="row">
      <div class="col-12 mb-4">
        <div class="d-flex justify-content-end">
          <!-- Button trigger modal -->
          <button
            type="button"
            class="btn btn-success"
            data-bs-toggle="modal"
            data-bs-target="#addPlaintextModal"
          >
            Add New Plaintext
          </button>

          <!-- Modal -->
          <div
            class="modal fade"
            id="addPlaintextModal"
            tabindex="-1"
            aria-labelledby="addPlaintextModalLabel"
            aria-hidden="true"
          >
            <div class="modal-dialog">
              <div class="modal-content">
                <div class="modal-header">
                  <h5 class="modal-title" id="addPlaintextModalLabel">
                    Add Dataset 
                  </h5>
                  <button
                    type="button"
                    class="btn-close"
                    data-bs-dismiss="modal"
                    aria-label="Close"
                  ></button>
                </div>
                <div class="modal-body">
                  <div class="input-group mb-3">
                    <input
                      type="file"
                      class="form-control"
                      id="inputGroupFile02"
                      v-on:change="onFileChange"
                    />
                    <!-- inputs for the plaintext name and description -->
                  </div>
                  <input
                    type="text"
                    class="form-control mb-3"
                    placeholder="Plaintext Name"
                    v-model="newPtData.name"
                  />
                  <input
                    type="text"
                    class="form-control mb-3"
                    placeholder="Plaintext Description"
                    v-model="newPtData.description"
                  />
                  <div
                    v-if="file_is_uploading"
                    class="alert alert-secondary"
                    role="alert"
                  >
                    File is uploading...
                  </div>
                  <div
                    v-if="upload_succeeded"
                    class="alert alert-success"
                    role="alert"
                  >
		  Plaintext Upload Successful
                  </div>
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
                    @click="fileUpload()"
                  >
                    Upload
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
