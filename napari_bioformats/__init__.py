try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

from ._core import download_loci_jar, napari_get_reader, read_bioformats

__all__ = ["napari_get_reader", "read_bioformats", "download_loci_jar"]
