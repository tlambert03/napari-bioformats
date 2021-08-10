"""Routines for finding java and loci_tools"""
import os
from pathlib import Path

from pims.bioformats import _gen_jar_locations
from qtpy.QtCore import QProcess, QProcessEnvironment
from qtpy.QtWidgets import QDialog, QPushButton, QTextEdit, QVBoxLayout


def _get_current_window():
    try:
        from napari._qt.qt_main_window import _QtMainWindow

        return _QtMainWindow.current().qt_viewer
    except Exception:
        return None


class CondaInstaller(QDialog):
    def __init__(self) -> None:
        super().__init__(parent=_get_current_window())
        self.setModal(True)

        self._output_widget = QTextEdit(self)
        self._output_widget.setReadOnly(True)
        self._closebtn = QPushButton("cancel", self)
        self._closebtn.clicked.connect(self._cancel)

        self.process = QProcess()
        self.process.setProgram("conda")
        self.process.finished.connect(self.accept)
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.readyReadStandardOutput.connect(self._on_stdout_ready)
        # setup process path
        self.process.setProcessEnvironment(QProcessEnvironment.systemEnvironment())

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self._output_widget)
        self.layout().addWidget(self._closebtn)

    def _on_stdout_ready(self):
        text = self.process.readAllStandardOutput().data().decode()
        self._output_widget.append(text)

    def _cancel(self):
        self.process.kill()
        self.reject()

    def install(self, env, *packages):
        self.process.setArguments(["install", "-y", "--name", env] + list(packages))
        self._output_widget.clear()
        self.process.start()


def _show_jdk_message():
    from qtpy.QtWidgets import QMessageBox

    env_name = os.getenv("CONDA_DEFAULT_ENV")
    prefix = os.getenv("CONDA_PREFIX")
    parent = _get_current_window()
    if env_name and prefix:
        msg = (
            "napari-bioformats requires a java but could not detect it in your "
            f"environment.\n\nIt looks like you are running in a conda environment "
            f"({env_name!r}).  Would you like to install 'openjdk' from the "
            "conda-forge channel?\n\n"
            "(You may also install java manually and set the JAVA_HOME environment "
            "variable properly)."
        )
        if QMessageBox.question(parent, "No JVM found", msg) == QMessageBox.Yes:
            conda_dialog = CondaInstaller()
            conda_dialog.install(env_name, "openjdk")
            if conda_dialog.exec_() == QDialog.Accepted:
                os.environ["JAVA_HOME"] = prefix
                return True
    else:
        msg = (
            "napari-bioformats requires a JVM but could not detect one in your "
            "environment.  Please install java or set the JAVA_HOME environment "
            "variable."
        )
        QMessageBox.information(parent, "No JVM found", msg)
    return False


def download_loci_jar(v="latest"):
    import hashlib
    from urllib.request import urlopen

    from ._downloader import DownloadDialog

    url = (
        f"https://downloads.openmicroscopy.org/bio-formats/{v}/artifacts/loci_tools.jar"
    )

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

    d = DownloadDialog(parent=_get_current_window())
    d.help_text.setText("Downloading Bioformats. This will only happen once")
    d.help_text.show()
    d.show()
    d.download(url)
    d.wait()
    if not d.reply.isReadable():
        return False

    loci_tools = bytes(d.reply.readAll())
    sha1_checksum = urlopen(url + ".sha1").read().split(b" ")[0].decode()
    if hashlib.sha1(loci_tools).hexdigest() != sha1_checksum:
        raise OSError(
            "Downloaded loci_tools.jar has invalid checksum. Please try again."
        )

    with open(loc / "loci_tools.jar", "wb") as output:
        output.write(loci_tools)
    return True
