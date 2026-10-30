# Adli İmaj İnceleme Aracı

Disk imajı ve dosya sistemi incelemesi için geliştirilen PyQt5 tabanlı masaüstü araç. Sakarya Uygulamalı Bilimler Üniversitesi Uzaktan Eğitim Uygulama ve Araştırma Merkezi'ndeki staj kapsamında, talep edilen bir ihtiyaç üzerine hazırlandı.

Gereksinimler, mevcut adli bilişim araçları (Autopsy, FTK Imager) incelenerek çıkarıldı.

---

## Durum

Proje iki bileşenden oluşuyor ve bu haliyle **bileşenler henüz birbirine bağlı değil**:

| Bileşen | Durum |
|---|---|
| `arayuz.py` — inceleme arayüzü | Çalışıyor, dosya sistemi üzerinde |
| `image_parser.py` — disk imajı okuyucu | Çalışıyor, bağımsız olarak kullanılabilir |

Arayüz şu an yerel dosya sistemi üzerinde çalışıyor; imaj okuma modülünün arayüze entegrasyonu tamamlanmadı. Planlanan sonraki adım, arayüze "İmaj Aç" akışı eklenerek `DiskImageParser` çıktısının dosya tablosuna bağlanmasıdır.

---

## Arayüz (`arayuz.py`)

Üç panelli bir inceleme penceresi:

- **Sol panel** — dizin ağacı (`QFileSystemModel`)
- **Orta panel** — dosya listesi (isim, tür, boyut, oluşturulma tarihi) ve içerik görüntüleyici
- **Sağ panel** — seçili dosyanın metadata bilgileri

### İçerik görüntüleme

| Dosya türü | Davranış |
|---|---|
| Görsel (png, jpg, jpeg, bmp, gif) | En-boy oranı korunarak önizleme |
| Video (mp4, avi, mkv, mov) | Oynatma kontrolü, konum çubuğu ve süre göstergesi ile oynatıcı |
| Diğer tüm dosyalar | Byte byte hex görünümü |

Araç çubuğundaki **Metin Modu** anahtarı, tüm dosyaları hex yerine düz metin olarak göstermeye geçirir — görsel ve video dosyalarının ham içeriğini incelemek için.

### Metadata paneli

Seçilen her dosya için: isim, tür, boyut, oluşturulma ve değişiklik zamanı, dosya izinleri, sahip UID'si ve **MD5 / SHA1 özet değerleri**.

Hash değerleri adli incelemede dosya bütünlüğünün doğrulanması için kullanılır; aynı dosyanın farklı kopyalarının özdeş olup olmadığı bu değerlerle karşılaştırılır.

---

## İmaj Okuyucu (`image_parser.py`)

`pytsk3` (The Sleuth Kit) ve `pyewf` kütüphaneleri üzerine kurulu disk imajı okuma modülü.

**Desteklenen formatlar:**
- **E01 (EnCase)** — `pyewf` ile açılır; çok parçalı imajlar `pyewf.glob()` ile toplanır. `pytsk3.Img_Info` arayüzünü uygulayan bir sarmalayıcı sınıf (`EWFImgInfo`) üzerinden TSK'ya bağlanır.
- **Ham imaj (dd/raw)** — doğrudan `pytsk3.Img_Info` ile açılır.

**Dosya sistemi tespiti:**

Bölüm tablosu (`Volume_Info`) taranarak NTFS, FAT veya "basic data" bölümü aranır; bulunan bölümün başlangıç sektörü 512 ile çarpılarak offset hesaplanır. Bölüm tablosu okunamayan imajlarda offset 0 kabul edilerek dosya sistemine doğrudan bağlanılır — bölümlenmemiş imajlar için bu gerekli.

**Silinmiş ve bozuk kayıt tespiti:**

`list_directory()` bir dizindeki girdileri dönerken üç küme üretir:

```python
entries, deleted, corrupted = parser.list_directory("/")
```

- `deleted` — `TSK_FS_META_FLAG_UNALLOC` bayrağı taşıyan, yani metadata kaydı hâlâ duran ama alanı serbest bırakılmış (silinmiş) dosyalar
- `corrupted` — metadata kaydına hiç ulaşılamayan bozuk girdiler

---

## Dosya Yapısı

```
├── arayuz.py          # Ana uygulama — üç panelli inceleme penceresi
├── image_parser.py    # E01/ham imaj okuma ve dosya sistemi gezinme
├── dosyalar.py        # Dosya tablosu bileşeni (modüler sürüm)
├── metadata.py        # Metadata paneli bileşeni (modüler sürüm)
├── info.py            # Hex/metin görüntüleyici bileşeni (modüler sürüm)
├── dizin.py           # Dizin ağacı bileşeni (modüler sürüm)
└── requirements.txt
```

`arayuz.py` tek dosyalık çalışan sürümdür ve bileşenleri kendi içinde barındırır. `dosyalar.py`, `metadata.py`, `info.py` ve `dizin.py` aynı işlevlerin modüler hale getirilmiş sürümleridir; entegrasyon adımında arayüzün bunları kullanacak şekilde yeniden düzenlenmesi planlanıyor.

---

## Kurulum ve Çalıştırma

```bash
pip install -r requirements.txt
python arayuz.py
```

`pytsk3` ve `pyewf` derleme gerektirir. Linux üzerinde:

```bash
sudo apt install libtsk-dev libewf-dev python3-dev
```

İmaj okuyucuyu bağımsız kullanmak için:

```python
from image_parser import DiskImageParser

parser = DiskImageParser("delil.E01")
entries, deleted, corrupted = parser.list_directory("/")

print(f"{len(entries)} girdi, {len(deleted)} silinmiş, {len(corrupted)} bozuk")
```

---

## Notlar

Bu araç bir staj projesi olarak geliştirildi; üretim ortamında kullanılmak üzere tasarlanmadı. Gerçek adli inceleme işleri için Autopsy veya benzeri olgunlaşmış araçlar kullanılmalıdır.
