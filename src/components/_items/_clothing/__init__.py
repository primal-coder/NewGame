from ..item import _Item, _ITEM_SLOT, _WEIGHTS, _QUALITY_TYPES, _MATERIAL_TYPES, _ITEM_EVENTS, _ITEM_CATEGORIES, \
    _CURRENCY, _Optional

_CLOTHING_DICT = {
    1: {
        'item_id': 46,
        'name': 'Burlap Tunic',
        'slot': 'SHIRT',
        'weight': (.2, 'kg'),
        'material': 'BURLAP',
        'mundane': True,
        'description': 'A basic burlap tunic.',
        'quality': 'COMMON',
        'value': (1, 'cp'),
        'color': 'BROWN',
        'appeal': 1
    },
    2: {
        'item_id': 47,
        'name': 'Leather Tunic',
        'slot': 'SHIRT',
        'weight': (.5, 'kg'),
        'material': 'LEATHER',
        'mundane': True,
        'description': 'A basic leather tunic.',
        'quality': 'COMMON',
        'value': (5, 'cp'),
        'color': 'BROWN',
        'appeal': 2
    },
    3: {
        'item_id': 48,
        'name': 'Burlap Trousers',
        'slot': 'TROUSERS',
        'weight': (.4, 'kg'),
        'material': 'BURLAP',
        'mundane': True,
        'description': 'A basic pair of burlap trousers.',
        'quality': 'COMMON',
        'value': (1, 'cp'),
        'color': 'BROWN',
        'appeal': 1
    },
    4: {
        'item_id': 49,
        'name': 'Leather Trousers',
        'slot': 'TROUSERS',
        'weight': (.6, 'kg'),
        'material': 'LEATHER',
        'mundane': True,
        'description': 'A basic pair of leather trousers.',
        'quality': 'COMMON',
        'value': (5, 'cp'),
        'color': 'BROWN',
        'appeal': 2
    },
    5: {
        'item_id': 58,
        'name': 'Loincloth',
        'slot': 'TROUSERS',
        'weight': (.1, 'kg'),
        'material': 'CLOTH',
        'mundane': True,
        'description': 'A basic loincloth.',
        'quality': 'COMMON',
        'value': (1, 'cp'),
        'color': 'BROWN',
        'appeal': 1
    }

}


class _Clothing(_Item):
    def __init__(
            self,
            item_id: _Optional[int] = None,
            name: _Optional[str] = None,
            slot: _Optional[str] = None,
            weight: _Optional[tuple[float, str]] = None,
            material: _Optional[str] = None,
            mundane: _Optional[bool] = None,
            description: _Optional[str] = None,
            quality: _Optional[str] = None,
            value: _Optional[tuple[int, str]] = None,
            color: _Optional[str] = None,
            appeal: _Optional[int] = None
    ):
        self.color = color
        self.appeal = appeal
        super(_Clothing, self).__init__(
            item_id=item_id,
            name=name,
            category='CLOTHING',
            slot=slot,
            weight=weight,
            material=material,
            consumable=False,
            mundane=mundane,
            description=description,
            quality=quality,
            value=value,
            binding='UNBOUND',
            quest_item=False,
            relic=False
        )


class _ClothingById(_Clothing):
    def __init__(self, clothing_id):
        super(_ClothingById, self).__init__(**_CLOTHING_DICT[clothing_id])


class _ClothingFactory:
    @staticmethod
    def create_clothing(clothing_id: int) -> type | None:
        _clothing_class = type(_CLOTHING_DICT[clothing_id]['name'].replace(" ", "").replace(",", "_").lower(),
                               (_ClothingById,),
                               {})
        if _clothing_class is None:
            return None
        return _clothing_class
