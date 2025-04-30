# SwiftTrack - Kargo Takip Sistemi

SwiftTrack, modern ve kullanıcı dostu bir kargo takip sistemidir. Bu sistem, kargoların takibi, yönetimi ve raporlanması için kapsamlı bir çözüm sunar.

## Özellikler

- **Kargo Takibi:** Müşteriler kargo takip numarası ile kargolarının durumunu gerçek zamanlı olarak takip edebilir
- **Operasyon Yönetimi:** Operatör ve yöneticiler için gelişmiş kargo yönetim arayüzü
- **Araç ve Şoför Yönetimi:** Filonuzu ve personeli etkin bir şekilde yönetme imkanı
- **Kapsamlı Raporlama:** Grafikler ve detaylı analizler ile iş süreçlerinizi daha iyi anlayın
- **Rol Tabanlı Yetkilendirme:** Müşteri, operatör ve yönetici rolleri için farklı erişim seviyeleri

## Teknik Altyapı

- **Backend:** Django 4.2.9
- **Frontend:** HTML, CSS, JavaScript, Bootstrap
- **Veri Tabanı:** SQLite (Geliştirme), PostgreSQL (Üretim için önerilen)
- **API:** Django REST Framework

## Kurulum

### Gereksinimler

- Python 3.9+
- pip
- virtualenv (önerilen)

### Adımlar

1. Repo'yu klonlayın:
   ```
   git clone https://github.com/kullanici/CargoTracking.git
   cd CargoTracking
   ```

2. Sanal ortam oluşturun ve etkinleştirin:
   ```
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. Bağımlılıkları yükleyin:
   ```
   pip install -r requirements.txt
   ```

4. Veritabanı migrasyonlarını uygulayın:
   ```
   python manage.py migrate
   ```

5. Admin kullanıcısı oluşturun:
   ```
   python manage.py createsuperuser
   ```

6. Geliştirme sunucusunu başlatın:
   ```
   python manage.py runserver
   ```

7. Tarayıcınızda `http://127.0.0.1:8000/` adresine gidin

## Proje Yapısı

- `cargotracking/` - Ana Django projesi ve yapılandırmaları
- `user/` - Kullanıcı yönetimi (müşteri, operatör, admin rolleri)
- `shipment/` - Kargo bilgileri ve işlemleri
- `tracking/` - Kargo durum takibi ve güncelleme
- `vehicle/` - Araç ve sürücü yönetimi

<img width="1710" alt="Ekran Resmi 2025-04-30 16 27 23" src="https://github.com/user-attachments/assets/d7203c65-43ae-49b1-a2f8-a413b5f3b1c4" />



- `report/` - Raporlama ve analiz işlemleri
- `templates/` - HTML şablonları

## Kullanıcı Rolleri

- **Müşteri:** Kargo takibi yapabilir, yeni gönderi oluşturabilir
- **Operatör:** Kargo durumlarını güncelleyebilir, araç ve şoför atayabilir
- **Yönetici:** Tam sistem erişimi, raporlama ve kullanıcı yönetimi yapabilir
