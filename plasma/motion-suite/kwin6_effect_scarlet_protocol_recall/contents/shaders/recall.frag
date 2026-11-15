// SPDX-License-Identifier: MIT
#ifdef GL_ES
precision mediump float;
#endif

uniform sampler2D sampler;
uniform int textureWidth;
uniform int textureHeight;
uniform float uProgress;
varying vec2 texcoord0;

void main() {
    vec2 uv = vec2(texcoord0.x, 1.0 - texcoord0.y);
    vec2 size = vec2(float(textureWidth), float(textureHeight));
    vec4 source = texture2D(sampler, texcoord0);
    float t = clamp(uProgress, 0.0, 1.0);
    float phase = t * t * (3.0 - 2.0 * t);

    float along = uv.x + 0.34 * (1.0 - uv.y);
    float front = mix(-0.12, 1.48, phase);
    float slash = exp(-pow((along - front) / 0.047, 2.0));
    float wake = step(along, front) * exp(-max(front - along, 0.0) / 0.16);
    float edgePx = min(min(uv.x, 1.0 - uv.x) * size.x,
                       min(uv.y, 1.0 - uv.y) * size.y);
    float line = 1.0 - smoothstep(1.0, 4.0, edgePx);
    float halo = exp(-max(edgePx, 0.0) / 15.0);
    float pulse = 4.0 * t * (1.0 - t);
    float energy = 0.84 * slash + 0.20 * wake +
                   pulse * (0.45 * line + 0.20 * halo);

    vec3 straight = source.a > 0.0 ? source.rgb / source.a : vec3(0.0);
    vec3 scarlet = vec3(1.0, 0.0, 0.32); // #FF0051
    straight = clamp(straight + scarlet * energy, 0.0, 1.0);
    float fade = 1.0 - smoothstep(0.74, 1.0, t);
    float alpha = source.a * fade;
    gl_FragColor = vec4(straight * alpha, alpha);
}
