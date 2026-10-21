from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from math import sin,cos,pi
import os
from pathlib import Path
O=str(Path(__file__).resolve().parents[1] / 'drawings'); os.makedirs(O,exist_ok=True); W,H=1684,1191
c=canvas.Canvas(O+'/NEREID-532_concept_blueprint.pdf',pagesize=(W,H))
c.setTitle('NEREID-532 | Underwater LiDAR concept | Engineering drawing set')
BG='#09233D'; INK='#DCECF6'; DIM='#83B7D2'; ACC='#6DE1DE'
def line(x,y,X,Y,w=.8,col=INK,dash=None):
 c.setStrokeColor(HexColor(col));c.setLineWidth(w);c.setDash(dash or []);c.line(x,y,X,Y);c.setDash([])
def rect(x,y,w,h,col=INK,fill=None,lw=.8):
 c.setStrokeColor(HexColor(col));c.setLineWidth(lw)
 if fill:c.setFillColor(HexColor(fill))
 c.rect(x,y,w,h,stroke=1,fill=bool(fill))
def circ(x,y,r,col=INK,w=.8):
 c.setStrokeColor(HexColor(col));c.setLineWidth(w);c.circle(x,y,r,stroke=1,fill=0)
def txt(x,y,t,s=10,col=INK,font='Courier'):
 c.setFillColor(HexColor(col));c.setFont(font,s);c.drawString(x,y,t)
def lines(x,y,ss,s=11,lead=17,col=INK):
 for i,t in enumerate(ss):txt(x,y-i*lead,t,s,col)
def arrow(x,y,X,Y,col=ACC,w=1):
 line(x,y,X,Y,w,col);a=__import__('math').atan2(Y-y,X-x)
 for d in [-.45,.45]:line(X,Y,X-7*cos(a+d),Y-7*sin(a+d),w,col)
def dim(x,y,X,Y,label,off=22):
 if y==Y:
  yy=y+off;line(x,y,x,yy+7,.5,DIM);line(X,Y,X,yy+7,.5,DIM);line(x,yy,X,yy,.5,DIM)
  for xx in [x,X]:line(xx-4,yy-4,xx+4,yy+4,.7,DIM)
  txt((x+X)/2-len(label)*3,yy+6,label,10,DIM)
 else:
  xx=x+off;line(x,y,xx+7,y,.5,DIM);line(X,Y,xx+7,Y,.5,DIM);line(xx,y,xx,Y,.5,DIM)
  for yy in [y,Y]:line(xx-4,yy-4,xx+4,yy+4,.7,DIM)
  c.saveState();c.translate(xx-7,(y+Y)/2-len(label)*3);c.rotate(90);txt(0,0,label,10,DIM);c.restoreState()
def center(x,y,X,Y):line(x,y,X,Y,.5,DIM,[14,4,2,4])
def panel(x,y,w,h,title):
 rect(x,y,w,h,DIM);txt(x+14,y+h-24,title,13,ACC,'Courier-Bold');line(x,y+h-36,x+w,y+h-36,.5,DIM)
def tag(n,x,y,X,Y):
 circ(x,y,11,ACC);txt(x-6,y-4,f'{n:02}',10,ACC);line(x+11,y,X,Y,.6,DIM)
