import threading
from contextlib import suppress
from functools import lru_cache
from pathlib import Path
from typing import Tuple

import dask.array as da
import numpy as np
import ome_types
from napari_plugin_engine import napari_hook_implementation

JAVA_MEMORY = "1024m"
# fmt: off
SUPPORTED_FORMATS = (
    '.afm', '.nef', '.lif', '.nhdr', '.ps', '.bmp', '.frm', '.pr3', '.tif',
    '.aim', '.dat', '.fits', '.pcoraw', '.qptiff', '.acff', '.xys', '.mrw',
    '.xml', '.svs', '.arf', '.dm4', '.ome.xml', '.v', '.pds', '.zvi', '.apl',
    '.mrcs', '.i2i', '.mdb', '.ipl', '.oir', '.ali', '.fff', '.vms', '.jpg',
    '.inr', '.pcx', '.vws', '.html', '.al3d', '.ims', '.bif', '.labels',
    '.dicom', '.par', '.map', '.ome.tf2', '.htd', '.tnb', '.mrc',
    '.obf', '.xdce', '.png', '.jpx', '.fli', '.psd', '.pgm', '.obsep',
    '.jpk', '.ome.tif', '.rcpnl', '.pbm', '.grey', '.raw', '.zfr', '.klb',
    '.spc', '.sdt', '.2fl', '.ndpis', '.ipm', '.pict', '.st', '.seq', '.nii',
    '.lsm', '.epsi', '.cr2', '.zfp', '.wat', '.lim', '.1sc', '.ffr', '.liff',
    '.mea', '.nd2', '.tf8', '.naf', '.ch5', '.afi', '.ipw', '.img', '.ids',
    '.mnc', '.crw', '.mtb', '.cxd', '.gel', '.dv', '.jpf', '.tga', '.vff',
    '.ome.tiff', '.ome', '.bin', '.cfg', '.dti', '.ndpi', '.c01', '.avi',
    '.sif', '.flex', '.txt', '.spe', '.ics', '.jp2', '.xv', '.spi', '.lms',
    '.sld', '.vsi', '.lei', '.sm3', '.hx', '.czi', '.nrrd', '.ppm', '.exp',
    '.mov', '.xqd', '.dm3', '.im3', '.pic', '.his', '.j2k', '.rec', '.top',
    '.pnl', '.tf2', '.oif', '.l2d', '.stk', '.fdf', '.mng', '.ome.btf',
    '.tfr', '.res', '.dm2', '.eps', '.hdr', '.am', '.stp', '.sxm',
    '.ome.tf8', '.dib', '.mvd2', '.wlz', '.nd', '.h5', '.cif', '.mod',
    '.nii.gz', '.bip', '.oib', '.csv', '.amiramesh', '.scn', '.gif',
    '.sm2', '.tiff', '.hdf', '.hed', '.r3d', '.wpi', '.dcm', '.btf',
    '.msr', '.xqf'
)
# fmt: on


@napari_hook_implementation(trylast=True)
def napari_get_reader(path):
    """A basic implementation of the napari_get_reader hook specification.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    function or None
        If the path is a recognized format, return a function that accepts the
        same path or list of paths, and returns a list of layer data tuples.
    """
    if isinstance(path, (str, Path)) and str(path).endswith(SUPPORTED_FORMATS):
        return read_bioformats
    return None


def _load_loci():
    import jpype

    # Start java VM and initialize logger (globally)
    if not jpype.isJVMStarted():
        jpype.startJVM(
            jpype.getDefaultJVMPath(),
            "-ea",
            f"-Djava.class.path={Path(__file__).parent / 'bioformats.jar'}",
            "-Xmx" + JAVA_MEMORY,
            convertStrings=False,
        )
        loci = jpype.JPackage("loci")
        loci.common.DebugTools.setRootLevel("ERROR")

    if not jpype.isThreadAttachedToJVM():
        jpype.attachThreadToJVM()

    return jpype.JPackage("loci")


def _get_loci_reader(path, meta=False):
    loci = _load_loci()
    rdr = loci.formats.ChannelSeparator(loci.formats.ChannelFiller())
    if meta:
        _meta = loci.formats.MetadataTools.createOMEXMLMetadata()
        rdr.setMetadataStore(_meta)
    rdr.setId(str(path))
    return (rdr, _meta) if meta else rdr


_FMT_2_DTYPE = {
    0: "i1",  # int8
    1: "u1",  # uint8
    2: "i2",  # int16
    3: "u2",  # uint16
    4: "i4",  # int32
    5: "u4",  # uint32
    6: "f4",  # float32
    7: "f8",  # float64
}


def _get_shape_dtype(rdr) -> Tuple[Tuple[int, int, int, int, int], str]:
    """Returns shape (TCZYX) and dtype of rdr"""
    shape = (
        rdr.getSizeT(),
        rdr.getRGBChannelCount() if rdr.isRGB() else rdr.getSizeC(),
        rdr.getSizeZ(),
        rdr.getSizeY(),
        rdr.getSizeX(),
    )
    le = rdr.isLittleEndian()
    pixel_type = ("<" if le else ">") + _FMT_2_DTYPE[rdr.getPixelType()]
    return shape, pixel_type


# TODO: figure this out with dask
lock = threading.Lock()


def _load_block(rdr, block_info: dict) -> np.ndarray:
    """Load a single plane with a loci reader"""
    info = block_info[None]
    idx = rdr.getIndex(*info["chunk-location"][2::-1])  # Z, C, T
    with lock:
        im = np.frombuffer(rdr.openBytes(idx)[:], dtype=info["dtype"]).copy()
    im.shape = info["shape"][-2:]
    return im[np.newaxis, np.newaxis, np.newaxis]


