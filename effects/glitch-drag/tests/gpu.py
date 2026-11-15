"""Render shipped GLSL, checking opacity, sustained motion, and visible strength.
SDR preview stubs color conversion only; this is not a recording of live KWin.
"""
from pathlib import Path
import math,subprocess,tempfile
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import moderngl
ROOT=Path(__file__).resolve().parents[1]
PLUGIN=ROOT/'kwin6_effect_scarlet_vector_wake'
VERTEX='''#version 140
in vec2 position; out vec2 texcoord0;
void main(){gl_Position=vec4(position,0,1);texcoord0=(position+1.0)*.5;}
'''
class Renderer:
 def __init__(self):
  self.ctx=moderngl.create_standalone_context(backend='egl',require=310)
  self.vertex=self.ctx.buffer(np.array([-1,-1,1,-1,-1,1,1,1],dtype='f4').tobytes())
  for core in (False,True):
   source=(PLUGIN/'contents/shaders'/('wake_core.frag' if core else 'wake.frag')).read_text()
   source=source.replace('#include "colormanagement.glsl"','vec4 sourceEncodingToNitsInDestinationColorspace(vec4 c){return c;}\nvec4 nitsToDestinationEncoding(vec4 c){return c;}')
   vertex=VERTEX if core else VERTEX.replace('#version 140','#version 110').replace('in vec2 position; out vec2 texcoord0;','attribute vec2 position; varying vec2 texcoord0;')
   program=self.ctx.program(vertex_shader=vertex,fragment_shader=source)
   if core:self.program=program
   else:program.release()
 def render(self,image,time,strength=.85):
  p=self.program
  for key,value in dict(sampler=0,uSize=tuple(map(float,image.size)),uMotion=(.8,.2),uColor=(1.,32/255,86/255),uClock=float(time),uStrength=strength,uOffset=24.,uBandHeight=14.,uRate=12.,uEcho=.65).items():p[key].value=value
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
 for t in (0,.25,1,3,10,60,300):
  result=np.array(renderer.render(sample,t));assert np.array_equal(result[:,:,3],pixels[:,:,3]),'alpha changed'
  changed=(np.abs(result[:,:,:3].astype('i2')-pixels[:,:,:3]).max(axis=2)>8).mean();assert changed>.10,(t,changed)
  frames.append(result)
 assert not np.array_equal(frames[0],frames[1]),'clock must animate the image'
 zero=np.array(renderer.render(sample,1,strength=0)).astype('i2');assert np.max(np.abs(zero-pixels.astype('i2')))<=1,'zero strength must be identity'
 print('PASS GPU: both GLSL versions compile/link; continuously visible at 0–300 s; time changes image; alpha preserved; zero strength restores image. Release itself cancels shader in event tests.')

def preview(renderer,fixtures):
 wall=Image.open(fixtures/'wallpaper.jpg').convert('RGBA');files=Image.open(fixtures/'files.png').convert('RGBA')
 font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
 with tempfile.TemporaryDirectory() as temp:
  temp=Path(temp)
  for i in range(120):
   t=i/24;drag=i<96;pos=(round(320+190*math.sin(min(t,95/24)*1.3)),round(205+35*math.sin(min(t,95/24)*2)))
   image=wall.copy();image.alpha_composite(renderer.render(files,t) if drag else files,pos)
   d=ImageDraw.Draw(image);d.rounded_rectangle((28,20,1250,105),radius=16,fill='#101116',outline='#ff2056')
   d.text((48,35),'SCARLET PROTOCOL / GLITCH DRAG 3.0',font=font,fill='#ffc4d2')
   d.text((48,68),'DRAG: scarlet scans + torn echoes' if drag else 'RELEASE: original window restored',font=font,fill='#ff6689')
   d.text((32,760),'ACTUAL SHADER / SAMPLE CONTENT / GPU PREVIEW, NOT LIVE KWIN',font=font,fill='#eaa1b7')
   image.convert('RGB').save(temp/f'{i:04d}.png')
   if i==45:image.convert('RGB').save(ROOT/'Preview.png')
  subprocess.run(['ffmpeg','-v','error','-y','-framerate','24','-i',str(temp/'%04d.png'),'-c:v','libx264','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(ROOT/'Preview.mp4')],check=True)
if __name__=='__main__':
 import sys
 renderer=Renderer();checks(renderer)
 if len(sys.argv)>1:preview(renderer,Path(sys.argv[1]))
