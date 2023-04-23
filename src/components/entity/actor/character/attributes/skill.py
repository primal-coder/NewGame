from abc import ABC as _ABC

import pyglet.event as _event

from src.components.misc.die import *
from src.components.misc.quiet_dict import QuietDict as _QuietDict 
from src.components.utility.saved_objects import load_json as _load_json

SKILLS = _load_json('src/dicts/skills.json')


class AbstractSkill(_event.EventDispatcher, _ABC):
    """Abstract class for skills.

    :param parent: The parent entity
    :type parent: :class:`entity.actor.Actor`"""
    def __init__(self, parent, name, description, ability, proficient):
        self.parent = parent
        self.name = name
        self.description = description
        self.ability = ability
        self.proficient = proficient
        self.level = 0
        self.register_event_type('on_level_up')

    def __repr__(self):
        return repr(self.level)


class Skill(AbstractSkill):
    """A skill

    :param parent: The parent entity
    :type parent: :class:`entity.actor.Actor`"""

    def __init__(self, parent):
        self.name = self.__class__.__name__.replace("_", " ").replace("O", "o")

        super(Skill, self).__init__(parent, self.name, SKILLS[self.name]["description"], SKILLS[self.name]["ability"],
                                    SKILLS[self.name]["proficient"])

    def level_up(self):
        self.dispatch_event('on_level_up', self)

    def check(self, dc):
        """Perform a skill check"""
        ability = getattr(self.parent, self.ability)
        modifier = getattr(ability, 'modifier')
        return check(self.level + modifier, dc)


class SkillFactory:
    """A factory for creating skills"""

    @staticmethod
    def create_skill(parent, skill_name):
        if skill_name is not None:
            return type(skill_name, (Skill,), SKILLS[skill_name])(parent)


class Skillbook(_QuietDict, _event.EventDispatcher):
    def __init__(self, parent):
        self.parent = parent
        super(Skillbook, self).__init__()
