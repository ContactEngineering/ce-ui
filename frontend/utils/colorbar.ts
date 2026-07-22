export interface ColorbarTick {
    /** Position of the tick, in percent measured from the top (maximum). */
    relpos: number;
    /** Tick label. */
    label: string;
}

/**
 * Compute tick positions and labels for a colorbar spanning the value range
 * [min, max]. Tick distances are round (powers of ten, doubled until at most
 * `maxTicks` ticks remain) and ticks that would sit exactly on the ends of
 * the bar are omitted.
 */
export function computeColorbarTicks(min: number, max: number, maxTicks: number = 15): ColorbarTick[] {
    const log10TickDist = Math.round(Math.log10(max - min)) - 1;
    const fractionDigits = log10TickDist > 0 ? 0 : -log10TickDist;
    let tickDist = 10 ** log10TickDist;
    let nbTicks = Math.trunc((max - min) / tickDist) + 1;

    while (nbTicks > maxTicks) {
        tickDist *= 2;
        nbTicks = Math.trunc((max - min) / tickDist) + 1;
    }

    const ticks: ColorbarTick[] = [];
    for (let i = 0; i < nbTicks; i++) {
        const v = Math.trunc(min / tickDist) * tickDist + tickDist * i;
        const relpos = (max - v) * 100 / (max - min);
        if (relpos > 0 && relpos < 100) {
            ticks.push({
                relpos: relpos,
                label: v.toFixed(fractionDigits)
            });
        }
    }
    return ticks;
}
