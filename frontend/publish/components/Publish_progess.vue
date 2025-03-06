<script setup>
const props = defineProps({
  stage: Number,
});

const stages = [
  {
    name: "Publish warning",
    icon: 'fa-info'
  },
  {
    name: "Authors",
    icon: 'fa-users-rectangle'
  },
  {
    name: "License",
    icon: 'fa-scale-balanced'
  },
  {
    name: "Submit",
    icon: 'fa-paper-plane'
  }
];

</script>
<template>
  <h3>Publish</h3>
  <div id="progress" class="d-flex flex-row justify-content-center">
    <div v-for="stage in [0, 1, 2, 3]" class="d-flex flex-row align-items-center">
      <div class="position-relative" style="transition-property: color; transition-delay: 1s;"
        :style="stage < props.stage ? 'color: oklch(0.627 0.194 149.214);' : (stage == props.stage ? 'color: oklch(0.546 0.245 262.881);' : 'color: oklch(0.872 0.01 258.338);')">
        <span class="fa-stack fa-lg">
          <i class="fa-regular fa-circle fa-stack-2x"></i>
          <i class="fa-solid fa-stack-1x" :class="stages[stage].icon"></i>
        </span>
        <span class="position-absolute top-100 start-50 translate-middle text-nowrap pt-3">
          {{ stages[stage].name }}
        </span>
      </div>

      <div v-if="stage != 3" :style="{ width: stage < props.stage ? '120px' : '0px' }"
        style="height: 10px; transition: width 1s ease-in-out; background-color: oklch(0.627 0.194 149.214);">
      </div>
      <div v-if="stage != 3" :style="{ width: stage < props.stage ? '0' : '120px' }"
        style="height: 10px; transition: width 1s ease-in-out; background-color: oklch(0.872 0.01 258.338);">
      </div>
    </div>
  </div>
</template>
