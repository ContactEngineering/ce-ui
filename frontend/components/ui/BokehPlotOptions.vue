<script setup lang="ts">
/**
 * Form controls for adjusting the appearance of a Bokeh plot (layout,
 * legend, line width, symbol size, opacity). Which widgets are shown is
 * controlled through the `optionsWidgets` property.
 */

import {
    BFormGroup,
    BFormInput,
    BFormSelect,
    BFormSelectOption
} from "bootstrap-vue-next";

defineProps({
    optionsWidgets: {
        type: Array,
        default: function () {
            return ["layout", "legend", "lineWidth", "symbolSize", "opacity"];
        }
    }
});

const layout = defineModel('layout', {type: String, default: "web"});
const legendLocation = defineModel('legendLocation', {type: String, default: "off"});
const lineWidth = defineModel('lineWidth', {type: [Number, String], default: 1});
const symbolSize = defineModel('symbolSize', {type: [Number, String], default: 10});
const opacity = defineModel('opacity', {type: [Number, String], default: 0.4});
</script>

<template>
    <BFormGroup v-if="optionsWidgets.includes('layout')"
                class="mt-2"
                label="Plot layout"
                label-cols="4"
                content-cols="8">
        <BFormSelect v-model="layout">
            <BFormSelectOption value="web">
                Optimize plot for web (plot scales with window size)
            </BFormSelectOption>
            <BFormSelectOption value="print-single">
                Optimize plot for print (single-column layout)
            </BFormSelectOption>
            <BFormSelectOption value="print-double">
                Optimize plot for print (two-column layout)
            </BFormSelectOption>
        </BFormSelect>
    </BFormGroup>

    <BFormGroup v-if="optionsWidgets.includes('legend')"
                class="mt-2"
                label="Legend"
                label-cols="4"
                content-cols="8">
        <BFormSelect v-model="legendLocation">
            <BFormSelectOption value="off">Do not show legend</BFormSelectOption>
            <BFormSelectOption value="top_right">Show legend top right</BFormSelectOption>
            <BFormSelectOption value="top_left">Show legend top left</BFormSelectOption>
            <BFormSelectOption value="bottom_right">Show legend bottom right</BFormSelectOption>
            <BFormSelectOption value="bottom_left">Show legend bottom left</BFormSelectOption>
        </BFormSelect>
    </BFormGroup>

    <BFormGroup v-if="optionsWidgets.includes('lineWidth')"
                class="mt-2"
                label="Line width"
                label-cols="4"
                content-cols="8">
        <BFormInput type="range"
                    min="0.1"
                    max="3.0"
                    step="0.1"
                    v-model="lineWidth"/>
    </BFormGroup>

    <BFormGroup v-if="optionsWidgets.includes('symbolSize')"
                class="mt-2"
                label="Symbol size"
                label-cols="4"
                content-cols="8">
        <BFormInput type="range"
                    min="1"
                    max="20"
                    step="1"
                    v-model="symbolSize"/>
    </BFormGroup>

    <BFormGroup v-if="optionsWidgets.includes('opacity')"
                class="mt-2"
                label="Opacity of lines/symbols (measurements only)"
                label-cols="4"
                content-cols="8">
        <BFormInput type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    v-model="opacity"/>
    </BFormGroup>
</template>
