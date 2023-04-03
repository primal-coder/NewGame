""" _Die and Dice rolling module

This module allows for the creation and use of _Die objects that can be used to
emulate any sort of die rolling activities related to role playing games. It
also provides a few static functions for rolling die and generating ability
scores. 

"""

import types as _types
from random import randint as _randint, choice as _choice
from time import sleep as _sleep
from typing import Optional as _Optional, Callable as _Callable, Union as _Union

import pyglet.event


# Path: build/Dice.py

# Create a static roll function which accepts the die to roll as an argument.

# The function should return the result of the roll.

def roll(
        die: _Union[_Callable[[int], None], int, tuple[_Callable, ], tuple[int, ], list[_Callable, ], list[int, ]] = None
) -> int:
    """
    Rolls a die with the specified number of sides.

    Args: die (_Union[_Callable[[int], None], int]): The die to roll. Either an integer representing the number of
    sides on a standard die, a custom die object with a 'roll' method that takes an integer argument and returns an
    integer, or None.

    Returns:
        int: The result of the die roll.
    """
    if die is not None:
        if isinstance(
                die,
                _Die
        ):
            return die.roll()
        elif isinstance(
                die,
                int
        ):
            d = _Die(die)
            r = d.roll()
            return r
        elif isinstance(
                die,
                tuple
        ):
            raise ValueError(
                "Try usig the rolls function instead of the roll function for rolling multiple die."
                "\nLike this:\n\t`rolls(3, d6)`")
        elif isinstance(
                die,
                list
        ):
            raise ValueError(
                "Try usig the rolls function instead of the roll function for rolling multiple die."
                "\nLike this:\n\t`rolls(3, d6)`")
        else:
            try:
                i = int(die)
                d = _Die(i)
                r = d.roll()
                return r
            except ValueError:
                raise ValueError(
                    "Try again with an argument that can be interpreted as an integer or one as an instance of the "
                    "_Die class."
                    "\nLike this:\n\t`roll(6)` or `roll(d8)`"
                )
    else:
        standard = _Die(6)
        r = standard.roll()
        return r


# Create a static rolls function which accepts a number of die to roll and the type of die to roll.

# The function should return the total of all die rolled.

def rolls(
        dice: _Optional[int] = None,
        die: _Union[_Callable[[int], None], int] = None
) -> int:
    """
    Rolls a number(dice) of die(die) and returns the total. If no arguments are provided, a single 6-sided die is rolled.


    @param dice:
    @param die:
    @return:
    """
    if dice is None:
        dice = 1
    if die is None:
        die = 6
    if isinstance(
        die,
        _Die
    ):
        total = 0
        for i in range(dice):
            total += die.roll()
        return total
    elif isinstance(
        die,
        int
    ):
        d = _Die(die)
        total = 0
        for i in range(dice):
            total += d.roll()
        return total

# Create static roll_sequence function which accepts the number of die to roll and the type of die to roll.

# This function should return a set of `die.roll()` results at the length of the value of the `die` parameter


def roll_sequence(
        dice: int,
        die: _Union[_Callable[[int], None], int]
) -> tuple:
    """
    Rolls a sequence of die and returns the results as a tuple.

    @param dice:
    @param die:
    @return:
    """
    result = []
    for i in range(dice):
        result.append(die.roll())
    return tuple(result)


# Create a static _ability_roll function which accepts no arguments

# The function should return a tuple of 4 numbers as a list, each between 1 and 6, and the sum of the 3 highest numbers.

def _ability_roll() -> tuple:
    """
    Rolls 5d6 and returns the sum of the 3 highest numbers.

    @return:
    """
    rs = []
    for i in range(5):
        rs.append(_randint(1, 6))
    rs.sort()
    return rs, sum(rs[2:])


# Create a static _ability_rolls function which accepts no arguments

# The function should return a list of all 6 ability rolls ordered from highest to lowest.

def _ability_rolls(expunge: _Optional[bool] = True) -> list:
    """
    Rolls 6 ability scores and returns them in a list ordered from highest to lowest.

    @return:
    """
    rs = []
    for i in range(6):
        rs.append(_ability_roll())
    rs = [rs[i][1] for i in range(len(rs))]
    rs.sort(reverse=True)
    if expunge:
        if rs[-1] < 12:
            print("Expunging low ability scores (<= 11) ... ")
            rs = _ability_rolls()
    return rs


# Create a check function which accepts an ability_modifier and dc as arguments.

# The function should return True if the ability_modifier is greater than or equal to the dc.

# The function should return (True, True) if the result of the roll is a 20 to indicate a critical success.

# The function should return False if the ability_modifier is less than the dc or the result of the roll is a 1.

def check(
        modifier: _Optional[int] = None,
        dc: _Optional[int] = None) -> bool:
    mod = modifier if modifier is not None else 0
    r = d20.roll()
    result = (r + mod >= dc) if r not in (1, 20) else (r == 20)
    return result


# Build a die class that can be used to roll a die with a given number of sides.

# The class should have a constructor that takes the number of sides as an argument.

# The class should have a roll method that returns a random number between 1 and the number of sides.

# The class should have a flip method that returns either "heads" or "tails".

# The class should have a __str__ method that returns a string representation of the die.

# The class should have a __repr__ method that returns a string representation of the die.

# The class should have a __int__ method that returns the number of sides on the die.


