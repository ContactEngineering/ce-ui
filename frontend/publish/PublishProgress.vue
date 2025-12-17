<script setup lang="ts">

const props = defineProps({
  stage: Number,
});

const stages = [
  {
    name: "Information",
    icon: 'info'
  },
  {
    name: "Authors",
    icon: 'group'
  },
  {
    name: "License",
    icon: 'balance'
  },
  {
    name: "Submit",
    icon: 'send'
  }
];
</script>

<template>
  <div id="progress" class="flex row justify-center">
    <div v-for="stage in [0, 1, 2, 3]" :key="stage" class="flex row items-center">
      <div class="progress-step" style="transition-property: color; transition-delay: 1s;"
        :style="stage < props.stage ? 'color: oklch(0.627 0.194 149.214);' : (stage == props.stage ? 'color: oklch(0.546 0.245 262.881);' : 'color: oklch(0.872 0.01 258.338);')">
        <div class="progress-icon-wrapper">
          <q-icon name="circle" size="3rem" class="progress-circle" />
          <q-icon :name="stages[stage].icon" size="1.25rem" class="progress-inner-icon" />
        </div>
        <span class="progress-label">
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

<style scoped>
.progress-step {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.progress-icon-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.progress-circle {
  opacity: 0.3;
}

.progress-inner-icon {
  position: absolute;
}

.progress-label {
  position: absolute;
  top: 100%;
  white-space: nowrap;
  padding-top: 0.75rem;
}
</style>
