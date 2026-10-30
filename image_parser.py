import os
import pytsk3
import pyewf

class EWFImgInfo(pytsk3.Img_Info):
    def __init__(self, ewf_handle):
        self._ewf_handle = ewf_handle
        super().__init__(url="", type=pytsk3.TSK_IMG_TYPE_EXTERNAL)

    def read(self, offset, size):
        self._ewf_handle.seek(offset)
        return self._ewf_handle.read(size)

    def get_size(self):
        return self._ewf_handle.get_media_size()

class DiskImageParser:
    def __init__(self, image_path):
        if not isinstance(image_path, str):
            image_path = str(image_path)
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Dosya bulunamadı: {image_path}")

        # uzantıyı küçük harfe çevir
        image_path_lower = image_path.lower()

        if image_path_lower.endswith(".e01"):
            try:
                image_path = os.path.abspath(image_path)  # yol tam olsun
                filenames = pyewf.glob([image_path])     # HATA BURADAYDI: liste içinde ver
                ewf_handle = pyewf.handle()
                ewf_handle.open(filenames)
                img_info = EWFImgInfo(ewf_handle)

            except Exception as e:
                raise Exception(f"E01 dosyası glob yapılamadı: {e}")
        else:
            try:
                img_info = pytsk3.Img_Info(image_path)
            except Exception as e:
                raise Exception(f"İmaj dosyası açılamadı: {e}")

        # Dosya sistemini bulmak için offset belirle
        try:
            volume = pytsk3.Volume_Info(img_info)
            fs_offset = None
            for part in volume:
                desc = part.desc.decode(errors="ignore").lower()
                if "ntfs" in desc or "fat" in desc or "basic data" in desc:
                    fs_offset = part.start * 512
                    break
            if fs_offset is None:
                raise Exception("Desteklenen dosya sistemi bölümü bulunamadı.")
        except IOError:
            # Eğer partition tablosu yoksa doğrudan 0 offset'le başla
            fs_offset = 0

        # Dosya sistemine bağlan
        self.fs = pytsk3.FS_Info(img_info, offset=fs_offset)

    def list_directory(self, path="/"):
        directory = self.fs.open_dir(path=path)
        entries = []
        deleted = set()
        corrupted = set()

        for entry in directory:
            try:
                name = entry.info.name.name.decode()
                if name in [".", ".."]:
                    continue
                entries.append(name)
                if entry.info.meta is None:
                    corrupted.add(name)
                elif entry.info.meta.flags & pytsk3.TSK_FS_META_FLAG_UNALLOC:
                    deleted.add(name)
            except Exception:
                continue

        return entries, deleted, corrupted
