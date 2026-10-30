from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt5.QtGui import QIcon
import os, time

class FileTable:
    """
    Orta panelde dosya listesi ve imaj girdilerini gösterir.
    """
    def __init__(self):
        self.widget = QTableWidget()
        self.widget.setColumnCount(4)
        self.widget.setHorizontalHeaderLabels(["İsim", "Tür", "Boyut", "Oluşturma"])
        self.widget.setAlternatingRowColors(True)
        self.widget.setSelectionBehavior(self.widget.SelectRows)
        self.widget.setEditTriggers(self.widget.NoEditTriggers)

    def load_path(self, path, deleted=set(), corrupted=set()):
        items = os.listdir(path)
        self.widget.setRowCount(len(items))
        for row, name in enumerate(items):
            full = os.path.join(path, name)
            kind = 'Dosya' if os.path.isfile(full) else 'Klasör'
            size = os.path.getsize(full) if os.path.isfile(full) else ''
            ctime = time.ctime(os.path.getctime(full))
            item = QTableWidgetItem(name)
            if name in deleted:
                item.setIcon(QIcon('icons/deleted.png'))
            if name in corrupted:
                item.setIcon(QIcon('icons/corrupt.png'))
            self.widget.setItem(row, 0, item)
            self.widget.setItem(row, 1, QTableWidgetItem(kind))
            self.widget.setItem(row, 2, QTableWidgetItem(str(size)))
            self.widget.setItem(row, 3, QTableWidgetItem(ctime))

    def load_image_entries(self, entries, deleted=set(), corrupted=set()):
        self.widget.setRowCount(len(entries))
        for row, (name, is_dir) in enumerate(entries):
            item = QTableWidgetItem(name)
            base = name.rstrip('/')
            if base in deleted:
                item.setIcon(QIcon('icons/deleted.png'))
            if base in corrupted:
                item.setIcon(QIcon('icons/corrupt.png'))
            self.widget.setItem(row, 0, item)
            self.widget.setItem(row, 1, QTableWidgetItem('Klasör' if is_dir else 'Dosya'))
            self.widget.setItem(row, 2, QTableWidgetItem(''))
            self.widget.setItem(row, 3, QTableWidgetItem(''))
