"""Draw the fourth edition's Aurorae and Plasma assets. Sizes are logical pixels."""
from pathlib import Path
import json
import shutil
import re

ROOT = Path(__file__).resolve().parents[1]
BASE = "ScarletProtocolGlobal"
NIGHT = "ScarletProtocolNight"
STYLE = "ScarletProtocolPlasma"
DIMSTYLE = "ScarletProtocolNightPlasma"
SCARLET, HOT, WHITE = "#e41951", "#ff0051", "#ffd4df"
INK = "#101116"
NINE = ("topleft","top","topright","left","center","right","bottomleft","bottom","bottomright")


def write_svg(path, width, height, body):
    path.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">{body}</svg>\n')


def stroke(d, color, weight, opacity=1):
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{weight}" stroke-opacity="{opacity}" stroke-linejoin="round" stroke-linecap="round"/>'


def tile_path(part, m, inset):
    # All tiles have the same bounds. Reflection keeps corner tangents identical.
    if part=="center":
        return f'M0 0h{m}v{m}H0Z'
    if part in ("left","right"):
        return f'M{inset} 0H{m}v{m}H{inset}Z'
    if part in ("top","bottom"):
        return f'M0 {inset}H{m}v{m-inset}H0Z'
    radius=m-inset
    return f'M{m} {inset}A{radius} {radius} 0 0 0 {inset} {m}H{m}Z'


