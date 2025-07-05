
# ...existing code...

import os
import json
from datetime import datetime, timedelta
import random
import logging
from typing import Dict, Any, List

from mockApis  import (
    getUserInfo,
    getAvailablePackages,
    checkServiceAvailability,
    scheduleTechnicalSupport,
    getUsageHistory,
    blockIncomingNumber,
    unblockIncomingNumber,
    activateEsim,
    suspendLineDueToLoss,
    deactivateEsim,
    removeDataRestriction,
    activateChildProfile,
    deactivateChildProfile,
    enable5G,
    getCallHistory,
    getSupportTicketStatus,
    checkServiceStatus,
    addAuthorizedContact,
    requestNumberPorting,
    requestNumberChange,
    pausePackageTemporarily,
    activateInternationalRoaming,
    sendGiftPackage,
    getReceivedGifts,
    requestInstallmentPlan,
    checkInfrastructure,
    scheduleInternetRelocation,
    checkContractEndDate
)


USER_DB = os.path.join(os.path.dirname(__file__), 'user.json')
PACKAGE_DB = os.path.join(os.path.dirname(__file__), 'packages.json')

def _load_users():
    with open(USER_DB, encoding='utf-8') as f:
        return json.load(f)

def _save_users(users):
    with open(USER_DB, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def _load_packages():
    with open(PACKAGE_DB, encoding='utf-8') as f:
        return json.load(f)

def _find_user(identifier):
    users = _load_users()
    for u in users:
        # TC kimlik numarası ile arama
        if u.get('tc_no') == identifier:
            return u
        # Müşteri ID ile arama
        if u.get('customer_id') == identifier:
            return u
        # Telefon numarası ile arama (tüm tire ve boşlukları kaldır)
        if u.get('phone_number', '').replace('-', '').replace(' ', '') == identifier.replace('-', '').replace(' ', ''):
            return u
    return None

# ...existing code...

logger = logging.getLogger(__name__)
# OpenAI fonksiyon şemaları
openai_function_schemas = [
    # getUserInfo
    {
        "name": "getUserInfo",
        "description": "Kullanıcı kimlik doğrulama için TC kimlik numarası ile kullanıcı bilgilerini getirir.",
        "parameters": {
            "type": "object",
            "properties": {
                "tc_no": {"type": "string", "description": "TC kimlik numarası"}
            },
            "required": ["tc_no"]
        }
    },
    # getAvailablePackages
    {
        "name": "getAvailablePackages",
        "description": "Kullanıcıya uygun paketleri listeler.",
        "parameters": {
            "type": "object",
            "properties": {
                "tc_no": {"type": "string", "description": "TC kimlik numarası"},
                "category": {"type": "string", "description": "Paket kategorisi (isteğe bağlı)"},
                "min_speed": {"type": "integer", "description": "Minimum hız (isteğe bağlı)"},
                "has_fiber_infra_check": {"type": "boolean", "description": "Fiber altyapı kontrolü (isteğe bağlı)"}
            },
            "required": ["tc_no"]
        }
    },
    # initiatePackageChange
    {
        "name": "initiatePackageChange",
        "description": "Kullanıcının paketini değiştirir (onay gerektirir).",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcı ID veya telefon numarası"},
                "package_id": {"type": "string", "description": "Yeni paket ID"},
                "confirmation": {"type": "boolean", "description": "Kullanıcı onayı (zorunlu)"}
            },
            "required": ["user_identifier", "package_id", "confirmation"]
        }
    },
    # getBillDetails
    {
        "name": "getBillDetails",
        "description": "Kullanıcının fatura detaylarını ve ödeme geçmişini getirir.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcı ID veya telefon numarası"},
                "bill_id": {"type": "string", "description": "Fatura ID (isteğe bağlı)"},
                "period": {"type": "string", "description": "Fatura dönemi (son/tümü/ay) (isteğe bağlı)"}
            },
            "required": ["user_identifier"]
        }
    },
    # submitComplaint
    {
        "name": "submitComplaint",
        "description": "Kullanıcının şikayetini kaydeder.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcı ID veya telefon numarası"},
                "complaint_type": {"type": "string", "description": "Şikayet türü"},
                "description": {"type": "string", "description": "Şikayet açıklaması"}
            },
            "required": ["user_identifier", "complaint_type", "description"]
        }
    },
    # checkServiceAvailability
    {
        "name": "checkServiceAvailability",
        "description": "Belirtilen adreste hizmet kullanılabilirliğini kontrol eder.",
        "parameters": {
            "type": "object",
            "properties": {
                "address_street": {"type": "string", "description": "Sokak adı"},
                "address_city": {"type": "string", "description": "Şehir adı"},
                "address_zip_code": {"type": "string", "description": "Posta kodu"},
                "user_identifier": {"type": "string", "description": "Kullanıcı ID veya telefon numarası (isteğe bağlı)"},
                "service_type": {"type": "string", "description": "Hizmet türü (Fiber İnternet/ADSL/Mobil Kapsama)"}
            },
            "required": []
        }
    },
    # scheduleTechnicalSupport
    {
        "name": "scheduleTechnicalSupport",
        "description": "Teknik destek randevusu oluşturur.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcı ID veya telefon numarası"},
                "issue_description": {"type": "string", "description": "Sorun açıklaması"},
                "preferred_date": {"type": "string", "description": "Tercih edilen tarih (YYYY-MM-DD)"},
                "preferred_time": {"type": "string", "description": "Tercih edilen saat (HH:MM)"}
            },
            "required": ["user_identifier", "issue_description", "preferred_date", "preferred_time"]
        }
    },
    # cancelSubscription
    {
        "name": "cancelSubscription",
        "description": "Kullanıcının aboneliğini iptal eder.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcı ID veya telefon numarası"},
                "reason": {"type": "string", "description": "İptal nedeni"}
            },
            "required": ["user_identifier", "reason"]
        }
    },
    # getUsageHistory
    {
        "name": "getUsageHistory",
        "description": "Kullanım geçmişini döndürür.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcı ID veya telefon numarası"},
                "period": {"type": "string", "description": "Dönem (isteğe bağlı)"}
            },
            "required": ["user_identifier"]
        }
    },
    # blockIncomingNumber
    {
        "name": "blockIncomingNumber",
        "description": "Numara engelleme.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcı ID veya telefon numarası"},
                "target_number": {"type": "string", "description": "Engellenecek numara"}
            },
            "required": ["user_identifier", "target_number"]
        }
    },
    # unblockIncomingNumber
    {
        "name": "unblockIncomingNumber",
        "description": "Numara engelini kaldırma.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcı ID veya telefon numarası"},
                "target_number": {"type": "string", "description": "Engeli kaldırılacak numara"}
            },
            "required": ["user_identifier", "target_number"]
        }
    },
    # activateEsim
    {
        "name": "activateEsim",
        "description": "eSIM aktivasyonu.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcı ID veya telefon numarası"}
            },
            "required": ["user_identifier"]
        }
    },
    # suspendLineDueToLoss
    {
        "name": "suspendLineDueToLoss",
        "description": "Hattı kayıp/çalıntı nedeniyle askıya alır.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcı ID veya telefon numarası"},
                "reason": {"type": "string", "description": "Sebep (kayip/çalinti)"}
            },
            "required": ["user_identifier", "reason"]
        }
    },
    # deactivateEsim
    {
        "name": "deactivateEsim",
        "description": "eSIM devre dışı bırakma.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcı ID veya telefon numarası"}
            },
            "required": ["user_identifier"]
        }
    },
    # removeDataRestriction
    {
        "name": "removeDataRestriction",
        "description": "Veri kısıtlamasını kaldırır.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcı ID veya telefon numarası"}
            },
            "required": ["user_identifier"]
        }
    },
    # activateChildProfile
    {
        "name": "activateChildProfile",
        "description": "Çocuk modunu aktif eder.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcı ID veya telefon numarası"}
            },
            "required": ["user_identifier"]
        }
    },
    # deactivateChildProfile
    {
        "name": "deactivateChildProfile",
        "description": "Çocuk profilini devre dışı bırakır.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcı ID veya telefon numarası"}
            },
            "required": ["user_identifier"]
        }
    },
    # enable5G
    {
        "name": "enable5G",
        "description": "5G'yi aktif eder.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcı ID veya telefon numarası"}
            },
            "required": ["user_identifier"]
        }
    },
    # getCallHistory
    {
        "name": "getCallHistory",
        "description": "Çağrı geçmişini döndürür.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcı ID veya telefon numarası"}
            },
            "required": ["user_identifier"]
        }
    },
    # getSupportTicketStatus
    {
        "name": "getSupportTicketStatus",
        "description": "Destek kaydı durumunu döndürür.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcı ID veya telefon numarası"}
            },
            "required": ["user_identifier"]
        }
    },
    # checkServiceStatus
    {
        "name": "checkServiceStatus",
        "description": "Hizmet durumunu kontrol eder.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcı ID veya telefon numarası"}
            },
            "required": ["user_identifier"]
        }
    },
    # addAuthorizedContact
    {
        "name": "addAuthorizedContact",
        "description": "Yetkili kişi ekler.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcı ID veya telefon numarası"},
                "name": {"type": "string", "description": "Yetkili kişi adı"},
                "phone": {"type": "string", "description": "Yetkili kişi telefon numarası"}
            },
            "required": ["user_identifier", "name", "phone"]
        }
    },
    # requestNumberPorting
    {
        "name": "requestNumberPorting",
        "description": "Numara taşıma talebi oluşturur.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcı ID veya telefon numarası"},
                "current_operator": {"type": "string", "description": "Mevcut operatör"},
                "reason": {"type": "string", "description": "Taşıma nedeni"}
            },
            "required": ["user_identifier", "current_operator", "reason"]
        }
    },
    # requestNumberChange
    {
        "name": "requestNumberChange",
        "description": "Numara değişikliği talebi.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcı ID veya telefon numarası"},
                "reason": {"type": "string", "description": "Değişiklik nedeni"}
            },
            "required": ["user_identifier", "reason"]
        }
    },
    # pausePackageTemporarily
    {
        "name": "pausePackageTemporarily",
        "description": "Paketi geçici olarak duraklatır.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcı ID veya telefon numarası"},
                "duration_days": {"type": "integer", "description": "Duraklatma süresi (gün)"},
                "reason": {"type": "string", "description": "Duraklatma nedeni"}
            },
            "required": ["user_identifier", "duration_days", "reason"]
        }
    },
    # activateInternationalRoaming
    {
        "name": "activateInternationalRoaming",
        "description": "Yurt dışı kullanımını aktif eder.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcı ID veya telefon numarası"},
                "countries": {"type": "array", "items": {"type": "string"}, "description": "Ülkeler listesi"}
            },
            "required": ["user_identifier", "countries"]
        }
    },
    # sendGiftPackage
    {
        "name": "sendGiftPackage",
        "description": "Hediye paket gönderir.",
        "parameters": {
            "type": "object",
            "properties": {
                "sender_id": {"type": "string", "description": "Gönderen kullanıcı ID"},
                "receiver_number": {"type": "string", "description": "Alıcı telefon numarası"},
                "package_type": {"type": "string", "description": "Paket türü (internet)"},
                "amount": {"type": "integer", "description": "Miktar (GB)"}
            },
            "required": ["sender_id", "receiver_number", "package_type", "amount"]
        }
    },
    # getReceivedGifts
    {
        "name": "getReceivedGifts",
        "description": "Alınan hediyeleri listeler.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcı ID veya telefon numarası"}
            },
            "required": ["user_identifier"]
        }
    },
    # requestInstallmentPlan
    {
        "name": "requestInstallmentPlan",
        "description": "Taksitli ödeme planı oluşturur.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcı ID veya telefon numarası"},
                "total_amount": {"type": "number", "description": "Toplam tutar"},
                "installments": {"type": "integer", "description": "Taksit sayısı"}
            },
            "required": ["user_identifier", "total_amount", "installments"]
        }
    },
    # checkInfrastructure
    {
        "name": "checkInfrastructure",
        "description": "Altyapı durumunu kontrol eder.",
        "parameters": {
            "type": "object",
            "properties": {
                "address": {"type": "string", "description": "Adres"}
            },
            "required": ["address"]
        }
    },
    # scheduleInternetRelocation
    {
        "name": "scheduleInternetRelocation",
        "description": "İnternet hizmetini taşır.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcı ID veya telefon numarası"},
                "new_address": {"type": "object", "description": "Yeni adres (street, city, zip_code)", "properties": {
                    "street": {"type": "string"},
                    "city": {"type": "string"},
                    "zip_code": {"type": "string"}
                }, "required": ["street", "city", "zip_code"]}
            },
            "required": ["user_identifier", "new_address"]
        }
    },
    # checkContractEndDate
    {
        "name": "checkContractEndDate",
        "description": "Taahhüt bitiş tarihini kontrol eder.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_identifier": {"type": "string", "description": "Kullanıcı ID veya telefon numarası"}
            },
            "required": ["user_identifier"]
        }
    }
]


