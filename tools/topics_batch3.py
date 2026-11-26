"""Topic bank batch 3 (018-042). Run from inside tools/: python3 topics_batch3.py"""
import json, os
from topicgen import topic, ROOT

DEF = "Sen hangisini biliyordun?"


def T(fname, *a, ekstra=None, **kw):
    topic(fname, *a, **kw)
    if ekstra:
        p = os.path.join(ROOT, "topics", fname)
        t = json.load(open(p, encoding="utf-8"))
        t.update(ekstra)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(t, f, ensure_ascii=False, indent=1); f.write("\n")


def look(renk, doku, **k):
    return dict(renk=renk, doku=doku, **k)


# 018 ---------------------------------------------------------------------------------
T("018-gunes-sisteminin-en-buyuk-5-uydusu.json", "gunes-sisteminin-en-buyuk-5-uydusu",
  ["GÜNEŞ SİSTEMİ'NİN", "EN BÜYÜK", "UYDUSU"],
  ["1 numara, Merkür", "gezegeninden bile BÜYÜK!"],
  "Güneş Sistemi'nin en büyük beş uydusu! Bir numara, Merkür gezegeninden bile büyük.",
  "km", "gezegen", [
      ("Ay", 3475, "Dünya", ["Her yıl Dünya'dan", "yaklaşık 3,8 cm uzaklaşıyor"],
       "Ay. Her yıl Dünya'dan yaklaşık üç virgül sekiz santim uzaklaşıyor.", "Moon", look([175, 172, 165], "krater")),
      ("İo", 3643, "Jüpiter", ["Güneş Sistemi'nde en çok", "yanardağı olan gök cismi"],
       "İo. Güneş Sistemi'nde en çok yanardağı olan gök cismi.", "Io moon", look([222, 196, 92], "krater")),
      ("Kallisto", 4821, "Jüpiter", ["Güneş Sistemi'nde en çok", "krater kaplı yüzeylerden biri"],
       "Kallisto. Güneş Sistemi'nde en çok kraterle kaplı yüzeylerden biri.", "Callisto", look([105, 96, 86], "krater")),
      ("Titan", 5150, "Satürn", ["Kalın atmosferi olan", "tek uydu"],
       "Titan. Kalın bir atmosferi olan tek uydu. Yüzeyinde metan gölleri var.", "Titan moon", look([214, 158, 68], "bulut")),
      ("Ganymede", 5268, "Jüpiter", ["Kendi manyetik alanı", "olan tek uydu"],
       "Ganimed! Güneş Sistemi'nin en büyük uydusu, ve kendi manyetik alanı olan tek uydu.", "Ganymede", look([150, 138, 122], "krater")),
  ],
  "Güneş Sistemi'nin en büyük 5 uydusu 🌕 1 numara Merkür'den bile büyük! Sence hangisi? Tahminini yorumlara yaz 👇",
  ["#uzay", "#uydu", "#güneşsistemi", "#astronomi", "#bilgi", "#reels", "#keşfet"],
  kapanis_ust="Sen hangisini", kapanis_vurgu="biliyordun?",
  notlar="Ortalama çaplar (NASA). Karşılaştırma için Dünya çizilir.")

# 019 ---------------------------------------------------------------------------------
T("019-dunyanin-en-yuksek-5-tv-kulesi.json", "dunyanin-en-yuksek-5-tv-kulesi",
  ["DÜNYANIN", "EN YÜKSEK", "TV KULESİ"],
  ["1 numara, Eyfel Kulesi'nin", "neredeyse 2 KATI!"],
  "Dünyanın en yüksek beş televizyon kulesi! Bir numara, Eyfel Kulesi'nin neredeyse iki katı.",
  "m", "bina", [
      ("Oriental Pearl Kulesi", 468, "Şanghay, Çin", ["İçinde küreler var:", "en üstteki bir gözlem salonu"],
       "Oriental Pörl Kulesi, Şanghay. Gövdesindeki kürelerin en üstü bir gözlem salonu.", "Oriental Pearl Tower"),
      ("Ostankino Kulesi", 540, "Moskova, Rusya", ["Avrupa'nın en yüksek", "serbest duran yapısı"],
       "Ostankino Kulesi, Moskova. Avrupa'nın en yüksek serbest duran yapısı.", "Ostankino Tower"),
      ("CN Tower", 553, "Toronto, Kanada", ["32 yıl boyunca dünyanın", "en yüksek serbest yapısıydı"],
       "Si En Tavır, Toronto. Otuz iki yıl boyunca dünyanın en yüksek serbest duran yapısıydı.", "CN Tower"),
      ("Canton Kulesi", 604, "Guançu, Çin", ["Tepesinde dönen", "dev kabinler var"],
       "Kanton Kulesi, Guançu. Tepesinde dönen dev kabinler var.", "Canton Tower"),
      ("Tokyo Skytree", 634, "Tokyo, Japonya", ["Dünyanın en yüksek kulesi;", "634 sayısı 'Musaşi' okunur"],
       "Tokyo Skaytri! Dünyanın en yüksek kulesi. Altı yüz otuz dört sayısı Japoncada Musaşi diye okunuyor, bölgenin eski adı.", "Tokyo Skytree"),
  ],
  "Dünyanın en yüksek 5 TV kulesi 🗼 1 numara Eyfel'in neredeyse 2 katı! Sence hangisi? 👇",
  ["#kule", "#mimari", "#dünya", "#mühendislik", "#bilgi", "#reels", "#keşfet"],
  kapanis_ust="Sen hangisine", kapanis_vurgu="çıkmak isterdin?",
  notlar="Toplam yükseklik (anten dahil). Burj Khalifa bina olduğu için listede yok.")

# 020 ---------------------------------------------------------------------------------
T("020-dunyanin-en-buyuk-5-hidroelektrik-santrali.json", "dunyanin-en-buyuk-5-hidroelektrik-santrali",
  ["DÜNYANIN", "EN BÜYÜK", "BARAJ SANTRALİ"],
  ["1 numara, Dünya'nın", "dönüşünü bile YAVAŞLATTI!"],
  "Dünyanın en büyük beş hidroelektrik santrali! Bir numaranın barajı, Dünya'nın dönüşünü bile yavaşlattı.",
  "GW", "cubuk", [
      ("Belo Monte", 11.2, "Brezilya", ["Amazon'un kolu Xingu", "Nehri üzerinde"],
       "Belo Monte, Brezilya. Amazonun kollarından Şingu Nehri üzerinde.", "Belo Monte Dam"),
      ("Xiluodu", 13.9, "Çin", ["Yangtze'nin yukarı kolu", "Jinsha Nehri'nde"],
       "Şiluodu, Çin. Yangçe'nin yukarı kolu Cinşa Nehri üzerinde.", "Xiluodu Dam"),
      ("Itaipu", 14.0, "Brezilya – Paraguay", ["Paraguay elektriğinin", "neredeyse tamamını sağlıyor"],
       "İtaypu, Brezilya ve Paraguay. Paraguay'ın elektriğinin neredeyse tamamını sağlıyor.", "Itaipu Dam"),
      ("Baihetan", 16.0, "Çin", ["Dünyanın en güçlü", "türbinleri burada: 1 GW"],
       "Bayhetan, Çin. Dünyanın en güçlü türbinleri burada, her biri bir gigavat.", "Baihetan Dam"),
      ("Üç Boğaz Barajı", 22.5, "Çin", ["Dünyanın en büyük", "elektrik santrali"],
       "Üç Boğaz Barajı! Dünyanın en büyük elektrik santrali. Biriktirdiği su, günü mikrosaniyenin küçük bir kesri kadar uzattı.", "Three Gorges Dam"),
  ],
  "Dünyanın en büyük 5 hidroelektrik santrali ⚡ 1 numaranın barajı Dünya'nın dönüşünü bile yavaşlattı! Sence hangisi? 👇",
  ["#enerji", "#baraj", "#mühendislik", "#elektrik", "#bilgi", "#reels", "#keşfet"],
  kapanis_ust="Sen hangisini", kapanis_vurgu="biliyordun?",
  notlar="Kurulu güç (GW). Yavaşlama etkisi NASA hesabı: günü yaklaşık 0,06 mikrosaniye uzatır.")

