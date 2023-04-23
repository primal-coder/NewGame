from abc import ABC as _ABC
from build._components.die import *
from ..._components.die import _ability_roll
from typing import Optional as _Optional


_ABILITIES = {
    'Strength' : {"Primary":['Barbarian', 'Fighter', 'Paladin', 'Ranger'], "Save": None},
    'Dexterity' : {"Primary":['Bard', 'Monk', 'Rogue', 'Ranger'], "Save": "Reflex"},
    'Constitution' : {"Primary":['Barbarian', 'Fighter', 'Paladin', 'Rogue', 'Sorcerer', 'Warlock'], "Save":"Fortitude" },
    'Intelligence' : {"Primary":['Bard', 'Druid', 'Rogue', 'Wizard'], "Save": None },
    'Wisdom' : {"Primary":['Cleric', 'Druid', 'Monk', 'Ranger', 'Warlock', 'Wizard'], "Save": "Will"},
    'Charisma' : {"Primary":['Bard', 'Cleric', 'Paladin', 'Sorcerer', 'Warlock', 'Wizard'], "Save": None }
}

_SAVING_THROWS = {
    'Fortitude': {'ability': 'Constitution'},
    'Reflex': {'ability': 'Dexterity'},
    'Will': {'ability': 'Wisdom'}
}

