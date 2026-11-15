#version 110
// SPDX-License-Identifier: GPL-2.0-or-later
#include "colormanagement.glsl"
uniform sampler2D sampler;
uniform vec2 uSize;
uniform vec2 uMotion;
uniform vec3 uColor;
uniform float uClock;
uniform float uStrength;
uniform float uOffset;
uniform float uBandHeight;
uniform float uRate;
uniform float uEcho;
varying vec2 texcoord0;

float noise(vec2 p) { return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453); }
vec3 straight(vec4 c) { return c.a > .0001 ? c.rgb/c.a : vec3(0.0); }
void main() {
    vec2 size = max(uSize,vec2(1.0));
    vec2 uv = vec2(texcoord0.x,1.0-texcoord0.y);
    vec2 px = uv*size;
    vec4 original = texture2D(sampler,texcoord0);
    float tick = floor(uClock*uRate);
    float band = floor(px.y/uBandHeight);
    float rnd = noise(vec2(band,tick));
    float broken = step(.56,rnd);
    float power = uStrength;
    float shift = (noise(vec2(band+19.0,tick))*2.0-1.0)*uOffset*power*broken;
    shift *= .75+.25*min(1.0,length(uMotion));
    vec2 displaced = clamp(texcoord0+vec2(shift/size.x,0.0),vec2(0.0),vec2(1.0));
    vec4 primary = texture2D(sampler,displaced);
    vec4 echo = texture2D(sampler,clamp(texcoord0-vec2((shift*.7+7.0*power)/size.x,0.0),vec2(0.0),vec2(1.0)));
    vec3 rgb = straight(primary);
    float ghost = length(straight(echo)-rgb)*uEcho*broken;
    // Two bright vertical scanning columns recall the existing close effect.
    float scanX = fract(uClock*.42);
    float dx = abs(uv.x-scanX);
    dx = min(dx,1.0-dx);
    float scan = exp(-pow(dx*size.x/15.0,2.0));
    float second = exp(-pow((uv.x-fract(scanX+.39))*size.x/7.0,2.0));
    float line = 1.0-smoothstep(.25,1.4,mod(px.y,uBandHeight));
    float chips = step(.76,fract(px.x/21.0+rnd*6.0))*line*broken;
    float perimeter = 1.0-smoothstep(1.0,4.0,min(min(px.x,size.x-px.x),min(px.y,size.y-px.y)));
    float light = power*(ghost*.65+line*broken*.24+chips*.25+
                        scan*(.35+.20*broken)+second*.25+perimeter*.2);
    rgb = clamp(rgb+uColor*light,0.0,1.0);
    // Preserve the source alpha, including antialiased rounded edges/shadows.
    gl_FragColor = vec4(rgb*original.a,original.a);
    gl_FragColor = sourceEncodingToNitsInDestinationColorspace(gl_FragColor);
    gl_FragColor = nitsToDestinationEncoding(gl_FragColor);
}