# 021 ---------------------------------------------------------------------------------
T("021-turkiyenin-en-yuksek-5-dagi.json", "turkiyenin-en-yuksek-5-dagi",
  ["TÜRKİYE'NİN", "EN YÜKSEK", "DAĞI"],
  ["1 numara, 5.000 metreyi", "aşan TEK dağımız!"],
  "Türkiye'nin en yüksek beş dağı! Bir numara, beş bin metreyi aşan tek dağımız.",
  "m", "dag", [
      ("Erciyes", 3917, "Kayseri", ["Orta Anadolu'nun", "en yüksek zirvesi"],
       "Erciyes, Kayseri. Orta Anadolunun en yüksek zirvesi, aynı zamanda bir kayak merkezi.", "Mount Erciyes"),
      ("Kaçkar", 3937, "Rize", ["Karadeniz'in en yüksek", "dağı; buzul gölleri var"],
       "Kaçkar, Rize. Karadeniz'in en yüksek dağı. Zirvesinin çevresinde buzul gölleri var.", "Kackar Mountains"),
      ("Süphan", 4058, "Bitlis", ["Sönmüş bir volkan;", "Van Gölü'ne bakıyor"],
       "Süphan, Bitlis. Van Gölüne bakan, sönmüş bir volkan.", "Mount Suphan"),
      ("Uludoruk", 4135, "Hakkâri", ["Cilo Dağları'nın zirvesi;", "Türkiye'nin buzul yurdu"],
       "Uludoruk, Hakkâri. Cilo Dağlarının zirvesi. Türkiye'nin en büyük buzulları burada.", "Cilo Mountains"),
      ("Ağrı Dağı", 5137, "Ağrı – Iğdır", ["Zirvesi yaz kış", "buzul ile kaplı"],
       "Ağrı Dağı! Türkiye'nin çatısı. Zirvesi yaz kış buzul ile kaplı.", "Mount Ararat"),
  ],
  "Türkiye'nin en yüksek 5 dağı 🏔️ 1 numara 5.000 metreyi aşan tek dağımız! Sence hangisi? 👇",
  ["#türkiye", "#dağ", "#doğa", "#coğrafya", "#bilgi", "#reels", "#keşfet"],
  kapanis_ust="Sen hangisine", kapanis_vurgu="tırmanmak isterdin?",
  notlar="Yükseklikler kaynaklara göre birkaç metre değişebilir (ör. Uludoruk 4.116–4.135 m).")

# 022 ---------------------------------------------------------------------------------
T("022-dunyanin-en-kalabalik-10-sehri.json", "dunyanin-en-kalabalik-10-sehri",
  ["DÜNYANIN", "EN KALABALIK", "ŞEHRİ"],
  ["Listede sadece 1 şehir", "ASYA DIŞINDAN!"],
  "Dünyanın en kalabalık on şehri! Listede Asya dışından sadece bir şehir var.",
  "milyon", "ikon", [
      ("Seul", 22.5, "Güney Kore", ["Ülke nüfusunun yarısı", "bu bölgede yaşıyor"],
       "Seul, Güney Kore. Ülkenin neredeyse yarısı bu bölgede yaşıyor.", "Seoul"),
      ("Kalküta", 22.5, "Hindistan", ["Hindistan'ın eski", "başkenti"],
       "Kalküta, Hindistan. Ülkenin eski başkenti.", "Kolkata"),
      ("Manila", 24.7, "Filipinler", ["Dünyanın en yoğun", "nüfuslu şehirlerinden"],
       "Manila, Filipinler. Dünyanın en yoğun nüfuslu şehirlerinden biri.", "Manila"),
      ("Kahire", 25.6, "Mısır", ["Listedeki tek", "Asya dışı şehir"],
       "Kahire, Mısır. Listedeki tek Asya dışı şehir.", "Cairo"),
      ("Guangzhou", 27.6, "Çin", ["2.000 yılı aşkın", "bir liman şehri"],
       "Guançu, Çin. İki bin yılı aşkın bir liman şehri.", "Guangzhou"),
      ("Şanghay", 29.6, "Çin", ["Dünyanın en işlek", "konteyner limanı"],
       "Şanghay, Çin. Dünyanın en işlek konteyner limanı.", "Shanghai"),
      ("Yeni Delhi", 30.2, "Hindistan", ["Hindistan'ın başkenti", "hızla büyümeye devam ediyor"],
       "Yeni Delhi, Hindistan. Başkent hızla büyümeye devam ediyor.", "New Delhi"),
      ("Tokyo", 33.4, "Japonya", ["Onlarca yıl 1 numaraydı,", "şimdi 3. sırada"],
       "Tokyo, Japonya. Onlarca yıl bir numaraydı, şimdi üçüncü sırada.", "Tokyo"),
      ("Dakka", 36.6, "Bangladeş", ["2050'de 1 numara", "olması bekleniyor"],
       "Dakka, Bangladeş. İki bin elli yılında bir numara olması bekleniyor.", "Dhaka"),
      ("Cakarta", 41.9, "Endonezya", ["7 yılda 33. sıradan", "zirveye çıktı"],
       "Cakarta! Dünyanın en kalabalık şehri. Yeni BM hesaplamasıyla otuz üçüncü sıradan zirveye çıktı.", "Jakarta"),
  ],
  "Dünyanın en kalabalık 10 şehri 🌆 Listede Asya dışından sadece 1 şehir var! Sence 1 numara hangisi? 👇",
  ["#şehir", "#nüfus", "#dünya", "#coğrafya", "#bilgi", "#reels", "#keşfet"],
  kapanis_ust="Sen hangisinde", kapanis_vurgu="yaşamak isterdin?",
  notlar="BM World Urbanization Prospects 2025 (yeni 'Degree of Urbanisation' yöntemi, kentsel alan nüfusu).",
  ekstra={"ikon": "insan", "ikon_deger": 2, "ikon_etiket": "2 milyon kişi"})

# 023 ---------------------------------------------------------------------------------
T("023-avrupanin-en-buyuk-5-golu.json", "avrupanin-en-buyuk-5-golu",
  ["AVRUPA'NIN", "EN BÜYÜK", "GÖLÜ"],
  ["1 numara, 2. sıradakinin", "neredeyse 2 KATI!"],
  "Avrupa'nın en büyük beş gölü! Bir numara, ikinci sıradakinin neredeyse iki katı.",
  "km²", "sekil", [
      ("Peipus Gölü", 3555, "Estonya – Rusya", ["Avrupa'nın sınır ötesi", "en büyük gölü"],
       "Peypus Gölü, Estonya ve Rusya. Avrupa'nın en büyük sınır ötesi gölü.", "Lake Peipus"),
      ("Saimaa Gölü", 4377, "Finlandiya", ["Nadir Saimaa foku", "sadece burada yaşıyor"],
       "Saymaa Gölü, Finlandiya. Nadir Saymaa foku sadece burada yaşıyor.", "Lake Saimaa"),
      ("Vänern Gölü", 5655, "İsveç", ["Avrupa Birliği'nin", "en büyük gölü"],
       "Venern Gölü, İsveç. Avrupa Birliği'nin en büyük gölü.", "Lake Vanern"),
      ("Onega Gölü", 9700, "Rusya", ["Ahşap kiliseleriyle", "ünlü Kiji Adası burada"],
       "Onega Gölü, Rusya. Ahşap kiliseleriyle ünlü Kiji Adası burada.", "Lake Onega"),
      ("Ladoga Gölü", 17700, "Rusya", ["Kuşatmada Leningrad'a", "uzanan 'Hayat Yolu'"],
       "Ladoga Gölü! Avrupa'nın en büyük gölü. Kuşatma sırasında buzunun üstünden Hayat Yolu geçti.", "Lake Ladoga"),
  ],
  "Avrupa'nın en büyük 5 gölü 💧 1 numara, 2. sıradakinin neredeyse 2 katı! Sence hangisi? 👇",
  ["#avrupa", "#göl", "#doğa", "#coğrafya", "#bilgi", "#reels", "#keşfet"],
  kapanis_ust="Sen hangisini", kapanis_vurgu="gördün?",
  notlar="Doğal göller; Hazar Denizi ve baraj gölleri hariç (Wikipedia / EEA).",
  ekstra={"stil": "su"})

