# Source of the reference data under this directory

The "STC consensus" curves (median and interquartile range of power spectral
density and RMS height, for a rougher and a smoother reference surface) are
digitized from Figure 9 of:

> Pradhan, A., Müser, M.H., Miller, N., Abdelnabe, J.P., Afferrante, L.,
> Albertini, D., et al., Pastewka, L., Jacobs, T.D.B. "The Surface-Topography
> Challenge: A Multi-Laboratory Benchmark Study to Advance the
> Characterization of Topography." *Tribology Letters* **73**, 41 (2025).
> https://doi.org/10.1007/s11249-025-02014-y

Published under [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/),
which permits this reuse provided the source is credited (as done here and in
`frontend/utils/referenceData.ts`).

STC = "Surface-Topography Challenge", the multi-laboratory benchmark this
paper describes; "rougher"/"smoother" refer to the two reference surfaces
compared in Figure 9.

## Files

- `psd/{rougher,smoother}_surface_{median,lower_quartile,upper_quartile}.json`
  — `{x: [...], y: [...]}` with x = wavevector (m⁻¹), y = PSD (m³)
- `rms_height/{rougher,smoother}_surface_{median,lower_quartile,upper_quartile}.json`
  — `{x: [...], y: [...]}` with x = bandwidth (m), y = RMS height (m)

All values are raw SI units, straight from the digitized data; unit display
conversion happens client-side (see `referenceData.ts`).