_SPECIAL_ABILITIES = {
    "Barbarian": {
        "name": "Rage",
        "description": "\n\033[1mRAGE\033[0m -  In battle, you fight with primal ferocity. On your turn, you can enter a "
                       "rage as a bonus action. \n\tWhile raging, you gain the following "
                       "benefits if you aren't wearing heavy _armor: \n\n"
                       f"\t  \033[1m•\033[0m You have advantage on Strength checks and Strength saving throws. \n\n"
                       f"\t  \033[1m•\033[0m When you make a melee weapon attack using Strength, you gain a "
                       "bonus \n\t  to the damage roll that increases as you gain levels as a "
                       "barbarian, \n\t  as shown in the Rage Damage column of the Barbarian table. \n\n"
                       f"\t  \033[1m•\033[0m You have resistance to bludgeoning, piercing, and slashing damage. \n\n"
                       "\tIf you are able to cast spells, you can't cast them or concentrate on "
                       "them while raging. \n"
                       "\tYour rage lasts for 1 minute. It ends early if you are knocked "
                       "unconscious or if your turn ends \n\tand you haven't attacked a hostile "
                       "creature since your last turn or taken damage since then.\n\tYou can also "
                       "end your rage on your turn as a bonus action. "
                       "Once you have raged the number of times \n\tshown for your barbarian level "
                       "in the Rages column of the Barbarian table,\n\tyou must finish a long rest "
                       "before you can rage again."},

    "Bard": {
        "name": "Bardic Inspiration",
        "description": "\n\033[1mBARDIC INSPIRATION\033[0m -    You can inspire others through stirring words or music." 
        "To do so, you use a bonus action on your turn\n\t\t\tto choose one creature other than yourself within 60 feet of you who can hear you." 
        "That creature gains one Bardic Inspiration die, a d6.\n\t\t\tOnce within the next 10 minutes, the creature can roll the die" 
        "and add the number rolled to one ability check, attack roll,\n\t\t\tor saving throw it makes. The creature can wait until after it" 
        "rolls the d20 before deciding to use the Bardic Inspiration die, \n\t\t\tbut must decide before the DM says whether the roll succeeds or fails." 
        "Once the Bardic Inspiration die is rolled, it is lost. \n\t\t\tA creature can have only one Bardic Inspiration die at a time." 
        "You can use this feature a number of times equal to your Charisma \n\t\t\tmodifier (a minimum of once). You regain any expended uses when you finish a long rest."""
}, 
    "Cleric": {
        "name": "Channel Divinity",
        "description": "At 2nd level, you gain the ability to channel divine energy directly "
                       "from your deity, using that energy to fuel magical effects. Each "
                       "Cleric domain has its own Channel Divinity option. When you use your "
                       "Channel Divinity, you choose which option to use. You must then finish "
                       "a short or long rest to use your Channel Divinity again. \n"
                       "Some Channel Divinity effects require saving throws. When you use such "
                       "an effect from this class, the DC equals your cleric spell save DC."},
    "Druid": {
        "name": "Druidic",
        "description": "You know Druidic, the secret language of druids. You can speak the "
                       "language and use it to leave hidden messages. You and others who "
                       "know this language automatically spot such a message. Others spot "
                       "the message's presence with a successful DC 15 Wisdom (Perception) "
                       "check but can't decipher it without magic."},
    "Fighter": {
        "name": "Fighting Style",
        "description": "You have trained extensively to gain the following benefits: \n"
                       "• Increase your Strength or Dexterity score by 1, to a maximum of 20. \n"
                       "• You learn one additional fighting style of your choice. \n"
                       "• You gain proficiency with light _armor."},
    "Monk": {
        "name": "Unarmored Defense",
        "description": "While you are not wearing any _armor, your Armor Class equals 10 + your "
                       "Dexterity modifier + your Wisdom modifier. You can use a shield and "
                       "still gain this benefit."},
    "Paladin": {
        "name": "Divine Sense",
        "description": "The presence of strong evil registers on your senses like a noxious "
                       "odor, and powerful good rings like heavenly music in your ears. As an "
                       "action, you can open your awareness to detect such forces. Until the "
                       "end of your next turn, you know the location of any celestial, fiend, "
                       "or undead within 60 feet of you that is not behind total cover. "
                       "You know the type (celestial, fiend, or undead) of any being whose "
                       "presence you sense, but not its identity (the vampire Count Strahd "
                       "von Zarovich, for instance). Within the same radius, you also "
                       "detect the presence of any place or object that has been consecrated "
                       "or desecrated, as with the hallow spell. You can use this feature "
                       "a number of times equal to 1 + your Charisma modifier. When you "
                       "finish a long rest, you regain all expended uses."},
    "Ranger": {
        "name": "Favored Enemy",
        "description": "Beginning at 1st level, you have significant experience studying, "
                          "tracking, hunting, and even talking to a certain type of enemy. "
                            "Choose a type of favored enemy: aberrations, beasts, celestials, "
                            "constructs, dragons, elementals, fey, fiends, giants, monstrosities, "
                            "naga, oozes, plants, or undead. Alternatively, you can select two "
                            "races of humanoid (such as gnolls and orcs) as favored enemies. \n"
                            "You have advantage on Wisdom (Survival) checks to track your "
                            "favored enemies, as well as on Intelligence checks to recall "
                            "information about them. \n"
                            "When you gain this feature, you also learn one language of your "
                            "choice that is spoken by your favored enemies, if they speak one "
                            "at all. \n"
                            "You choose one additional favored enemy, as well as an associated "
                            "language, at 6th and 14th level. \n"
                            "Your choices should reflect the types of monsters you are likely "
                            "to encounter during your adventures. \n"
                            "You can also select a favored enemy option presented to you in an "
                            "adventure. Doing so grants you features when you choose it and "
                            "at 6th and 14th level."},
    "Rogue": {
        "name": "Sneak Attack",
        "description": "Beginning at 1st level, you know how to strike subtly and exploit a "
                          "foe's distraction. Once per turn, you can deal an extra 1d6 damage to "
                            "one creature you hit with an attack if you have advantage on the attack "
                            "roll. The attack must use a finesse or a ranged weapon. \n"
                            "You don't need advantage on the attack roll if another enemy of the "
                            "target is within 5 feet of it, that enemy isn't incapacitated, and you "
                            "don't have disadvantage on the attack roll. \n"
                            "The amount of the extra damage increases as you gain levels in this "
                            "class, as shown in the Sneak Attack column of the Rogue table. \n"
                            "At 11th level, you also gain the ability to deal this extra damage "
                            "when a creature is within 5 feet of an ally of yours that isn't "
                            "incapacitated and you don't have disadvantage on the attack roll. "
                            "A creature is within 5 feet of an ally if the ally is within 5 feet "
                            "of the creature, or the ally is within 5 feet of a hostile creature "
                            "that is within 5 feet of the creature. \n"
                            "You don't need advantage on the attack roll if another enemy of the "
                            "target is within 5 feet of it, that enemy isn't incapacitated, and you "
                            "don't have disadvantage on the attack roll. \n"
                            "The amount of the extra damage increases as you gain levels in this "
                            "class, as shown in the Sneak Attack column of the Rogue table. \n"
                            "At 11th level, you also gain the ability to deal this extra damage "
                            "when a creature is within 5 feet of an ally of yours that isn't "
                            "incapacitated and you don't have disadvantage on the attack roll. "
                            "A creature is within 5 feet of an ally if the ally is within 5 feet "
                            "of the creature, or the ally is within 5 feet of a hostile creature "
                            "that is within 5 feet of the creature."},
    "Sorcerer": {
        "name": "Sorcerous Origin",
        "description": "At 1st level, you choose a sorcerous origin, which describes the source "
                            "of your innate magical power: Draconic Bloodline, Wild Magic, or "
                            "the Divine Soul. Your choice grants you features at 1st level and "
                            "again at 6th, 14th, and 18th level."},
    "Warlock": {
        "name": "Otherworldly Patron",
        "description": "At 1st level, you have struck a bargain with an otherworldly being of "
                            "your choice: the Archfey, the Fiend, or the Great Old One, each of "
                            "which is detailed at the end of the class description. Your choice "
                            "grants you features at 1st level and again at 6th, 10th, and 14th "
                            "level."},
    "Wizard": {
        "name": "Arcane Recovery",
        "description": "You have learned to regain some of your magical energy by studying "
                            "your spellbook. Once per day when you finish a short rest, you can "
                            "choose expended spell slots to recover. The spell slots can have a "
                            "combined level that is equal to or less than half your wizard level "
                            "(rounded up), and none of the slots can be 6th level or higher. \n"
                            "For example, if you're a 4th-level wizard, you can recover up to two "
                            "levels worth of spell slots. You can recover either a 2nd-level slot "
                            "or two 1st-level slots. You can't recover any 3rd-level or higher "
                            "slots with this feature, and you can't recover a 2nd-level slot and "
                            "a 1st-level slot, since the slots have a combined level of 3, which "
                            "is higher than half your wizard level. \n"
                            "You regain all expended spell slots when you finish a long rest."},
    } 

