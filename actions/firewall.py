import ipaddress
import os
import shutil
import subprocess

from core.duration import to_nft

FAMILY = "inet"
TABLE = "knockwatch"
SET = "banned"

# Az első két sor teszi idempotenssé: létrehozza (ha nincs), törli, majd újraépíti
RULESET = f"""
table {FAMILY} {TABLE} {{}}
delete table {FAMILY} {TABLE}
table {FAMILY} {TABLE} {{
    set {SET} {{
        type ipv4_addr
        flags timeout
    }}
    chain input {{
        type filter hook input priority -10; policy accept;
        ip saddr @{SET} drop
    }}
}}
"""


class FirewallError(Exception):
    pass


def check_requirements():
    if shutil.which("nft") is None:
        raise FirewallError("nftables nincs telepítve. Telepítsd: sudo apt install nftables")
    if os.geteuid() != 0:
        raise FirewallError("Root jog szükséges (futtasd sudo-val).")


def _validate_ip(ip):
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        raise FirewallError(f"Érvénytelen IP-cím: {ip}")
    if addr.version != 4:
        raise FirewallError("IPv6 még nem támogatott.")
    return str(addr)


def build_ban_cmd(ip, seconds):
    element = [ip]
    if seconds is not None:
        element += ["timeout", to_nft(seconds)]
    return ["add", "element", FAMILY, TABLE, SET, "{", *element, "}"]


def build_unban_cmd(ip):
    return ["delete", "element", FAMILY, TABLE, SET, "{", ip, "}"]


def _run(args, dry_run, input_text=None, check=True):
    if dry_run:
        print("[dry-run] nft", " ".join(args))
        if input_text:
            print(input_text)
        return True

    result = subprocess.run(
        ["nft", *args], input=input_text, text=True, capture_output=True
    )
    if check and result.returncode != 0:
        raise FirewallError(f"nft hiba: {result.stderr.strip()}")
    return result.returncode == 0


def setup(dry_run=False):
    if not dry_run:
        check_requirements()
    _run(["-f", "-"], dry_run, input_text=RULESET)


def ban(ip, seconds, dry_run=False):
    ip = _validate_ip(ip)
    if not dry_run:
        check_requirements()
    # ha már bent van, előbb kivesszük, hogy a timeout frissüljön
    _run(build_unban_cmd(ip), dry_run, check=False)
    _run(build_ban_cmd(ip, seconds), dry_run)


def unban(ip, dry_run=False):
    ip = _validate_ip(ip)
    if not dry_run:
        check_requirements()
    return _run(build_unban_cmd(ip), dry_run, check=False)