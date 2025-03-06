<script setup>

import axios from "axios";
import {computed, inject, onMounted, ref} from "vue";

import {
  BForm,
  BFormCheckbox,
  BFormCheckboxGroup,
  BFormGroup,
  BToastOrchestrator
} from "bootstrap-vue-next";

import {subjectsFromBase64} from "../utils/api";

const props = defineProps({
  apiRegistryUrl: {
    type: String,
    default: '/analysis/api/workflow/'
  },
  subjects: String
});

const appProps = inject("appProps");

const _activeCards = ref(new Set([]));  // Cards that are active, i.e. have data loaded
const _cards = ref([]);
const _visibleCards = ref([]);  // Cards that are visible

function getSubjectsDict() {
  let subjects = appProps.searchParams.get("subjects");
  if (props.subjects != null) {
    subjects = props.subjects;
  }
  if (subjects != null) {
    return subjectsFromBase64(subjects);
  }
  return null;
}

const subjectsDict = computed(() => {
  return getSubjectsDict();
});

onMounted(() => {
  //const visibleCards = $cookies.get("topobank-visible-cards");
  const visibleCards = null;
  _visibleCards.value = visibleCards === null ? [] : visibleCards;
  _activeCards.value = new Set(_visibleCards.value);
  //const subjects = JSON.parse(atob(props.subjects));
  let queryParams = '';
  /*
  if (Object.entries(subjects).length === 1) {
      queryParams = '?subject_type=' + Object.keys(subjects)[0];
  }
  */
  axios.get(`${props.apiRegistryUrl}${queryParams}`).then(response => {
    _cards.value = response.data;
  });
});

function updateSelection() {
  //$cookies.set("topobank-visible-cards", _visibleCards.value);
  for (const id of _visibleCards.value) {
    _activeCards.value.add(id);
  }
}

</script>

<template>
  <BToastOrchestrator/>
  <div class="row mb-2">
    <b-form class="col-12">
      <b-form-group>
        <b-form-checkbox-group v-model="_visibleCards">
          <b-form-checkbox v-for="card in _cards"
                           :key="card.id"
                           :value="card.id"
                           @change="updateSelection">
            {{ card.display_name }}
          </b-form-checkbox>
        </b-form-checkbox-group>
      </b-form-group>
    </b-form>
  </div>
  <div class="row">
    <div v-for="card in _cards"
         :key="card.id"
         :class="{ 'col-lg-6': true, 'mb-4': true, 'd-none': !_visibleCards.includes(card.id) }">
      <component :is="`${card.visualization_type}-card`"
                 v-if="_activeCards.has(card.id)"
                 :enlarged="false"
                 :function-id="card.id"
                 :function-name="card.name"
                 :subjects="subjectsDict">
      </component>
    </div>
  </div>
</template>
