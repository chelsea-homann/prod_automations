"""
Skills 4.2 / 4.3 - Go tournament pairing & results (圍棋賽事配對與成績)
==================================================================
Working implementation of the tournament-operations skills from the Haifong
Go Academy skills book (SKILLS_BOOK_HAIFONG.md):

  * pairing (配對編排) for three formats:
      - single elimination  單淘汰 (Haifong Cup / 海峰盃 style)
      - swiss               瑞士制 (same-score, avoid rematches)
      - round robin         循環賽
  * results & standings (成績與名次) with Sum-of-Opponent-Scores (SOS) tiebreak
  * Go handicap (讓子) derived from rank difference; the weaker player takes black

Design
------
The algorithm core works on plain ``list[dict]`` players so it runs and is
testable without pandas. Thin pandas wrappers (``pair_round_df`` /
``standings_df``) accept and return DataFrames to match the skills book and the
rest of the skills/ package. pandas is imported lazily so importing this module
never requires it.

Player dict shape
-----------------
    {"name": "王小明", "rank": "3d", "rating": 2100}   # rating optional
``rank`` accepts dan/kyu in English or Chinese: "3d", "5k", "3段", "10級", "1p".

Run ``python -m skills.tournament`` for a self-test (no pandas needed).
"""

import re
import itertools

BYE = "__BYE__"  # sentinel opponent meaning "no game; player advances"


# --------------------------------------------------------------------------- #
# Rank / handicap helpers (段級位 與 讓子)
# --------------------------------------------------------------------------- #
def parse_rank(rank):
    """
    Convert a Go rank to a strength index where +1 == one stone stronger.

    Scale (1 rank = 1 stone, no zero between 1k and 1d):
        1d -> 1, 2d -> 2, ...      (dan / 段, and pro / 段位 'p' treated as dan)
        1k -> 0, 2k -> -1, 3k -> -2 (kyu / 級 / 级)
    Returns None if the rank can't be parsed.
    """
    if rank is None:
        return None
    s = str(rank).strip().lower()
    m = re.match(r"^(\d+)\s*(d|k|p|段|级|級|段位)?$", s)
    if not m:
        return None
    n = int(m.group(1))
    unit = m.group(2) or "d"
    if unit in ("d", "p", "段", "段位"):   # dan / pro
        return n
    return 1 - n                            # kyu: 1k=0, 2k=-1, ...


def handicap(rank_a, rank_b, cap=9):
    """
    Return (stones, black_is_a) for a game between two ranks.

    The weaker player takes black; stones = rank gap (capped, max 9).
    A gap of 0 or 1 is an even game (0 stones). Returns (0, True) when either
    rank is unknown so play can proceed even-game.
    """
    sa, sb = parse_rank(rank_a), parse_rank(rank_b)
    if sa is None or sb is None or sa == sb:
        return 0, True
    gap = abs(sa - sb)
    stones = 0 if gap <= 1 else min(gap, cap)
    black_is_a = sa < sb  # weaker (lower strength) plays black
    return stones, black_is_a


def _game_row(table, a, b):
    """Build one pairing row (table, black, white, handicap) from two players."""
    if b is BYE or b is None:
        return {"table": table, "black": a["name"], "white": BYE,
                "handicap": 0, "result": "bye"}
    if a is BYE or a is None:
        return {"table": table, "black": b["name"], "white": BYE,
                "handicap": 0, "result": "bye"}
    stones, black_is_a = handicap(a.get("rank"), b.get("rank"))
    black, white = (a, b) if black_is_a else (b, a)
    return {"table": table, "black": black["name"], "white": white["name"],
            "handicap": stones, "result": ""}


# --------------------------------------------------------------------------- #
# Skill 4.2 - pairing (配對編排)
# --------------------------------------------------------------------------- #
def _seed_order(size):
    """Standard single-elimination bracket seed order for a power-of-two size."""
    seeds = [1, 2]
    while len(seeds) < size:
        m = len(seeds) * 2
        seeds = list(itertools.chain.from_iterable(
            (s, m + 1 - s) for s in seeds))
    return seeds


def single_elimination(players):
    """
    Round-1 bracket for single elimination (單淘汰, Haifong Cup style).

    ``players`` should be pre-seeded strongest-first (use ``seed_players``).
    Byes are given to the top seeds when the field isn't a power of two.
    """
    count = len(players)
    if count < 2:
        return []
    size = 1
    while size < count:
        size *= 2
    order = _seed_order(size)

    rows, table = [], 1
    for i in range(0, size, 2):
        seed_a, seed_b = order[i], order[i + 1]
        pa = players[seed_a - 1] if seed_a <= count else BYE
        pb = players[seed_b - 1] if seed_b <= count else BYE
        rows.append(_game_row(table, pa, pb))
        table += 1
    return rows


