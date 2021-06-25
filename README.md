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
