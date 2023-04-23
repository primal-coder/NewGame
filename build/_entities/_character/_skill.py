from ..._components.die import *
from abc import ABC as _ABC

import pyglet.event as _event

_SKILLS = {
    "Acrobatics": {
        "description": "Maneuvering your body through the air and over obstacles without the need for strenuous effort. Stability improves with higher scores.",
        "ability": "Dexterity",
        "proficient": False
        },
    "Animal Handling": {
        "description": "Strong relationship with animals, both wild and domestic. From taming beasts to training mounts to understanding the behavior of animals.",
        "ability": "Wisdom",
        "proficient": False
        },
    "Arcana": {
        "description": "A depth of knowledge about the magical forces that underlie the universe and the creatures that inhabit it. Including the knowledge of spells, magic items, eldritch symbols, magical traditions, the planes of existence, and the inhabitants of those planes.",
        "ability": "Intelligence",
        "proficient": False
        },
    "Athletics": {
        "description": "Physical prowess and competency in endeavors which demand physical strength, endurance and coordination",
        "ability": "Strength",
        "proficient": False
        },
    "Deception": {
        "description": "Manipulation of others through misdirection, trickery, falsehoods, disguise, seduction or other means.",
        "ability": "Charisma",
        "proficient": False
        },
    "History": {
        "description": "A thorough understanding of historical facts. A knowledge of historical events, legendary people, ancient kingdoms, past disputes, recent wars, and lost civilizations.",
        "ability": "Intelligence",
        "proficient": False
        },
    "Insight": {
        "description": "A sense of people's intentions and feelings. The ability to determine the true intentions of a creature, such as when searching out a lie or predicting someone's next move.",
        "ability": "Wisdom",
        "proficient": False
        },
    "Intimidation": {
        "description": "Using threats, violence, and fear to influence others' behavior. The ability to influence someone through overt threats, hostile actions, and physical violence.",
        "ability": "Charisma",
        "proficient": False
        },
    "Investigation": {
        "description": "Forensic approach to uncovering the truth and a dedicated consideration to the details of a situation, especially when searching for clues and answers.",
        "ability": "Intelligence",
        "proficient": False
        },
    "Medicine": {
        "description": "Diagnostics and treatment of injuries and afflictions. General knowledge of anatomy, physiology, and common diseases and the application of a variety of conventional medical techniques.",
        "ability": "Wisdom",
        "proficient": False
        },
    "Nature": {
        "description": "Knowledge of the natural world and the creatures that inhabit it. A thorough understanding of plants and animals, the weather and the terrain, and the way these factors interact.",
        "ability": "Intelligence",
        "proficient": False
        },
    "Perception": {
        "description": "Awareness of surroundings and the ability to notice details. The ability to notice things that are not obvious or to make deductions based on those things you do notice.",
        "ability": "Wisdom",
        "proficient": False
        },
    "Performance": {
        "description": "Entertaining an audience through acting, dancing, singing, storytelling, or some other form of performance. The ability to delight an audience with music, dance, acting, storytelling, or some other form of entertainment.",
        "ability": "Charisma",
        "proficient": False
        },
    "Persuasion": {
        "description": "Influencing others through reasoning or the use of compelling arguments. The ability to influence others or a group of people to do something or to believe something, usually through the use of reasoning and good argument.",
        "ability": "Charisma",
        "proficient": False
        },
    "Religion": {
        "description": "Knowledge of the gods, rites, and rituals of a religion. A thorough understanding of the deities worshipped, religious practices, holy days, rites of passage, religious hierarchies, and the underlying principles of a religion.",
        "ability": "Intelligence",
        "proficient": False
        },
    "Sleight of Hand": {
        "description": "Prestidigitation and manual dexterity. The ability to perform sleight of hand tricks such as palming objects, hiding small objects on your person, picking pockets, opening locked containers, and other types of manual trickery.",
        "ability": "Dexterity",
        "proficient": False
        },
    "Stealth": {
        "description": "Concealment, camoflauge, and movement without being detected. The ability to move quietly and stealthily, hide from enemies, slip away without being noticed, and avoid being tracked by non-magical means.",
        "ability": "Dexterity",
        "proficient": False
        },
    "Survival": {
        "description": "Knowledge of the wilds and how to survive in them. A thorough understanding of the natural world, including terrain, plants and animals, the weather, and natural cycles.",
        "ability": "Wisdom",
        "proficient": False
        }
}



# Path: build/entities/actor/skill.py

# Build a class hierarchy for skills
# Skills are a special case of abilities

class _AbstractSkill(_event.EventDispatcher, _ABC):
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


class _Skill(_AbstractSkill):
    def __init__(self, parent):
        self.name = self.__class__.__name__.replace("_", " ").replace("O", "o")

        super(_Skill, self).__init__(parent, self.name, _SKILLS[self.name]["description"], _SKILLS[self.name]["ability"], _SKILLS[self.name]["proficient"])

    def level_up(self):
        self.dispatch_event('on_level_up', self)

    def check(self, dc):
        """Perform a skill check"""
        ability = getattr(self.parent, self.ability)
        modifier = getattr(ability, 'modifier')
        return check(self.level + modifier, dc)
        

class _SkillFactory:
    """A factory for creating skills"""

    @staticmethod
    def create_skill(parent, skill_name):
        if skill_name is not None:
            return type(skill_name, (_Skill,), _SKILLS[skill_name])(parent)
        
class _Skillbook(dict, _event.EventDispatcher):
    def __init__(self, parent):
        self.parent = parent
        super(_Skillbook, self).__init__(self)


    