import pyglet.shapes as _shapes
import pyglet.window as _window

from typing import Optional as _Optional
from random import randint as _randint

from ..._components.map.board import _Grid
from ..._components.die import _ability_rolls
from ..._components.notation import _DynamicLabel
from ..._items import Armory, Wardrobe
from .._dynamic_entity import _DynamicEntity
from ._ability import _ABILITIES, _AbilityFactory, _SAVING_THROWS
from ._role import _RoleFactory
from ._race import _RaceFactory
from ._skill import _Skillbook, _SKILLS, _SkillFactory
from ._inventory import _Inventory

_key = _window.key

_MOVE_KEYS = [_key.W, _key.D, _key.S, _key.A]


class _BaseActor(_DynamicEntity):
    def __init__(
            self,
            scene: _Optional[object] = None,
            actor_type: _Optional[str] = None,
            name: _Optional[str] = None,
            role: _Optional[str] = None,
            race: _Optional[str] = None,
            age: _Optional[int] = None,
            *args, **kwargs

    ):
        super(_BaseActor, self).__init__(scene, name, *args, **kwargs)
        self._register_event_type('on_level_up')
        self._actor_type = actor_type if actor_type is not None else "Base"
        self.name = name if name is not None else "Unnamed"
        self.level = 1
        self._initial_ability_scores = {}
        self._role = None
        self._race = None
        self._abilities = {}
        self._skills = {}
        self.saving_throws = {}
        self.initiative = 0
        self.skillbook = _Skillbook(self)
        self.skillpoints = 0
        self.armor_class = 0
        self._traveling = False
        self._labels = []
        self._initialize(role, race, age)
        self._shape = _shapes.Rectangle(self._x, self._y, 7, 7, color=(255, 255, 255))

    def _initialize(self, role, race, age):
        self._add_role(role)
        self._add_race(race)
        self._init_ability_scores()
        self._add_abilities()
        self._add_skills()
        self._init_hp()
        self._determine_saves_and_initiative()
        self._set_age(age)
        self._init_inventory()
        self._determine_armor_class()
        self._build_labels()

    def _build_labels(self):
        for attr, value in self.__dict__.items():
            if attr.startswith('_'):
                continue
            if attr in _ABILITIES.keys():
                label = _DynamicLabel(self, attr, 20, 300 + len(self._labels) * 12, None, 1)
            else:
                label = _DynamicLabel(self, attr, 20, 300 + len(self._labels) * 12, None, 2)
            self._labels.append(label)

    def _set_age(self, age: _Optional[int] = None):
        if age is not None and self._race.age['maturity'] <= age <= self._race.age['maximum']:
            setattr(self, 'age', age)
        elif age is None:
            setattr(self, 'age', _randint(self._race.age['maturity'], self._race.age['maximum']))
        else:
            raise ValueError("Age is outside the acceptable range")

    def _init_ability_scores(self):
        initabilityscores = _ability_rolls()
        for ability_name, info in _ABILITIES.items():
            if self._role.title in info["Primary"]:
                self._initial_ability_scores[ability_name] = initabilityscores[0]
                initabilityscores.pop(0)
            else:
                self._initial_ability_scores[ability_name] = initabilityscores[-1]
                initabilityscores.pop(-1)

    def _add_abilities(self):
        for ability_name, info in _ABILITIES.items():
            ability_class = _AbilityFactory.create_ability(self, ability_name)
            if ability_class is not None:
                ability_instance = ability_class
                self._abilities[ability_name] = ability_instance
                setattr(self, ability_name, ability_instance)

    def _determine_saves_and_initiative(self):
        for save, info in _SAVING_THROWS.items():
            ability = info['ability']
            self.saving_throws[save] = self._abilities[ability].modifier
        self.initiative = self._abilities["Dexterity"].modifier

    def _add_role(self, role):
        role_class = _RoleFactory.create_role(role)
        if role_class is not None:
            role_instance = role_class(role)
            self._role = role_instance
            self._role._add_special_ability()
            setattr(self, role_instance.title, role_instance)

    def _init_hp(self):
        self.hp = self._role.hit_die.value + self._abilities["Constitution"].modifier

    def _add_skills(self):
        for skill_name, info in _SKILLS.items():
            skill_class = _SkillFactory.create_skill(self, skill_name)
            if skill_class is not None:
                skill_instance = skill_class
                self._skills[skill_name] = skill_instance
                attr_name = skill_name.title().replace(" ", "_")
                setattr(self.skillbook, attr_name, skill_instance)
                self.skillbook.update({attr_name: skill_instance})

    def _add_race(self, race):
        race_class = _RaceFactory.create_race(race)
        if race_class is not None:
            race_instance = race_class(race)
            self._race = race_instance
            setattr(self, race_instance.title.replace("-", "_"), race_instance)

    def _init_inventory(self):
        setattr(self, 'inventory', _Inventory(self))
        self.inventory.add_item(Armory['Leather Cuirass'])
        self.inventory.add_item(Armory['Leather Boots'])
        self.inventory.add_item(Armory['Leather Gauntlet'])
        self.inventory.add_item(Armory['Leather Gauntlet'])
        self.inventory.add_item(Armory['Leather Helmet'])
        self.inventory.add_item(Armory['Leather Leggings'])
        self.inventory.add_item(Armory['Leather Pauldron'])
        self.inventory.add_item(Armory['Leather Pauldron'])
        self.inventory.add_item(Armory['Leather Bracer'])
        self.inventory.add_item(Armory['Leather Bracer'])
        self.inventory.add_item(Armory['Leather Belt'])
        for i in range(11):
            self.inventory.equip_item(self.inventory.items[i])

    def _determine_armor_class(self):
        ac = self.Dexterity.modifier
        for slot, item in self.inventory.equipment._slots.items():
            if item is not None:
                ac += item.armor_class
        self.armor_class = ac

    def _on_skill_up(self, skill):
        if self.skillpoints > 0:
            self.skillpoints -= 1
            skill.level += 1

    def _process(self):
        self._get_path_to(self._grid.random_cell().designation)
        while self._path:
            self._set_destination()
            self.move()

    def _reflect(self):
        self._shape.x = self.x
        self._shape.y = self.y

    def __repr__(self):
        return f'A level {self.level}, {self._race.title} {self._role.title} named {self.name}\nLocation: Cell -> {self._cell_name}@{self._position}\n\n{self.Strength}\tInitiative: {self.initiative}\n{self.Dexterity}\tHP: {self.hp}\n{self.Constitution}\tAC: {self.armor_class}\n{self.Intelligence}\n{self.Wisdom}\n{self.Charisma}\n\n'

    def _draw(self):
        self._shape.draw()
        [label._draw() for label in self._labels]

    def _update(self):
        super()._update()
        if self._traveling:
            if self._path:
                if self._window.frame_count % 3 == 0:
                    self._set_destination()
                    self.move()
            else:
                self._traveling = False
        self._reflect()
        [label.update() for label in self._labels]

    # @property
    # def role(self):
    #     return self._role

    # @role.setter
    # def role(self, role_name):
    #     role_class = _RoleFactory.create_role(role_name)
    #     if role_class is not None:
    #         self._role = role_class(role_name)
    #         self._role._add_special_ability()
