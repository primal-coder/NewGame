from typing import Union as _Union, Any as _Any, Optional as _Optional
from src.components.misc.die import *
from src.components.misc.die import Die as _Die
from ..item import _Item

_ARMOR_DICT = {
    1: {
        'item_id': 50,
        'name': 'Leather Cuirass',
        'slot': 'CHEST',
        'weight': (1.5, 'kg'),
        'material': 'LEATHER',
        'mundane': True,
        'description': 'A basic leather chest-piece.',
        'quality': 'COMMON',
        'value': (5, 'cp'),
        'armor_class': 2
    },
    2: {
        'item_id': 51,
        'name': 'Leather Helmet',
        'slot': 'HEAD',
        'weight': (1.0, 'kg'),
        'material': 'LEATHER',
        'mundane': True,
        'description': 'A basic leather helmet.',
        'quality': 'COMMON',
        'value': (5, 'cp'),
        'armor_class': 1
    },
    3: {
        'item_id': 52,
        'name': 'Leather Gauntlet',
        'slot': ('LEFT_HAND', 'RIGHT_HAND'),
        'weight': (.5, 'kg'),
        'material': 'LEATHER',
        'mundane': True,
        'description': 'A basic pair of leather gauntlets.',
        'quality': 'COMMON',
        'value': (5, 'cp'),
        'armor_class': 1
    },
    4: {
        'item_id': 53,
        'name': 'Leather Boots',
        'slot': 'FEET',
        'weight': (.5, 'kg'),
        'material': 'LEATHER',
        'mundane': True,
        'description': 'A basic pair of leather boots.',
        'quality': 'COMMON',
        'value': (5, 'cp'),
        'armor_class': 1
    },
    5: {
        'item_id': 54,
        'name': 'Leather Leggings',
        'slot': 'LEGS',
        'weight': (1.0, 'kg'),
        'material': 'LEATHER',
        'mundane': True,
        'description': 'A basic pair of leather leggings.',
        'quality': 'COMMON',
        'value': (5, 'cp'),
        'armor_class': 2
    },
    6: {
        'item_id': 55,
        'name': 'Leather Bracer',
        'slot': ('LEFT_WRIST', 'RIGHT_WRIST'),
        'weight': (.25, 'kg'),
        'material': 'LEATHER',
        'mundane': True,
        'description': 'A basic pair of leather bracers.',
        'quality': 'COMMON',
        'value': (5, 'cp'),
        'armor_class': 1
    },
    7: {
        'item_id': 56,
        'name': 'Leather Belt',
        'slot': 'WAIST',
        'weight': (.25, 'kg'),
        'material': 'LEATHER',
        'mundane': True,
        'description': 'A basic leather belt.',
        'quality': 'COMMON',
        'value': (5, 'cp'),
        'armor_class': 1
    },
    8: {
        'item_id': 57,
        'name': 'Leather Pauldron',
        'slot': ('LEFT_SHOULDER', 'RIGHT_SHOULDER'),
        'weight': (1.5, 'kg'),
        'material': 'LEATHER',
        'mundane': True,
        'description': 'A basic leather pauldron.',
        'quality': 'COMMON',
        'value': (5, 'cp'),
        'armor_class': 1
    }
}


class _Armor(_Item):
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
            binding: _Optional[str] = None,
            relic: _Optional[bool] = None,
            armor_class: _Optional[_Union[_Die, int]] = None,
            *args, **kwargs
    ):
        super(_Armor, self).__init__(
            item_id=item_id,
            name=name,
            category='ARMOR',
            slot=slot,
            weight=weight,
            material=material,
            consumable=False,
            mundane=mundane,
            description=description,
            quality=quality,
            value=value,
            binding=binding,
            quest_item=False,
            relic=relic,
            *args, **kwargs
        )
        self.armor_class = armor_class

    def __repr__(self):
        return f'{super(_Armor, self).__repr__()}[ac {self.armor_class}]'

    def _equip(self):
        self._dispatch_event('on_equip', self)

    def _unequip(self):
        self._dispatch_event('on_unequip', self)


class _ArmorById(_Armor):
    def __init__(self, armor_id):
        super(_ArmorById, self).__init__(**_ARMOR_DICT[armor_id])


class _ArmorFactory:
    @staticmethod
    def create_armor(armor_id):
        _armor_class = type(_ARMOR_DICT[armor_id]['name'].replace(" ", "").lower(), (_ArmorById, ), {})
        if _armor_class is None:
            return None
        return _armor_class
