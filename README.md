# napari-bioformats

[![License](https://img.shields.io/pypi/l/napari-bioformats.svg?color=green)](https://github.com/napari/napari-bioformats/raw/master/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/napari-bioformats.svg?color=green)](https://pypi.org/project/napari-bioformats)
[![Conda](https://img.shields.io/conda/v/conda-forge/napari-bioformats)](https://anaconda.org/conda-forge/napari-bioformats)
[![Python Version](https://img.shields.io/pypi/pyversions/napari-bioformats.svg?color=green)](https://python.org)
[![tests](https://github.com/tlambert03/napari-bioformats/workflows/tests/badge.svg)](https://github.com/tlambert03/napari-bioformats/actions)
[![codecov](https://codecov.io/gh/tlambert03/napari-bioformats/branch/master/graph/badge.svg)](https://codecov.io/gh/tlambert03/napari-bioformats)

Bioformats plugin for napari using
[pims-bioformats](http://soft-matter.github.io/pims/v0.5/bioformats.html)

----------------------------------

## Use this plugin as a fallback!

Anyone coming to napari from the Fiji/ImageJ world will likely be aware of the
_incredible_ [Bio-Formats](https://docs.openmicroscopy.org/bio-formats/6.6.1/index.html)
library.  A heroic effort, built over years, to read
[more than a 100 file formats](https://docs.openmicroscopy.org/bio-formats/6.6.1/supported-formats.html).  Naturally, we want some of that goodness for `napari` ... hence this plugin.

**However:** it's important to note that this plugin _still_
requires having a java runtime engine installed.  This is easy enough to do
(the plugin will ask to install it for you if you're in a `conda` environment), but
it definitely makes for a more complicated environment setup, it's not very
"pythonic", and the performance will likely not feel as snappy as a native "pure"
python module.

So, before you reflexively install this plugin to fill that bio-formats
sized hole in your python heart, consider trying some of the other pure-python
plugins designed to read your format of interest:

- **Zeiss (.czi)**: [napari-aicsimageio](https://github.com/AllenCellModeling/napari-aicsimageio), [napari-czifile2](https://github.com/BodenmillerGroup/napari-czifile2)
- **Nikon (.nd2)**: [napari-nikon-nd2](https://github.com/cwood1967/napari-nikon-nd2), [nd2-dask](https://github.com/DragaDoncila/nd2-dask)
- **Leica (.lif)**: [napari-aicsimageio](https://github.com/AllenCellModeling/napari-aicsimageio)
- **Olympus (.oif)**: no plugin?  (but see [oiffile](https://pypi.org/project/oiffile/) )
- **DeltaVision (.dv, .mrc)**: [napari-dv](https://github.com/tlambert03/napari-dv)

> *if you have a pure-python reader for a bio-formats-supported file format that
you'd like to see added to this list, please open an issue*

## Installation

The easiest way to install `napari-bioformats` is via [conda], from the
[conda-forge] channel:

    conda install -c conda-forge napari-bioformats

It is also possible to install via [pip], but you will need to have a working
JVM installed, and may need to set the `JAVA_HOME` environment variable

    pip install napari-bioformats

### First Usage

The first time you attempt to open a file with napari-bioformats, you will
likely notice a long delay as pims downloads the `loci_tools.jar` (speed will
depend on your internet connection). Subsequent files should open more quickly.

## License

Distributed under the terms of the [BSD-3] license,
"napari-bioformats" is free and open source software

## Issues

If you encounter any problems, please [file an issue] along with a detailed description.

_This [napari] plugin was generated with [Cookiecutter] using with [@napari]'s [cookiecutter-napari-plugin] template._

[napari]: https://github.com/napari/napari
[Cookiecutter]: https://github.com/audreyr/cookiecutter
[@napari]: https://github.com/napari
[BSD-3]: http://opensource.org/licenses/BSD-3-Clause
[cookiecutter-napari-plugin]: https://github.com/napari/cookiecutter-napari-plugin
[file an issue]: https://github.com/tlambert03/napari-bioformats/issues
[napari]: https://github.com/napari/napari
[tox]: https://tox.readthedocs.io/en/latest/
[pip]: https://pypi.org/project/pip/
[conda]: https://docs.conda.io/en/latest/
[conda-forge]: https://conda-forge.org
[PyPI]: https://pypi.org/
