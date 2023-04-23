from ..._components.event import _EventDispatcher
from abc import ABC as _ABC
from typing import Optional as _Optional

EQUIPMENT_SLOTS = {
    'HEAD': None,
    'NECK': None,
    'LEFT_SHOULDER': None,
    'RIGHT_SHOULDER': None,
    'CHEST': None,
    'BACK': None,
    'LEFT_WRIST': None,
    'RIGHT_WRIST': None,
    'LEFT_HAND': None,
    'RIGHT_HAND': None,
    'WAIST': None,
    'LEGS': None,
    'FEET': None,
    'FINGER_A': None,
    'FINGER_B': None,
    'TRINKET_A': None,
    'TRINKET_B': None,
    'MAIN_HAND': None,
    'OFF_HAND': None,
    'RANGED': None,
    'AMMO': None,
    'MOUNT': None,
    'TOY': None,
    'CLOAK': None,
    'BAG': None,
    'TABARD': None,
    'ROBE': None,
    'QUIVER': None,
    'RELIC': None,
    'SHIELD': None,
    'HOLDABLE': None,
    'THROWN': None,
    'SHIRT': None,
    'TROUSERS': None
}


class _Equipment(_EventDispatcher, _ABC):
    def __init__(self, _parent):
        self._parent = _parent
        self._slots = EQUIPMENT_SLOTS
        self._register_event_type('on_equip_item')
        self._register_event_type('on_unequip_item')

    def __repr__(self):
        return repr({list(self._slots.keys())[i]: list(self._slots.values())[i] for i in range(len(self._slots)) if
                     list(self._slots.values())[i] is not None})

    def __getitem__(self, key):
        return self._slots[key]

    def __setitem__(self, key, value):
        self._slots[key] = value

    def __delitem__(self, key):
        del self._slots[key]

    def __iter__(self):
        return iter(self._slots)

    def __contains__(self, key):
        return key in self._slots

    def update(self, other=None, **kwargs):
        if other:
            if hasattr(other, "keys"):
                for key in other.keys():
                    self[key] = other[key]
            else:
                for key, value in other:
                    self[key] = value
        for key, value in kwargs.items():
            self[key] = value

    def equip_item(self, item):
        if isinstance(item.slot, tuple):
            for slot in item.slot:
                if slot in self._slots:
                    if self._slots[slot] is not None:
                        continue
                    else:
                        self._slots[slot] = item
                        self._dispatch_event('on_equip_item', item)
        elif item.slot in self._slots:
            if self._slots[item.slot] is None:
                self._slots[item.slot] = item
                self._dispatch_event('on_equip_item', item)
            else:
                self._slots[item.slot] = item
                self._dispatch_event('on_unequip_item', item)
                self._dispatch_event('on_equip_item', item)

    def unequip_item(self, item):
        if item.slot in self._slots:
            if self._slots[item.slot] is not None:
                self._slots[item.slot] = None
                self._dispatch_event('on_unequip_item', item)

    def get_equipped_item(self, slot):
        if slot in self._slots:
            return self._slots[slot]


class _Inventory(_EventDispatcher, _ABC):
    def __init__(self, _parent):
        self._parent = _parent
        self._carry_limit = self._calc_carry_limit()
        self._carry_weight = 0
        self.items = []
        self.equipment = _Equipment(self._parent)
        self._register_event_type('on_add_item')
        self._register_event_type('on_remove_item')
        self._register_event_type('on_equip_item')
        self._register_event_type('on_unequip_item')

    def _calc_carry_limit(self):
        return self._parent.Strength.score * 10

    def _calc_carry_weight(self):
        return sum(item.weight[0] for item in self.items)

    def add_item(self, item):
        if self._calc_carry_weight() + item.weight[0] > self._carry_limit:
            return False
        self.items.append(item)
        self._carry_weight = self._calc_carry_weight()
        self._dispatch_event('on_add_item', item)

    def remove_item(self, item):
        self.items.remove(item)
        self._carry_weight = self._calc_carry_weight()
        self._dispatch_event('on_remove_item', item)

    def equip_item(self, item):
        self.equipment.equip_item(item)
        self._dispatch_event('on_equip_item', item)

    def unequip_item(self, item):
        self.equipment[item.slot] = None
        self._dispatch_event('on_unequip_item', item)
