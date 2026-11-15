"""Etch the fixed dial face as vector artwork. The wallpaper positions the hands."""
from pathlib import Path
from math import sin,cos,radians
root=Path(__file__).resolve().parents[1]/'wallpaper-plugins/org.scarletprotocol.orbit/contents/ui'
root.mkdir(parents=True,exist_ok=True)
parts=[]
def circle(r, color, width=1):
    parts.append(f'<circle cx="180" cy="180" r="{r}" fill="none" stroke="{color}" stroke-width="{width}"/>')
def radial(r,a):return 180+r*sin(radians(a)),180-r*cos(radians(a))
for r,c,w in [(174,'#6c253e',1),(170,'#2e1924',1),(151,'#743046',1),(133,'#481e30',1),(93,'#462030',1),(88,'#251a23',2),(53,'#341f29',1)]:circle(r,c,w)
for k in range(120):
    major=k%10==0;minute=k%2==0
    x,y=radial(147 if major else 156 if minute else 159,k*3); xx,yy=radial(166 if major else 163,k*3)
    parts.append(f'<path d="M{x:.2f} {y:.2f}L{xx:.2f} {yy:.2f}" stroke="{("#ed7694" if major else "#84354e" if minute else "#482335")}" stroke-width="{(2 if major else 1)}"/>')
for h in range(1,13):
    x,y=radial(118,h*30)
    parts.append(f'<text x="{x:.1f}" y="{y+4:.1f}" text-anchor="middle" font-family="monospace" font-size="10" fill="#b38090">{h:02}</text>')
(root/'face.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="360" height="360" viewBox="0 0 360 360">'+''.join(parts)+'</svg>')

# Raster fallback keeps the face available on Qt installations without the SVG image plugin.
import subprocess
subprocess.run(['inkscape', str(root/'face.svg'), '--export-width=1440', '--export-filename='+str(root/'face.png')], check=True)
