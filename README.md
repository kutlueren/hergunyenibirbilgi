# Her Gün Yeni Bir Bilgi

Her sabah otomatik olarak dikey (9:16) bir "Top 10" bilgi videosu üretir, onayın için Telegram'a gönderir, **✅ Paylaş**'a basınca Instagram'a Reels olarak yükler.

```
08:00  GitHub Actions ──► konu seç ► Pexels fotoğrafları ► video + Türkçe seslendirme ► Telegram'a gönder
                                                                                    │
                       sen Telegram'da ✅ Paylaş / ❌ Reddet ◄──────────────────────┘
                                                                                    │
her saat (08:25–22:25) ──► butonları oku ► Instagram Reels olarak yayınla ► Telegram'a link
```

- **Video:** Python (Pillow) + ffmpeg, LLM yok. Her gün farklı renk teması (6 tema), bazı sahnelerde gerçek fotoğraf.
- **Ses:** Piper "Fahrettin" Türkçe sesi (CC0 lisans, ticari kullanım serbest), GitHub Actions içinde çalışır.
- **Konular:** `topics/` klasöründeki JSON dosyaları, dosya adı sırasıyla. Yayınlanan/reddedilen konular `state/state.json`'a yazılır ve bir daha gelmez.
- **Onaylanmayan video:** Ertesi sabah süresi dolar, konu sıraya geri döner.

---

## Kurulum (bir kerelik)

Tüm anahtarlar repo'da **Settings → Secrets and variables → Actions → New repository secret** ile eklenir. Koda asla yazılmaz.

### 1. Telegram botu → `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`

1. Telegram'da **@BotFather**'a `/newbot` yaz, bir isim ver. Verdiği token = `TELEGRAM_BOT_TOKEN`.
2. Yeni botuna Telegram'dan herhangi bir mesaj at (örn. "merhaba").
3. Tarayıcıda aç: `https://api.telegram.org/bot<TOKEN>/getUpdates`
   Çıkan JSON'da `"chat":{"id": 123456789 ...}` → bu sayı = `TELEGRAM_CHAT_ID`.

Sadece bu chat ID'den gelen butonlar kabul edilir; botu başkası bulsa bile onaylayamaz.

### 2. Pexels (fotoğraflar) → `PEXELS_API_KEY`  *(isteğe bağlı)*

https://www.pexels.com/api/ → ücretsiz hesap → **Your API Key**. Eklemezsen videolar fotoğrafsız, sadece animasyonlu temalarla üretilir.

### 3. Instagram → `IG_USER_ID`, `IG_ACCESS_TOKEN`

Gerekenler: Instagram **Business veya Creator** hesabı + ona bağlı bir **Facebook Sayfası**.

