<script setup>
import TabZero from "./components/TabZero.vue";
import TabOne from "./components/TabOne.vue";
import TabTwo from "./components/TabTwo.vue";
import TabThree from "./components/TabThree.vue";

import { ref, computed, onMounted, reactive } from "vue";

// current tab
const active_tab = ref(0);
// total tabs
const total_tabs = ref(4);
// plaintext files (for tab 1)
const ptexts = ref(null);
// selected plaintext 1
const pts1 = ref(null);
// selected plaintext 2
const pts2 = ref(null);
// selected plaintext 1 name
const pts1_name = ref(null);
// selected plaintext 2 name
const pts2_name = ref(null);
// all embeddings associated with the selected pt1
const e_s1 = ref(null);
// all embeddings associated with the selected pt2
const e_s2 = ref(null);
// selected embedding 1
const e_1 = ref(null);
// selected embedding 2
const e_2 = ref(null);
// selected alignments
const alignments = ref(null);
const tab0ready = computed(() => {
  return true;
});
const tab1ready = computed(() => {
  return ptexts.value !== null;
});
const tab2ready = computed(() => {
  return (
    pts1.value !== null &&
      pts2.value !== null &&
      e_1.value !== null &&
      e_2.value !== null,
    e_s1.value !== null && e_s2.value !== null
  );
});
const tab3ready = computed(() => {
  const r =  alignments.value != null;
  return r;
});
// initial api call
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
// get pt by id
function ptByPtId(id) {
  return ptexts.value.find((pt) => pt.id == id);
}

onMounted(() => {
  getPlainTexts();
});
function tab0hook() {}
function tab1hook() {}
function tab2hook() {
  // get embeddings for pt1

  // query the server for the embeddings for the selected plaintexts
  fetch("/api/getEmbeddings", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      pt_id: pts1.value,
    }),
  })
    .then((res) => res.json())
    .then((data) => {
      // set the embeddings to the data
      e_s1.value = data;
    });
  fetch("/api/getEmbeddings", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      pt_id: pts2.value,
    }),
  })
    .then((res) => res.json())
    .then((data) => {
      // set the embeddings to the data
      e_s2.value = data;
    });
}
function tab3hook() {
  fetch("/api/getAlignments", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      e1_id: e_1.value,
      e2_id: e_2.value,
    }),
  })
    .then((res) => res.json())
    .then((data) => {
      // set the alignments to the data alignments
      alignments.value = data.alignments;

    });
}

function setTab(i) {
  // set the active tab and call the loading function
  active_tab.value = i;
  switch (i) {
    case 0:
      console.log("opened tab0");
      tab0hook();
      break;
    case 1:
      console.log("opened tab1");
      tab1hook();
      break;
    case 2:
      console.log("opened tab2");
      tab2hook();
      break;
    case 3:
      console.log("opened tab3");
      tab3hook();
      break;
  }
}
// object to say if next is disabled
const nextDisabled = computed(() => ({
  disabled:
  // we are on tab one and haven't selected two plaintexts
    (active_tab.value === 1 && pts1.value === null) ||
    (active_tab.value === 1 && pts2.value === null) ||
    // we are on the last tab
    active_tab.value === total_tabs.value - 1 || 
    // we are on tab 2 and haven't selected two embeddings
    active_tab.value === 2 && e_1.value === null ||
    active_tab.value === 2 && e_2.value ===  null
}));
// object to say if prev is disabled
const prevDisabled = computed(() => ({
  disabled: active_tab.value === 0,
}));
</script>
<template>
  <div class="d-flex flex-column h-100">
    <div class="flex-shrink-0">
      <div class="container-xl pt-4">
        <nav class="navbar navbar-expand-lg navbar-light bg-light">
          <div class="container-fluid">
            <a class="navbar-brand" href="#">SenSE</a>
            <button
              class="navbar-toggler"
              type="button"
              data-bs-toggle="collapse"
              data-bs-target="#navbarNavAltMarkup"
              aria-controls="navbarNavAltMarkup"
              aria-expanded="false"
              aria-label="Toggle navigation"
            >
              <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNavAltMarkup">
              <div class="navbar-nav">
                <a
                  class="nav-link"
                  :class="{ active: active_tab === 0 }"
                  aria-current="page"
                  href="#!"
                  @click="setTab(0)"
                  >Home</a
                >
                <a
                  class="nav-link"
                  :class="{ active: active_tab === 1 }"
                  @click="setTab(1)"
                  href="#!"
                  >Datasets</a
                >
                <a
                  class="nav-link"
                  :class="{ active: active_tab === 2 }"
                  @click="setTab(2)"
                  href="#!"
                  >Embeddings</a
                >
                <a
                  class="nav-link"
                  :class="{ active: active_tab === 3 }"
                  @click="setTab(3)"
                  href="#!"
                  >Alignments</a
                >
              </div>
            </div>
          </div>
        </nav>
      </div>
      <div v-if="active_tab == 0">
        <div v-if="tab0ready">
          <TabZero />
        </div>
        <div v-else>
          <p>ERROR: tab0 should always be ready</p>
        </div>
      </div>
      <div v-if="active_tab == 1">
        <div v-if="tab1ready">
          <div class="container-xl mt-4">
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
                      'text-white': pt.id == pts1 || pt.id == pts2,
                      'bg-primary': pt.id == pts1 || pt.id == pts2,
                    }"
                    @click="
                      pts2 != pt.id && pts1 != pt.id
                        ? ([pts2, pts1] = [pts1, pt.id])
                        : pass
                    "
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
        </div>
        <div v-else>
          <p>Loading: tab1 not ready</p>
        </div>
      </div>
      <div v-if="active_tab == 2">
        <div v-if="tab2ready">
          <div class="container-xl mt-3">
            <div class="row">
              <div class="col-6">
                <h4>Embeddings for {{ ptByPtId(pts1).name }}</h4>
              </div>
              <div class="col-6">
                <h4>Embeddings for {{ ptByPtId(pts2).name }}</h4>
              </div>
            </div>
            <div class="row">
              <div class="col-6">
                <div class="list-group">
                  <a
                    v-for="e in e_s1"
                    :key="e.id"
                    class="list-group-item list-group-item-action"
                    @click="e_1 = e.id"
                    :class="{ active: e_1 == e.id }"
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
                    v-for="e in e_s2"
                    :key="e.id"
                    @click="e_2 = e.id"
                    :class="{ active: e_2 == e.id }"
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
        </div>
        <div v-else>
          <p>Tab2 not ready; did you make sure to select two plaintexts?</p>
        </div>
      </div>
      <div v-if="active_tab == 3">
        <TabThree v-if="tab3ready" :alignments="alignments" />
        <div v-else>
          <p>
            Tab3 not ready; you must select two embeddings to see their
            alignments.
          </p>
        </div>
      </div>
    </div>
    <div class="container-xl">
      <div class="row">
        <div class="col-12">
          <div class="d-flex justify-content-end">
            <button
              type="button"
              class="btn btn-secondary btn-lg"
              :class="prevDisabled"
              @click="setTab(Math.max(active_tab - 1, 0))"
            >
              Back
            </button>
            <button
              type="button"
              class="btn btn-primary btn-lg"
              :class="nextDisabled"
              @click="setTab(Math.min(active_tab + 1, total_tabs))"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>

    <footer class="footer mt-auto py-3 bg-light"></footer>
  </div>
</template>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
