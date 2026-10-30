from PyQt5.QtWidgets import QGroupBox, QFormLayout, QLabel
import os, time, hashlib

class MetadataPanel:
    """
    Sağ panelde dosya metadata'sını gösterir.
    """
    def __init__(self):
        self.group = QGroupBox("Metadata")
        layout = QFormLayout()
        self.labels = {}
        for key in ("İsim","Tür","Boyut","Oluşturulma","Değişiklik","MD5","SHA1","İzinler","Sahip"): 
            lbl = QLabel("")
            layout.addRow(f"{key}:", lbl)
            self.labels[key] = lbl
        self.group.setLayout(layout)

    def update(self, path):
        if not os.path.exists(path): return
        is_file = os.path.isfile(path)
        self.labels["İsim"].setText(os.path.basename(path))
        self.labels["Tür"].setText('Dosya' if is_file else 'Klasör')
        self.labels["Boyut"].setText(str(os.path.getsize(path)) if is_file else '')
        self.labels["Oluşturulma"].setText(time.ctime(os.path.getctime(path)))
        self.labels["Değişiklik"].setText(time.ctime(os.path.getmtime(path)))
        if is_file:
            data = open(path,'rb').read()
            self.labels["MD5"].setText(hashlib.md5(data).hexdigest())
            self.labels["SHA1"].setText(hashlib.sha1(data).hexdigest())
        self.labels["İzinler"].setText(oct(os.stat(path).st_mode)[-3:])
        self.labels["Sahip"].setText(str(os.stat(path).st_uid))