# Path: build/_Ability.py

# build an _Ability class which can be attached to a character

# The class should have a constructor that takes a character object, the ability name and score as an argument.

# The class should have a method to calculate the modifier from the score.

# The class should have a method to permanently alter the score.

# The class should have a method to temporarily alter the score.

# The class should have a method that returns the ability score.

# The class should have a method that returns the ability modifier.

# The class should have a method which performs an ability check and returns the result.

# The class should have a method which can determine if the ability is a primary ability.
# The method should have a constructor that takes a character_class as an argument
# The method should return True if the ability is a primary ability for the character_class.

class _AbstractAbility:
    def __init__(
            self,
            parent: _Optional[object] = None,
            name: _Optional[str] = None,
            score: _Optional[int] = None,
    ) -> None:
        """
        Abstract class representing an ability.
        :param parent: The object that has this ability.
        :param name: The name of the ability.
        :param score: The score associated with the ability.
        """
        self.parent = parent
        self.name = name
        self.primary = self.is_primary(self.parent._role.title)
        self.short = name[0:3].upper()
        self.score = score if score is not None else _ability_roll()
        self.modifier = (self.score - 10) // 2
        self.temp_mod = 0
        self.temp_mod_duration = 0

    

    def _get_score(self):
        """
        Gets the score associated with the ability.
        """
        
        return self.score
    
    def _get_modifier(self):
        """
        Gets the modifier associated with the ability.
        """
        
        return self.modifier
    
    def _set_score(self, score: int):
        """
        Sets the score associated with this ability.
        """
        
        self.score = score
        self.modifier = (self.score - 10) // 2

    def _increase_score(self, amount: int):
        """
        Inceases the score associated with this ability
        """
        
        self._set_score(self.score + amount)

    def _decrease_score(self, amount: int):
        """
        Decreases the score associated with this ability
        """

        self._set_score(self.score - amount)

    def _plus_one(self):
        """
        Increases the ability score by a single point.
        """

        self._increase_score(1)

    def _minus_one(self):
        """
        Decreases the ability score by a single point.
        """
        
        self._decrease_score(1)
    
    def ability_check(self, dc: int):
        """
        Checks if the ability passes a DC check.
        :param dc: The DC value to check against.
        :return: True if the check passes, False otherwise.
        """
    
        mod = self.modifier + self.temp_mod
        return check(mod, dc)
    
    def is_primary(self, role: _Optional[str] = None):
        """
        Checks if the ability is a primary ability for a given role.
        :param role: The role to check against.
        :return: True if the ability is a primary ability for the given role, False otherwise.
        """
        
        if role is None:
            role = self.parent._role.title
        return role in _ABILITIES[self.name]
    
    def __str__(self):
        """
        Gets a string representation of the ability.
        :return: A string representation of the ability.
        """

        return f'{self.short}: {self.score} ({"+" if self.modifier > 0 else ""}{self.modifier})'
    
    def __repr__(self):
        
        return f'{self.short}: {self.score} ({"+" if self.modifier > 0 else ""}{self.modifier})'
    
