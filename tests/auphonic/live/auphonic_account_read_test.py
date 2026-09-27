# -*- coding: utf-8 -*-
"""The account answers with the two fields the program reads, as it reads them.

Against auphonic.com itself: GET /api/user.json with the key this
machine keeps, which costs no credit. It prints every field the answer
carries -- the name and the value, with what names a person (an address,
a user name, a uuid) shown as its type only -- so what the account
really says stands in the run and not in a guess. Then it checks that
"credits" reads as hours, that "is_paying_user" is there and a truth
value, and that account_credit() hands on the same two.

The limit: which plan the account is on is the owner's, so the test
does not judge free or paying; it only says which the account answered.
"""
PLATFORM_BOUND = True
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import auphonic_ground as ground

ground.gate()

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


# What names a person is shown by its type only, never by its value.
PERSONAL = ("email", "username", "user_id", "uuid", "first_name",
            "last_name", "name", "avatar", "notification_email")


def shown(key, value):
    if key.lower() in PERSONAL or (isinstance(value, str) and "@" in value):
        return "<%s, not shown>" % type(value).__name__
    if isinstance(value, (dict, list)):
        return "<%s with %d entries>" % (type(value).__name__, len(value))
    return repr(value)


def walk(d, lead="      "):
    for k in sorted(d):
        print("%s%-32s %s" % (lead, k, shown(k, d[k])))
        if isinstance(d[k], dict) and k.lower() not in PERSONAL:
            walk(d[k], lead + "  ")


vpm = ground.program()
key, origin = ground.the_key(vpm)

print("1. GET /api/user.json, asked with the key from the %s" % origin)
d, why = None, ""
try:
    d = vpm._parse_json(vpm._curl_call(key, [vpm.AUPHONIC + "/api/user.json"]))
except Exception as e:
    why = " ".join(str(e).split())[:200]
check("auphonic.com answers the account with a JSON object",
      isinstance(d, dict), why or type(d).__name__)
data = (d or {}).get("data") if isinstance(d, dict) else None
check("the answer carries a \"data\" object",
      isinstance(data, dict), "status_code %r" % (d or {}).get("status_code"))
data = data if isinstance(data, dict) else {}
print("      every field of \"data\", %d in all:" % len(data))
walk(data)

print("\n2. The two fields the program reads")
try:
    hours = float(data["credits"])
    why = "%.4f h" % hours
except (KeyError, TypeError, ValueError) as e:
    hours, why = None, "credits = %r (%s)" % (data.get("credits"), e)
check("\"credits\" reads as a number of hours", hours is not None, why)
paying = data.get("is_paying_user", "<missing>")
check("\"is_paying_user\" is there and a truth value",
      isinstance(paying, bool), "is_paying_user = %r" % (paying,))

print("\n3. What account_credit() makes of it")
got = vpm.account_credit(key)
check("account_credit() answers", isinstance(got, dict), repr(got))
got = got or {}
check("it hands on the same hours",
      hours is not None and got.get("hours") is not None
      and abs(got["hours"] - hours) < 1e-6,
      "read %r, handed on %r" % (hours, got.get("hours")))
check("it hands on the same plan",
      isinstance(paying, bool) and got.get("paying") is paying,
      "read %r, handed on %r" % (paying, got.get("paying")))
print("      the account answered: %s"
      % {True: "paying", False: "free plan"}.get(got.get("paying"),
                                                 "no plan said"))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