# 024 ---------------------------------------------------------------------------------
T("024-gezegenlerin-uydu-sayisi.json", "gezegenlerin-uydu-sayisi",
  ["EN ÇOK UYDUSU", "OLAN", "GEZEGEN"],
  ["1 numaranın uydu sayısı", "diğerlerinin TOPLAMINDAN fazla!"],
  "En çok uydusu olan beş gezegen! Bir numaranın uydu sayısı, diğer tüm gezegenlerin toplamından fazla.",
  "uydu", "cubuk", [
      ("Mars", 2, "Kızıl gezegen", ["Uyduları Phobos ve", "Deimos: Korku ve Dehşet"],
       "Mars. İki uydusunun adı Fobos ve Deimos, yani korku ve dehşet.", "Mars"),
      ("Neptün", 16, "Buz devi", ["En büyük uydusu Triton", "ters yönde dönüyor"],
       "Neptün. En büyük uydusu Triton, gezegenin etrafında ters yönde dönüyor.", "Neptune"),
      ("Uranüs", 29, "Buz devi", ["Uydularına Shakespeare", "karakterlerinin adı verildi"],
       "Uranüs. Uydularına Şekspir karakterlerinin adları verildi.", "Uranus"),
      ("Jüpiter", 115, "Gaz devi", ["En büyük uydu da", "bu gezegende"],
       "Jüpiter. Güneş Sistemi'nin en büyük uydusu da bu gezegende.", "Jupiter"),
      ("Satürn", 292, "Gaz devi", ["Uydularının çoğu sadece", "birkaç kilometre boyunda"],
       "Satürn! Uydu kralı. Uydularının çoğu sadece birkaç kilometre boyunda.", "Saturn"),
  ],
  "En çok uydusu olan 5 gezegen 🪐 1 numaranın uydu sayısı diğerlerinin toplamından fazla! Sence hangisi? 👇",
  ["#uzay", "#gezegen", "#astronomi", "#güneşsistemi", "#bilgi", "#reels", "#keşfet"],
  kapanis_ust="Sen bunu", kapanis_vurgu="biliyor muydun?",
  notlar="Yörüngesi duyurulmuş uydular, 2026 ortası (Minor Planet Center / Wikipedia). Sayılar yeni keşiflerle artabiliyor; yayından önce kontrol et.")

# 025 ---------------------------------------------------------------------------------
T("025-dunyanin-en-derin-5-golu.json", "dunyanin-en-derin-5-golu",
  ["DÜNYANIN", "EN DERİN", "GÖLÜ"],
  ["1 numara, dünyadaki tatlı", "suyun 5'te BİRİNİ tutuyor!"],
  "Dünyanın en derin beş gölü! Bir numara, dünyadaki donmamış tatlı suyun beşte birini tutuyor.",
  "m", "cubuk", [
      ("Malavi Gölü", 706, "Malavi – Mozambik – Tanzanya", ["Dünyada en çok balık", "türü yaşayan göl"],
       "Malavi Gölü. Dünyada en çok balık türünün yaşadığı göl.", "Lake Malawi"),
      ("O'Higgins / San Martín", 836, "Şili – Arjantin", ["Amerika kıtasının", "en derin gölü"],
       "O Higgins, San Martin Gölü, Şili ve Arjantin. Amerika kıtasının en derin gölü.", "OHiggins Lake"),
      ("Hazar Denizi", 1025, "Asya – Avrupa", ["Adı deniz ama dünyanın", "en büyük gölü"],
       "Hazar Denizi. Adı deniz ama aslında dünyanın en büyük gölü.", "Caspian Sea"),
      ("Tanganika Gölü", 1470, "Doğu Afrika", ["Dünyanın en uzun", "tatlı su gölü: 673 km"],
       "Tanganika Gölü, Doğu Afrika. Dünyanın en uzun tatlı su gölü.", "Lake Tanganyika"),
      ("Baykal Gölü", 1642, "Rusya", ["25 milyon yaşında;", "dünyanın en eski gölü"],
       "Baykal Gölü! Dünyanın en derin ve en eski gölü, yaklaşık yirmi beş milyon yaşında.", "Lake Baikal"),
  ],
  "Dünyanın en derin 5 gölü 🌊 1 numara dünyadaki tatlı suyun 5'te 1'ini tutuyor! Sence hangisi? 👇",
  ["#göl", "#doğa", "#dünya", "#coğrafya", "#bilgi", "#reels", "#keşfet"],
  kapanis_ust="Sen hangisini", kapanis_vurgu="biliyordun?",
  notlar="En büyük derinlik. Buzul altındaki Vostok Gölü hariç.")

# 026 ---------------------------------------------------------------------------------
T("026-afrikanin-en-yuksek-5-dagi.json", "afrikanin-en-yuksek-5-dagi",
  ["AFRİKA'NIN", "EN YÜKSEK", "DAĞI"],
  ["1 numara, dünyanın tek başına", "duran EN YÜKSEK dağı!"],
  "Afrika'nın en yüksek beş dağı! Bir numara, dünyanın tek başına duran en yüksek dağı.",
  "m", "dag", [
      ("Baker Dağı", 4844, "Uganda", ["Rwenzori'de: 'Ay Dağları'", "olarak bilinen sıra"],
       "Beyker Dağı, Uganda. Ay Dağları diye bilinen Ruvenzori sırasında.", "Mount Baker Rwenzori"),
      ("Speke Dağı", 4890, "Uganda", ["Adını Nil'in kaynağını", "arayan kaşiften alıyor"],
       "Spik Dağı, Uganda. Adını Nilin kaynağını arayan kaşiften alıyor.", "Mount Speke"),
      ("Stanley Dağı", 5109, "Uganda – KDC", ["Ekvator'un hemen yanında", "ama buzulları var"],
       "Stenli Dağı, Uganda ve Kongo. Ekvatorun hemen yanında ama buzulları var.", "Mount Stanley"),
      ("Kenya Dağı", 5199, "Kenya", ["Ülkeye adını", "veren dağ"],
       "Kenya Dağı. Ülkeye adını veren dağ.", "Mount Kenya"),
      ("Kilimanjaro", 5895, "Tanzanya", ["Zirvesine teknik", "tırmanış gerekmeden çıkılır"],
       "Kilimanjaro! Afrika'nın çatısı. Zirvesine teknik tırmanış bilgisi olmadan çıkılabiliyor.", "Kilimanjaro"),
  ],
  "Afrika'nın en yüksek 5 dağı 🏔️ 1 numara dünyanın tek başına duran en yüksek dağı! Sence hangisi? 👇",
  ["#afrika", "#dağ", "#doğa", "#coğrafya", "#bilgi", "#reels", "#keşfet"],
  kapanis_ust="Sen hangisine", kapanis_vurgu="tırmanmak isterdin?",
  notlar="Ayrı dağlar (aynı dağın alt zirveleri sayılmadı).")

