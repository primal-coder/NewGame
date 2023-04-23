from ..._components.die import *
from ._ability import _ABILITIES, _ABC, _SPECIAL_ABILITIES, _Ability, _AbilityFactory, _AbstractAbility, _AbstractSpecialAbility, _SpecialAbility, _SpecialAbilityFactory

_ROLE_ATTRIBUTES = {
    "Barbarian": {
        "title": "Barbarian",
        "_class_description": "A master of rage.",
        "hit_die": d12,
        "proficiencies": ["Light Armor", "Medium Armor", "Shields", "Simple Weapons", "Martial Weapons"],
        "special_ability": "Rage",
        "starting_equipment": ["Greataxe", "Loincloth"]},
    "Bard": {
        "title": "Bard",
        "_class_description": "A master of lore.",
        "hit_die": d8,
        "proficiencies": ["Light Armor", "Simple Weapons", "Hand Crossbows", "Longswords", "Rapiers",
                          "Shortswords"],
        "special_ability": "Bardic Inspiration",
        "starting_equipment": ["Rapier", "Lute"]},
    "Cleric": {
        "title": "Cleric",
        "_class_description": "A master of worship.",
        "hit_die": d8,
        "proficiencies": ["Light Armor", "Medium Armor", "Shields", "Simple Weapons"],
        "special_ability": "Divine Domain",
        "starting_equipment": ["Mace", "Chain Mail"]},
    "Druid": {
        "title": "Druid",
        "_class_description": "A master of nature.",
        "hit_die": d8,
        "proficiencies": ["Light Armor", "Medium Armor", "Shields", "Clubs", "Daggers", "Darts", "Javelins",
                          "Maces", "Quarterstaffs", "Scimitars", "Sickles", "Slings", "Spears"],
        "special_ability": "Druidic",
        "starting_equipment": ["Wooden Shield", "Scimitar"]},
    "Fighter": {
        "title": "Fighter",
        "_class_description": "A master of arms.",
        "hit_die": d10,
        "proficiencies": ["Light Armor", "Medium Armor", "Heavy Armor", "Shields", "Simple Weapons",
                          "Martial Weapons"],
        "special_ability": "Fighting Style",
        "starting_equipment": ["Chain Mail", "Longsword"]},
    "Monk": {
        "title": "Monk",
        "_class_description": "A master of discipline.",
        "hit_die": d8,
        "proficiencies": ["Simple Weapons", "Shortswords"],
        "special_ability": "Unarmored Defense",
        "starting_equipment": ["Shortsword", "Dungeoneer's Pack"]},
    "Paladin": {
        "title": "Paladin",
        "_class_description": "A master of resolve.",
        "hit_die": d10,
        "proficiencies": ["Light Armor", "Medium Armor", "Heavy Armor", "Shields", "Simple Weapons",
                          "Martial Weapons"],
        "special_ability": "Divine Sense",
        "starting_equipment": ["Chain Mail", "Longsword"]},
    "Ranger": {
        "title": "Ranger",
        "_class_description": "A master of sight.", "hit_die": 10,
        "hit_die": d10,
        "proficiencies": ["Light Armor", "Medium Armor", "Shields", "Simple Weapons", "Martial Weapons"],
        "special_ability": "Favored Enemy",
        "starting_equipment": ["Scale Mail", "Longbow"]},
    "Rogue": {
        "title": "Rogue",
        "_class_description": "A master of shadow.", "hit_die": 8,
        "hit_die": d8,
        "proficiencies": ["Light Armor", "Simple Weapons", "Hand Crossbows", "Longswords",
                          "Rapiers", "Shortswords"],
        "special_ability": "Expertise",
        "starting_equipment": ["Rapier", "Dungeoneer's Pack"]},
    "Sorcerer": {
        "title": "Sorcerer",
        "_class_description": "A master of mind.", "hit_die": 6,
        "hit_die": d8,
        "proficiencies": ["Daggers", "Darts", "Slings", "Quarterstaffs", "Light Crossbows"],
        "special_ability": "Sorcerous Origin",
        "starting_equipment": ["Light Crossbow", "Component Pouch"]},
    "Warlock": {
        "title": "Warlock",
        "_class_description": "A master of darkness.", "hit_die": 8,
        "hit_die": d8,
        "proficiencies": ["Light Armor", "Simple Weapons"],
        "special_ability": "Otherworldly Patron",
        "starting_equipment": ["Crossbow, Light", "Component Pouch"]},
    "Wizard": {
        "title": "Wizard",
        "_class_description": "A master of magic.", "hit_die": 6,
        "hit_die": d6,
        "proficiencies": ["Daggers", "Darts", "Slings", "Quarterstaffs", "Light Crossbows"],
        "special_ability": "Arcane Recovery",
        "starting_equipment": ["Quarterstaff", "Component Pouch"]},
    # "Base": {
    #     "title": "Base", 
    #     "description": "A base class for all roles.", "hit_die": 0,
    #     "hit_die": None,
    #     "proficiencies": []},
    # "Abstract": {
    #     "title": "Abstract", 
    #     "description": "An abstract class for all roles.", "hit_die": 0,
    #     "hit_die": None,
    #     "proficiencies": []},
}


class _AbstractRole(_ABC):
    def __init__(self, title, class_description, hit_die, proficiencies):
        self.title = title
        self._class_description = class_description
        self.hit_die = hit_die
        self.proficiencies = proficiencies
        self._special_abilities = {}

    def __str__(self):
        return self.title

    def __repr__(self):
        return f'{self._class_description}'


class _Role(_AbstractRole):
    def __init__(self, title):
        attributes = _ROLE_ATTRIBUTES.get(title)
        super(_Role, self).__init__(attributes['title'], attributes['_class_description'], attributes['hit_die'],
                                   attributes['proficiencies'])

    def _add_special_ability(self):
        ability_name = _SPECIAL_ABILITIES[self.title]["name"]
        ability_class = _SpecialAbilityFactory.create_special_ability(self.title)
        if ability_class is not None:
            ability_instance = ability_class(self.title)
            self._special_abilities[ability_name] = ability_instance
            setattr(self, ability_name.replace(" ", "_").lower(), ability_instance)


class _RoleFactory:
    @staticmethod
    def create_role(role_name):
        role_attr = _ROLE_ATTRIBUTES.get(role_name)
        if role_attr is None:
            return None

        # Create a new class based on the role attributes
        return type(role_name, (_Role,), _ROLE_ATTRIBUTES[role_name])


if __name__ == '__main__':
    role_instances = {}

    for role_name, role_attributes in _ROLE_ATTRIBUTES.items():
        role_class = _RoleFactory.create_role(role_name)
        if role_class is not None:
            role_instance = role_class(role_name)
            role_instances[role_name] = role_instance
            role_instance._add_special_ability()
    globals().update(role_instances)
