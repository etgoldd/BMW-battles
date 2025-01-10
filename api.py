"""
Welcome to the API Documentation!

You probably want to get started with `API` methods, and have a look at `Exceptions`.
"""

from dataclasses import dataclass
from enum import IntEnum
from typing import List, Optional, Tuple


class Exceptions(IntEnum):
    """
    An enum representing result of API methods.
    See each method for a list of possible exceptions.
    If a method was successful, it always returns `OK`.
    """

    OK = 0

    NOT_ENOUGH_RESOURCES = 1
    """You don't have the resource/development card required for the action."""

    NOT_A_RESOURCE = 2
    """The given `Resources` argument is invalid."""

    ILLEGAL_POSITION = 3
    """One of the given positions is not a legal point on the map corresponding to the correct item (intersection/edge/terrain), or doesn't abide by positioning rules (for instance, a taken position or a neighboring such position)."""

    ILLEGAL_PLAYER_INDEX = 4
    """An illegal player index parameter was passed to the action."""

    ILLEGAL_OFFER_INDEX = 5
    """An illegal offer index was passed to the action."""

    OUT_OF_ITEMS = 6
    """You don't have enough settlement/city/road/development cards to perform this action."""

    TOO_MANY_TRADES = 7
    """You've surpassed the maximum trade offers allowed per turn, which is 5."""

    BAD_TIMING = 8
    """You called this action in an invalid stage or turn."""

    ALREADY_PLAYED_DEVELOPMENT_CARD = 9
    """You cannot play more than one development card per turn."""

    BAD_AMOUNT = 10
    """The specified positions or counts is invalid."""


class Lands(IntEnum):
    """An enum representing all land types. Matches the resource produced by the land."""

    FOREST = 0
    HILLS = 1
    FIELDS = 2
    PASTURE = 3
    MOUNTAINS = 4
    DESERT = 5


class Resources(IntEnum):
    """An enum representing all resource types. Matches the land which produces this resource."""

    LUMBER = 0
    BRICK = 1
    GRAIN = 2
    WOOL = 3
    ORE = 4


class Buildings(IntEnum):
    """An enum representing all building types."""

    SETTLEMENT = 0
    CITY = 1


class DevelopmentCards(IntEnum):
    """An enum representing all development card types."""

    KNIGHT = 0
    ROAD_BUILDING = 1
    YEAR_OF_PLENTY = 2
    MONOPOLY = 3
    VICTORY_POINT = 4


Position = Tuple[int, int]
"""A position on the board, as (x, y) coordinates."""


class Vector(list):
    def __init__(self, *args, **kwargs):
        list.__init__(self, *args, **kwargs)

    def __add__(self, other: "Vector"):
        return Vector([x + y for x, y in zip(self, other)])

    def __sub__(self, other: "Vector"):
        return Vector([x - y for x, y in zip(self, other)])

    def __iadd__(self, other: "Vector"):
        assert len(self) == len(other)
        for i in range(len(self)):
            self[i] += other[i]
        return self

    def __isub__(self, other: "Vector"):
        assert len(self) == len(other)
        for i in range(len(self)):
            self[i] -= other[i]
        return self

    def __le__(self, other: "Vector"):
        return all([x <= y for x, y in zip(self, other)])

    def __lt__(self, other: "Vector"):
        return all([x < y for x, y in zip(self, other)])

    def __ge__(self, other: "Vector"):
        return all([x >= y for x, y in zip(self, other)])

    def __gt__(self, other: "Vector"):
        return all([x > y for x, y in zip(self, other)])


class ResourceCounts(Vector):
    """The count of each resource, indexed by the `Resources` enum."""

    def __init__(self, lumber=0, brick=0, grain=0, wool=0, ore=0):
        Vector.__init__(self, [lumber, brick, grain, wool, ore])

    def __str__(self):
        return ", ".join(
            [
                f"{self[resource]} {Resources(resource).name.lower()}"
                for resource in Resources
                if self[resource] > 0
            ]
        )

    def __add__(self, other: "ResourceCounts"):
        assert len(self) == len(other)
        return ResourceCounts(*[x + y for x, y in zip(self, other)])

    def __sub__(self, other: "ResourceCounts"):
        assert len(self) == len(other)
        return ResourceCounts(*[x - y for x, y in zip(self, other)])


