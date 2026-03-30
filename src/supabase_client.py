import os
from supabase import create_client, Client
from datetime import datetime
from typing import Optional

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://kntstvebwuhvzelizcqx.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtudHN0dmVid3VodnplbGl6Y3F4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ4NTk5MDMsImV4cCI6MjA5MDQzNTkwM30.nIfluzn3rjKv3pqKYBNwVvnaK4I5PsYXe1NobTFmbZo")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def init_db():
    pass

def get_bankroll():
    response = supabase.table("bankroll").select("*").order("id", desc=True).limit(1).execute()
    if response.data:
        return response.data[0]
    return None

def update_bankroll(amount: float):
    bankroll = get_bankroll()
    if bankroll:
        supabase.table("bankroll").update({
            "current_amount": amount,
            "updated_at": datetime.now().isoformat()
        }).eq("id", bankroll["id"]).execute()

def update_initial_bankroll(initial: float, current: float):
    bankroll = get_bankroll()
    if bankroll:
        supabase.table("bankroll").update({
            "initial_amount": initial,
            "current_amount": current,
            "updated_at": datetime.now().isoformat()
        }).eq("id", bankroll["id"]).execute()
    else:
        supabase.table("bankroll").insert({
            "initial_amount": initial,
            "current_amount": current,
            "updated_at": datetime.now().isoformat()
        }).execute()

def add_trade(data: dict) -> int | None:
    response = supabase.table("trades").insert({
        "date": data["date"],
        "sport": data.get("sport", "Tenis"),
        "tournament": data.get("tournament"),
        "player": data.get("player"),
        "opponent": data.get("opponent"),
        "market": data["market"],
        "trade_type": data["trade_type"],
        "odds": data["odds"],
        "stake": data["stake"],
        "method": data.get("method"),
        "notes": data.get("notes"),
        "status": "open",
        "created_at": datetime.now().isoformat()
    }).execute()
    return response.data[0]["id"] if response.data else None

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
    
    supabase.table("trades").update({
        "exit_odds": exit_odds,
        "exit_stake": stake,
        "pnl": pnl,
        "status": "closed"
    }).eq("id", trade_id).execute()
    
    bankroll = get_bankroll()
    if bankroll:
        update_bankroll(bankroll["current_amount"] + stake + pnl)
    
    return True, "Trade fechado com sucesso"

def get_trades(status: Optional[str] = None, method: Optional[str] = None):
    query = supabase.table("trades").select("*")
    if status:
        query = query.eq("status", status)
    if method:
        query = query.eq("method", method)
    response = query.order("date", desc=True).execute()
    return response.data

def get_methods():
    response = supabase.table("methods").select("name").order("name").execute()
    return [row["name"] for row in response.data]

def add_method(name: str):
    supabase.table("methods").insert({"name": name}).execute()
    return True

def get_stats():
    closed_trades = supabase.table("trades").select("*").eq("status", "closed").execute().data
    
    total_trades = len(closed_trades)
    wins = sum(1 for t in closed_trades if t.get("pnl", 0) > 0)
    losses = sum(1 for t in closed_trades if t.get("pnl", 0) < 0)
    total_pnl = sum(t.get("pnl", 0) for t in closed_trades)
    
    by_method = {}
    by_market = {}
    
    for t in closed_trades:
        method = t.get("method")
        if method:
            if method not in by_method:
                by_method[method] = {"method": method, "trades": 0, "wins": 0, "pnl": 0}
            by_method[method]["trades"] += 1
            if t.get("pnl", 0) > 0:
                by_method[method]["wins"] += 1
            by_method[method]["pnl"] += t.get("pnl", 0)
        
        market = t.get("market")
        if market:
            if market not in by_market:
                by_market[market] = {"market": market, "trades": 0, "wins": 0, "pnl": 0}
            by_market[market]["trades"] += 1
            if t.get("pnl", 0) > 0:
                by_market[market]["wins"] += 1
            by_market[market]["pnl"] += t.get("pnl", 0)
    
    return {
        "general": {
            "total_trades": total_trades,
            "wins": wins,
            "losses": losses,
            "total_pnl": total_pnl,
            "avg_pnl": total_pnl / total_trades if total_trades > 0 else 0
        },
        "by_method": list(by_method.values()),
        "by_market": list(by_market.values())
    }

