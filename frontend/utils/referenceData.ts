/**
 * Fixed reference curves that can be overlaid on an analysis plot for
 * comparison against a previously published consensus-study result.
 *
 * The "STC consensus" curves below (median and interquartile range of PSD and
 * RMS height, for a rougher and a smoother reference surface) are digitized
 * from Figure 9 of:
 *
 *   Pradhan, A., Müser, M.H., Miller, N., et al. "The Surface-Topography
 *   Challenge: A Multi-Laboratory Benchmark Study to Advance the
 *   Characterization of Topography." Tribology Letters 73, 41 (2025).
 *   https://doi.org/10.1007/s11249-025-02014-y
 *
 * See `ce_ui/static/reference_data/SOURCE.md` for the full author list and
 * how the raw data files here were derived from the paper.
 *
 * A reference dataset is registered once per workflow (keyed by its function
 * name) in `REFERENCE_DATASETS` below; `SeriesCard` shows a checkbox for each
 * entry registered for the card's own function and, when checked, merges the
 * corresponding synthetic `dataSource` into the ones `BokehPlot` renders.
 *
 * The data itself is stored in raw SI units (metres) as a static JSON file
 * fetched the same way a real analysis series is (see
 * `topobank_rest_api/analysis/v1/views.py`'s `series_card_view` for the shape
 * `dataSource` objects are built in). Unlike real analyses, no backend view
 * picks a display unit for it, so `buildReferenceDataSources` rescales it
 * itself to whatever unit the card's own axes are already using.
 */

import {parseAxisLabel} from "@/utils/axes";
import {factorFromMetrePower, parseLengthPower} from "@/utils/units";

export interface ReferenceDataset {
    /** Unique key, used as the checkbox's `v-model` value. */
    key: string;
    /** Checkbox label shown to the user. */
    label: string;
    /** URL of the `{x: [...], y: [...]}` JSON file, in raw SI units. */
    url: string;
    /**
     * Legend/category grouping. Curves that share one `subjectName` (e.g. the
     * median and both quartiles of the same surface) get one row under
     * "Averages / Measurements"; curves that share one `seriesName` (e.g. the
     * median of both surfaces) get one toggle chip under "Data series".
     */
    subjectName: string;
    seriesName: string;
    /** Power of a length the x axis is, e.g. -1 for a wavevector (m⁻¹). */
    xExponent: number;
    /** Power of a length the y axis is, e.g. 3 for a PSD (m³). */
    yExponent: number;
    /**
     * Fixed line color/dash, overriding the automatic per-plot palette/dash
     * assignment (`assignElementColors`/`assignElementDashes` in `plot.ts`) —
     * these are reference curves from a fixed external study, not one more
     * measurement to tell apart from the others in whatever colors are left.
     */
    color: string;
    dash: string;
}

// The reference curves should read as a callback to Figure 9 of the STC
// paper itself: grey for the rougher surface, honey for the smoother one.
const ROUGH_COLOR = "#808080";
const SMOOTH_COLOR = "#D9A521";

type Quartile = "median" | "lower-quartile" | "upper-quartile";

const QUARTILE_LABEL: { [key in Quartile]: string } = {
    "median": "median",
    "lower-quartile": "lower IQR",
    "upper-quartile": "upper IQR",
};

const QUARTILE_FILE_SUFFIX: { [key in Quartile]: string } = {
    "median": "median",
    "lower-quartile": "lower_quartile",
    "upper-quartile": "upper_quartile",
};

// Figure 9's own convention: a solid line for the median, dashed for either
// quartile bound.
const QUARTILE_DASH: { [key in Quartile]: string } = {
    "median": "solid",
    "lower-quartile": "dashed",
    "upper-quartile": "dashed",
};

/**
 * Build the 6 reference datasets (rough/smooth surface × median/lower/upper
 * IQR) for one workflow, all following the same naming/color/dash convention.
 * `urlFolder` must match a directory under `ce_ui/static/reference_data/`
 * containing `{rougher,smoother}_surface_{median,lower_quartile,upper_quartile}.json`.
 */
function stcConsensusDatasets(
    keyPrefix: string, urlFolder: string, xExponent: number, yExponent: number
): ReferenceDataset[] {
    const surfaces: { key: string, subject: string, color: string, file: string }[] = [
        {key: "rough", subject: "STC consensus (rough surface)", color: ROUGH_COLOR, file: "rougher_surface"},
        {key: "smooth", subject: "STC consensus (smooth surface)", color: SMOOTH_COLOR, file: "smoother_surface"},
    ];
    const quartiles: Quartile[] = ["median", "lower-quartile", "upper-quartile"];

    const datasets: ReferenceDataset[] = [];
    for (const surface of surfaces) {
        for (const quartile of quartiles) {
            datasets.push({
                key: `${keyPrefix}-${surface.key}-${quartile}`,
                label: `${surface.subject} - ${QUARTILE_LABEL[quartile]}`,
                url: `/static/reference_data/${urlFolder}/${surface.file}_${QUARTILE_FILE_SUFFIX[quartile]}.json`,
                subjectName: surface.subject,
                seriesName: `${QUARTILE_LABEL[quartile]} (reference)`,
                xExponent,
                yExponent,
                color: surface.color,
                dash: QUARTILE_DASH[quartile],
            });
        }
    }
    return datasets;
}

