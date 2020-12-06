from napari_plugin_engine import napari_hook_implementation
from pims.bioformats import BioformatsReader
import numpy as np

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
    if isinstance(path, str) and path.endswith(SUPPORTED_FORMATS):
        return reader_function
    return None


def reader_function(path):
    """Take a path or list of paths and return a list of LayerData tuples.

    Readers are expected to return data as a list of tuples, where each tuple
    is (data, [add_kwargs, [layer_type]]), "add_kwargs" and "layer_type" are
    both optional.

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
    axes = [ax for ax in "tczyx" if ax in reader.axes]
    reader.bundle_axes = axes
    try:
        channel_axis = axes.index("c")
    except ValueError:
        channel_axis = None

    # stack arrays into single array
    data = np.asarray(np.squeeze(reader[0]))
    try:
        dz = reader.metadata.PixelsPhysicalSizeZ(0)
        dx = reader.metadata.PixelsPhysicalSizeX(0)
        scale = [(np.round(dz / dx, 4) if ax == "z" else 1) for ax in axes if ax != "c"]
    except AttributeError:
        scale = None

    meta = {
        "channel_axis": channel_axis,
        "name": str(reader.metadata.ImageName(0)),
        "scale": scale,
    }

    return [(data, meta)]
