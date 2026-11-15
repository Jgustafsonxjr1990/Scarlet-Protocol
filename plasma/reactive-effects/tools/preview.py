"""GPU preview using the actual shipped shaders and sample window textures."""
from pathlib import Path
import math
import tempfile
import subprocess
from PIL import Image,ImageDraw,ImageFont
from gpu import Renderer,ROOT

def main():
    renderer=Renderer()
    source=ROOT/'tools/fixtures'
    wall=Image.open(source/'wallpaper.jpg').convert('RGBA')
    files=Image.open(source/'files.png').convert('RGBA')
    terminal=Image.open(source/'terminal.png').convert('RGBA')
    fonts='/usr/share/fonts/truetype/dejavu/'
    title=ImageFont.truetype(fonts+'DejaVuSans.ttf',26)
    body=ImageFont.truetype(fonts+'DejaVuSans.ttf',14)
    def base(name,description):
        image=wall.copy();draw=ImageDraw.Draw(image)
        draw.rounded_rectangle((32,20,1248,111),radius=18,fill='#111119',outline='#6c2943')
        draw.text((52,34),'SCARLET PROTOCOL / '+name,font=title,fill='#ffc8db')
        draw.text((53,76),description,font=body,fill='#bd899e')
        draw.text((44,760),'GPU SHADER PREVIEW  /  SAMPLE WINDOW CONTENT  /  LIVE KWIN PLAYBACK NOT RECORDED',font=body,fill='#b87993')
        return image
    with tempfile.TemporaryDirectory(prefix='scarlet-reactive-preview-') as directory:
        directory=Path(directory);frame=0
        previous=(340.,180.)
        motion=(0.,0.)
        # Window movement followed by the release/settle phase.
        for i in range(108):
            t=i/24
            if i<80:
                phase=i/79*2*math.pi
                pos=(340+260*math.sin(phase),205+65*math.sin(phase*2))
                dx=(pos[0]-previous[0])*16/(1000/24)/18
                dy=(pos[1]-previous[1])*16/(1000/24)/18
                motion=(.55*motion[0]+.45*dx,.55*motion[1]+.45*dy)
                previous=pos;progress=0.
            else:
                pos=previous;progress=min(1.,(i-80)/7)
            moving=renderer.render('wake',files,progress,uMotion=tuple(max(-1,min(1,v)) for v in motion),uTime=t)
            image=base('VECTOR WAKE / GLITCH DRAG','Broken scan bands, displaced image strips and scarlet echoes while dragging.')
            image.alpha_composite(moving,tuple(round(v) for v in pos))
            if i==45:image.convert('RGB').save(ROOT.parent/'Scarlet-Protocol-Reactive-Preview.png')
            image.convert('RGB').save(directory/f'{frame:04d}.png');frame+=1
        # Previously frontmost window A reveals B only in their overlap.
        old=(450,295);target=(135,165)
        for i in range(96):
            progress=max(0.,min(1.,(i-18)/42))
            incoming=renderer.render('relay',files,progress)
            image=base('PHASE RELAY / PIXEL LOCK','The selected window is in front immediately, with an opaque scarlet pixel-scan transition.')
            if i<18:
                image.alpha_composite(files,target);image.alpha_composite(terminal,old)
            else:
                image.alpha_composite(terminal,old);image.alpha_composite(incoming,target)
            image.convert('RGB').save(directory/f'{frame:04d}.png');frame+=1
        output=ROOT.parent/'Scarlet-Protocol-Reactive-Effects-Preview.mp4'
        subprocess.run(['ffmpeg','-v','error','-y','-framerate','24','-i',str(directory/'%04d.png'),'-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(output)],check=True)
        print(output)

if __name__=='__main__':main()
