<script setup lang="ts">

/**
 * Table header cell that sorts the column it heads.
 *
 * `ordering` is the DRF-style ordering string currently in effect ("name" or
 * "-name"); clicking emits the field so the parent can toggle it.
 */
const props = defineProps({
    field: {type: String, required: true},
    ordering: {type: String, default: null},
    // Right-align numeric columns.
    numeric: {type: Boolean, default: false}
});

const emit = defineEmits(["sort"]);

</script>

<template>
    <th :class="{'text-end': numeric}"
        class="user-select-none"
        role="button"
        scope="col"
        @click="emit('sort', field)">
        <slot></slot>
        <i v-if="ordering === field" class="fa fa-caret-up ms-1"></i>
        <i v-else-if="ordering === `-${field}`" class="fa fa-caret-down ms-1"></i>
        <i v-else class="fa fa-sort ms-1 text-muted opacity-25"></i>
    </th>
</template>
