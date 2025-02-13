<script setup>
import { ref, computed } from 'vue';
import { BFormRadioGroup, BButton } from 'bootstrap-vue-next';
const props = defineProps({
  stage: Number
});
defineEmits(['back', 'continue'])

const options = [
  { text: 'CC0 1.0 (Public Domain Dedication) Description Legal code ', value: 'first' },
  { text: 'CC BY 4.0 Description Legal code', value: 'second' },
  { text: 'CC BY-SA 4.0 Description Legal code', value: 'third' },
]

const selected = ref('first')
</script>
<template>
  <div v-if="props.stage == 2">
    <h2 class="alert-heading">
      Please choose a license
    </h2>
    <div class="d-flex flex-row justify-content-center">
      <BFormRadioGroup v-model="selected" :options="options" name="radio-stacked" stacked />
    </div>

    <div class="d-flex flex-row justify-content-between">
      <BButton @click="$emit('back')" variant="primary" size="lg">
        Back
      </BButton>
      <BButton @click="$emit('continue')" variant="primary" size="lg">
        Continue
      </BButton>
    </div>
  </div>
</template>
