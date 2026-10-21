"""Proposed NWP1 point packet format; no hardware implements it yet."""
import math
import struct
import zlib
from .pipeline import Point, NO_RETURN, OUT_OF_RANGE, INVALID
RECORD = struct.Struct('<QfffffHHIHH')
HEADER = struct.Struct('<4sIHH')
CRC = struct.Struct('<I')
MAX_POINTS = 32
assert RECORD.size == 40

def validate_point(p):
    if not (type(p.timestamp_ns) is int and 0 <= p.timestamp_ns < 2**64 and type(p.line_id) is int and 0 <= p.line_id < 2**32):
        raise ValueError('timestamp or line ID outside wire range')
    if not all(type(v) is int and 0 <= v <= 65535 for v in (p.intensity,p.quality,p.status)):
        raise ValueError('invalid integer field')
    if not math.isfinite(p.angle_rad) or abs(p.angle_rad) >= math.pi/2:
        raise ValueError('invalid scan angle')
    coords=(p.x,p.y,p.z,p.range_tx_m)
    invalid=p.quality & (NO_RETURN|OUT_OF_RANGE|INVALID)
    if invalid:
        if not all(math.isnan(v) for v in coords):
            raise ValueError('invalid point must carry NaN coordinates/range')
    elif not all(math.isfinite(v) for v in coords) or p.range_tx_m <= 0:
        raise ValueError('valid point must have finite positive range')

def encode_point(p):
    validate_point(p)
    try:
        return RECORD.pack(p.timestamp_ns,p.x,p.y,p.z,p.range_tx_m,p.angle_rad,p.intensity,p.quality,p.line_id,p.status,0)
    except (OverflowError,struct.error) as e:
        raise ValueError('point outside wire representation') from e

def decode_point(data):
    if len(data)!=RECORD.size:
        raise ValueError('record must contain 40 bytes')
    t,x,y,z,r,a,i,q,line,status,reserved=RECORD.unpack(data)
    if reserved:
        raise ValueError('reserved field must be zero')
    p=Point(t,x,y,z,r,i,a,line,q,status);validate_point(p);return p

def encode_packet(sequence,points):
    if type(sequence) is not int or not 0 <= sequence < 2**32 or not 1 <= len(points) <= MAX_POINTS:
        raise ValueError('invalid sequence or packet point count')
    data=HEADER.pack(b'NWP1',sequence,len(points),1)+b''.join(encode_point(p) for p in points)
    return data+CRC.pack(zlib.crc32(data))

def decode_packet(data):
    if len(data)<HEADER.size+RECORD.size+CRC.size:
        raise ValueError('truncated packet')
    magic,seq,count,version=HEADER.unpack_from(data)
    if magic!=b'NWP1' or version!=1 or not 1<=count<=MAX_POINTS:
        raise ValueError('unsupported packet header')
    if len(data)!=HEADER.size+count*RECORD.size+CRC.size:
        raise ValueError('packet length/count mismatch')
    if CRC.unpack(data[-4:])[0] != zlib.crc32(data[:-4]):
        raise ValueError('CRC mismatch')
    return seq,[decode_point(data[12+i*40:12+(i+1)*40]) for i in range(count)]
