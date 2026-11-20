# Her Gün Yeni Bir Bilgi

Her gün öğlen 12:00'de otomatik olarak dikey (9:16) bir "Top 10" bilgi videosu üretir, onayın için Telegram'a gönderir, **✅ Paylaş**'a basınca Instagram'a Reels olarak yükler.

```
12:00  GitHub Actions ──► konu seç ► Pexels fotoğrafları ► video + Türkçe seslendirme ► Telegram'a gönder
                                                                                    │
                       sen Telegram'da ✅ Paylaş / ❌ Reddet ◄──────────────────────┘
                                                                                    │
her saat (12:25–22:25) ──► butonları oku ► Instagram Reels olarak yayınla ► Telegram'a link
```

- **Video:** Python (Pillow) + ffmpeg, LLM yok. Her gün farklı renk teması (6 tema), bazı sahnelerde gerçek fotoğraf.
- **Ses:** Piper "Fahrettin" Türkçe sesi (CC0 lisans, ticari kullanım serbest), GitHub Actions içinde çalışır.
- **Konular:** `topics/` klasöründeki JSON dosyaları, dosya adı sırasıyla. Yayınlanan/reddedilen konular `state/state.json`'a yazılır ve bir daha gelmez.
- **Onaylanmayan video:** Ertesi gün öğlen süresi dolar, konu sıraya geri döner.

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

### 3. Instagram → `IG_USER_ID`, `IG_ACCESS_TOKEN`, `GH_PAT`

Varsayılan yol **Instagram ile giriş** (Facebook sayfası gerekmez). Gereken: Instagram **Business veya Creator** hesabı.

1. https://developers.facebook.com/apps → **Create app** → kullanım durumu: **Manage messaging & content on Instagram**.
2. Uygulama panelinde **Use cases → Manage messaging & content on Instagram → Customize** → Facebook olmayan kurulumu seç (panelde **API setup with Instagram login** veya **Unified login** adıyla geçebilir).
3. **Permissions** bölümünde `instagram_business_basic` ve `instagram_business_content_publish` izinlerinin ekli olduğundan emin ol.
4. **Generate access tokens** bölümünde **Add account** → Instagram hesabınla giriş yap → **Generate token**.
   Çıkan token = **`IG_ACCESS_TOKEN`**. **`IGAA` ile başlamalı** (Instagram token'ı). `EAA` ile başlıyorsa Facebook token'ıdır; o da çalışır ama aşağıdaki Facebook yolunun adımları geçerli olur.
   (60 gün geçerli; haftalık `Instagram token yenileme` workflow'u GH_PAT ile otomatik uzatır).
5. Hesap ID'si (aynı ekranda görünmüyorsa) tarayıcıda:
   ```
   https://graph.instagram.com/v25.0/me?fields=user_id,username&access_token=IG_ACCESS_TOKEN
   ```
   `user_id` = **`IG_USER_ID`**.
6. **`GH_PAT`** (token'ın kendiliğinden yenilenmesi için): GitHub → Settings → Developer settings → **Fine-grained tokens** → Generate new token → *Repository access: Only select repositories → hergunyenibirbilgi* → *Permissions: Repository → **Secrets: Read and write***. Çıkan token'ı `GH_PAT` secret'ı olarak ekle.

**Repo public olmalı.** Instagram ile giriş yolunda Instagram videoyu bir linkten çekmek isteyebiliyor. Bu durumda video yayın sırasında birkaç dakikalığına `media` branch'ine konur (`raw.githubusercontent.com` linki), Instagram aldıktan sonra silinir. Private repo'da bu link açılmaz.
Repo → Settings → General → en altta **Change repository visibility → Public**. Secret'lar public repo'da da gizli kalır; ayrıca GitHub Actions dakikaları public repo'da sınırsızdır.

<details>
<summary>Alternatif: Facebook ile giriş (Facebook sayfası gerekir, token süresiz, repo private kalabilir)</summary>

Token `EAA` ile başladığı için `IG_LOGIN` ayarlamana gerek yok. Graph API Explorer'da `instagram_basic`, `instagram_content_publish`, `pages_show_list`, `pages_read_engagement`, `business_management` izinleriyle kullanıcı token'ı üret, [Access Token Debugger](https://developers.facebook.com/tools/debug/accesstoken/)'da **Extend Access Token** ile uzat, sonra Explorer'da:

```
me/accounts?fields=name,access_token,instagram_business_account
```

Sayfanın `access_token` = `IG_ACCESS_TOKEN`, `instagram_business_account.id` = `IG_USER_ID`. Bu yolda video doğrudan yüklenir, `GH_PAT` gerekmez.
</details>

### 4. İlk deneme

1. **Actions** sekmesi → **Günlük video** → **Run workflow**. ~5 dakika sonra video Telegram'a gelir.
2. Telegram'da **✅ Paylaş**'a bas.
3. Beklemek istemezsen **Actions → Onay kontrolü → Run workflow** (yoksa en geç bir saat içinde kendisi çalışır).

---

## Ayarlar

| Nerede | Ne | Varsayılan |
|---|---|---|
| `src/daily.py` → `SEND_WINDOW` + `daily.yml` → `cron` | Videonun Telegram'a geleceği saat. Cron UTC'dir; yaz/kış saati için iki tetikleyici var, script Berlin saatine göre birini seçer | ~12:00 (Berlin) |
| `.github/workflows/approve.yml` → `cron` | Onay kontrol saatleri | her saat 12:25–22:25 |
| Repo **Variables** → `PHOTO_RATIO` | Fotoğraflı sahne oranı (0–1) | `0.5` |
| Repo **Variables** → `GRAPH_API_VERSION` | Instagram API sürümü | `v25.0` |
| Repo **Variables** → `IG_LOGIN` | `instagram` veya `facebook` | boş: token `IGAA…` ile başlıyorsa instagram, `EAA…` ise facebook |
| Repo **Variables** → `IG_UPLOAD_MODE` | `auto`: önce doğrudan yükleme, olmazsa geçici link · `url` · `resumable` | `auto` |
| `src/themes.py` | Renk temaları | 6 tema, güne göre sırayla |

GitHub Actions dakikası: public repo'da sınırsız; private repo'da (Facebook ile giriş yolu) ayda 2.000 dakika ücretsiz, bu kurulum ayda yaklaşık 500–650 dakika kullanır.

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
