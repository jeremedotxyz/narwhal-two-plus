# Development roadmap and release gates

The software is a working research reference. Physical sensor control starts after component selection, not by adding guessed register writes.

| Gate | Work and deliverables | Exit evidence |
|---|---|---|
| G0 Concept reference | Drawings, assumptions, geometry model, tests, replay and synthetic experiment | This repository and its verification record |
| G1 Optical feasibility | Ray trace TX/RX ports, validate field/filter/APD etendue and near-range overlap; close link budget including ambient/backscatter | Reviewed model and component trade study; revised achievable requirements |
| G2 Mechanical design | Solid CAD, windows, retainers, dual glands, corrosion isolation, FEA, tolerance and preload studies | Reviewed drawings, calculations and controlled BOM |
| G3 Electronics selection | Laser/galvo/APD/TIA/ADC/clock/FPGA/CPU/power components and exact interfaces | Schematics, PCB, interface control document and bench bring-up plan |
| G4 Embedded implementation | ADC capture, FPGA trigger/angle/time pipeline, waveform estimator, MCU health, authenticated control/session protocol and independent inhibit | Hardware-in-the-loop tests, fault-injection logs and reproducible firmware builds |
| G5 Calibration | Port/baseline/ray/ToF/temperature calibration; PTP/PPS/TAI synchronization | Traceable calibration data and uncertainty model |
| G6 Tank validation | Controlled range/reflectance/attenuation trials with archived raw waveforms | Bias/precision/dropout reports and bounded performance specification |
| G7 Environmental qualification | Hydrostatic tests under approved procedure, thermal soak, EMI/corrosion and connector cycling | Reviewed test reports and assigned operating limits |
| G8 Vehicle integration | Navigation time alignment, extrinsics, motion compensation and mapping | Survey reference comparison and deployment procedure |

## Embedded software work breakdown

- Define acquisition registers and DMA format against the chosen ADC/FPGA, with exact clock domains and overflow behavior.
- Implement calibrated emission monitoring, galvo encoder latching and windowed waveform acquisition.
- Develop/test a sub-sample delay estimator using measured pulses, saturation, backscatter and ambient conditions.
- Select whether host or FPGA performs bistatic reconstruction; preserve raw data for estimator validation.
- Implement health monitoring and an independent fail-off chain; assess laser hazards in dry and wet conditions.
- Negotiate protocol version, sensor/calibration ID, time epoch and clock validity before any capture session.
- Validate sensor packets against NWP1 or revise the host protocol jointly. The present UDP interface has no authenticated command channel.

A future hardware driver should live in a separate module with simulator/fake implementations and explicit startup, fault and shutdown semantics. Unit tests should cover protocol adapters; hardware-in-the-loop evidence must cover the actual device. No gate is satisfied by a placeholder firmware directory.
