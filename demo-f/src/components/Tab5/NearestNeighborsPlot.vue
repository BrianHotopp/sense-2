<script setup>
import { ref, computed } from "vue";
const props = defineProps(["word", "neighborWords", "neighborCoords", "context1", "context2"]);
const option = computed(() => {
  const tdata = props.neighborCoords.map((v, i) =>
    v.concat(props.neighborWords[i][0])
  );
  const cdata = tdata.slice(0, -1);
  const wdata = tdata.slice(-1);
  return {
    xAxis: {},
    yAxis: {},
    tooltip: {
      trigger: "item",
      formatter: function (param) {
        return param.data[2];
      },
    },
    legend: {
    type: "plain",
    bottom: 10,
    left:30,
    selectedMode: false,
    },
    series: [
      {

        symbolSize: 15,
        data: wdata,
	name: props.context1,
        type: "scatter",
        label: {
          show: true,
          position: "right",
          minMargin: 3,
          formatter: function (param) {
            return param.data[2];
          },
        },
      },
      {
        symbolSize: 15,
        data: cdata,
	name: props.context2,
        type: "scatter",
        label: {
          show: true,
          position: "right",
          minMargin: 3,
          formatter: function (param) {
            return param.data[2];
          },
        },
      },
    ],
  };
});
</script>

<template>
  <div>
    <v-chart class="chart" style="height: 400px" :option="option" />
  </div>
</template>

<style scoped></style>
