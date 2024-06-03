<script setup>

const props = defineProps({
    functionId: Number,
    functionName: String,
    visualizationType: String,
    subjects: String
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