1. https://developers.facebook.com/apps → **Create app** → kullanım durumu olarak Instagram/içerik yayınlama (**Facebook Login for Business**) seçeneğini seç.
2. **Tools → Graph API Explorer**'ı aç, uygulamanı seç, **User Token** iste ve şu izinleri işaretle:
   `instagram_basic`, `instagram_content_publish`, `pages_show_list`, `pages_read_engagement`, `business_management`
   → **Generate Access Token** (Facebook'ta sayfanı ve Instagram hesabını seçerek onayla).
3. Kısa ömürlü tokenı **uzun ömürlüye** çevir (App ID ve App Secret: App settings → Basic):
   ```
   https://graph.facebook.com/v25.0/oauth/access_token?grant_type=fb_exchange_token&client_id=APP_ID&client_secret=APP_SECRET&fb_exchange_token=KISA_TOKEN
   ```
4. Uzun ömürlü kullanıcı tokenı ile **sayfa tokenını** al (bu token süresiz):
   ```
   https://graph.facebook.com/v25.0/me/accounts?access_token=UZUN_TOKEN
   ```
   Sayfanın `access_token` değeri = **`IG_ACCESS_TOKEN`**, `id` değeri = sayfa ID'si.
5. Instagram hesap ID'si:
   ```
   https://graph.facebook.com/v25.0/SAYFA_ID?fields=instagram_business_account&access_token=IG_ACCESS_TOKEN
   ```
   `instagram_business_account.id` = **`IG_USER_ID`**.

İpucu: Token'ı https://developers.facebook.com/tools/debug/accesstoken/ adresinde kontrol edebilirsin; "Expires: Never" görmelisin.

### 4. İlk deneme

1. **Actions** sekmesi → **Günlük video** → **Run workflow**. ~5 dakika sonra video Telegram'a gelir.
2. Telegram'da **✅ Paylaş**'a bas.
3. Beklemek istemezsen **Actions → Onay kontrolü → Run workflow** (yoksa en geç bir saat içinde kendisi çalışır).

---

## Ayarlar

| Nerede | Ne | Varsayılan |
|---|---|---|
| `.github/workflows/daily.yml` → `cron` | Videonun üretileceği saat (UTC) | `0 7 * * *` = 08:00 kış saati |
| `.github/workflows/approve.yml` → `cron` | Onay kontrol saatleri | her saat 08:25–22:25 |
| Repo **Variables** → `PHOTO_RATIO` | Fotoğraflı sahne oranı (0–1) | `0.5` |
| Repo **Variables** → `GRAPH_API_VERSION` | Instagram API sürümü | `v25.0` |
| `src/themes.py` | Renk temaları | 6 tema, güne göre sırayla |

GitHub Actions dakikası: private repo'da ayda 2.000 dakika ücretsiz; bu kurulum ayda yaklaşık 500–650 dakika kullanır.

---

## Yeni konu ekleme

`topics/` içine sıradaki numarayla bir JSON ekle (örn. `002-turkiyenin-en-yuksek-10-dagi.json`). Format için `topics/001-turkiyenin-en-buyuk-10-golu.json`'a bak:

| Alan | Açıklama |
|---|---|
| `id` | Benzersiz kısa ad |
| `baslik` | Açılıştaki 3 satır: `["TÜRKİYE'NİN", "EN BÜYÜK", "GÖLÜ"]` (ortaya madde sayısı otomatik gelir) |
| `kanca`, `kanca_seslendirme` | İlk 3 saniyedeki merak cümlesi (ekranda 2 satır / seslendirme metni) |
| `birim` | `km²`, `m`, `km`, `milyon` … |
| `gorsel` | `daire` (alan gibi değerler) veya `cubuk` (yükseklik, uzunluk) |
| `maddeler[]` | `sira`, `ad`, `deger`, `yer`, `bilgi` (2 satır), `seslendirme`, `foto` (Pexels arama terimi, İngilizce daha iyi sonuç verir; `null` = fotoğrafsız) |
| `kapanis_vurgu`, `kapanis_seslendirme` | Kapanış: "Sen hangisini **gördün?**" |
| `aciklama`, `etiketler` | Instagram açıklaması ve hashtag'ler |
| `notlar` | Sadece sana Telegram'da gösterilir |

Seslendirmede sayıları yazıyla yaz ("bin altı yüz"), ses motoru rakamları her zaman doğru okumaz.

## Yerelde çalıştırma

```bash
pip install -r requirements.txt   # + ffmpeg
python -m src.render topics/001-turkiyenin-en-buyuk-10-golu.json out/ --preview         # birkaç kare
PIPER_MODEL=.piper/tr_TR-fahrettin-medium.onnx python -m src.render topics/001-....json out/ --theme neon
PIPER_MODEL=... python tests/test_pipeline.py   # Telegram/Pexels/Instagram taklit edilerek uçtan uca test
```

Lisanslar: Inter fontu OFL-1.1 (`fonts/LICENSE-Inter.txt`), Piper Fahrettin sesi CC0, Pexels fotoğrafları Pexels lisansı.
