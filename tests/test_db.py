import pytest
from core.db import db_init, add_ban, remove_ban, list_active

YEAR = 365 * 86400

@pytest.fixture

def conn(tmp_path):
    return db_init(tmp_path / "test.db")

def active_ips(conn, now=None):
   return [row[0] for row in list_active(conn, now)]

def test_add_and_list(conn):
    add_ban(conn, "1.2.3.4", 3600, "test")
    assert "1.2.3.4" in active_ips(conn)

def test_expired_not_listed(conn):
    add_ban(conn, "1.2.3.4", 3600, now=1000)
    assert "1.2.3.4" not in active_ips(conn, now=1000 + YEAR)

def test_perm_always_active(conn):
    add_ban(conn, "1.2.3.4", None, now=1000)
    assert "1.2.3.4" in active_ips(conn, now=1000 + 10 * YEAR)

def test_unban(conn):
    add_ban(conn, "1.2.3.4", 1600)
    assert remove_ban(conn, "1.2.3.4") is True
    assert "1.2.3.4" not in active_ips(conn)
    assert remove_ban(conn, "1.2.3.4") is False

def test_invalid_ip(conn):
    with pytest.raises(ValueError):
        add_ban(conn, "test", 3600)

def test_reban_extends(conn):
    add_ban(conn, "1.2.3.4", 60, now=1000)
    add_ban(conn, "1.2.3.4", 3600, now=1000)
    assert "1.2.3.4" in active_ips(conn, now=1000 + 120)