/**
 * Reference datasets available per workflow, keyed by `Meta.name` of the
 * `WorkflowImplementation` (i.e. `SeriesCard`'s `functionName` prop). A
 * workflow with no entry here simply shows no "reference data" checkboxes.
 */
export const REFERENCE_DATASETS: { [functionName: string]: ReferenceDataset[] } = {
    // Wavevector (m⁻¹) and PSD (m³) are never auto-rescaled server-side
    // (`natural_display_units` leaves power-of-length axes with exponent != 1
    // alone), unlike RMS height below.
    "topobank_statistics.power_spectral_density": stcConsensusDatasets("psd", "psd", -1, 3),
    "topobank_statistics.variable_bandwidth": stcConsensusDatasets("rms", "rms_height", 1, 1),
};

/**
 * The index a data source should use for a category, reusing the index of an
 * existing data source with the same value so that, e.g., curves sharing one
 * `subjectName` end up under the same row instead of each minting their own,
 * and curves sharing one `seriesName` end up under the same toggle chip.
 *
 * @param dataSources Data sources assembled so far (real and already-added synthetic ones).
 * @param key Category key, e.g. "subjectName".
 * @param value The value this data source would carry for that key.
 * @returns The index to use.
 */
function categoryIndex(dataSources: any[], key: string, value: string): number {
    const indexKey = key + "Index";
    let nextIndex = 0;
    for (const dataSource of dataSources) {
        if (dataSource[key] === value) {
            return dataSource[indexKey];
        }
        if (dataSource[indexKey] >= nextIndex) {
            nextIndex = dataSource[indexKey] + 1;
        }
    }
    return nextIndex;
}

/**
 * Build the synthetic `dataSource` entries for the selected reference
 * datasets, scaled to match the axes of the card they are added to.
 *
 * @param selectedKeys `key`s of the reference datasets to include.
 * @param functionName The card's workflow function name.
 * @param dataSources The card's own fetched data sources, used to pick
 *     category indices that do not collide with them (or with each other).
 * @param xAxisLabel The card's current x axis label, e.g. "Wavevector (nm⁻¹)".
 * @param yAxisLabel The card's current y axis label, e.g. "PSD (nm³)".
 * @returns One `dataSource` per selected key that is actually registered for
 *     `functionName`; unknown keys are silently skipped.
 */
export function buildReferenceDataSources(
    selectedKeys: string[],
    functionName: string,
    dataSources: any[],
    xAxisLabel: string | null,
    yAxisLabel: string | null,
): any[] {
    const available = REFERENCE_DATASETS[functionName] ?? [];
    // The axis label carries the whole compound unit (e.g. "µm⁻¹"), but
    // `factorFromMetrePower` wants just the length it is built from ("µm") —
    // the power is known per dataset already, from `xExponent`/`yExponent`.
    const xUnit = parseLengthPower(parseAxisLabel(xAxisLabel).unit)?.base ?? null;
    const yUnit = parseLengthPower(parseAxisLabel(yAxisLabel).unit)?.base ?? null;

    const built: any[] = [];
    for (const selectedKey of selectedKeys) {
        const dataset = available.find(d => d.key === selectedKey);
        if (dataset == null) {
            continue;
        }

        const allDataSources = [...dataSources, ...built];
        built.push({
            sourceName: `reference-${dataset.key}`,
            subjectName: dataset.subjectName,
            subjectNameIndex: categoryIndex(allDataSources, "subjectName", dataset.subjectName),
            subjectNameHasParent: false,
            seriesName: dataset.seriesName,
            seriesNameIndex: categoryIndex(allDataSources, "seriesName", dataset.seriesName),
            seriesNameHasParent: false,
            hasParent: false,
            // Falls back to no rescaling if the card's axis is not a power of a
            // length unit we recognize; the curve is then shown in raw SI units.
            xScaleFactor: factorFromMetrePower(dataset.xExponent, xUnit) ?? 1,
            yScaleFactor: factorFromMetrePower(dataset.yExponent, yUnit) ?? 1,
            url: dataset.url,
            width: 2,
            alpha: 1,
            visible: true,
            isSurfaceAnalysis: false,
            isTopographyAnalysis: false,
            // Fixed styling, bypassing BokehPlot's automatic per-plot palette/dash
            // assignment (see `color`/`dash` on `ReferenceDataset`), so the curve
            // reads as consistent with Figure 9 regardless of what else is on the plot.
            color: dataset.color,
            dash: dataset.dash,
            // Figure 9 plots these as lines, not scattered points; a reference
            // curve from a fixed external study is not one more measurement to
            // compare markers against.
            showSymbols: false,
        });
    }
    return built;
}
