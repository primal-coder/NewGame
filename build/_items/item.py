from .._components.event import _EventDispatcher
from abc import ABC as _ABC
from typing import Optional as _Optional, Union as _Union

_WEIGHTS = ['mg', 'g', 'kg']

_CURRENCY = ['cp', 'sp', 'gp', 'pp']

_ITEM_EVENTS = ['on_pickup', 'on_drop', 'on_equip', 'on_unequip', 'on_use', 'on_destroy', 'on_sell', 'on_buy',
                'on_trade', 'on_identify',
                'on_consume', 'on_eat', 'on_drink', 'on_read', 'on_wear', 'on_wield', 'on_hold', 'on_throw', 'on_shoot',
                'on_cast', 'on_activate',
                'on_repair', 'on_recharge']

_ITEM_CATEGORIES = ['FOOD', 'CLOTHING', 'TOYS', 'TOOLS', 'EQUIPMENT', 'WEAPONS', 'ARMOR', 'JEWELRY', 'GEMS', 'ORE',
                    'MATERIALS', 'POTIONS', 'SCROLLS', 'BOOKS', 'RELICS', 'MISC']

_ITEM_SLOT = ['HEAD', 'NECK', 'LEFT_SHOULDER', 'RIGHT_SHOULDER', 'CHEST', 'BACK', 'LEFT_WRIST', 'RIGHT_WRIST',
              'LEFT_HAND', 'RIGHT_HAND', 'WAIST', 'LEGS', 'FEET', 'FINGER_A', 'FINGER_B', 'TRINKET_A', 'TRINKET_B',
              'MAIN_HAND', 'OFF_HAND', 'RANGED', 'AMMO', 'MOUNT', 'TOY', 'CLOAK', 'BAG', 'TABARD', 'ROBE', 'QUIVER',
              'RELIC', 'SHIELD', 'HOLDABLE', 'THROWN', 'SHIRT', 'TROUSERS']

_MATERIAL_TYPES = ['WOOD', 'LEATHER', 'CLOTH', 'BURLAP', 'IRON', 'BRONZE', 'STEEL', 'SILVER', 'GOLD', 'STONE', 'GLASS',
                   'FUR', 'SILK', 'BONE', 'SHELL', 'CERAMIC', 'PAPER', 'FABRIC', 'ORGANIC', 'MISC']

_QUALITY_TYPES = ['COMMON', 'UNCOMMON', 'RARE', 'EPIC', 'LEGENDARY', 'ARTIFACT', 'MYTHIC']

_BINDINGS = ['BOUND', 'UNBOUND']

_ITEM_DICT = {
    1: {
        'item_id': 59,
        'name': 'Gold Coin',
        'category': 'MISC',
        'weight': (.01, 'g'),
        'material': 'GOLD',
        'mundane': True,
        'description': 'A gold coin.',
        'quality': 'COMMON',
        'value': (1, 'gp'),
        'binding': 'UNBOUND',
        'quest_item': False,
        'relic': False
    },
    2: {
        'item_id': 60,
        'name': 'Silver Coin',
        'category': 'MISC',
        'weight': (.01, 'g'),
        'material': 'SILVER',
        'mundane': True,
        'description': 'A silver coin.',
        'quality': 'COMMON',
        'value': (1, 'sp'),
        'binding': 'UNBOUND',
        'quest_item': False,
        'relic': False
    },
    3: {
        'item_id': 61,
        'name': 'Copper Coin',
        'category': 'MISC',
        'weight': (.01, 'g'),
        'material': 'COPPER',
        'mundane': True,
        'description': 'A copper coin.',
        'quality': 'COMMON',
        'value': (1, 'cp'),
        'binding': 'UNBOUND',
        'quest_item': False,
        'relic': False
    },
    4: {
        'item_id': 62,
        'name': "Dungeoneer's Pack",
        'category': 'TOOLS',
        'weight': (2, 'kg'),
        'material': 'OTHER',
        'mundane': True,
        'description': 'A pack of assorted tools and supplies often used by spelunkers',
        'quality': 'COMMON',
        'value': (1, 'cp'),
        'binding': 'UNBOUND',
        'quest_item': False,
        'relic': False
    }
}

