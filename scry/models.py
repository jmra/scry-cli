from dataclasses import dataclass
from typing import Optional


@dataclass
class Card:
    name: str
    mana_cost: str
    type_line: str
    oracle_text: str
    power: Optional[str]
    toughness: Optional[str]
    set_code: str
    set_name: str
    rarity: str
    colors: list[str]
    cmc: float

    @classmethod
    def from_api(cls, data: dict) -> "Card":
        faces = data.get("card_faces")
        if faces:
            mana_cost = " // ".join(
                f.get("mana_cost", "") for f in faces if f.get("mana_cost")
            )
            oracle_text = "\n---\n".join(
                f"{f.get('name', '')}\n{f.get('oracle_text', '')}" for f in faces
            )
        else:
            mana_cost = data.get("mana_cost", "")
            oracle_text = data.get("oracle_text", "")

        return cls(
            name=data.get("name", ""),
            mana_cost=mana_cost,
            type_line=data.get("type_line", ""),
            oracle_text=oracle_text,
            power=data.get("power"),
            toughness=data.get("toughness"),
            set_code=data.get("set", "").upper(),
            set_name=data.get("set_name", ""),
            rarity=data.get("rarity", ""),
            colors=data.get("colors", []),
            cmc=data.get("cmc", 0.0),
        )