# 027 ---------------------------------------------------------------------------------
T("027-dunyanin-en-kalabalik-8-ulkesi.json", "dunyanin-en-kalabalik-8-ulkesi",
  ["DÜNYANIN", "EN KALABALIK", "ÜLKESİ"],
  ["Dünyadaki her 6 kişiden", "biri 1 NUMARADA yaşıyor!"],
  "Dünyanın en kalabalık sekiz ülkesi! Dünyadaki her altı kişiden biri, bir numarada yaşıyor.",
  "milyon", "ikon", [
      ("Bangladeş", 177.8, "Asya", ["Dünyanın en yoğun nüfuslu", "büyük ülkesi"],
       "Bangladeş. Dünyanın en yoğun nüfuslu büyük ülkesi.", "Bangladesh"),
      ("Brezilya", 213.6, "Güney Amerika", ["Güney Amerika'nın", "en kalabalık ülkesi"],
       "Brezilya. Güney Amerika'nın en kalabalık ülkesi.", "Brazil"),
      ("Nijerya", 242.4, "Afrika", ["Afrika'nın en", "kalabalık ülkesi"],
       "Nijerya. Afrika'nın en kalabalık ülkesi, ve en hızlı büyüyenlerden.", "Nigeria"),
      ("Pakistan", 259.3, "Asya", ["Nüfusu her yıl", "yüzde 1,6 artıyor"],
       "Pakistan. Nüfusu her yıl yüzde bir virgül altı artıyor.", "Pakistan"),
      ("Endonezya", 287.9, "Asya", ["17.000'den fazla", "adadan oluşuyor"],
       "Endonezya. On yedi binden fazla adadan oluşuyor.", "Indonesia"),
      ("ABD", 349.0, "Kuzey Amerika", ["Asya dışındaki", "en kalabalık ülke"],
       "Amerika Birleşik Devletleri. Asya dışındaki en kalabalık ülke.", "United States"),
      ("Çin", 1412.9, "Asya", ["Nüfusu artık", "azalmaya başladı"],
       "Çin. Nüfusu artık azalmaya başladı.", "China"),
      ("Hindistan", 1476.6, "Asya", ["2023'te zirveye çıktı;", "her 6 kişiden 1'i burada"],
       "Hindistan! İki bin yirmi üçte zirveye çıktı. Dünyadaki her altı kişiden biri burada yaşıyor.", "India"),
  ],
  "Dünyanın en kalabalık 8 ülkesi 🌍 Her 6 kişiden 1'i 1 numarada yaşıyor! Sence hangisi? 👇",
  ["#nüfus", "#ülke", "#dünya", "#coğrafya", "#bilgi", "#reels", "#keşfet"],
  kapanis_ust="Sen bunu", kapanis_vurgu="biliyor muydun?",
  notlar="BM World Population Prospects 2024, 2026 tahmini (Worldometer).",
  ekstra={"ikon": "insan", "ikon_deger": 100, "ikon_etiket": "100 milyon kişi"})

# 028 ---------------------------------------------------------------------------------
T("028-dunyanin-en-uzun-5-asma-koprusu.json", "dunyanin-en-uzun-5-asma-koprusu",
  ["DÜNYANIN", "EN UZUN", "ASMA KÖPRÜSÜ"],
  ["1 numaranın orta açıklığı", "2 KİLOMETREYİ aşıyor!"],
  "Dünyanın en uzun açıklıklı beş asma köprüsü! Bir numaranın orta açıklığı iki kilometreyi aşıyor.",
  "m", "cubuk", [
      ("Nansha Köprüsü", 1688, "Guangdong, Çin", ["Günde 100.000'den", "fazla araç geçiyor"],
       "Nanşa Köprüsü, Çin. Günde yüz binden fazla araç geçiyor.", "Nansha Bridge"),
      ("Yangsigang Köprüsü", 1700, "Vuhan, Çin", ["Dünyanın en uzun", "çift katlı asma köprüsü"],
       "Yangsıgang Köprüsü, Vuhan. Dünyanın en uzun açıklıklı çift katlı asma köprüsü.", "Yangsigang Yangtze River Bridge"),
      ("Nanjing Xianxin Köprüsü", 1760, "Nanjing, Çin", ["2025'te açıldı;", "Yangtze'yi tek açıklıkla geçer"],
       "Nancing Şyanşin Köprüsü. İki bin yirmi beşte açıldı, Yangçe'yi tek açıklıkla geçiyor.", "Nanjing Xianxin Bridge"),
      ("Akashi Kaikyō", 1991, "Japonya", ["24 yıl boyunca", "dünya rekoru onda kaldı"],
       "Akaşi Kaykyo Köprüsü, Japonya. Yirmi dört yıl boyunca dünya rekoru ondaydı.", "Akashi Kaikyo Bridge"),
      ("1915 Çanakkale Köprüsü", 2023, "Çanakkale, Türkiye", ["Açıklığı 2023 m:", "Cumhuriyet'in 100. yılı"],
       "Bin dokuz yüz on beş Çanakkale Köprüsü! İki bin yirmi üç metrelik açıklığı, Cumhuriyetin yüzüncü yılına bir selam.", "1915 Canakkale Bridge"),
  ],
  "Dünyanın en uzun 5 asma köprüsü 🌉 1 numaranın orta açıklığı 2 km'yi aşıyor! Sence hangisi? 👇",
  ["#köprü", "#mühendislik", "#mimari", "#dünya", "#bilgi", "#reels", "#keşfet"],
  kapanis_ust="Sen hangisinden", kapanis_vurgu="geçtin?",
  notlar="Orta açıklığa göre (Wikipedia). DİKKAT: Çin'deki Yanji Köprüsü (1.860 m) 2026 sonunda açılırsa 3. sıraya girer; yayından önce kontrol et.")

# 029 ---------------------------------------------------------------------------------
T("029-en-buyuk-5-cuce-gezegen.json", "en-buyuk-5-cuce-gezegen",
  ["GÜNEŞ SİSTEMİ'NİN", "EN BÜYÜK", "CÜCE GEZEGENİ"],
  ["1 numara 76 yıl boyunca", "GEZEGEN sayıldı!"],
  "Güneş Sistemi'nin en büyük beş cüce gezegeni! Bir numara, yetmiş altı yıl boyunca gezegen sayıldı.",
  "km", "gezegen", [
      ("Gonggong", 1230, "Kuiper Kuşağı ötesi", ["Adını Çin mitolojisindeki", "su tanrısından alıyor"],
       "Gonggong. Adını Çin mitolojisindeki su tanrısından alıyor.", None, look([175, 95, 80], "duz")),
      ("Makemake", 1430, "Kuiper Kuşağı", ["Paskalya Adası'nın", "yaratıcı tanrısı"],
       "Makemake. Adı Paskalya Adası halkının yaratıcı tanrısı.", None, look([196, 128, 92], "duz")),
      ("Haumea", 1560, "Kuiper Kuşağı", ["Çok hızlı döndüğü için", "yumurta şeklinde"],
       "Haumea. Dört saatte bir döndüğü için yumurta şeklinde.", None, look([228, 228, 232], "duz")),
      ("Eris", 2326, "Dağınık disk", ["Keşfi, 9. gezegenin", "sonunu getirdi"],
       "Eris. Onun keşfi, dokuzuncu gezegen tartışmasını başlattı.", None, look([214, 214, 220], "krater")),
      ("Plüton", 2377, "Kuiper Kuşağı", ["1930–2006 arası", "9. gezegendi"],
       "Plüton! Bin dokuz yüz otuzdan iki bin altıya kadar dokuzuncu gezegendi. Yüzeyinde dev bir kalp şekli var.", None, look([206, 176, 146], "krater")),
  ],
  "Güneş Sistemi'nin en büyük 5 cüce gezegeni 🌑 1 numara 76 yıl boyunca gezegen sayıldı! Sence hangisi? 👇",
  ["#uzay", "#astronomi", "#güneşsistemi", "#gezegen", "#bilgi", "#reels", "#keşfet"],
  kapanis_ust="Sen bunu", kapanis_vurgu="biliyor muydun?",
  notlar="Ortalama çaplar (NASA/Wikipedia). Haumea uzun şekilli olduğundan ortalama değer verildi. Gonggong IAU tarafından resmi cüce gezegen olarak onaylanmadı ama yaygın kabul görüyor.")

