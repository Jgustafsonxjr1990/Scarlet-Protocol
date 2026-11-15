"""Render shipped GLSL, checking opacity, sustained motion, and visible strength.
SDR preview stubs color conversion only; this is not a recording of live KWin.
"""
from pathlib import Path
import math,subprocess,tempfile
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import moderngl
ROOT=Path(__file__).resolve().parents[1]
PLUGIN=ROOT/'kwin6_effect_scarlet_phase_relay'
VERTEX='''#version 140
in vec2 position; out vec2 texcoord0;
void main(){gl_Position=vec4(position,0,1);texcoord0=(position+1.0)*.5;}
'''
class Renderer:
 def __init__(self):
  self.ctx=moderngl.create_standalone_context(backend='egl',require=310)
  self.vertex=self.ctx.buffer(np.array([-1,-1,1,-1,-1,1,1,1],dtype='f4').tobytes())
  for core in (False,True):
   source=(PLUGIN/'contents/shaders'/('relay_core.frag' if core else 'relay.frag')).read_text()
   source=source.replace('#include "colormanagement.glsl"','vec4 sourceEncodingToNitsInDestinationColorspace(vec4 c){return c;}\nvec4 nitsToDestinationEncoding(vec4 c){return c;}')
   vertex=VERTEX if core else VERTEX.replace('#version 140','#version 110').replace('in vec2 position; out vec2 texcoord0;','attribute vec2 position; varying vec2 texcoord0;')
   program=self.ctx.program(vertex_shader=vertex,fragment_shader=source)
   if core:self.program=program
   else:program.release()
 def render(self,image,time,strength=.85):
  p=self.program
  for key,value in dict(sampler=0,uSize=tuple(map(float,image.size)),uColor=(1.,32/255,86/255),uProgress=float(time),uStrength=strength,uOffset=14.,uBandHeight=14.,uScanWidth=32.).items():p[key].value=value
  pixels=np.array(image,dtype='f4')/255;pixels[:,:,:3]*=pixels[:,:,3:4]
  texture=self.ctx.texture(image.size,4,np.flipud(pixels).copy().tobytes(),dtype='f4');texture.filter=(moderngl.LINEAR,moderngl.LINEAR);texture.repeat_x=False;texture.repeat_y=False;texture.use(0)
  fbo=self.ctx.simple_framebuffer(image.size,components=4,dtype='f4');fbo.use();self.ctx.viewport=(0,0,*image.size);fbo.clear()
  vao=self.ctx.simple_vertex_array(p,self.vertex,'position');vao.render(moderngl.TRIANGLE_STRIP)
  pixels=np.flipud(np.frombuffer(fbo.read(components=4,dtype='f4'),dtype='f4').reshape(image.height,image.width,4)).copy()
  pixels[:,:,:3]=np.divide(pixels[:,:,:3],pixels[:,:,3:4],out=np.zeros_like(pixels[:,:,:3]),where=pixels[:,:,3:4]>.00001)
  result=Image.fromarray(np.uint8(np.round(np.clip(pixels,0,1)*255)),'RGBA')
  vao.release();fbo.release();texture.release();return result

def checks(renderer):
 pixels=np.zeros((240,420,4),dtype='uint8');pixels[:]=[30,33,40,255];pixels[:,::15,:3]=[210,170,180];pixels[:4,:,:]=[10,12,14,64]
 sample=Image.fromarray(pixels,'RGBA');frames=[]
 for t in (0,.1,.25,.5,.75,.9,1):
  result=np.array(renderer.render(sample,t));assert np.array_equal(result[:,:,3],pixels[:,:,3]),'alpha changed'
  if t in (0,1):assert np.max(np.abs(result.astype('i2')-pixels.astype('i2')))<=1,'identity endpoint'
  frames.append(result)
 assert not np.array_equal(frames[2],frames[3]),'scan must animate'
 changed=(np.abs(frames[3][:,:,:3].astype('i2')-pixels[:,:,:3]).max(axis=2)>8).mean();assert changed>.10,changed
 zero=np.array(renderer.render(sample,.5,strength=0)).astype('i2');assert np.max(np.abs(zero-pixels.astype('i2')))<=1
 print('PASS GPU: both GLSL variants compile/link; unchanged alpha throughout; native image at both endpoints; time-varying scarlet scan; >10% image change midpulse; zero-strength identity.')

def preview(renderer,fixtures):
 wall=Image.open(fixtures/'wallpaper.jpg').convert('RGBA');files=Image.open(fixtures/'files.png').convert('RGBA');terminal=Image.open(fixtures/'terminal.png').convert('RGBA')
 font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
 positions=((155,190),(440,295));sources=(files,terminal)
 with tempfile.TemporaryDirectory() as temp:
  temp=Path(temp)
  for i in range(144):
   # Three native-speed 380ms handoffs. Neither window moves or disappears.
   segment=i//48;local=i%48;selected=1-segment%2;previous=1-selected
   progress=max(0.,min(1.,(local-12)/(24*.380)))
   switching=12<=local<22
   image=wall.copy()
   if local<12:
    image.alpha_composite(sources[selected],positions[selected]);image.alpha_composite(sources[previous],positions[previous])
   else:
    image.alpha_composite(sources[previous],positions[previous]);image.alpha_composite(renderer.render(sources[selected],progress) if switching else sources[selected],positions[selected])
   d=ImageDraw.Draw(image);d.rounded_rectangle((28,20,1250,105),radius=16,fill='#101116',outline='#ff2056')
   d.text((48,35),'SCARLET PROTOCOL / PHASE RELAY 3.0',font=font,fill='#ffc4d2')
   d.text((48,68),'SELECT WINDOW: scarlet scan + glitch handoff / no sliding',font=font,fill='#ff6689')
   d.text((32,760),'ACTUAL SHADER / SAMPLE CONTENT / GPU PREVIEW, NOT LIVE KWIN',font=font,fill='#eaa1b7')
   image.convert('RGB').save(temp/f'{i:04d}.png')
   if i==17:image.convert('RGB').save(ROOT/'Preview.png')
  subprocess.run(['ffmpeg','-v','error','-y','-framerate','24','-i',str(temp/'%04d.png'),'-c:v','libx264','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(ROOT/'Scarlet-Protocol-Phase-Relay-Preview.mp4')],check=True)
if __name__=='__main__':
 import sys
 renderer=Renderer();checks(renderer)
 if len(sys.argv)>1:preview(renderer,Path(sys.argv[1]))
