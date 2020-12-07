# napari-pims-bioformats

[![License](https://img.shields.io/pypi/l/napari-pims-bioformats.svg?color=green)](https://github.com/napari/napari-pims-bioformats/raw/master/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/napari-pims-bioformats.svg?color=green)](https://pypi.org/project/napari-pims-bioformats)
[![Conda](https://img.shields.io/conda/v/conda-forge/napari-pims-bioformats)](https://anaconda.org/conda-forge/napari-pims-bioformats)
[![Python Version](https://img.shields.io/pypi/pyversions/napari-pims-bioformats.svg?color=green)](https://python.org)
[![tests](https://github.com/tlambert03/napari-pims-bioformats/workflows/tests/badge.svg)](https://github.com/tlambert03/napari-pims-bioformats/actions)
[![codecov](https://codecov.io/gh/tlambert03/napari-pims-bioformats/branch/master/graph/badge.svg)](https://codecov.io/gh/tlambert03/napari-pims-bioformats)

Bioformats plugin for napari using [pims-bioformats](http://soft-matter.github.io/pims/v0.5/bioformats.html)

----------------------------------

## Installation

The easiest way to install `napari-pims-bioformats` is via [conda], from the [conda-forge] channel:

    conda install -c conda-forge napari-pims-bioformats

It is also possible to install via [pip], but you will need to have a working JVM installed,
and may need to set the `JAVA_HOME` environment variable

    pip install napari-pims-bioformats

## First Usage:

The first time you attempt to open a file with pims-bioformats, you will likely notice a long
delay as pims downloads the `loci_tools.jar` (speed will depend on your internet connection).
Subsequent files should open a bit quicker.

## License

Distributed under the terms of the [BSD-3] license,
"napari-pims-bioformats" is free and open source software

## Issues

If you encounter any problems, please [file an issue] along with a detailed description.


_This [napari] plugin was generated with [Cookiecutter] using with [@napari]'s [cookiecutter-napari-plugin] template._


[napari]: https://github.com/napari/napari
[Cookiecutter]: https://github.com/audreyr/cookiecutter
[@napari]: https://github.com/napari
[MIT]: http://opensource.org/licenses/MIT
[BSD-3]: http://opensource.org/licenses/BSD-3-Clause
[GNU GPL v3.0]: http://www.gnu.org/licenses/gpl-3.0.txt
[GNU LGPL v3.0]: http://www.gnu.org/licenses/lgpl-3.0.txt
[Apache Software License 2.0]: http://www.apache.org/licenses/LICENSE-2.0
[Mozilla Public License 2.0]: https://www.mozilla.org/media/MPL/2.0/index.txt
[cookiecutter-napari-plugin]: https://github.com/napari/cookiecutter-napari-plugin
[file an issue]: https://github.com/tlambert03/napari-pims-bioformats/issues
[napari]: https://github.com/napari/napari
[tox]: https://tox.readthedocs.io/en/latest/
[pip]: https://pypi.org/project/pip/
[conda]: https://docs.conda.io/en/latest/
[conda-forge]: https://conda-forge.org
[PyPI]: https://pypi.org/
