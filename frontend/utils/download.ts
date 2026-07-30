/**
 * Helpers for producing downloadable artifacts.
 *
 * Analysis results are stored as split JSON/NetCDF files in the object store
 * and handed to the browser as (pre-signed) URLs, so everything that a plot or
 * a table shows is already client-side. Tabular exports are therefore built
 * here rather than re-assembled by the server; see `fetchArchiveUrl` for the
 * large-artifact case, which stays on the server but runs asynchronously.
 */

/**
 * A single data series as fetched from the object store.
 *
 * JSON has no NaN, so the backend encodes non-finite values as `null`; they are
 * written as an empty CSV field and as "nan" in text files.
 */
export interface Series {
    /** Name of the subject (measurement or average of a dataset). */
    subjectName: string | null;
    /** Name of the data series, e.g. "1D PSD along x". */
    seriesName: string | null;
    x: (number | null)[];
    y: (number | null)[];
    /** Standard error of `y`, only present for averages over a dataset. */
    stdErrY?: (number | null)[] | null;
}

/**
 * Quote a single CSV field. Fields containing the delimiter, a quote or a line
 * break are wrapped in double quotes with inner quotes doubled (RFC 4180).
 */
export function quoteCsvField(value: unknown, delimiter: string = ","): string {
    if (value == null) {
        return "";
    }
    const s = String(value);
    if (s.includes(delimiter) || s.includes('"') || s.includes("\n") || s.includes("\r")) {
        return `"${s.replace(/"/g, '""')}"`;
    }
    return s;
}

/**
 * Turn rows of values into CSV text. Rows may be ragged; short rows simply
 * yield fewer fields.
 */
export function toCsvText(rows: unknown[][], delimiter: string = ","): string {
    return rows.map(row => row.map(field => quoteCsvField(field, delimiter)).join(delimiter)).join("\n") + "\n";
}

/** Multiply a column by a scale factor, leaving missing values missing. */
function scaleColumn(values: (number | null)[] | null | undefined,
                     scaleFactor: number | null | undefined): (number | null)[] {
    if (values == null) {
        return [];
    }
    if (scaleFactor == null) {
        return values;
    }
    return values.map(value => value == null ? null : scaleFactor * value);
}

/**
 * Combine a data source (the plot metadata describing one series) with the JSON
 * fetched from its URL into an exportable series.
 *
 * The scale factors convert each series into the common units of the plot axes,
 * exactly as the plot itself does, so an export matches what is on screen.
 */
export function seriesFromDataSource(dataSource: any, data: any): Series {
    const stdErrY = data.std_err_y == null ? null : scaleColumn(data.std_err_y, dataSource.yScaleFactor);
    return {
        subjectName: dataSource.subjectName ?? null,
        seriesName: dataSource.seriesName ?? data.name ?? null,
        x: scaleColumn(data.x, dataSource.xScaleFactor),
        y: scaleColumn(data.y, dataSource.yScaleFactor),
        stdErrY: stdErrY
    };
}

/**
 * Build the rows of a long-format CSV table for a set of data series: one row
 * per data point, with the subject and series name repeated. Long format keeps
 * a single table valid even though series differ in length and in whether they
 * carry a standard error.
 *
 * @param series The series to export.
 * @param xLabel Header for the x column, including its unit.
 * @param yLabel Header for the y column, including its unit.
 */
export function buildSeriesCsvRows(series: Series[], xLabel: string, yLabel: string): unknown[][] {
    const hasStdErr = series.some(s => s.stdErrY != null);
    const header = ["Subject", "Series", xLabel, yLabel];
    if (hasStdErr) {
        header.push(`Standard error of ${yLabel}`);
    }

    const rows: unknown[][] = [header];
    for (const s of series) {
        // Guard against a series whose x and y arrays disagree in length: export
        // only the points that have both coordinates.
        const nbPoints = Math.min(s.x?.length ?? 0, s.y?.length ?? 0);
        for (let i = 0; i < nbPoints; i++) {
            const row: unknown[] = [s.subjectName ?? "", s.seriesName ?? "", s.x[i], s.y[i]];
            if (hasStdErr) {
                row.push(s.stdErrY?.[i] ?? "");
            }
            rows.push(row);
        }
    }
    return rows;
}

/**
 * Build a text (whitespace-separated) export of a set of data series, with a
 * commented header per series so the file stays self-describing and loadable
 * with `numpy.loadtxt`.
 *
 * @param series The series to export.
 * @param options.title Title of the analysis workflow.
 * @param options.xLabel Label of the x column, including its unit.
 * @param options.yLabel Label of the y column, including its unit.
 * @param options.dois DOIs that should be cited when the data is used.
 */