def base(n,title,sub):
 c.setFillColor(HexColor(BG));c.rect(0,0,W,H,fill=1,stroke=0)
 for x in range(32,W-31,24):line(x,32,x,H-32,.15,'#17334C')
 for y in range(32,H-31,24):line(32,y,W-32,y,.15,'#17334C')
 rect(32,32,W-64,H-64,DIM,lw=1)
 txt(52,H-67,'NEREID / 532',25,INK,'Courier-Bold');txt(52,H-89,'SUBSEA OPTICAL METROLOGY / CONCEPT ENGINEERING',10,DIM)
 txt(575,H-64,title,20,INK,'Courier-Bold');txt(575,H-87,sub,10,DIM)
 line(32,H-105,W-32,H-105,1,DIM)
 for i in range(1,9):txt(32+(W-64)*i/9,H-22,str(i),9,DIM)
 for i,a in enumerate('ABCDEFG'):txt(17,H-165-i*135,a,9,DIM)
 rect(32,32,W-64,77,DIM)
 for x in [1050,1290,1460]:line(x,32,x,109,.8,DIM)
 txt(48,88,'CONCEPT ONLY / NOT RELEASED FOR MANUFACTURE',12,ACC,'Courier-Bold')
 txt(48,68,'ALL DIMENSIONS mm. NUMERIC DIMENSIONS GOVERN. DO NOT SCALE PDF.',10)
 txt(48,49,'Assumed geometry; pressure, optics, thermal performance and laser safety require validation.',9,DIM)
 txt(1065,87,'DRAWING  NRD-532-'+str(n).zfill(3),11);txt(1065,65,'REV A / 2026-10-21',10);txt(1065,46,'STATUS: PRELIMINARY',10)
 txt(1305,86,'FORMAT A2',11);txt(1305,65,'VIEW SCALE: AS NOTED',9);txt(1305,46,'UNITS: mm / SI',10)
 txt(1475,84,f'SHEET {n} OF 3',14,ACC,'Courier-Bold');txt(1475,62,'ENGINEERING CONCEPT',9);txt(1475,45,'NO TEST DATA',10)
def table(x,y,width,headers,rows,cols,rowh=25):
 # top coordinate
 edges=[x]
 for f in cols:edges.append(edges[-1]+width*f)
 total=rowh*(len(rows)+1);rect(x,y-total,width,total,DIM)
 for e in edges[1:-1]:line(e,y-total,e,y,.5,DIM)
 for i in range(1,len(rows)+1):line(x,y-i*rowh,x+width,y-i*rowh,.4,DIM)
 for j,v in enumerate(headers):txt(edges[j]+9,y-17,v,10,ACC,'Courier-Bold')
 for i,row in enumerate(rows):
  for j,v in enumerate(row):txt(edges[j]+9,y-(i+1)*rowh-17,str(v),9)
# SHEET 1
base(1,'GENERAL ARRANGEMENT & PRESSURE BOUNDARY','Orthographic views / longitudinal section / mounting interface / parts schedule')
panel(52,630,1020,440,'01  LONGITUDINAL SECTION A-A / NOMINAL GEOMETRY / DISPLAY SCALE 2 pt:mm')
x=220;y=830
# body extends 320 mm at 2 pt/mm
rect(x,y-140,640,280,lw=1.7);rect(x+36,y-120,568,240,lw=1.2)
rect(x,y-160,36,320,lw=1.7);rect(x+604,y-160,36,320,lw=1.7)
# section wall hatch
for xx in range(x+40,x+600,13):
 line(xx,y+120,xx+20,y+140,.45,DIM);line(xx,y-140,xx+20,y-120,.45,DIM)
for xx in [x+20,x+616]:
 for yy in range(y-150,y+150,13):line(xx-14,yy,xx+12,yy+12,.45,DIM)
# optical penetrations schematically arranged in section
rect(x-3,y+28,22,64,ACC,fill=BG,lw=1.6);rect(x-3,y-120,22,120,ACC,fill=BG,lw=1.6)
# seals
for xx in [x+42,x+55,x+585,x+598]:
 for yy in [y-120,y+120]:rect(xx,yy-4,5,8,ACC)
