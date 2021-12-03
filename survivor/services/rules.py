from sqlite3 import Cursor

from survivor.data import Rules
from survivor.utils.db import wrap_operation


@wrap_operation()
def get(rules_id: int, *, cursor: Cursor = None) -> Rules:
    cursor.execute("SELECT * FROM rules WHERE id = :id LIMIT 1;", {"id": rules_id})

    rules_raw = cursor.fetchone()
    return Rules.to_rules(rules_raw)


@wrap_operation(is_write=True)
def upsert(rules: Rules | None, *, cursor: Cursor = None) -> int:
    input = rules or Rules()

    cursor.execute(
        """
        INSERT INTO rules
            (id, max_strikes, max_team_picks, pick_cutoff, pick_reveal, entry_fee, winnings)
        VALUES
            (:id, :max_strikes, :max_team_picks, :pick_cutoff, :pick_reveal, :entry_fee, :winnings)
        ON CONFLICT DO UPDATE SET
            max_strikes = :max_strikes,
            max_team_picks = :max_team_picks,
            pick_cutoff = :pick_cutoff,
            pick_reveal = :pick_reveal,
            entry_fee = :entry_fee,
            winnings = :winnings;
        """,
        {
            "id": input.id,
            "max_strikes": input.max_strikes,
            "max_team_picks": input.max_team_picks,
            "pick_cutoff": input.pick_cutoff,
            "pick_reveal": input.pick_reveal,
            "entry_fee": input.entry_fee,
            "winnings": input.winnings,
        },
    )

    return id
