import {describe, expect, it} from "vitest";

import {
    buildColumnsCsvRows,
    buildSeriesCsvRows,
    buildSeriesTxt,
    buildTableCsvRows,
    describeRequestError,
    fetchArchiveUrl,
    pollUntilTerminal,
    quoteCsvField,
    seriesFromDataSource,
    slugifyFilename,
    toCsvText
} from "@/utils/download";

describe("quoteCsvField", () => {
    it("leaves plain fields untouched", () => {
        expect(quoteCsvField("abc")).toBe("abc");
        expect(quoteCsvField(1.5)).toBe("1.5");
    });

    it("returns an empty field for null and undefined", () => {
        expect(quoteCsvField(null)).toBe("");
        expect(quoteCsvField(undefined)).toBe("");
    });

    it("quotes fields containing the delimiter", () => {
        expect(quoteCsvField("a,b")).toBe('"a,b"');
        expect(quoteCsvField("a;b", ";")).toBe('"a;b"');
        // Not the delimiter in use, so no quoting needed
        expect(quoteCsvField("a;b")).toBe("a;b");
    });

    it("doubles inner quotes", () => {
        expect(quoteCsvField('say "hi"')).toBe('"say ""hi"""');
    });

    it("quotes fields containing line breaks", () => {
        expect(quoteCsvField("a\nb")).toBe('"a\nb"');
    });
});

describe("toCsvText", () => {
    it("joins rows and fields and ends with a newline", () => {
        expect(toCsvText([["a", "b"], [1, 2]])).toBe("a,b\n1,2\n");
    });

    it("honors a custom delimiter", () => {
        expect(toCsvText([["a", "b"]], ";")).toBe("a;b\n");
    });
});

describe("seriesFromDataSource", () => {
    it("applies the scale factors of the plot axes", () => {
        const series = seriesFromDataSource(
            {subjectName: "topo-1", seriesName: "1D PSD", xScaleFactor: 1000, yScaleFactor: 0.5},
            {x: [1, 2], y: [10, 20]}
        );
        expect(series.x).toEqual([1000, 2000]);
        expect(series.y).toEqual([5, 10]);
        expect(series.stdErrY).toBeNull();
    });

    it("leaves data untouched when no scale factor is given", () => {
        const series = seriesFromDataSource({subjectName: "s", seriesName: "t"}, {x: [1], y: [2]});
        expect(series.x).toEqual([1]);
        expect(series.y).toEqual([2]);
    });

    it("scales the standard error like y", () => {
        const series = seriesFromDataSource(
            {subjectName: "average", seriesName: "1D PSD", yScaleFactor: 2},
            {x: [1], y: [10], std_err_y: [0.5]}
        );
        expect(series.stdErrY).toEqual([1]);
    });

    it("keeps missing values missing", () => {
        const series = seriesFromDataSource({xScaleFactor: 2, yScaleFactor: 2}, {x: [null, 1], y: [2, null]});
        expect(series.x).toEqual([null, 2]);
        expect(series.y).toEqual([4, null]);
    });

    it("falls back to the series name stored in the data", () => {
        const series = seriesFromDataSource({subjectName: "s"}, {name: "2D PSD", x: [], y: []});
        expect(series.seriesName).toBe("2D PSD");
    });
});

describe("buildSeriesTxt with missing values", () => {
    it("writes nan so the column count stays constant", () => {
        const txt = buildSeriesTxt([
            {subjectName: "s", seriesName: "t", x: [1], y: [null], stdErrY: [null]}
        ], {title: "T", xLabel: "x", yLabel: "y"});
        expect(txt).toContain("1 nan nan");
    });
});

const seriesWithoutError = [
    {subjectName: "topo-1", seriesName: "1D PSD", x: [1, 2], y: [10, 20]},
    {subjectName: "topo-2", seriesName: "1D PSD", x: [3], y: [30]}
];

