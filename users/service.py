def normalize_phone(phone: str) -> str:
    if phone.startswith("8"):
        return "+7" + phone[1:]
    return phone
