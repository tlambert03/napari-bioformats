__all__ = [
    "dask_bioformats",
    "napari_get_reader",
    "read_bioformats",
    "download_loci_jar",
]

try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Union
    from pathlib import Path
    import dask.array as da

from ._core import download_loci_jar, napari_get_reader, read_bioformats


def dask_bioformats(path: "Union[str, Path]" = None) -> "da.Array":
    from ._core import _get_loci_reader, _reader2dask

    return _reader2dask(_get_loci_reader(path))