class DevelopmentCardCounts(Vector):
    """The count of each development card, indexed by the `DevelopmentCards` enum."""

    def __init__(
        self, knight=0, road_bulding=0, year_of_plenty=0, monopoly=0, victory_point=0
    ):
        Vector.__init__(
            self, [knight, road_bulding, year_of_plenty, monopoly, victory_point]
        )

    def __add__(self, other: "DevelopmentCardCounts"):
        assert len(self) == len(other)
        return DevelopmentCardCounts(*[x + y for x, y in zip(self, other)])

    def __sub__(self, other: "DevelopmentCardCounts"):
        assert len(self) == len(other)
        return DevelopmentCardCounts(*[x - y for x, y in zip(self, other)])


@dataclass
class Trade:
    """A data class for describing a trade offer."""

    give_counts: ResourceCounts
    """The resource counts the sender is willing to give"""
    receive_counts: ResourceCounts
    """The resource counts the sender is expecting to get back"""

    def reversed(self):
        return Trade(
            ResourceCounts(*self.receive_counts),
            ResourceCounts(*self.give_counts),
        )

    def copy(self):
        return Trade(
            ResourceCounts(*self.give_counts),
            ResourceCounts(*self.receive_counts),
        )


class API:
    """
    The main access point for your bot. Access this using `self.context` inside your `run` method.

    Each action method returns `Exceptions`, which is `Exceptions.OK` if it succeeded, or another value explaining why it failed.
    """

    ### SIMULATION UTILITIES ###

    def breakpoint(self) -> None:
        """
        Request the simulation to stop.
        It will be stopped after the current step is finished, so make sure you continue to run your bot as usual.
        """

        raise NotImplementedError()

    ### GENERAL ###

    def get_player_index(self) -> int:
        """Returns the player index of your bot."""

        raise NotImplementedError()

    ### BOARD GETTERS ###

    def get_terrains(self) -> list[Position]:
        """Returns a list of all terrain positions."""

        raise NotImplementedError()

    def get_intersections(self) -> list[Position]:
        """Returns a list of all intersection positions."""

        raise NotImplementedError()

    def get_edges(self) -> list[Tuple[Position, Position]]:
        """Returns a list of all edge positions (ends)."""

        raise NotImplementedError()

    def get_adjacent_terrains(self, position: Position) -> list[Position]:
        """Returns the adjacent positions of the terrains for a given intersection."""

        raise NotImplementedError()

    def get_adjacent_intersections(self, position: Position) -> list[Position]:
        """Returns the adjacent positions of the intersections for a given intersection or terrain position."""

        raise NotImplementedError()

    def get_adjacent_edges(self, position: Position) -> list[Tuple[Position, Position]]:
        """Returns the adjacent positions of the edges (ends) for a given intersection or terrain position."""

        raise NotImplementedError()

    def get_distance(self, x: Position, y: Position) -> int:
        """Returns the edge distance between the two provided intersection positions."""

        raise NotImplementedError()

    def get_land(self, position: Position) -> Optional[Lands]:
        """Returns the land type at the given position or None if the position is invalid."""

        raise NotImplementedError()

    def get_number(self, position: Position) -> Optional[int]:
        """Returns the number (from 2 to 12) at the given position or None if the position is invalid."""

        raise NotImplementedError()

    def get_current_building(
        self, position: Position
    ) -> Optional[Tuple[Buildings, int]]:
        """Returns the current building and player index at the given position, or None if there isn't any."""

        raise NotImplementedError()

    def get_current_road(self, ends: Tuple[Position, Position]) -> Optional[int]:
        """
        Returns the player index of the road between the given positions or None if there isn't any.

        **Note:** the order of the `ends` doesn't matter.
        """

        raise NotImplementedError()

    def get_current_robber_position(self) -> Position:
        """Returns the current position of the robber."""

        raise NotImplementedError()

    def get_harbor_positions(
        self,
    ) -> list[Tuple[Tuple[Position, Position], Optional[Resources]]]:
        """
        Returns a list of the harbor edge positions and their resource, or None if a 3-to-1 harbor.
        Example:
        ```
        [
            (
                ((-8, -2), (-8, 2)),
                Resources.ORE
            ),
            ...
        ]
        ```
        """

        raise NotImplementedError()

    def get_player_buildings(
        self, player_index: int
    ) -> list[Tuple[Position, Buildings]]:
        """Returns the buildings the specified player owns and their positions."""

        raise NotImplementedError()

    def get_player_roads(self, player_index: int) -> list[Tuple[Position, Position]]:
        """Returns the roads the specified player owns and their positions."""

        raise NotImplementedError()

    ### RESOURCE GETTERS ###

    def get_resource_counts(self) -> ResourceCounts:
        """Returns the resources your bot owns, indexed by the `Resources` enum."""

        raise NotImplementedError()

    def get_development_cards(self) -> DevelopmentCardCounts:
        """Returns the development cards your bot owns, indexed by the `DevelopmentCards` enum."""

        raise NotImplementedError()

    def get_playable_development_cards(self) -> DevelopmentCardCounts:
        """Returns the development cards your bot can play this turn (if haven't played a card this turn yet!), indexed by the `DevelopmentCards` enum."""

        raise NotImplementedError()

    def get_total_resource_count(self, player_index: int) -> int:
        """Returns the total resource count the given player owns. You do not have access to the exact resource counts through this API."""

        raise NotImplementedError()

    def get_total_development_card_count(self, player_index: int) -> int:
        """Returns the total number of development cards the given player owns."""

        raise NotImplementedError()

    ### ADDITIONAL GAME INFORMATION GETTERS ###

    def get_victory_points(self, player_index: int) -> int:
        """
        Returns the visible victory points of the given player.
        Does not include information about the player's victory point development cards, if there are any.
        """

        raise NotImplementedError()

    def get_road_length(self, player_index: int) -> int:
        """Returns the longest road length of the given player."""

        raise NotImplementedError()

    def get_army_size(self, player_index: int) -> int:
        """Returns the army size of the given player (i.e. the amount of knight cards they have played)."""

        raise NotImplementedError()

    def get_longest_road_player_index(self) -> Optional[int]:
        """Returns the index of the player which has the longest road, or None if no player has a road of length at least 5."""

        raise NotImplementedError()

    def get_largest_army_player_index(self) -> Optional[int]:
        """Returns the index of the player which has the largest army, or None if no player has played at least 3 knights."""

        raise NotImplementedError()

    ### TURN GETTERS ###

    def get_current_roll(self) -> int:
        """Returns the current value of the dice."""

        raise NotImplementedError()

    ### OFFER GETTERS ###

    def get_pending_trade_offers(self) -> list[Trade]:
        """Returns the current pending trade offers to be answered with `accept_trade_offer` or with a counter offer using `propose_trade_offer`."""

        raise NotImplementedError()

    ### ACTIONS ###

    def play_knight(self) -> Exceptions:
        """
        Play a `DevelopmentCards.KNIGHT` card you own.

        After running this action your `move_robber` method will be called.

        Possible exceptions: `Exceptions.NOT_ENOUGH_RESOURCES`, `Exceptions.ALREADY_PLAYED_DEVELOPMENT_CARD`, `Exceptions.BAD_TIMING`.
        """

        raise NotImplementedError()

    def play_road_building(
        self, road_positions: List[Tuple[Position, Position]]
    ) -> Exceptions:
        """
        Play a `DevelopmentCards.ROAD_BUILDING` card you own to build up to 2 roads anywhere.

        Possible exceptions: `Exceptions.ALREADY_PLAYED_DEVELOPMENT_CARD`, `Exceptions.NOT_ENOUGH_RESOURCES`, `Exceptions.BAD_AMOUNT`, `Exceptions.OUT_OF_ITEMS`, `Exceptions.ILLEGAL_POSITION`, `Exceptions.BAD_TIMING`.
        """

        raise NotImplementedError()

    def play_year_of_plenty(self, resources: ResourceCounts) -> Exceptions:
        """
        Play a `DevelopmentCards.YEAR_OF_PLENTY` card you own to receive 2 resources of any kind.

        Possible exceptions: `Exceptions.NOT_ENOUGH_RESOURCES`, `Exceptions.ALREADY_PLAYED_DEVELOPMENT_CARD`, `Exceptions.BAD_AMOUNT`, `Exceptions.BAD_TIMING`.
        """

        raise NotImplementedError()

    def play_monopoly(self, resource: Resources) -> Exceptions:
        """
        Play a `DevelopmentCards.MONOPOLY` card you own to steal all of the other players' resource of the specified kind.

        Possible exceptions: `Exceptions.NOT_A_RESOURCE`, `Exceptions.NOT_ENOUGH_RESOURCES`, `Exceptions.ALREADY_PLAYED_DEVELOPMENT_CARD`, `Exceptions.BAD_TIMING`.
        """

        raise NotImplementedError()

    def build_road(self, ends: Tuple[Position, Position]) -> Exceptions:
        """
        Build a road between the given ends.

        **Note:** the order of the `ends` doesn't matter.

        Possible exceptions: `Exceptions.OUT_OF_ITEMS`, `Exceptions.NOT_ENOUGH_RESOURCES`, `Exceptions.ILLEGAL_POSITION`, `Exceptions.BAD_TIMING`.
        """

        raise NotImplementedError()

    def build_settlement(self, position: Position) -> Exceptions:
        """
        Build a settlement at the given position.

        Possible exceptions: `Exceptions.OUT_OF_ITEMS`, `Exceptions.NOT_ENOUGH_RESOURCES`, `Exceptions.ILLEGAL_POSITION`, `Exceptions.BAD_TIMING`.
        """

        raise NotImplementedError()

    def build_city(self, position: Position) -> Exceptions:
        """
        Build a city at the given position.

        Possible exceptions: `Exceptions.OUT_OF_ITEMS`, `Exceptions.NOT_ENOUGH_RESOURCES`, `Exceptions.ILLEGAL_POSITION`, `Exceptions.BAD_TIMING`.
        """

        raise NotImplementedError()

    def buy_development_card(self) -> Exceptions:
        """
        Buy a development card.  it will be added to your cards at the end of the turn.

        Possible exceptions: `Exceptions.OUT_OF_ITEMS`, `Exceptions.NOT_ENOUGH_RESOURCES`, `Exceptions.BAD_TIMING`.
        """

        raise NotImplementedError()

    def maritime_trade(self, sell: Resources, receive: Resources) -> Exceptions:
        """
        Trade with the bank. You will pay either 4, 3 or 2 according to the harbors you possess.

        Possible exceptions: `Exceptions.NOT_ENOUGH_RESOURCES`, `Exceptions.BAD_TIMING`.
        """

        raise NotImplementedError()

    def propose_trade_offer(self, trade: Trade) -> Exceptions:
        """
        Propose the given offer.
        If it's your turn, it will be proposed to every other player.
        If it's not your turn, use this method for counter-offers and it will only be proposed to the original player.

        You're limited to 5 trade offers per turn.

        Possible exceptions: `Exceptions.NOT_ENOUGH_RESOURCES`, `Exceptions.TOO_MANY_TRADES`, `Exceptions.BAD_TIMING`.
        """

        raise NotImplementedError()

    def accept_trade_offer(self, trade_offer_index: int) -> Exceptions:
        """
        Accept the trade offer in get_pending_trade_offers at the given index. If not called, the trade offers will be rejected.

        Possible exceptions: `Exceptions.ILLEGAL_OFFER_INDEX`, `Exceptions.NOT_ENOUGH_RESOURCES`, `Exceptions.BAD_TIMING`.
        """

        raise NotImplementedError()

    def move_robber(self, position: Position, player_index: int) -> Exceptions:
        """
        Choose a new position for the robber which must not be the current position after playing a knight card or if a 7 is rolled on your turn.

        Additionally, you may choose one of the **adjacent** players to rob one resource from, give index -1 if the terrain is not adjecent to any player's settelment.

        Possible exceptions: `Exceptions.ILLEGAL_PLAYER_INDEX`, `Exceptions.ILLEGAL_POSITION`, `Exceptions.BAD_TIMING`.
        """
        raise NotImplementedError()

    def set_resources_to_drop(self, resource_counts: ResourceCounts) -> Exceptions:
        """
        Select resources to drop if a 7 is rolled and you have more than 7 cards.

        Possible exceptions: `Exceptions.NOT_ENOUGH_RESOURCES`, `Exceptions.BAD_TIMING`.
        """

        raise NotImplementedError()


