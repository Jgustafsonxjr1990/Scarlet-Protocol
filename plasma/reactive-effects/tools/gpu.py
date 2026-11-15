"""Render the actual shipped GLSL in a headless OpenGL context for checks/previews."""
from pathlib import Path
import numpy as np
from PIL import Image
import moderngl

ROOT=Path(__file__).resolve().parents[1]
VERTEX='''#version 140
in vec2 in_position;
out vec2 texcoord0;
void main(){gl_Position=vec4(in_position,0.0,1.0);texcoord0=(in_position+1.0)*.5;}
'''

class Renderer:
    def __init__(self):
        self.ctx=moderngl.create_standalone_context(backend='egl',require=310)
        self.vertex=self.ctx.buffer(np.array([-1,-1,1,-1,-1,1,1,1],dtype='f4').tobytes())
        self.programs={}
        self.uniforms={}
        for kind,plugin in [('wake','kwin6_effect_scarlet_vector_wake'),('relay','kwin6_effect_scarlet_phase_relay')]:
            for legacy in [False,True]:
                path=ROOT/plugin/'contents/shaders'/(kind+('' if legacy else '_core')+'.frag')
                source=path.read_text().replace('#include "colormanagement.glsl"','vec4 sourceEncodingToNitsInDestinationColorspace(vec4 c){return c;}\nvec4 nitsToDestinationEncoding(vec4 c){return c;}')
                vertex=VERTEX if not legacy else VERTEX.replace('#version 140','#version 110').replace('in vec2 in_position;','attribute vec2 in_position;').replace('out vec2 texcoord0;','varying vec2 texcoord0;')
                program=self.ctx.program(vertex_shader=vertex,fragment_shader=source)
                if legacy:program.release();continue
                self.programs[kind]=program
                self.uniforms[kind]=set(program)
    def render(self,kind,image,progress,**parameters):
        program=self.programs[kind]
        defaults={'sampler':0,'modulation':(1.,1.,1.,1.),'uSize':tuple(map(float,image.size)),
                  'uColor':(1.,32/255,86/255),'uProgress':float(progress),'uStrength':.65}
        if kind=='wake':defaults.update(uMotion=(.7,.1),uOffset=24.,uBandHeight=14.,uRate=12.,uEcho=.65,uStrength=.85,uTime=1.)
        else:defaults.update(uCellSize=14.,uStrength=.85)
        defaults.update(parameters)
        for key,value in defaults.items():program[key].value=value
        pixels=np.asarray(image,dtype='f4')/255
        pixels[:,:,:3]*=pixels[:,:,3:4]
        texture=self.ctx.texture(image.size,4,np.flipud(pixels).copy().tobytes(),dtype='f4')
        texture.filter=(moderngl.LINEAR,moderngl.LINEAR);texture.repeat_x=False;texture.repeat_y=False;texture.use(0)
        target=self.ctx.simple_framebuffer(image.size,components=4,dtype='f4');target.use();target.clear(0,0,0,0)
        self.ctx.viewport=(0,0,*image.size)
        vao=self.ctx.simple_vertex_array(program,self.vertex,'in_position')
        vao.render(moderngl.TRIANGLE_STRIP)
        raw=np.frombuffer(target.read(components=4,dtype='f4'),dtype='f4').reshape(image.height,image.width,4)
        pixels=np.flipud(raw).copy()
        pixels[:,:,:3]=np.divide(pixels[:,:,:3],pixels[:,:,3:4],out=np.zeros_like(pixels[:,:,:3]),where=pixels[:,:,3:4]>.00001)
        result=Image.fromarray(np.uint8(np.round(np.clip(pixels,0,1)*255)),'RGBA')
        vao.release();target.release();texture.release()
        return result

def check():
    renderer=Renderer()
    array=np.zeros((160,240,4),dtype=np.uint8)
    array[:,:,:3]=[36,40,49];array[:,:,3]=255
    # Partly transparent edge verifies premultiplied alpha handling.
    array[:4,:,:]=[6,8,10,64]
    image=Image.fromarray(array,'RGBA')
    original=np.asarray(image).astype('i2')
    for kind in ['wake','relay']:
        result=np.asarray(renderer.render(kind,image,1.)).astype('i2')
        assert np.max(np.abs(result-original))<=1,(kind,'identity endpoint mismatch')
    patterned=array.copy()
    patterned[8:,::16,:3]=[220,200,190]
    sample=Image.fromarray(patterned,'RGBA')
    for kind in ['wake','relay']:
        for progress in [.1,.35,.6,.9]:
            result=np.asarray(renderer.render(kind,sample,progress))
            assert np.array_equal(result[:,:,3],patterned[:,:,3]),(kind,'opacity changed')
        result=np.asarray(renderer.render(kind,sample,.35))
        changed=np.any(np.abs(result[:,:,:3].astype('i2')-patterned[:,:,:3].astype('i2'))>8,axis=2)
        assert changed.mean()>.12,(kind,'effect too subtle',changed.mean())
    start=np.asarray(renderer.render('relay',sample,0.)).astype('i2')
    assert np.max(np.abs(start-patterned.astype('i2')))<=1
    print('PASS: four GLSL variants compile/link; opacity preserved throughout both effects; native images restored at completion; focus starts opaque; visible pixel changes exceed 12% of the test texture')

if __name__=='__main__':check()