export function buildSeriesTxt(series: Series[],
                               options: {
                                   title: string,
                                   xLabel: string,
                                   yLabel: string,
                                   dois?: string[]
                               }): string {
    const lines: string[] = [];

    lines.push(`# ${options.title}`);
    lines.push(`# ${"=".repeat(options.title.length)}`);
    if (options.dois != null && options.dois.length > 0) {
        lines.push("#");
        lines.push("# IF YOU USE THIS DATA IN A PUBLICATION, PLEASE CITE THE FOLLOWING PAPERS:");
        for (const doi of options.dois) {
            lines.push(`# - ${doi}`);
        }
    }

    for (const s of series) {
        const heading = [s.subjectName, s.seriesName].filter(name => name != null && name !== "").join(" - ");
        const hasStdErr = s.stdErrY != null;
        lines.push("#");
        lines.push(`# ${heading}`);
        lines.push(`# ${"-".repeat(heading.length)}`);
        lines.push(`# Columns: ${options.xLabel}, ${options.yLabel}`
            + (hasStdErr ? `, standard error of ${options.yLabel}` : ""));
        if (hasStdErr) {
            lines.push('# The value "nan" for the standard error of an average indicates that no error');
            lines.push("# could be computed because the average contains only a single data point.");
        }

        const nbPoints = Math.min(s.x?.length ?? 0, s.y?.length ?? 0);
        for (let i = 0; i < nbPoints; i++) {
            const columns = [s.x[i], s.y[i]];
            if (hasStdErr) {
                columns.push(s.stdErrY?.[i] ?? null);
            }
            // "nan" keeps the column count constant so the file stays loadable
            // with `numpy.loadtxt`.
            lines.push(columns.map(value => value == null || isNaN(value) ? "nan" : value).join(" "));
        }
        lines.push("");
    }

    return lines.join("\n");
}

/**
 * Build the rows of a long-format CSV table from result data held as parallel
 * arrays, one group of arrays per analyzed subject.
 *
 * @param groups The groups to export, each with a label and its columns.
 * @param columns Which keys to export, and under which title.
 * @param labelTitle Header of the leading label column.
 */
export function buildColumnsCsvRows(groups: { label: string | null, data: Record<string, unknown[]> }[],
                                   columns: { key: string, title: string }[],
                                   labelTitle: string = "Subject"): unknown[][] {
    const rows: unknown[][] = [[labelTitle, ...columns.map(column => column.title)]];
    for (const group of groups) {
        // Columns of one group are parallel arrays; a column that is absent
        // yields empty fields rather than shifting the remaining ones.
        const nbRows = Math.max(...columns.map(column => group.data[column.key]?.length ?? 0), 0);
        for (let i = 0; i < nbRows; i++) {
            rows.push([group.label ?? "", ...columns.map(column => group.data[column.key]?.[i] ?? "")]);
        }
    }
    return rows;
}

/**
 * Build the rows of a CSV table from the row objects and column definitions of
 * a displayed table. Columns without a `data` key (e.g. a column rendering a
 * link) are skipped, as they carry no plain value.
 *
 * @param data The table rows, keyed by column `data` name.
 * @param columns Column definitions with `title` and optional `data`.
 * @param extraColumns Columns prepended to every row, e.g. the subject name.
 */
export function buildTableCsvRows(data: Record<string, unknown>[],
                                 columns: { title: string, data?: string }[],
                                 extraColumns: { title: string, data: string }[] = []): unknown[][] {
    const valueColumns = [...extraColumns, ...columns.filter(column => column.data != null)] as
        { title: string, data: string }[];
    const rows: unknown[][] = [valueColumns.map(column => column.title)];
    for (const row of data) {
        rows.push(valueColumns.map(column => {
            const value = row[column.data];
            // NaN round-trips through CSV as an empty field rather than the
            // string "NaN", which spreadsheets read as text.
            return typeof value === "number" && isNaN(value) ? "" : value;
        }));
    }
    return rows;
}

/**
 * Turn a display name into something safe to use as a file name.
 */
export function slugifyFilename(name: string): string {
    const slug = name
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, "-")
        .replace(/^-+|-+$/g, "");
    return slug === "" ? "download" : slug;
}

/**
 * Hand a string to the browser as a file download.
 */
export function triggerBrowserDownload(filename: string, content: string, mimeType: string): void {
    const url = URL.createObjectURL(new Blob([content], {type: mimeType}));
    try {
        const anchor = document.createElement("a");
        anchor.href = url;
        anchor.download = filename;
        anchor.click();
    } finally {
        // Safe to revoke immediately: the click has already started the download.
        URL.revokeObjectURL(url);
    }
}

/** Longest error text we are willing to put in front of a user. */
const MAX_ERROR_LENGTH = 300;

/** Collapse whitespace and cap the length, so an error stays one readable line. */
function summarize(text: string, maxLength: number = MAX_ERROR_LENGTH): string {
    const collapsed = text.replace(/\s+/g, " ").trim();
    return collapsed.length <= maxLength ? collapsed : `${collapsed.slice(0, maxLength - 1)}…`;
}

