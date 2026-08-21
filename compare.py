# -*- coding: utf-8 -*-
"""比对逻辑：参加人员名单 − 考勤记录 = 未签到/签退人员

匹配优先级：
1. 证件号（身份证/志愿者证号）—— 最可靠
2. 手机号
3. 姓名（有重名风险，仅兜底，且给出提示）
"""
import re
from collections import Counter


# 常见证件号/手机号字段名（已联调校准）
# userid 是名单与考勤共有且未脱敏的唯一标识，匹配优先级最高
ID_KEYS = [
    "userid", "userId", "idCard", "idcard", "cardId", "cardNo", "idNumber",
    "IDCard", "volunteerCardCode", "cardCode", "certificateNo", "identityCard",
    "userNo", "volunteerNo", "missionPersonlId", "missionServiceLogId",
]
PHONE_KEYS = ["mobile", "phone", "phoneNo", "mobileNo", "tel"]
NAME_KEYS = ["hireUsername", "realName", "name", "userName", "volunteerName",
             "nickName"]
STATUS_KEYS = ["status", "state", "type", "signStatus", "attendStatus",
               "signState", "isAttend"]


def _pick(item: dict, keys: list):
    """从记录中取第一个非空字段值"""
    for k in keys:
        v = item.get(k)
        if v is not None and v != "":
            return v
    return None


def _norm(v):
    if v is None:
        return ""
    s = str(v).strip().lower()
    s = re.sub(r"\s+", "", s)
    return s


def _extract_phone(v):
    """手机号键：优先提取 11 位手机号；若为脱敏格式（如 186****2991）则原样使用"""
    s = _norm(v)
    if not s:
        return ""
    m = re.search(r"1[3-9]\d{9}", s)
    if m:
        return m.group(0)
    # 脱敏手机号保留原样（同一人两方脱敏规则一致，可匹配）
    return s


def _extract_id(v):
    """证件号/唯一标识键：直接使用原值（userid 为 32 位 hex、身份证、脱敏证件号均可匹配）"""
    s = _norm(v)
    if not s:
        return ""
    return s.upper()


def build_person_key(item: dict) -> dict:
    """构建人员匹配键：优先唯一标识(userid/证件号) → 手机号 → 姓名"""
    id_val = _pick(item, ID_KEYS)
    id_key = _extract_id(id_val) if id_val else ""

    phone_val = _pick(item, PHONE_KEYS)
    phone_key = _extract_phone(phone_val) if phone_val else ""

    name = _norm(_pick(item, NAME_KEYS))
    return {"id_key": id_key, "phone_key": phone_key, "name_key": name}


def _has_checkout(att: dict) -> bool:
    """判断该考勤记录是否已签退

    签到 ≠ 签退：有考勤记录只代表已签到（或补录），
    需 checkOutMode / endDatetime / attendanceEndTime 任一非空才算已签退。
    """
    for k in ("checkOutMode", "endDatetime", "attendanceEndTime"):
        v = att.get(k)
        if v not in (None, "", "null", "None"):
            return True
    return False


def compare(attendees: list, attendance: list) -> dict:
    """比对人员名单与考勤记录（签到 ≠ 签退，三态分类）

    返回：
    {
      "signed":            [所有已签到人员（含未签退），兼容旧字段]
      "signed_both":       [已签到且已签退]（绿）
      "signed_no_checkout":[已签到但未签退]（橙）
      "not_signed":        [未签到：名单中但无任何考勤记录]（红）—— 核心结果
      "anomalies":         [在考勤记录但不在名单中的人员]
      "stats": {attendee_total, signed_total, signed_both,
                signed_no_checkout, not_signed_total, anomaly_total}
      "warnings": [匹配方式提示]
    }
    """
    att_by_id = {}
    att_by_phone = {}
    att_by_name = {}

    for att in attendance:
        k = build_person_key(att)
        if k["id_key"]:
            att_by_id.setdefault(k["id_key"], att)
        if k["phone_key"]:
            att_by_phone.setdefault(k["phone_key"], att)
        if k["name_key"]:
            att_by_name.setdefault(k["name_key"], att)

    signed_both, signed_no_out, not_signed = [], [], []
    warnings = []
    name_only_matches = 0

    for person in attendees:
        k = build_person_key(person)
        matched = None
        method = ""

        if k["id_key"] and k["id_key"] in att_by_id:
            matched, method = att_by_id[k["id_key"]], "证件号"
        elif k["phone_key"] and k["phone_key"] in att_by_phone:
            matched, method = att_by_phone[k["phone_key"]], "手机号"
        elif k["name_key"] and k["name_key"] in att_by_name:
            matched, method = att_by_name[k["name_key"]], "姓名"
            name_only_matches += 1

        rec = {
            "person": person,
            "match_method": method,
            "attendance_record": matched,
        }
        if matched is None:
            not_signed.append(rec)
        elif _has_checkout(matched):
            signed_both.append(rec)
        else:
            signed_no_out.append(rec)

    if name_only_matches > 0:
        warnings.append(
            f"有 {name_only_matches} 人仅通过姓名匹配，若存在重名请核对（建议用证件号/手机号）"
        )

    attendee_keys = set()
    for person in attendees:
        k = build_person_key(person)
        if k["id_key"]:
            attendee_keys.add(("id", k["id_key"]))
        elif k["phone_key"]:
            attendee_keys.add(("phone", k["phone_key"]))
        elif k["name_key"]:
            attendee_keys.add(("name", k["name_key"]))

    anomalies = [att for att in attendance
                 if not _att_in_set(build_person_key(att), attendee_keys)]

    signed_all = signed_both + signed_no_out
    stats = {
        "attendee_total": len(attendees),
        "signed_total": len(signed_all),
        "signed_both": len(signed_both),
        "signed_no_checkout": len(signed_no_out),
        "not_signed_total": len(not_signed),
        "anomaly_total": len(anomalies),
    }
    return {
        "signed": signed_all,
        "signed_both": signed_both,
        "signed_no_checkout": signed_no_out,
        "not_signed": not_signed,
        "anomalies": anomalies,
        "stats": stats,
        "warnings": warnings,
    }


def _att_in_set(k: dict, keyset: set) -> bool:
    if k["id_key"] and ("id", k["id_key"]) in keyset:
        return True
    if k["phone_key"] and ("phone", k["phone_key"]) in keyset:
        return True
    if k["name_key"] and ("name", k["name_key"]) in keyset:
        return True
    return False