class _AbstractItem(_EventDispatcher, _ABC):
    def __init__(
            self,
            id: _Optional[int] = None,
            name: _Optional[str] = None,
            category: _Optional[str] = None,
            slot: _Optional[_Union[str, tuple[str, str]]] = None,
            weight: _Optional[tuple[float, str]] = None,
            material: _Optional[str] = None,
            consumable: _Optional[bool] = None,
            mundane: _Optional[bool] = None,
            description: _Optional[str] = None,
            quality: _Optional[str] = None,
            value: _Optional[tuple[int, str]] = None,
            binding: _Optional[str] = None,
            quest_item: _Optional[bool] = None,
            relic: _Optional[bool] = None,
            *args, **kwargs
    ):
        super(_AbstractItem, self).__init__()
        self.id = id
        self.name = name
        self.category = category if category in _ITEM_CATEGORIES else None
        self.slot = slot if isinstance(slot, tuple) and slot[0] in _ITEM_SLOT and slot[1] in _ITEM_SLOT or \
            isinstance(slot, str) and slot in _ITEM_SLOT else None
        self.weight = weight if isinstance(weight[0], float) and weight[1] in _WEIGHTS else None
        self.material = material if material in _MATERIAL_TYPES else None
        self.consumable = consumable if consumable is not None else False
        self.mundane = mundane if mundane is not None else True
        self.description = description if description is not None else ""
        self.quality = quality if quality in _QUALITY_TYPES else None
        self.value = value if isinstance(value[0], int) and value[1] in _CURRENCY else None
        self.binding = binding if binding in _BINDINGS else None
        self.quest_item = quest_item if quest_item is not None else False
        self.relic = relic
        self.identified = False
        self.equipped = False
        self.owner = None
        for event in _ITEM_EVENTS:
            self._register_event_type(event)

    def _pickup(self, owner):
        self.owner = owner
        self._dispatch_event('on_pickup', self)

    def _drop(self):
        self._dispatch_event('on_drop', self)

    def _use(self):
        self._dispatch_event('on_use', self)

    def _destroy(self):
        self._dispatch_event('on_destroy', self)

    def _sell(self):
        self._dispatch_event('on_sell', self)

    def _buy(self):
        self._dispatch_event('on_buy', self)

    def _trade(self):
        self._dispatch_event('on_trade', self)

    def _identify(self):
        self._dispatch_event('on_identify', self)

    def _consume(self):
        self._dispatch_event('on_consume', self)


class _Item(_AbstractItem):
    def __repr__(self):
        return self.name
    
    def __init__(
            self,
            item_id: _Optional[int] = None,
            name: _Optional[str] = None,
            category: _Optional[str] = None,
            slot: _Optional[_Union[str, tuple[str, str]]] = None,
            weight: _Optional[tuple[float, str]] = None,
            material: _Optional[str] = None,
            consumable: _Optional[bool] = None,
            mundane: _Optional[bool] = None,
            description: _Optional[str] = None,
            quality: _Optional[str] = None,
            value: _Optional[tuple[int, str]] = None,
            binding: _Optional[str] = None,
            quest_item: _Optional[bool] = None,
            relic: _Optional[bool] = None,
            *args, **kwargs
    ):
        super(_Item, self).__init__(
            item_id=item_id,
            name=name,
            category=category,
            slot=slot,
            weight=weight,
            material=material,
            consumable=consumable,
            mundane=mundane,
            description=description,
            quality=quality,
            value=value,
            binding=binding,
            quest_item=quest_item,
            relic=relic,
            *args, **kwargs
        )
