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
    {
      person:
        { firstName: "", lastName: "", orcidId: "" },
      affiliations: []
    }
  ]);

const valid = ref([{ person: { firstName: null, lastName: null, orcidId: null }, affiliations: [] }]);

function fillAuthor(index) {
  authors.value[index].person = { ...props.user };
}

function addAuthor() {
  authors.value.push(
    {
      person:
        { firstName: "", lastName: "", orcidId: "" },
      affiliations: []
    }
  );
  valid.value.push({ person: { firstName: null, lastName: null, orcidId: null }, affiliations: [] });

}

function addAffiliation(index) {
  authors.value[index].affiliations.push(
    {
      name: "",
      rorId: ""
    }
  );
  valid.value[index].affiliations.push({ name: null, rorId: null });
}

function removeAuthor(index) {
  authors.value.splice(index, 1);
  valid.value.splice(index, 1);
}

function removeAffiliation(authorIndex, affiliationIndex) {
  authors.value[authorIndex].affiliations.splice(affiliationIndex, 1);
  valid.value[authorIndex].affiliations.splice(affiliationIndex, 1);
}

function moveAuthorUp(index) {
  if (index > 0) {
    const tmp = authors.value[index];
    authors.value[index] = authors.value[index - 1];
    authors.value[index - 1] = tmp;
  }
}

function moveAffiliationUp(authorIndex, affiliationIndex) {
  if (affiliationIndex > 0) {
    const tmp = authors.value[authorIndex].affiliations[affiliationIndex];
    authors.value[authorIndex].affiliations[affiliationIndex] = authors.value[authorIndex].affiliations[affiliationIndex - 1];
    authors.value[authorIndex].affiliations[affiliationIndex - 1] = tmp;
  }
}

function moveAuthorDown(index) {
  if (index < authors.value.length - 1) {
    const tmp = authors.value[index];
    authors.value[index] = authors.value[index + 1];
    authors.value[index + 1] = tmp;

  }
}

function moveAffiliationDown(authorIndex, affiliationIndex) {
  if (affiliationIndex < authors.value[authorIndex].affiliations.length - 1) {
    const tmp = authors.value[authorIndex].affiliations[affiliationIndex];
    authors.value[authorIndex].affiliations[affiliationIndex] = authors.value[authorIndex].affiliations[affiliationIndex + 1];
    authors.value[authorIndex].affiliations[affiliationIndex + 1] = tmp;
  }
}


const orcidIdRegex = new RegExp("^\\d{4}-\\d{4}-\\d{4}-\\d{4}$");
const rorIdRegex = new RegExp("^0[a-z|0-9]{6}[0-9]{2}$");
function check_validity() {
  let is_valid = true;
  authors.value.forEach((author, index) => {
    valid.value[index].person.firstName = author.person.firstName != "";
    valid.value[index].person.lastName = author.person.lastName != "";
    valid.value[index].person.orcidId = author.person.orcidId === "" || orcidIdRegex.test(author.person.orcidId);
    author.affiliations.forEach((affiliation, affIndex) => {
      valid.value[index].affiliations[affIndex].name = affiliation.name != "";
      valid.value[index].affiliations[affIndex].rorId = affiliation.rorId === "" || rorIdRegex.test(affiliation.rorId);
    });
    console.log(valid.value[index].affiliations)
    is_valid = is_valid && Object.values(valid.value[index].person).every((x) => x) && valid.value[index].affiliations.every((affiliation) => Object.values(affiliation).every((x) => x))
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
  return authors.value.map((author) => `${author.person.firstName} ${author.person.lastName}`).join(", ");
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
            <BButton v-else @click="moveAuthorUp(index)" title="Move up">
              <i class="fa-solid fa-arrow-up"></i>
            </BButton>
            <BButton v-if="index == authors.length - 1" disabled>
              <i class="fa-solid fa-arrow-down"></i>
            </BButton>
            <BButton v-else @click="moveAuthorDown(index)" title="Move down">
              <i class="fa-solid fa-arrow-down"></i>
            </BButton>
          </BButtonGroup>
          <div class="d-flex flex-column">
            <span>First name*</span>
            <BFormInput v-model="author.person.firstName" :state="valid[index].person.firstName"
              aria-describedby="input-live-help input-live-feedback" placeholder="First name">
            </BFormInput>
          </div>
          <div class="d-flex flex-column">
            <span>Last name*</span>
            <BFormInput v-model="author.person.lastName" :state="valid[index].person.lastName" placeholder="Last name">
            </BFormInput>
          </div>
          <div class="d-flex flex-column">
            <span>ORCID ID (optional)</span>
            <BFormInput v-model="author.person.orcidId" :state="valid[index].person.orcidId"
              placeholder="xxxx-xxxx-xxxx-xxxx">
            </BFormInput>
          </div>
        </div>
        <template #footer>
          <h6 class="mb-0">{{ author.affiliations.length }} Affiliations</h6>
          <div v-for="(affiliation, affiliation_index) in author.affiliations"
            class="d-flex flex-row justify-content-center align-items-end mt-2">
            <BButtonGroup class="me-2">
              <BButton @click="removeAffiliation(index, affiliation_index)" variant="danger"
                title="Delete this affiliation">
                <i class="fa-solid fa-trash-can"></i>
              </BButton>
              <BButton v-if="affiliation_index == 0" disabled>
                <i class="fa-solid fa-arrow-up"></i>
              </BButton>
              <BButton v-else @click="moveAffiliationUp(index, affiliation_index)">
                <i class="fa-solid fa-arrow-up"></i>
              </BButton>
              <BButton v-if="affiliation_index == author.affiliations.length - 1" disabled>
                <i class="fa-solid fa-arrow-down"></i>
              </BButton>
              <BButton v-else @click="moveAffiliationDown(index, affiliation_index)">
                <i class="fa-solid fa-arrow-down"></i>
              </BButton>
            </BButtonGroup>
            <div class="d-flex flex-column me-2">
              <span>Affiliation name*</span>
              <BFormInput v-model="affiliation.name" :state="valid[index].affiliations[affiliation_index].name"
                placeholder="Name">
              </BFormInput>
            </div>
            <div class="d-flex flex-column">
              <span>ROR ID (optional)</span>
              <BFormInput v-model="affiliation.rorId" :state="valid[index].affiliations[affiliation_index].rorId"
                placeholder="0xxxxxxxx">
              </BFormInput>
            </div>
          </div>

          <BButton @click="addAffiliation(index)" variant="success" class="mt-2">
            <i class="fa-solid fa-plus"></i>
            One more affiliation
          </BButton>
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
