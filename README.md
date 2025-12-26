# Psychonaut Station - Custom Discord RPC Launcher

**Space Station 13 - Psychonaut Station (SS13.tr)** sunucusu için geliştirilmiş, oyun içi durumunuzu Discord profilinizde detaylı ve canlı olarak gösteren özel başlatıcı.

Bu araç, oyunu otomatik olarak başlatır ve Discord Rich Presence (RPC) özelliğini kullanarak anlık bilgileri (Harita, Oyuncu Sayısı, Round ID, İstasyon Adı, Alarm Seviyesi) gösterir.

![Discord RPC Önizleme](a)
//TODO


## 🛠️ Kurulum ve Kullanım

Bu projeyi ister Python dosyası olarak çalıştırabilir, isterseniz de `.exe` formatına çevirip kullanabilirsiniz.

### Gereksinimler
* BYOND (Varsayılan yol: `C:\Program Files (x86)\BYOND`) olmalı!

### 1. Kaynak Koddan Çalıştırma

Gerekli kütüphaneleri yükleyin:

```bash
pip install psutil requests pypresence