# 030 ---------------------------------------------------------------------------------
T("030-en-cok-altin-rezervi-olan-10-ulke.json", "en-cok-altin-rezervi-olan-10-ulke",
  ["EN ÇOK", "ALTIN REZERVİ", "OLAN ÜLKE"],
  ["1 numaranın altını,", "2. sıradakinin 2 KATINDAN fazla!"],
  "En çok altın rezervi olan on ülke! Bir numaranın altını, ikinci sıradakinin iki katından fazla.",
  "ton", "cubuk", [
      ("Polonya", 648, "Avrupa", ["Son yılların en çok", "altın alan merkez bankası"],
       "Polonya. Son yılların en çok altın alan merkez bankalarından.", "Poland"),
      ("Japonya", 846, "Asya", ["Rezervlerinin sadece", "küçük bir kısmı altın"],
       "Japonya. Rezervlerinin sadece küçük bir kısmı altın.", "Japan"),
      ("Hindistan", 881, "Asya", ["Halkın elindeki altın", "bundan kat kat fazla"],
       "Hindistan. Halkın elindeki altın bunun kat kat fazlası.", "India"),
      ("İsviçre", 1040, "Avrupa", ["Kişi başına en çok altını", "olan ülkelerden"],
       "İsviçre. Kişi başına en çok altını olan ülkelerden.", "Switzerland"),
      ("Rusya", 2271, "Avrupa – Asya", ["Son 20 yılda", "rezervini kat kat büyüttü"],
       "Rusya. Son yirmi yılda altın rezervini katlayarak büyüttü.", "Russia"),
      ("Çin", 2387, "Asya", ["Aylardır aralıksız", "altın alıyor"],
       "Çin. Merkez bankası aylardır aralıksız altın alıyor.", "China"),
      ("Fransa", 2437, "Avrupa", ["Altının çoğu Paris'te", "yeraltı kasalarında"],
       "Fransa. Altının çoğu Pariste, yeraltı kasalarında.", "France"),
      ("İtalya", 2452, "Avrupa", ["Rezervinin yaklaşık", "üçte ikisi altın"],
       "İtalya. Döviz rezervinin büyük kısmı altın.", "Italy"),
      ("Almanya", 3349, "Avrupa", ["Bir kısmı hâlâ New York", "ve Londra'da saklanıyor"],
       "Almanya. Altınının bir kısmı hâlâ New York ve Londra'da saklanıyor.", "Germany"),
      ("ABD", 8133, "Kuzey Amerika", ["Çoğu Fort Knox'ta;", "yıllardır miktar sabit"],
       "Amerika Birleşik Devletleri! Altının büyük kısmı Fort Noks'ta. Miktar yıllardır neredeyse hiç değişmedi.", "Fort Knox"),
  ],
  "En çok altın rezervi olan 10 ülke 🥇 1 numaranın altını 2. sıradakinin 2 katından fazla! Sence hangisi? 👇",
  ["#altın", "#ekonomi", "#merkezbankası", "#dünya", "#bilgi", "#reels", "#keşfet"],
  kapanis_ust="Sen bunu", kapanis_vurgu="biliyor muydun?",
  notlar="Resmi altın rezervleri, World Gold Council / IMF IFS (Temmuz–Ağustos 2026 verisi, bestbrokers.com Ekim 2026). Türkiye ve Hollanda yakın sıralarda; sıralama alımlarla değişebilir.")

# 031 ---------------------------------------------------------------------------------
T("031-turkiyenin-en-kalabalik-5-ilcesi.json", "turkiyenin-en-kalabalik-5-ilcesi",
  ["TÜRKİYE'NİN", "EN KALABALIK", "İLÇESİ"],
  ["1 numara, nüfusuyla", "57 İLİ geride bırakıyor!"],
  "Türkiye'nin en kalabalık beş ilçesi! Bir numara, nüfusuyla elli yedi ili geride bırakıyor.",
  "kişi", "ikon", [
      ("Şehitkamil", 905880, "Gaziantep", ["Gaziantep'in iki dev", "ilçesinden biri"],
       "Şehitkamil, Gaziantep. Şehrin iki dev ilçesinden biri.", None),
      ("Keçiören", 931722, "Ankara", ["Başkentin en kalabalık", "ikinci ilçesi"],
       "Keçiören, Ankara. Başkentin en kalabalık ikinci ilçesi.", None),
      ("Çankaya", 952198, "Ankara", ["Meclis, Anıtkabir ve", "bakanlıklar burada"],
       "Çankaya, Ankara. Meclis, Anıtkabir ve bakanlıklar burada.", None),
      ("Şahinbey", 957792, "Gaziantep", ["Gaziantep Kalesi ve", "Zeugma Müzesi burada"],
       "Şahinbey, Gaziantep. Gaziantep Kalesi ve Zeugma Müzesi burada.", None),
      ("Esenyurt", 1003905, "İstanbul", ["Nüfusu 1 milyonu aşan", "ilk ilçe"],
       "Esenyurt, İstanbul! Nüfusu bir milyonu aşan ilk ilçe. Elli yedi ilden daha kalabalık.", None),
  ],
  "Türkiye'nin en kalabalık 5 ilçesi 🏙️ 1 numara, nüfusuyla 57 ili geride bırakıyor! Sence hangisi? 👇",
  ["#türkiye", "#nüfus", "#tüik", "#şehir", "#bilgi", "#reels", "#keşfet"],
  kapanis_ust="Sen hangi ilçede", kapanis_vurgu="yaşıyorsun?",
  notlar="TÜİK ADNKS 2025 sonuçları (31.12.2025).",
  ekstra={"ikon": "insan", "ikon_deger": 100000, "ikon_etiket": "100 bin kişi"})

# 032 ---------------------------------------------------------------------------------
T("032-dunyanin-en-yuksek-5-heykeli.json", "dunyanin-en-yuksek-5-heykeli",
  ["DÜNYANIN", "EN YÜKSEK", "HEYKELİ"],
  ["1 numara, Özgürlük Heykeli'nin", "neredeyse 4 KATI!"],
  "Dünyanın en yüksek beş heykeli! Bir numara, Özgürlük Heykeli'nin neredeyse dört katı.",
  "m", "cubuk", [
      ("Ushiku Daibutsu", 100, "Japonya", ["İçinde asansörle çıkılan", "bir gözlem katı var"],
       "Uşiku Daybutsu, Japonya. İçinde asansörle çıkılan bir gözlem katı var.", "Ushiku Daibutsu"),
      ("Vishwas Swaroopam", 106, "Hindistan", ["Dünyanın en yüksek", "Şiva heykeli"],
       "Vişvas Svarupam, Hindistan. Dünyanın en yüksek Şiva heykeli.", "Statue of Belief Nathdwara"),
      ("Laykyun Sekkya", 116, "Myanmar", ["Önünde 95 metrelik", "yatan bir Buda da var"],
       "Laykyun Sekya, Myanmar. Önünde doksan beş metrelik yatan bir Buda heykeli de var.", "Laykyun Sekkya"),
      ("Bahar Tapınağı Budası", 128, "Henan, Çin", ["10 yıl boyunca dünyanın", "en yüksek heykeliydi"],
       "Bahar Tapınağı Budası, Çin. On yıl boyunca dünyanın en yüksek heykeliydi.", "Spring Temple Buddha"),
      ("Birlik Heykeli", 182, "Gucerat, Hindistan", ["Sardar Patel'i anlatıyor;", "kaidesiyle 240 metre"],
       "Birlik Heykeli, Hindistan! Bağımsızlık lideri Sardar Patel'i anlatıyor. Kaidesiyle birlikte iki yüz kırk metre.", "Statue of Unity"),
  ],
  "Dünyanın en yüksek 5 heykeli 🗿 1 numara Özgürlük Heykeli'nin neredeyse 4 katı! Sence hangisi? 👇",
  ["#heykel", "#anıt", "#dünya", "#mimari", "#bilgi", "#reels", "#keşfet"],
  kapanis_ust="Sen hangisini", kapanis_vurgu="görmek isterdin?",
  notlar="Kaidesiz heykel yüksekliği (Wikipedia, BBC Science Focus). Özgürlük Heykeli kaidesiz 46 m.")