class _Die(pyglet.event.EventDispatcher):
    """
    ~py class:: _Die(value=6)
    ~pyglet::event::EventDispatcher

    A class to represent a die, which can be rolled to produce a random value between 1 and the specified number of
    sides, or flipped like a coin to produce either "heads" or "tails". _Die objects can be used as arguments to the
    roll function. The roll function will return the result of the roll. The roll function can also be used to roll
    multiple die at once, and will return the total of all die rolled. The roll function can also be used to roll a
    sequence of die and will return a tuple of the results of the rolls. The roll function can also be used to roll
    ability scores and will return a list of 6 ability scores ordered from highest to lowest. The _Die class subclasses
    the pyglet.event.EventDispatcher class and raises an event "on_roll" when the die is rolled. The _Die class also
    raises an event "on_rolls" when the roll function is used to roll a sequence of die.

    Attributes:
    value (int): The number of sides on the die. Defaults to 6 if no value is specified.

    Methods:
    roll(self) -> int:
    Rolls the die and returns a random value between 1 and the number of sides on the die.
    Raises an event "on_roll" with the last roll as argument.

    rolls(self) -> tuple:
    Rolls the die and returns a tuple of the results of the rolls.

    flip(self) -> str:
    Flips the coin and returns either "heads" or "tails".

    __str__(self) -> str:
    Returns a string representation of the die.

    __repr__(self) -> str:
    Returns a string representation of the die.

    __int__(self) -> int:
    Returns the number of sides on the die.

    Events:
    on_roll(self, roll: int):
    Event raised when the die is rolled.

    on_rolls(self, rolls: tuple):
    Event raised when the die is rolled multiple times.

    """

    def __init__(
            self,
            value: int = None
    ) -> None:
        super().__init__()
        self.register_event_type('on_roll')
        self.register_event_type('on_rolls')
        self.value = value if value is not None else 6
        if self.value > 2:  # if the die is not a coin
            def roll(self) -> int:
                """
                Rolls the die and returns a random value between 1 and the number of sides on the die.
                Raises an event "on_roll" with the _Die object which was rolled and the last roll as arguments.

                @param self:
                @return:
                """
                self.last_roll = _randint(1, self.value)
                self.dispatch_event('on_roll', (self, self.last_roll))
                _sleep(_choice([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]))
                return self.last_roll

            setattr(self, 'roll', _types.MethodType(roll, self))
            setattr(self, 'last_roll', None)

            def rolls(self, quantity: int = None, total: bool = False) -> _Union[tuple, int]:
                """
                Rolls the die a specified number of times (defaulting to 1) and returns a tuple of the results. If the
                total argument is True, the sum of the rolls is returned instead of the tuple. Raises an event "on_rolls"
                with the last roll as argument.

                @param self:
                @param quantity:
                @param total:
                """

                r = []
                for _ in range(quantity):
                    r.append(_randint(1, self.value))
                if total:
                    self.last_roll = sum(r)
                else:
                    self.last_roll = tuple(r)
                self.dispatch_event('on_rolls', (self, self.last_roll))
                return self.last_roll

            setattr(self, 'rolls', _types.MethodType(rolls, self))
        else:  # if the die is a coin
            def flip(self) -> str:
                """
                Flips the die like a coin and returns either "heads" or "tails".
                Raises an event "on_roll" with the last flip as argument.

                @param self:
                @return:
                """

                flip = _randint(0, 1)
                sides = ['heads', 'tails']
                self.last_flip = sides[flip]
                self.dispatch_event('on_roll', self.last_flip)
                return self.last_flip

            setattr(self, 'flip', _types.MethodType(flip, self))
            setattr(self, 'last_flip', None)

    def __str__(self):
        if self.value > 2:
            return f'd{self.value}'
        else:
            return 'coin'

    def __repr__(self):
        if self.value > 2:
            return f'{self.value}-sided die'
        else:
            return 'coin'

    def __int__(self):
        return self.value


class _d20(_Die):
    """
    A class to represent a _d20, which can be rolled to produce a random value between 1 and 20. The class also has a
    check function which accepts an ability_modifier and dc as arguments. The class also has a get_last_check function
    which returns the result of the last check. The class also has an on_check event which is raised when a check is
    made. The event passes the result of the check as an argument.

    Attributes:
    value (int): The number of sides on the die. Defaults to 20 if no value is specified.

    Methods:
    check(self, mod: int, dc: int) -> None:

    get_last_check(self) -> bool:

    on_roll(self, value: int) -> None:

    on_check(self, value: bool) -> None:
    """

    def __init__(self):
        super(_d20, self).__init__(20)
        self.register_event_type('on_check')
        self.last_check = None

    def check(self, mod: int = None, dc: int = None) -> bool:
        """
        Rolls the die and checks if the result plus the modifier is greater than or equal to the dc. Raises an event

        @param mod:
        @param dc:
        @return:
        """
        res = self.roll()
        fin = res + mod
        self.last_check = fin >= dc
        self.dispatch_event('on_check', self.last_check)
        return self.last_check

    def get_last_check(self):
        """
        Returns the result of the last check.
        @return:
        """
        return self.last_check


# Create all the die

coin = _Die(2)
d4 = _Die(4)
d6 = _Die(6)
d8 = _Die(8)
d10 = _Die(10)
d12 = _Die(12)
d20 = _d20()
