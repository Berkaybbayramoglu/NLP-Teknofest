# src/agentkit/tools/api_functions.py
import os, json, random
from datetime import datetime, timedelta

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.getenv("AGENTKIT_DATA_DIR", os.path.join(ROOT, "data"))
USER_DB = os.getenv("AGENTKIT_USER_DB", os.path.join(DATA_DIR, "user.json"))
PACKAGE_DB = os.getenv("AGENTKIT_PACKAGES_DB", os.path.join(DATA_DIR, "packages.json"))

def _load_users():
    with open(USER_DB, encoding="utf-8") as f:
        return json.load(f)

def _save_users(users):
    os.makedirs(os.path.dirname(USER_DB), exist_ok=True)
    with open(USER_DB, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def _load_packages():
    with open(PACKAGE_DB, encoding="utf-8") as f:
        return json.load(f)

def _normalize_phone(s: str) -> str:
    return (s or "").replace(" ", "").replace("-", "")

def _find_user(identifier: str, users=None):
    if users is None:
        users = _load_users()
    ident = _normalize_phone(identifier)
    for u in users:
        if u.get("tc_no") == identifier:
            return u
        if u.get("customer_id") == identifier:
            return u
        if _normalize_phone(u.get("phone_number", "")) == ident:
            return u
    return None

def getUserInfo(user_identifier: str) -> str:
    u = _find_user(user_identifier)
    if not u:
        return json.dumps({"success": False, "error": "Kullanıcı bulunamadı."}, ensure_ascii=False)
    data = {
        "tc_no": u.get("tc_no"),
        "name": u.get("name"),
        "current_package": u.get("current_package"),
        "contract_end_date": u.get("contract_end_date"),
    }
    return json.dumps({"success": True, "data": data}, ensure_ascii=False)

def getAvailablePackages(user_identifier: str) -> str:
    users = _load_users()
    pkgs = _load_packages()
    c = _find_user(user_identifier, users)
    if not c:
        return json.dumps({"success": False, "error": "Kullanıcı bulunamadı. Paket önerisi yapılamadı."}, ensure_ascii=False)
    cur = c.get("current_package", "")
    occ = (c.get("occupation", "") or "").strip().lower()
    out = []
    for p in pkgs:
        name = p.get("name", "")
        groups = [g.lower() for g in p.get("allowed_groups", ["genel"])]
        if occ in groups and name != cur:
            out.append(p)
    if not out:
        return json.dumps({"success": True, "data": [], "message": f"{occ} grubuna özel paket bulunamadı."}, ensure_ascii=False)
    return json.dumps({"success": True, "data": out, "message": f"{occ} grubuna özel {len(out)} paket bulundu."}, ensure_ascii=False)

def initiatePackageChange(user_identifier: str, new_package_name: str) -> str:
    users = _load_users()
    for u in users:
        if _find_user(user_identifier, [u]):
            if u.get("payment_status") == "Gecikmiş":
                return json.dumps({"success": False, "message": "Gecikmiş fatura nedeniyle paket değişikliği yapılamıyor."}, ensure_ascii=False)
            old = u.get("current_package", "belirtilmemiş")
            u["current_package"] = new_package_name
            _save_users(users)
            return json.dumps({"success": True, "message": f"Mevcut paket güncellendi: {old} → {new_package_name}", "new_package": new_package_name}, ensure_ascii=False)
    return json.dumps({"success": False, "message": "Kullanıcı bulunamadı. Paket güncellenemedi."}, ensure_ascii=False)

def getBillDetails(user_identifier: str, bill_id: str | None = None, period: str | None = None) -> str:
    users = _load_users()
    c = _find_user(user_identifier, users)
    if not c:
        return json.dumps({"success": False, "error": "Kullanıcı bulunamadı."}, ensure_ascii=False)
    bills = c.get("bills", [])
    if not bills:
        return json.dumps({"success": False, "error": "Bu kullanıcıya ait fatura kaydı bulunamadı."}, ensure_ascii=False)
    if bill_id:
        b = next((x for x in bills if x.get("bill_id") == bill_id), None)
        if b:
            return json.dumps({"success": True, "data": b, "message": f"{bill_id} ID'li fatura bulundu."}, ensure_ascii=False)
        return json.dumps({"success": False, "error": f"{bill_id} ID'li fatura bulunamadı."}, ensure_ascii=False)
    if period == "son":
        try:
            latest = max(bills, key=lambda x: datetime.strptime(x["bill_date"], "%Y-%m-%d"))
            return json.dumps({"success": True, "data": latest, "message": "En son fatura getirildi."}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"success": False, "error": f"Tarih formatı hatalı: {e}"}, ensure_ascii=False)
    if period == "tümü":
        return json.dumps({"success": True, "data": bills, "message": "Tüm faturalar listelendi."}, ensure_ascii=False)
    return json.dumps({"success": True, "data": bills, "message": "Varsayılan olarak tüm faturalar getirildi."}, ensure_ascii=False)

def checkServiceAvailability(address_street: str | None = None, address_city: str | None = None, address_zip_code: str | None = None, user_identifier: str | None = None, service_type: str = "Fiber İnternet") -> str:
    return json.dumps({"success": True, "available": True, "message": "Adresinizde hizmet mevcut (örnek)."}, ensure_ascii=False)

def scheduleTechnicalSupport(user_identifier: str, issue_description: str, preferred_date: str, preferred_time: str) -> str:
    users = _load_users()
    try:
        req_dt = datetime.strptime(f"{preferred_date} {preferred_time}", "%Y-%m-%d %H:%M")
        if req_dt < datetime.now():
            return json.dumps({"success": False, "error": "Geçmiş tarihe randevu alınamaz."}, ensure_ascii=False)
        if req_dt.weekday() >= 5 or not (9 <= req_dt.hour < 17):
            return json.dumps({"success": False, "error": "Randevular hafta içi 09:00–17:00 arasıdır."}, ensure_ascii=False)
    except ValueError:
        return json.dumps({"success": False, "error": "Tarih/saat formatı geçersiz. YYYY-MM-DD ve HH:MM olmalı."}, ensure_ascii=False)
    for u in users:
        if _find_user(user_identifier, [u]):
            apps = u.setdefault("appointments", [])
            for a in apps:
                if a.get("date") == preferred_date and a.get("time") == preferred_time:
                    return json.dumps({"success": False, "error": "Bu tarih ve saat için zaten randevunuz var."}, ensure_ascii=False)
            app_id = f"destek-{random.randint(10, 100)}"
            new_app = {
                "appointment_id": app_id,
                "issue": issue_description,
                "date": preferred_date,
                "time": preferred_time,
                "status": "Planlandı",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "active": True,
            }
            apps.append(new_app)
            _save_users(users)
            return json.dumps({"success": True, "message": f"Randevu oluşturuldu. Takip: {app_id}", "appointment": new_app}, ensure_ascii=False)
    return json.dumps({"success": False, "error": "Kullanıcı bulunamadı."}, ensure_ascii=False)

