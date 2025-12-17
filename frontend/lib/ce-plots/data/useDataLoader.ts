/**
 * useDataLoader - Composable for async data loading
 *
 * Replaces Bokeh's AjaxDataSource with a Vue-reactive approach.
 * Supports:
 * - Loading data from URLs
 * - Custom data transformation
 * - Scale factors
 * - Loading state tracking
 * - Error handling
 */

import { ref, type Ref } from 'vue';
import axios, { type AxiosRequestConfig } from 'axios';
import type { DataPoint, DataSeries, DataLoaderOptions } from '../types';

export interface LoadedData {
    /** Raw response data */
    raw: any;
    /** Extracted X values */
    x: number[];
    /** Extracted Y values */
    y: number[];
    /** Transformed data points */
    points: DataPoint[];
}

export interface UseDataLoaderOptions {
    /** Base URL to prepend to relative URLs */
    baseUrl?: string;
    /** Default axios config */
    axiosConfig?: AxiosRequestConfig;
    /** Transform all responses */
    globalTransform?: (data: any) => any;
}

export interface UseDataLoaderReturn {
    /** Number of pending requests */
    loading: Ref<number>;
    /** Whether any request is loading */
    isLoading: Ref<boolean>;
    /** Last error (if any) */
    error: Ref<Error | null>;
    /** Load a single data series */
    loadSeries: (
        id: string,
        name: string,
        options: DataLoaderOptions,
        seriesOptions?: Partial<DataSeries>
    ) => Promise<DataSeries | null>;
    /** Load multiple series in parallel */
    loadMultiple: (
        configs: Array<{
            id: string;
            name: string;
            options: DataLoaderOptions;
            seriesOptions?: Partial<DataSeries>;
        }>
    ) => Promise<DataSeries[]>;
    /** Load raw data from URL */
    loadRaw: (url: string) => Promise<any>;
    /** Clear error state */
    clearError: () => void;
}

/**
 * Extract values from data using a field specification
 */
function extractValues(
    data: any,
    field: string | ((data: any) => number[]) | undefined,
    defaultField: string
): number[] {
    if (typeof field === 'function') {
        return field(data);
    }

    const fieldName = field ?? defaultField;
    const values = data[fieldName];

    if (!Array.isArray(values)) {
        console.warn(`Field "${fieldName}" is not an array in data`);
        return [];
    }

    return values;
}

/**
 * Apply scale factor to values
 */
function applyScaleFactor(values: number[], factor: number | undefined): number[] {
    if (factor === undefined || factor === 1) {
        return values;
    }
    return values.map(v => v * factor);
}

export function useDataLoader(options: UseDataLoaderOptions = {}): UseDataLoaderReturn {
    const { baseUrl = '', axiosConfig = {}, globalTransform } = options;

    const loading = ref(0);
    const isLoading = ref(false);
    const error = ref<Error | null>(null);

    /**
     * Load raw data from URL
     */
    async function loadRaw(url: string): Promise<any> {
        const fullUrl = url.startsWith('http') ? url : `${baseUrl}${url}`;

        loading.value++;
        isLoading.value = true;
        error.value = null;

        try {
            const response = await axios.get(fullUrl, axiosConfig);
            let data = response.data;

            if (globalTransform) {
                data = globalTransform(data);
            }

            return data;
        } catch (e) {
            error.value = e as Error;
            throw e;
        } finally {
            loading.value--;
            isLoading.value = loading.value > 0;
        }
    }

    /**
     * Load a single data series from URL
     */
    async function loadSeries(
        id: string,
        name: string,
        loaderOptions: DataLoaderOptions,
        seriesOptions: Partial<DataSeries> = {}
    ): Promise<DataSeries | null> {
        try {
            const rawData = await loadRaw(loaderOptions.url);

            let points: DataPoint[];

            if (loaderOptions.transform) {
                // Use custom transform function
                points = loaderOptions.transform(rawData);
            } else {
                // Extract x and y values
                let xValues = extractValues(rawData, loaderOptions.xField, 'x');
                let yValues = extractValues(rawData, loaderOptions.yField, 'y');

                // Apply scale factors
                xValues = applyScaleFactor(xValues, loaderOptions.xScaleFactor);
                yValues = applyScaleFactor(yValues, loaderOptions.yScaleFactor);

                // Validate lengths match
                if (xValues.length !== yValues.length) {
                    console.warn(
                        `X and Y arrays have different lengths: ${xValues.length} vs ${yValues.length}`
                    );
                }

                // Build points array
                const length = Math.min(xValues.length, yValues.length);
                points = [];

                for (let i = 0; i < length; i++) {
                    const point: DataPoint = {
                        x: xValues[i],
                        y: yValues[i]
                    };

                    // Add auxiliary fields
                    if (loaderOptions.auxiliaryFields) {
                        for (const [key, fieldSpec] of Object.entries(loaderOptions.auxiliaryFields)) {
                            if (typeof fieldSpec === 'function') {
                                point[key] = fieldSpec(rawData, i);
                            } else if (typeof fieldSpec === 'string' && rawData[fieldSpec]) {
                                const arr = rawData[fieldSpec];
                                point[key] = Array.isArray(arr) ? arr[i] : arr;
                            }
                        }
                    }

                    points.push(point);
                }
            }

            // Build series object
            const series: DataSeries = {
                id,
                name,
                data: points,
                visible: true,
                ...seriesOptions
            };

            return series;
        } catch (e) {
            console.error(`Failed to load series "${name}" from ${loaderOptions.url}:`, e);
            return null;
        }
    }

    /**
     * Load multiple series in parallel
     */
    async function loadMultiple(
        configs: Array<{
            id: string;
            name: string;
            options: DataLoaderOptions;
            seriesOptions?: Partial<DataSeries>;
        }>
    ): Promise<DataSeries[]> {
        const results = await Promise.all(
            configs.map(config =>
                loadSeries(config.id, config.name, config.options, config.seriesOptions)
            )
        );

        // Filter out null results (failed loads)
        return results.filter((s): s is DataSeries => s !== null);
    }

    /**
     * Clear error state
     */
    function clearError() {
        error.value = null;
    }

    return {
        loading,
        isLoading,
        error,
        loadSeries,
        loadMultiple,
        loadRaw,
        clearError
    };
}
