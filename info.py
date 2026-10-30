from PyQt5.QtWidgets import QPlainTextEdit

class HexViewer:
    """
    Alt panelde hex veya düz metin gösterimi.
    """
    def __init__(self):
        self.widget = QPlainTextEdit()
        self.widget.setReadOnly(True)
        self.mode = 'hex'

    def set_mode(self, mode):
        self.mode = mode

    def display_content(self, data: bytes):
        if self.mode == 'text':
            try:
                txt = data.decode(errors='replace')
            except:
                txt = ''
            self.widget.setPlainText(txt)
        else:
            h = data.hex()
            spaced = ' '.join(h[i:i+2] for i in range(0, len(h), 2))
            self.widget.setPlainText(spaced)