def cancelSubscription(user_identifier: str, reason: str) -> str:
    users = _load_users()
    for u in users:
        if _find_user(user_identifier, [u]):
            for k in ["current_package", "package_start_date", "package_end_date", "remaining_data", "remaining_minutes", "remaining_sms"]:
                u.pop(k, None)
            u["status"] = "pasif"
            u["service_status"] = "Abonelik iptal edildi"
            u["cancellation_reason"] = reason
            u["cancellation_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            _save_users(users)
            return json.dumps({"success": True, "message": f"Aboneliğiniz '{reason}' nedeniyle iptal edildi."}, ensure_ascii=False)
    return json.dumps({"success": False, "message": "Kullanıcı bulunamadı."}, ensure_ascii=False)

def getUsageHistory(user_identifier: str, period: str = "Son 3 Ay") -> str:
    users = _load_users()
    c = _find_user(user_identifier, users)
    if not c:
        return json.dumps({"success": False, "error": "Kullanıcı bulunamadı."}, ensure_ascii=False)
    data = c.get("usage_history", {})
    if data:
        return json.dumps({"success": True, "data": data, "message": f"{c.get('name','')} için kullanım geçmişi getirildi."}, ensure_ascii=False)
    return json.dumps({"success": True, "data": {}, "message": f"{c.get('name','')} için kullanım geçmişi bulunamadı."}, ensure_ascii=False)

def blockIncomingNumber(user_identifier: str, target_number: str) -> str:
    users = _load_users()
    num = _normalize_phone(target_number)
    if not num.isdigit() or len(num) != 11 or not num.startswith("05"):
        return json.dumps({"success": False, "error": "Geçersiz numara. 05XXXXXXXXX biçiminde girin."}, ensure_ascii=False)
    for u in users:
        if _find_user(user_identifier, [u]):
            bl = u.setdefault("blocked_numbers", [])
            if num in bl:
                return json.dumps({"success": False, "error": "Bu numara zaten engelli."}, ensure_ascii=False)
            bl.append(num)
            _save_users(users)
            return json.dumps({"success": True, "message": f"{num} engellendi."}, ensure_ascii=False)
    return json.dumps({"success": False, "error": "Kullanıcı bulunamadı."}, ensure_ascii=False)

def unblockIncomingNumber(user_identifier: str, target_number: str) -> str:
    users = _load_users()
    num = _normalize_phone(target_number)
    if len(num) != 11 or not num.startswith("05"):
        return json.dumps({"success": False, "error": "Geçersiz numara formatı."}, ensure_ascii=False)
    for u in users:
        if _find_user(user_identifier, [u]):
            bl = u.get("blocked_numbers", [])
            if num not in bl:
                return json.dumps({"success": False, "error": "Bu numara engelli listesinde değil."}, ensure_ascii=False)
            bl.remove(num)
            u["blocked_numbers"] = bl
            _save_users(users)
            return json.dumps({"success": True, "message": f"{num} engeli kaldırıldı."}, ensure_ascii=False)
    return json.dumps({"success": False, "error": "Kullanıcı bulunamadı."}, ensure_ascii=False)

def activateEsim(user_identifier: str) -> str:
    users = _load_users()
    for u in users:
        if _find_user(user_identifier, [u]):
            if u.get("esim_active"):
                return json.dumps({"success": False, "message": "eSIM zaten aktif."}, ensure_ascii=False)
            u["esim_active"] = True
            _save_users(users)
            return json.dumps({"success": True, "message": "eSIM aktivasyonu başarılı."}, ensure_ascii=False)
    return json.dumps({"success": False, "message": "Kullanıcı bulunamadı."}, ensure_ascii=False)

def suspendLineDueToLoss(user_identifier: str, reason: str) -> str:
    users = _load_users()
    for u in users:
        if _find_user(user_identifier, [u]):
            u["status"] = "pasif"
            u["service_status"] = "Askıya Alındı"
            _save_users(users)
            return json.dumps({"success": True, "message": f"Hattınız '{reason}' nedeniyle askıya alındı."}, ensure_ascii=False)
    return json.dumps({"success": False, "message": "Kullanıcı bulunamadı."}, ensure_ascii=False)

def deactivateEsim(user_identifier: str) -> str:
    users = _load_users()
    for u in users:
        if _find_user(user_identifier, [u]):
            if not u.get("esim_active"):
                return json.dumps({"success": False, "message": "eSIM zaten devre dışı."}, ensure_ascii=False)
            u["esim_active"] = False
            _save_users(users)
            return json.dumps({"success": True, "message": "eSIM devre dışı bırakıldı."}, ensure_ascii=False)
    return json.dumps({"success": False, "message": "Kullanıcı bulunamadı."}, ensure_ascii=False)

def removeDataRestriction(user_identifier: str) -> str:
    users = _load_users()
    for u in users:
        if _find_user(user_identifier, [u]):
            if not u.get("roaming_restricted", False):
                return json.dumps({"success": False, "message": "Aktif veri kısıtlaması yok."}, ensure_ascii=False)
            u["roaming_restricted"] = False
            _save_users(users)
            return json.dumps({"success": True, "message": "Yurt dışı veri kısıtlaması kaldırıldı."}, ensure_ascii=False)
    return json.dumps({"success": False, "message": "Kullanıcı bulunamadı."}, ensure_ascii=False)

def activateChildProfile(user_identifier: str) -> str:
    users = _load_users()
    for u in users:
        if _find_user(user_identifier, [u]):
            if u.get("child_mode_enabled") is True:
                return json.dumps({"success": True, "message": "Çocuk profili zaten aktif."}, ensure_ascii=False)
            u["child_mode_enabled"] = True
            _save_users(users)
            return json.dumps({"success": True, "message": "Çocuk profili aktif edildi."}, ensure_ascii=False)
    return json.dumps({"success": False, "message": "Kullanıcı bulunamadı."}, ensure_ascii=False)

def deactivateChildProfile(user_identifier: str) -> str:
    users = _load_users()
    for u in users:
        if _find_user(user_identifier, [u]):
            if u.get("child_mode_enabled") is False:
                return json.dumps({"success": True, "message": "Çocuk profili zaten devre dışı."}, ensure_ascii=False)
            u["child_mode_enabled"] = False
            _save_users(users)
            return json.dumps({"success": True, "message": "Çocuk profili devre dışı bırakıldı."}, ensure_ascii=False)
    return json.dumps({"success": False, "message": "Kullanıcı bulunamadı."}, ensure_ascii=False)

def enable5G(user_identifier: str) -> str:
    users = _load_users()
    for u in users:
        if _find_user(user_identifier, [u]):
            if u.get("network_mode") == "5G":
                return json.dumps({"success": False, "message": "Zaten 5G'ye tanımlısınız."}, ensure_ascii=False)
            city = (u.get("address", {}).get("city", "") or "").lower()
            if city not in ["ankara", "izmir", "istanbul"]:
                return json.dumps({"success": False, "message": f"{city.title()} bölgesinde 5G altyapısı yok."}, ensure_ascii=False)
            u["network_mode"] = "5G"
            _save_users(users)
            return json.dumps({"success": True, "message": "5G ağ profili aktif edildi."}, ensure_ascii=False)
    return json.dumps({"success": False, "message": "Kullanıcı bulunamadı."}, ensure_ascii=False)

def getCallHistory(user_identifier: str) -> str:
    users = _load_users()
    for u in users:
        if _find_user(user_identifier, [u]):
            call_types = ["Gelen", "Giden", "Cevapsız"]
            hist = []
            for _ in range(5):
                t = (datetime.now() - timedelta(minutes=random.randint(1, 1440))).strftime("%H:%M")
                hist.append({"type": random.choice(call_types), "number": f"05{random.randint(100000000, 999999999)}", "time": t})
            return json.dumps({"success": True, "call_history": hist, "message": f"{u.get('name','')} için son 5 çağrı kaydı."}, ensure_ascii=False)
    return json.dumps({"success": False, "error": "Kullanıcı bulunamadı."}, ensure_ascii=False)

def getSupportTicketStatus(user_identifier: str) -> str:
    users = _load_users()
    for u in users:
        if _find_user(user_identifier, [u]):
            apps = u.get("appointments", [])
            if not apps:
                return json.dumps({"success": False, "message": "Teknik destek kaydı bulunmuyor."}, ensure_ascii=False)
            try:
                last = sorted(apps, key=lambda x: datetime.strptime(f"{x['date']} {x['time']}", "%Y-%m-%d %H:%M"), reverse=True)[0]
            except Exception as e:
                return json.dumps({"success": False, "error": f"Randevu verisi okunamadı: {e}"}, ensure_ascii=False)
            return json.dumps({"success": True, "ticket": {"ticket_id": last.get("appointment_id","destek-XXXX"), "status": last.get("status",""), "created_at": last.get("created_at",""), "description": last.get("issue","")}, "message": "Son teknik destek kaydınız:"}, ensure_ascii=False)
    return json.dumps({"success": False, "message": "Kullanıcı bulunamadı."}, ensure_ascii=False)

def checkServiceStatus(user_identifier: str) -> str:
    return json.dumps({"success": True, "status": "Aktif", "message": "Hizmet aktif (örnek)."}, ensure_ascii=False)

def addAuthorizedContact(user_identifier: str, name: str, phone: str) -> str:
    users = _load_users()
    cleaned = _normalize_phone(phone)
    for u in users:
        if _find_user(user_identifier, [u]):
            lst = u.setdefault("authorized_contacts", [])
            for c in lst:
                if _normalize_phone(c.get("phone","")) == cleaned:
                    return json.dumps({"success": False, "error": f"{phone} zaten yetkili kişiler arasında."}, ensure_ascii=False)
            lst.append({"name": name, "phone": cleaned})
            _save_users(users)
            return json.dumps({"success": True, "message": f"{name} ({cleaned}) yetkili olarak eklendi."}, ensure_ascii=False)
    return json.dumps({"success": False, "error": "Kullanıcı bulunamadı."}, ensure_ascii=False)

def requestNumberPorting(user_identifier: str, current_operator: str, reason: str) -> str:
    return json.dumps({"success": True, "message": "Numara taşıma başvurusu alındı (örnek)."}, ensure_ascii=False)

def _generate_unique_phone(users):
    while True:
        new_num = "05" + "".join(str(random.randint(0, 9)) for _ in range(9))
        if not any(_normalize_phone(u.get("phone_number","")) == new_num for u in users):
            return new_num

def requestNumberChange(user_identifier: str, reason: str) -> str:
    users = _load_users()
    for u in users:
        if _find_user(user_identifier, [u]):
            old = u.get("phone_number")
            new = _generate_unique_phone(users)
            u["phone_number"] = new
            u["status"] = "aktif"
            _save_users(users)
            return json.dumps({"success": True, "message": f"Numaranız '{reason}' nedeniyle değiştirildi. Yeni: {new}. Eski: {old}."}, ensure_ascii=False)
    return json.dumps({"success": False, "message": "Kullanıcı bulunamadı."}, ensure_ascii=False)

def pausePackageTemporarily(user_identifier: str, duration_days: int, reason: str) -> str:
    return json.dumps({"success": True, "message": f"Paket {duration_days} gün askıya alındı (örnek)."}, ensure_ascii=False)

def activateInternationalRoaming(user_identifier: str) -> str:
    users = _load_users()
    c = _find_user(user_identifier, users)
    if not c:
        return json.dumps({"success": False, "error": "Kullanıcı bulunamadı."}, ensure_ascii=False)
    if c.get("roaming_restricted") is False:
        return json.dumps({"success": True, "message": "Yurt dışı kullanım zaten açık."}, ensure_ascii=False)
    c["roaming_restricted"] = False
    _save_users(users)
    return json.dumps({"success": True, "message": "Yurt dışı kullanım başarıyla açıldı.", "roaming_status": "Açık"}, ensure_ascii=False)

def sendGiftPackage(sender_id: str, receiver_number: str, package_type: str, amount: int) -> str:
    if (package_type or "").lower() != "internet":
        return json.dumps({"success": False, "error": "Şu anda yalnızca internet paketi hediye edilebilir."}, ensure_ascii=False)
    if amount <= 0 or amount > 10:
        return json.dumps({"success": False, "error": "Gönderim miktarı geçersiz ya da limit üstü (maksimum 10 GB)."}, ensure_ascii=False)
    users = _load_users()
    s = _find_user(sender_id, users)
    r = next((u for u in users if _normalize_phone(u.get("phone_number","")) == _normalize_phone(receiver_number)), None)
    if not s:
        return json.dumps({"success": False, "error": "Gönderen kullanıcı bulunamadı."}, ensure_ascii=False)
    if not r:
        return json.dumps({"success": False, "error": "Alıcı kullanıcı bulunamadı."}, ensure_ascii=False)
    gb_price = 50
    total = gb_price * amount
    bills = s.get("bills", [])
    editable = [b for b in bills if b.get("status") in ["Beklemede", "Gecikmiş"]]
    if not editable:
        return json.dumps({"success": False, "error": "Düzenlenebilir fatura bulunamadı."}, ensure_ascii=False)
    latest = max(editable, key=lambda b: datetime.strptime(b.get("bill_date", "1900-01-01"), "%Y-%m-%d"))
    latest["amount"] = float(latest.get("amount", 0)) + total
    br = latest.setdefault("breakdown", {})
    try:
        base_val = float(str(br.get("base", "0")).replace(" TL", ""))
    except Exception:
        base_val = 0.0
    br["base"] = f"{base_val + total:.2f} TL"
    details = latest.get("details", "")
    latest["details"] = (details + " + " if details else "") + f"{amount} GB hediye internet"
    r.setdefault("usage_history", {})
    r["usage_history"]["internet_gb_used_monthly"] = r["usage_history"].get("internet_gb_used_monthly", 0) + amount
    _save_users(users)
    return json.dumps({"success": True, "message": f"{r.get('name','')} kullanıcısına {amount} GB gönderildi. Faturaya {total} TL eklendi.", "updated_bill": latest}, ensure_ascii=False)

def getReceivedGifts(user_identifier: str) -> str:
    return json.dumps({"success": True, "gifts": [{"type": "internet", "amount": "2GB", "sender": "Bilinmiyor", "date": "2025-07-04"}]}, ensure_ascii=False)

def requestInstallmentPlan(user_identifier: str, total_amount: float, installments: int) -> str:
    return json.dumps({"success": True, "message": f"{total_amount} TL {installments} taksite bölündü (örnek)."}, ensure_ascii=False)

def checkInfrastructure(address: str) -> str:
    return json.dumps({"success": True, "infrastructure": "fiber (örnek)"}, ensure_ascii=False)

def scheduleInternetRelocation(user_identifier: str, new_address: dict) -> str:
    users = _load_users()
    for u in users:
        if _find_user(user_identifier, [u]):
            old = u.get("address", {})
            u["address"] = new_address
            u.setdefault("appointments", []).append({
                "type": "İnternet Nakil",
                "requested_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "Planlandı",
                "old_address": old,
                "new_address": new_address,
            })
            _save_users(users)
            return json.dumps({"success": True, "message": f"İnternet taşıma kaydedildi. Yeni adres: {new_address.get('street')}, {new_address.get('city')} ({new_address.get('zip_code')})"}, ensure_ascii=False)
    return json.dumps({"success": False, "message": "Kullanıcı bulunamadı. Taşıma yapılamadı."}, ensure_ascii=False)

def checkContractEndDate(user_identifier: str) -> str:
    return json.dumps({"success": True, "contract_end_date": "2025-12-31", "days_remaining": 180, "message": "Taahhüt bitiş tarihi (örnek)."}, ensure_ascii=False)

def freezeLine(user_identifier: str, reason: str = "Kullanıcı talebiyle donduruldu") -> str:
    users = _load_users()
    for u in users:
        if _find_user(user_identifier, [u]):
            if u.get("status") == "pasif":
                return json.dumps({"success": True, "message": "Hattınız zaten pasif."}, ensure_ascii=False)
            u["status"] = "pasif"
            _save_users(users)
            return json.dumps({"success": True, "message": f"Hat donduruldu. ({reason})"}, ensure_ascii=False)
    return json.dumps({"success": False, "message": "Kullanıcı bulunamadı."}, ensure_ascii=False)

def activateLine(user_identifier: str) -> str:
    users = _load_users()
    for u in users:
        if _find_user(user_identifier, [u]):
            if u.get("status") == "aktif" and (u.get("service_status","").lower() == "aktif"):
                return json.dumps({"success": True, "message": "Hattınız zaten aktif."}, ensure_ascii=False)
            u["status"] = "aktif"
            u["service_status"] = "Aktif"
            _save_users(users)
            return json.dumps({"success": True, "message": "Hat aktifleştirildi."}, ensure_ascii=False)
    return json.dumps({"success": False, "message": "Kullanıcı bulunamadı."}, ensure_ascii=False)

def deleteSubscription(user_identifier: str, reason: str) -> str:
    users = _load_users()
    for u in users:
        if _find_user(user_identifier, [u]):
            u["status"] = "pasif"
            u["service_status"] = "İptal Edildi"
            _save_users(users)
            return json.dumps({"success": True, "message": f"Abonelik '{reason}' nedeniyle iptal edildi."}, ensure_ascii=False)
    return json.dumps({"success": False, "message": "Kullanıcı bulunamadı."}, ensure_ascii=False)
import os, json, random
from datetime import datetime, timedelta

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.getenv("AGENTKIT_DATA_DIR", os.path.join(ROOT, "data"))
USER_DB = os.getenv("AGENTKIT_USER_DB", os.path.join(DATA_DIR, "user.json"))
PACKAGE_DB = os.getenv("AGENTKIT_PACKAGES_DB", os.path.join(DATA_DIR, "packages.json"))

def _load_users():
    with open(USER_DB, encoding="utf-8") as f:
        return json.load(f)

def _save_users(users):
    os.makedirs(os.path.dirname(USER_DB), exist_ok=True)
    with open(USER_DB, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def _load_packages():
    with open(PACKAGE_DB, encoding="utf-8") as f:
        return json.load(f)

def _normalize_phone(s: str) -> str:
    return (s or "").replace(" ", "").replace("-", "")

def _find_user(identifier: str, users=None):
    if users is None:
        users = _load_users()
    ident = _normalize_phone(identifier)
    for u in users:
        if u.get("tc_no") == identifier:
            return u
        if u.get("customer_id") == identifier:
            return u
        if _normalize_phone(u.get("phone_number", "")) == ident:
            return u
    return None

def getUserInfo(user_identifier: str) -> str:
    u = _find_user(user_identifier)
    if not u:
        return json.dumps({"success": False, "error": "Kullanıcı bulunamadı."}, ensure_ascii=False)
    data = {
        "tc_no": u.get("tc_no"),
        "name": u.get("name"),
        "current_package": u.get("current_package"),
        "contract_end_date": u.get("contract_end_date"),
    }
    return json.dumps({"success": True, "data": data}, ensure_ascii=False)

def getAvailablePackages(user_identifier: str) -> str:
    users = _load_users()
    pkgs = _load_packages()
    c = _find_user(user_identifier, users)
    if not c:
        return json.dumps({"success": False, "error": "Kullanıcı bulunamadı. Paket önerisi yapılamadı."}, ensure_ascii=False)
    cur = c.get("current_package", "")
    occ = (c.get("occupation", "") or "").strip().lower()
    out = []
    for p in pkgs:
        name = p.get("name", "")
        groups = [g.lower() for g in p.get("allowed_groups", ["genel"])]
        if occ in groups and name != cur:
            out.append(p)
    if not out:
        return json.dumps({"success": True, "data": [], "message": f"{occ} grubuna özel paket bulunamadı."}, ensure_ascii=False)
    return json.dumps({"success": True, "data": out, "message": f"{occ} grubuna özel {len(out)} paket bulundu."}, ensure_ascii=False)

def initiatePackageChange(user_identifier: str, new_package_name: str) -> str:
    users = _load_users()
    for u in users:
        if _find_user(user_identifier, [u]):
            if u.get("payment_status") == "Gecikmiş":
                return json.dumps({"success": False, "message": "Gecikmiş fatura nedeniyle paket değişikliği yapılamıyor."}, ensure_ascii=False)
            old = u.get("current_package", "belirtilmemiş")
            u["current_package"] = new_package_name
            _save_users(users)
            return json.dumps({"success": True, "message": f"Mevcut paket güncellendi: {old} → {new_package_name}", "new_package": new_package_name}, ensure_ascii=False)
    return json.dumps({"success": False, "message": "Kullanıcı bulunamadı. Paket güncellenemedi."}, ensure_ascii=False)

def getBillDetails(user_identifier: str, bill_id: str | None = None, period: str | None = None) -> str:
    users = _load_users()
    c = _find_user(user_identifier, users)
    if not c:
        return json.dumps({"success": False, "error": "Kullanıcı bulunamadı."}, ensure_ascii=False)
    bills = c.get("bills", [])
    if not bills:
        return json.dumps({"success": False, "error": "Bu kullanıcıya ait fatura kaydı bulunamadı."}, ensure_ascii=False)
    if bill_id:
        b = next((x for x in bills if x.get("bill_id") == bill_id), None)
        if b:
            return json.dumps({"success": True, "data": b, "message": f"{bill_id} ID'li fatura bulundu."}, ensure_ascii=False)
        return json.dumps({"success": False, "error": f"{bill_id} ID'li fatura bulunamadı."}, ensure_ascii=False)
    if period == "son":
        try:
            latest = max(bills, key=lambda x: datetime.strptime(x["bill_date"], "%Y-%m-%d"))
            return json.dumps({"success": True, "data": latest, "message": "En son fatura getirildi."}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"success": False, "error": f"Tarih formatı hatalı: {e}"}, ensure_ascii=False)
    if period == "tümü":
        return json.dumps({"success": True, "data": bills, "message": "Tüm faturalar listelendi."}, ensure_ascii=False)
    return json.dumps({"success": True, "data": bills, "message": "Varsayılan olarak tüm faturalar getirildi."}, ensure_ascii=False)

def checkServiceAvailability(address_street: str | None = None, address_city: str | None = None, address_zip_code: str | None = None, user_identifier: str | None = None, service_type: str = "Fiber İnternet") -> str:
    return json.dumps({"success": True, "available": True, "message": "Adresinizde hizmet mevcut (örnek)."}, ensure_ascii=False)

def scheduleTechnicalSupport(user_identifier: str, issue_description: str, preferred_date: str, preferred_time: str) -> str:
    users = _load_users()
    try:
        req_dt = datetime.strptime(f"{preferred_date} {preferred_time}", "%Y-%m-%d %H:%M")
        if req_dt < datetime.now():
            return json.dumps({"success": False, "error": "Geçmiş tarihe randevu alınamaz."}, ensure_ascii=False)
        if req_dt.weekday() >= 5 or not (9 <= req_dt.hour < 17):
            return json.dumps({"success": False, "error": "Randevular hafta içi 09:00–17:00 arasıdır."}, ensure_ascii=False)
    except ValueError:
        return json.dumps({"success": False, "error": "Tarih/saat formatı geçersiz. YYYY-MM-DD ve HH:MM olmalı."}, ensure_ascii=False)
    for u in users:
        if _find_user(user_identifier, [u]):
            apps = u.setdefault("appointments", [])
            for a in apps:
                if a.get("date") == preferred_date and a.get("time") == preferred_time:
                    return json.dumps({"success": False, "error": "Bu tarih ve saat için zaten randevunuz var."}, ensure_ascii=False)
            app_id = f"destek-{random.randint(10, 100)}"
            new_app = {
                "appointment_id": app_id,
                "issue": issue_description,
                "date": preferred_date,
                "time": preferred_time,
                "status": "Planlandı",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "active": True,
            }
            apps.append(new_app)
            _save_users(users)
            return json.dumps({"success": True, "message": f"Randevu oluşturuldu. Takip: {app_id}", "appointment": new_app}, ensure_ascii=False)
    return json.dumps({"success": False, "error": "Kullanıcı bulunamadı."}, ensure_ascii=False)

def cancelSubscription(user_identifier: str, reason: str) -> str:
    users = _load_users()
    for u in users:
        if _find_user(user_identifier, [u]):
            for k in ["current_package", "package_start_date", "package_end_date", "remaining_data", "remaining_minutes", "remaining_sms"]:
                u.pop(k, None)
            u["status"] = "pasif"
            u["service_status"] = "Abonelik iptal edildi"
            u["cancellation_reason"] = reason
            u["cancellation_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            _save_users(users)
            return json.dumps({"success": True, "message": f"Aboneliğiniz '{reason}' nedeniyle iptal edildi."}, ensure_ascii=False)
    return json.dumps({"success": False, "message": "Kullanıcı bulunamadı."}, ensure_ascii=False)

def getUsageHistory(user_identifier: str, period: str = "Son 3 Ay") -> str:
    users = _load_users()
    c = _find_user(user_identifier, users)
    if not c:
        return json.dumps({"success": False, "error": "Kullanıcı bulunamadı."}, ensure_ascii=False)
    data = c.get("usage_history", {})
    if data:
        return json.dumps({"success": True, "data": data, "message": f"{c.get('name','')} için kullanım geçmişi getirildi."}, ensure_ascii=False)
    return json.dumps({"success": True, "data": {}, "message": f"{c.get('name','')} için kullanım geçmişi bulunamadı."}, ensure_ascii=False)

def blockIncomingNumber(user_identifier: str, target_number: str) -> str:
    users = _load_users()
    num = _normalize_phone(target_number)
    if not num.isdigit() or len(num) != 11 or not num.startswith("05"):
        return json.dumps({"success": False, "error": "Geçersiz numara. 05XXXXXXXXX biçiminde girin."}, ensure_ascii=False)
    for u in users:
        if _find_user(user_identifier, [u]):
            bl = u.setdefault("blocked_numbers", [])
            if num in bl:
                return json.dumps({"success": False, "error": "Bu numara zaten engelli."}, ensure_ascii=False)
            bl.append(num)
            _save_users(users)
            return json.dumps({"success": True, "message": f"{num} engellendi."}, ensure_ascii=False)
    return json.dumps({"success": False, "error": "Kullanıcı bulunamadı."}, ensure_ascii=False)

def unblockIncomingNumber(user_identifier: str, target_number: str) -> str:
    users = _load_users()
    num = _normalize_phone(target_number)
    if len(num) != 11 or not num.startswith("05"):
        return json.dumps({"success": False, "error": "Geçersiz numara formatı."}, ensure_ascii=False)
    for u in users:
        if _find_user(user_identifier, [u]):
            bl = u.get("blocked_numbers", [])
            if num not in bl:
                return json.dumps({"success": False, "error": "Bu numara engelli listesinde değil."}, ensure_ascii=False)
            bl.remove(num)
            u["blocked_numbers"] = bl
            _save_users(users)
            return json.dumps({"success": True, "message": f"{num} engeli kaldırıldı."}, ensure_ascii=False)
    return json.dumps({"success": False, "error": "Kullanıcı bulunamadı."}, ensure_ascii=False)

def activateEsim(user_identifier: str) -> str:
    users = _load_users()
    for u in users:
        if _find_user(user_identifier, [u]):
            if u.get("esim_active"):
                return json.dumps({"success": False, "message": "eSIM zaten aktif."}, ensure_ascii=False)
            u["esim_active"] = True
            _save_users(users)
            return json.dumps({"success": True, "message": "eSIM aktivasyonu başarılı."}, ensure_ascii=False)
    return json.dumps({"success": False, "message": "Kullanıcı bulunamadı."}, ensure_ascii=False)

def suspendLineDueToLoss(user_identifier: str, reason: str) -> str:
    users = _load_users()
    for u in users:
        if _find_user(user_identifier, [u]):
            u["status"] = "pasif"
            u["service_status"] = "Askıya Alındı"
            _save_users(users)
            return json.dumps({"success": True, "message": f"Hattınız '{reason}' nedeniyle askıya alındı."}, ensure_ascii=False)
    return json.dumps({"success": False, "message": "Kullanıcı bulunamadı."}, ensure_ascii=False)

def deactivateEsim(user_identifier: str) -> str:
    users = _load_users()
    for u in users:
        if _find_user(user_identifier, [u]):
            if not u.get("esim_active"):
                return json.dumps({"success": False, "message": "eSIM zaten devre dışı."}, ensure_ascii=False)
            u["esim_active"] = False
            _save_users(users)
            return json.dumps({"success": True, "message": "eSIM devre dışı bırakıldı."}, ensure_ascii=False)
    return json.dumps({"success": False, "message": "Kullanıcı bulunamadı."}, ensure_ascii=False)

def removeDataRestriction(user_identifier: str) -> str:
    users = _load_users()
    for u in users:
        if _find_user(user_identifier, [u]):
            if not u.get("roaming_restricted", False):
                return json.dumps({"success": False, "message": "Aktif veri kısıtlaması yok."}, ensure_ascii=False)
            u["roaming_restricted"] = False
            _save_users(users)
            return json.dumps({"success": True, "message": "Yurt dışı veri kısıtlaması kaldırıldı."}, ensure_ascii=False)
    return json.dumps({"success": False, "message": "Kullanıcı bulunamadı."}, ensure_ascii=False)

def activateChildProfile(user_identifier: str) -> str:
    users = _load_users()
    for u in users:
        if _find_user(user_identifier, [u]):
            if u.get("child_mode_enabled") is True:
                return json.dumps({"success": True, "message": "Çocuk profili zaten aktif."}, ensure_ascii=False)
            u["child_mode_enabled"] = True
            _save_users(users)
            return json.dumps({"success": True, "message": "Çocuk profili aktif edildi."}, ensure_ascii=False)
    return json.dumps({"success": False, "message": "Kullanıcı bulunamadı."}, ensure_ascii=False)

def deactivateChildProfile(user_identifier: str) -> str:
    users = _load_users()
    for u in users:
        if _find_user(user_identifier, [u]):
            if u.get("child_mode_enabled") is False:
                return json.dumps({"success": True, "message": "Çocuk profili zaten devre dışı."}, ensure_ascii=False)
            u["child_mode_enabled"] = False
            _save_users(users)
            return json.dumps({"success": True, "message": "Çocuk profili devre dışı bırakıldı."}, ensure_ascii=False)
    return json.dumps({"success": False, "message": "Kullanıcı bulunamadı."}, ensure_ascii=False)

def enable5G(user_identifier: str) -> str:
    users = _load_users()
    for u in users:
        if _find_user(user_identifier, [u]):
            if u.get("network_mode") == "5G":
                return json.dumps({"success": False, "message": "Zaten 5G'ye tanımlısınız."}, ensure_ascii=False)
            city = (u.get("address", {}).get("city", "") or "").lower()
            if city not in ["ankara", "izmir", "istanbul"]:
                return json.dumps({"success": False, "message": f"{city.title()} bölgesinde 5G altyapısı yok."}, ensure_ascii=False)
            u["network_mode"] = "5G"
            _save_users(users)
            return json.dumps({"success": True, "message": "5G ağ profili aktif edildi."}, ensure_ascii=False)
    return json.dumps({"success": False, "message": "Kullanıcı bulunamadı."}, ensure_ascii=False)

def getCallHistory(user_identifier: str) -> str:
    users = _load_users()
    for u in users:
        if _find_user(user_identifier, [u]):
            call_types = ["Gelen", "Giden", "Cevapsız"]
            hist = []
            for _ in range(5):
                t = (datetime.now() - timedelta(minutes=random.randint(1, 1440))).strftime("%H:%M")
                hist.append({"type": random.choice(call_types), "number": f"05{random.randint(100000000, 999999999)}", "time": t})
            return json.dumps({"success": True, "call_history": hist, "message": f"{u.get('name','')} için son 5 çağrı kaydı."}, ensure_ascii=False)
    return json.dumps({"success": False, "error": "Kullanıcı bulunamadı."}, ensure_ascii=False)

def getSupportTicketStatus(user_identifier: str) -> str:
    users = _load_users()
    for u in users:
        if _find_user(user_identifier, [u]):
            apps = u.get("appointments", [])
            if not apps:
                return json.dumps({"success": False, "message": "Teknik destek kaydı bulunmuyor."}, ensure_ascii=False)
            try:
                last = sorted(apps, key=lambda x: datetime.strptime(f"{x['date']} {x['time']}", "%Y-%m-%d %H:%M"), reverse=True)[0]
            except Exception as e:
                return json.dumps({"success": False, "error": f"Randevu verisi okunamadı: {e}"}, ensure_ascii=False)
            return json.dumps({"success": True, "ticket": {"ticket_id": last.get("appointment_id","destek-XXXX"), "status": last.get("status",""), "created_at": last.get("created_at",""), "description": last.get("issue","")}, "message": "Son teknik destek kaydınız:"}, ensure_ascii=False)
    return json.dumps({"success": False, "message": "Kullanıcı bulunamadı."}, ensure_ascii=False)

def checkServiceStatus(user_identifier: str) -> str:
    return json.dumps({"success": True, "status": "Aktif", "message": "Hizmet aktif (örnek)."}, ensure_ascii=False)

def addAuthorizedContact(user_identifier: str, name: str, phone: str) -> str:
    users = _load_users()
    cleaned = _normalize_phone(phone)
    for u in users:
        if _find_user(user_identifier, [u]):
            lst = u.setdefault("authorized_contacts", [])
            for c in lst:
                if _normalize_phone(c.get("phone","")) == cleaned:
                    return json.dumps({"success": False, "error": f"{phone} zaten yetkili kişiler arasında."}, ensure_ascii=False)
            lst.append({"name": name, "phone": cleaned})
            _save_users(users)
            return json.dumps({"success": True, "message": f"{name} ({cleaned}) yetkili olarak eklendi."}, ensure_ascii=False)
    return json.dumps({"success": False, "error": "Kullanıcı bulunamadı."}, ensure_ascii=False)

def requestNumberPorting(user_identifier: str, current_operator: str, reason: str) -> str:
    return json.dumps({"success": True, "message": "Numara taşıma başvurusu alındı (örnek)."}, ensure_ascii=False)

def _generate_unique_phone(users):
    while True:
        new_num = "05" + "".join(str(random.randint(0, 9)) for _ in range(9))
        if not any(_normalize_phone(u.get("phone_number","")) == new_num for u in users):
            return new_num

def requestNumberChange(user_identifier: str, reason: str) -> str:
    users = _load_users()
    for u in users:
        if _find_user(user_identifier, [u]):
            old = u.get("phone_number")
            new = _generate_unique_phone(users)
            u["phone_number"] = new
            u["status"] = "aktif"
            _save_users(users)
            return json.dumps({"success": True, "message": f"Numaranız '{reason}' nedeniyle değiştirildi. Yeni: {new}. Eski: {old}."}, ensure_ascii=False)
    return json.dumps({"success": False, "message": "Kullanıcı bulunamadı."}, ensure_ascii=False)

def pausePackageTemporarily(user_identifier: str, duration_days: int, reason: str) -> str:
    return json.dumps({"success": True, "message": f"Paket {duration_days} gün askıya alındı (örnek)."}, ensure_ascii=False)

def activateInternationalRoaming(user_identifier: str) -> str:
    users = _load_users()
    c = _find_user(user_identifier, users)
    if not c:
        return json.dumps({"success": False, "error": "Kullanıcı bulunamadı."}, ensure_ascii=False)
    if c.get("roaming_restricted") is False:
        return json.dumps({"success": True, "message": "Yurt dışı kullanım zaten açık."}, ensure_ascii=False)
    c["roaming_restricted"] = False
    _save_users(users)
    return json.dumps({"success": True, "message": "Yurt dışı kullanım başarıyla açıldı.", "roaming_status": "Açık"}, ensure_ascii=False)

def sendGiftPackage(sender_id: str, receiver_number: str, package_type: str, amount: int) -> str:
    if (package_type or "").lower() != "internet":
        return json.dumps({"success": False, "error": "Şu anda yalnızca internet paketi hediye edilebilir."}, ensure_ascii=False)
    if amount <= 0 or amount > 10:
        return json.dumps({"success": False, "error": "Gönderim miktarı geçersiz ya da limit üstü (maksimum 10 GB)."}, ensure_ascii=False)
    users = _load_users()
    s = _find_user(sender_id, users)
    r = next((u for u in users if _normalize_phone(u.get("phone_number","")) == _normalize_phone(receiver_number)), None)
    if not s:
        return json.dumps({"success": False, "error": "Gönderen kullanıcı bulunamadı."}, ensure_ascii=False)
    if not r:
        return json.dumps({"success": False, "error": "Alıcı kullanıcı bulunamadı."}, ensure_ascii=False)
    gb_price = 50
    total = gb_price * amount
    bills = s.get("bills", [])
    editable = [b for b in bills if b.get("status") in ["Beklemede", "Gecikmiş"]]
    if not editable:
        return json.dumps({"success": False, "error": "Düzenlenebilir fatura bulunamadı."}, ensure_ascii=False)
    latest = max(editable, key=lambda b: datetime.strptime(b.get("bill_date", "1900-01-01"), "%Y-%m-%d"))
    latest["amount"] = float(latest.get("amount", 0)) + total
    br = latest.setdefault("breakdown", {})
    try:
        base_val = float(str(br.get("base", "0")).replace(" TL", ""))
    except Exception:
        base_val = 0.0
    br["base"] = f"{base_val + total:.2f} TL"
    details = latest.get("details", "")
    latest["details"] = (details + " + " if details else "") + f"{amount} GB hediye internet"
    r.setdefault("usage_history", {})
    r["usage_history"]["internet_gb_used_monthly"] = r["usage_history"].get("internet_gb_used_monthly", 0) + amount
    _save_users(users)
    return json.dumps({"success": True, "message": f"{r.get('name','')} kullanıcısına {amount} GB gönderildi. Faturaya {total} TL eklendi.", "updated_bill": latest}, ensure_ascii=False)

def getReceivedGifts(user_identifier: str) -> str:
    return json.dumps({"success": True, "gifts": [{"type": "internet", "amount": "2GB", "sender": "Bilinmiyor", "date": "2025-07-04"}]}, ensure_ascii=False)

def requestInstallmentPlan(user_identifier: str, total_amount: float, installments: int) -> str:
    return json.dumps({"success": True, "message": f"{total_amount} TL {installments} taksite bölündü (örnek)."}, ensure_ascii=False)

def checkInfrastructure(address: str) -> str:
    return json.dumps({"success": True, "infrastructure": "fiber (örnek)"}, ensure_ascii=False)

def scheduleInternetRelocation(user_identifier: str, new_address: dict) -> str:
    users = _load_users()
    for u in users:
        if _find_user(user_identifier, [u]):
            old = u.get("address", {})
            u["address"] = new_address
            u.setdefault("appointments", []).append({
                "type": "İnternet Nakil",
                "requested_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "Planlandı",
                "old_address": old,
                "new_address": new_address,
            })
            _save_users(users)
            return json.dumps({"success": True, "message": f"İnternet taşıma kaydedildi. Yeni adres: {new_address.get('street')}, {new_address.get('city')} ({new_address.get('zip_code')})"}, ensure_ascii=False)
    return json.dumps({"success": False, "message": "Kullanıcı bulunamadı. Taşıma yapılamadı."}, ensure_ascii=False)

def checkContractEndDate(user_identifier: str) -> str:
    return json.dumps({"success": True, "contract_end_date": "2025-12-31", "days_remaining": 180, "message": "Taahhüt bitiş tarihi (örnek)."}, ensure_ascii=False)

def freezeLine(user_identifier: str, reason: str = "Kullanıcı talebiyle donduruldu") -> str:
    users = _load_users()
    for u in users:
        if _find_user(user_identifier, [u]):
            if u.get("status") == "pasif":
                return json.dumps({"success": True, "message": "Hattınız zaten pasif."}, ensure_ascii=False)
            u["status"] = "pasif"
            _save_users(users)
            return json.dumps({"success": True, "message": f"Hat donduruldu. ({reason})"}, ensure_ascii=False)
    return json.dumps({"success": False, "message": "Kullanıcı bulunamadı."}, ensure_ascii=False)

def activateLine(user_identifier: str) -> str:
    users = _load_users()
    for u in users:
        if _find_user(user_identifier, [u]):
            if u.get("status") == "aktif" and (u.get("service_status","").lower() == "aktif"):
                return json.dumps({"success": True, "message": "Hattınız zaten aktif."}, ensure_ascii=False)
            u["status"] = "aktif"
            u["service_status"] = "Aktif"
            _save_users(users)
            return json.dumps({"success": True, "message": "Hat aktifleştirildi."}, ensure_ascii=False)
    return json.dumps({"success": False, "message": "Kullanıcı bulunamadı."}, ensure_ascii=False)

def deleteSubscription(user_identifier: str, reason: str) -> str:
    users = _load_users()
    for u in users:
        if _find_user(user_identifier, [u]):
            u["status"] = "pasif"
            u["service_status"] = "İptal Edildi"
            _save_users(users)
            return json.dumps({"success": True, "message": f"Abonelik '{reason}' nedeniyle iptal edildi."}, ensure_ascii=False)
    return json.dumps({"success": False, "message": "Kullanıcı bulunamadı."}, ensure_ascii=False)
