<script setup>
import { BButton } from 'bootstrap-vue-next';
const props = defineProps({
  stage: Number
});
defineEmits(['continue'])
</script>
<template>
  <div v-if="props.stage == 0">
    <div class="alert alert-danger mt-5">
      <h4>
        You are about to publish your digital surface twin Digital surface twin #1
      </h4>

      By publishing, you create an <strong>immutable copy</strong> of this digital twin as a snapshot with all its
      data.<br>
      This snapshot has a version number and a unique URL for citations and it is visible and usable for everyone.
    </div>

    <div class="d-flex flex-row justify-content-end">
      <BButton @click="$emit('continue')" variant="primary" size="lg">
        Continue
      </BButton>
    </div>
  </div>
</template>
