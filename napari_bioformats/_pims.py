from napari_plugin_engine import napari_hook_implementation
from pims.bioformats import BioformatsReader
import numpy as np
import pathlib

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
    if isinstance(path, (str, pathlib.Path)) and str(path).endswith(SUPPORTED_FORMATS):
        return read_bioformats
    return None


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

    # load all files into array
    reader = BioformatsReader(path, read_mode="jpype")

    # The bundle_axes property defines which axes will be present in a single frame.
    # The frame_shape property is changed accordingly:
    axes = [ax for ax in "tczyx" if ax in reader.axes]
    reader.bundle_axes = axes

    # stack arrays into single array
    try:
        _sizes = {
            "y": reader.metadata.PixelsPhysicalSizeY(0),
            "x": reader.metadata.PixelsPhysicalSizeX(0),
            "z": reader.metadata.PixelsPhysicalSizeZ(0),
            "t": 1,
            "c": 1,
        }
        _ax = [x for x in axes if x != "c"] if split_channels else axes
        scale = [round(_sizes[ax], 5) for ax in _ax]
    except AttributeError:
        scale = None

    meta = {
        "channel_axis": axes.index("c") if split_channels and "c" in axes else None,
        "name": str(reader.metadata.ImageName(0)),
        "scale": scale,
    }
    if meta.get("channel_axis") and reader.colors:
        meta["colormap"] = [_PRIMARY_COLORS.get(c) for c in reader.colors]

    def retrieve_ome_metadata():
        import ome_types

        return ome_types.from_xml(str(reader._metadata.dumpXML()))

    meta["metadata"] = retrieve_ome_metadata

    return [(reader[0], meta)]
