<script setup lang="ts">
/**
 * ExportButton - Export toolbar button/dropdown
 *
 * Provides UI for exporting plots with format selection:
 * - SVG export (vector)
 * - PNG export (raster, with resolution options)
 */

import { ref, computed, inject } from 'vue';
import { PlotContextKey } from '../core/PlotContext';
import { useExport } from './useExport';
import type { ExportOptions } from '../types';

const props = withDefaults(defineProps<{
    /** Reference to the SVG element to export */
    svgElement?: SVGElement | null;
    /** Default filename (without extension) */
    filename?: string;
    /** Show as dropdown with format options */
    showDropdown?: boolean;
    /** Available PNG scale options */
    scaleOptions?: number[];
    /** Button label */
    label?: string;
    /** Custom CSS class */
    buttonClass?: string;
    /** Show loading spinner */
    showSpinner?: boolean;
}>(), {
    filename: 'plot',
    showDropdown: true,
    scaleOptions: () => [1, 2, 4],
    label: 'Export',
    showSpinner: true
});

const emit = defineEmits<{
    (e: 'export', format: 'svg' | 'png', options: Partial<ExportOptions>): void;
    (e: 'error', error: Error): void;
}>();

// Try to get SVG from plot context if not provided
const plotContext = inject(PlotContextKey, null);

const { exporting, error, exportSvg, exportPng } = useExport({
    defaultFilename: props.filename
});

const dropdownOpen = ref(false);

// Get the SVG element to export
const targetSvg = computed(() => {
    if (props.svgElement) return props.svgElement;

    // Try to find SVG in plot context (would need to be exposed)
    // For now, return null if not provided
    return null;
});

function toggleDropdown() {
    dropdownOpen.value = !dropdownOpen.value;
}

function closeDropdown() {
    dropdownOpen.value = false;
}

async function handleExportSvg() {
    const svg = targetSvg.value;
    if (!svg) {
        const err = new Error('No SVG element available for export');
        emit('error', err);
        return;
    }

    try {
        await exportSvg(svg, { filename: props.filename });
        emit('export', 'svg', { filename: props.filename });
    } catch (e) {
        emit('error', e as Error);
    }

    closeDropdown();
}

async function handleExportPng(scale: number) {
    const svg = targetSvg.value;
    if (!svg) {
        const err = new Error('No SVG element available for export');
        emit('error', err);
        return;
    }

    try {
        await exportPng(svg, { filename: props.filename, scale });
        emit('export', 'png', { filename: props.filename, scale });
    } catch (e) {
        emit('error', e as Error);
    }

    closeDropdown();
}

function getScaleLabel(scale: number): string {
    if (scale === 1) return 'PNG (1x)';
    return `PNG (${scale}x)`;
}
</script>

<template>
    <div class="ce-export" @mouseleave="closeDropdown">
        <!-- Simple button mode -->
        <button
            v-if="!showDropdown"
            class="ce-export-button"
            :class="buttonClass"
            :disabled="exporting || !targetSvg"
            @click="handleExportSvg"
        >
            <span v-if="exporting && showSpinner" class="ce-export-spinner"></span>
            <span v-else>{{ label }}</span>
        </button>

        <!-- Dropdown mode -->
        <div v-else class="ce-export-dropdown">
            <button
                class="ce-export-button"
                :class="buttonClass"
                :disabled="exporting || !targetSvg"
                @click="toggleDropdown"
            >
                <span v-if="exporting && showSpinner" class="ce-export-spinner"></span>
                <template v-else>
                    <span>{{ label }}</span>
                    <span class="ce-export-arrow">▼</span>
                </template>
            </button>

            <div v-show="dropdownOpen" class="ce-export-menu">
                <!-- SVG option -->
                <button
                    class="ce-export-option"
                    @click="handleExportSvg"
                >
                    SVG (vector)
                </button>

                <!-- PNG options -->
                <button
                    v-for="scale in scaleOptions"
                    :key="scale"
                    class="ce-export-option"
                    @click="handleExportPng(scale)"
                >
                    {{ getScaleLabel(scale) }}
                </button>
            </div>
        </div>

        <!-- Error display -->
        <div v-if="error" class="ce-export-error">
            {{ error.message }}
        </div>
    </div>
</template>

<style scoped>
.ce-export {
    position: relative;
    display: inline-block;
}

.ce-export-button {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 12px;
    font-size: 12px;
    font-family: system-ui, -apple-system, sans-serif;
    color: #333;
    background: white;
    border: 1px solid #ddd;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.15s ease, border-color 0.15s ease;
}

.ce-export-button:hover:not(:disabled) {
    background-color: #f5f5f5;
    border-color: #ccc;
}

.ce-export-button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.ce-export-arrow {
    font-size: 8px;
    margin-left: 2px;
}

.ce-export-dropdown {
    position: relative;
}

.ce-export-menu {
    position: absolute;
    top: 100%;
    left: 0;
    margin-top: 4px;
    min-width: 120px;
    background: white;
    border: 1px solid #ddd;
    border-radius: 4px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    z-index: 100;
    overflow: hidden;
}

.ce-export-option {
    display: block;
    width: 100%;
    padding: 8px 12px;
    font-size: 12px;
    font-family: system-ui, -apple-system, sans-serif;
    color: #333;
    background: none;
    border: none;
    text-align: left;
    cursor: pointer;
    transition: background-color 0.15s ease;
}

.ce-export-option:hover {
    background-color: #f5f5f5;
}

.ce-export-option:not(:last-child) {
    border-bottom: 1px solid #eee;
}

.ce-export-spinner {
    display: inline-block;
    width: 12px;
    height: 12px;
    border: 2px solid #ddd;
    border-top-color: #666;
    border-radius: 50%;
    animation: ce-spin 0.8s linear infinite;
}

@keyframes ce-spin {
    to {
        transform: rotate(360deg);
    }
}

.ce-export-error {
    position: absolute;
    top: 100%;
    left: 0;
    margin-top: 4px;
    padding: 6px 10px;
    font-size: 11px;
    color: #c00;
    background: #fee;
    border: 1px solid #fcc;
    border-radius: 4px;
    white-space: nowrap;
}
</style>
