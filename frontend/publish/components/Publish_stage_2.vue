<script setup>
import { ref, computed } from 'vue';
import { BCard, BCardBody, BButton, BButtonGroup, BFormInput, BAlert, BFormRadioGroup, BFormCheckbox } from 'bootstrap-vue-next';

const props = defineProps({
  stage: Number,
  user: Object
});
const emit = defineEmits(['back', 'continue'])


const authors = ref(
  [
    { firstName: "", lastName: "", orcidId: "" },
  ]);

// TODO: Affiliations

const valid = ref([{ firstName: null, lastName: null, orcidId: null }]);

function fillAuthor(index) {
  authors.value[index] = { ...props.user };
}

function addAuthor() {
  authors.value.push({ firstName: "", lastName: "", orcidId: "" });
  valid.value.push({ firstName: null, lastName: null, orcidId: null });
}

function removeAuthor(index) {
  authors.value.splice(index, 1);
  valid.value.splice(index, 1);
}

function moveAuthorUp(index) {
  if (index > 0) {
    const tmp = authors.value[index];
    authors.value[index] = authors.value[index - 1];
    authors.value[index - 1] = tmp;
  }
}

function moveAuthorDown(index) {
  if (index < authors.value.length - 1) {
    const tmp = authors.value[index];
    authors.value[index] = authors.value[index + 1];
    authors.value[index + 1] = tmp;

  }
}

const orcidIdRegex = new RegExp("\\d{4}-\\d{4}-\\d{4}-\\d{4}");;
function check_validity() {
  let is_valid = true;
  authors.value.forEach((author, index) => {
    valid.value[index].firstName = author.firstName != "";
    valid.value[index].lastName = author.lastName != "";
    valid.value[index].orcidId = author.orcidId === "" || orcidIdRegex.test(author.orcidId);
    is_valid = is_valid && valid.value[index].firstName && valid.value[index].lastName && valid.value[index].orcidId;
  })
  return is_valid;
}

function nextStage() {
  if (!check_validity()) {
    return;
  }
  emit('continue');
}


const authors_string = computed(() => {
  return authors.value.map((author) => `${author.firstName} ${author.lastName}`).join(", ");
})
</script>
<template>
  <div v-if="props.stage == 1" class="mt-4">
    <h2 class="alert-heading">
      Please enter the authors:
    </h2>
    <BAlert :model-value="true">
      Authors will be listed like this: <strong> {{ authors_string }} </strong>
    </BAlert>
    <div class="p-2">
      <BCard v-for="(author, index) in authors" class="mb-2" header-tag="header" footer-tag="footer">
        <template #header>
          <h5 class="mb-0">{{ index + 1 }}. Author</h5>
        </template>
        <div class="d-flex flex-row justify-content-evenly align-items-end">
          <BButtonGroup aria-label="Basic example">
            <BButton v-if="authors.length == 1" disabled variant="danger" title="Delete this author">
              <i class="fa-solid fa-trash-can"></i>
            </BButton>
            <BButton v-else @click="removeAuthor(index)" variant="danger" title="Delete this author">
              <i class="fa-solid fa-trash-can"></i>
            </BButton>
            <BButton @click="fillAuthor(index)" variant="info" title="Insert your name and ORCID ID as author">
              <i class="fa-solid fa-id-card"></i>
            </BButton>
            <BButton v-if="index == 0" disabled>
              <i class="fa-solid fa-arrow-up"></i>
            </BButton>
            <BButton v-else @click="moveAuthorUp(index)">
              <i class="fa-solid fa-arrow-up"></i>
            </BButton>
            <BButton v-if="index == authors.length - 1" disabled>
              <i class="fa-solid fa-arrow-down"></i>
            </BButton>
            <BButton v-else @click="moveAuthorDown(index)">
              <i class="fa-solid fa-arrow-down"></i>
            </BButton>
          </BButtonGroup>
          <div class="d-flex flex-column">
            <span>First name*</span>
            <BFormInput v-model="author.firstName" :state="valid[index].firstName"
              aria-describedby="input-live-help input-live-feedback" placeholder="First name">
            </BFormInput>
          </div>
          <div class="d-flex flex-column">
            <span>Last name*</span>
            <BFormInput v-model="author.lastName" :state="valid[index].lastName" placeholder="Last name">
            </BFormInput>
          </div>
          <div class="d-flex flex-column">
            <span>ORCID ID (optional)</span>
            <BFormInput v-model="author.orcidId" :state="valid[index].orcidId" placeholder="xxxx-xxxx-xxxx-xxxx">
            </BFormInput>
          </div>
        </div>
        <template #footer>
          <h6 class="mb-0">Affiliations</h6>
          <div class="d-flex flex-row justify-content-center align-items-end">
            <BButtonGroup aria-label="Basic example" class="me-2">
              <BButton variant="danger" title="Delete this author">
                <i class="fa-solid fa-trash-can"></i>
              </BButton>
              <BButton>
                <i class="fa-solid fa-arrow-up"></i>
              </BButton>
              <BButton>
                <i class="fa-solid fa-arrow-down"></i>
              </BButton>
            </BButtonGroup>
            <div class="d-flex flex-column me-2">
              <span>Affiliation name*</span>
              <BFormInput placeholder="Name">
              </BFormInput>
            </div>
            <div class="d-flex flex-column">
              <span>ROR ID (optional)</span>
              <BFormInput placeholder="0xxxxxxxx">
              </BFormInput>
            </div>
          </div>
        </template>
      </BCard>

      <BButton @click="addAuthor()" variant="success">
        <i class="fa-solid fa-plus"></i>
        One more author
      </BButton>
    </div>

    <div class="d-flex flex-row justify-content-between">
      <BButton @click="$emit('back')" variant="primary" size="lg">
        Back
      </BButton>
      <BButton @click="nextStage()" variant="primary">
        Continue
      </BButton>
    </div>
  </div>
</template>