describe("buildSeriesCsvRows", () => {
    it("emits one row per data point in long format", () => {
        expect(buildSeriesCsvRows(seriesWithoutError, "q (1/m)", "C (m³)")).toEqual([
            ["Subject", "Series", "q (1/m)", "C (m³)"],
            ["topo-1", "1D PSD", 1, 10],
            ["topo-1", "1D PSD", 2, 20],
            ["topo-2", "1D PSD", 3, 30]
        ]);
    });

    it("adds a standard-error column if any series carries one", () => {
        const rows = buildSeriesCsvRows([
            {subjectName: "average", seriesName: "1D PSD", x: [1], y: [10], stdErrY: [0.5]},
            {subjectName: "topo-1", seriesName: "1D PSD", x: [1], y: [10]}
        ], "x", "y");
        expect(rows[0]).toEqual(["Subject", "Series", "x", "y", "Standard error of y"]);
        expect(rows[1]).toEqual(["average", "1D PSD", 1, 10, 0.5]);
        // A series without an error leaves the column empty rather than shifting it
        expect(rows[2]).toEqual(["topo-1", "1D PSD", 1, 10, ""]);
    });

    it("exports only points that have both coordinates", () => {
        const rows = buildSeriesCsvRows([{subjectName: "s", seriesName: "t", x: [1, 2, 3], y: [10]}], "x", "y");
        expect(rows).toHaveLength(2);
    });

    it("tolerates missing subject and series names", () => {
        const rows = buildSeriesCsvRows([{subjectName: null, seriesName: null, x: [1], y: [2]}], "x", "y");
        expect(rows[1]).toEqual(["", "", 1, 2]);
    });
});

describe("buildSeriesTxt", () => {
    it("writes a commented header and whitespace-separated data", () => {
        const txt = buildSeriesTxt(seriesWithoutError, {
            title: "Power spectrum",
            xLabel: "q (1/m)",
            yLabel: "C (m³)"
        });
        const lines = txt.split("\n");
        expect(lines[0]).toBe("# Power spectrum");
        expect(lines[1]).toBe("# ==============");
        expect(lines).toContain("# topo-1 - 1D PSD");
        expect(lines).toContain("# Columns: q (1/m), C (m³)");
        expect(lines).toContain("1 10");
        expect(lines).toContain("2 20");
        expect(lines).toContain("3 30");
    });

    it("includes DOIs to cite when given", () => {
        const txt = buildSeriesTxt(seriesWithoutError, {
            title: "Power spectrum",
            xLabel: "x",
            yLabel: "y",
            dois: ["10.1000/xyz"]
        });
        expect(txt).toContain("PLEASE CITE THE FOLLOWING PAPERS");
        expect(txt).toContain("# - 10.1000/xyz");
    });

    it("documents and writes the standard error where present", () => {
        const txt = buildSeriesTxt([
            {subjectName: "average", seriesName: "1D PSD", x: [1], y: [10], stdErrY: [0.5]}
        ], {title: "T", xLabel: "x", yLabel: "y"});
        expect(txt).toContain("# Columns: x, y, standard error of y");
        expect(txt).toContain("1 10 0.5");
    });
});

describe("buildColumnsCsvRows", () => {
    const columns = [
        {key: "mean_pressures", title: "Normalized pressure p/E*"},
        {key: "total_contact_areas", title: "Fractional contact area A/A0"}
    ];

    it("emits one row per entry of the parallel arrays", () => {
        const rows = buildColumnsCsvRows([{
            label: "topo-1",
            data: {mean_pressures: [0.1, 0.2], total_contact_areas: [0.01, 0.03]}
        }], columns, "Measurement");
        expect(rows).toEqual([
            ["Measurement", "Normalized pressure p/E*", "Fractional contact area A/A0"],
            ["topo-1", 0.1, 0.01],
            ["topo-1", 0.2, 0.03]
        ]);
    });

    it("concatenates several groups under one header", () => {
        const rows = buildColumnsCsvRows([
            {label: "topo-1", data: {mean_pressures: [0.1], total_contact_areas: [0.01]}},
            {label: "topo-2", data: {mean_pressures: [0.2], total_contact_areas: [0.02]}}
        ], columns);
        expect(rows).toHaveLength(3);
        expect(rows[1][0]).toBe("topo-1");
        expect(rows[2][0]).toBe("topo-2");
    });

    it("leaves fields of a missing column empty", () => {
        const rows = buildColumnsCsvRows([{label: "topo-1", data: {mean_pressures: [0.1]}}], columns);
        expect(rows[1]).toEqual(["topo-1", 0.1, ""]);
    });

    it("emits only the header for an empty group", () => {
        expect(buildColumnsCsvRows([{label: "topo-1", data: {}}], columns)).toHaveLength(1);
    });
});

