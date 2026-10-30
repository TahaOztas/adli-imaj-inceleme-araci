from PyQt5.QtWidgets import QTreeView, QFileSystemModel, QFileDialog

class DirectoryTree:
    """
    Sol panelde dosya ağacını gösteren bileşen.
    """
    def __init__(self):
        self.model = QFileSystemModel()
        self.view = QTreeView()
        self.view.setModel(self.model)
        for col in (1,2,3):
            self.view.hideColumn(col)
        self.view.setVisible(False)

    def add_all_disks(self):
        self.model.setRootPath('')
        self.view.setRootIndex(self.model.index(''))
        self.view.setVisible(True)

    def add_directory(self):
        directory = QFileDialog.getExistingDirectory(None, "Klasör Seç")
        if directory:
            self.model.setRootPath(directory)
            idx = self.model.index(directory)
            self.view.setRootIndex(idx)
            self.view.setVisible(True)