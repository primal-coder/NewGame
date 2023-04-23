from typing import Optional as _Optional, Union as _Union, List as _List
from .item import *
from ._weapon import _WeaponFactory, _WEAPONS_DICT
from ._clothing import _ClothingFactory, _CLOTHING_DICT
from ._armor import _ArmorFactory, _ARMOR_DICT


class QuietDict:
    def __init__(self, manifest_names: _Optional[_Union[list[str, ], str]], *args, **kwargs):
        self.items = {}
        if isinstance(manifest_names, list):
            for name in manifest_names:
                setattr(self, f'{name}_manifest', [])
        else:
            setattr(self, f'{manifest_names}_manifest', [])

    def __getitem__(self, key):
        return self.items[key]
    
    def __setitem__(self, key, value):
        self.items[key] = value

    def __delitem__(self, key):
        del self.items[key]

    def __iter__(self):
        return iter(self.items)
    
    def __contains__(self, key):
        return key in self.items
    
    def __repr__(self):
        return repr(self.items)
    
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

    
class Wardrobe(QuietDict):
    def __init__(self):
        super(Wardrobe, self).__init__("clothing")
    

class Armory(QuietDict):
    def __init__(self):
        super(Armory, self).__init__(['armor', 'weapons'])

Armory = Armory()

_weapon_instances = {}

for _weapon_id, _weapon_attr in _WEAPONS_DICT.items():
    _weapon_class = _WeaponFactory.create_weapon(_weapon_id)
    if _weapon_class is not None:
        _weapon_instance = _weapon_class(_weapon_id)
        _weapon_instances[_weapon_instance.name] = _weapon_instance
        setattr(Armory, _WEAPONS_DICT[_weapon_id]['name'].replace(" ", "").replace(",", "_").lower(), _weapon_instance)
        Armory.weapons_manifest.append(_WEAPONS_DICT[_weapon_id]['name'])
Armory.update(_weapon_instances)

Wardrobe = Wardrobe()

_clothing_instances = {}

for _clothing_id, _clothing_attr in _CLOTHING_DICT.items():
    _clothing_class = _ClothingFactory.create_clothing(_clothing_id)
    if _clothing_class is not None:
        _clothing_instance = _clothing_class(_clothing_id)
        _clothing_instances[_clothing_instance.name] = _clothing_instance
        setattr(Wardrobe, _CLOTHING_DICT[_clothing_id]['name'].replace(" ", "").replace(",", "_").lower(),
                _clothing_instance)
        Wardrobe.clothing_manifest.append(_CLOTHING_DICT[_clothing_id]['name'])
Wardrobe.update(_clothing_instances)

_armor_instances = {}
for _armor_id, _armor_attr in _ARMOR_DICT.items():
    _armor_class = _ArmorFactory.create_armor(_armor_id)
    if _armor_class is not None:
        _armor_instance = _armor_class(_armor_id)
        _armor_instances[_armor_instance.name] = _armor_instance
        setattr(Armory, _ARMOR_DICT[_armor_id]['name'].replace(" ", "").replace(",", "_").lower(), _armor_instance)
        Armory.armor_manifest.append(_ARMOR_DICT[_armor_id]['name'])
Armory.update(_armor_instances)
