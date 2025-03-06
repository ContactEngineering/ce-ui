<script setup>
import { ref, computed } from 'vue';
import axios from "axios";
import PublishStage1 from './components/Publish_stage_1.vue';
import PublishStage2 from './components/Publish_stage_2.vue';
import PublishStage3 from './components/Publish_stage_3.vue';
import PublishStage4 from './components/Publish_stage_4.vue';
import ProgessBar from './components/Publish_progess.vue';

const props = defineProps({
  user: Object,
  surfaceId: Number
});

const stage = ref(0);

let authors;
let license;

function publish() {
  axios.post('/publication/publish/', {
    'surface': props.surfaceId,
    'authors': authors,
    'license': license
  })
}

</script>
<template>
  <div class="container">
    <ProgessBar :stage="stage" />
    <div class="p-5">
      <PublishStage1 :stage="stage" :surfaceId="surfaceId" @continue="stage = 1"></PublishStage1>
      <PublishStage2 :stage="stage" :user="props.user" @continue="(emitedAuthors) => {
        authors = emitedAuthors;
        stage = 2;
      }" @back="stage = 0"></PublishStage2>
      <PublishStage3 :stage="stage" @continue="(emitedLicense) => {
        license = emitedLicense;
        stage = 3;
      }" @back="stage = 1"></PublishStage3>
      <PublishStage4 :stage="stage" @back="stage = 2" @publish="publish()"></PublishStage4>
    </div>
  </div>
</template>
