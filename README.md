TEKNOFEST 2025 Türkçe Doğal Dil İşleme Yarışması Projesi
Bu depo, TEKNOFEST 2025 Türkçe Doğal Dil İşleme Yarışması'na katılan ekibimizin "Üretken Yapay Zeka Destekli Otonom Çağrı Merkezi Senaryoları" kategorisi için geliştirdiği projeyi içermektedir. Projemiz, telekomünikasyon sektöründeki karmaşık müşteri taleplerini anlayan, işleyen ve çözüme ulaştıran otonom bir yapay zeka sistemi geliştirmeyi hedeflemektedir.

Proje Amacı ve Kapsamı
Günümüz telekomünikasyon sektöründe müşteri memnuniyetini artırmak amacıyla, geleneksel statik çağrı merkezi akışlarının ötesine geçen, dinamik ve insansı yeteneklere sahip bir yapay zeka ajanı geliştirmeyi amaçlıyoruz. Projemiz, Agentic Framework'ler ve Büyük Dil Modelleri (LLM) kullanarak aşağıdaki temel beklentileri karşılamaktadır:

Dinamik Araç Seçimi ve Kullanımı: Ajan, konuşma bağlamına göre gerekli "aracı" (fonksiyonu, API çağrısını) dinamik olarak kendisi seçer ve kullanır. Önceden tanımlanmış if/else ağaçları yerine, LLM'in düşünme yeteneği ile ihtiyacı belirler.

Bağlam Değişimi ve Kesinti Yönetimi: Müşteri bir senaryo sırasında farklı bir konuya geçtiğinde veya sohbet kesildiğinde, ajan bu durumu anlar, yönetir ve diyaloğu uygun şekilde sürdürür.

Çok Adımlı Karar Zincirleri: Ajan, tek bir API çağrısıyla çözülemeyen, birden fazla adımdan oluşan karmaşık senaryoları (örn: getUserInfo sonucuna göre getAvailablePackages çağırma) yönetir.

Harici Sistem Simülasyonu (Mock Fonksiyonlar): Gerçekçi bir çağrı merkezi deneyimi için müşteri veritabanı, faturalama sistemi, paket kataloğu gibi "arka uç sistemlerle" etkileşimi simüle eden kendi "mock" fonksiyonlarımızı geliştirdik ve ajanın araçları olarak entegre ettik.

Durum Yönetimi ve Bellek: Ajan, sohbet geçmişini (bellek) etkin kullanarak daha bilinçli ve bağlama uygun yanıtlar üretir. Tüm etkileşimler uygun bir mimari ile loglanır ve monitör edilebilir.

Hata İşleme ve Kullanıcıya Bilgi Verme: Mock fonksiyonlardan gelebilecek hataları anlar, nazikçe kullanıcıya aktarır ve çözüm önerileri sunar. Ham hata mesajları kullanıcıya iletilmez.

Minimum Statik Yapı: Çözüm, önceden kodlanmış, koşullu dallanma yapıları yerine ajanın dinamik akıl yürütme ve araç çağırma yeteneklerine dayanır.

Açık Kaynak Kod Yaklaşımı: Projemizdeki tüm kodlar açık kaynak kod tabanlı teknolojiler kullanılarak geliştirilmiştir ve Apache Lisansı 2.0 altında lisanslanmıştır.

Örnek Senaryo: Paket Değişikliği Talebi
Projemiz, telekom çağrı merkezlerinde sıkça karşılaşılan "Paket Değişikliği Talebi" gibi senaryoları uçtan uca otomatize etmeyi başarmaktadır. Bu senaryo, müşteriyi tanımlama, mevcut paket durumunu kontrol etme, uygun paketleri listeleme, müşterinin seçimini anlama ve paket değişikliği işlemini başlatma gibi aşamaları içermektedir.

Teslim Edilenler
Çalışan Proje Kodu: Agent, mock fonksiyonlar, arayüz kodu ve benchmark kodu dahil tüm kaynak kodları.

Kurulum Talimatları: Kodun çalıştırılması için gerekli tüm adımlar (gereksinimler, çevre değişkenleri vb.) net bir şekilde belirtilmiştir.

Proje Dokümantasyonu: Sistem mimarisi, kullanılan framework'ler, implemente edilen senaryolar ve karşılaşılan zorluklara getirilen çözümler detaylıca açıklanmıştır.

Ölçümleme Sonuçları: Çözümün etkinliğini ölçmek üzere geliştirilen KPI'lar (başarı oranı, karar doğruluğu, hata yönetimi etkinliği vb.) raporlanmıştır.

Ölçekleme İhtiyaçları: Günlük 100K çağrı için gerekli kaynak tahminleri sunulmuştur.

Bu proje, Türkçe Doğal Dil İşleme ve Üretken Yapay Zeka alanında telekomünikasyon sektörüne yenilikçi ve otonom bir çözüm sunmayı hedeflemektedir.