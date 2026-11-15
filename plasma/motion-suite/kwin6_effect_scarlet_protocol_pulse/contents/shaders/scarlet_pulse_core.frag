#version 140
// SPDX-License-Identifier: MIT
// KWin's MapTexture input is premultiplied alpha.
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

    // One shader works in both directions: 0 = hidden, 1 = fully visible.
    float t = clamp(uProgress, 0.0, 1.0);
    float phase = t * t * (3.0 - 2.0 * t);
    float front = mix(-0.08, 1.08, phase);
    float softness = clamp(12.0 / max(size.y, 1.0), 0.012, 0.10);
    float reveal = 1.0 - smoothstep(front - softness, front + softness, uv.y);

    // A short red perimeter pulse and a bright scan crossing the window.
    float distancePx = min(min(uv.x, 1.0 - uv.x) * size.x,
                           min(uv.y, 1.0 - uv.y) * size.y);
    float line = 1.0 - smoothstep(1.2, 4.2, distancePx);
    float halo = exp(-max(distancePx, 0.0) / 17.0);
    float pulse = 4.0 * t * (1.0 - t);
    float scan = exp(-pow((uv.y - front) * size.y / 14.0, 2.0));
    float intensity = pulse * (0.42 * line + 0.27 * halo) + 0.78 * scan;

    vec3 straight = source.a > 0.0 ? source.rgb / source.a : vec3(0.0);
    vec3 scarlet = vec3(1.0, 0.0, 0.32); // #FF0051
    straight = clamp(straight + scarlet * intensity, 0.0, 1.0);
    float alpha = source.a * reveal;
    fragColor = vec4(straight * alpha, alpha);
    fragColor = sourceEncodingToNitsInDestinationColorspace(fragColor);
    fragColor = nitsToDestinationEncoding(fragColor);
}
