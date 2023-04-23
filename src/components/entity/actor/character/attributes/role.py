from src.components.utility.saved_objects import load_json as _load_json
from src.components.misc.die import *
from src.components.entity.actor.character.attributes.ability import _ABC, SPECIAL_ABILITIES as _SPECIAL_ABILITIES, SpecialAbilityFactory as _SpecialAbilityFactory

ROLE_ATTRIBUTES = _load_json('src/dicts/role_attributes.json')

class AbstractRole(_ABC):
    def __init__(self, title, class_description, hit_die, proficiencies):
        self.title = title
        self._class_description = class_description
        self.hit_die = Die(int(hit_die.removeprefix('d'))) if isinstance(hit_die, str) else hit_die
        self.proficiencies = proficiencies
        self._special_abilities = {}

    def __str__(self):
        return self.title

    def __repr__(self):
        return f'{self._class_description}'


class Role(AbstractRole):
    def __init__(self, title):
        attributes = ROLE_ATTRIBUTES.get(title)
        super(Role, self).__init__(attributes['title'], attributes['_class_description'], attributes['hit_die'],
                                   attributes['proficiencies'])

    def add_special_ability(self):
        ability_name = _SPECIAL_ABILITIES[self.title]["name"]
        ability_class = _SpecialAbilityFactory.create_special_ability(self.title)
        if ability_class is not None:
            ability_instance = ability_class(self.title)
            self._special_abilities[ability_name] = ability_instance
            setattr(self, ability_name.replace(" ", "_").lower(), ability_instance)


class RoleFactory:
    @staticmethod
    def create_role(role_name):
        role_attr = ROLE_ATTRIBUTES.get(role_name)
        if role_attr is None:
            return None

        # Create a new class based on the role attributes
        return type(role_name, (Role,), ROLE_ATTRIBUTES[role_name])


if __name__ == '__main__':
    role_instances = {}

    for role_name, role_attributes in ROLE_ATTRIBUTES.items():
        role_class = RoleFactory.create_role(role_name)
        if role_class is not None:
            role_instance = role_class(role_name)
            role_instances[role_name] = role_instance
            role_instance.add_special_ability()
    globals().update(role_instances)