/**
 * Turn a failed request into a short, human-readable message.
 *
 * The body of an error response is not fit to display as-is: with `DEBUG` on,
 * Django answers a failing request with a complete HTML debug page, and dumping
 * that into the UI buries the actual problem in markup. HTML bodies are
 * therefore reduced to their title (which carries the exception and the route),
 * while plain-text and JSON error bodies — the ones the API returns
 * deliberately — are shown as they are.
 *
 * @param error The rejected request (an axios error, or any Error).
 * @returns A single line describing what went wrong.
 */
export function describeRequestError(error: any): string {
    const response = error?.response;
    if (response == null) {
        return summarize(error?.message ?? String(error));
    }

    const status = `HTTP ${response.status}`
        + (response.statusText ? ` ${response.statusText}` : "");
    const data = response.data;

    if (typeof data === "string") {
        const body = data.trim();
        if (body === "") {
            return status;
        }
        if (body.startsWith("<")) {
            // A server error page rather than an API error message
            const title = /<title[^>]*>([\s\S]*?)<\/title>/i.exec(body)?.[1];
            return title == null ? status : `${status}: ${summarize(title)}`;
        }
        return summarize(body);
    }

    if (data != null && typeof data === "object") {
        // DRF reports errors as {"detail": "..."}
        if (typeof data.detail === "string") {
            return summarize(data.detail);
        }
        try {
            return summarize(JSON.stringify(data));
        } catch {
            return status;
        }
    }

    return status;
}

/** Task states of a `TaskStateModel`, as reported by the REST API. */
export const TASK_SUCCESS = "su";
export const TASK_FAILURE = "fa";

const TERMINAL_TASK_STATES = [TASK_SUCCESS, TASK_FAILURE];

export interface TaskState {
    task_state: string;
    task_error?: string | null;
    /** Percentage of the work done, if the task reports progress. */
    task_progress?: number | null;
    task_messages?: string[] | null;
}

/**
 * Poll a task-state resource until it reaches a terminal state.
 *
 * Bundling many (or large) result files into an archive is done by a Celery
 * worker, so the client starts the job and then waits for it here.
 *
 * @param fetchState Returns the current state of the task.
 * @param options.intervalMs Delay between polls.
 * @param options.timeoutMs Give up after this long.
 * @param options.onPoll Called with every state read, so a caller can show progress.
 * @param options.sleep Injectable delay, for tests.
 * @param options.now Injectable clock, for tests.
 * @returns The terminal state.
 * @throws If the task fails or the timeout is exceeded.
 */
export async function pollUntilTerminal<T extends TaskState>(
    fetchState: () => Promise<T>,
    options: {
        intervalMs?: number,
        timeoutMs?: number,
        onPoll?: (state: T) => void,
        sleep?: (ms: number) => Promise<void>,
        now?: () => number
    } = {}): Promise<T> {
    const intervalMs = options.intervalMs ?? 1000;
    const timeoutMs = options.timeoutMs ?? 600000;
    const sleep = options.sleep ?? ((ms: number) => new Promise<void>(resolve => setTimeout(resolve, ms)));
    const now = options.now ?? (() => Date.now());

    const startTime = now();
    for (; ;) {
        const state = await fetchState();
        options.onPoll?.(state);
        if (state.task_state === TASK_FAILURE) {
            throw new Error(state.task_error == null || state.task_error === ""
                ? "The task failed." : state.task_error);
        }
        if (TERMINAL_TASK_STATES.includes(state.task_state)) {
            return state;
        }
        if (now() - startTime >= timeoutMs) {
            throw new Error("Timed out waiting for the task to finish.");
        }
        await sleep(intervalMs);
    }
}

/** The subset of an HTTP client that `fetchArchiveUrl` needs. */
export interface Http {
    post: (url: string) => Promise<{ data: any }>;
    get: (url: string) => Promise<{ data: any }>;
}

export interface PollOptions {
    intervalMs?: number;
    timeoutMs?: number;
    onPoll?: (state: any) => void;
    sleep?: (ms: number) => Promise<void>;
    now?: () => number;
}

/**
 * Ask the server for a ZIP archive, wait until it has been built, and return
 * the URL to download it from.
 *
 * Archives of datasets and of analysis results can be large, so they are
 * assembled by a Celery worker: the POST creates a container whose task state
 * is then polled until the archive is ready.
 *
 * @param http HTTP client (e.g. axios).
 * @param startUrl Endpoint that creates the container.
 * @param options Passed on to `pollUntilTerminal`.
 * @returns The URL of the finished archive.
 * @throws If the task fails, times out, or produced no file.
 */
export async function fetchArchiveUrl(http: Http,
                                      startUrl: string,
                                      options: PollOptions = {}): Promise<string> {
    const {data: container} = await http.post(startUrl);
    const finished = await pollUntilTerminal<TaskState & { manifest?: { file?: string } }>(
        () => http.get(container.url).then(response => response.data),
        {intervalMs: 2000, ...options});
    const url = finished.manifest?.file;
    if (url == null) {
        throw new Error("The archive was prepared but no file was returned.");
    }
    return url;
}