# internals
rect(340,865,157,44);txt(350,882,'532 nm LASER',11)
rect(285,866,30,42);line(296,866,309,908,1.5,ACC);txt(276,923,'GALVO',9,DIM)
arrow(340,888,315,888);arrow(285,888,178,888)
rect(278,716,14,95,ACC);rect(305,733,8,62,ACC);rect(337,748,32,32);txt(381,758,'APD / TIA',10)
arrow(178,764,278,764);arrow(292,764,337,764)
rect(470,726,135,65);txt(480,762,'ADC / FPGA',11);txt(480,744,'TIMING ENGINE',9)
rect(650,746,132,80);txt(661,794,'DC/DC + CPU',11);txt(661,775,'ISOLATED I/O',9)
line(369,764,470,764,.8,ACC);line(605,764,650,764,.8,ACC)
rect(272,699,522,12,DIM);txt(500,680,'OPTICAL BENCH / THERMAL SPREADER',9,DIM)
rect(860,795,60,64);rect(920,806,18,42);txt(882,875,'J1',11)
center(190,830,960,830)
dim(220,990,860,990,'320 BODY',18);dim(220,1016,938,1016,'359 CONNECTOR ENVELOPE',18)
dim(860,690,860,970,'D140',100)
tag(1,155,946,224,940);tag(2,158,912,222,895);tag(3,151,721,222,744);tag(4,528,936,492,905);tag(5,591,858,552,790);tag(6,782,905,760,826);tag(7,965,742,930,807)
txt(70,649,'SECTION IS SCHEMATIC: component envelopes / retainers and wire routes not to fabrication detail.',9,DIM)
panel(1090,630,542,440,'02  FRONT ELEVATION / VIEW FROM WATER')
cx=1361;cy=855;scale=1.45
for r in [80,70,60]:circ(cx,cy,r*scale,w=1.2 if r==80 else .6)
for a in range(0,360,45):
 xx=cx+73*scale*cos(a*pi/180);yy=cy+73*scale*sin(a*pi/180);circ(xx,yy,4.5);circ(xx,yy,7)
# windows separated vertically for consistency with section
circ(cx,cy+30*scale,16*scale,ACC,1.5);circ(cx,cy-30*scale,30*scale,ACC,1.5)
center(cx-143,cy,cx+143,cy);center(cx,cy-135,cx,cy+135)
txt(1486,918,'TX D32 CA',10);line(1478,915,cx+24,cy+58,.6,DIM)
txt(1486,779,'RX D60 CA',10);line(1478,783,cx+42,cy-58,.6,DIM)
dim(cx,cy-43.5,cx,cy+43.5,'60 BASELINE',-160)
txt(1110,688,'8 x M5 RETAINER FASTENERS ON D146 PCD',10)
txt(1110,670,'Front/rear flange D160; housing OD140 / ID120.',10)
txt(1110,651,'CA = clear aperture. Window blanks/seat design TBD.',9,DIM)
panel(52,276,600,338,'03  UNDERSIDE / VEHICLE MOUNT DATUMS')
rect(132,370,400,150,lw=1.2);center(110,445,553,445)
for xx in [194.5,469.5]:
 rect(xx-18,349,36,192)
 for yy in [388.75,501.25]:circ(xx,yy,5.3);center(xx-12,yy,xx+12,yy);center(xx,yy-12,xx,yy+12)
dim(132,520,532,520,'320',43);dim(194.5,349,469.5,349,'220',-29);dim(469.5,388.75,469.5,501.25,'90',91)
lines(72,301,['4 x D8.5 THRU / 220 x 90 RECTANGULAR PATTERN','Clamp-on saddle rails; no holes through pressure tube.'],10,16)
panel(670,276,962,338,'04  ASSEMBLY SCHEDULE / CONCEPT MATERIAL SELECTION')
rows=[('01','1','Pressure tube + end flanges','Titanium Grade 5 / isolation at dissimilar metals'),('02','1','Transmit pressure window','Sapphire / D32 clear / thickness TBD by analysis'),('03','1','Receive pressure window','Sapphire / D60 clear / thickness TBD by analysis'),('04','1','Pulsed source + scan head','532 nm source / 1-axis galvo / monitor photodiode'),('05','1','Receiver + timing chain','Lens / filter / silicon APD / TIA / ADC / FPGA'),('06','1','Power + compute assembly','18-30 VDC / isolated converter / Ethernet'),('07','1','Rear wet-mate interface','12-contact concept / vendor and rating TBD'),('08','2','Mount saddles + seal sets','Titanium saddles / elastomer compound TBD')]
table(686,568,930,['ITEM','QTY','DESCRIPTION','MATERIAL / REMARK'],rows,[.065,.055,.30,.58],27)
lines(52,250,['GENERAL NOTES  1. Depth target 300 m; geometry is not a pressure rating.  2. Window retention, seal glands, bolt preload and collapse margin require analysis.',
'3. Two radial body seals at each removable cap; inter-seal leak detection provision.  4. Dry nitrogen fill and humidity sensor proposed.',
'5. Deburr wetted edges; optical face protection required. Finish, tolerances, fastener torque and seal specifications remain unreleased.',
'6. Datum concept: A = front optical plane; B = housing axis; C = saddle clocking plane. Mounting dimensions are nominal interface targets.'],10,22)
c.showPage()
# SHEET 2
base(2,'OPTICAL, ELECTRICAL & TIMING ARCHITECTURE','Functional schematic / power domains / logical connector allocation / scan geometry')
panel(52,615,1580,455,'01  SIGNAL PATH / BLOCK SCHEMATIC - NOT A COMPONENT-LEVEL CIRCUIT')
def block(x,y,w,h,title,ss=[]):
 rect(x,y,w,h,DIM,fill=BG);txt(x+12,y+h-24,title,12,INK,'Courier-Bold');lines(x+12,y+h-44,ss,10,16)
