<script setup>
import TabZero from "./components/Tab0/TabZero.vue";
import TabOne from "./components/Tab1/TabOne.vue";
import TabTwo from "./components/Tab2/TabTwo.vue";
import TabThree from "./components/Tab3/TabThree.vue";
import TabFour from "./components/Tab4/TabFour.vue";
import TabFive from "./components/Tab5/TabFive.vue";
import TabSix from "./components/Tab6/TabSix.vue";
import {store} from "./store.js";
import { ref, computed } from "vue";
const active_tab = ref(0);
const total_tabs = ref(7);
function setTab(i) {
  active_tab.value = i;
}
// true if tab zero is disabled
const tab_zero_disabled = computed(() => (false));
// true if tab one is disabled
const tab_one_disabled = computed(() => (false));
// true if tab two is disabled
const tab_two_disabled = computed(() => (
  store.selectedPlaintexts.length < 2
));
// true if tab three is disabled
const tab_three_disabled = computed(() => (
  store.selectedEmbeddings.forPt1.length < 1 || store.selectedEmbeddings.forPt2.length < 1
));
// true if tab four is disabled
const tab_four_disabled = computed(() => (
 store.selectedAlignments.length < 1
 ));
// true if tab five is disabled
const tab_five_disabled = computed(() => (
  store.selectedAlignments.length < 1
));
// true if tab six is disabled
const tab_six_disabled = computed(() => (
  store.selectedAlignments.length < 1
));
// true if next is disabled
const nextDisabled = computed(() => (
  {
  disabled:
    // we are on tab one and haven't selected two plaintexts
    (active_tab.value === 1 && store.selectedPlaintexts.length < 2) || 
    // we are on tab 2 and haven't selected two embeddings
    (active_tab.value === 2 && (store.selectedEmbeddings.forPt1.length < 1 || store.selectedEmbeddings.forPt2.length < 1)) || 
    // we are on tab 3 and we haven't selected at least one alignment
    (active_tab.value === 3 && store.selectedAlignments.length < 1) ||
    // we are on the last tab
    active_tab.value === total_tabs.value - 1  
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
        <nav class="navbar navbar-expand-lg navbar-light bg-light mb-3">
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
              <ul class="navbar-nav">
                <li class="nav-item">
                  <a
                    class="nav-link"
                    :class="{ active: active_tab === 0, disabled: tab_zero_disabled }"
                    aria-current="page"
                    href="#"
                    @click="setTab(0)"
                    >Home</a
                  >
                </li>
                <li class="nav-item">
                  <a
                    class="nav-link"
                    :class="{ active: active_tab === 1, disabled: tab_one_disabled }"
                    @click="setTab(1)"
                    href="#"
                    >Datasets</a
                  >
                </li>
                <li class="nav-item">
                  <a
                    class="nav-link"
                    :class="{ active: active_tab === 2, disabled: tab_two_disabled }"
                    @click="setTab(2)"
                    href="#"
                    >Embeddings</a
                  >
                </li>
                <li class="nav-item">
                  <a
                    class="nav-link"
                    :class="{ active: active_tab === 3, disabled: tab_three_disabled }"
                    @click="setTab(3)"
                    href="#"
                    >Alignments</a
                  >
                </li>
<li class="nav-item">
                  <a
                    class="nav-link"
                    :class="{ active: active_tab === 4, disabled: tab_four_disabled }"
                    @click="setTab(4)"
                    href="#"
                    >Most Shifted</a
                  >
                </li>
<li class="nav-item">
                  <a
                    class="nav-link"
                    :class="{ active: active_tab === 5, disabled: tab_five_disabled }"
                    @click="setTab(5)"
                    href="#"
                    >Nearest Neighbors</a
                  >
                </li>
<li class="nav-item">
                  <a
                    class="nav-link"
                    :class="{ active: active_tab === 6, disabled: tab_six_disabled }"
                    @click="setTab(6)"
                    href="#"
                    >Sentences</a
                  >
                </li>
              </ul>
            </div>
          </div>
        </nav>
      </div>
      <TabZero v-if="active_tab == 0" />
      <TabOne
        v-if="active_tab == 1"
      />
      <TabTwo
        v-if="active_tab == 2"
      />
      <TabThree
        v-if="active_tab == 3"
      />
      <TabFour v-if="active_tab == 4" :selected-alignments="store.selectedAlignments" @next-tab="setTab"/>
      <TabFive v-if="active_tab == 5" :selected-alignments="store.selectedAlignments"/>
      <TabSix v-if="active_tab == 6" :selected-alignments="store.selectedAlignments"/>
      <div class="container-xl mb-3">
        <div class="row">
          <div class="col-12">
            <div class="d-flex justify-content-end">
              <button
                type="button"
                class="btn btn-secondary btn-lg me-md-2"
                :class="prevDisabled"
                @click.prevent="setTab(Math.max(active_tab - 1, 0))"
              >
                Back
              </button>
              <button
                type="button"
                class="btn btn-primary btn-lg"
                :class="nextDisabled"
                @click.prevent="setTab(Math.min(active_tab + 1, total_tabs))"
              >
                Next
              </button>
            </div>
          </div>
        </div>
      </div>
      <footer class="footer mt-auto py-3 bg-light"></footer>
    </div>
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
