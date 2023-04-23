from typing import Optional


class Encounter:
    def __init__(
            self,
            participants: Optional[list[object, ]] = None,
    ):
        self.round_count = 0
        self.current_round = None
        self.participants = participants if participants is not None else []
        self.feed_line = None

    def start_feed(self):
        pass


class Round:
    def __init__(self, round_id, participants):
        self.round_id = round_id
        self.participants = participants
        self.turn_count = 0
        self.current_turn = None
        self.turns = []
        self.current_actor = None

    def record_turn(self):
        self.turns.append(self.current_turn)

    def clear_turn(self):
        self.current_turn = None

    def clear_actor(self):
        self.current_actor = None

    def set_actor(self):
        self.current_actor = self.participants[self.turn_count%len(self.participants)]

    def new_turn(self):
        self.set_actor()
        self.current_turn = Turn(self, self.turn_count, self.current_actor)

    def end_turn(self):
        self.record_turn()
        self.clear_turn()
        self.clear_actor()
        self.turn_count += 1

    def process_round(self):
        self.new_turn()
        self.end_turn()
# Create a Turn class which will be used to track the all of the events that occur during a turn,
# including actions taken by characters, NPCs and the DM and the relevant rolls, damage dealt/damage taken,
# status changes, duration of effects, etc.

# The class should have attributes for encounter, index, attendance, actions, the current actor, etc.
# The class should have a method that adds each attendant in an encounter to a list
# The class should have a method to update the current actor

class Turn: 
    def __init__(self, round, turn_id, actor):
        self.round = round
        self.turn_id = turn_id
        self.actor = actor
        self.actor_intent = self.actor.intent
        self.event_count = 0
        self.events = {}
        self.current_event = None
        self.event_dc = None
        self.active = True
        self.feed_line = None

    def start_feed(self):
        pass

    def get_event(self, event_id):
        return self.events[event_id]

    def record_event(self):
        self.events[self.event_count] = {"actor": self.actor, "intent":self.actor_intent, "event":self.current_event}

    def clear_event(self):
        self.current_event = None

    def new_event(self):
        if self.actor_intent.upper() == "Move":
            self.current_event = Move(self.actor, self.actor.destination)

    def prepare_for_event(self):
        self.clear_event()
        self.clear_intent()
        self.clear_event_dc()
    
    def proceed(self):
        self.record_event()
        self.prepare_for_event()
        self.event_count += 1

    def process_turn(self):
        self.read_intent()
        self.new_event()
        self.proceed()

    def read_intent(self):
        self.actor_intent = self.actor.intent

    def clear_intent(self):
        self.actor_intent = None

    def set_event_dc(self, dc):
        self.event_dc = dc

    def clear_event_dc(self):
        self.event_dc = None

    def end_turn(self):
        self.active = False


# Build an Event class which represents any single event which may take place during a turn, including character actions, ability rolls,
# damage rolls, status effects, conditions, etc.

EVENT_TYPES = ["Action", "Effect", "Check", "Pass"]

ACTION_TYPES = ["Attack", "Cast", "Prepare", "Use", "Move"]

CHECK_TYPES = ["Save", "Skill", "Unknown"]

EFFECT_TYPES = ["Buff", "Debuff", "Taunt", "Condition"]

EVENT_FAMILY = {"Event": {
    "Action": { 
        "Attack": ["Basic attack", "Full-round attack", "Grapple", "Unarmed attack"],
        "Cast": ["Cantrip", "Esotery", "Incantation", "Spell"],
        "Prepare": ["Channel", "Don"],
        "Move": "Move",
        "Pass": "Pass"
        },
    "Effect": {
        "Buff": ["Heal", "Shield", "Cloak", "Empower", "Haste", "Prayer"],
        "Debuff": ["Curse", "Hex", "Enfeeble", "Silence", "Fear", "Disarm"],

        },
    "Check": {
        "Save":["Will","Reflex","Fortitude"],
        "Skill": ["","",""],
        "Unknown": "Unknown"
        }
    }
}

class AbstractEvent:
    def __init__(self, *args, **kwargs):
        self.event_type = "abstract"
        self.actor = None
        self.instrument = None
        self.intent = None
        self.target = None
        self.dc = None
        self.description = None
        self.encounter = None

class BaseEvent(AbstractEvent):
    def __init__(
            self,
            event_type: Optional[str] = None,            
            actor: Optional[object] = None,
            instrument: Optional[object] = None,
            target: Optional[list[object,]] = None,
            dc: Optional[int] = None,
            description: Optional[str] = None,
            *args, **kwargs
    ) -> None:
        self.event_type = event_type if event_type is not None else "Base"
        self.actor = actor
        self.instrument = instrument
        self.intent = actor.intent
        self.target = target
        self.dc = dc
        self.description = description
        self.encounter = None

    def queue(self):
        pass

    def perform(self):
        pass


class Action(BaseEvent):
    def __init__(
        self, 
        name: Optional[str]  = None, 
        actor: Optional[object] = None, 
        instrument: Optional[object] = None, 
        target: Optional[object] = None, 
        dc: Optional[int] = None,  
        description: Optional[str] = None
    ):
        self.action_name = name
        super(Action, self).__init__("Action", actor, instrument, target, dc, description)
        self.result = None

    def perform(self):
        pass


class Attack(Action):
    def __init__(
        self, 
        actor: Optional[object] = None, 
        target: Optional[object] = None
    ):
        super(Attack, self).__init__("Attack", actor, actor.weapon, target.ac, target, f"{actor.name} attacks {target.name}")

    def perform(self):
        pass

class Prepare(Action):
    def __init__(
        self, 
        actor, tactic, plan, dc):
        super(Prepare, self).__init__("Prepare", actor, tactic, plan, dc  )

    def perform(self):
        pass

class Cast(Action):
    def __init__(
        self, 
        actor, target):
        super(Cast, self).__init__("Cast", actor, actor.spell, target, actor.spell.save, f"{actor.name} casts {actor.spell.name} on {target.name}")

    def perform(self):
        pass

class Use(Action):
    def __init__(
        self, 
        actor, item, target):
        super(Use, self).__init__("Use", actor, item, target, item.dc, f"{actor.name} uses {item.name} on {target.name}")

    def perform(self):
        pass

class Move(Action):
    def __init__(
            self,
            actor,
            target
    ):
        super(Move, self).__init__("Move", actor, None, target, None, f'{actor.name} moves from {actor.current_cell} to {target.designation}.')

    def perform(self):
        pass

class Check(BaseEvent):
    def __init__(
        self, 
        name, target, ability,  dc):
        self.check_name = name
        super(Check, self).__init__("Check", None, ability, target, dc)

    def perform(self):
        pass

class Save(Check):
    def __init__(
        self, 
        name, target, save, dc):
        self.save_name = name
        super(Save, self).__init__("Save", target, save, dc)

    def perform(self):
        pass

class Effect(BaseEvent):
    def __init__(
        self, 
        name, source: Optional[object] = None, target: Optional[list[object,]] = None, dc: int = None):
        self.effect_name = name
        super(Effect, self).__init__("Effect", None, source, target, dc, None)

    def perform(self):
        pass

class Buff(Effect):
    def __init__(
        self, 
        name, source, target, dc):
        self.buff_name = name
        super(Buff,self).__init__("Buff", source, target, dc)

    def perform(self):
        pass


class EventFactory:
    @staticmethod
    def create_event(event_type,actor, instrument, target, dc, description):
        pass