block(85,894,185,94,'LASER DRIVER',['Trigger / current monitor','Emission inhibit input'])
block(322,894,175,94,'PULSED SOURCE',['532 nm / 2 ns target','5 uJ / 20 kHz target'])
block(554,894,190,94,'TX OPTICS',['Collimator / galvo','Beam monitor pickoff'])
block(803,894,153,94,'TX WINDOW',['Flat sapphire','Refraction model'])
block(1028,894,205,94,'WATER / TARGET',['Outgoing pulse / scatter','Return from surface'])
for a,b in [(270,322),(497,554),(744,803),(956,1028)]:arrow(a,941,b,941)
block(1292,894,299,94,'SYSTEM INTERLOCK',['J1 enable AND software arm','Leak / overtemp -> emission OFF'])
block(1028,697,205,107,'RX WINDOW + LENS',['D60 clear aperture','Wide field receiver','Overlap at R >= 1 m TBD'])
block(803,697,153,107,'FILTER + APD',['532 nm / 1 nm','Gated bias','TIA / limiter'])
block(554,697,190,107,'DIGITIZER',['2 GS/s target','Waveform extraction','Return quality flags'])
block(322,697,175,107,'FPGA TIMING',['Trigger timestamp','Galvo angle latch','Range estimator'])
block(85,697,185,107,'CPU / ETHERNET',['Calibrated point cloud','Health / diagnostics','IEEE 1588 target'])
arrow(1130,894,1130,804)
for a,b in [(1028,956),(803,744),(554,497),(322,270)]:arrow(a,751,b,751)
line(410,894,410,845,.8,ACC);line(410,845,410,804,.8,ACC);txt(424,840,'START / TX MONITOR',10,ACC)
line(647,894,647,845,.8,DIM);line(647,845,485,845,.8,DIM);txt(659,847,'ENCODER',9,DIM)
block(1292,697,299,107,'HEALTH + POWER SUPERVISION',['Water temp / case temp / humidity','Leak sensor / input V / laser current','Hardware inhibit independent of CPU'])
lines(84,650,['ACCENT ARROWS: optical / sampled signal flow.  All modules inside dry pressure boundary except water path.',
'Beam monitor measures emission timing; per-pulse reference corrects driver delay. Receive gate suppresses early backscatter.'],10,17)
panel(52,277,620,321,'02  POWER & LOGICAL J1 ALLOCATION')
lines(70,550,['J1 18-30 VDC -> surge/reverse protection -> EMI filter',
'-> isolated DC/DC -> laser rail / analog rail / digital rail',
'Chassis bond separate from isolated signal return.'],10,18)
table(70,486,584,['CONTACTS','FUNCTION','IMPLEMENTATION NOTE'],[
('1 / 2','VIN+ / VIN-','24 V nominal; 60 W peak budget'),('3 / 4','ETH TX+ / TX-','100BASE-TX differential pair'),('5 / 6','ETH RX+ / RX-','100BASE-TX differential pair'),('7 / 8','PPS+ / PPS-','Isolated differential timing input'),('9 / 10','ENABLE+ / ENABLE-','Isolated laser permit input'),('11 / 12','SERVICE+ / SERVICE-','Isolated RS-485 / maintenance')],[.18,.34,.48],26)
txt(70,295,'Logical assignment only; connector pin geometry/rating not selected.',9,DIM)
panel(690,277,942,321,'03  REFRACTED SCAN / BISTATIC RANGE MODEL')
# geometry occupies left half
line(905,328,905,530,2,ACC);line(917,328,917,530,1,ACC)
txt(732,531,'DRY OPTICS',10,DIM);txt(935,531,'WATER',10,DIM)
for dy in [-80,0,80]:
 line(752,427,905,427+dy,.8,INK);line(917,427+dy,1113,427+dy+dy*.72,.8,ACC)
