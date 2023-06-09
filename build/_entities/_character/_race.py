from ..._components.die import *
from abc import ABC as _ABC
from typing import Optional as _Optional

_RACE_ATTRIBUTES = {
    'Dwarf': {
        'title': 'Dwarf',
        'description': "A stout and hardy creature, with a rugged exterior and a heart of gold. Dwarves are known for their skill with metalworking, mining, and craftsmanship, as well as their fierce loyalty and determination in battle.",
        '_ability_score_increase': {'Constitution': 2},
        '_age': {'maturity': 50, 'maximum': 350},
        'size': 'Medium',
        'speed': 25,
        'languages': ['Common', 'Dwarvish'],
        'traits': ['Darkvision', 'Dwarven Resilience', 'Dwarven Combat Training', 'Tool Proficiency', 'Stonecunning'],
        'subraces': ['Hill Dwarf', 'Mountain Dwarf']
    },
    'Elf': {
        'title': 'Elf',
        'description': "Graceful and ethereal, elves possess a natural beauty and magical prowess that sets them apart from other races. They are skilled hunters, archers, and trackers, with a deep connection to nature and a profound love of music and art.",
        '_ability_score_increase': {'Dexterity': 2},
        '_age': {'maturity': 100, 'maximum': 750},
        'size': 'Medium',
        'speed': 30,
        'languages': ['Common', 'Elvish'],
        'traits': ['Darkvision', 'Keen Senses', 'Fey Ancestry', 'Trance', 'Elf Weapon Training', 'Cantrip'],
        'subraces': ['High Elf', 'Wood Elf', 'Dark Elf']
    },
    'Halfling': {
        'title': 'Halfling',
        'description': "Small but mighty, halflings are a curious and adventurous race, with a love of good food, drink, and company. They are nimble and quick-witted, with a talent for stealth and mischief, and an uncanny ability to find themselves in the most unexpected places.",
        '_ability_score_increase': {'Dexterity': 2},
        '_age': {'maturity': 20, 'maximum': 150},
        'size': 'Small',
        'speed': 25,
        'languages': ['Common', 'Halfling'],
        'traits': ['Lucky', 'Brave', 'Halfling Nimbleness'],
        'subraces': ['Lightfoot Halfling', 'Stout Halfling']
    },
    'Human': {
        'title': 'Human',
        'description': "The most populous and adaptable of all the races, humans are a diverse and dynamic people, with a wide range of skills, talents, and personalities. They are driven by a desire for knowledge, discovery, and achievement, and possess an innate curiosity and thirst for adventure.",
        '_ability_score_increase': {'Strength': 1, 'Dexterity': 1, 'Constitution': 1, 'Intelligence': 1, 'Wisdom': 1, 'Charisma': 1},
        '_age': {'maturity': 15, 'maximum': 100},
        'size': 'Medium',
        'speed': 30,
        'languages': ['Common'],
        'traits': ['Extra Language'],
        'subraces': None
    },
    'Dragonborn': {
        'title': 'Dragonborn',
        'description': "Descended from dragons themselves, dragonborn are a proud and majestic race, with a deep respect for tradition and a fierce sense of honor. They possess the strength and power of their draconic ancestors, as well as their innate magic and wisdom.",
        '_ability_score_increase': {'Strength': 2, 'Charisma': 1},
        '_age': {'maturity': 15, 'maximum': 80},
        'size': 'Medium',
        'speed': 30,
        'languages': ['Common', 'Draconic'],
        'traits': ['Draconic Ancestry', 'Breath Weapon', 'Damage Resistance'],
        'subraces': None
    },
    'Gnome': {
        'title': 'Gnome',
        'description': "Small in stature but big in spirit, gnomes are a curious and inventive race, with a talent for tinkering, invention, and illusion magic. They are often underestimated by their larger counterparts, but their cleverness and resourcefulness make them formidable allies and foes.",
        '_ability_score_increase': {'Intelligence': 2},
        '_age': {'maturity': 40, 'maximum': 500},
        'size': 'Small',
        'speed': 25,
        'languages': ['Common', 'Gnomish'],
        'traits': ['Darkvision', 'Gnome Cunning'],
        'subraces': ['Tinkerton Gnome', 'Forest Gnome']
    },
    'Half-Elf': {
        'title': 'Half-Elf',
        'description': "A hybrid of elf and human, half-elves embody the best of both worlds, combining the grace and magic of the elves with the resilience and versatility of the humans. They are natural diplomats and mediators, with a talent for bridging cultural divides and forging alliances between different peoples.",
        '_ability_score_increase': {'Charisma': 2},
        '_age': {'maturity': 20, 'maximum': 180},
        'size': 'Medium',
        'speed': 30,
        'languages': ['Common', 'Elvish'],
        'traits': ['Darkvision', 'Fey Ancestry', 'Skill Versatility', 'Cantrip', 'Extra Language'],
        'subraces': None
    },
    'Half-Orc': {
        'title': 'Half-Orc',
        'description': "A formidable and fearsome creature, half-orcs are the product of an unlikely union between orc and human. They possess a fierce strength and ferocity in battle, tempered by a deep sense of honor and loyalty to their friends and family.",
        '_ability_score_increase': {'Strength': 2, 'Constitution': 1},
        '_age': {'maturity': 14, 'maximum': 75},
        'size': 'Medium',
        'speed': 30,
        'languages': ['Common', 'Orc'],
        'traits': ['Darkvision', 'Menacing', 'Relentless Endurance', 'Savage Attacks'],
        'subraces': None
    },
    'Tiefling': {
        'title': 'Tiefling',
        'description':  "Bearing the mark of their infernal heritage, tieflings are a mysterious and misunderstood race, often regarded with suspicion and fear by those around them. They possess a natural charm and cunning, as well as a talent for dark magic and deception.",
        '_ability_score_increase': {'Intelligence': 1, 'Charisma': 2},
        '_age': {'maturity': 18, 'maximum': 100},
        'size': 'Medium',
        'speed': 30,
        'languages': ['Common', 'Infernal'],
        'traits': ['Darkvision', 'Hellish Resistance', 'Infernal Legacy'],
        'subraces': None
    }
}

class _AbstractRace(_ABC):
    def __init__(
            self,
            title: _Optional[str] = None,
            description: _Optional[str] = None,
            _ability_score_increase: _Optional[dict] = None,
            _age: _Optional[dict] = None,
            size: _Optional[str] = None,
            speed: _Optional[int] = None,
            languages: _Optional[list] = None,
            traits: _Optional[list] = None,
            subraces: _Optional[list] = None
    ) -> None:
        self.title = title
        self.description = description
        self._ability_score_increase = _ability_score_increase
        self._age = _age
        self.size = size
        self.speed = speed
        self.languages = languages
        self.traits = traits
        self.subraces = subraces

    def __repr__(self) -> str:
        return self.description

class _Race(_AbstractRace):
    def __init__(self, title):
        attributes = _RACE_ATTRIBUTES.get(title)
        super(_Race, self).__init__(attributes['title'], attributes['description'], attributes['_ability_score_increase'], attributes['_age'], attributes['size'], attributes['speed'], attributes['languages'], attributes['traits'], attributes['subraces'])

class _RaceFactory:
    @staticmethod
    def create_race(race_name):
        race_attr = _RACE_ATTRIBUTES.get(race_name)
        if race_attr is None:
            return None
        return type(race_name, (_Race, ), _RACE_ATTRIBUTES[race_name])
    
