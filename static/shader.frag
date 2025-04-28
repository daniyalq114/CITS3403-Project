// using low precision float
precision lowp float;
// u_resolution gets the resolution of the canvas
uniform vec2 u_resolution;
// the time since the website was reloaded
uniform float u_time;
// IF YOU'RE EDITING THIS AND IT BREAKS, CHECK THAT YOUR NUMBERS ARE FLOATS

// COLOUR SCHEMES
const vec3 top = vec3(0.741, 0.840, 1.0); 
const vec3 bottom = vec3(0.7, 0.482, 0.612); // was vec3(1, 0.482, 0.612)
// alt
// const vec3 top = vec3(0.8, 0.831, 1.0);
// const vec3 bottom = vec3(0.094, 0.141, 0.424);
// alt 2 - maybe a bit much
// const vec3 top = vec3(1, 0.482, 0.612); // was vec3(1, 0.482, 0.612)
// const vec3 bottom = vec3(0.094, 0.141, 0.424);

const float widthFactor = 0.5;
// Resonsible for drawing the sine curves 
vec3 calcSine(vec2 uv, float angular_freq, float velocity, float phase, float amp, 
              vec3 color, float width, float yshift) {
    // typical y(x,t) = sin(k * x - omega * t + phi), 
    float angle = angular_freq * ((uv.x/velocity) - u_time) + phase;

    // scaling the y values
    float y = sin(angle) * amp + yshift;

    // interpolates colour intensity using the width factor, and the distance of this point
    // from norm of the line being drawn 
    float scale = pow(smoothstep(width * widthFactor, 0.0, distance(y, uv.y)), 15.0);

    return color * scale;
}
void main() {
    // represent the coordinate system as {uv in R^2 | 0 <= uv_x, uv_y <= 1}
    vec2 uv = gl_FragCoord.xy /u_resolution.xy;
    
    // adjusts colour of the pixel according to its y position  
    vec3 color = vec3(mix(bottom, top, uv.y));

    // lines
    color += calcSine(uv, 0.4, 0.20, 0.2, .3, color, 0.5, 0.6);
    color += calcSine(uv, 0.4, 0.15, 0.0, 0.4, color, 0.3, 0.5);
    color += calcSine(uv, 0.3, 0.13, 0.2, 0.3, color, 0.225, 0.65);
    color += calcSine(uv, 0.3, 0.10, 0.60, 0.2, color, 0.35, 0.2);

    // colour of this pixel to be drawn to the canvas
    gl_FragColor = vec4(color,1.0);
}