def swiss(players, history=None):
    """
    One round of Swiss pairings (瑞士制): pair players of similar score while
    avoiding rematches; the lowest player gets a bye when the field is odd.

    Parameters
    ----------
    players : list[dict]  each may carry "score" (default 0) and "rating".
    history : set[frozenset[str]]  name-pairs already played.

    Returns the round's pairing rows.
    """
    history = history or set()
    ranked = sorted(players,
                    key=lambda p: (-p.get("score", 0), -(p.get("rating") or 0),
                                   p.get("name", "")))
    pool = list(ranked)
    rows, table = [], 1

    # Odd field: bye to the lowest-scoring player who hasn't had one.
    if len(pool) % 2 == 1:
        for p in reversed(pool):
            if not p.get("had_bye"):
                pool.remove(p)
                rows.append(_game_row(0, p, BYE))
                break
        else:  # everyone already had a bye; give it to the very last
            rows.append(_game_row(0, pool.pop(), BYE))

    # Greedy slide pairing: first unpaired meets the nearest legal opponent.
    while pool:
        a = pool.pop(0)
        opponent = next(
            (q for q in pool
             if frozenset((a["name"], q["name"])) not in history), None)
        if opponent is None:           # all rematches -> take the nearest
            opponent = pool[0]
        pool.remove(opponent)
        rows.append(_game_row(table, a, opponent))
        table += 1

    # Number the bye row(s) last so real games keep tables 1..n.
    for r in rows:
        if r["white"] is BYE and r["table"] == 0:
            r["table"] = table
            table += 1
    return rows