center(741,427,1124,427);txt(942,453,'+/-15 deg',10);txt(935,437,'external',9,DIM)
txt(730,351,'~20.3 deg internal ray angle',9);txt(730,334,'Parallel faces: sin(a_air) = n_phase sin(a_water)',8.5)
lines(1160,545,['FOV target: 30 deg in water','Flat port / 1-axis fan scan','RX full FOV target >= 40 deg','Vehicle motion supplies axis 2','',
'Optical path L = c0 * dt / n_group','L = |P - TX| + |P - RX|','Solve on calibrated TX ray.','R ~ L/2 only in far field.','',
'n_phase for refraction;','n_group for flight time.'],10,18)
lines(52,246,['TIMING BUDGET  20 kHz pulse rate -> 50 us pulse interval.  1,000 angular samples/line -> 20 lines/s before turnaround and rejected returns.',
'2 GS/s sampling -> 0.5 ns intervals -> ~56 mm monostatic range spacing at assumed n_group = 1.34; interpolation is required for a 20 mm precision target.',
'Flat-port and 60 mm bistatic baseline calibration are mandatory. Range gate 1-15 m corresponds to ~8.9-134 ns monostatic-equivalent delay.',
'LASER CONTROL  Classification and accessible-emission assessment pending. Hardware permit, watchdog and fail-off driver are required design provisions.'],10,23)
c.showPage()
# SHEET 3
base(3,'SENSOR DATA & VERIFICATION BASIS','Separate data sheet / assumed design targets / derived quantities / validation plan')
panel(52,525,790,545,'01  SENSOR SPECIFICATION / ALL VALUES ARE CONCEPT TARGETS')
rows=[('Principle','Pulsed direct time of flight; bistatic receiver'),('Wavelength / pulse width','532 nm / 2 ns nominal'),('Pulse energy / rate','5 uJ / 20 kHz nominal'),('Optical average power','0.10 W, derived before optical losses'),('Range objective','1-15 m in clear water; not demonstrated'),('Precision objective','<=20 mm, 1 sigma at 5 m under test conditions'),('Absolute accuracy','Unspecified until calibration and tank test'),('Scan field / angular step','30 deg in water / nominal 0.03 deg'),('Scan throughput','20,000 shots/s; <=20 lines/s at 1,000 shots/line'),('Receive aperture / FOV','D60 clear window / >=40 deg full optical FOV'),('Receiver / digitizer','Silicon APD + TIA / 2 GS/s target'),('Power / electrical','18-30 VDC; 35 W nominal / 60 W peak budget'),('Data / timing','100BASE-TX / PPS / PTP support target'),('Depth / temperature','300 m target / water 0 to +35 C target'),('Mechanical envelope','D160 max x 359 incl. connector; 320 body'),('Mass / buoyancy','TBD by CAD mass model; no claimed value'),('Output','XYZ, intensity, time, scan angle, quality flags')]
table(68,1018,758,['PARAMETER','TARGET / DESIGN ASSUMPTION'],rows,[.32,.68],26)
panel(860,525,772,545,'02  CALCULATIONS / NOT MEASURED SENSOR DATA')
lines(879,1018,['A  TIME OF FLIGHT / n_group = 1.34 assumed',
'   c0 = 299,792,458 m/s; v_group ~ 223.73 x 10^6 m/s',
'   At 5 m: dt ~ 44.70 ns (monostatic equivalent)',
'   20 mm range change -> ~179 ps timing change',
'',
'B  SAMPLING / SCAN GEOMETRY',
'   30 deg / 1,000 samples ~ 0.03 deg per shot',
'   At 5 m: angular pitch ~ 2.62 mm near boresight',
'   Swath at 5 m: 2R tan(15 deg) ~ 2.68 m',
'   Beam divergence target 2 mrad -> ~10 mm growth at 5 m',
'   Sample pitch does not equal spatial resolution.',
'',
'C  EXTERNAL PRESSURE / seawater density 1,025 kg/m^3',
'   p_gauge = rho*g*h ~ 3.02 MPa at 300 m (g=9.81)',
'   On D60 clear aperture: F ~ p*A = 8.53 kN',
'   Window seat load also depends on unsupported diameter.',
'   No collapse, fatigue, seal or window stress analysis done.',
'',
'D  ATTENUATION EXAMPLE / homogeneous water only',
'   Two-way transmission factor ~ exp(-2*c_att*R)',
'   At 10 m: c_att=0.10/m -> 0.135; 0.30/m -> 0.00248',
'   Excludes geometric loss, reflectance and receiver noise.',
'   No link-budget closure or range guarantee is implied.'],10.5,20)
panel(52,164,790,343,'03  OUTPUT RECORD / PROPOSED WIRE FORMAT')
table(68,454,758,['FIELD','TYPE / UNIT','MEANING'],[
('timestamp_ns','uint64 / ns','TAI epoch; validity flag required'),('xyz_sensor','3 x float32 / m','Right-handed sensor coordinate frame'),('range_tx','float32 / m','Distance along calibrated transmitted ray'),('intensity','uint16 / count','Uncalibrated amplitude; saturation flagged'),('angle / line_id','float32 rad / uint32','Water-side ray angle / line index'),('quality/status/pad','3 x uint16','Quality, health flags, reserved zero pad')],[.24,.25,.51],27)
lines(70,251,['Frame: +Z forward along optical axis; +X starboard; +Y down.',
'Packed point record: 40 bytes; 20k records/s -> 0.8 MB/s payload.',
'Add packet framing, sequence, CRC and calibration ID at transport layer.',
'No-return records carry validity flag; invalid coordinates use NaN.',
'Health stream: case/water temp, humidity, input V/I, interlock state.'],10,17)
panel(860,164,772,343,'04  ACCEPTANCE PLAN / UNRESOLVED ENGINEERING')
lines(879,454,['V1  OPTICS / Ray trace through sapphire and seawater; verify full',
'    scan clearance, APD etendue, FOV overlap and internal scatter.',
'V2  RANGE / Tank target at 1, 5, 10, 15 m; record reflectance,',
'    attenuation, ambient light, water T/S and n_group model.',
'    >=1,000 valid returns/position; report bias, sigma and dropout.',
'V3  PRESSURE / External-pressure FEA, windows, glands and preload;',
'    establish proof protocol and fatigue life before hydrotest.',
'V4  THERMAL / Test 35 W continuous and 60 W peak duty in still water;',
'    verify source drift, APD noise and maximum case temperature.',
'V5  INTEGRATION / Timestamp alignment, EMC, leakage, corrosion,',
'    connector service life and hardware fail-off fault injection.',
'V6  SAFETY / Determine laser class for every accessible condition;',
'    release interlock design only after documented assessment.'],10,20)
txt(52,136,'REFERENCE BASIS: [R1] Non-coaxial underwater lidar research (2023)   [R2] NIST speed of light. Targets above are original concept assumptions.',9,DIM)
c.linkURL('https://www.mdpi.com/2072-4292/15/14/3618',(52,130,800,148),relative=0)
c.linkURL('https://www.nist.gov/pml/special-publication-330/sp-330-section-2',(805,130,1600,148),relative=0)
# sources are hyperlinks; no vendor performance is claimed
c.showPage();c.save()
from pypdf import PdfReader, PdfWriter
writer=PdfWriter(); writer.add_page(PdfReader(O+'/NEREID-532_concept_blueprint.pdf').pages[2]); writer.write(O+'/NEREID-532_sensor_data.pdf')
print('Created',O+'/NEREID-532_concept_blueprint.pdf')
