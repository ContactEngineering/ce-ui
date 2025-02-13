<script setup>
const props = defineProps({
  stage: Number,
});

function highlight(n) {
  if (n == props.stage) {
    return "text-primary";
  }
  else if (n < props.stage) {
    return "text-success";
  }
  else {
    return "text-muted";
  }
}
</script>
<template>
  <h3>Publish</h3>
  <div id="progress" class="d-flex flex-row justify-content-evenly">
    <div class="d-flex flex-column align-items-center" :class="highlight(0)">
      <span class="fa-stack fa-lg">
        <i class="fa-regular fa-circle fa-stack-2x"></i>
        <i class="fa-solid fa-info fa-stack-1x"></i>
      </span>
      <span>
        Publish warning
      </span>
    </div>
    <div class="d-flex flex-column align-items-center" :class="highlight(1)">
      <span class="fa-stack fa-lg">
        <i class="fa-regular fa-circle fa-stack-2x"></i>
        <i class="fa-solid fa-users-rectangle fa-stack-1x"></i>
      </span>
      <span class="text-muted">
        Authors
      </span>
    </div>
    <div class="d-flex flex-column align-items-center" :class="highlight(2)">
      <span class="fa-stack fa-lg">
        <i class="fa-regular fa-circle fa-stack-2x"></i>
        <i class="fa-solid fa-scale-balanced fa-stack-1x"></i>
      </span>
      <span class="text-muted">
        License
      </span>
    </div>
    <div class="d-flex flex-column align-items-center" :class="highlight(3)">
      <span class="fa-stack fa-lg">
        <i class="fa-regular fa-circle fa-stack-2x"></i>
        <i class="fa-regular fa-paper-plane fa-stack-1x"></i>
      </span>
      <span class="text-muted">
        Submit
      </span>
    </div>
  </div>
</template>
