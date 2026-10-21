# Hardware design record

Assembly **NEREID-532 revision A** is the sensor concept within Narwhal Two Plus. Original files are retained as delivered. Drawings are vector PDFs with a blueprint palette, sheet borders, view labels, dimensions, callouts and an assembly schedule. They are engineering-style concept drawings, not a complete manufacturing CAD package.

## Drawing register

| Sheet | Identifier | Contents |
|---|---|---|
| 1 | NRD-532-001 | Longitudinal schematic section, front elevation, underside mounting view, functional assembly schedule |
| 2 | NRD-532-002 | Functional optical/electrical blocks, logical connector assignment, scan/refraction geometry and timing notes |
| 3 | NRD-532-003 | Separate sensor data, calculations, point-output proposal and acceptance plan |

The drawing's displayed view scale is a procedural drawing scale. Dimensions are nominal millimeters; use the labeled numbers rather than measuring the PDF. The source does not generate an actual machining solid. Surface finishes, fits, machining tolerances, bolt torque and gland cross sections have not been released.

## Pressure assembly and seal concept

Tube OD140/ID120, body length 320, flange D160 and 359 connector envelope are interface assumptions. Two removable caps would use dual radial body seals with inter-seal monitoring. The current drawing does not dimension the glands or provide an independent retention/load path design. Eight front-retainer fasteners on a D146 circle are shown schematically. Their size/number do not establish structural adequacy.

Transmit D32 and receive D60 clear windows are sapphire targets; window blanks are larger than clear aperture. Their seat footprint and separation must be checked for interference with each other, housing bore and retaining fasteners once actual retainer geometry is modeled. Thicknesses are deliberately unspecified until external-pressure and optical analyses are completed.

The 300 m target corresponds to approximately 3.02 MPa differential pressure under the stated seawater assumptions. No proof pressure, certification or rated depth is assigned. Titanium Grade 5 is provisional, and procurement specifications require traceable material standards and approved processing.

## Optical allocation

TX: 532 nm pulsed source, beam pickoff, collimator and galvo behind D32 clear window. RX: D60 window, collection lens, narrowband filter, silicon APD, TIA, limiter and digitizer. Source pulse energy, wavelength and bandwidth are targets; no vendor has been chosen.

The field target is +/-15 degrees in water. The receiver full field is provisionally >=40 degrees. A 1 nm interference filter over this field is an unresolved feasibility issue; passband shift and receiver etendue must be modeled. A ray trace must also prove scan clearance at the transmit aperture, overlap across the full gated range, window-induced aberration, stray-light rejection and feasible APD imaging. The report's homogeneous model uses calibrated external ray origins, not literal internal mirror coordinates.

## Electrical interfaces

See `interfaces.csv` and drawing sheet 2. Input power target is 18-30 VDC with 35 W nominal/60 W peak allocation. Proposed J1 is 12 contacts: power pair, two Ethernet pairs, differential PPS, isolated hardware enable and RS-485 service. The actual connector, current rating, mating cycles, cable, isolation voltages and shielding scheme remain unselected.

PPS alone does not identify an absolute epoch. A host time-distribution/session protocol must establish TAI epoch and measured clock quality. No PTP implementation is included. Ethernet magnetics, analog grounding, EMI protections, ADC clock generation and FPGA I/O require a schematic and layout.

The independent emission permit and fail-off fault chain must be designed in hardware. The software cannot verify interlock functionality and exposes no command to emit light. Laser accessible-emission classification has not been determined.

## Assembly schedule and manufacturing gates

`bom.csv` is a functional work breakdown with provisional materials, not an orderable BOM. No part numbers or costs are invented. A release needs optical prescriptions, component selections, solid CAD, tolerance analysis, pressure/window calculations, seal handbook compliance, fastener preload/load paths, assembly procedures, calibration fixtures, test protocols and revision approval.

Mass, buoyancy, center of gravity and thermal resistance remain TBD. Do not infer them from the two-dimensional sketch or from the power allocation alone.
