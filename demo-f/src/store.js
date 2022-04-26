import { reactive } from 'vue'
import { Queue } from "./Queue.js";
export const store = reactive({
    selectedPlaintexts: new Queue(),
    selectedEmbeddings: {forPt1: new Queue(), forPt2: new Queue()},
    selectedAlignments: new Queue(),
    selectedWord: null,
})
