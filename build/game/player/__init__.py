from ..._entities._character._base_actor import _BaseActor
from ..._entities._character._role import _ROLE_ATTRIBUTES


# Create a new actor

class NewCharacter(_BaseActor):
    def __init__(self, *args, **kwargs):
        self._actor_type = 'Player'
        self.name = self._gather_name()
        self._role_choice = self._gather_role()
        super(NewCharacter, self).__init__(self._actor_type,self.name,self._role_choice)


    def _gather_name(self):
        name = input('What would you like to name your new character?')
        if name != '':
            return name
        else:
            print("If you'd rather not name your character, you may do so later, but for now, we'll call you 'Player'.")
            return 'Player'

    def _gather_role(self):
        role = input('What role will your new character take?\nYou may choose from the following:\n\n1. Barbarian\n2. Bard\n3. Cleric\n4. Druid\n5. Fighter\n6. Monk\n7. Paladin\n8. Ranger\n9. Rogue\n10. Sorcerer\n11. Warlock\n12. Wizard\n\n')
        if role != '':
            role = int(role)
            return list(_ROLE_ATTRIBUTES.keys())[role - 1]
        
# Create a few preset characters

char1 = _BaseActor('Preset', 'Drog', 'Barbarian', 'Half-Orc')
char2 = _BaseActor('Preset', 'Grim', 'Rogue', 'Human')
char3 = _BaseActor('Preset', 'Lilith', 'Wizard', 'Elf')
char4 = _BaseActor('Preset', 'Rex', 'Fighter', 'Dwarf')