try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

from ._pims import napari_get_reader, read_bioformats

__all__ = ["napari_get_reader", "read_bioformats"]
