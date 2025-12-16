/**
 * useSelection - Composable for point selection state management
 *
 * Provides reactive selection state for selecting data points
 * in scatter plots and other interactive visualizations.
 */

import { ref, computed, type Ref } from 'vue';
import type { SelectionState, DataPoint, DataSeries } from '../types';

export interface UseSelectionOptions {
    /** Allow multiple selections */
    multiple?: boolean;
    /** Callback when selection changes */
    onSelect?: (selection: SelectionState | SelectionState[]) => void;
    /** Callback when selection is cleared */
    onClear?: () => void;
}

export interface UseSelectionReturn {
    /** Current selection state */
    selection: Ref<SelectionState>;
    /** All selections (for multiple mode) */
    selections: Ref<SelectionState[]>;
    /** Whether anything is selected */
    hasSelection: Ref<boolean>;
    /** Select a point */
    select: (seriesId: string, pointIndex: number) => void;
    /** Toggle selection (select if not selected, deselect if selected) */
    toggle: (seriesId: string, pointIndex: number) => void;
    /** Clear all selections */
    clear: () => void;
    /** Check if a specific point is selected */
    isSelected: (seriesId: string, pointIndex: number) => boolean;
    /** Get selected point data from series */
    getSelectedPoint: (series: DataSeries[]) => { series: DataSeries; point: DataPoint; index: number } | null;
}

export function useSelection(options: UseSelectionOptions = {}): UseSelectionReturn {
    const { multiple = false, onSelect, onClear } = options;

    // Single selection state
    const selection = ref<SelectionState>({
        seriesId: null,
        pointIndex: null
    });

    // Multiple selection state
    const selections = ref<SelectionState[]>([]);

    // Computed: whether anything is selected
    const hasSelection = computed(() => {
        if (multiple) {
            return selections.value.length > 0;
        }
        return selection.value.seriesId !== null && selection.value.pointIndex !== null;
    });

    /**
     * Select a point (replaces current selection in single mode)
     */
    function select(seriesId: string, pointIndex: number) {
        const newSelection: SelectionState = { seriesId, pointIndex };

        if (multiple) {
            // Add to selections if not already present
            const exists = selections.value.some(
                s => s.seriesId === seriesId && s.pointIndex === pointIndex
            );
            if (!exists) {
                selections.value = [...selections.value, newSelection];
                onSelect?.(selections.value);
            }
        } else {
            selection.value = newSelection;
            onSelect?.(newSelection);
        }
    }

    /**
     * Toggle selection state of a point
     */
    function toggle(seriesId: string, pointIndex: number) {
        if (multiple) {
            const index = selections.value.findIndex(
                s => s.seriesId === seriesId && s.pointIndex === pointIndex
            );
            if (index >= 0) {
                // Remove from selections
                selections.value = [
                    ...selections.value.slice(0, index),
                    ...selections.value.slice(index + 1)
                ];
                if (selections.value.length === 0) {
                    onClear?.();
                } else {
                    onSelect?.(selections.value);
                }
            } else {
                // Add to selections
                select(seriesId, pointIndex);
            }
        } else {
            // In single mode, toggle means select or clear
            if (selection.value.seriesId === seriesId && selection.value.pointIndex === pointIndex) {
                clear();
            } else {
                select(seriesId, pointIndex);
            }
        }
    }

    /**
     * Clear all selections
     */
    function clear() {
        selection.value = { seriesId: null, pointIndex: null };
        selections.value = [];
        onClear?.();
    }

    /**
     * Check if a specific point is selected
     */
    function isSelected(seriesId: string, pointIndex: number): boolean {
        if (multiple) {
            return selections.value.some(
                s => s.seriesId === seriesId && s.pointIndex === pointIndex
            );
        }
        return selection.value.seriesId === seriesId && selection.value.pointIndex === pointIndex;
    }

    /**
     * Get the selected point data from series array
     */
    function getSelectedPoint(series: DataSeries[]): { series: DataSeries; point: DataPoint; index: number } | null {
        if (!hasSelection.value) return null;

        const sel = multiple ? selections.value[0] : selection.value;
        if (!sel.seriesId || sel.pointIndex === null) return null;

        const selectedSeries = series.find(s => s.id === sel.seriesId);
        if (!selectedSeries) return null;

        const point = selectedSeries.data[sel.pointIndex];
        if (!point) return null;

        return {
            series: selectedSeries,
            point,
            index: sel.pointIndex
        };
    }

    return {
        selection,
        selections,
        hasSelection,
        select,
        toggle,
        clear,
        isSelected,
        getSelectedPoint
    };
}
