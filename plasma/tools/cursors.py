"""Create original multiresolution Xcursor files; no compiler is needed to install."""
from pathlib import Path
from math import sin,cos,radians
import struct
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
SIZES=(24,32,48,64)
SET={
    "default":("left_ptr arrow top_left_arrow",(3,2)),
    "pointer":("hand hand1 hand2 pointing_hand link",(12,3)),
    "text":("xterm ibeam",(16,16)),
    "crosshair":("tcross cross",(16,16)),
    "wait":("watch",(16,16)),
    "progress":("left_ptr_watch half-busy",(3,2)),
    "ew-resize":("col-resize w-resize e-resize sb_h_double_arrow size_hor size-hor h_double_arrow left_side right_side",(16,16)),
    "ns-resize":("row-resize n-resize s-resize sb_v_double_arrow size_ver size-ver v_double_arrow top_side bottom_side",(16,16)),
    "nwse-resize":("nw-resize se-resize size_fdiag size-fdiag top_left_corner bottom_right_corner",(16,16)),
    "nesw-resize":("ne-resize sw-resize size_bdiag size-bdiag top_right_corner bottom_left_corner",(16,16)),
    "move":("fleur all-scroll size_all",(16,16)),
    "not-allowed":("forbidden no-drop crossed_circle",(16,16)),
}
HOT="#ff315e"; SHELL="#16131c"; LIGHT="#ffe8ed"


def draw_frame(kind, phase, size):
    scale=8
    im=Image.new("RGBA",(32*scale,32*scale))
    d=ImageDraw.Draw(im)
    def points(ps):return [(round(x*scale),round(y*scale)) for x,y in ps]
    def line(ps,c,w):d.line(points(ps),fill=c,width=max(1,round(w*scale)),joint="curve")
    def circle(cx,cy,r,c):d.ellipse(points([(cx-r,cy-r),(cx+r,cy+r)]),fill=c)
    def glyph(ps):
        d.polygon(points(ps),fill=SHELL)
        line(ps+[ps[0]],LIGHT,1.35)
    if kind in ("default","progress"):
        glyph([(3,2),(3.8,23),(8.5,18.5),(13.2,27),(16,25.4),(11.7,17.2),(19.4,16.3)])
        line([(5,6),(6,18),(9,14.8),(14.5,15)],HOT,1.65)
    if kind in ("wait","progress"):
        cx,cy,r=(16,16,10) if kind=="wait" else (22.4,23.5,5.3)
        circle(cx,cy,r+1.5,SHELL); circle(cx,cy,r,LIGHT); circle(cx,cy,r-.9,SHELL)
        for i in range(12):
            a=radians(30*i-90); k=(phase-i)%12
            b=1-k/12
            c=(int(94+161*b),int(26+65*b),int(48+79*b),255)
            circle(cx+cos(a)*(r-2),cy+sin(a)*(r-2),max(.7,r*.125),c)
        circle(cx,cy,r*.23,HOT)
    elif kind=="pointer":
        glyph([(11,18),(10,5),(11.7,3),(13.5,4),(14,13),(15.5,11.8),(17.2,12.9),(19,12),(21,14),(22.5,13.6),(24.3,15.5),(24,23),(21,28),(13,28),(6.7,19),(6.7,16.8),(8.5,16.4)])
        line([(12,6),(12.7,16)],HOT,1.6);line([(14,24),(21.8,24)],HOT,1.6)
    elif kind=="text":
        for ps in [[(11,4),(16,6),(21,4)],[(16,6),(16,26)],[(11,28),(16,26),(21,28)]]:
            line(ps,SHELL,4);line(ps,LIGHT,1.7)
        line([(16,10),(16,23)],HOT,1.5)
    elif kind in ("crosshair","move") or kind.endswith("-resize"):
        angles={"ew-resize":[0,180],"ns-resize":[90,270],"nwse-resize":[45,225],"nesw-resize":[135,315],"move":[0,90,180,270],"crosshair":[0,90,180,270]}[kind]
        for deg in angles:
            a=radians(deg)
            def pt(x,y):return (16+x*cos(a)-y*sin(a),16+x*sin(a)+y*cos(a))
            ps=[pt(3,0),pt(13,0)]
            line(ps,SHELL,4.6);line(ps,LIGHT,2)
            if kind!="crosshair":
                ps=[pt(9,-3.8),pt(13,0),pt(9,3.8)]
                line(ps,SHELL,4);line(ps,HOT,1.8)
        circle(16,16,1.4,HOT)
    elif kind=="not-allowed":
        circle(16,16,11,SHELL);circle(16,16,9,LIGHT);circle(16,16,7.5,SHELL)
        line([(10,22),(22,10)],HOT,2.6)
    return im.resize((size,size),Image.Resampling.LANCZOS)


def packed(kind,hotspot):
    lines=[]
    kind_id=0xfffd0002
    for size in SIZES:
        count=12 if kind in ("wait","progress") else 1
        for i in range(count):
            image=draw_frame(kind,i,size).convert('RGBa')
            pixels=b''.join(struct.pack('<I',(a<<24)|(r<<16)|(g<<8)|b) for r,g,b,a in image.getdata())
            header=struct.pack('<9I',36,kind_id,size,1,size,size,*[round(v*size/32) for v in hotspot],75 if count>1 else 0)
            lines.append((size,header+pixels))
    offset=16+12*len(lines)
    toc=[]
    for size,chunk in lines:
        toc.append(struct.pack('<3I',kind_id,size,offset))
        offset+=len(chunk)
    return struct.pack('<4I',0x72756358,16,65536,len(lines))+b''.join(toc)+b''.join(chunk for _,chunk in lines)


def build():
    root=ROOT/'cursors/ScarletProtocolCursors'
    out=root/'cursors'; out.mkdir(parents=True,exist_ok=True)
    (root/'index.theme').write_text('[Icon Theme]\nName=Scarlet Protocol — Relay\nComment=Dark pointers with a pale rim and scarlet spine\nInherits=breeze_cursors\n')
    for name,(aliases,hotspot) in SET.items():
        data=packed(name,hotspot)
        for alias in [name]+aliases.split(): (out/alias).write_bytes(data)

if __name__=="__main__":build()
