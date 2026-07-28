<script setup lang="ts">
/**
 * Form controls for adjusting the appearance of a Bokeh plot (layout,
 * legend, line width, symbol size, opacity). Which widgets are shown is
 * controlled through the `optionsWidgets` property.
 */

import {
    BFormInput,
    BFormSelect,
    BFormSelectOption,
    BBadge
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
    <div class="d-flex flex-column gap-3">
        <!-- Row 1: Dropdown selects for layout and legend -->
        <div v-if="optionsWidgets.includes('layout') || optionsWidgets.includes('legend')" class="row g-3 align-items-center">
            <div v-if="optionsWidgets.includes('layout')" class="col-sm-6 col-md-6 col-lg-4">
                <label class="form-label small fw-semibold text-muted mb-1">Plot layout</label>
                <BFormSelect v-model="layout" size="sm">
                    <BFormSelectOption value="web">Responsive (web)</BFormSelectOption>
                    <BFormSelectOption value="print-single">Print (single column)</BFormSelectOption>
                    <BFormSelectOption value="print-double">Print (two columns)</BFormSelectOption>
                </BFormSelect>
            </div>

            <div v-if="optionsWidgets.includes('legend')" class="col-sm-6 col-md-6 col-lg-4">
                <label class="form-label small fw-semibold text-muted mb-1">Legend</label>
                <BFormSelect v-model="legendLocation" size="sm">
                    <BFormSelectOption value="off">Hidden</BFormSelectOption>
                    <BFormSelectOption value="top_right">Top right</BFormSelectOption>
                    <BFormSelectOption value="top_left">Top left</BFormSelectOption>
                    <BFormSelectOption value="bottom_right">Bottom right</BFormSelectOption>
                    <BFormSelectOption value="bottom_left">Bottom left</BFormSelectOption>
                </BFormSelect>
            </div>
        </div>

        <!-- Row 2: Sliders for line width, symbol size, and opacity -->
        <div v-if="optionsWidgets.includes('lineWidth') || optionsWidgets.includes('symbolSize') || optionsWidgets.includes('opacity')" class="row g-3 align-items-center">
            <div v-if="optionsWidgets.includes('lineWidth')" class="col-sm-4 col-md-4 col-lg-4">
                <div class="d-flex justify-content-between align-items-center mb-1">
                    <label class="form-label small fw-semibold text-muted mb-0">Line width</label>
                    <BBadge variant="secondary" size="sm">{{ lineWidth }}px</BBadge>
                </div>
                <BFormInput type="range" min="0.1" max="3.0" step="0.1" v-model="lineWidth" size="sm" />
            </div>

            <div v-if="optionsWidgets.includes('symbolSize')" class="col-sm-4 col-md-4 col-lg-4">
                <div class="d-flex justify-content-between align-items-center mb-1">
                    <label class="form-label small fw-semibold text-muted mb-0">Symbol size</label>
                    <BBadge variant="secondary" size="sm">{{ symbolSize }}px</BBadge>
                </div>
                <BFormInput type="range" min="1" max="20" step="1" v-model="symbolSize" size="sm" />
            </div>

            <div v-if="optionsWidgets.includes('opacity')" class="col-sm-4 col-md-4 col-lg-4">
                <div class="d-flex justify-content-between align-items-center mb-1">
                    <label class="form-label small fw-semibold text-muted mb-0">Opacity</label>
                    <BBadge variant="secondary" size="sm">{{ Math.round(Number(opacity) * 100) }}%</BBadge>
                </div>
                <BFormInput type="range" min="0" max="1" step="0.1" v-model="opacity" size="sm" />
            </div>
        </div>
    </div>
</template>
