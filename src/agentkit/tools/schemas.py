# src/agentkit/tools/schemas.py
function_schemas = [
    {
        "name": "getUserInfo",
        "description": "Kullanıcı kimlik doğrulama için T.C. kimlik numarası, müşteri ID’si veya telefon numarası ile kullanıcı bilgilerini getirir.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcının T.C. kimlik numarası, müşteri ID’si veya telefon numarası."}
            },
            "required": ["user_identifier"]
        }
    },
    {
        "name": "getAvailablePackages",
        "description": "Kullanıcının meslek bilgisine göre uygun paketleri getirir.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcının T.C. kimlik numarası, müşteri ID’si veya telefon numarası."}
            },
            "required": ["user_identifier"]
        }
    },
    {
        "name": "initiatePackageChange",
        "description": "Kullanıcının mevcut paketini yeni bir paket ile değiştirir. Gecikmiş fatura varsa işlem yapılmaz.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcının T.C. kimlik numarası, müşteri ID’si veya telefon numarası."},
                "new_package_name": {"type": "string", "description": "Yeni paket adı."}
            },
            "required": ["user_identifier", "new_package_name"]
        }
    },
    {
        "name": "getBillDetails",
        "description": "Kullanıcının fatura detaylarını listeler. Fatura ID'si veya dönem bilgisine göre filtrelenebilir.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcının kimlik bilgisi (T.C. no, müşteri ID veya telefon)."},
                "bill_id": {"type": "string", "description": "Opsiyonel fatura ID’si."},
                "period": {"type": "string", "description": "Opsiyonel dönem ('son', 'tümü')."}
            },
            "required": ["user_identifier"]
        }
    },
    {
        "name": "checkServiceAvailability",
        "description": "Girilen adres veya kullanıcı bilgisine göre fiber internet altyapısı olup olmadığını kontrol eder.",
        "parameters": {
            "type": "object",
            "properties": {
                "address_street": {"type": "string", "description": "Adres sokak bilgisi."},
                "address_city": {"type": "string", "description": "Adres şehir bilgisi."},
                "address_zip_code": {"type": "string", "description": "Adres posta kodu."},
                "user_identifier": {"type": "string", "description": "Kullanıcının kimlik bilgisi."},
                "service_type": {"type": "string", "description": "Hizmet türü (ör. 'Fiber İnternet')."}
            },
            "required": []
        }
    },
    {
        "name": "scheduleTechnicalSupport",
        "description": "Kullanıcı için teknik destek randevusu oluşturur. Hafta içi 09:00–17:00 arası olmalıdır.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcının kimlik bilgisi."},
                "issue_description": {"type": "string", "description": "Sorun açıklaması."},
                "preferred_date": {"type": "string", "description": "YYYY-MM-DD."},
                "preferred_time": {"type": "string", "description": "HH:MM."}
            },
            "required": ["user_identifier", "issue_description", "preferred_date", "preferred_time"]
        }
    },
    {
        "name": "cancelSubscription",
        "description": "Kullanıcının aktif aboneliğini iptal eder ve tarifeyle ilişkili tüm bilgileri siler.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcının kimlik bilgisi."},
                "reason": {"type": "string", "description": "İptal gerekçesi."}
            },
            "required": ["user_identifier", "reason"]
        }
    },
    {
        "name": "getUsageHistory",
        "description": "Kullanıcının internet, çağrı ve SMS kullanım geçmişini döner.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcının kimlik bilgisi."},
                "period": {"type": "string", "description": "Dönem bilgisi (ör. 'Son 3 Ay')."}
            },
            "required": ["user_identifier"]
        }
    },
    {
        "name": "blockIncomingNumber",
        "description": "Kullanıcının istemediği bir numarayı engellemesini sağlar.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcının kimlik bilgisi."},
                "target_number": {"type": "string", "description": "05XXXXXXXXX formatı."}
            },
            "required": ["user_identifier", "target_number"]
        }
    },
    {
        "name": "unblockIncomingNumber",
        "description": "Kullanıcının daha önce engellediği bir numaranın engelini kaldırır.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcının kimlik bilgisi."},
                "target_number": {"type": "string", "description": "Engeli kaldırılacak numara."}
            },
            "required": ["user_identifier", "target_number"]
        }
    },
    {
        "name": "activateEsim",
        "description": "Kullanıcının hattı için eSIM hizmetini aktif eder.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcının kimlik bilgisi."}
            },
            "required": ["user_identifier"]
        }
    },
    {
        "name": "suspendLineDueToLoss",
        "description": "Kullanıcının hattını kayıp, çalıntı veya benzeri nedenlerle geçici olarak askıya alır.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcının kimlik bilgisi."},
                "reason": {"type": "string", "description": "Gerekçe."}
            },
            "required": ["user_identifier", "reason"]
        }
    },
    {
        "name": "deactivateEsim",
        "description": "Kullanıcının hattı için aktif olan eSIM hizmetini devre dışı bırakır.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcının kimlik bilgisi."}
            },
            "required": ["user_identifier"]
        }
    },
    {
        "name": "removeDataRestriction",
        "description": "Kullanıcının hattı üzerindeki yurt dışı veri kısıtlamasını kaldırır.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcının kimlik bilgisi."}
            },
            "required": ["user_identifier"]
        }
    },
    {
        "name": "activateChildProfile",
        "description": "Kullanıcının hattı için çocuk profili modunu aktif hale getirir.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcının kimlik bilgisi."}
            },
            "required": ["user_identifier"]
        }
    },
    {
        "name": "deactivateChildProfile",
        "description": "Kullanıcının hattı için aktif olan çocuk profilini devre dışı bırakır.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcının kimlik bilgisi."}
            },
            "required": ["user_identifier"]
        }
    },
    {
        "name": "enable5G",
        "description": "Kullanıcının hattını 5G ağ moduna geçirir (İstanbul, Ankara, İzmir).",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcının kimlik bilgisi."}
            },
            "required": ["user_identifier"]
        }
    },
    {
        "name": "getCallHistory",
        "description": "Kullanıcının son 5 çağrı kaydını döner.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcının kimlik bilgisi."}
            },
            "required": ["user_identifier"]
        }
    },
    {
        "name": "getSupportTicketStatus",
        "description": "Kullanıcının son teknik destek randevusunun durumunu döner.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcının kimlik bilgisi."}
            },
            "required": ["user_identifier"]
        }
    },
    {
        "name": "checkServiceStatus",
        "description": "Kullanıcının hizmet durumunu kontrol eder.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcının kimlik bilgisi."}
            },
            "required": ["user_identifier"]
        }
    },
    {
        "name": "addAuthorizedContact",
        "description": "Kullanıcının hesabına yetkili kişi ekler.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcının kimlik bilgisi."},
                "name": {"type": "string", "description": "Yetkili kişi adı."},
                "phone": {"type": "string", "description": "Yetkili kişi telefonu."}
            },
            "required": ["user_identifier", "name", "phone"]
        }
    },
    {
        "name": "requestNumberPorting",
        "description": "Numara taşıma başvurusu oluşturur.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcının kimlik bilgisi."},
                "current_operator": {"type": "string", "description": "Mevcut operatör."},
                "reason": {"type": "string", "description": "Gerekçe."}
            },
            "required": ["user_identifier", "current_operator", "reason"]
        }
    },
    {
        "name": "requestNumberChange",
        "description": "Mevcut hattın telefon numarasını değiştirir.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcının kimlik bilgisi."},
                "reason": {"type": "string", "description": "Gerekçe."}
            },
            "required": ["user_identifier", "reason"]
        }
    },
    {
        "name": "pausePackageTemporarily",
        "description": "Mevcut paketi geçici olarak askıya alır.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcının kimlik bilgisi."},
                "duration_days": {"type": "integer", "description": "Gün cinsinden süre."},
                "reason": {"type": "string", "description": "Gerekçe."}
            },
            "required": ["user_identifier", "duration_days", "reason"]
        }
    },
    {
        "name": "activateInternationalRoaming",
        "description": "Uluslararası dolaşımı aktif eder.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcının kimlik bilgisi."}
            },
            "required": ["user_identifier"]
        }
    },
    {
        "name": "sendGiftPackage",
        "description": "Hediye internet paketi gönderir (ücret göndericinin faturasına eklenir).",
        "parameters": {
            "type": "object",
            "properties": {
                "sender_id": {"type": "string", "description": "Gönderen kimliği."},
                "receiver_number": {"type": "string", "description": "Alıcı telefon numarası."},
                "package_type": {"type": "string", "description": "Şu an yalnızca 'internet'."},
                "amount": {"type": "integer", "description": "GB miktarı (maks. 10)."}
            },
            "required": ["sender_id", "receiver_number", "package_type", "amount"]
        }
    },
    {
        "name": "getReceivedGifts",
        "description": "Kullanıcının aldığı hediye paketleri döner.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcının kimlik bilgisi."}
            },
            "required": ["user_identifier"]
        }
    },
    {
        "name": "requestInstallmentPlan",
        "description": "Toplam tutarı belirtilen taksite böler.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcının kimlik bilgisi."},
                "total_amount": {"type": "number", "description": "Toplam tutar."},
                "installments": {"type": "integer", "description": "Taksit sayısı."}
            },
            "required": ["user_identifier", "total_amount", "installments"]
        }
    },
    {
        "name": "checkInfrastructure",
        "description": "Adreste hangi altyapıların mevcut olduğunu kontrol eder.",
        "parameters": {
            "type": "object",
            "properties": {
                "address": {"type": "string", "description": "Açık adres."}
            },
            "required": ["address"]
        }
    },
    {
        "name": "scheduleInternetRelocation",
        "description": "İnternet hizmetini yeni adrese taşıma talebini kaydeder.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcının kimlik bilgisi."},
                "new_address": {
                    "type": "object",
                    "description": "Yeni adres bilgileri.",
                    "properties": {
                        "street": {"type": "string", "description": "Sokak."},
                        "city": {"type": "string", "description": "Şehir."},
                        "zip_code": {"type": "string", "description": "Posta kodu."}
                    },
                    "required": ["street", "city", "zip_code"]
                }
            },
            "required": ["user_identifier", "new_address"]
        }
    },
    {
        "name": "checkContractEndDate",
        "description": "Mevcut taahhüt bitiş tarihi ve kalan gün sayısını döner.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcının kimlik bilgisi."}
            },
            "required": ["user_identifier"]
        }
    },
    {
        "name": "freezeLine",
        "description": "Kullanıcının hattını geçici olarak dondurur.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcının kimlik bilgisi."},
                "reason": {"type": "string", "description": "Gerekçe."}
            },
            "required": ["user_identifier"]
        }
    },
    {
        "name": "activateLine",
        "description": "Pasif hattı yeniden aktif eder.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcının kimlik bilgisi."}
            },
            "required": ["user_identifier"]
        }
    },
    {
        "name": "deleteSubscription",
        "description": "Kullanıcının mevcut aboneliğini iptal eder ve hizmet durumunu pasife alır.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcının kimlik bilgisi."},
                "reason": {"type": "string", "description": "Gerekçe."}
            },
            "required": ["user_identifier", "reason"]
        }
    }
]
