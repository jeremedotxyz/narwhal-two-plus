# Verification and evidence record

Date: 21 October 2026. Version: 0.1.0. Scope: reference software and concept documentation.

## Completed checks

The local reference suite passed **17 tests** on the bundled Python runtime. One test uses a real UDP socket bound to 127.0.0.1; a sandbox exception was needed for localhost binding. No physical sensor and no remote host participated.

| Area | Evidence |
|---|---|
| Geometry | Independently constructed oblique points recover their distance along the TX ray; monostatic limit agrees |
| Refraction helper | Snell relation and reduced water-side angle checked |
| Config validation | NaN, unsupported versions, noninteger rates, invalid baseline/scan/dropout rejected |
| Synthetic reconstruction | Zero-noise plane recovered; seed repeatability and changed-seed divergence checked |
| Invalid returns | Missing, impossible and out-of-range delays produce flags and invalid coordinates |
| Wire format | Exact byte count, little-endian timestamp and float round trip checked |
| Corruption | CRC errors, truncation, reserved bytes and impossible packet sizes rejected |
| Export/replay | Raw replay yields byte-identical reconstructed JSONL for a fixed file |
| UDP receiver | A generated packet traverses a localhost socket and appears in exported capture metadata |
| CLI failures | Malformed JSON and invalid line counts return failure code 2 |
| Drawings | All three rendered sheets visually inspected during initial creation; labels and data sheet reviewed |

The Actions workflow runs unit/integration tests on Python 3.10 and 3.12 plus a simulation/replay smoke test. Local execution does not itself establish the status of a GitHub Actions run; consult that run's actual result.

## Numerical experiment

See [committed result](../examples/reference-results.md), configuration and reproducibility script. Default seed 532 produces 2,000 synthetic shots with 1,952 valid returns and 48 modeled dropouts. Plane-depth sample sigma is approximately 0.011041 m under the assumed 0.1 ns timing noise. This is a simulator result and does not verify the 20 mm hardware objective.

## Evidence absent

No ray-trace feasibility closure, full radiative transfer model, APD noise budget, ADC waveform timing study, pressure analysis, seal/window qualification, thermal characterization, physical time synchronization, hardware protocol test, laser classification or tank/subsea measurement has been performed. No PCB, firmware, FPGA bitstream or manufacturing CAD is included.

## Hardware acceptance gates

1. Freeze reference conditions and calibration model before claiming range/precision.
2. Establish traced reference distances and reflectance, independent water attenuation measurements and environmental logging.
3. Test at 1/5/10/15 m, reporting total shots, valid shots, bias, dispersion and dropout separately.
4. Complete pressure/window/fatigue calculations and approved hydrostatic procedure before depth claims.
5. Test thermal drift, fault inhibit, watchdog, isolation, EMI and leakage on actual electronics.
6. Archive raw data, analysis code, calibration files and uncertainty budget with each measured claim.
