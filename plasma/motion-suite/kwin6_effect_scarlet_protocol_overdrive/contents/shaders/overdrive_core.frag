#version 140
// SPDX-License-Identifier: MIT
#include "colormanagement.glsl"

uniform sampler2D sampler;
uniform int textureWidth;
uniform int textureHeight;
uniform float uProgress;
in vec2 texcoord0;
out vec4 fragColor;

void main() {
    vec2 uv = vec2(texcoord0.x, 1.0 - texcoord0.y);
    vec2 size = vec2(float(textureWidth), float(textureHeight));
    vec4 source = texture2D(sampler, texcoord0);
    float t = clamp(uProgress, 0.0, 1.0);
    float phase = t * t * (3.0 - 2.0 * t);

    // A horizontal override band passes across the stretching frame.
    float front = mix(-0.10, 1.10, phase);
    float beam = exp(-pow((uv.x - front) * size.x / 24.0, 2.0));
    float segment = 0.74 + 0.26 * pow(sin(uv.y * size.y * 0.095), 2.0);
    float wake = step(uv.x, front) *
                 exp(-max(front - uv.x, 0.0) * size.x / 58.0);
    float edgePx = min(min(uv.x, 1.0 - uv.x) * size.x,
                       min(uv.y, 1.0 - uv.y) * size.y);
    float line = 1.0 - smoothstep(1.0, 3.8, edgePx);
    float halo = exp(-max(edgePx, 0.0) / 18.0);
    float pulse = 4.0 * t * (1.0 - t);
    float energy = 0.88 * beam * segment + 0.20 * wake * pulse +
                   pulse * (0.50 * line + 0.22 * halo);

    vec3 straight = source.a > 0.0 ? source.rgb / source.a : vec3(0.0);
    vec3 scarlet = vec3(1.0, 0.0, 0.32); // #FF0051
    straight = clamp(straight + scarlet * energy, 0.0, 1.0);
    fragColor = vec4(straight * source.a, source.a);
    fragColor = sourceEncodingToNitsInDestinationColorspace(fragColor);
    fragColor = nitsToDestinationEncoding(fragColor);
}
