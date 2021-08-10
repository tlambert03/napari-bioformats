from contextlib import suppress
from functools import lru_cache
from pathlib import Path

import ome_types
from napari_plugin_engine import napari_hook_implementation

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


def _has_jar():
    from pims.bioformats import _gen_jar_locations

    for loc in _gen_jar_locations():
        jar = Path(loc) / "loci_tools.jar"
        if jar.is_file():
            return True
    return False


def download_jar():
    try:
        from ._dialogs import download_loci_jar

        return download_loci_jar("latest")
    except ImportError:
        from pims.bioformats import download_jar

        return download_jar("latest")


def read_bioformats(path, split_channels=True, java_memory="1024m"):
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
    from pims.bioformats import BioformatsReader

    if not _has_jar() and not download_jar():
        return

    # load all files into array
    try:
        reader = BioformatsReader(
            path, java_memory=java_memory, meta=False, read_mode="jpype"
        )
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

    # The bundle_axes property defines which axes will be present in a single frame.
    # The frame_shape property is changed accordingly:
    axes = [ax for ax in "tczyx" if ax in reader.axes]
    # stack arrays into single array
    reader.bundle_axes = axes

    loci = jpype.JPackage("loci")
    _meta = loci.formats.MetadataTools.createOMEXMLMetadata()
    reader.rdr.close()
    reader.rdr.setMetadataStore(_meta)
    reader.rdr.setId(reader.filename)
    xml = str(_meta.dumpXML())

    try:
        _sizes = {
            "z": _meta.getPixelsPhysicalSizeZ(0).value(),
            "y": _meta.getPixelsPhysicalSizeY(0).value(),
            "x": _meta.getPixelsPhysicalSizeX(0).value(),
            "t": 1,
            "c": 1,
        }
        _ax = [x for x in axes if x != "c"] if split_channels else axes
        scale = [round(_sizes[ax], 5) for ax in _ax]
    except AttributeError:
        scale = None

    meta = {
        "channel_axis": axes.index("c") if split_channels and "c" in axes else None,
        "name": str(_meta.getImageName(0)),
        "scale": scale,
        "metadata": {
            "ome_types": lru_cache(maxsize=1)(lambda: ome_types.from_xml(xml))
        },
    }
    if meta.get("channel_axis") is not None:
        names = []
        colormaps = []
        for x in range(reader.sizes.get("c", 0)):
            names.append(str(_meta.getChannelName(0, x)) + f": {meta['name']}")
            jclr = _meta.getChannelColor(0, x)
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

    return [(reader[0], meta)]


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