function_map = {
    "getUserInfo": getUserInfo,
    "getAvailablePackages": getAvailablePackages,
    "checkServiceAvailability": checkServiceAvailability,
    "scheduleTechnicalSupport": scheduleTechnicalSupport,
    "getUsageHistory": getUsageHistory,
    "blockIncomingNumber": blockIncomingNumber,
    "unblockIncomingNumber": unblockIncomingNumber,
    "activateEsim": activateEsim,
    "suspendLineDueToLoss": suspendLineDueToLoss,
    "deactivateEsim": deactivateEsim,
    "removeDataRestriction": removeDataRestriction,
    "activateChildProfile": activateChildProfile,
    "deactivateChildProfile": deactivateChildProfile,
    "enable5G": enable5G,
    "getCallHistory": getCallHistory,
    "getSupportTicketStatus": getSupportTicketStatus,
    "checkServiceStatus": checkServiceStatus,
    "addAuthorizedContact": addAuthorizedContact,
    "requestNumberPorting": requestNumberPorting,
    "requestNumberChange": requestNumberChange,
    "pausePackageTemporarily": pausePackageTemporarily,
    "activateInternationalRoaming": activateInternationalRoaming,
    "sendGiftPackage": sendGiftPackage,
    "getReceivedGifts": getReceivedGifts,
    "requestInstallmentPlan": requestInstallmentPlan,
    "checkInfrastructure": checkInfrastructure,
    "scheduleInternetRelocation": scheduleInternetRelocation,
    "checkContractEndDate": checkContractEndDate
}