class CatanBot:
    """
    Base class for writing your bots.

    **Important:** Your bot must subclass this directly, and be called MyBot!

    **Important:** Your bot must not have a custom __init__ method. Use `setup` for any setup code you may have.

    **Example:**

    ```python
    class MyBot(CatanBot):
        def setup(self):
            self.message = "Hello!"

        def play(self):
            print(self.context)
    ```
    """

    context: API

    def __init__(self, context: API):
        """Don't override this method!"""

        self.context = context
        self.setup()

    def setup(self) -> None:
        """
        This optional method will be called upon construction.

        If you need to define any instance variables like in a constructor, do it here.
        """

    def place_settlement_and_road(self) -> None:
        """
        This method will be called twice at the beginning of the game.

        Use `self.context.build_settlement` and then `self.context.build_road` to mark your positions.
        If you don't, the first legal positions will be selected.

        **Note:** make sure the road is adjacent to the settlement.
        """

    def play(self) -> None:
        """
        This method will be called when it's your turn.

        After running any specific action you MUST return from this method.
        It will be called again after the action is performed.

        When you don't set any action, your turn will end.

        You may use `self.context.play_card`, `self.context.build_road`, `self.context.build_settlement`, `self.context.build_city`, `self.context.buy_development_card`, `self.context.maritime_trade`, `self.context.propose_trade_offer`, `self.context.accept_trade_offer`.

        **Note:** If you call `self.context.propose_trade_offer`, after the other players respond your `play` method will be called again (not `respond_to_trade_offer`).
        """

    def respond_to_trade_offers(self) -> None:
        """
        This method will be called when offers from other players are available.
        This can be called when it's your turn and you get counter-offers, or when it's someone else's turn and they offer a trade.

        Use `self.context.accept_trade_offer` and `self.context.propose_trade_offer` to choose your answer, or don't do anything to reject all trades.
        You may only respond to a single trade offer and only accept it or propose a counter-offer.

        **Note:** You may not propose a trade offer in this method when it's your turn (to prevent infinite trade loops!)
        """

    def move_robber(self) -> None:
        """
        This method will be called when a 7 is rolled on your turn and when you play the knight card.

        Use `self.context.rob_player` to choose your desired position and player to rob.

        If you don't do anything, the robber's position will be set to the desert and you won't steal anyone's resources.
        """

    def drop_resources(self) -> None:
        """
        This method will be called when a 7 is rolled and you have more than 7 cards.
        You must select half of your cards (rounded down) to drop.

        Use `self.context.set_resources_to_drop`.
        If you don't select resources, the first half sorted according to the order in `Resources` will be dropped.
        """

    def before_dice(self) -> None:
        """
        This method will be called once before the dice is rolled on someone's turn (including yours).

        You may use `self.context.play_card`.
        """

    def after_turn(self) -> None:
        """
        This method will be called once after someone's turn (including yours).

        You may not run any actions here.
        """
