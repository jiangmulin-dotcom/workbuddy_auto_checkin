#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""在 Actions 内运行的诊断：判定 401 是IP 拦截还是 token 问题。"""
import json, os, ssl, urllib.request, urllib.error, datetime

token = os.environ.get("WB_ACCESS_TOKEN", "")
base = "https://copilot.tencent.com"
h = {"Accept": "application/json", "Authorization": "Bearer " + token,
     "Content-Type": "application/json", "User-Agent": "WorkBuddy"}


def probe(label, url, headers):
    req = urllib.request.Request(url, headers=headers, method="POST",
                                 data=json.dumps({"timestamp": 0}).encode())
    try:
        with urllib.request.urlopen(req, timeout=15,
                context=ssl.create_default_context()) as r:
            print("[%s] HTTP %s | %s" % (label, r.status,
                  r.read().decode('utf-8','replace')[:150]))
    except urllib.error.HTTPError as e:
        print("[%s] HTTP %s | %s" % (label, e.code,
              e.read().decode('utf-8','replace')[:150].replace("\n"," ")))
    except Exception as e:
        print("[%s] ERR | %s: %s" % (label, type(e).__name__, e))


print("runner 时间:", datetime.datetime.utcnow().isoformat())
print("token 长度:", len(token), "| 前缀:", token[:6] if token else "(空)")
print("token 末尾:", token[-4:] if token else "(空)")
print()

probe("A_带token", base + "/v2/billing/meter/checkin-activity-status", h)
probe("B_无token", base + "/v2/billing/meter/checkin-activity-status",
      {k: v for k, v in h.items() if k != "Authorization"})
probe("C_备用域名", "https://www.codebuddy.cn"
      "/v2/billing/meter/checkin-activity-status", h)
# 连首页都访问不了，说明是IP 层拦截
probe("D_无鉴权访问首页", base + "/", {"User-Agent": "WorkBuddy"})