def get_trade_by_id(trade_id: int):
    response = supabase.table("trades").select("*").eq("id", trade_id).execute()
    return response.data[0] if response.data else None

def update_trade(trade_id: int, data: dict):
    supabase.table("trades").update({
        "date": data["date"],
        "tournament": data.get("tournament"),
        "player": data.get("player"),
        "opponent": data.get("opponent"),
        "market": data["market"],
        "trade_type": data["trade_type"],
        "odds": data["odds"],
        "stake": data["stake"],
        "method": data.get("method"),
        "notes": data.get("notes")
    }).eq("id", trade_id).execute()

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
    
    update_data = {"pnl": pnl}
    if exit_odds:
        update_data["exit_odds"] = exit_odds
    
    supabase.table("trades").update(update_data).eq("id", trade_id).execute()
    
    return True, "PNL atualizado"

def delete_trade(trade_id: int):
    trade = get_trade_by_id(trade_id)
    if trade and trade["status"] == "closed" and trade.get("pnl") is not None:
        bankroll = get_bankroll()
        if bankroll:
            update_bankroll(bankroll["current_amount"] - trade["pnl"])
    
    supabase.table("trades").delete().eq("id", trade_id).execute()

def get_players(sport: str = "Tenis"):
    response = supabase.table("players").select("*").eq("sport", sport).order("name").execute()
    return response.data

def add_player(name: str, sport: str = "Tenis"):
    supabase.table("players").insert({
        "name": name,
        "sport": sport,
        "created_at": datetime.now().isoformat()
    }).execute()
    return True

def update_player(player_id: int, name: str):
    supabase.table("players").update({"name": name}).eq("id", player_id).execute()

def delete_player(player_id: int):
    supabase.table("players").delete().eq("id", player_id).execute()

def export_data():
    trades = supabase.table("trades").select("*").execute().data
    players = supabase.table("players").select("*").execute().data
    bankroll = get_bankroll()
    methods = get_methods()
    return {"trades": trades, "players": players, "bankroll": bankroll, "methods": methods}

def import_data(data: dict):
    if "bankroll" in data and data["bankroll"]:
        b = data["bankroll"]
        bankroll = get_bankroll()
        if bankroll:
            supabase.table("bankroll").update({
                "initial_amount": b.get("initial_amount", bankroll["initial_amount"]),
                "current_amount": b.get("current_amount", bankroll["current_amount"]),
                "updated_at": datetime.now().isoformat()
            }).eq("id", bankroll["id"]).execute()
        else:
            supabase.table("bankroll").insert({
                "initial_amount": b.get("initial_amount", 1000),
                "current_amount": b.get("current_amount", 1000),
                "updated_at": datetime.now().isoformat()
            }).execute()
    
    if "methods" in data:
        for m in data["methods"]:
            add_method(m)
    
    if "players" in data:
        for p in data["players"]:
            add_player(p.get("name", ""), p.get("sport", "Tenis"))
    
    if "trades" in data:
        for t in data["trades"]:
            supabase.table("trades").insert({
                "date": t.get("date"),
                "sport": t.get("sport", "Tenis"),
                "tournament": t.get("tournament"),
                "player": t.get("player"),
                "opponent": t.get("opponent"),
                "market": t.get("market"),
                "trade_type": t.get("trade_type"),
                "odds": t.get("odds"),
                "stake": t.get("stake"),
                "exit_odds": t.get("exit_odds"),
                "exit_stake": t.get("exit_stake"),
                "pnl": t.get("pnl"),
                "method": t.get("method"),
                "notes": t.get("notes"),
                "status": t.get("status", "open"),
                "created_at": t.get("created_at", datetime.now().isoformat())
            }).execute()