# 033 ---------------------------------------------------------------------------------
T("033-gezegenlerde-en-uzun-yil.json", "gezegenlerde-en-uzun-yil",
  ["YILI EN UZUN", "SÜREN", "GEZEGEN"],
  ["1 numara keşfedildiğinden beri", "Güneş'i ancak 1 KEZ dolandı!"],
  "Bir yılı en uzun süren beş gezegen! Bir numara keşfedildiğinden beri, Güneş'in etrafını ancak bir kez dolandı.",
  "Dünya yılı", "cubuk", [
      ("Mars", 1.88, "Kızıl gezegen", ["Bir yılı yaklaşık", "687 gün sürüyor"],
       "Mars. Bir yılı yaklaşık altı yüz seksen yedi gün sürüyor.", "Mars"),
      ("Jüpiter", 11.86, "Gaz devi", ["Bir günü ise", "sadece 10 saat"],
       "Jüpiter. Bir yılı on iki yıla yakın, ama bir günü sadece on saat.", "Jupiter"),
      ("Satürn", 29.46, "Gaz devi", ["Burada 30 yaşında", "olan kimse yok"],
       "Satürn. Bir yılı neredeyse otuz Dünya yılı.", "Saturn"),
      ("Uranüs", 84.0, "Buz devi", ["Yan yatmış döner: 42 yıl", "gündüz, 42 yıl gece"],
       "Uranüs. Yan yatmış döndüğü için kutuplarında kırk iki yıl gündüz, kırk iki yıl gece.", "Uranus"),
      ("Neptün", 164.8, "Buz devi", ["1846'da keşfedildi; ilk tam", "turunu 2011'de bitirdi"],
       "Neptün! Bir yılı yüz altmış beş Dünya yılı. Bin sekiz yüz kırk altıda keşfedildi, ilk tam turunu iki bin on birde tamamladı.", "Neptune"),
  ],
  "Bir yılı en uzun süren 5 gezegen 🪐 1 numara keşfedildiğinden beri Güneş'i ancak 1 kez dolandı! Sence hangisi? 👇",
  ["#uzay", "#gezegen", "#astronomi", "#güneşsistemi", "#bilgi", "#reels", "#keşfet"],
  kapanis_ust="Sen bunu", kapanis_vurgu="biliyor muydun?",
  notlar="Yörünge dönemleri Dünya yılı cinsinden (NASA).")

# 034 ---------------------------------------------------------------------------------
T("034-dunyanin-en-uzun-4-demiryolu-tuneli.json", "dunyanin-en-uzun-4-demiryolu-tuneli",
  ["DÜNYANIN", "EN UZUN", "TREN TÜNELİ"],
  ["Dünyada 50 km'yi aşan", "sadece 4 tren tüneli var!"],
  "Dünyanın en uzun dört demiryolu tüneli! Dünyada elli kilometreyi aşan sadece dört tren tüneli var.",
  "km", "cubuk", [
      ("Yulhyeon Tüneli", 50.3, "Güney Kore", ["Sadece 3,5 yılda", "tamamlandı"],
       "Yulhyon Tüneli, Güney Kore. Sadece üç buçuk yılda tamamlandı.", "Yulhyeon Tunnel"),
      ("Manş Tüneli", 50.5, "İngiltere – Fransa", ["38 km'si deniz altında:", "bir rekor"],
       "Manş Tüneli, İngiltere ve Fransa. Otuz sekiz kilometresi deniz altında, bu bir dünya rekoru.", "Channel Tunnel"),
      ("Seikan Tüneli", 53.9, "Japonya", ["Deniz tabanının 100 m", "altından geçiyor"],
       "Seykan Tüneli, Japonya. Deniz tabanının yüz metre altından geçiyor.", "Seikan Tunnel"),
      ("Gotthard Tüneli", 57.1, "İsviçre", ["Üstünde 2.300 metre", "dağ var"],
       "Gothard Tüneli, İsviçre! Dünyanın en uzun ve en derin tren tüneli. Üstünde iki bin üç yüz metre dağ var.", "Gotthard Base Tunnel"),
  ],
  "Dünyanın en uzun 4 tren tüneli 🚄 50 km'yi aşan sadece 4 tünel var! Sence 1 numara hangisi? 👇",
  ["#tünel", "#tren", "#mühendislik", "#dünya", "#bilgi", "#reels", "#keşfet"],
  kapanis_ust="Sen hangisinden", kapanis_vurgu="geçtin?",
  notlar="Metro tünelleri hariç (Wikipedia).")

# 035 ---------------------------------------------------------------------------------
T("035-dunyanin-en-kalabalik-5-adasi.json", "dunyanin-en-kalabalik-5-adasi",
  ["DÜNYANIN", "EN KALABALIK", "ADASI"],
  ["1 numarada, Türkiye'den", "çok daha FAZLA insan yaşıyor!"],
  "Dünyanın en kalabalık beş adası! Bir numarada, Türkiye'den çok daha fazla insan yaşıyor.",
  "milyon", "ikon", [
      ("Sumatra", 58.6, "Endonezya", ["Orangutanların yaşadığı", "iki adadan biri"],
       "Sumatra, Endonezya. Orangutanların yaşadığı iki adadan biri.", "Sumatra"),
      ("Luzon", 64.3, "Filipinler", ["Başkent Manila", "bu adada"],
       "Luzon, Filipinler. Başkent Manila bu adada.", "Luzon"),
      ("Büyük Britanya", 65.0, "Birleşik Krallık", ["İngiltere, İskoçya ve", "Galler bu adada"],
       "Büyük Britanya. İngiltere, İskoçya ve Galler bu adada.", "Great Britain"),
      ("Honşu", 104.0, "Japonya", ["Tokyo, Osaka ve", "Kyoto bu adada"],
       "Honşu, Japonya. Tokyo, Osaka ve Kyoto bu adada.", "Honshu"),
      ("Cava", 151.6, "Endonezya", ["Endonezyalıların yarısından", "fazlası burada yaşıyor"],
       "Cava, Endonezya! Dünyanın en kalabalık adası. Endonezyalıların yarısından fazlası burada yaşıyor.", "Java Indonesia"),
  ],
  "Dünyanın en kalabalık 5 adası 🏝️ 1 numarada Türkiye'den çok daha fazla insan yaşıyor! Sence hangisi? 👇",
  ["#ada", "#nüfus", "#dünya", "#coğrafya", "#bilgi", "#reels", "#keşfet"],
  kapanis_ust="Sen hangisine", kapanis_vurgu="gitmek isterdin?",
  notlar="Son nüfus sayımları (Endonezya/Filipinler/Japonya 2020, Birleşik Krallık 2021–22); yaklaşık değerler.",
  ekstra={"ikon": "insan", "ikon_deger": 10, "ikon_etiket": "10 milyon kişi"})

