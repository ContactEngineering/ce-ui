/**
 * useExport - Composable for exporting plots to SVG/PNG
 *
 * Provides functionality to export plots as:
 * - SVG (vector format, ideal for publications)
 * - PNG (raster format, with configurable resolution)
 */

import { ref } from 'vue';
import type { ExportOptions } from '../types';

export interface UseExportOptions {
    /** Default filename (without extension) */
    defaultFilename?: string;
    /** Default PNG scale factor (2 = 2x resolution) */
    defaultScale?: number;
    /** Default background color */
    defaultBackground?: string;
}

export interface UseExportReturn {
    /** Whether export is in progress */
    exporting: ReturnType<typeof ref<boolean>>;
    /** Export error (if any) */
    error: ReturnType<typeof ref<Error | null>>;
    /** Export SVG element to file */
    exportSvg: (svgElement: SVGElement, options?: Partial<ExportOptions>) => Promise<void>;
    /** Export SVG element to PNG */
    exportPng: (svgElement: SVGElement, options?: Partial<ExportOptions>) => Promise<void>;
    /** Get SVG as string */
    getSvgString: (svgElement: SVGElement, options?: Partial<ExportOptions>) => string;
    /** Get SVG as data URL */
    getSvgDataUrl: (svgElement: SVGElement, options?: Partial<ExportOptions>) => string;
    /** Get PNG as data URL */
    getPngDataUrl: (svgElement: SVGElement, options?: Partial<ExportOptions>) => Promise<string>;
    /** Get PNG as Blob */
    getPngBlob: (svgElement: SVGElement, options?: Partial<ExportOptions>) => Promise<Blob>;
}

/**
 * Clone SVG element and prepare it for export
 */
function prepareSvgForExport(
    svgElement: SVGElement,
    options: Partial<ExportOptions>
): SVGElement {
    // Clone the SVG
    const clone = svgElement.cloneNode(true) as SVGElement;

    // Get computed dimensions
    const bbox = svgElement.getBoundingClientRect();
    const width = options.width ?? bbox.width;
    const height = options.height ?? bbox.height;

    // Set explicit dimensions
    clone.setAttribute('width', String(width));
    clone.setAttribute('height', String(height));

    // Add background if specified
    if (options.background && options.background !== 'transparent') {
        const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        rect.setAttribute('width', '100%');
        rect.setAttribute('height', '100%');
        rect.setAttribute('fill', options.background);
        clone.insertBefore(rect, clone.firstChild);
    }

    // Inline all computed styles for proper rendering
    inlineStyles(clone);

    return clone;
}

/**
 * Inline computed styles into SVG elements
 * This ensures styles are preserved when SVG is exported
 */
function inlineStyles(element: Element): void {
    const computedStyle = window.getComputedStyle(element);

    // Properties to inline for SVG elements
    const svgProperties = [
        'fill',
        'stroke',
        'stroke-width',
        'stroke-dasharray',
        'stroke-linecap',
        'stroke-linejoin',
        'opacity',
        'fill-opacity',
        'stroke-opacity',
        'font-family',
        'font-size',
        'font-weight',
        'text-anchor',
        'dominant-baseline',
        'visibility',
        'display'
    ];

    // Only inline for SVG elements
    if (element instanceof SVGElement && !(element instanceof SVGSVGElement)) {
        const style: string[] = [];

        for (const prop of svgProperties) {
            const value = computedStyle.getPropertyValue(prop);
            if (value && value !== 'none' && value !== '') {
                style.push(`${prop}: ${value}`);
            }
        }

        if (style.length > 0) {
            const existingStyle = element.getAttribute('style') || '';
            element.setAttribute('style', existingStyle + style.join('; '));
        }
    }

    // Recurse into children
    for (const child of element.children) {
        inlineStyles(child);
    }
}

/**
 * Convert SVG element to string
 */
function svgToString(svgElement: SVGElement): string {
    const serializer = new XMLSerializer();
    let svgString = serializer.serializeToString(svgElement);

    // Add XML declaration and DOCTYPE
    if (!svgString.startsWith('<?xml')) {
        svgString = '<?xml version="1.0" encoding="UTF-8"?>\n' + svgString;
    }

    return svgString;
}

/**
 * Convert SVG to data URL
 */
