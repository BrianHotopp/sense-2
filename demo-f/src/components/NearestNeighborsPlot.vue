<script setup>
import { ref } from 'vue'
const props = defineProps(
    ["word", "neighborWords", "neighborCoords"]
)
console.log(props.neighborCoords) 
const tdata = props.neighborCoords.map((v, i)=>v.concat(props.neighborWords[i].neighbor))
const option = ref(
  {
  xAxis: {},
  yAxis: {},
  tooltip: {
      trigger: "item",
        formatter: function (param) {

          return param.data[2];
        },
},
  series: [
    {
      symbolSize: 15,
      data: tdata,
      type: 'scatter',
      label: {
        show: true,
        position: 'right',
        minMargin: 3,
        formatter: function (param) {
          return param.data[2];
        },
      }
    }
  ]
}
);
const count = ref(0)
</script>

<template>
<div>
<v-chart class="chart" style="height: 400px; width: 100%;" :option="option" />
</div>
</template>

<style scoped>
</style>
