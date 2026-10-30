# arayuz.py
import sys, os, time, hashlib
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QToolBar, QAction, QDateTimeEdit, QFileDialog, QMessageBox,
    QPlainTextEdit, QTableWidget, QTableWidgetItem, QTreeView,
    QFileSystemModel, QGroupBox, QFormLayout, QLabel, QSizePolicy, QSlider, QPushButton
)
from PyQt5.QtCore import QDateTime, Qt, QUrl, QTimer
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget

class ForensicViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Adli Bilim Aracı")
        self.resize(1200, 800)
        self.view_mode = 'hex'
        self.current_path = None
        self._setup_ui()

    def _setup_ui(self):
        tb = QToolBar(); self.addToolBar(tb)
        a_open = QAction("Klasör Aç", self)
        a_toggle = QAction("Metin Modu", self); a_toggle.setCheckable(True)
        tb.addAction(a_open); tb.addSeparator(); tb.addAction(a_toggle); tb.addSeparator()
        dt = QDateTimeEdit(QDateTime.currentDateTime(), self); dt.setDisplayFormat("dd.MM.yyyy HH:mm:ss")
        tb.addWidget(dt)
        a_open.triggered.connect(self.open_directory)
        a_toggle.toggled.connect(lambda c: setattr(self, 'view_mode', 'text' if c else 'hex'))

        central = QWidget(); hl = QHBoxLayout(central)

        # Left panel - Tree View
        self.tree = QTreeView()
        self.tree.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.fs_model = QFileSystemModel()
        self.tree.setModel(self.fs_model)
        for col in (1,2,3): self.tree.hideColumn(col)
        self.tree.clicked.connect(self.on_tree_click)
        hl.addWidget(self.tree, 2)

        # Middle panel - Table + Content
        vl = QVBoxLayout()
        self.table = QTableWidget(); self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["İsim","Tür","Boyut","Oluşturulma"])
        self.table.cellClicked.connect(self.on_table_click)
        self.table.cellDoubleClicked.connect(self.on_table_double_click)
        vl.addWidget(self.table, 3)

        # Content Viewer
        self.image_label = QLabel(alignment=Qt.AlignCenter); self.image_label.hide()

        self.video_widget = QVideoWidget(); self.video_widget.setMinimumHeight(300); self.video_widget.hide()
        self.player = QMediaPlayer(); self.player.setVideoOutput(self.video_widget)

        self.play_button = QPushButton("⏸")
        self.play_button.setFixedSize(30, 30)
        self.play_button.clicked.connect(self.toggle_play)
        self.play_button.hide()

        self.slider = QSlider(Qt.Horizontal); self.slider.hide()
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.hide()
        self.slider.sliderMoved.connect(self.seek_video)

        self.player.positionChanged.connect(self.update_slider)
        self.player.positionChanged.connect(self.update_time_label)
        self.player.durationChanged.connect(lambda d: self.slider.setMaximum(d))

        self.hex_view = QPlainTextEdit(); self.hex_view.setReadOnly(True)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0,0,0,0)
        content_layout.addWidget(self.image_label)
        content_layout.addWidget(self.video_widget)
        
        time_layout = QHBoxLayout()
        self.time_label_start = QLabel("00:00")
        self.time_label_end = QLabel("00:00")
        self.time_label_start.setFixedWidth(50)
        self.time_label_end.setFixedWidth(50)
        time_layout.addWidget(self.time_label_start)
        time_layout.addWidget(self.slider)
        time_layout.addWidget(self.time_label_end)
        controls_layout = QVBoxLayout()
        controls_layout.addWidget(self.play_button, alignment=Qt.AlignCenter)
        controls_layout.addLayout(time_layout)
        content_layout.addLayout(controls_layout)
        content_layout.addWidget(self.hex_view)
        content_widget = QWidget(); content_widget.setLayout(content_layout)
        vl.addWidget(content_widget, 2)
        hl.addLayout(vl, 5)

        # Right panel - Metadata
        meta = QGroupBox("Metadata"); form = QFormLayout()
        self.labels = {}
        for key in ("İsim","Tür","Boyut","Oluşturulma","Değişiklik","MD5","SHA1","İzinler","Sahip"):
            lbl = QLabel(""); form.addRow(f"{key}:", lbl); self.labels[key] = lbl
        meta.setLayout(form); meta.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        hl.addWidget(meta, 2)

        self.setCentralWidget(central)

    def toggle_play(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause(); self.play_button.setText("▶")
        else:
            self.player.play(); self.play_button.setText("⏸")

    def seek_video(self, position):
        self.player.setPosition(position)

    def update_slider(self, position):
        self.slider.blockSignals(True)
        self.slider.setValue(position)
        self.slider.blockSignals(False)

    def update_time_label(self, position):
        duration = self.player.duration()
        pos_min, pos_sec = divmod(position // 1000, 60)
        dur_min, dur_sec = divmod(duration // 1000, 60)
        self.time_label_start.setText(f"{pos_min:02}.{pos_sec:02}")
        self.time_label_end.setText(f"{dur_min:02}.{dur_sec:02}")


    def open_directory(self):
        path = QFileDialog.getExistingDirectory(self, "Klasör Seç")
        if not path: return
        self.current_path = path
        self.fs_model.setRootPath(path)
        self.tree.setRootIndex(self.fs_model.index(path))
        self._load_directory(path)

    def on_tree_click(self, index):
        path = self.fs_model.filePath(index)
        if os.path.isdir(path): self.current_path=path; self._load_directory(path)
        else: self.load_file(path)

    def on_table_click(self, row, col):
        name=self.table.item(row,0).text()
        if name=="..": return self._go_parent()
        path=os.path.join(self.current_path,name)
        if os.path.isdir(path): return self._enter_dir(path)
        self.load_file(path)

    def on_table_double_click(self, row, col): self.on_table_click(row,col)

    def _go_parent(self):
        parent=os.path.dirname(self.current_path)
        if parent: self.current_path=parent; self._enter_dir(parent)

    def _enter_dir(self, path):
        self.tree.setExpanded(self.fs_model.index(path),True)
        self._load_directory(path)

    def _load_directory(self, path):
        items=sorted(os.listdir(path)); entries=[".."]+items
        self.table.setRowCount(len(entries))
        for r,n in enumerate(entries):
            full=os.path.join(path,n) if n!=".." else None
            if n=="..":t,s,ctime="Önceki Dizin","",""
            else:
                if os.path.isdir(full): t='Klasör';s=''
                else:
                    ext=os.path.splitext(n)[1].lstrip('.')
                    t=f"{ext.upper()} dosyası" if ext else "Unknown"; size=os.path.getsize(full)
                    for u in ['B','KB','MB','GB']:
                        if size<1024: s=f"{size:.1f} {u}"; break
                        size/=1024
                ctime=time.ctime(os.path.getctime(full))
            self.table.setItem(r,0,QTableWidgetItem(n));self.table.setItem(r,1,QTableWidgetItem(t))
            self.table.setItem(r,2,QTableWidgetItem(s));self.table.setItem(r,3,QTableWidgetItem(ctime))

    def load_file(self, path):
        self.player.stop()
        self.current_path=os.path.dirname(path); self.current_file=path
        ext=os.path.splitext(path)[1].lower()
        self.image_label.hide(); self.video_widget.hide(); self.hex_view.hide()
        self.play_button.hide(); self.slider.hide(); self.time_label.hide()

        if ext in ('.png','.jpg','.jpeg','.bmp','.gif') and self.view_mode=='hex':
            pix=QPixmap(path)
            self.image_label.setPixmap(pix.scaled(self.image_label.size(),Qt.KeepAspectRatio,Qt.SmoothTransformation))
            self.image_label.show()
        elif ext in ('.mp4','.avi','.mkv','.mov') and self.view_mode=='hex':
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(path)))
            self.video_widget.show(); self.slider.show(); self.play_button.show(); self.time_label.show()
            self.player.play(); self.play_button.setText("⏸")
        else:
            try: data=open(path,'rb').read(); hexs=data.hex(); spaced=' '.join(hexs[i:i+2] for i in range(0,len(hexs),2))
            except Exception as e: spaced=f"Error: {e}"
            self.hex_view.setPlainText(spaced); self.hex_view.show()
        self._update_metadata(path)

    def _update_metadata(self,path):
        st=os.stat(path); is_f=os.path.isfile(path)
        self.labels['İsim'].setText(os.path.basename(path))
        self.labels['Tür'].setText('Dosya' if is_f else 'Klasör')
        self.labels['Boyut'].setText(str(st.st_size) if is_f else '')
        self.labels['Oluşturulma'].setText(time.ctime(st.st_ctime))
        self.labels['Değişiklik'].setText(time.ctime(st.st_mtime))
        if is_f:
            data=open(path,'rb').read(); self.labels['MD5'].setText(hashlib.md5(data).hexdigest()); self.labels['SHA1'].setText(hashlib.sha1(data).hexdigest())
        self.labels['İzinler'].setText(oct(st.st_mode)[-3:]); self.labels['Sahip'].setText(str(st.st_uid))

if __name__=='__main__':
    app=QApplication(sys.argv); viewer=ForensicViewer(); viewer.show(); sys.exit(app.exec_())
