<script setup>

import {BNavbar, BNavbarNav, BNavItem, BOffcanvas} from "bootstrap-vue-next";

const visible = defineModel("visible");

const props = defineProps({
  apiUrl: String,
  name: String,
  orcid: String,
  isStaff: Boolean
});

</script>

<template>
  <BNavbar fixed="top">
    <BOffcanvas v-model="visible" placement="end">
      <h3 class="text-center">{{ name }}</h3>
      <h5 class="text-center"><a :href="`https://orcid.org/${orcid}`">{{ orcid }}</a></h5>

      <BNavbarNav class="justify-content-end flex-grow-1 pe-3 mb-3">
        <BNavItem href="">User profile</BNavItem>
      </BNavbarNav>
      <BNavbarNav v-if="isStaff" class="justify-content-end flex-grow-1 pe-3 mb-3">
        <BNavItem href="">Admin interface</BNavItem>
        <BNavItem href="">Watchman dashboard</BNavItem>
        <BNavItem href="">Watchman status (JSON)</BNavItem>
      </BNavbarNav>
      <BNavbarNav class="justify-content-end flex-grow-1 pe-3 mb-3">
        <BNavItem>Version information</BNavItem>
        <BNavItem href="">Terms &amp; conditions</BNavItem>
        <BNavItem href="">Help</BNavItem>
        <BNavItem href="https://github.com/ContactEngineering/TopoBank/discussions">Feedback</BNavItem>
        <BNavItem>Contact</BNavItem>
        <BNavItem href="https://doi.org/10.1088/2051-672X/ac860a">Read our paper!</BNavItem>
      </BNavbarNav>
      <BNavbarNav class="justify-content-end flex-grow-1 pe-3">
        <BNavItem>Sign out</BNavItem>
      </BNavbarNav>
    </BOffcanvas>
  </BNavbar>
</template>