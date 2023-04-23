from abc import ABC as _ABC
from typing import Optional as _Optional

from src.components.utility.saved_objects import save_json as _save_json, load_json as _load_json

RACE_ATTRIBUTES = _load_json('src/dicts/race_attributes.json')

SUBRACE_ATTRIBUTES = _load_json('src/dicts/subrace_attributes.json')


class AbstractRace(_ABC):
    def __init__(
            self,
            title: _Optional[str] = None,
            description: _Optional[str] = None,
            _ability_score_increase: _Optional[dict] = None,
            age: _Optional[dict] = None,
            size: _Optional[str] = None,
            speed: _Optional[int] = None,
            languages: _Optional[list] = None,
            traits: _Optional[list] = None,
            subraces: _Optional[list] = None,
            parent_race: _Optional[str] = None,
    ) -> None:
        self.title = title
        self.description = description
        self.racial_bonuses = _ability_score_increase
        self.age = age
        self.size = size
        self.speed = speed
        self.languages = languages
        self.traits = traits
        self.subraces = subraces

    def __repr__(self) -> str:
        return self.description


class Race(AbstractRace):
    def __init__(self, title):
        attributes = RACE_ATTRIBUTES.get(title)
        super(Race, self).__init__(attributes['title'], attributes['description'],
                                   attributes['_ability_score_increase'], attributes['_age'], attributes['size'],
                                   attributes['speed'], attributes['languages'], attributes['traits'],
                                   attributes['subraces'])


class SubRace(AbstractRace):
    def __init__(self, title):
        attributes = SUBRACE_ATTRIBUTES.get(title)
        super(SubRace, self).__init__(attributes['title'], attributes['description'],
                                      attributes['_ability_score_increase'], attributes['_age'], attributes['size'],
                                      attributes['speed'], attributes['languages'], attributes['traits'],
                                      attributes['subraces'])


class RaceFactory:
    @staticmethod
    def create_race(race_name):
        race_attr = RACE_ATTRIBUTES.get(race_name)
        if race_attr is None:
            return None
        return type(race_name, (Race,), RACE_ATTRIBUTES[race_name])
