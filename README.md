![Darkroom with no lettering: one stereoscope near and large with its paired card seated, a light table glowing with aligned pairs, a ruler at rest, squared sleeves, further stereoscopes in diminishing scale, and pinned flight strips climbing the wall](intro-banner.png)

# codeintel-Fuzz-Test-Generator

Specimen label treatment: the title is set in Be Vietnam Pro on a lab white plate ruled as a specimen label, with the single stereoscope drawn once as a header plate beneath the banner, and the remaining headings stay typographic, as specimen labels in Cabin.

![One stereoscope in profile on a plain ground line: hood in lab white, reagent violet shadow under the holder, copper stand and card clips, slate base, and the name hand lettered on a specimen label tag](logo.png)

![The cartography darkroom at work: a light table at the centre bearing aligned paired aerial photographs, stereoscopes along the bench, sleeves squared at the edge, a ruler across one pair, pinned flight strips on the far wall, one warm lamp in the sorter corner, and the title once on the light table fascia](banner.png)

![Darkroom in three depths: a paired photograph slides a little into alignment on the light table, a stereoscope tips a little toward true and rests, and the light table glow breathes faintly at its edge, while the pinned flight strips stay still](scene.svg)


Generates basic fuzz tests based on code structure and function signatures, focusing on boundary conditions and common error patterns. - Focused on Tools for static code analysis, vulnerability scanning, and code quality assurance

The target module is read and parsed from its syntax tree only. It is never imported or executed, so its top level code does not run during generation. A run exits 1 when the target cannot be read or parsed, and exits 1 when a readable module defines no functions of its own. A failed run writes no output file.

> **Specimen label, on the printout.** A generated file reports its failures only in its printout: the generated tests catch their own exceptions and merely print them, so the exit code of a generated file stays at nought even when a case has failed.


![Major separator: a microscope focus wheel pattern, copper on slate](sep-heavy.svg)

## Install
`git clone https://github.com/ShadowStrikeHQ/codeintel-fuzz-test-generator`

> **Specimen label, flagged in place.** The install line above reads git clone https://github.com/ShadowStrikeHQ/codeintel-fuzz-test-generator, naming ShadowStrikeHQ in place of ShadowGuard-AI. It is preserved exactly as printed and flagged here, never silently fixed.


![Minor separator: a microscope focus wheel pattern, copper on slate](sep-light.svg)

## Usage
`./codeintel-fuzz-test-generator [params]`


![Major separator: a microscope focus wheel pattern, copper on slate](sep-heavy.svg)

## Parameters
- `-h`: Show help message and exit
- `--num_tests`: Number of fuzz tests to generate per function. Defaults to 10.
- `--string_length`: Length of random strings used in fuzzing. Defaults to 10.
- `--int_min`: Minimum integer value for fuzzing. Defaults to -100.
- `--int_max`: Maximum integer value for fuzzing. Defaults to 100.
- `--output_file`: Optional file to save the generated tests to. If not provided, tests will be printed to stdout.


![Minor separator: a microscope focus wheel pattern, copper on slate](sep-light.svg)

## License
Copyright (c) ShadowStrikeHQ

> **Specimen label, flagged in place.** The closing line above reads Copyright (c) ShadowStrikeHQ, while the repository LICENSE file carries the MIT License. Both stand as printed; neither is forced to agree with the other.
