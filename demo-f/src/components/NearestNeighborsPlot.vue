<script setup>
import { ref, computed } from 'vue'
const props = defineProps(
    ["word", "neighborWords", "neighborCoords"]
)
const option = computed(
()=>{
const tdata = props.neighborCoords.map((v, i)=>v.concat(props.neighborWords[i][0]))
return {
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

}
)
</script>

<template>
<div>
<v-chart class="chart" style="height: 400px;" :option="option" />
</div>
</template>

<style scoped>
</style>
