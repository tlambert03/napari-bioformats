from qtpy.QtCore import QEventLoop, QFile, QUrl
from qtpy.QtNetwork import QNetworkAccessManager, QNetworkRequest
from qtpy.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
)


class DownloadDialog(QDialog):
    def __init__(self, url=None, dest=None, parent=None) -> None:
        super().__init__(parent=parent)
        self.setModal(True)
        self._progress = QProgressBar()
        self._status = QLabel()
        self._cancelbtn = QPushButton("cancel")
        self._cancelbtn.clicked.connect(self._cancel)
        self.help_text = QLabel()
        self.help_text.setVisible(False)
        self.setLayout(QVBoxLayout())
        row2 = QHBoxLayout()
        row2.addWidget(self._progress)
        row2.addWidget(self._status)
        row2.addWidget(self._cancelbtn)
        self.layout().addWidget(self.help_text)
        self.layout().addLayout(row2)
        self.file = QFile(self)

    def download(self, url, destination=None):
        self._progress.setValue(0)
        self.manager = QNetworkAccessManager()
        self.manager.setRedirectPolicy(QNetworkRequest.NoLessSafeRedirectPolicy)
        self.manager.finished.connect(self._on_download_finished)
        self.reply = self.manager.get(QNetworkRequest(QUrl(url)))
        self.reply.downloadProgress.connect(self._update_progress)

        if destination:
            self.file.setFileName(destination)
            self.file.open(QFile.WriteOnly)
            self.reply.readyRead.connect(self._on_ready_read)

    def _on_ready_read(self):
        if self.file.isOpen():
            self.file.write(self.reply.readAll())

    def _update_progress(self, cur, tot):
        self._progress.setMaximum(tot)
        self._progress.setValue(cur)
        self._status.setText(f"{cur*1e-6:0.2f} MB / {tot*1e-6:0.2f} MB")

    def _on_download_finished(self, reply):
        if self.file.isOpen():
            self.file.close()
        self.close()

    def _cancel(self):
        self.reply.abort()
        self.file.exists()
        if self.file.exists():
            self.file.close()
            self.file.remove()

    def closeEvent(self, a0) -> None:
        self._cancel()
        return super().closeEvent(a0)

    def wait(self):
        if self.reply.isRunning():
            loop = QEventLoop()
            self.reply.finished.connect(loop.quit)
            loop.exec_()
