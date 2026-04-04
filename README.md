# Enhanced RAOBF Wheel SVG Generator

This project include SVG templates and the Python script used to generate these SVG files, for building
a hand-held RAOBF (Range and Angle On Bow Finder) slide rule calculator to use with WWII submarine simulators such as Silent Hunter 3 and U-Boat.  It is enhanced from original RAOBF to include two scales for the optical angle:
degrees and milliradians.  This is because using a realistic periscope mod will have a vertical stadimeter in 
milliradians, and horizontal reticle in degrees; so being able to convert from both scales on the same wheel
becomes handy.

The wheel also includes reference markers for both normal periscope zoom levels (1.5x and 6x) and for the extended periscope zoom levels for the U-Boat game (1.5x, 3.8x, and 15x), to correctly position the optical length value.

There is also a speed calculator marker (in knots). To calculate speed, rotate the ship transit time (in seconds) on the hectometer distance scale to the ship length/meters on the outer scale, then read the optical degrees value indicated by the 'kts' marker line.

These scales are generated with the underlying logarithmic equations from the trigonometric formulas, and fixes a few inaccuracies in the original RAOBF dials, such as correct position of tick marks (the 80-degree tick mark between 70 and 90 degrees on the AOB scale, for instance) on a logarithmic scale.

The generator creates three files:

- `raobf_base.svg`: fixed base disc
- `raobf_rotor.svg`: rotating overlay disc (to print on transparent film)
- `raobf_composite.svg`: combined view of base and rotor (mainly for visual diagnostics of the script output)

## Requirements

If you want to modify the output of the SVG templates, the script will require:
- Python 3

## Usage

Run the generator from the project directory:

```bash
python3 raobf_generator.py
```

This writes the combined wheel artwork:

- `raobf_base.svg`
- `raobf_rotor.svg`
- `raobf_composite.svg`

## Files

- `raobf_generator.py`: main generator script
- `.gitignore`: project ignore rules