class _Ability(_AbstractAbility):
    """A class representing an ability score for a actor, such as strength or dexterity.

    Attributes:
    - name (str): The name of the ability score.
    - _init_score (_Optional[int]): The initial score of the ability, if it is provided in the parent object.
    """

    def __init__(
            self,
            parent: _Optional[object] = None,
    ):
        """Initialize a new _Ability object.

        Args:
        - parent (_Optional[object]): The parent object that the ability belongs to, usually a BaseActor object.
        """
        self.name = self.__class__.__name__.capitalize()
        self._init_score = parent._initial_ability_scores[self.name] if parent._initial_ability_scores is not None else None
        if self.name in parent._race.racial_bonuses.keys():
            self._racial_bonus = parent._race.racial_bonuses[self.name]
            self._init_score += self._racial_bonus
        super(_Ability, self).__init__(parent, self.name, self._init_score)
        if _ABILITIES[self.name]["Save"] is not None:
            setattr(self, f'{_ABILITIES[self.name]["Save"].lower()}_save',  self.ability_check)


class _AbilityFactory:
    """A factory class for creating _Ability objects.

    Methods:
    - create_ability(parent, ability_name): Create a new _Ability object with the given parent object and ability name.
    """
    
    @staticmethod
    def create_ability(parent, ability_name):
        """Create a new _Ability object with the given parent object and ability name.

        Args:
        - parent (object): The parent object that the ability belongs to.
        - ability_name (str): The name of the ability to create.

        Returns:
        - _Ability: The newly created _Ability object.
        """
    
        if ability_name is not None:
            return type(ability_name, (_Ability,), {})(parent )
        return None

class _AbstractSpecialAbility(_ABC):
    """An abstract base class for special abilities that a actor can have.

    Attributes:
    - name (str): The name of the special ability.
    - description (str): A description of the special ability.
    """
    def __init__(
            self, 
            name: str, 
            description: str
            ) -> None:
        """Initialize a new _AbstractSpecialAbility object.

        Args:
        - name (str): The name of the special ability.
        - description (str): A description of the special ability.
        """
        self.name = name
        self.description = description


class _SpecialAbility(_AbstractSpecialAbility):
    """A class representing a special ability that a actor can have.

    Attributes:
    - _role_title (_Optional[str]): The role title of the special ability, if it is provided in the parent object.
    """

    def __init__(
            self, 
            role_title: _Optional[str] = None
            ) -> None:
        self._role_title = role_title
        attributes = _SPECIAL_ABILITIES[self._role_title]
        super(_SpecialAbility, self).__init__(attributes["name"], attributes["description"])

    def __repr__(self):
        """Return a string representation of the _SpecialAbility object.

        Returns:
        - str: A string representation of the _SpecialAbility object.
        """

        return self.description

    def __str__(self):
        """Return a string representation of the _SpecialAbility object.

        Returns:
        - str: A string representation of the _SpecialAbility object.
        """
        return f'{self.name}: {self.description}'

class _SpecialAbilityFactory:
    @staticmethod
    def create_special_ability(role_title):
        """
        A static method that creates an instance of the _SpecialAbility class based on the attributes
        defined in the _SPECIAL_ABILITIES dictionary for the given role title.

        Args:
        - role_title: A string representing the role title for which a special ability needs to be created.

        Returns:
        - An instance of the _SpecialAbility class or None if the role title is not found in _SPECIAL_ABILITIES.
        """
        
        special_ability_attr = _SPECIAL_ABILITIES[role_title]
        if special_ability_attr is None:
            return None
        return type(special_ability_attr["name"], (_SpecialAbility,), dict(special_ability_attr))
    
if __name__ == '__main__':
    specialability_instances = {}
    
    for role_title, special_ability_attr in _SPECIAL_ABILITIES.items():
        specialability_class = _SpecialAbilityFactory.create_special_ability(role_title)
        if specialability_class is not None:
            specialability_instance = specialability_class(role_title)
            specialability_instances[special_ability_attr["name"].replace(" ","_").lower()] = specialability_instance
    globals().update(specialability_instances)