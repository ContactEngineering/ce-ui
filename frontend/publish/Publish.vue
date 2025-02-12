<script setup>
import { ref, computed } from 'vue';
import { BCard, BCardBody, BButton, BButtonGroup, BFormInput, BAlert, BFormRadioGroup, BFormCheckbox } from 'bootstrap-vue-next';

const props = defineProps({
  configured_for_doi_generation: Boolean,
  user: Object
});


const stage = ref(2);


const options = [
  { text: 'CC0 1.0 (Public Domain Dedication) Description Legal code ', value: 'first' },
  { text: 'CC BY 4.0 Description Legal code', value: 'second' },
  { text: 'CC BY-SA 4.0 Description Legal code', value: 'third' },
]

const selected = ref('first')

function highlight(n) {
  if (n == stage.value) {
    return "text-primary";
  }
  else if (n < stage.value) {
    return "text-success";
  }
  else {
    return "text-muted";
  }
}

const authors = ref(
  [
    { firstName: "", lastName: "", orcidId: "" },
  ]);

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
    valid.value[index].orcidId = orcidIdRegex.test(author.orcidId);
    is_valid = is_valid && valid.value[index].firstName && valid.value[index].lastName && valid.value[index].orcidId;
  })
  return is_valid;
}

function nextStage() {
  if (stage.value == 1) { // Author stage
    if (!check_validity()) {
      return;
    }
  }
  stage.value = stage.value >= 3 ? 3 : stage.value + 1;
}
const authors_string = computed(() => {
  return authors.value.map((author) => `${author.firstName} ${author.lastName}`).join(", ");
})


</script>
<template>
  <div class="container">
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
    <div class="p-5">
      <div v-if="stage == 0">
        <div class="alert alert-danger mt-5">
          <h4>
            You are about to publish your digital surface twin Digital surface twin #1
          </h4>

          By publishing, you create an <strong>immutable copy</strong> of this digital twin as a snapshot with all its
          data.<br>
          This snapshot has a version number and a unique URL for citations and it is visible and usable for everyone.
        </div>
        <div class="mt-4">
          <h2 class="alert-heading">Implications of publishing</h2>
          <ul>
            <li>The digital twin and all measurements will be <b>visible by everyone</b>,
              registered or anonymous users, now and in future.</li>
            <li>The related data (raw data, descriptions, ..) <b>will be downloadable by everyone</b>.</li>
            <li>Every user can perform analyses on your data.</li>
            <li>You choose a license for your data - the choice of the license is irrevocable.</li>
            <li>If you have assigned tags to the digital twin or its measurements, these tags are also
              part of the publication.</li>
            <li>Your ORCID iD will saved along with your publication.</li>
            <li v-if="configured_for_doi_generation">A <a href="https://www.doi.org/">DOI (Digital Object
                Identifier)</a> will be generated
              with the given data. Your data will be accessible under the corresponding URL.</li>
          </ul>
          <p>
            This is great if you want to <b>make your data public under a permanent URL</b>, e.g. in order
            to reference your data in a citation.
          </p>
          <p>
            Since a copy is made, you can still work on your
            original data as before the publication.
            You may also publish an updated version of this digital surface twin later.
          </p>
        </div>
      </div>
      <div v-if="stage == 1">
        <div class="mt-4">
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
                    <i class="fa-solid fa-arrow-up"></i>
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
        </div>
      </div>
      <div v-if="stage == 2">
        <h2 class="alert-heading">
          Please choose a license
        </h2>
        <div class="d-flex flex-row justify-content-center">
          <BFormRadioGroup v-model="selected" :options="options" name="radio-stacked" stacked />
        </div>
      </div>
      <div v-if="stage == 3">
        <h2 class="alert-heading">
          Final checks
        </h2>
        <div class="d-flex flex-row justify-content-center">
          <div class="d-flex flex-column">
            <BFormCheckbox>
              I understand the implications of publishing this surface and I agree.*<br>
              <span class="text-muted"> Please read the implications of publishing listed above and check.</span>
            </BFormCheckbox>
            <BFormCheckbox>
              I hold copyright of this data or have been authorized by the copyright holders.*<br>
              <span class="text-muted"> Please make sure you're not publishing data from others without their
                authorization.
              </span>
            </BFormCheckbox>
          </div>
        </div>
      </div>
    </div>
    <div class="d-flex flex-row justify-content-between">

      <BButton @click="stage = stage <= 0 ? 0 : stage - 1" size="xl" v-if="stage > 0" variant="primary">
        Back
      </BButton>
      <BButton v-else disabled>
        Back
      </BButton>
      <BButton @click="nextStage()" variant="primary">
        Continue
      </BButton>
    </div>
  </div>
</template>
