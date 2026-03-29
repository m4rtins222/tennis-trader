import sqlite3
import os
from datetime import datetime
from typing import Optional

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "trades.db")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bankroll (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            initial_amount REAL NOT NULL,
            current_amount REAL NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            sport TEXT DEFAULT 'Tenis',
            tournament TEXT,
            player TEXT,
            opponent TEXT,
            market TEXT NOT NULL,
            trade_type TEXT NOT NULL,
            odds REAL NOT NULL,
            stake REAL NOT NULL,
            exit_odds REAL,
            exit_stake REAL,
            pnl REAL,
            method TEXT,
            notes TEXT,
            status TEXT DEFAULT 'open',
            created_at TEXT NOT NULL
        )
    """)
    
    cursor.execute("PRAGMA table_info(trades)")
    columns = [col[1] for col in cursor.fetchall()]
    if "sport" not in columns:
        cursor.execute("ALTER TABLE trades ADD COLUMN sport TEXT DEFAULT 'Tenis'")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS methods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)
    
    cursor.execute("SELECT COUNT(*) FROM bankroll")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO bankroll (initial_amount, current_amount, updated_at) VALUES (?, ?, ?)",
            (1000.0, 1000.0, datetime.now().isoformat())
        )
    
    conn.commit()
    conn.close()

def get_bankroll():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bankroll ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def update_bankroll(amount: float):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE bankroll SET current_amount = ?, updated_at = ? WHERE id = (SELECT id FROM bankroll ORDER BY id DESC LIMIT 1)",
        (amount, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def update_initial_bankroll(initial: float, current: float):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE bankroll SET initial_amount = ?, current_amount = ?, updated_at = ? WHERE id = (SELECT id FROM bankroll ORDER BY id DESC LIMIT 1)",
        (initial, current, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def add_trade(data: dict) -> int | None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO trades (date, sport, tournament, player, opponent, market, trade_type, odds, stake, method, notes, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["date"], data.get("sport", "Tenis"), data.get("tournament"), data.get("player"), data.get("opponent"),
        data["market"], data["trade_type"], data["odds"], data["stake"],
        data.get("method"), data.get("notes"), "open", datetime.now().isoformat()
    ))
    trade_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return trade_id

def close_trade(trade_id: int, exit_odds: float, stake: float, pnl: float) -> tuple[bool, str]:
    trade = get_trade_by_id(trade_id)
    if not trade:
        return False, "Trade não encontrado"
    
    if trade["trade_type"] == "back":
        max_profit = stake * (exit_odds - 1)
    else:
        max_profit = stake * (1 - exit_odds)
    max_loss = -stake
    
    if pnl < max_loss or pnl > max_profit:
        return False, f"Lucro R$ {pnl:.2f} fora do range válido (R$ {max_loss:.2f} a R$ {max_profit:.2f})"
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE trades SET exit_odds = ?, exit_stake = ?, pnl = ?, status = 'closed' WHERE id = ?
    """, (exit_odds, stake, pnl, trade_id))
    conn.commit()
    
    bankroll = get_bankroll()
    if bankroll:
        update_bankroll(bankroll["current_amount"] + stake + pnl)
    conn.close()
    
    return True, "Trade fechado com sucesso"

def get_trades(status: Optional[str] = None, method: Optional[str] = None):
    conn = get_connection()
    query = "SELECT * FROM trades WHERE 1=1"
    params = []
    if status:
        query += " AND status = ?"
        params.append(status)
    if method:
        query += " AND method = ?"
        params.append(method)
    query += " ORDER BY date DESC"
    
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_methods():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM methods ORDER BY name")
    rows = cursor.fetchall()
    conn.close()
    return [row["name"] for row in rows]

def add_method(name: str):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO methods (name) VALUES (?)", (name,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()
    return True

def get_stats():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total_trades,
            SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) as losses,
            SUM(pnl) as total_pnl,
            AVG(pnl) as avg_pnl
        FROM trades WHERE status = 'closed'
    """)
    general = dict(cursor.fetchone())
    
    cursor.execute("""
        SELECT method, 
            COUNT(*) as trades,
            SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
            SUM(pnl) as pnl,
            AVG(CASE WHEN pnl != 0 THEN pnl/stake*100 ELSE 0 END) as yield
        FROM trades WHERE status = 'closed' AND method IS NOT NULL
        GROUP BY method
    """)
    by_method = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("""
        SELECT market,
            COUNT(*) as trades,
            SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
            SUM(pnl) as pnl
        FROM trades WHERE status = 'closed'
        GROUP BY market
    """)
    by_market = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return {"general": general, "by_method": by_method, "by_market": by_market}

def get_trade_by_id(trade_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM trades WHERE id = ?", (trade_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def update_trade(trade_id: int, data: dict):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE trades SET 
            date = ?, tournament = ?, player = ?, opponent = ?, market = ?,
            trade_type = ?, odds = ?, stake = ?, method = ?, notes = ?
        WHERE id = ?
    """, (
        data["date"], data.get("tournament"), data.get("player"), data.get("opponent"),
        data["market"], data["trade_type"], data["odds"], data["stake"],
        data.get("method"), data.get("notes"), trade_id
    ))
    conn.commit()
    conn.close()

def update_trade_pnl(trade_id: int, pnl: float, exit_odds: float | None = None, trade_type: str | None = None, stake: float | None = None, entry_odds: float | None = None) -> tuple[bool, str]:
    trade = get_trade_by_id(trade_id)
    if not trade:
        return False, "Trade não encontrado"
    
    actual_stake = stake if stake is not None else trade["stake"]
    actual_trade_type = trade_type if trade_type is not None else trade["trade_type"]
    actual_entry_odds = entry_odds if entry_odds is not None else trade["odds"]
    actual_exit_odds_val = trade.get("exit_odds")
    actual_exit_odds = exit_odds if exit_odds is not None else (actual_exit_odds_val if actual_exit_odds_val is not None else actual_entry_odds)
    
    if actual_trade_type == "back":
        max_profit = actual_stake * (actual_exit_odds - 1)
    else:
        max_profit = actual_stake * (1 - actual_exit_odds)
    max_loss = -actual_stake
    
    if pnl < max_loss or pnl > max_profit:
        return False, f"Lucro R$ {pnl:.2f} fora do range válido (R$ {max_loss:.2f} a R$ {max_profit:.2f})"
    
    conn = get_connection()
    cursor = conn.cursor()
    if exit_odds and actual_exit_odds_val is None:
        cursor.execute(
            "UPDATE trades SET pnl = ?, exit_odds = ? WHERE id = ?",
            (pnl, exit_odds, trade_id)
        )
    else:
        cursor.execute(
            "UPDATE trades SET pnl = ? WHERE id = ?",
            (pnl, trade_id)
        )
    conn.commit()
    conn.close()
    
    return True, "PNL atualizado"

def delete_trade(trade_id: int):
    trade = get_trade_by_id(trade_id)
    if trade and trade["status"] == "closed" and trade["pnl"] is not None:
        bankroll = get_bankroll()
        if bankroll:
            update_bankroll(bankroll["current_amount"] - trade["pnl"])
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM trades WHERE id = ?", (trade_id,))
    conn.commit()
    conn.close()
