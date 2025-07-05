# --- Gerekli Modüller ---
import json
import random
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


USER_DB = os.path.join(os.path.dirname(__file__), 'user.json')

def _load_users():
    with open(USER_DB, encoding='utf-8') as f:
        return json.load(f)

def _save_users(users):
    with open(USER_DB, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

PACKAGE_DB = os.path.join(os.path.dirname(__file__), 'packages.json')

def _load_packages():
    with open(PACKAGE_DB, encoding='utf-8') as f:
        return json.load(f)


def getUserInfo(tc_no: str):
    print(f"getUserInfo çağrıldı: {tc_no}")
    user = _find_user(tc_no)
    print(f"getUserInfo user: {user}")
    if not user:
        return {"success": False, "error": "Kullanıcı bulunamadı."}
    # Sadece temel bilgileri döndür (güvenlik için)
    data = {
        "tc_no": user.get("tc_no"),
        "name": user.get("name"),
        "current_package": user.get("current_package"),
        "contract_end_date": user.get("contract_end_date")
    }
    return {"success": True, "data": data}


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

def getAvailablePackages(user_identifier: str) -> dict:
    logger.info(f"[MOCK API] getAvailablePackages (sadece birebir occupation eşleşmesi) çağrıldı. user_identifier: {user_identifier}")

    users = _load_users()
    packages = _load_packages()

    customer = next((user for user in users if
        user.get("tc_no") == user_identifier
        or user.get("customer_id") == user_identifier
        or user.get("phone_number", "").replace("-", "").replace(" ", "") == user_identifier.replace("-", "").replace(" ", "")
    ), None)

    if not customer:
        return {"success": False, "error": "Kullanıcı bulunamadı. Paket önerisi yapılamadı."}

    current_package = customer.get("current_package", "")
    occupation = customer.get("occupation", "").strip().lower()

    eligible_packages = []

    for pkg in packages:
        pkg_name = pkg.get("name", "")
        allowed_groups = [grp.lower() for grp in pkg.get("allowed_groups", ["genel"])]

        # Sadece occupation değeriyle birebir eşleşen paketler
        if occupation not in allowed_groups:
            continue

        # Kullanıcının zaten kullandığı paketi çıkar
        if pkg_name == current_package:
            continue

        eligible_packages.append(pkg)

    if not eligible_packages:
        return {
            "success": True,
            "data": [],
            "message": f"{occupation} grubuna özel paket bulunamadı."
        }

    return {
        "success": True,
        "data": eligible_packages,
        "message": f"{occupation} grubuna özel {len(eligible_packages)} paket bulundu."
    }

def initiatePackageChange(user_identifier: str, new_package_name: str) -> dict:
    """
    Kullanıcının mevcut paketini değiştirir. Sadece 'current_package' alanı güncellenir.
    """
    users = _load_users()
    updated = False

    for user in users:
        if (
            user.get("tc_no") == user_identifier
            or user.get("customer_id") == user_identifier
            or user.get("phone_number", "").replace("-", "").replace(" ", "") == user_identifier.replace("-", "").replace(" ", "")
        ):
            old_package = user.get("current_package", "belirtilmemiş")
            user["current_package"] = new_package_name
            updated = True
            break

    if not updated:
        return {"success": False, "message": "Kullanıcı bulunamadı. Paket güncellenemedi."}

    _save_users(users)
    return {
        "success": True,
        "message": f"Mevcut paket başarıyla güncellendi: {old_package} → {new_package_name}",
        "new_package": new_package_name
    }

from datetime import datetime
def getBillDetails(user_identifier: str, bill_id: str = None, period: str = None) -> dict:
    users = _load_users()

    # Kullanıcıyı bul
    customer = next((user for user in users if
        user.get("tc_no") == user_identifier
        or user.get("customer_id") == user_identifier
        or user.get("phone_number", "").replace("-", "").replace(" ", "") == user_identifier.replace("-", "").replace(" ", "")
    ), None)

    if not customer:
        return {"success": False, "error": "Kullanıcı bulunamadı. Lütfen geçerli bir kimlik bilgisi girin."}

    bills = customer.get("bills", [])
    if not bills:
        return {"success": False, "error": "Bu kullanıcıya ait hiç fatura kaydı bulunmamaktadır."}

    # Belirli bir fatura ID'si istenmişse
    if bill_id:
        bill = next((b for b in bills if b.get("bill_id") == bill_id), None)
        if bill:
            return {
                "success": True,
                "data": bill,
                "message": f"'{bill_id}' ID'li fatura başarıyla bulundu."
            }
        else:
            return {
                "success": False,
                "error": f"'{bill_id}' ID'li bir fatura bulunamadı."
            }

    # En son fatura istenmişse
    if period == "son":
        try:
            latest = max(bills, key=lambda b: datetime.strptime(b["bill_date"], "%Y-%m-%d"))
            return {
                "success": True,
                "data": latest,
                "message": "En son fatura başarıyla getirildi."
            }
        except Exception as e:
            return {"success": False, "error": f"Tarih formatında sorun var: {e}"}

    # Tüm faturalar istenmişse
    if period == "tümü":
        return {
            "success": True,
            "data": bills,
            "message": "Tüm faturalar başarıyla listelendi."
        }

    # Hiç parametre verilmemişse: tüm faturaları getir
    if not bill_id and not period:
        return {
            "success": True,
            "data": bills,
            "message": "Varsayılan olarak tüm faturalar getirildi."
        }

    # Geçersiz parametre durumu
    return {
        "success": False,
        "error": "Geçersiz parametre girdiniz. Lütfen 'bill_id', 'period=\"son\"' veya 'period=\"tümü\"' şeklinde deneyin."
    }

def checkServiceAvailability(address_street: str = None, address_city: str = None, address_zip_code: str = None, user_identifier: str = None, service_type: str = "Fiber İnternet"):
    return {"success": True, "available": True, "message": "Adresinizde hizmet mevcut (örnek)."}

def scheduleTechnicalSupport(user_identifier: str, issue_description: str, preferred_date: str, preferred_time: str) -> dict:
    users = _load_users()
    updated = False

    try:
        req_datetime = datetime.strptime(f"{preferred_date} {preferred_time}", "%Y-%m-%d %H:%M")
        if req_datetime < datetime.now():
            return {"success": False, "error": "Geçmiş tarihe randevu alınamaz."}
        if req_datetime.weekday() >= 5 or not (9 <= req_datetime.hour < 17):
            return {"success": False, "error": "Randevular sadece hafta içi 09:00–17:00 arasında alınabilir."}
    except ValueError:
        return {"success": False, "error": "Tarih/saat formatı geçersiz. YYYY-MM-DD ve HH:MM olmalı."}

    for user in users:
        if (
            user.get("tc_no") == user_identifier
            or user.get("customer_id") == user_identifier
            or user.get("phone_number", "").replace("-", "").replace(" ", "") == user_identifier.replace("-", "").replace(" ", "")
        ):
            appointments = user.setdefault("appointments", [])
            for app in appointments:
                if app["date"] == preferred_date and app["time"] == preferred_time:
                    return {"success": False, "error": "Bu tarih ve saat için zaten bir randevunuz var."}

            appointment_id = f"destek-{random.randint(10,100)}"
            new_appointment = {
                "appointment_id": appointment_id,
                "issue": issue_description,
                "date": preferred_date,
                "time": preferred_time,
                "status": "Planlandı",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "active": True
            }
            appointments.append(new_appointment)
            updated = True
            break

    if updated:
        _save_users(users)
        return {
            "success": True,
            "message": f"Randevunuz oluşturuldu. Takip numaranız: {appointment_id}",
            "appointment": new_appointment
        }
    else:
        return {"success": False, "error": "Kullanıcı bulunamadı. Randevu oluşturulamadı."}

def cancelSubscription(user_identifier: str, reason: str) -> dict:
    users = _load_users()
    for user in users:
        if (
            user.get("tc_no") == user_identifier
            or user.get("customer_id") == user_identifier
            or user.get("phone_number", "").replace("-", "").replace(" ", "") == user_identifier.replace("-", "").replace(" ", "")
        ):
            # Tarife bilgilerini sil
            user.pop("current_package", None)
            user.pop("package_start_date", None)
            user.pop("package_end_date", None)
            user.pop("remaining_data", None)
            user.pop("remaining_minutes", None)
            user.pop("remaining_sms", None)

            # Diğer durumu güncelle
            user["status"] = "pasif"
            user["service_status"] = "Abonelik iptal edildi"
            user["cancellation_reason"] = reason
            user["cancellation_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            _save_users(users)
            return {
                "success": True,
                "message": f"Aboneliğiniz '{reason}' nedeniyle iptal edildi. Tarifeye dair tüm bilgiler silindi."
            }

    return {
        "success": False,
        "message": "Kullanıcı bulunamadı. Abonelik iptali yapılamadı."
    }

def getUsageHistory(user_identifier: str, period: str = "Son 3 Ay") -> dict:
    """Kullanıcının kullanım geçmişini getirir."""
    logger.info(f"[MOCK API] getUsageHistory çağrıldı. user_identifier: {user_identifier}, period: {period}")

    users = _load_users()

    customer = next((user for user in users if
        user.get("tc_no") == user_identifier
        or user.get("customer_id") == user_identifier
        or user.get("phone_number", "").replace("-", "").replace(" ", "") == user_identifier.replace("-", "").replace(" ", "")
    ), None)

    if not customer:
        return {"success": False, "error": "Kullanıcı bulunamadı. Kullanım geçmişi alınamadı."}

    usage_data = customer.get("usage_history", {})

    if usage_data:
        return {
            "success": True,
            "data": usage_data,
            "message": f"{customer['name']} için kullanım geçmişi başarıyla getirildi."
        }
    else:
        return {
            "success": True,
            "data": {},
            "message": f"{customer['name']} adlı kullanıcıya ait kullanım geçmişi bulunamadı."
        }

def blockIncomingNumber(user_identifier: str, target_number: str):
    users = _load_users()
    updated = False
    cleaned_number = target_number.replace(" ", "").replace("-", "")

    if not cleaned_number.isdigit() or len(cleaned_number) != 11 or not cleaned_number.startswith("05"):
        return {"success": False, "error": "Geçersiz numara formatı. 05XXXXXXXXX biçiminde girin."}

    for user in users:
        if (
            user.get('tc_no') == user_identifier
            or user.get('customer_id') == user_identifier
            or user.get('phone_number', '').replace('-', '').replace(' ', '') == user_identifier.replace('-', '').replace(' ', '')
        ):
            if "blocked_numbers" not in user:
                user["blocked_numbers"] = []

            if cleaned_number in user["blocked_numbers"]:
                return {"success": False, "error": "Bu numara zaten engellenmiş."}

            user["blocked_numbers"].append(cleaned_number)
            updated = True
            break

    if updated:
        _save_users(users)
        return {"success": True, "message": f"{cleaned_number} başarıyla engellendi."}
    else:
        return {"success": False, "error": "Kullanıcı bulunamadı."}

def unblockIncomingNumber(user_identifier: str, target_number: str) -> dict:
    users = _load_users()
    cleaned_number = target_number.replace(" ", "").replace("-", "")
    updated = False

    if len(cleaned_number) != 11 or not cleaned_number.startswith("05"):
        return {"success": False, "error": "Geçersiz numara formatı. Lütfen 05XXXXXXXXX biçiminde giriniz."}

    for user in users:
        if (
            user.get('tc_no') == user_identifier
            or user.get('customer_id') == user_identifier
            or user.get('phone_number', '').replace('-', '').replace(' ', '') == user_identifier.replace('-', '').replace(' ', '')
        ):
            if "blocked_numbers" not in user or cleaned_number not in user["blocked_numbers"]:
                return {"success": False, "error": "Bu numara engellenmişler listesinde bulunmuyor."}

            user["blocked_numbers"].remove(cleaned_number)
            updated = True
            break

    if updated:
        _save_users(users)
        return {"success": True, "message": f"{cleaned_number} numarasının engeli başarıyla kaldırıldı."}
    else:
        return {"success": False, "error": "Kullanıcı bulunamadı. Engel kaldırılamadı."}

def activateEsim(user_identifier: str):
    users = _load_users()
    updated = False
    for user in users:
        if (
            user.get('tc_no') == user_identifier
            or user.get('customer_id') == user_identifier
            or user.get('phone_number', '').replace('-', '').replace(' ', '') == user_identifier.replace('-', '').replace(' ', '')
        ):
            if user.get('esim_active'):
                return {"success": False, "message": "eSIM zaten aktif durumda."}
            user['esim_active'] = True
            updated = True
            break
    if updated:
        _save_users(users)
        return {"success": True, "message": "eSIM aktivasyonu başarılı ve veritabanı güncellendi."}
    else:
        return {"success": False, "message": "Kullanıcı bulunamadı."}

def suspendLineDueToLoss(user_identifier: str, reason: str):
    users = _load_users()
    for user in users:
        if (
            user.get('tc_no') == user_identifier
            or user.get('customer_id') == user_identifier
            or user.get('phone_number', '').replace('-', '').replace(' ', '') == user_identifier.replace('-', '').replace(' ', '')
        ):
            user['status'] = 'pasif'
            user['service_status'] = 'Askıya Alındı'
            _save_users(users)
            return {"success": True, "message": f"Hattınız başarıyla {reason} sebebiyle askıya alındı ve veritabanı güncellendi."}
    return {"success": False, "message": "Kullanıcı bulunamadı. Hat askıya alınamadı."}

def deactivateEsim(user_identifier: str):
    users = _load_users()
    updated = False
    for user in users:
        if (
            user.get('tc_no') == user_identifier
            or user.get('customer_id') == user_identifier
            or user.get('phone_number', '').replace('-', '').replace(' ', '') == user_identifier.replace('-', '').replace(' ', '')
        ):
            if not user.get('esim_active'):
                return {"success": False, "message": "eSIM zaten devre dışı durumda."}
            user['esim_active'] = False
            updated = True
            break
    if updated:
        _save_users(users)
        return {"success": True, "message": "eSIM devre dışı bırakıldı ve veritabanı güncellendi."}
    else:
        return {"success": False, "message": "Kullanıcı bulunamadı."}

def removeDataRestriction(user_identifier: str) -> dict:
    users = _load_users()
    updated = False

    for user in users:
        if (
            user.get("tc_no") == user_identifier
            or user.get("customer_id") == user_identifier
            or user.get("phone_number", "").replace("-", "").replace(" ", "") == user_identifier.replace("-", "").replace(" ", "")
        ):
            if not user.get("roaming_restricted", False):
                return {"success": False, "message": "Hattınızda aktif bir veri kısıtlaması bulunmamaktadır."}
            user["roaming_restricted"] = False
            updated = True
            break

    if updated:
        _save_users(users)
        return {
            "success": True,
            "message": "Yurt dışı veri kısıtlaması başarıyla kaldırıldı. Artık hattınızı tam kapasiteyle kullanabilirsiniz."
        }
    else:
        return {"success": False, "message": "Kullanıcı bulunamadı. Kısıtlama kaldırma işlemi yapılamadı."}

def activateChildProfile(user_identifier: str):
    users = _load_users()
    for user in users:
        if (
            user.get('tc_no') == user_identifier
            or user.get('customer_id') == user_identifier
            or user.get('phone_number', '').replace('-', '').replace(' ', '') == user_identifier.replace('-', '').replace(' ', '')
        ):
            if user.get('child_mode_enabled') == True:
                return {"success": True, "message": "Çocuk profili zaten aktif."}
            user['child_mode_enabled'] = True
            _save_users(users)
            return {"success": True, "message": "Çocuk profili başarıyla aktif edildi ve veritabanı güncellendi."}
    return {"success": False, "message": "Kullanıcı bulunamadı. Çocuk profili aktif edilemedi."}

def deactivateChildProfile(user_identifier: str):
    users = _load_users()
    for user in users:
        if (
            user.get('tc_no') == user_identifier
            or user.get('customer_id') == user_identifier
            or user.get('phone_number', '').replace('-', '').replace(' ', '') == user_identifier.replace('-', '').replace(' ', '')
        ):
            if user.get('child_mode_enabled') == False:
                return {"success": True, "message": "Çocuk profili zaten devre dışı."}
            user['child_mode_enabled'] = False
            _save_users(users)
            return {"success": True, "message": "Çocuk profili başarıyla devre dışı bırakıldı ve veritabanı güncellendi."}
    return {"success": False, "message": "Kullanıcı bulunamadı. Çocuk profili devre dışı bırakılamadı."}

def enable5G(user_identifier: str) -> dict:
    users = _load_users()
    updated = False

    for user in users:
        if (
            user.get("tc_no") == user_identifier
            or user.get("customer_id") == user_identifier
            or user.get("phone_number", "").replace("-", "").replace(" ", "") == user_identifier.replace("-", "").replace(" ", "")
        ):
            if user.get("network_mode") == "5G":
                return {"success": False, "message": "Zaten 5G ağına tanımlısınız."}
            
            # İsteğe bağlı bölge kontrolü
            city = user.get("address", {}).get("city", "").lower()
            if city not in ["ankara", "izmir", "istanbul"]:
                return {"success": False, "message": f"{city.title()} bölgesinde şu anda 5G altyapısı bulunmamaktadır."}

            user["network_mode"] = "5G"
            updated = True
            break

    if updated:
        _save_users(users)
        return {"success": True, "message": "5G ağ profiliniz başarıyla aktif edildi. Artık 5G hızında bağlantı kullanabilirsiniz."}
    else:
        return {"success": False, "message": "Kullanıcı bulunamadı. 5G aktivasyonu yapılamadı."}

import random
from datetime import datetime, timedelta

def getCallHistory(user_identifier: str) -> dict:
    users = _load_users()
    for user in users:
        if (
            user.get("tc_no") == user_identifier
            or user.get("customer_id") == user_identifier
            or user.get("phone_number", "").replace("-", "").replace(" ", "") == user_identifier.replace("-", "").replace(" ", "")
        ):
            name = user.get("name", "Kullanıcı")
            call_types = ["Gelen", "Giden", "Cevapsız"]
            history = []

            for i in range(5):  # 5 kayıt üret
                call = {
                    "type": random.choice(call_types),
                    "number": f"05{random.randint(100000000, 999999999)}",
                    "time": (datetime.now() - timedelta(minutes=random.randint(1, 1440))).strftime("%H:%M")
                }
                history.append(call)

            return {
                "success": True,
                "call_history": history,
                "message": f"{name} için son 5 çağrı kaydı listelendi."
            }

    return {"success": False, "error": "Kullanıcı bulunamadı. Çağrı geçmişi getirilemedi."}

def getSupportTicketStatus(user_identifier: str) -> dict:
    users = _load_users()
    
    for user in users:
        if (
            user.get("tc_no") == user_identifier
            or user.get("customer_id") == user_identifier
            or user.get("phone_number", "").replace("-", "").replace(" ", "") == user_identifier.replace("-", "").replace(" ", "")
        ):
            appointments = user.get("appointments", [])
            if not appointments:
                return {"success": False, "message": "Herhangi bir teknik destek kaydınız bulunmamaktadır."}

            # Tarihe göre en yeni randevuyu bul
            try:
                sorted_appointments = sorted(
                    appointments,
                    key=lambda x: datetime.strptime(f"{x['date']} {x['time']}", "%Y-%m-%d %H:%M"),
                    reverse=True
                )
            except Exception as e:
                return {"success": False, "error": f"Randevu verisi okunamadı: {e}"}

            last = sorted_appointments[0]

            return {
                "success": True,
                "ticket": {
                    "ticket_id": last.get("appointment_id", "destek-XXXX"),
                    "status": last.get("status", "Bilinmiyor"),
                    "created_at": last.get("created_at", ""),
                    "description": last.get("issue", "Belirtilmemiş")
                },
                "message": "Son teknik destek kaydınız aşağıda listelenmiştir."
            }

    return {"success": False, "message": "Kullanıcı bulunamadı. Destek durumu getirilemedi."}


def checkServiceStatus(user_identifier: str):
    return {"success": True, "status": "Aktif", "message": "Hizmet aktif (örnek)"}

def addAuthorizedContact(user_identifier: str, name: str, phone: str) -> dict:
    users = _load_users()
    updated = False

    cleaned_phone = phone.replace(" ", "").replace("-", "")

    for user in users:
        if (
            user.get("tc_no") == user_identifier
            or user.get("customer_id") == user_identifier
            or user.get("phone_number", "").replace("-", "").replace(" ", "") == user_identifier.replace("-", "").replace(" ", "")
        ):
            authorized_list = user.setdefault("authorized_contacts", [])

            for contact in authorized_list:
                if contact["phone"].replace("-", "").replace(" ", "") == cleaned_phone:
                    return {"success": False, "error": f"{phone} numarası zaten yetkili kişiler arasında."}

            authorized_list.append({"name": name, "phone": cleaned_phone})
            updated = True
            break

    if updated:
        _save_users(users)
        return {
            "success": True,
            "message": f"{name} adlı kişi ({cleaned_phone}) başarıyla yetkili olarak eklendi."
        }
    else:
        return {"success": False, "error": "Kullanıcı bulunamadı. Yetkili kişi eklenemedi."}

def requestNumberPorting(user_identifier: str, current_operator: str, reason: str):
    return {"success": True, "message": "Numara taşıma başvurusu alındı (örnek)"}

import random

def _generate_unique_phone(users):
    while True:
        new_num = "05" + "".join([str(random.randint(0, 9)) for _ in range(9)])
        # Aynı numara sistemde varsa tekrar üret
        if not any(user.get("phone_number", "").replace(" ", "").replace("-", "") == new_num for user in users):
            return new_num

def requestNumberChange(user_identifier: str, reason: str) -> dict:
    users = _load_users()
    updated = False

    for user in users:
        if (
            user.get('tc_no') == user_identifier
            or user.get('customer_id') == user_identifier
            or user.get('phone_number', '').replace('-', '').replace(' ', '') == user_identifier.replace('-', '').replace(' ', '')
        ):
            old_number = user.get("phone_number")
            new_number = _generate_unique_phone(users)
            user["phone_number"] = new_number
            user["status"] = "aktif"
            updated = True
            _save_users(users)

            return {
                "success": True,
                "message": f"Numara değişikliği '{reason}' gerekçesiyle başarıyla gerçekleştirildi. Yeni numaranız: {new_number}. Eski numara: {old_number}."
            }

    return {"success": False, "message": "Kullanıcı bulunamadı. Numara değişikliği yapılamadı."}

def pausePackageTemporarily(user_identifier: str, duration_days: int, reason: str):
    return {"success": True, "message": f"Paket {duration_days} gün askıya alındı (örnek)"}

def activateInternationalRoaming(user_identifier: str) -> dict:
    """Kullanıcının yurt dışı kullanımını (roaming) açar."""
    users = _load_users()

    customer = next((user for user in users if
        user.get("tc_no") == user_identifier
        or user.get("customer_id") == user_identifier
        or user.get("phone_number", "").replace("-", "").replace(" ", "") == user_identifier.replace("-", "").replace(" ", "")
    ), None)

    if not customer:
        return {"success": False, "error": "Kullanıcı bulunamadı. Yurt dışı kullanım açılamadı."}

    if customer.get("roaming_restricted") == False:
        return {"success": True, "message": "Yurt dışı kullanım zaten açık."}

    customer["roaming_restricted"] = False
    _save_users(users)

    return {
        "success": True,
        "message": "Yurt dışı kullanım başarıyla açıldı.",
        "roaming_status": "Açık"
    }


def sendGiftPackage(sender_id: str, receiver_number: str, package_type: str, amount: int) -> dict:
    """Var olan faturaya GB ücreti ekleyerek hediye internet gönderir."""
    logger.info(f"[MOCK API] sendGiftPackage çağrıldı. Gönderen: {sender_id}, Alıcı: {receiver_number}, Tür: {package_type}, Miktar: {amount}")

    users = _load_users()

    if package_type.lower() != "internet":
        return {"success": False, "error": "Şu anda yalnızca internet paketi hediye edilebilir."}

    if amount <= 0 or amount > 10:
        return {"success": False, "error": "Gönderim miktarı geçersiz ya da limit üstü (maksimum 10 GB)."}

    # Göndereni bul
    sender = next((user for user in users if
        user.get("tc_no") == sender_id
        or user.get("customer_id") == sender_id
        or user.get("phone_number", "").replace("-", "").replace(" ", "") == sender_id.replace("-", "").replace(" ", "")
    ), None)

    # Alıcıyı bul
    receiver = next((user for user in users if
        user.get("phone_number", "").replace("-", "").replace(" ", "") == receiver_number.replace("-", "").replace(" ", "")
    ), None)

    if not sender:
        return {"success": False, "error": "Gönderen kullanıcı bulunamadı."}
    if not receiver:
        return {"success": False, "error": "Alıcı kullanıcı bulunamadı."}

    gb_price = 50
    total_price = gb_price * amount

    # En güncel fatura: Beklemede veya Gecikmiş olanlardan en son tarihli olan
    bills = sender.get("bills", [])
    editable_bills = [b for b in bills if b.get("status") in ["Beklemede", "Gecikmiş"]]

    if not editable_bills:
        return {"success": False, "error": "Göndericiye ait düzenlenebilir fatura bulunamadı. Fatura olmadan GB gönderimi yapılamaz."}

    latest_bill = max(editable_bills, key=lambda b: datetime.strptime(b.get("bill_date", "1900-01-01"), "%Y-%m-%d"))

    # Amount artırılır
    latest_bill["amount"] = float(latest_bill.get("amount", 0)) + total_price

    # Breakdown güncellenir
    breakdown = latest_bill.setdefault("breakdown", {})
    breakdown["base"] = f"{float(breakdown.get('base', '0').replace(' TL', '')) + total_price:.2f} TL"

    # Details satırı güncellenir
    current_details = latest_bill.get("details", "")
    latest_bill["details"] = f"{current_details} + {amount} GB hediye internet"

    # Alıcıya GB ekle
    receiver.setdefault("usage_history", {})
    receiver["usage_history"]["internet_gb_used_monthly"] = (
        receiver["usage_history"].get("internet_gb_used_monthly", 0) + amount
    )

    _save_users(users)

    return {
        "success": True,
        "message": f"{receiver['name']} adlı kullanıcıya {amount} GB internet gönderildi. Mevcut faturaya {total_price} TL eklendi.",
        "updated_bill": latest_bill
    }

def getReceivedGifts(user_identifier: str):
    return {"success": True, "gifts": [{"type": "internet", "amount": "2GB", "sender": "Bilinmiyor", "date": "2025-07-04"}]}

def requestInstallmentPlan(user_identifier: str, total_amount: float, installments: int):
    return {"success": True, "message": f"{total_amount} TL {installments} taksite bölündü (örnek)"}

def checkInfrastructure(address: str):
    return {"success": True, "infrastructure": "fiber (örnek)"}

def scheduleInternetRelocation(user_identifier: str, new_address: dict) -> dict:
    """
    Kullanıcının internetini yeni bir adrese taşıma talebini işler.
    'address' alanı güncellenir ve 'appointments' listesine kayıt eklenir.
    """
    users = _load_users()
    updated = False

    for user in users:
        if (
            user.get("tc_no") == user_identifier
            or user.get("customer_id") == user_identifier
            or user.get("phone_number", "").replace("-", "").replace(" ", "") == user_identifier.replace("-", "").replace(" ", "")
        ):
            old_address = user.get("address", {})
            user["address"] = new_address

            user.setdefault("appointments", []).append({
                "type": "İnternet Nakil",
                "requested_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "Planlandı",
                "old_address": old_address,
                "new_address": new_address
            })

            updated = True
            break

    if not updated:
        return {"success": False, "message": "Kullanıcı bulunamadı. Taşıma işlemi yapılamadı."}

    _save_users(users)

    return {
        "success": True,
        "message": f"İnternet taşıma işlemi başarıyla kaydedildi. Yeni adres: {new_address['street']}, {new_address['city']} ({new_address['zip_code']})"
    }

def checkContractEndDate(user_identifier: str):
    return {"success": True, "contract_end_date": "2025-12-31", "days_remaining": 180, "message": "Taahhüt bitiş tarihi (örnek)"}


# cancelSubscription fonksiyonu (status: pasif, service_status: İptal Edildi)
def deleteSubscription(user_identifier: str, reason: str):
    users = _load_users()
    for user in users:
        if (
            user.get('tc_no') == user_identifier
            or user.get('customer_id') == user_identifier
            or user.get('phone_number', '').replace('-', '').replace(' ', '') == user_identifier.replace('-', '').replace(' ', '')
        ):
            user['status'] = 'pasif'
            user['service_status'] = 'İptal Edildi'
            _save_users(users)
            return {"success": True, "message": f"Hattınız {reason} nedeniyle başarıyla iptal edildi ve veritabanı güncellendi."}
    return {"success": False, "message": "Kullanıcı bulunamadı. Abonelik iptal edilemedi."}


# Hat dondurma fonksiyonu (status: pasif)
def freezeLine(user_identifier: str, reason: str = "Kullanıcı talebiyle donduruldu"):
    users = _load_users()
    for user in users:
        if (
            user.get('tc_no') == user_identifier
            or user.get('customer_id') == user_identifier
            or user.get('phone_number', '').replace('-', '').replace(' ', '') == user_identifier.replace('-', '').replace(' ', '')
        ):
            if user.get('status') == 'pasif':
                return {"success": True, "message": "Hattınız zaten pasif durumda."}
            user['status'] = 'pasif'
            _save_users(users)
            return {"success": True, "message": f"Hattınız başarıyla donduruldu ve pasif moda alındı. ({reason})"}
    return {"success": False, "message": "Kullanıcı bulunamadı. Hat dondurulamadı."}


def activateLine(user_identifier: str):
    users = _load_users()
    for user in users:
        if (
            user.get('tc_no') == user_identifier
            or user.get('customer_id') == user_identifier
            or user.get('phone_number', '').replace('-', '').replace(' ', '') == user_identifier.replace('-', '').replace(' ', '')
        ):
            if user.get('status') == 'aktif' and user.get('service_status', '').lower() == 'aktif':
                return {"success": True, "message": "Hattınız zaten aktif durumda."}
            user['status'] = 'aktif'
            user['service_status'] = 'Aktif'
            _save_users(users)
            return {"success": True, "message": "Hattınız başarıyla aktifleştirildi ve veritabanı güncellendi."}
    return {"success": False, "message": "Kullanıcı bulunamadı. Hat aktifleştirilemedi."}



# Fonksiyon haritası
function_map = {
    "getUserInfo": getUserInfo,
    "getAvailablePackages": getAvailablePackages,
    "initiatePackageChange": initiatePackageChange,
    "getBillDetails": getBillDetails,
    "checkServiceAvailability": checkServiceAvailability,
    "scheduleTechnicalSupport": scheduleTechnicalSupport,
    "cancelSubscription": cancelSubscription,
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
    "checkContractEndDate": checkContractEndDate,
    "activateLine" : activateLine,
    "freezeLine" :freezeLine,
    "deleteSubscription":deleteSubscription
}

if __name__ == "__main__":
    print("Mock API servisi başlatıldı. Fonksiyonlar hazır.")