# 036 ---------------------------------------------------------------------------------
T("036-avrupanin-en-uzun-5-nehri.json", "avrupanin-en-uzun-5-nehri",
  ["AVRUPA'NIN", "EN UZUN", "NEHRİ"],
  ["1 numara baştan sona", "TEK BİR ülkeden akıyor!"],
  "Avrupa'nın en uzun beş nehri! Bir numara baştan sona tek bir ülkeden akıyor.",
  "km", "cubuk", [
      ("Don", 1870, "Rusya", ["Azak Denizi'ne", "dökülüyor"],
       "Don Nehri, Rusya. Azak Denizine dökülüyor.", "Don River"),
      ("Dinyeper", 2201, "Rusya – Belarus – Ukrayna", ["Kiev'in ortasından", "geçiyor"],
       "Dinyeper. Kiev'in ortasından geçiyor ve Karadeniz'e dökülüyor.", "Dnieper"),
      ("Ural", 2428, "Rusya – Kazakistan", ["Avrupa ile Asya'nın", "sınırı sayılıyor"],
       "Ural Nehri. Avrupa ile Asya'nın sınırı sayılıyor.", "Ural River"),
      ("Tuna", 2850, "10 ülke", ["Dünyada en çok ülkeden", "geçen nehir: 10"],
       "Tuna. Dünyada en çok ülkeden geçen nehir, tam on ülke.", "Danube"),
      ("Volga", 3530, "Rusya", ["Hazar Denizi'ne", "dökülüyor"],
       "Volga! Avrupa'nın en uzun nehri. Baştan sona Rusya'dan akıp Hazar Denizine dökülüyor.", "Volga River"),
  ],
  "Avrupa'nın en uzun 5 nehri 🏞️ 1 numara baştan sona tek bir ülkeden akıyor! Sence hangisi? 👇",
  ["#avrupa", "#nehir", "#doğa", "#coğrafya", "#bilgi", "#reels", "#keşfet"],
  kapanis_ust="Sen hangisini", kapanis_vurgu="gördün?",
  notlar="Uzunluklar kaynaklara göre biraz değişebilir.")

# 037 ---------------------------------------------------------------------------------
T("037-dunyanin-en-buyuk-5-stadyumu.json", "dunyanin-en-buyuk-5-stadyumu",
  ["DÜNYANIN", "EN BÜYÜK", "STADYUMU"],
  ["1 numara bir futbol değil,", "KRİKET stadyumu!"],
  "Dünyanın en büyük beş stadyumu! Bir numara, bir futbol değil kriket stadyumu.",
  "kişi", "ikon", [
      ("Ohio Stadyumu", 102780, "Columbus, ABD", ["Bir üniversite", "futbol stadyumu"],
       "Ohayo Stadyumu, Amerika. Bir üniversite futbol stadyumu.", "Ohio Stadium"),
      ("Beaver Stadyumu", 106572, "Pennsylvania, ABD", ["Maç günü eyaletin", "en kalabalık 3. şehri olur"],
       "Biver Stadyumu, Amerika. Maç günü eyaletin en kalabalık üçüncü şehri gibi.", "Beaver Stadium"),
      ("Michigan Stadyumu", 107601, "Ann Arbor, ABD", ["Lakabı 'Büyük Ev':", "ABD'nin en büyüğü"],
       "Miçigın Stadyumu, Amerika. Lakabı Büyük Ev.", "Michigan Stadium"),
      ("Rungrado 1 Mayıs", 114000, "Pyongyang, Kuzey Kore", ["Çatısı bir çiçeğin", "taç yapraklarına benziyor"],
       "Rungrado Bir Mayıs Stadyumu, Kuzey Kore. Çatısı bir çiçeğin taç yapraklarına benziyor.", "Rungrado May Day Stadium"),
      ("Narendra Modi Stadyumu", 132000, "Ahmedabad, Hindistan", ["Dünyanın en büyük", "kriket stadyumu"],
       "Narendra Modi Stadyumu, Hindistan! Yüz otuz iki bin kişilik bir kriket stadyumu.", "Narendra Modi Stadium"),
  ],
  "Dünyanın en büyük 5 stadyumu 🏟️ 1 numara futbol değil, kriket stadyumu! Sence hangisi? 👇",
  ["#stadyum", "#spor", "#futbol", "#dünya", "#bilgi", "#reels", "#keşfet"],
  kapanis_ust="Sen hangisinde", kapanis_vurgu="maç izlemek isterdin?",
  notlar="Oturma kapasitesi (Wikipedia). Rungrado için eski 150.000 iddiası resmi değil; güncel 114.000.",
  ekstra={"ikon": "insan", "ikon_deger": 10000, "ikon_etiket": "10 bin kişi"})

# 038 ---------------------------------------------------------------------------------
T("038-turkiyenin-en-buyuk-5-baraj-golu.json", "turkiyenin-en-buyuk-5-baraj-golu",
  ["TÜRKİYE'NİN", "EN BÜYÜK", "BARAJ GÖLÜ"],
  ["1 numara, Türkiye'nin", "en büyük 3. gölü!"],
  "Türkiye'nin en büyük beş baraj gölü! Bir numara, doğal göller dahil Türkiye'nin en büyük üçüncü gölü.",
  "km²", "sekil", [
      ("Hirfanlı", 263, "Kırşehir – Ankara", ["Kızılırmak üzerinde;", "1959'da tamamlandı"],
       "Hirfanlı Baraj Gölü, Kızılırmak üzerinde. Bin dokuz yüz elli dokuzda tamamlandı.", None),
      ("Karakaya", 298, "Malatya – Elazığ – Diyarbakır", ["Fırat üzerindeki", "ikinci büyük baraj"],
       "Karakaya Baraj Gölü, Fırat üzerinde.", None),
      ("Ilısu", 313, "Mardin – Şırnak – Siirt – Batman", ["Dicle üzerinde;", "eski Hasankeyf sular altında"],
       "Ilısu Baraj Gölü, Dicle üzerinde. Eski Hasankeyf sular altında kaldı.", None),
      ("Keban", 675, "Elazığ – Tunceli", ["Türkiye'nin ilk", "dev baraj projesi"],
       "Keban Baraj Gölü, Elazığ. Türkiye'nin ilk dev baraj projesi.", None),
      ("Atatürk Baraj Gölü", 817, "Şanlıurfa – Adıyaman", ["GAP'ın kalbi;", "Van ve Tuz Gölü'nden sonra"],
       "Atatürk Baraj Gölü! GAP'ın kalbi. Van ve Tuz Gölünden sonra Türkiye'nin en büyük üçüncü gölü.", None),
  ],
  "Türkiye'nin en büyük 5 baraj gölü 💧 1 numara, doğal göller dahil Türkiye'nin en büyük 3. gölü! Sence hangisi? 👇",
  ["#türkiye", "#baraj", "#göl", "#coğrafya", "#bilgi", "#reels", "#keşfet"],
  kapanis_ust="Sen hangisini", kapanis_vurgu="gördün?",
  notlar="Yüzölçümleri (Wikipedia 'List of lakes of Turkey' / DSİ). Su seviyesine göre değişir.",
  ekstra={"stil": "su"})