def read_bioformats(path, split_channels=True):
    """Take a path or list of paths and return a list of LayerData tuples.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    layer_data : list of tuples
        A list of LayerData tuples where each tuple in the list contains
        (data, metadata, layer_type), where data is a numpy array, metadata is
        a dict of keyword arguments for the corresponding viewer.add_* method
        in napari, and layer_type is a lower-case string naming the type of layer.
        Both "meta", and "layer_type" are optional. napari will default to
        layer_type=="image" if not provided
    """
    import jpype

    # load all files into array
    try:
        reader, loci_meta = _get_loci_reader(path, meta=True)
    except jpype.JVMNotFoundException as e:
        try:
            from ._dialogs import _show_jdk_message

            # will return true if the dialog successfully installed Java
            if _show_jdk_message():
                return read_bioformats(path, split_channels=split_channels)
        except ImportError:
            pass
        raise jpype.JVMNotFoundException(
            "napari-bioformats requires (but could not find) a java virtual machine. "
            "please install java and try again."
        ) from e

    axes = "tczyx"
    try:
        _sizes = {
            "z": loci_meta.getPixelsPhysicalSizeZ(0).value(),
            "y": loci_meta.getPixelsPhysicalSizeY(0).value(),
            "x": loci_meta.getPixelsPhysicalSizeX(0).value(),
            "t": 1,
            "c": 1,
        }
        _ax = [x for x in axes if x != "c"] if split_channels else axes
        scale = [round(_sizes[ax], 5) for ax in _ax]
    except AttributeError:
        scale = None

    meta = {
        "channel_axis": 1 if split_channels else None,
        "name": str(loci_meta.getImageName(0)),
        "scale": scale,
        "metadata": {
            "ome_types": lru_cache(maxsize=1)(
                lambda: ome_types.from_xml(loci_meta.dumpXML())
            )
        },
    }

    if meta.get("channel_axis") is not None:
        names = []
        colormaps = []
        for x in range(reader.getSizeC()):
            names.append(str(loci_meta.getChannelName(0, x)) + f": {meta['name']}")
            jclr = loci_meta.getChannelColor(0, x)
            rgb = _jrgba_to_rgb(jclr.getValue()) if jclr else (1.0, 1.0, 1.0)
            cmap = _PRIMARY_COLORS.get(rgb)
            if cmap is None:
                with suppress(ImportError):
                    from napari.utils.colormaps import Colormap

                    cmap = Colormap([[0, 0, 0], rgb])
            colormaps.append(cmap)
        meta["name"] = names or meta["name"]
        if colormaps:
            meta["colormap"] = colormaps

    return [(_reader2dask(reader), meta)]


_PRIMARY_COLORS = {
    (1.0, 0.0, 0.0): "red",
    (0.0, 1.0, 0.0): "green",
    (0.0, 0.0, 1.0): "blue",
    (0.0, 1.0, 1.0): "cyan",
    (1.0, 1.0, 0.0): "yellow",
    (1.0, 0.0, 1.0): "magenta",
    (0.0, 0.0, 0.0): "black",
    (1.0, 1.0, 1.0): "gray",
}


def _jrgba_to_rgb(rgba):
    return (
        (rgba >> 24 & 255) / 255.0,
        (rgba >> 16 & 255) / 255.0,
        (rgba >> 8 & 255) / 255.0,
    )


def download_loci_jar(v="latest", loc=Path(__file__).parent):
    """Download version `v` of loci_tools` to directory `loc`."""
    import hashlib
    import os
    from urllib.request import urlopen

    url = (
        f"https://downloads.openmicroscopy.org/bio-formats/{v}/artifacts/loci_tools.jar"
    )

    if loc is None:
        from pims.bioformats import _gen_jar_locations

        for loc in _gen_jar_locations():
            # check if dir exists and has write access:
            loc = Path(loc)
            if loc.exists() and os.access(loc, os.W_OK):
                break
            # if directory is pims and it does not exist, so make it (if allowed)
            if loc.name == "pims" and os.access(loc.parent, os.W_OK):
                loc.mkdir(exist_ok=True)
                break
        else:
            raise OSError(
                "No writeable location found. In order to use the Bioformats reader, "
                f"please download loci_tools.jar ({url}) to one of the following "
                f"locations:\n{list(_gen_jar_locations())}."
            )

    try:
        from qtpy.QtWidgets import QApplication

        from ._dialogs import _get_current_window
        from ._downloader import DownloadDialog

        if QApplication.instance() is None:
            raise RuntimeError()
        d = DownloadDialog(parent=_get_current_window())
        d.help_text.setText("Downloading Bioformats. This will only happen once")
        d.help_text.show()
        d.show()
        d.download(url)
        d.wait()
        if not d.reply.isReadable():
            return False
        loci_tools = bytes(d.reply.readAll())
    except (ImportError, RuntimeError):  # if no Qt is installed
        print("downloading...")
        loci_tools = urlopen(url).read()

    sha1_checksum = urlopen(url + ".sha1").read().split(b" ")[0].decode()
    if hashlib.sha1(loci_tools).hexdigest() != sha1_checksum:
        raise OSError(
            "Downloaded loci_tools.jar has invalid checksum. Please try again."
        )

    with open(loc / "loci_tools.jar", "wb") as output:
        output.write(loci_tools)
    return True


def _reader2dask(rdr):
    (nt, nc, nz, ny, nx), dtype = _get_shape_dtype(rdr)
    return da.map_blocks(
        _load_block,
        rdr,
        chunks=((1,) * nt, (1,) * nc, (1,) * nz, (ny,), (nx,)),
        dtype=dtype,
    )
