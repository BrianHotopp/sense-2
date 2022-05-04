import { reactive } from "vue";
// exports some reactive configuration objects
// these contain defaults for generating embeddings for different embedding types
// currently only word2vec is supported
export const selectedEmbedding = reactive({
  embedding: "word2vec"
});
export const availableEmbeddings = reactive({
	"word2vec":{
		  "size": 100,
		  "window": 5,
		  "minCount": 5
	}
});
