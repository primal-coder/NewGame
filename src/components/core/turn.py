from .event import EventDispatcher

class TurnManager(EventDispatcher):
    """TurnManager class
    
    This class is used to manage the turn order of the game. It is used to
    determine which actor is currently active and which actor is next in line.
    
    Attributes:
        window (Window): The window object.
        current_turn (int): The current turn number.
        current_actor (_BaseActor): The current actor.
        actor_list (list): A list of all actors in the game.
        turn_queue (list): A list of actors in turn order.
        turn_queue_index (int): The index of the current actor in the turn queue.
        turn_queue_length (int): The length of the turn queue.
        turn_queue_dirty (bool): Whether the turn queue needs to be sorted.
        turn_queue_sorted (bool): Whether the turn queue is sorted.
        
    Methods:
        create_queue: Creates a turn queue from the actor list.
        add_actor: Adds an actor to the actor list.
        remove_actor: Removes an actor from the actor list.
        get_actor_list: Returns the actor list.
        get_current_actor: Returns the current actor.
        get_current_turn: Returns the current turn number.
        get_turn_queue: Returns the turn queue.
        get_turn_queue_index: Returns the turn queue index.
        get_turn_queue_length: Returns the turn queue length.
        get_turn_queue_dirty: Returns the turn queue dirty flag.
        get_turn_queue_sorted: Returns the turn queue sorted flag.
        set_current_actor: Sets the current actor.
        set_current_turn: Sets the current turn number.
        set_turn_queue: Sets the turn queue.
        set_turn_queue_index: Sets the turn queue index.
        set_turn_queue_length: Sets the turn queue length.
        set_turn_queue_dirty: Sets the turn queue dirty flag.
        set_turn_queue_sorted: Sets the turn queue sorted flag.
        sort_turn_queue: Sorts the turn queue.
        next_turn: Increments the turn number and returns the next actor.
        reset: Resets the turn manager.
        
        """
    def __init__(self, window, first_player=None, second_player=None, length = 10000):
        super(TurnManager, self).__init__()
        self._register_event_type('on_turn_change')
        self.window = window
        self.current_turn_number = 0
        self.current_actor = None
        self.actor_list = []
        self.turn_queue = []
        self.turn_queue_index = 0
        self.turn_queue_length = length
        self.turn_queue_dirty = False
        self.turn_queue_sorted = False
        self.turn_history = []
        self.add_actor(first_player)
        self.add_actor(second_player)
        self.create_queue()
        self.set_current_actor(self.turn_queue[0])
        self.set_current_turn_number(0)
        self.current_turn = Turn(self.current_turn_number, self.current_actor)
        self._set_handler('on_turn_change', self.current_actor._on_turn_change)

    def create_queue(self):
        self.turn_queue = self.actor_list * (self.turn_queue_length//len(self.actor_list))
        self.turn_queue_dirty = True
        self.turn_queue_sorted = True

    def add_actor(self, actor):
        self.actor_list.append(actor)
        self.turn_queue_dirty = True

    def remove_actor(self, actor):
        self.actor_list.remove(actor)
        self.turn_queue_dirty = True

    def get_actor_list(self):
        return self.actor_list
    
    def get_current_actor(self):
        return self.current_actor
    
    def get_current_turn_number(self):
        return self.current_turn_number
    
    def get_turn_queue(self):
        return self.turn_queue
    
    def get_turn_queue_index(self):
        return self.turn_queue_index
    
    def get_turn_queue_length(self):
        return self.turn_queue_length
    
    def get_turn_queue_dirty(self):
        return self.turn_queue_dirty
    
    def get_turn_queue_sorted(self):
        return self.turn_queue_sorted
    
    def set_current_actor(self, actor):
        self.current_actor = actor

    def set_current_turn_number(self, turn):
        self.current_turn_number = turn

    def set_turn_queue(self, queue):
        self.turn_queue = queue

    def set_turn_queue_index(self, index):
        self.turn_queue_index = index

    def set_turn_queue_length(self, length):
        self.turn_queue_length = length

    def set_turn_queue_dirty(self, dirty):
        self.turn_queue_dirty = dirty

    def set_turn_queue_sorted(self, sorted):
        self.turn_queue_sorted = sorted

    def sort_turn_queue(self):
        self.turn_queue.sort(key=lambda actor: actor.get_speed(), reverse=True)
        self.turn_queue_sorted = True

    def next_turn(self):
        self.turn_history.append(Turn(self.current_turn_number, self.current_actor))
        if self.turn_queue_index >= self.turn_queue_length:
            self.turn_queue_index = 0
        else:
            self.turn_queue_index += 1
        self.current_turn_number += 1
        self.current_actor = self.turn_queue[self.turn_queue_index]
        self._dispatch_event('on_turn_change')
        self._set_handler('on_turn_change', self.current_actor._on_turn_change)

    def reset(self):
        self.current_turn_number = 0
        self.current_actor = None
        self.turn_queue = []
        self.turn_queue_index = 0
        self.turn_queue_length = 0
        self.turn_queue_dirty = False
        self.turn_queue_sorted = False

class Turn:
    def __init__(self, turn_number=None, current_actor=None):
        self.turn_number = turn_number if turn_number is not None else 0
        self.current_actor = current_actor if current_actor is not None else None
        self.events = []
