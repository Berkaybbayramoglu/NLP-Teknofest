✨ TEKNOFEST 2025 Türkçe Doğal Dil İşleme Yarışması Projesi ✨
🚀 Bu depo, TEKNOFEST 2025 Türkçe Doğal Dil İşleme Yarışması'na katılan ekibimizin "Üretken Yapay Zeka Destekli Otonom Çağrı Merkezi Senaryoları" kategorisi için geliştirdiği çığır açan projeyi sunmaktadır. Amacımız, telekomünikasyon sektöründeki karmaşık müşteri taleplerini anlayan, işleyen ve çözüme ulaştıran tamamen otonom bir yapay zeka sistemi geliştirmektir.

🎯 Proje Amacı ve Kapsamı
Günümüz telekomünikasyon sektöründe müşteri memnuniyetini en üst düzeye çıkarmak için, geleneksel statik çağrı merkezi akışlarının ötesine geçen, dinamik ve insansı yeteneklere sahip bir yapay zeka ajanı tasarlıyoruz. Projemiz, Agentic Framework'ler ve Büyük Dil Modelleri (LLM) kullanarak aşağıdaki temel beklentileri titizlikle karşılamaktadır:

Dinamik Araç Seçimi ve Kullanımı: Ajanımız, konuşma bağlamına göre hangi "aracı" (fonksiyonu, API çağrısını) kullanacağına akıllıca ve dinamik olarak kendisi karar verir. Önceden tanımlanmış if/else ağaçları yerine, LLM'in derin düşünme yeteneği ile ihtiyacı belirler.

Bağlam Değişimi ve Kesinti Yönetimi: Müşteri bir senaryo sırasında aniden farklı bir konuya geçtiğinde veya sohbet kesintiye uğradığında, ajan bu durumu anlar, mevcut durumu ustaca yönetir ve diyaloğu sorunsuz bir şekilde sürdürür.

Çok Adımlı Karar Zincirleri: Ajan, tek bir API çağrısıyla çözülemeyen, birden fazla adımdan oluşan karmaşık senaryoları (örn: getUserInfo sonucuna göre getAvailablePackages çağırma) başarıyla yönetir, zincirleme kararlar alır.

Harici Sistem Simülasyonu (Mock Fonksiyonlar): Gerçekçi bir çağrı merkezi deneyimi sunmak için müşteri veritabanı, faturalama sistemi, paket kataloğu gibi "arka uç sistemlerle" etkileşimi simüle eden kendi "mock" fonksiyonlarımızı geliştirdik ve ajanın araçları olarak sorunsuz bir şekilde entegre ettik.

Durum Yönetimi ve Bellek: Ajan, sohbet geçmişini (bellek) etkin bir şekilde kullanarak daha bilinçli ve bağlama uygun yanıtlar üretir. Tüm etkileşimler uygun bir mimari ile loglanır ve gerçek zamanlı olarak monitör edilebilir.

Hata İşleme ve Kullanıcıya Bilgi Verme: Mock fonksiyonlardan gelebilecek hataları anlar, nazikçe kullanıcıya aktarır ve olası çözüm önerileri sunar. Ham hata mesajları asla kullanıcıya iletilmez.

Minimum Statik Yapı: Çözümümüz, önceden kodlanmış, koşullu dallanma yapıları yerine ajanın dinamik akıl yürütme ve araç çağırma yeteneklerine dayanır. Senaryo akışları, ajanın çalışma zamanındaki kararlarına bırakılır.

Açık Kaynak Kod Yaklaşımı: Projemizdeki tüm kodlar açık kaynak kod tabanlı teknolojiler kullanılarak geliştirilmiştir ve Apache Lisansı 2.0 altında lisanslanmıştır. Şeffaflığa ve topluluğa katkıya inanıyoruz!

📞 Örnek Senaryo: Paket Değişikliği Talebi
Projemiz, telekom çağrı merkezlerinde sıkça karşılaşılan "Paket Değişikliği Talebi" gibi senaryoları uçtan uca otomatize etmeyi başarmaktadır. Bu senaryo, müşteriyi tanımlama, mevcut paket durumunu kontrol etme, uygun paketleri listeleme, müşterinin seçimini anlama ve paket değişikliği işlemini başlatma gibi kritik aşamaları içermektedir.

📦 Teslim Edilenler
Çalışan Proje Kodu: Agent, mock fonksiyonlar, arayüz kodu ve benchmark kodu dahil tüm kaynak kodları.

Kurulum Talimatları: Kodun çalıştırılması için gerekli tüm adımlar (gereksinimler, çevre değişkenleri vb.) net bir şekilde belirtilmiştir.

Veri Setleri:

STT ve TTS Test Verileri: Konuşma Tanıma (STT) ve Metin Okuma (TTS) testleri için kullanılan büyük Türkçe ses ve metin veri seti TR.zip dosyası olarak mevcuttur. Bu dosya boyutu nedeniyle doğrudan bu depoya dahil edilmemiştir. Lütfen aşağıdaki bağlantıdan indiriniz ve projenizin ana dizinindeki data/ klasörüne açınız:

TR.zip Veri Seti İndirme Bağlantısı

Diğer mock veri dosyaları (user.json, packages.json) proje dizini içinde data/ klasöründe yer almaktadır.

Proje Dokümantasyonu: Sistem mimarisi, kullanılan framework'ler, implemente edilen senaryolar ve karşılaşılan zorluklara getirilen çözümler detaylıca açıklanmıştır.

Ölçümleme Sonuçları: Çözümün etkinliğini ölçmek üzere geliştirilen KPI'lar (başarı oranı, karar doğruluğu, hata yönetimi etkinliği vb.) raporlanmıştır.

Ölçekleme İhtiyaçları: Günlük 100K çağrı için gerekli kaynak tahminleri sunulmuştur.

Bu proje, Türkçe Doğal Dil İşleme ve Üretken Yapay Zeka alanında telekomünikasyon sektörüne yenilikçi ve otonom bir çözüm sunmayı hedeflemektedir.