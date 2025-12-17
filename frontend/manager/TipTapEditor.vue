<script setup>
import { QEditor } from 'quasar'

const props = defineProps({
    modelValue: { type: String, default: '' },
    disabled: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue'])

const toolbar = [
    ['bold', 'italic', 'underline'],
    ['unordered', 'ordered'],
    ['h1', 'h2', 'h3'],
    ['removeFormat']
]

function updateValue(val) {
    emit('update:modelValue', val)
}
</script>

<template>
    <QEditor
        :model-value="modelValue"
        @update:model-value="updateValue"
        :readonly="disabled"
        :toolbar="toolbar"
        :dense="true"
        flat
        bordered
        min-height="100px"
        content-class="text-body2"
    />
</template>
