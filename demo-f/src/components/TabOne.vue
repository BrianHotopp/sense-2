<script setup>
import { ref, onMounted } from 'vue';
const ptexts = ref(null);
const pts1 = ref(null);
const pts2 = ref(null);
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
</script>

<template>
<div class="container-xl mt-4">
      <div class="row" >
        <div class="col mb-4" v-for="pt in ptexts" :key="pt.id" >
          <a
            href="#"
            class="list-group-item-action"
            style="text-decoration: none"
            @click="$emit('ptClicked', pt.id)"
          >
            <div class="card" :class="{'text-white': pt.id == pts1 || pt.id == pts2, 'bg-primary':pt.id == pts1 || pt.id== pts2}" @click="pts2 != pt.id && pts1 != pt.id ? [pts2, pts1]=[pts1, pt.id]: pass">
              <div class="card-header">
                <h6>
                    {{pt.id}}
                  {{ pt.name }}
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
a {
}
</style>