function svgToDataUrl(svgString: string): string {
    const encoded = encodeURIComponent(svgString)
        .replace(/'/g, '%27')
        .replace(/"/g, '%22');

    return `data:image/svg+xml,${encoded}`;
}

/**
 * Convert SVG to PNG using canvas
 */
async function svgToPng(
    svgElement: SVGElement,
    scale: number,
    background?: string
): Promise<{ dataUrl: string; blob: Blob }> {
    return new Promise((resolve, reject) => {
        const bbox = svgElement.getBoundingClientRect();
        const width = Math.ceil(bbox.width * scale);
        const height = Math.ceil(bbox.height * scale);

        // Create canvas
        const canvas = document.createElement('canvas');
        canvas.width = width;
        canvas.height = height;

        const ctx = canvas.getContext('2d');
        if (!ctx) {
            reject(new Error('Could not get canvas context'));
            return;
        }

        // Fill background
        if (background && background !== 'transparent') {
            ctx.fillStyle = background;
            ctx.fillRect(0, 0, width, height);
        }

        // Create image from SVG
        const img = new Image();
        const svgString = svgToString(svgElement);
        const svgBlob = new Blob([svgString], { type: 'image/svg+xml;charset=utf-8' });
        const url = URL.createObjectURL(svgBlob);

        img.onload = () => {
            ctx.drawImage(img, 0, 0, width, height);
            URL.revokeObjectURL(url);

            canvas.toBlob(
                blob => {
                    if (blob) {
                        resolve({
                            dataUrl: canvas.toDataURL('image/png'),
                            blob
                        });
                    } else {
                        reject(new Error('Failed to create PNG blob'));
                    }
                },
                'image/png'
            );
        };

        img.onerror = () => {
            URL.revokeObjectURL(url);
            reject(new Error('Failed to load SVG image'));
        };

        img.src = url;
    });
}

/**
 * Trigger download of a blob/data URL
 */
function downloadFile(data: Blob | string, filename: string): void {
    const url = typeof data === 'string' ? data : URL.createObjectURL(data);

    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    if (typeof data !== 'string') {
        URL.revokeObjectURL(url);
    }
}

export function useExport(options: UseExportOptions = {}): UseExportReturn {
    const {
        defaultFilename = 'plot',
        defaultScale = 2,
        defaultBackground = 'white'
    } = options;

    const exporting = ref(false);
    const error = ref<Error | null>(null);

    /**
     * Get SVG as string
     */
    function getSvgString(
        svgElement: SVGElement,
        exportOptions: Partial<ExportOptions> = {}
    ): string {
        const prepared = prepareSvgForExport(svgElement, {
            background: defaultBackground,
            ...exportOptions
        });
        return svgToString(prepared);
    }

    /**
     * Get SVG as data URL
     */
    function getSvgDataUrl(
        svgElement: SVGElement,
        exportOptions: Partial<ExportOptions> = {}
    ): string {
        const svgString = getSvgString(svgElement, exportOptions);
        return svgToDataUrl(svgString);
    }

    /**
     * Get PNG as data URL
     */
    async function getPngDataUrl(
        svgElement: SVGElement,
        exportOptions: Partial<ExportOptions> = {}
    ): Promise<string> {
        const prepared = prepareSvgForExport(svgElement, {
            background: defaultBackground,
            ...exportOptions
        });

        const scale = exportOptions.scale ?? defaultScale;
        const { dataUrl } = await svgToPng(prepared, scale, exportOptions.background ?? defaultBackground);
        return dataUrl;
    }

    /**
     * Get PNG as Blob
     */
    async function getPngBlob(
        svgElement: SVGElement,
        exportOptions: Partial<ExportOptions> = {}
    ): Promise<Blob> {
        const prepared = prepareSvgForExport(svgElement, {
            background: defaultBackground,
            ...exportOptions
        });

        const scale = exportOptions.scale ?? defaultScale;
        const { blob } = await svgToPng(prepared, scale, exportOptions.background ?? defaultBackground);
        return blob;
    }

    /**
     * Export SVG to file
     */
    async function exportSvg(
        svgElement: SVGElement,
        exportOptions: Partial<ExportOptions> = {}
    ): Promise<void> {
        exporting.value = true;
        error.value = null;

        try {
            const svgString = getSvgString(svgElement, exportOptions);
            const blob = new Blob([svgString], { type: 'image/svg+xml;charset=utf-8' });
            const filename = (exportOptions.filename ?? defaultFilename) + '.svg';
            downloadFile(blob, filename);
        } catch (e) {
            error.value = e as Error;
            throw e;
        } finally {
            exporting.value = false;
        }
    }

    /**
     * Export SVG to PNG file
     */
    async function exportPng(
        svgElement: SVGElement,
        exportOptions: Partial<ExportOptions> = {}
    ): Promise<void> {
        exporting.value = true;
        error.value = null;

        try {
            const blob = await getPngBlob(svgElement, exportOptions);
            const filename = (exportOptions.filename ?? defaultFilename) + '.png';
            downloadFile(blob, filename);
        } catch (e) {
            error.value = e as Error;
            throw e;
        } finally {
            exporting.value = false;
        }
    }

    return {
        exporting,
        error,
        exportSvg,
        exportPng,
        getSvgString,
        getSvgDataUrl,
        getPngDataUrl,
        getPngBlob
    };
}