# 039 ---------------------------------------------------------------------------------
T("039-alplerin-en-yuksek-5-dagi.json", "alplerin-en-yuksek-5-dagi",
  ["ALPLERİN", "EN YÜKSEK", "DAĞI"],
  ["1 numaranın zirvesi", "her yıl BOYU değişiyor!"],
  "Alplerin en yüksek beş dağı! Bir numaranın zirvesi, her yıl boyu değişiyor.",
  "m", "dag", [
      ("Weisshorn", 4506, "İsviçre", ["Alplerin en güzel", "piramitlerinden biri"],
       "Vayshorn, İsviçre. Alplerin en güzel piramit şekilli zirvelerinden.", "Weisshorn"),
      ("Lyskamm", 4527, "İsviçre – İtalya", ["Çığları yüzünden", "'insan yiyen' lakaplı"],
       "Liskam, İsviçre ve İtalya. Çığları yüzünden insan yiyen lakabı var.", "Lyskamm"),
      ("Dom", 4545, "İsviçre", ["Tamamı İsviçre'de olan", "en yüksek dağ"],
       "Dom, İsviçre. Tamamı İsviçre'de olan en yüksek dağ.", "Dom mountain"),
      ("Monte Rosa", 4634, "İsviçre – İtalya", ["Avrupa'nın en yüksek", "kulübesi zirvesinde"],
       "Monte Roza, İsviçre ve İtalya. Avrupa'nın en yüksek dağ kulübesi zirvesinde.", "Monte Rosa"),
      ("Mont Blanc", 4806, "Fransa – İtalya", ["Zirvesindeki buz yüzünden", "boyu her yıl değişiyor"],
       "Mon Blan! Alplerin ve Batı Avrupa'nın çatısı. Zirvesindeki buz yüzünden boyu her ölçümde değişiyor.", "Mont Blanc"),
  ],
  "Alplerin en yüksek 5 dağı 🏔️ 1 numaranın zirvesi her yıl boyu değişiyor! Sence hangisi? 👇",
  ["#alpler", "#dağ", "#avrupa", "#doğa", "#bilgi", "#reels", "#keşfet"],
  kapanis_ust="Sen hangisine", kapanis_vurgu="tırmanmak isterdin?",
  notlar="Ayrı dağlar, alt zirveler sayılmadı. Mont Blanc son ölçüm ~4.805,6 m.")

# 040 ---------------------------------------------------------------------------------
T("040-akdenizin-en-buyuk-5-adasi.json", "akdenizin-en-buyuk-5-adasi",
  ["AKDENİZ'İN", "EN BÜYÜK", "ADASI"],
  ["1 numaranın üstünde, Avrupa'nın", "en yüksek AKTİF yanardağı var!"],
  "Akdeniz'in en büyük beş adası! Bir numaranın üstünde, Avrupa'nın en yüksek aktif yanardağı var.",
  "km²", "sekil", [
      ("Girit", 8336, "Yunanistan", ["Minos uygarlığının", "beşiği"],
       "Girit, Yunanistan. Minos uygarlığının beşiği.", "Crete"),
      ("Korsika", 8680, "Fransa", ["Napolyon'un", "doğduğu ada"],
       "Korsika, Fransa. Napolyon'un doğduğu ada.", "Corsica"),
      ("Kıbrıs", 9251, "Doğu Akdeniz", ["Doğu Akdeniz'in", "en büyük adası"],
       "Kıbrıs. Doğu Akdeniz'in en büyük adası.", "Cyprus"),
      ("Sardinya", 24090, "İtalya", ["Dünyada en çok 100 yaşını", "aşanın yaşadığı yerlerden"],
       "Sardinya, İtalya. Dünyada yüz yaşını aşan insanların en çok yaşadığı yerlerden.", "Sardinia"),
      ("Sicilya", 25711, "İtalya", ["Etna Yanardağı:", "yaklaşık 3.300 metre"],
       "Sicilya! Akdeniz'in en büyük adası. Üstünde Avrupa'nın en yüksek aktif yanardağı Etna var.", "Sicily"),
  ],
  "Akdeniz'in en büyük 5 adası 🏝️ 1 numaranın üstünde Avrupa'nın en yüksek aktif yanardağı var! Sence hangisi? 👇",
  ["#akdeniz", "#ada", "#tatil", "#coğrafya", "#bilgi", "#reels", "#keşfet"],
  kapanis_ust="Sen hangisine", kapanis_vurgu="gitmek isterdin?",
  ekstra={"stil": "kara"})

# 041 ---------------------------------------------------------------------------------
T("041-avrupanin-en-buyuk-5-ulkesi.json", "avrupanin-en-buyuk-5-ulkesi",
  ["TAMAMI AVRUPA'DA", "EN BÜYÜK", "ÜLKE"],
  ["Rusya'yı saymazsak", "1 numara seni ŞAŞIRTABİLİR!"],
  "Topraklarının tamamı Avrupa'da olan en büyük beş ülke! Rusya'yı saymazsak, bir numara seni şaşırtabilir.",
  "bin km²", "sekil", [
      ("Norveç", 385.2, "İskandinavya", ["Fiyortlarıyla kıyısı", "100.000 km'yi aşıyor"],
       "Norveç. Fiyortları ve adalarıyla kıyısı yüz bin kilometreyi aşıyor.", "Norway fjord"),
      ("İsveç", 450.3, "İskandinavya", ["Yaklaşık 100.000", "gölü var"],
       "İsveç. Yaklaşık yüz bin gölü var.", "Sweden"),
      ("İspanya", 506.0, "İber Yarımadası", ["Avrupa'nın en dağlık", "ülkelerinden"],
       "İspanya. Avrupa'nın en dağlık ülkelerinden biri.", "Spain"),
      ("Fransa", 551.7, "Batı Avrupa", ["Dünyada en çok turist", "ağırlayan ülke"],
       "Fransa. Dünyada en çok turist ağırlayan ülke.", "France"),
      ("Ukrayna", 603.6, "Doğu Avrupa", ["Toprağının yarısından", "fazlası verimli kara toprak"],
       "Ukrayna! Tamamı Avrupa'da olan en büyük ülke. Toprağının yarısından fazlası verimli kara toprak.", "Ukraine wheat"),
  ],
  "Tamamı Avrupa'da olan en büyük 5 ülke 🗺️ Rusya'yı saymazsak 1 numara seni şaşırtabilir! Sence hangisi? 👇",
  ["#avrupa", "#ülke", "#harita", "#coğrafya", "#bilgi", "#reels", "#keşfet"],
  kapanis_ust="Sen hangisine", kapanis_vurgu="gittin?",
  notlar="Rusya, Türkiye ve Kazakistan topraklarının çoğu Asya'da olduğu için hariç. Fransa: anakara; Norveç: Svalbard dahil.",
  ekstra={"stil": "kara"})

# 042 ---------------------------------------------------------------------------------
T("042-asteroit-kusaginin-en-buyuk-5-cismi.json", "asteroit-kusaginin-en-buyuk-5-cismi",
  ["ASTEROİT KUŞAĞI'NIN", "EN BÜYÜK", "CİSMİ"],
  ["1 numara tek başına kuşağın", "kütlesinin 3'te BİRİ!"],
  "Asteroit kuşağının en büyük beş cismi! Bir numara, tek başına kuşağın kütlesinin üçte biri.",
  "km", "daire", [
      ("Interamnia", 332, "Asteroit kuşağı", ["Adı İtalya'daki", "Teramo şehrinden"],
       "İnteramnia. Adını İtalya'daki Teramo şehrinin eski adından alıyor.", None),
      ("Hygiea", 434, "Asteroit kuşağı", ["Neredeyse küre şeklinde;", "cüce gezegen adayı"],
       "Haygiya. Neredeyse küre şeklinde, cüce gezegen adayı.", None),
      ("Pallas", 511, "Asteroit kuşağı", ["Yörüngesi çok", "eğik"],
       "Pallas. Yörüngesi diğerlerine göre çok eğik.", None),
      ("Vesta", 525, "Asteroit kuşağı", ["Bazen çıplak gözle", "görülebilen tek asteroit"],
       "Vesta. Bazen çıplak gözle görülebilen tek asteroit.", None),
      ("Ceres", 939, "Asteroit kuşağı", ["Kuşaktaki tek", "cüce gezegen"],
       "Seres! Kuşağın en büyük cismi, ve kuşaktaki tek cüce gezegen.", None),
  ],
  "Asteroit kuşağının en büyük 5 cismi ☄️ 1 numara tek başına kuşağın kütlesinin 3'te 1'i! Sence hangisi? 👇",
  ["#uzay", "#asteroit", "#astronomi", "#güneşsistemi", "#bilgi", "#reels", "#keşfet"],
  kapanis_ust="Sen bunu", kapanis_vurgu="biliyor muydun?",
  notlar="Ortalama çaplar (NASA/JPL).", olcek="dogrusal")
print("ok")
