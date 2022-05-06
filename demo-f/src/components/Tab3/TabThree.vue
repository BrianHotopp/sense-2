<script setup>
import { ref, onMounted, reactive } from "vue";
import { store } from "../../store.js";
import { togglePush } from "../../Queue.js";
const alignments = ref(null);
import { availableAlignments, selectedAlignment} from "../../alignmentConfigs.js";	
import AlignmentSettings from "./AlignmentSettings.vue";

const alignmentForm = ref({
 e1_id: store.selectedEmbeddings.forPt1.elements[0].id,
 e2_id: store.selectedEmbeddings.forPt2.elements[0].id,
 name: null,
 description: null,
 alignmentType: null,
 settings: null
});
function generateAlignment(){
// error check name and description
if(alignmentForm.value.name == null || alignmentForm.value.description == null){
	alert("Please enter a name and description for your alignment.");
	return;
}
	alignmentForm.value.alignmentType = selectedAlignment.alignmentType;
	alignmentForm.value.settings = availableAlignments[selectedAlignment.alignmentType];
	fetch("/api/generateAlignment", {
		method: "POST",
		body: JSON.stringify(alignmentForm.value),
		headers: {
			"Content-Type": "application/json"
		}
	}).then(res => res.json()).then(res => {
	getAlignments();
	});
}
function getAlignments() {
  fetch("/api/getAlignments", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      e1_id: store.selectedEmbeddings.forPt1.elements[0].id,
      e2_id: store.selectedEmbeddings.forPt2.elements[0].id,
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
    <div class="row mb-4">
    <div class="col-12">
      <div class="d-flex justify-content-end">
          <!-- Button trigger modal -->
          <button
            type="button"
            class="btn btn-success"
            data-bs-toggle="modal"
            data-bs-target="#addAlignmentModal"
          >
            Add Alignment for embeddings
          </button>

          <!-- Modal -->
          <div
            class="modal fade"
            id="addAlignmentModal"
            tabindex="-1"
            aria-labelledby="addAlignmentModalLabel"
            aria-hidden="true"
          >
            <div class="modal-dialog">
              <div class="modal-content">
                <div class="modal-header">
                  <h5 class="modal-title" id="addAlignmentModalLabel">
                   Generate Alignment 
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
		      <label class="d-flex justify-content-start" for="name">Name</label>
		      <input
			type="text"
			class="form-control"
			id="name"
			v-model="alignmentForm.name"
		      />
		    </div>
		    <div class="form-group mb-3">
		      <label class="d-flex justify-content-start" for="description">Description</label>
		      <input
			type="text"
			class="form-control"
			id="description"
			v-model="alignmentForm.description"
		      />
		    </div>
		    <div class="form-group mb-3">
		   	<AlignmentSettings></AlignmentSettings>
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
		    @click="generateAlignment(alignmentForm)"	
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

<style scoped>
a {
}
</style>
