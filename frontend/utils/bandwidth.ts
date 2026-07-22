export interface BandwidthPlotData {
    y: number[];
    left: number[];
    cutoff: (number | null)[];
    right: number[];
    name: string[];
    thumbnail: (string | null)[];
    link: string[];
}

/**
 * Turn a list of topographies into the column data for the bandwidth plot.
 * Null entries are skipped and bars are stacked such that the topography
 * with the smallest lower bandwidth ends up at the bottom.
 */
export function bandwidthPlotData(topographies: any[]): BandwidthPlotData {
    const filtered = topographies.filter(t => t != null);

    // Compute vertical positions ordered by lower bandwidth
    const left = filtered.map(t => t.bandwidth_lower);
    const argsort = left
        .map((v, i): [number, number] => [v, i])
        .sort((a, b) => a[0] - b[0])
        .map(a => a[1]);
    const y: number[] = Array(argsort.length);
    for (const i of argsort.keys()) {
        y[argsort[i]] = i;
    }

    return {
        y: y,
        left: left,
        cutoff: filtered.map(t => t.short_reliability_cutoff),
        right: filtered.map(t => t.bandwidth_upper),
        name: filtered.map(t => t.name),
        thumbnail: filtered.map(t => t.thumbnail == null ? null : t.thumbnail.file),
        link: filtered.map(t => `/ui/topography/${t.id}/`),
    };
}
