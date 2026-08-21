# -*- coding: utf-8 -*-
"""gdzyz 管理后台 API 客户端

接口来自对前端 JS 的逆向分析，具体请求参数/返回字段在联调时通过调试模式校准。
"""
import json
import logging
import os
import time

import requests

from config import BASE_URL, TIMEOUT, PAGE_SIZE

logger = logging.getLogger("gdzyz")

# 调试模式：把最近一次原始响应写到 debug_last.json，方便校准字段
DEBUG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "debug_last.json")


class GdzyzError(Exception):
    pass


class GdzyzClient:
    def __init__(self, token: str):
        self.token = token
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {token}",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0 Safari/537.36 Edg/120.0"
            ),
            "Accept": "application/json, text/plain, */*",
            "Referer": BASE_URL + "/admin/",
        })

    # ---------- 基础请求 ----------
    def _request(self, method: str, path: str, params=None, data=None, raw=False,
                 timeout: int = TIMEOUT, _debug_tag: str = ""):
        url = BASE_URL + path
        try:
            resp = self.session.request(
                method, url, params=params, data=data, timeout=timeout
            )
        except requests.RequestException as e:
            raise GdzyzError(f"网络请求失败: {e}")

        if raw:
            return resp

        try:
            body = resp.json()
        except ValueError:
            raise GdzyzError(f"接口返回非 JSON（HTTP {resp.status_code}）: {resp.text[:300]}")

        # 保存调试样例
        try:
            with open(DEBUG_FILE, "w", encoding="utf-8") as f:
                json.dump({
                    "tag": _debug_tag or path,
                    "request": {"method": method, "url": path, "params": params, "data": data},
                    "status": resp.status_code,
                    "response": body,
                }, f, ensure_ascii=False, indent=2, default=str)
        except Exception:
            pass

        # code != 成功 视为业务错误（本网站成功码为 "1"）
        SUCCESS_CODES = (0, 1, 200, "0", "1", "200")
        code = body.get("code")
        if resp.status_code >= 400:
            raise GdzyzError(f"HTTP {resp.status_code}: {body.get('msg') or body.get('message') or body}")
        if code is not None and code not in SUCCESS_CODES:
            msg = body.get("msg") or body.get("message") or str(body.get("code"))
            # 401/403 特殊提示
            if code in (401, 403, "401", "403", 12022):
                raise GdzyzError(f"登录已过期或无权限（{code}），请重新登录")
            raise GdzyzError(f"业务错误 {code}: {msg}")
        return body

    def _extract_list(self, body: dict) -> list:
        """从响应中尽力提取列表数据，兼容多种返回结构"""
        if not isinstance(body, dict):
            return []
        data = body.get("data")
        if data is None:
            return []
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            for key in ("list", "records", "rows", "items", "dataList", "result"):
                v = data.get(key)
                if isinstance(v, list):
                    return v
            # 考勤接口结构：data.page.records
            page = data.get("page")
            if isinstance(page, dict):
                for key in ("records", "list", "rows"):
                    v = page.get(key)
                    if isinstance(v, list):
                        return v
        return []

    def _extract_total(self, body: dict) -> int:
        """尽力提取总数"""
        try:
            data = body.get("data")
            if isinstance(data, dict):
                for key in ("total", "totalCount", "totalRecord", "count", "totalNum"):
                    if isinstance(data.get(key), (int, float)):
                        return int(data[key])
                # 考勤接口：data.page.total
                page = data.get("page")
                if isinstance(page, dict):
                    for key in ("total", "totalCount", "records"):
                        if key == "records" and isinstance(page.get(key), list):
                            return len(page[key])
                        if isinstance(page.get(key), (int, float)):
                            return int(page[key])
            elif isinstance(data, list):
                return len(data)
        except Exception:
            pass
        return -1

    # ---------- 活动查询 ----------
    def get_activities(self, params: dict | None = None) -> dict:
        """活动查询：findMissionList

        注意：必须带完整参数（含 type=1 及空筛选字段），否则服务端返回 500。
        返回 {list, total, raw_body}
        """
        default_params = {
            "type": 1, "selectedLabelIdList": "", "missionId": "",
            "subject": "", "contactName": "", "contactPhone": "",
            "missionType": "", "serviceTimeType": "", "focusState": "",
            "districtId": "", "beginDateInput": "", "endDateInput": "",
            "districtIdTxt": "", "pageIndex": 1, "pageSize": 10,
        }
        if params:
            default_params.update(params)
        body = self._request("GET", "/v2/api/gdzyz/manage/pc/mission/findMissionList",
                             params=default_params, _debug_tag="findMissionList")
        return {
            "list": self._extract_list(body),
            "total": self._extract_total(body),
            "raw": body,
        }

    # ---------- 活动详情 ----------
    def get_mission_detail(self, mission_id) -> dict:
        body = self._request("GET", "/v2/api/gdzyz/manage/pc/mission/viewMission",
                             params={"missionId": mission_id}, _debug_tag="viewMission")
        return body

    # ---------- 人员名单（邀请录用页） ----------
    def get_personal_list(self, mission_id, page_index: int = 1, page_size: int = PAGE_SIZE) -> dict:
        """参加人员名单 getMPList，返回 {list, total, raw}"""
        params = {
            "missionId": mission_id,
            "pageIndex": page_index,
            "pageSize": page_size,
        }
        body = self._request("GET", "/v2/api/gdzyz/manage/pc/mission/personal/getMPList",
                             params=params, _debug_tag=f"getMPList-m{mission_id}-p{page_index}")
        return {
            "list": self._extract_list(body),
            "total": self._extract_total(body),
            "raw": body,
        }

    def get_all_personal(self, mission_id, max_pages: int = 50) -> list:
        """循环翻页拿全部参加人员名单"""
        all_items = []
        page = 1
        while page <= max_pages:
            result = self.get_personal_list(mission_id, page_index=page)
            items = result["list"]
            all_items.extend(items)
            total = result["total"]
            # 分页终止条件：未返回数据 / 总数可判断且已拿完
            if not items:
                break
            if total > 0 and len(all_items) >= total:
                break
            # 避免死循环：若返回不足一页则停止
            if len(items) < PAGE_SIZE and total < 0:
                break
            page += 1
            time.sleep(0.2)
        return all_items

    def export_personal(self, mission_id, save_path: str) -> str:
        """导出名单 Excel（getMPListExport），保存到 save_path，返回路径"""
        params = {"missionId": mission_id}
        resp = self._request("GET", "/v2/api/gdzyz/manage/pc/mission/personal/getMPListExport",
                             params=params, raw=True, _debug_tag="getMPListExport")
        if resp.status_code != 200:
            raise GdzyzError(f"导出失败 HTTP {resp.status_code}: {resp.text[:200]}")
        with open(save_path, "wb") as f:
            f.write(resp.content)
        return save_path

    # ---------- 活动场次 ----------
    def get_mission_times(self, mission_id, page_index: int = 1, page_size: int = 50) -> dict:
        """活动场次列表 findMissionTimesList，返回 {list, total, raw}"""
        params = {"missionId": mission_id, "pageIndex": page_index, "pageSize": page_size}
        body = self._request("GET", "/v2/api/gdzyz/manage/pc/mission/findMissionTimesList",
                             params=params, _debug_tag=f"findMissionTimesList-m{mission_id}")
        return {
            "list": self._extract_list(body),
            "total": self._extract_total(body),
            "raw": body,
        }

    # ---------- 考勤情况 ----------
    def get_attendance_list(self, mission_id, times_info_id=None,
                            page_index: int = 1, page_size: int = PAGE_SIZE) -> dict:
        """考勤情况 getAttendanceList（已签到/签退人员）

        注意：实测必须传 timesInfoId（场次ID），否则返回空。
        """
        params = {
            "missionId": mission_id,
            "timesInfoId": times_info_id,
            "pageIndex": page_index,
            "pageSize": page_size,
        }
        body = self._request("GET", "/v2/api/gdzyz/manage/pc/mission/attendance/getAttendanceList",
                             params=params, _debug_tag=f"getAttendanceList-m{mission_id}-t{times_info_id}-p{page_index}")
        return {
            "list": self._extract_list(body),
            "total": self._extract_total(body),
            "raw": body,
        }

    def get_all_attendance(self, mission_id, max_pages: int = 50) -> list:
        """获取活动全部场次的考勤记录（合并）

        流程：先拿场次列表，再逐个场次查考勤。
        """
        # 1. 获取场次列表
        times = self.get_mission_times(mission_id)
        times_list = times.get("list") or []
        if not times_list:
            # 无场次信息时尝试不带 timesInfoId 查询（部分活动可能支持）
            return self._get_attendance_pages(mission_id, None, max_pages)

        # 2. 对每个场次查考勤并合并
        all_items = []
        for t in times_list:
            tid = t.get("id")
            if not tid:
                continue
            items = self._get_attendance_pages(mission_id, tid, max_pages)
            all_items.extend(items)
            time.sleep(0.2)
        return all_items

    def _get_attendance_pages(self, mission_id, times_info_id, max_pages: int) -> list:
        """单个场次的考勤翻页"""
        all_items = []
        page = 1
        while page <= max_pages:
            result = self.get_attendance_list(mission_id, times_info_id=times_info_id,
                                              page_index=page)
            items = result["list"]
            all_items.extend(items)
            total = result["total"]
            if not items:
                break
            if total > 0 and len(all_items) >= total:
                break
            if len(items) < PAGE_SIZE and total < 0:
                break
            page += 1
            time.sleep(0.2)
        return all_items

    # ---------- 权限 ----------
    def get_mission_permission(self, mission_id) -> dict:
        body = self._request("GET", "/v2/api/gdzyz/manage/pc/mission/info/permission",
                             params={"missionId": mission_id}, _debug_tag="missionPermission")
        return body

    # ---------- 登录有效性 ----------
    def check_login(self) -> bool:
        """调一个轻量接口验证 token 是否有效"""
        try:
            body = self._request("GET", "/v2/api/gdzyz/manage/pc/usersAdmin/auditStatic",
                                 timeout=15, _debug_tag="checkLogin")
            return True
        except GdzyzError as e:
            if "登录" in str(e) or "401" in str(e) or "403" in str(e):
                return False
            # 其他错误（如参数错误）说明 token 有效但接口需要参数
            logger.warning("check_login 异常（token 可能有效）: %s", e)
            return True
        except Exception:
            return False


def load_debug_last() -> dict:
    try:
        with open(DEBUG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def dedup_records(items: list, id_keys=("userid", "missionPersonlId", "missionServiceLogId")) -> tuple:
    """按唯一标识去重，防止名单/考勤重复导致人数虚高

    优先使用 id_keys 中的字段（如 userid），字段缺失时用姓名+手机号兜底。
    返回 (去重后列表, 被移除的重复条数)
    """
    seen = set()
    unique = []
    removed = 0
    for it in items:
        if not isinstance(it, dict):
            unique.append(it)
            continue
        key = None
        for k in id_keys:
            v = it.get(k)
            if v not in (None, ""):
                key = f"{k}:{v}"
                break
        if key is None:
            name = it.get("hireUsername") or it.get("userName") or it.get("realName") or ""
            mobile = it.get("mobile") or ""
            key = f"name:{name}|mobile:{mobile}"
        if key in seen:
            removed += 1
        else:
            seen.add(key)
            unique.append(it)
    return unique, removed
