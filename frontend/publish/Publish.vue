<script setup>
import { ref, computed } from 'vue';
import PublishStage1 from './Publish_stage_1.vue';
import PublishStage2 from './Publish_stage_2.vue';
import PublishStage3 from './Publish_stage_3.vue';
import PublishStage4 from './Publish_stage_4.vue';
import ProgessBar from './Publish_progess.vue';

const props = defineProps({
  configured_for_doi_generation: Boolean,
  user: Object
});

const stage = ref(3);

</script>
<template>
  <div class="container">
    <ProgessBar :stage="stage" />
    <div class="p-5">
      <PublishStage1 :stage="stage" :configured_for_doi_generation="props.configured_for_doi_generation"
        @continue="stage = 1"></PublishStage1>
      <PublishStage2 :stage="stage" :user="props.user" @continue="stage = 2" @back="stage = 0"></PublishStage2>
      <PublishStage3 :stage="stage" @continue="stage = 3" @back="stage = 1"></PublishStage3>
      <PublishStage4 :stage="stage" @back="stage = 2"></PublishStage4>
    </div>
  </div>
</template>