def frame(prefix, y, m, bands, face, empty=False):
    out=[]
    for i, part in enumerate(NINE):
        x=(i%3)*m
        yy=y+(i//3)*m
        flipx = part.endswith("right")
        flipy = part.startswith("bottom")
        transform=f'translate({m if flipx else 0},{m if flipy else 0}) scale({-1 if flipx else 1},{-1 if flipy else 1})'
        layers=[]
        for n,(inset, color, opacity) in enumerate(bands):
            if part=="center":
                continue
            path=tile_path(part,m,inset)
            inner=bands[n+1][0] if n+1<len(bands) else inset+1
            if empty:
                path += " "+tile_path(part,m,inner)
            layers.append(f'<path d="{path}" fill="{color}" fill-opacity="{opacity}" fill-rule="evenodd"/>')
        if not empty:
            path=tile_path(part,m,bands[-1][0]+1)
            layers.append(f'<path d="{path}" fill="{face}"/>')
        if prefix == "decoration" and part in ("topleft", "topright"):
            # A short reflected highlight follows the top shoulder of the rim.
            highlight = "#f0a0b2" if len(bands) < 6 else "#ffc3d2"
            layers.append(stroke("M15.8 12.7 Q18.5 10.9 21.3 10.5", highlight, .8, .85))
        if prefix.startswith('decoration-maximized'):
            layers = [f'<rect width="{m}" height="{m}" fill="{face}"/>']
        name=f'{prefix}-{part}' if prefix else part
        out.append(f'<g id="{name}" transform="translate({x},{yy})"><rect width="{m}" height="{m}" fill="#000" fill-opacity="0"/><g transform="{transform}">{"".join(layers)}</g></g>')
    return ''.join(out)


def render_frames(path, entries, size):
    groups=[frame(prefix, n*(3*size+4), size, bands, face, outline) for n,(prefix,bands,face,outline) in enumerate(entries)]
    # Frame size and content padding are distinct for buttons/text inputs.
    if path.stem in ("button","lineedit"):
        for n,(prefix,*_) in enumerate(entries):
            for side in ("left","right","top","bottom"):
                width,height = (7,1) if side in ("left","right") else (1,4)
                groups.append(f'<rect id="{prefix}-hint-{side}-margin" x="{3*size+4}" y="{n*8}" width="{width}" height="{height}" opacity="0"/>')
    write_svg(path,3*size+16,len(entries)*(3*size+4),''.join(groups))


GLYPHS = {
    "close":"M11.9 9.9l6.2 6.2m0-6.2-6.2 6.2",
    "minimize":"M10.9 13.4h8.2",
    "maximize":"M11 15.9l7.5-7.1m-4 .1h4v4m-7.6.1v3.1h3.6",
    "restore":"M10.5 9l3.5 3.5m-3.1 0H14V9.4m5.5 7.6L16 13.5m3.1 0H16v3.1",
    "alldesktops":"M10 9h4v3h-4zM16 9h4v3h-4zM10 14h4v3h-4zM16 14h4v3h-4z",
    "keepabove":"M10.5 14.8l4.5-4 4.5 4M10.5 8.8h9",
    "keepbelow":"M10.5 11.2l4.5 4 4.5-4M10.5 17.2h9",
    "shade":"M10 10h10m-8.5 5.5 3.5-3 3.5 3",
    "help":"M12.2 10.8c0-3.5 6.5-3.5 6 0-.2 1.5-3.5 2-3.5 4m0 2v.4",
    "appmenu":"M10 9h10m-10 4h10m-10 4h7",
}
SEMANTIC={"close":"#FF315B","minimize":"#FFD43B","maximize":"#38EA77","restore":"#38EA77"}
STATES=("active","inactive","hover","hover-inactive","pressed","pressed-inactive","deactivated","deactivated-inactive")


def buttons(folder, night):
    for name,glyph in GLYPHS.items():
        body=[]
        for i,state in enumerate(STATES):
            lit=state.startswith(("hover","pressed"))
            idle=state=="active"
            color=SEMANTIC.get(name,"#FF4276") if lit else (SCARLET if idle and name=="close" else "#ae7588" if idle else "#876875")
            off=state.startswith("deactivated")
            pressed=state.startswith("pressed")
            parts=[]
            # Side contacts and a split annulus frame a recognizable center glyph.
            arcs="M6.3 10.8a9 9 0 0 1 14.9-4.4M23.7 15.2a9 9 0 0 1-14.9 4.4"
            hot=lit or (name=="close" and idle)
            if hot:
                for w,a in ((6.8,.07),(4.2,.12),(2.7,.16)):
                    parts.append(stroke(arcs,color,w,a*(.48 if night else 1)))
            parts.append('<circle cx="15" cy="13" r="8.4" fill="#20141c"/>' if hot else '<circle cx="15" cy="13" r="8.4" fill="#17161b"/>')
            parts.append(stroke(arcs,color,1.3,1 if hot else .40))
            parts.append(stroke("M4 13h1.6m18.8 0H26",color,1,.95 if lit else .5))
            if hot:
                parts.append(stroke(glyph,color,3.5,.28))
            parts.append(stroke(glyph, color, 1.85 if lit else 1.55))
            if lit:
                parts.append(stroke(glyph,"#fff2f5",.68,.95))
            inner=''.join(parts)
            if pressed:
                inner=f'<g transform="translate(1.5,1.3) scale(.90)">{inner}</g>'
            body.append(f'<g id="{state}-center" transform="translate({(i%4)*32},{(i//4)*28})"><rect width="30" height="26" fill="#000" fill-opacity="0"/><g opacity="{.40 if off else 1}">{inner}</g></g>')
        write_svg(folder/(name+".svg"),128,56,''.join(body))


def write_style(folder,night):
    def bands(rim,hot=False):
        return [(0,rim,.14 if hot else .10),(.8,rim,.42 if hot else .28),(1.8,rim,.95),(2.7,"#27151f",.86)]
    idle="#693047" if not night else "#482432"
    accent="#cf3b63" if night else HOT
    faces={"normal":("#1b171d",idle),"hover":("#341824",accent),"pressed":("#571830",SCARLET),"focus":("#27141e",accent)}
    def item(prefix,face,rim,hot=False,outline=False):
        return (prefix,bands(rim,hot),face,outline)
    w=folder/"widgets"
    render_frames(w/"button.svg",[item(state,*faces[state],state!="normal",state in ("focus","hover")) for state in faces]+[item("toolbutton-"+s,*faces[s],True,s=="focus") for s in ("hover","focus","pressed")],9)
    render_frames(w/"lineedit.svg",[item("base",INK,idle),item("hover",INK,SCARLET,True,True),item("focus",INK,accent,True,True)],8)
    tasks=[item("normal","#17161b",idle),item("hover","#341923",SCARLET,True),item("focus","#431725",accent,True),item("attention","#5c1a29","#ff6978",True),item("minimized","#131218","#4c3842")]
    render_frames(w/"tasks.svg",tasks,9)
    for file,face,rim in (("widgets/panel-background.svg",INK,idle),("dialogs/background.svg",INK,accent),("widgets/tooltip.svg","#1a151c",SCARLET),("widgets/background.svg","#17151c",idle)):
        render_frames(folder/file,[item("",face,rim,True)],14)
    render_frames(w/"viewitem.svg",[item("normal",INK,idle),item("hover","#301923",SCARLET),item("selected","#55182c",accent),item("selected+hover","#711b38",accent,True)],8)


def config(folder, oldid, newid, night):
    p=folder/f'{oldid}rc'
    s=p.read_text().replace('\nShadow=false','\nShadow=true').replace('UseTextShadow=true','UseTextShadow=false').replace('ActiveTextColor=228,25,81,255','ActiveTextColor=245,216,225,255')
    s=s.replace('ButtonWidth=34','ButtonWidth=33').replace('Animation=180','Animation=150')
    s = re.sub(r"^Padding(?:Left|Right|Top|Bottom)=.*\n?", "", s, flags=re.MULTILINE).rstrip()
    for edge in ("Left","Right","Top","Bottom"):
        s+=f'\nPadding{edge}=10'
    if oldid!=newid: p.unlink()
    (folder/f'{newid}rc').write_text(s+'\n')
    p=folder/'metadata.desktop'
    p.write_text(p.read_text().replace('2.0.0','4.0.0').replace(oldid,newid).replace('Blackout','Night Shift' if night else 'Blackout'))


def windows(folder,night):
    active=[(.2,"#c01747",.012),(2,"#c01747",.025),(4,"#ce164d",.045),(6,"#df1551",.080),(8,"#f91956",.18),(9.3,"#fa2660",.38),(10,"#ff3870",1),(11,"#772039",1),(12,"#261720",1)]
    if night:
        active=[(1,"#18101a",.05),(5,"#160b10",.10),(9,"#b2254e",.17),(10,"#a02b50",1),(11,"#381822",1)]
    inactive=[(2,"#100b0f",.05),(6,"#100b0f",.12),(9,"#482935",.28),(10,"#50313d",1),(11,"#241b21",1)]
    entries=[("decoration",active,INK,False),("decoration-inactive",inactive,"#151419",False)]
    entries.extend((name,[(0,"#181419",1)],face,False) for name,face in (("decoration-maximized",INK),("decoration-maximized-inactive","#151419")))
    render_frames(folder/"decoration.svg",entries,24)
    buttons(folder,night)


def update_meta(folder,plugin,name):
    path=folder/"metadata.json"
    meta=json.loads(path.read_text())
    meta["KPlugin"].update(Id=plugin,Name=name,Version="4.0.0")
    path.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n")


def editions():
    base_lnf=ROOT/"look-and-feel"/BASE
    base_style=ROOT/"plasma-style"/STYLE
    base_dec=ROOT/"aurorae"/BASE
    # Always clone edition inputs before edition-specific SVG and config edits.
    for group,src,dest in (("look-and-feel",base_lnf,NIGHT),("plasma-style",base_style,DIMSTYLE),("aurorae",base_dec,NIGHT)):
        target=ROOT/group/dest
        keep_previews = group == "look-and-feel" and (target / "contents/previews/preview.png").exists()
        ignore = shutil.ignore_patterns("preview.png", "fullscreenpreview.jpg") if keep_previews else None
        shutil.copytree(src, target, dirs_exist_ok=True, ignore=ignore)
    for night in (False,True):
        gid=NIGHT if night else BASE
        sid=DIMSTYLE if night else STYLE
        title="Scarlet Protocol — "+("Night Shift" if night else "Blackout")
        lnf=ROOT/"look-and-feel"/gid
        style=ROOT/"plasma-style"/sid
        dec=ROOT/"aurorae"/gid
        update_meta(lnf,gid,title)
        update_meta(style,sid,title)
        p=lnf/"contents/defaults"
        defaults=p.read_text().replace(BASE,gid).replace(STYLE,sid).split('\n[kcminputrc][Mouse]')[0]
        if night:
            defaults = defaults.replace("Image=ScarletProtocolWall", "Image=ScarletProtocolNoirWall")
        p.write_text(defaults.rstrip()+'\n\n[kcminputrc][Mouse]\ncursorTheme=ScarletProtocolCursors\n')
        config(dec,BASE,gid,night)
        windows(dec,night)
        write_style(style,night)