describe("buildTableCsvRows", () => {
    const columns = [
        {title: "Measurement"},  // rendered as a link, no `data` key
        {title: "Quantity", data: "quantity"},
        {title: "Value", data: "value"}
    ];

    it("skips columns that carry no plain value", () => {
        const rows = buildTableCsvRows([{quantity: "RMS height", value: 1.5}], columns);
        expect(rows).toEqual([
            ["Quantity", "Value"],
            ["RMS height", 1.5]
        ]);
    });

    it("prepends extra columns", () => {
        const rows = buildTableCsvRows(
            [{topography_name: "topo-1", quantity: "RMS height", value: 1.5}],
            columns,
            [{title: "Measurement", data: "topography_name"}]
        );
        expect(rows[0]).toEqual(["Measurement", "Quantity", "Value"]);
        expect(rows[1]).toEqual(["topo-1", "RMS height", 1.5]);
    });

    it("writes NaN as an empty field", () => {
        const rows = buildTableCsvRows([{quantity: "RMS height", value: NaN}], columns);
        expect(rows[1]).toEqual(["RMS height", ""]);
    });
});

describe("slugifyFilename", () => {
    it("lowercases and collapses non-alphanumerics", () => {
        expect(slugifyFilename("Power Spectral Density (1D)")).toBe("power-spectral-density-1d");
    });

    it("trims leading and trailing separators", () => {
        expect(slugifyFilename("--abc--")).toBe("abc");
    });

    it("falls back to a generic name if nothing is left", () => {
        expect(slugifyFilename("???")).toBe("download");
    });
});

describe("pollUntilTerminal", () => {
    const noSleep = () => Promise.resolve();

    it("returns as soon as the task succeeds", async () => {
        const states = [{task_state: "pe"}, {task_state: "st"}, {task_state: "su"}];
        let nbCalls = 0;
        const state = await pollUntilTerminal(() => {
            nbCalls++;
            return Promise.resolve(states.shift()!);
        }, {sleep: noSleep});
        expect(state.task_state).toBe("su");
        expect(nbCalls).toBe(3);
    });

    it("throws the reported error when the task fails", async () => {
        await expect(pollUntilTerminal(
            () => Promise.resolve({task_state: "fa", task_error: "disk full"}),
            {sleep: noSleep}
        )).rejects.toThrow("disk full");
    });

    it("throws a generic error when a failed task reports no error", async () => {
        await expect(pollUntilTerminal(
            () => Promise.resolve({task_state: "fa"}),
            {sleep: noSleep}
        )).rejects.toThrow("The task failed.");
    });

    it("gives up once the timeout is exceeded", async () => {
        let time = 0;
        await expect(pollUntilTerminal(
            () => Promise.resolve({task_state: "st"}),
            {sleep: noSleep, now: () => (time += 400), timeoutMs: 1000}
        )).rejects.toThrow("Timed out");
    });
});

describe("fetchArchiveUrl", () => {
    const noSleep = () => Promise.resolve();

    function http(states: any[]) {
        return {
            post: () => Promise.resolve({data: {url: "/manager/v2/zip-container/7/"}}),
            get: () => Promise.resolve({data: states.shift()})
        };
    }

    it("returns the file URL once the archive is ready", async () => {
        const url = await fetchArchiveUrl(http([
            {task_state: "st"},
            {task_state: "su", manifest: {file: "https://store/container.zip"}}
        ]), "/manager/v2/download-surface/1/", {sleep: noSleep});
        expect(url).toBe("https://store/container.zip");
    });

    it("polls the container URL returned by the POST", async () => {
        const polled: string[] = [];
        const client = {
            post: () => Promise.resolve({data: {url: "/manager/v2/zip-container/7/"}}),
            get: (url: string) => {
                polled.push(url);
                return Promise.resolve({data: {task_state: "su", manifest: {file: "f"}}});
            }
        };
        await fetchArchiveUrl(client, "/start/", {sleep: noSleep});
        expect(polled).toEqual(["/manager/v2/zip-container/7/"]);
    });

    it("throws if the finished task produced no file", async () => {
        await expect(fetchArchiveUrl(http([{task_state: "su"}]), "/start/", {sleep: noSleep}))
            .rejects.toThrow("no file was returned");
    });

    it("propagates a failed task", async () => {
        await expect(fetchArchiveUrl(http([{task_state: "fa", task_error: "boom"}]), "/start/", {sleep: noSleep}))
            .rejects.toThrow("boom");
    });
});

