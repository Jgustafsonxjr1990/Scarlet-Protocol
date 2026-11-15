#version 110
// SPDX-License-Identifier: GPL-2.0-or-later
#include "colormanagement.glsl"
uniform sampler2D sampler;
uniform vec2 uSize;
uniform vec3 uColor;
uniform float uProgress;
uniform float uStrength;
uniform float uOffset;
uniform float uBandHeight;
uniform float uScanWidth;
varying vec2 texcoord0;

float noise(vec2 p) { return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453); }
vec3 straight(vec4 c) { return c.a > .0001 ? c.rgb/c.a : vec3(0.0); }
void main() {
    vec2 size = max(uSize,vec2(1.0));
    vec2 uv = vec2(texcoord0.x,1.0-texcoord0.y);
    vec2 px = uv*size;
    vec4 original = texture2D(sampler,texcoord0);
    float p = clamp(uProgress,0.0,1.0);
    // Identity at both endpoints. A handoff never closes/hides either window.
    float envelope = 4.0*p*(1.0-p)*uStrength;
    float front = mix(-.12,1.12,p);
    float band = floor(px.y/uBandHeight);
    float tick = floor(p*11.0);
    float rnd = noise(vec2(band,tick));
    float broken = step(.5,rnd);
    float distancePx = abs(uv.x-front)*size.x;
    float scan = exp(-pow(distancePx/uScanWidth,2.0));
    float echoScan = exp(-pow((uv.x-(front-.17))*size.x/(uScanWidth*.48),2.0));
    float shift = (rnd*2.0-1.0)*uOffset*broken*envelope*max(scan,echoScan);
    vec4 primary = texture2D(sampler,clamp(texcoord0+vec2(shift/size.x,0.0),vec2(0.0),vec2(1.0)));
    vec4 echo = texture2D(sampler,clamp(texcoord0-vec2((shift+5.0*envelope*scan)/size.x,0.0),vec2(0.0),vec2(1.0)));
    vec3 rgb = straight(primary);
    float ghost = length(straight(echo)-rgb);
    float edge = min(min(px.x,size.x-px.x),min(px.y,size.y-px.y));
    float halo = exp(-max(edge,0.0)/15.0);
    float line = 1.0-smoothstep(.2,1.2,mod(px.y,uBandHeight));
    float energy = envelope*(scan*(.72+broken*.25)+echoScan*.45+
                             line*broken*.18+halo*.26+ghost*.5);
    rgb = clamp(rgb+uColor*energy,0.0,1.0);
    gl_FragColor = vec4(rgb*original.a,original.a);
    gl_FragColor = sourceEncodingToNitsInDestinationColorspace(gl_FragColor);
    gl_FragColor = nitsToDestinationEncoding(gl_FragColor);
}
