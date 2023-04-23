from typing import Union as _Union, Any as _Any, Optional as _Optional
from src.components.utility.saved_objects import load_json as _load_json
from src.components.misc.die import *
from src.components.misc.die import Die as _Die
from ..item import _Item

_WEAPONS_DICT = _load_json('src/dicts/weapons.json')

_WEAPON_PROFICIENCIES = ['SIMPLE', 'MARTIAL', 'EXOTIC', 'MASTER']

_WEAPON_PROPERTIES = ['LIGHT', 'ONE_HANDED', 'TWO_HANDED', 'VERSATILE', 'FINESSE', 'THROWN', 'REACH', 'AMMUNITION',
                      'LOADING', 'HEAVY', 'SPECIAL', 'OTHER']

_DAMAGE_TYPES = ['SLASHING', 'BLUDGEONING', 'PIERCING']


class _Weapon(_Item):
    def __init__(
            self,
            item_id: _Optional[int] = None,
            name: _Optional[str] = None,
            slot: _Optional[_Union[str, tuple[str, str]]] = None,
            weight: _Optional[tuple[float, str]] = None,
            material: _Optional[str] = None,
            mundane: _Optional[bool] = None,
            description: _Optional[str] = None,
            quality: _Optional[str] = None,
            value: _Optional[tuple[int, str]] = None,
            binding: _Optional[bool] = None,
            quest_item: _Optional[bool] = None,
            relic: _Optional[bool] = None,
            damage: _Optional[tuple[int, _Union[_Die, int, str]]] = None,
            damage_type: _Optional[str] = None,
            proficiency: _Optional[str] = None,
            weapon_range: _Optional[tuple[int, str]] = None,
            weapon_properties: _Optional[list[str]] = None,
            *args, **kwargs
    ):
        self.damage = damage
        if isinstance(self.damage[1], str):
            self.damage = (self.damage[0], _Die(int(self.damage[1].removeprefix('d'))))
        elif isinstance(self.damage[1], int):
            self.damage = (self.damage[0], _Die(self.damage[1]))
        self.damage_type = damage_type if damage_type in _DAMAGE_TYPES else 'UNKNOWN'
        self.proficiency = proficiency if proficiency in _WEAPON_PROFICIENCIES else None
        self.weapon_properties = weapon_properties if all(
            prop in _WEAPON_PROPERTIES for prop in weapon_properties) else None
        self.weapon_range = weapon_range
        super(_Weapon, self).__init__(
            item_id=item_id,
            name=name,
            category="WEAPON",
            slot=slot if slot in ('MAIN_HAND', 'OFF_HAND') or slot == ('MAIN_HAND', 'OFF_HAND') else None,
            weight=weight,
            material=material,
            consumable=False,
            mundane=mundane,
            description=description,
            quality=quality,
            value=value,
            binding=binding,
            quest_item=quest_item,
            relic=relic,
            *args, **kwargs
        )

    def __repr__(self):
        return f"({self.damage[0]}{self.damage[1]}/{self.weapon_range[0]}{self.weapon_range[1]})({self.damage_type})[{self.quality}]"


class _WeaponById(_Weapon):
    def __init__(self, id):
        super(_WeaponById, self).__init__(**_WEAPONS_DICT[id])


class _WeaponFactory:
    def __init__(self, weapon_dict=None):
        if weapon_dict is None:
            weapon_dict = _WEAPONS_DICT
        self.weapon_dict = weapon_dict

    @staticmethod
    def create_weapon(weapon_id: int) -> type | None:
        weapon_class = type(_WEAPONS_DICT[weapon_id]['name'].replace(" ", ""), (_WeaponById,), {})
        if weapon_class is None:
            return None
        return weapon_class
