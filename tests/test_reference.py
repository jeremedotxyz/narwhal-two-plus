import contextlib
from dataclasses import replace
import io
import json
import math
from pathlib import Path
import socket
import tempfile
import threading
import unittest
from narwhal.config import Config
from narwhal.physics import C0, bistatic_range, path_length, air_to_water_angle
from narwhal.pipeline import Point, simulate, reconstruct, NO_RETURN, INVALID, OUT_OF_RANGE, SIMULATED, UNSYNCED
from narwhal.protocol import encode_point, decode_point, encode_packet, decode_packet
from narwhal.cli import main

class GeometryTests(unittest.TestCase):
    def test_independent_ellipsoid_cases(self):
        tx=(0,-.03,0);rx=(0,.03,0)
        for point in [(1,.2,5),(-2,-.4,8),(0,-.03,1),(0,1.1,3)]:
            r=math.dist(point,tx);ray=tuple((point[i]-tx[i])/r for i in range(3))
            tof=path_length(point,tx,rx)*1.34/C0*1e9
            self.assertAlmostEqual(bistatic_range(tof,ray,tx,rx),r,places=11)
    def test_zero_baseline_reduces_to_monostatic(self):
        self.assertAlmostEqual(bistatic_range(10*1.34/C0*1e9,(0,0,1),(0,0,0),(0,0,0)),5)
    def test_impossible_delay(self):
        with self.assertRaises(ValueError):bistatic_range(.01,(0,0,1),(0,0,0),(0,.06,0))
    def test_refraction_independent_snell(self):
        a=math.radians(20);b=air_to_water_angle(a)
        self.assertAlmostEqual(math.sin(a),1.333*math.sin(b));self.assertLess(b,a)
    def test_invalid_config(self):
        for d in [dict(n_group=float('nan')),dict(samples_per_line=1),dict(dropout_probability=2),dict(baseline_m=2),dict(pulse_rate_hz=1.5),dict(n_phase=.9),dict(schema_version=2)]:
            with self.subTest(d=d),self.assertRaises(ValueError):Config(**d)

class PipelineTests(unittest.TestCase):
    def test_plane_without_noise(self):
        c=Config(timing_sigma_ns=0,dropout_probability=0,samples_per_line=12)
        for e in simulate(c,lines=2):
            p=reconstruct(e,c);self.assertAlmostEqual(p.z,5,places=11)
            self.assertEqual(p.quality,SIMULATED|UNSYNCED)
    def test_repeatable_noise(self):
        c=Config(samples_per_line=16)
        self.assertEqual(list(simulate(c,seed=8)),list(simulate(c,seed=8)))
        self.assertNotEqual(list(simulate(c,seed=8)),list(simulate(c,seed=9)))
    def test_dropout_invalid_and_gate(self):
        c=Config();e=next(simulate(c))
        for delay,flag in [(None,NO_RETURN),(-1,INVALID),(1000,OUT_OF_RANGE)]:
            p=reconstruct(dict(e,tof_ns=delay),c)
            self.assertTrue(p.quality & flag);self.assertTrue(math.isnan(p.x))
    def test_schema_and_angle_rejected(self):
        e=next(simulate(Config()))
        for patch in [dict(schema_version=2),dict(simulated='yes'),dict(angle_rad=2),dict(timestamp_ns=-1),dict(intensity=70000)]:
            with self.subTest(patch=patch),self.assertRaises(ValueError):reconstruct(dict(e,**patch),Config())

class WireTests(unittest.TestCase):
    def setUp(self):self.p=Point(123,1,2,3,4,500,.1,7,48)
    def test_layout_and_roundtrip(self):
        b=encode_point(self.p);self.assertEqual(len(b),40);self.assertEqual(b[:8],(123).to_bytes(8,'little'))
        p=decode_point(b);self.assertEqual(p.timestamp_ns,123);self.assertAlmostEqual(p.angle_rad,.1,places=6)
    def test_crc_and_length_fail_closed(self):
        data=encode_packet(9,[self.p]);self.assertEqual(decode_packet(data)[0],9)
        bad=bytearray(data);bad[20]^=1
        for b in [bytes(bad),data[:-1],b'garbage']:
            with self.assertRaises(ValueError):decode_packet(b)
    def test_nonzero_reserved_rejected(self):
        data=bytearray(encode_point(self.p));data[-1]=1
        with self.assertRaises(ValueError):decode_point(data)
    def test_nan_rules(self):
        invalid=replace(self.p,x=math.nan,y=math.nan,z=math.nan,range_tx_m=math.nan,quality=NO_RETURN)
        self.assertTrue(math.isnan(decode_point(encode_point(invalid)).z))
        with self.assertRaises(ValueError):encode_point(replace(self.p,x=math.nan))
    def test_packet_bounds(self):
        for seq,points in [(-1,[self.p]),(0,[]),(0,[self.p]*33)]:
            with self.assertRaises(ValueError):encode_packet(seq,points)

class IntegrationTests(unittest.TestCase):
    def test_cli_simulate_replay(self):
        with tempfile.TemporaryDirectory() as tmp,contextlib.redirect_stdout(io.StringIO()):
            prefix=str(Path(tmp)/'scan');replay=str(Path(tmp)/'replay')
            self.assertEqual(main(['simulate','--out',prefix,'--lines','1']),0)
            self.assertEqual(main(['replay',prefix+'.raw.jsonl','--out',replay]),0)
            self.assertEqual(Path(prefix+'.jsonl').read_bytes(),Path(replay+'.jsonl').read_bytes())
            self.assertEqual(json.loads(Path(prefix+'.metadata.json').read_text())['summary']['records'],1000)
            self.assertTrue(Path(prefix+'.ply').read_text().startswith('ply\n'))
    def test_udp_loopback(self):
        with tempfile.TemporaryDirectory() as tmp,contextlib.redirect_stdout(io.StringIO()):
            with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as probe:
                probe.bind(('127.0.0.1',0));port=probe.getsockname()[1]
            packet=encode_packet(0,[Point(1,0,0,5,5,2,0,0,48)])
            done=threading.Event()
            def send():
                with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as sock:
                    while not done.wait(.02):sock.sendto(packet,('127.0.0.1',port))
            t=threading.Thread(target=send);t.start()
            try: result=main(['receive','--port',str(port),'--timeout','2','--out',str(Path(tmp)/'rx')])
            finally:done.set();t.join()
            self.assertEqual(result,0)
            meta=json.loads((Path(tmp)/'rx.metadata.json').read_text());self.assertEqual(meta['summary']['records'],1)
    def test_bad_input_exit(self):
        with tempfile.TemporaryDirectory() as tmp,contextlib.redirect_stderr(io.StringIO()):
            path=Path(tmp)/'bad.jsonl';path.write_text('{bad json}\n')
            self.assertEqual(main(['replay',str(path),'--out',str(Path(tmp)/'bad')]),2)
            self.assertEqual(main(['simulate','--lines','0','--out',str(Path(tmp)/'none')]),2)

if __name__=='__main__':unittest.main()
