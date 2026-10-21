# Proposed NWP1 data protocol

**Status: host reference specification. No hardware implementation or compatibility claim.** All integers and IEEE 754 binary32 values are little-endian. Never reinterpret native C structs without explicit packing and endianness checks.

## Point record: 40 bytes

| Byte offset | Width | Field | Type / unit |
|---|---|---|---|
| 0 | 8 | timestamp_ns | uint64, nanoseconds |
| 8 | 4 | x | float32, m |
| 12 | 4 | y | float32, m |
| 16 | 4 | z | float32, m |
| 20 | 4 | range_tx_m | float32, m along TX ray |
| 24 | 4 | angle_rad | float32, water-side angle |
| 28 | 2 | intensity | uint16, arbitrary counts |
| 30 | 2 | quality | uint16 bitmask |
| 32 | 4 | line_id | uint32 |
| 36 | 2 | status | uint16, reserved health word in v0.1.0 |
| 38 | 2 | reserved | uint16, must be zero |

Python layout: `struct.Struct('<QfffffHHIHH')`. Timestamp epoch when synchronized is 1970-01-01 00:00:00 TAI. Simulator timestamps begin at zero and are explicitly UNSYNCED/SIMULATED. Sensor frame is right handed: +X starboard, +Y down, +Z forward, origin at optical-center midpoint. Range is measured from TX, not from this midpoint.

For NO_RETURN, OUT_OF_RANGE or INVALID, all four coordinate/range floats must be NaN. A point without those flags must have finite coordinates and positive finite range. Angle remains finite, including on invalid returns. Float32 export loses precision relative to the Python reconstruction's float64 intermediates.

## Quality flags

| Bit | Hex | Meaning |
|---|---|---|
| 0 | 0x0001 | NO_RETURN |
| 1 | 0x0002 | OUT_OF_RANGE |
| 2 | 0x0004 | SATURATED intensity |
| 3 | 0x0008 | INVALID delay |
| 4 | 0x0010 | UNSYNCED timestamp |
| 5 | 0x0020 | SIMULATED |

Upper bits are reserved for future specification. The decoder preserves unknown quality/status bits rather than silently stripping them; applications must not assume those bits are defined. Status is emitted as zero by the current reconstruction pipeline. Laser state, leak and thermal health need a separately versioned health specification.

## UDP packet envelope

| Offset | Width | Field |
|---|---|---|
| 0 | 4 | ASCII `NWP1` magic |
| 4 | 4 | uint32 sequence |
| 8 | 2 | uint16 point count, 1-32 |
| 10 | 2 | uint16 schema version, exactly 1 |
| 12 | 40 x count | Contiguous point records |
| 12 + 40 x count | 4 | uint32 CRC-32 over header and payload |

CRC uses Python `zlib.crc32`, the standard reflected CRC-32 with polynomial 0xEDB88320. The stored value is unsigned little-endian. Sequence wraps modulo 2^32. At 32 points a packet is 1,296 bytes, below a 1,500-byte Ethernet MTU even with IPv4/UDP headers; network paths with lower MTUs need separate handling.

The codec rejects unsupported header versions, zero or excessive counts, length mismatch, nonzero reserved record fields, invalid values and CRC errors. The receiver logs arrival sequence and sender addresses but does not reorder or deduplicate. Use the logs to detect loss. There is no authentication, retransmission, calibration negotiation, discovery, health channel or command protocol.

## Throughput and implementation boundary

40 bytes x 20,000 points/s = 800,000 bytes/s of point payload. At 32 points/packet this is 625 packets/s and about 810,000 bytes/s including this envelope, excluding network overhead. ADC waveform bandwidth is much larger and is not streamed by this format.

The 12-contact J1 assignment in the drawings is an electrical concept, not a packet transport implementation. An FPGA/CPU must estimate delays, latch angles, reconstruct or transmit raw measurements and produce this exact protocol before this receiver can consume a physical sensor stream. Raw JSONL replay is a separate host interface, not the NWP1 wire format.
