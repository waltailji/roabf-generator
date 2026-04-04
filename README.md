# RAOBF Wheel SVG Generator

This project contains a Python script that generates a WWII-style RAOBF wheel as SVG artwork.

The generator creates three files:

- `raobf_base.svg`: fixed base disc
- `raobf_rotor.svg`: rotating overlay disc
- `raobf_composite.svg`: combined view of base and rotor

## Requirements

- Python 3

## Usage

Run the generator from the project directory:

```bash
python3 raobf_generator.py
```

This writes both optical-length calibrations into the same folder:

- `*_degrees.svg` for the degree-based optical scale
- `*_mrads.svg` for the milliradian optical scale
- `*_mrads_extended.svg` for the extended mrads base/composite variant

## Files

- `raobf_generator.py`: main generator script
- `.gitignore`: project ignore rules

## What The Script Controls

The script is organized around editable constants near the top of the file. These include:

- overall disc radii and scale radii
- numeric label radii and curved text radii
- font families and font sizes
- tick lengths and stroke widths
- curved section-label placement
- colored marker lines, arrows, and marker-label placement
- AOB crosshair and crosshair tick settings

## Current Features

- separate base and rotor SVG generation
- composite SVG generation
- curved section labels using SVG `textPath`
- configurable ship, distance, optical-length, and AOB scales
- mirrored tick/label placement where needed
- guide circles for selected scale bands
- colored blue, green, and red reference markers with arrowheads
- curved labels for marker annotations
- AOB inner-circle crosshairs with graduated tick marks

## Notes

- Generated SVG files are ignored by git via `.gitignore`.
- Font appearance depends on the fonts installed on the local system.
- If a newly installed font does not appear in Chrome immediately, fully quit and reopen Chrome and refresh the SVG.
