"""Local research CLI. Provides no command that enables a laser."""
import argparse
import csv
import json
import math
from pathlib import Path
import socket
import sys
from .config import Config
from .physics import derived_metrics
from .pipeline import Point, simulate, reconstruct
from .protocol import decode_packet

def write_jsonl(path, records):
    with open(path,'w',encoding='utf-8') as stream:
        for r in records:
            stream.write(json.dumps(r,allow_nan=False,sort_keys=True)+'\n')

def read_jsonl(path):
    with open(path,encoding='utf-8') as stream:
        for i,line in enumerate(stream,1):
            if line.strip():
                try: yield json.loads(line)
                except json.JSONDecodeError as e: raise ValueError(f'{path}:{i}: invalid JSON') from e

def point_dict_to_object(d):
    d=dict(d)
    for k in ('x','y','z','range_tx_m'):
        if d.get(k) is None:d[k]=math.nan
    p=Point(**d)
    from .protocol import validate_point
    validate_point(p)
    return p

def export(points,prefix):
    prefix=Path(prefix);prefix.parent.mkdir(parents=True,exist_ok=True)
    good=[p for p in points if math.isfinite(p.z)]
    fields=list(Point.__dataclass_fields__)
    with open(str(prefix)+'.csv','w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(p.to_dict() for p in points)
    with open(str(prefix)+'.ply','w',encoding='ascii') as f:
        f.write(f'ply\nformat ascii 1.0\ncomment Narwhal concept; see metadata for provenance\nelement vertex {len(good)}\nproperty float x\nproperty float y\nproperty float z\nproperty ushort intensity\nend_header\n')
        for p in good:f.write(f'{p.x:.7f} {p.y:.7f} {p.z:.7f} {p.intensity}\n')
    write_jsonl(str(prefix)+'.jsonl',(p.to_dict() for p in points))
    return {'records':len(points),'valid':len(good),'rejected':len(points)-len(good)}

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',help='JSON calibration/configuration (default: concept assumptions)')
    subs=parser.add_subparsers(dest='command',required=True)
    sim=subs.add_parser('simulate',help='Generate synthetic raw returns and reconstruct points')
    sim.add_argument('--out',default='runs/demo');sim.add_argument('--lines',type=int,default=2)
    sim.add_argument('--plane-m',type=float,default=5);sim.add_argument('--seed',type=int,default=532)
    replay=subs.add_parser('replay',help='Reconstruct raw JSONL returns')
    replay.add_argument('input');replay.add_argument('--out',default='runs/replay')
    receive=subs.add_parser('receive',help='Receive proposed NWP1 packets; no control channel')
    receive.add_argument('--host',default='127.0.0.1');receive.add_argument('--port',type=int,default=53200)
    receive.add_argument('--packets',type=int,default=1);receive.add_argument('--timeout',type=float,default=5)
    receive.add_argument('--out',default='runs/capture')
    subs.add_parser('metrics',help='Print first-order concept calculations')
    args=parser.parse_args(argv)
    try:
        config=Config.load(args.config) if args.config else Config()
        if args.command=='metrics':
            print(json.dumps(derived_metrics(config),indent=2));return 0
        prefix=Path(args.out);prefix.parent.mkdir(parents=True,exist_ok=True)
        if args.command=='simulate':
            events=list(simulate(config,args.lines,args.plane_m,args.seed))
            write_jsonl(str(prefix)+'.raw.jsonl',events)
            points=[reconstruct(e,config) for e in events]
            provenance={'kind':'synthetic','seed':args.seed,'plane_z_m':args.plane_m,'time_basis':'SIM_RELATIVE'}
        elif args.command=='replay':
            events=list(read_jsonl(args.input));points=[reconstruct(e,config) for e in events]
            provenance={'kind':'reconstructed','source':str(args.input),'simulated_events':sum(e['simulated'] for e in events)}
        else:
            if args.packets<1 or not math.isfinite(args.timeout) or args.timeout<=0 or not 0<args.port<65536:
                raise ValueError('invalid capture bounds')
            points=[];sequences=[];peers=[]
            with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as sock:
                sock.bind((args.host,args.port));sock.settimeout(args.timeout)
                for _ in range(args.packets):
                    data,peer=sock.recvfrom(65535);seq,batch=decode_packet(data)
                    points.extend(batch);sequences.append(seq);peers.append(list(peer))
            provenance={'kind':'udp-capture','sequences':sequences,'peers':peers,'sequence_policy':'arrival order; gaps/duplicates not corrected'}
        summary=export(points,prefix)
        from dataclasses import asdict
        metadata={'software_version':'0.1.0','config':asdict(config),'provenance':provenance,'summary':summary,
                  'evidence_status':'reference software; no hardware performance validated'}
        Path(str(prefix)+'.metadata.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(summary,sort_keys=True));return 0
    except (ValueError,TypeError,KeyError,OSError) as e:
        print(f'error: {e}',file=sys.stderr);return 2
