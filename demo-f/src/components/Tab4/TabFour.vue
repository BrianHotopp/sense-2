<script setup>
import { ref, onMounted, watchEffect, computed, watch } from "vue";
import MostShifted from "./MostShifted.vue";
import { store } from "../../store.js";
const display = ref([]);
const numWords = ref(20);
const props = defineProps(["selectedAlignments"]);
const emit = defineEmits(["nextTab"]);
const filtertype = ref("all");
const shown_filtered_words = ref([]);
function chunkArray(myArray, chunk_size) {
  var index = 0;
  var arrayLength = myArray.length;
  var tempArray = [];
  for (index = 0; index < arrayLength; index += chunk_size) {
    var myChunk = myArray.slice(index, index + chunk_size);
    // Do something if you want with the group
    tempArray.push(myChunk);
  }
  return tempArray;
}
const chunkedArray = computed(() => {
  return chunkArray(display.value, 3);
});
watchEffect(async () => {
  // if numwords is between 1 and 100, don't do anything
  if (numWords.value < 1 || numWords.value > 100) {
    return;
  }
  // if numwords is not an integer, don't do anything
  if (numWords.value % 1 !== 0) {
    return;
  }
  const promises = props.selectedAlignments.map(async (al) => {
    const ret = await fetch("/api/getTopShiftedWords", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        id: al.id,
        num_words: numWords.value,
      }),
    }).then((res) => res.json());
    // error handling
    if (ret.error) {
      console.log(ret.error);
      return [];
    }
    return ret;
  });
  const data = await Promise.all(promises);
  display.value = props.selectedAlignments.map((al, i) => {
    return {
      id: al.id,
      name: al.name,
      words: data.find((d) => d.alignment_id === al.id).shifted_words,
      unionWords: [],
    };
  });
  // attach the union of the other alignment's words to the element for the current alignment
  display.value.forEach((al, i) => {
    // union the other alignment's words to the element for the current alignment
    display.value.forEach((other_al, j) => {
      if (i != j) {
        const o_words = other_al.words.map((w) => w[0]);
        al.unionWords = al.unionWords.concat(o_words);
      }
    });
  });
});
function selectWord(word) {
  store.selectedWord = word;
  emit("nextTab", 5);
}
function filter(type) {
  filtertype.value = type;
}
// computed for common words
const common_words = computed(() => {
  const per_al_type = display.value.map((al) => {
    return al.words.map((word) => {
      return word[0];
    });
  });
  // get the words common to all alignment types
  const common_words = per_al_type[0].filter((word) => {
    return per_al_type.every((al) => {
      return al.includes(word);
    });
  });
  return common_words;
});
</script>

<template>
  <div class="container-xl mb-3">
    <div class="row mb-3 text-start">
      <div class="col">
        <form>
          <div class="form-group">
            <label class="mb-3" for="numWords"
              >Number of words to display:</label
            >
            <input
              type="number"
              min="1"
              max="100"
              class="form-control"
              id="numWords"
              v-model="numWords"
              @click.prevent
            />
          </div>
        </form>
      </div>
    </div>
    <div class="row">
      <div class="col-1 text-start">
        <p>Filters:</p>
      </div>
    </div>
    <div class="row mb-3 align-items-center">
      <div class="col-1">
        <div
          class="btn-group"
          role="group"
          aria-label="Basic mixed styles example"
        >
          <button
            type="button"
            class="btn btn-danger"
            @click="filter('all')"
            :class="{ active: filtertype == 'all' }"
          >
            None
          </button>
          <button
            type="button"
            class="btn btn-warning"
            @click="filter('common')"
            :class="{ active: filtertype == 'common' }"
          >
            Common
          </button>
          <button
            type="button"
            class="btn btn-success"
            @click="filter('unique')"
            :class="{ active: filtertype == 'unique' }"
          >
            Unique
          </button>
        </div>
      </div>
    </div>
    <div v-for="triple in chunkedArray" class="row mb-3">
      <div v-for="alignment in triple" class="col-4">
        <MostShifted
          :alignmentName="alignment.name"
          :words="alignment.words"
          :filter-type="filtertype"
          :common-words="common_words"
          :union-words="alignment.unionWords"
          @select-word="selectWord"
        />
      </div>
    </div>
  </div>
</template>

<style scoped></style>
