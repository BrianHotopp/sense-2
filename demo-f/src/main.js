import { createApp } from 'vue'
import App from './App.vue'
// import echarts 
import ECharts from 'vue-echarts'
import { use } from "echarts/core"

// import ECharts modules manually to reduce bundle size
import {
    CanvasRenderer
  } from 'echarts/renderers'
  import {
    BarChart,
    PieChart,
    ScatterChart
  } from 'echarts/charts'
  import {
    TitleComponent,
    LegendComponent,
    GridComponent,
    TooltipComponent
  } from 'echarts/components'
  
  use([
    CanvasRenderer,
    BarChart,
    PieChart,
    GridComponent,
    TooltipComponent,
    TitleComponent,
    LegendComponent,
    ScatterChart
  ])

//import CSS Bootstrap
import 'bootstrap-icons/font/bootstrap-icons.css'
const app = createApp(App)
// register v chart component globally (or you can do it locally)
app.component('v-chart', ECharts)
app.mount('#app')
