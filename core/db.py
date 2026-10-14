import ipaddress
import sqlite3
import time

def db_init(path):
    conn = sqlite3.connect(path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS bans (
            ip          TEXT PRIMARY KEY,
            reason      TEXT,
            origin_node TEXT,
            created_at  INTEGER NOT NULL,
            expires_at  INTEGER
        )
    """)
    conn.commit()
    return conn

def add_ban(conn, ip, seconds, reason="", origin="local", now=None):
    ipaddress.ip_address(ip) #Check if the ip is valid!

    if now is None:
        now = int(time.time())

    expires_at = None if seconds is None else now + seconds

    conn.execute(
        "INSERT OR REPLACE INTO bans (ip, reason, origin_node, created_at, expires_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (ip, reason, origin, now, expires_at),
    )
    conn.commit()

def remove_ban(conn, ip):
    cur = conn.execute("DELETE FROM bans WHERE ip = ?", (ip,))
    conn.commit()
    return cur.rowcount > 0

def list_active(conn, now=None):
    if now is None:
        now = int(time.time())

    cur = conn.execute(
        "SELECT ip, reason, origin_node, created_at, expires_at FROM bans "
        "WHERE expires_at is NULL OR expires_at > ?",
        (now,)
    )
    return cur.fetchall()