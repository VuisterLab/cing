#include "colors.inc"
#include "textures.inc"


// Persistence of Vision Ray Tracer Scene Description File
// File: ?.pov
// Vers: 3.5
// Desc: Basic TTF font Example
// Date: mm/dd/yy
// Auth: ?
//

#version 3.5;

global_settings {
  assumed_gamma 1.0
}

// ----------------------------------------

camera {
  location  <0.0, 2.0, -6.0>
  direction 1.5*z
  right     4/3*x
  look_at   <0.0, 0.0,  0.0>
}

sky_sphere {
  pigment {
    gradient y
    color_map {
      [0.0 color blue 0.6]
      [1.0 color rgb 1]
    }
  }
}

light_source {
  <0, 0, 0>            // light's position (translated below)
  color rgb <1, 1, 1>  // light's color
  translate <-30, 30, -30>
}



// ----------------------------------------

plane {               // checkered floor
  y, -1
  texture
  {
    pigment {
      checker
      color rgb 1
      color blue 1
      scale 0.5
    }
    finish{
      diffuse 0.8
      ambient 0.1
    }
  }
}

sphere {              // reflective sphere
  0.0, 1
  texture {
    pigment {
      color rgb <0.8,0.8,1.0>
    }
    finish{
      diffuse 0.3
      ambient 0.0
      specular 0.6
      reflection {
        0.8
        metallic
      }
      conserve_energy
    }
  }
}

// ----------------------------------------

#declare Text_Tex = texture {
    pigment {
      color rgb <0.8,0.8,0.8>
    }
  finish { specular 0.7 }
}


text {
  ttf "crystal.ttf", "Molmol failed",
  1, // depth
  0  // spacing
  scale <1, 2, 1> // stretch it taller
  texture { Text_Tex }
  rotate <0, -30, 0>
  translate <-3, 0, 3>
}