describe("pollUntilTerminal progress reporting", () => {
    const noSleep = () => Promise.resolve();

    it("reports every state it reads, so a caller can show progress", async () => {
        const states = [
            {task_state: "pe"},
            {task_state: "st", task_progress: 40, task_messages: ["Bundling 'topo-1'"]},
            {task_state: "su", task_progress: 100}
        ];
        const seen: any[] = [];
        await pollUntilTerminal(() => Promise.resolve(states.shift()!), {
            sleep: noSleep,
            onPoll: state => seen.push(state)
        });
        expect(seen.map(s => s.task_state)).toEqual(["pe", "st", "su"]);
        expect(seen[1].task_progress).toBe(40);
        expect(seen[1].task_messages).toEqual(["Bundling 'topo-1'"]);
    });

    it("reports the failing state before throwing", async () => {
        const seen: any[] = [];
        await expect(pollUntilTerminal(
            () => Promise.resolve({task_state: "fa", task_error: "boom"}),
            {sleep: noSleep, onPoll: state => seen.push(state)}
        )).rejects.toThrow("boom");
        expect(seen).toHaveLength(1);
    });

    it("passes progress updates through fetchArchiveUrl", async () => {
        const states = [
            {task_state: "st", task_progress: 50},
            {task_state: "su", manifest: {file: "https://store/c.zip"}}
        ];
        const seen: number[] = [];
        const url = await fetchArchiveUrl({
            post: () => Promise.resolve({data: {url: "/c/1/"}}),
            get: () => Promise.resolve({data: states.shift()})
        }, "/start/", {sleep: noSleep, onPoll: state => seen.push(state.task_progress ?? 0)});
        expect(url).toBe("https://store/c.zip");
        expect(seen).toEqual([50, 0]);
    });
});

describe("describeRequestError", () => {
    it("uses the message when there is no response", () => {
        expect(describeRequestError(new Error("Network Error"))).toBe("Network Error");
    });

    it("shows a plain-text error body as-is", () => {
        expect(describeRequestError({
            response: {status: 400, statusText: "Bad Request", data: "Invalid workflow result ID(s)."}
        })).toBe("Invalid workflow result ID(s).");
    });

    it("reduces a Django debug page to its title", () => {
        // The real thing is ~100 kB of markup; the title carries what matters.
        const page = `<!DOCTYPE html>\n<html lang="en">\n<head>\n  <title>ProgrammingError at `
            + `/analysis/v2/download-results/26,27,28/</title>\n  <style>html * { padding:0; }</style>\n`
            + `</head>\n<body>${"x".repeat(5000)}</body></html>`;
        const message = describeRequestError({
            response: {status: 500, statusText: "Internal Server Error", data: page}
        });
        expect(message).toBe("HTTP 500 Internal Server Error: ProgrammingError at "
            + "/analysis/v2/download-results/26,27,28/");
        expect(message).not.toContain("<");
    });

    it("falls back to the status for an HTML page without a title", () => {
        expect(describeRequestError({
            response: {status: 502, statusText: "Bad Gateway", data: "<html><body>nope</body></html>"}
        })).toBe("HTTP 502 Bad Gateway");
    });

    it("prefers the detail of a DRF error body", () => {
        expect(describeRequestError({
            response: {status: 403, statusText: "Forbidden", data: {detail: "Not allowed."}}
        })).toBe("Not allowed.");
    });

    it("serializes an object body that carries no detail", () => {
        expect(describeRequestError({
            response: {status: 400, statusText: "Bad Request", data: {name: ["required"]}}
        })).toBe('{"name":["required"]}');
    });

    it("falls back to the status for an empty body", () => {
        expect(describeRequestError({response: {status: 500, statusText: "", data: ""}})).toBe("HTTP 500");
    });

    it("caps and collapses long bodies", () => {
        const message = describeRequestError({
            response: {status: 400, statusText: "Bad Request", data: "line\n\nline ".repeat(200)}
        });
        expect(message.length).toBeLessThanOrEqual(300);
        expect(message).not.toContain("\n");
        expect(message.endsWith("…")).toBe(true);
    });
});