def round_robin(players):
    """
    Full round-robin schedule (循環賽) via the circle method.

    Returns ``list[list[row]]`` - one pairing list per round. With an odd field
    a bye rotates through the players.
    """
    ps = list(players)
    if len(ps) < 2:
        return []
    if len(ps) % 2 == 1:
        ps.append(BYE)
    n = len(ps)
    fixed, rotating = ps[0], ps[1:]
    rounds = []
    for _ in range(n - 1):
        order = [fixed] + rotating
        pairs, table = [], 1
        for i in range(n // 2):
            a, b = order[i], order[n - 1 - i]
            row = _game_row(table, a, b)
            pairs.append(row)
            if row["white"] is not BYE:
                table += 1
        rounds.append(pairs)
        rotating = [rotating[-1]] + rotating[:-1]  # rotate
    return rounds


def seed_players(players):
    """Sort players strongest-first by rating then rank, for bracket seeding."""
    return sorted(
        players,
        key=lambda p: (-(p.get("rating") or 0), -(parse_rank(p.get("rank")) or -99)))


def pair_round(players, system="swiss", history=None):
    """
    Skill 4.2 dispatcher. ``system`` in {"single_elim", "swiss", "round_robin"}.

    Returns pairing rows; for "round_robin" returns a list of rounds.
    """
    if system in ("single_elim", "single_elimination"):
        return single_elimination(seed_players(players))
    if system == "swiss":
        return swiss(players, history)
    if system in ("round_robin", "rr"):
        return round_robin(players)
    raise ValueError(f"unknown system: {system!r}")


# --------------------------------------------------------------------------- #
# Skill 4.3 - results & standings (成績與名次)
# --------------------------------------------------------------------------- #
def update_standings(players, results, win=1.0, draw=0.5):
    """
    Compute standings from played results.

    Parameters
    ----------
    players : list[dict]   needs "name" (and optionally "rank").
    results : list[dict]   each {"black": name, "white": name, "winner": name}
                           winner may be a player name, "draw", or BYE's player
                           (a bye counts as a win).
    Tiebreak: Sum of Opponent Scores (SOS), then head-to-head points.

    Returns standings rows sorted best-first, each with rank/points/wins/
    losses/draws/sos and a 1-based "place".
    """
    stats = {p["name"]: {"name": p["name"], "rank": p.get("rank", ""),
                         "points": 0.0, "wins": 0, "losses": 0, "draws": 0,
                         "opponents": []} for p in players}

    def ensure(name):
        if name not in stats:
            stats[name] = {"name": name, "rank": "", "points": 0.0, "wins": 0,
                           "losses": 0, "draws": 0, "opponents": []}
        return stats[name]

    for g in results:
        black, white, winner = g.get("black"), g.get("white"), g.get("winner")
        if white is BYE or white is None:          # bye = full-point win
            s = ensure(black)
            s["points"] += win
            s["wins"] += 1
            continue
        sb, sw = ensure(black), ensure(white)
        sb["opponents"].append(white)
        sw["opponents"].append(black)
        if winner == "draw":
            sb["points"] += draw
            sw["points"] += draw
            sb["draws"] += 1
            sw["draws"] += 1
        elif winner == black:
            sb["points"] += win
            sb["wins"] += 1
            sw["losses"] += 1
        elif winner == white:
            sw["points"] += win
            sw["wins"] += 1
            sb["losses"] += 1

    # SOS = sum of each opponent's total points.
    for s in stats.values():
        s["sos"] = round(sum(stats[o]["points"] for o in s["opponents"]
                             if o in stats), 1)
        s["opponents"] = ";".join(s["opponents"])

    standings = sorted(stats.values(),
                       key=lambda s: (-s["points"], -s["sos"], s["name"]))
    for i, s in enumerate(standings, 1):
        s["place"] = i
    return standings


# --------------------------------------------------------------------------- #
# pandas wrappers (optional - match the skills book's DataFrame interface)
# --------------------------------------------------------------------------- #
def _to_records(df):
    return df.to_dict("records") if hasattr(df, "to_dict") else df


def pair_round_df(players, system="swiss", history=None):
    """DataFrame-in / DataFrame-out wrapper around :func:`pair_round`."""
    import pandas as pd
    rows = pair_round(_to_records(players), system=system, history=history)
    if rows and isinstance(rows[0], list):          # round_robin -> tag rounds
        tagged = [dict(r, round=i) for i, rnd in enumerate(rows, 1) for r in rnd]
        return pd.DataFrame(tagged)
    return pd.DataFrame(rows)


def standings_df(players, results, **kwargs):
    """DataFrame-in / DataFrame-out wrapper around :func:`update_standings`."""
    import pandas as pd
    rows = update_standings(_to_records(players), _to_records(results), **kwargs)
    cols = ["place", "name", "rank", "points", "wins", "losses", "draws", "sos"]
    return pd.DataFrame(rows)[cols]


# --------------------------------------------------------------------------- #
# Self-test (no pandas required):  python -m skills.tournament
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    roster = [
        {"name": "Aki",  "rank": "5d", "rating": 2400},
        {"name": "Bo",   "rank": "3d", "rating": 2200},
        {"name": "Chen", "rank": "1d", "rating": 2000},
        {"name": "Dai",  "rank": "2k", "rating": 1700},
        {"name": "Eun",  "rank": "4d", "rating": 2300},
    ]

    print("== handicap ==")
    print("5d vs 2k ->", handicap("5d", "2k"))   # weaker (Dai) takes black
    assert handicap("5d", "5d") == (0, True)
    assert handicap("5d", "2k")[0] == 6          # 5 - (-1) = 6 stones

    print("\n== single elimination (5 players -> bracket of 8, 3 byes) ==")
    se = single_elimination(seed_players(roster))
    for r in se:
        print(r)
    assert len(se) == 4

    print("\n== swiss round 1 (odd -> one bye) ==")
    for p in roster:
        p["score"] = 0
    sw = swiss(roster, history=set())
    for r in sw:
        print(r)
    assert sum(1 for r in sw if r["white"] is BYE) == 1
    real = [r for r in sw if r["white"] is not BYE]
    assert len({r["black"] for r in real} | {r["white"] for r in real}) == len(real) * 2

    print("\n== round robin (5 players -> 5 rounds) ==")
    rr = round_robin(roster)
    assert len(rr) == 5
    print(f"rounds: {len(rr)}, games in round 1: "
          f"{sum(1 for r in rr[0] if r['white'] is not BYE)}")

    print("\n== standings ==")
    results = [
        {"black": "Chen", "white": "Aki",  "winner": "Aki"},
        {"black": "Dai",  "white": "Bo",   "winner": "Bo"},
        {"black": "Eun",  "white": BYE,    "winner": "Eun"},
        {"black": "Bo",   "white": "Aki",  "winner": "draw"},
    ]
    table = update_standings(roster, results)
    for s in table:
        print(f"{s['place']}. {s['name']:5} pts={s['points']} "
              f"W{s['wins']}-L{s['losses']}-D{s['draws']} SOS={s['sos']}")
    assert table[0]["place"] == 1
    print("\nAll self-tests passed ✔")
