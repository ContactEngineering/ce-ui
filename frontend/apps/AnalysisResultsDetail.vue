<script setup>

import {computed, inject} from "vue";

import {subjectsFromBase64} from "topobank/utils/api";

const appProps = inject("appProps");

const visualizationType = computed(() => {
    return appProps.object.visualization_type;
});

const functionId = computed(() => {
    return appProps.object.id;
});

const functionName = computed(() => {
    return appProps.object.name;
});

const subjects = computed(() => {
    return subjectsFromBase64(appProps.searchParams.get("subjects"));
});

</script>

<template>
    <div class="row">
        <div class="col-lg-12 mb-4">
            <component :is="`${visualizationType}-card`"
                       :enlarged="true"
                       :function-id="functionId"
                       :function-name="functionName"
                       :subjects="subjects">
            </component>
        </div>
    </div>
</template>
