<script setup lang="ts">

const props = defineProps({
  stage: Number,
});

const stages = [
  {
    name: "Information",
    icon: 'fa-circle-info'
  },
  {
    name: "Authors",
    icon: 'fa-users'
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
  <div id="progress" class="wizard-stepper mb-4">
    <ol class="d-flex justify-content-between align-items-center list-unstyled p-0 m-0">
      <li v-for="(s, index) in stages" :key="index"
          class="stepper-item d-flex align-items-center flex-fill"
          :class="{ 'active': (props.stage ?? 0) === index, 'completed': (props.stage ?? 0) > index }">
        <div class="stepper-badge rounded-circle d-flex align-items-center justify-content-center me-2 flex-shrink-0">
          <i v-if="(props.stage ?? 0) > index" class="fa-solid fa-check"></i>
          <i v-else-if="(props.stage ?? 0) === index" class="fa-solid" :class="s.icon"></i>
          <span v-else class="fw-semibold">{{ index + 1 }}</span>
        </div>
        <div class="stepper-text d-none d-md-block">
          <div class="stepper-title fw-semibold">{{ s.name }}</div>
          <div class="stepper-subtitle text-muted small">Step {{ index + 1 }} of 4</div>
        </div>
        <div v-if="index < stages.length - 1" class="stepper-line flex-fill mx-3"></div>
      </li>
    </ol>
  </div>
</template>

<style scoped>
.wizard-stepper {
  padding: 1rem 0.5rem;
}
.stepper-badge {
  width: 2.5rem;
  height: 2.5rem;
  border: 2px solid var(--bs-border-color, #dee2e6);
  background-color: var(--bs-body-bg, #ffffff);
  color: var(--bs-secondary-color, #6c757d);
  transition: all 0.3s ease-in-out;
  font-size: 0.9rem;
}
.stepper-item.active .stepper-badge {
  border-color: #0d6efd;
  background-color: #e7f1ff;
  color: #0d6efd;
  box-shadow: 0 0 0 4px rgba(13, 110, 253, 0.15);
}
.stepper-item.completed .stepper-badge {
  border-color: #198754;
  background-color: #198754;
  color: #ffffff;
}
.stepper-title {
  font-size: 0.95rem;
  color: var(--bs-body-color, #212529);
}
.stepper-item.active .stepper-title {
  color: #0d6efd;
}
.stepper-item.completed .stepper-title {
  color: #198754;
}
.stepper-line {
  height: 3px;
  background-color: var(--bs-border-color, #e9ecef);
  border-radius: 2px;
  transition: background-color 0.4s ease-in-out;
}
.stepper-item.completed .stepper-line {
  background-color: #198754;
}
</style>
