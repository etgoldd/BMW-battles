from api import *
import random
import math


class PRICES:
    ROAD = ResourceCounts(lumber=1, brick=1)
    SETTLEMENT = ResourceCounts(lumber=1, brick=1, grain=1, wool=1)
    CITY = ResourceCounts(grain=2, ore=3)
    DEVELOPMENT_CARD = ResourceCounts(grain=1, wool=1, ore=1)

class MyBot(CatanBot):
    def rank_land(self, position, curr_land_worth):
        land = self.context.get_land(position)
        if land is None:
            return 0
        land_num = self.context.get_number(position)
        if land_num is None:
            return 0

        score = self.land_num_to_score[land_num]
        res = self.land_worth_mult[land.value] * curr_land_worth[land.value] * score
        curr_land_worth[land.value] -= score
        return res

    def update_land_worth_after_buy(self, intersection_position):
        # Calling rank_land with self.land_worth on each land updates it directly.
        terrains = self.context.get_adjacent_terrains(intersection_position)
        for land_pos in terrains:
            self.rank_land(land_pos, self.land_worth)

    def rank_intersection(self, position):
        terrains = self.context.get_adjacent_terrains(position)
        temp_land_worth = self.land_worth[::]
        res = sum(self.rank_land(land_pos, temp_land_worth) for land_pos in terrains)
        return res

    def setup(self):
        self.current_stage = 1
        self.city_amounts = 0

        # [LUMBER, BRICK, GRAIN, WOOL, ORE, DESERT]
        self.land_worth = [36, 36, 36, 36, 36, 0]
        self.land_worth_mult = [1, 1, 1, 0.99, 1, 1]  # slightly less want wool

        self.land_num_to_score = {2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 8: 5, 9: 4, 10: 3, 11: 2, 12: 1}
        self.min_count_to_trade = 6
        self.development_card_chance = 3

    def play(self):
        has_settlement_location = len(self.valid_settlement_locations_now()) != 0
        self.context.log_info(f"has_settlement_location: {has_settlement_location}")
        self.cards = self.context.get_resource_counts()
        if self.build_city():
            return
        elif self.build_settlement():
            return
        elif self.build_road(PRICES.SETTLEMENT if has_settlement_location else None):
            return
        elif self.trade_with_bank():
            return
        elif self.try_build_development_cards(PRICES.SETTLEMENT if has_settlement_location else None):
            return
        return

    def try_build_development_cards(self, save_cards=None):
        my_cards = self.cards
        if save_cards is not None:
            my_cards -= save_cards
        if not (my_cards >= PRICES.DEVELOPMENT_CARD):
            return False
        if random.randint(0, self.development_card_chance):
            if self.context.buy_development_card() == Exceptions.OK:
                return True
        return False

    def before_dice(self):
        dev_cards:  DevelopmentCardCounts = self.context.get_development_cards()
        if dev_cards[DevelopmentCards.YEAR_OF_PLENTY] > 0:
            requested_counts: ResourceCounts = ResourceCounts()
            requested_counts[self.most_needed_resource()] = 2  # Request all.
            self.context.play_year_of_plenty(requested_counts)
        elif dev_cards[DevelopmentCards.MONOPOLY] > 0:
            self.context.play_monopoly(self.most_needed_resource())
        elif dev_cards[DevelopmentCards.ROAD_BUILDING] > 0:
            roads_near_roads = self.get_roads_next_to_road()
            # Try to play 2 roads
            if len(roads_near_roads) >= 2:
                self.context.play_road_building(roads_near_roads[:1])  # TODO: fix
        elif dev_cards[DevelopmentCards.KNIGHT] > 0:
            self.context.play_knight()

    def build_city(self, save_cards=None):
        my_cards = self.cards
        if save_cards is not None:
            my_cards -= save_cards
        if not (my_cards >= PRICES.CITY):
            return False
        buildings = self.context.get_player_buildings(self.context.get_player_index())
        for pos, building in buildings:
            if building == Buildings.SETTLEMENT:
                e = self.context.build_city(pos)
                if e == Exceptions.OK:
                    self.city_amounts += 1
                    self.update_land_worth_after_buy(pos)
                    return True
                else:
                    return False
        return False
    
    def valid_settlement_locations_now(self):
        roads = self.context.get_player_roads(self.context.get_player_index())
        valid_locations=[]
        for intersection in self.context.get_intersections():
            if self.context.get_current_building(intersection):
                continue
            edges = self.context.get_adjacent_edges(intersection)
            if not (set(roads) & set(edges)):
                continue
            adj_intersections = self.context.get_adjacent_intersections(intersection)
            for adj in adj_intersections:
                if self.context.get_current_building(adj):
                    break
            else:
                valid_locations.append(intersection)
        return valid_locations

    def build_settlement(self, save_cards=None):
        my_cards = self.cards
        if save_cards is not None:
            my_cards -= save_cards
        if not (my_cards >= PRICES.SETTLEMENT):
            return False
        intersections= self.context.get_intersections()
        random.shuffle(intersections)
        for intersection in intersections:
            e = self.context.build_settlement(intersection)
            if e == Exceptions.OK:
                self.context.log_info("built settlement")
                self.update_land_worth_after_buy(intersection)
                return True
            elif e == Exceptions.NOT_ENOUGH_RESOURCES:
                return False
            elif e == Exceptions.ILLEGAL_POSITION:
                pass
        return False

    def build_road(self, save_cards=None):
        my_cards = self.cards
        if save_cards is not None:
            my_cards -= save_cards
        if not (my_cards >= PRICES.ROAD):
            return False
        edges= self.context.get_edges()
        random.shuffle(edges)
        for edge in edges:
            e = self.context.build_road(edge)
            if e == Exceptions.OK:
                return True
            elif e == Exceptions.NOT_ENOUGH_RESOURCES:
                return False
            elif e == Exceptions.ILLEGAL_POSITION:
                pass
        return

    def most_needed_resource(self):
        res_counts = self.context.get_resource_counts()
        return Resources(res_counts.index(min(res_counts)))

    def trade_with_bank(self):
        res_counts = self.context.get_resource_counts()
        min_resource = self.most_needed_resource()
        for i, count in enumerate(res_counts):
            if count >= self.min_count_to_trade:
                self.context.log_info(f"trading {i} with {min_resource}")
                self.context.maritime_trade(i, Resources(min_resource))
                return True
        return False

    def place_settlement_and_road(self):
        best_position: Position | None = None
        best_rank = 0
        for position in self.context.get_intersections():
            if self.context.get_current_building(position):
                continue
            rank = self.rank_intersection(position)
            if rank > best_rank:
                best_position = position
                best_rank = rank
        if best_position:
            self.context.build_settlement(best_position)
            #  Update worth of resources because the ones we bought are less needed.
            self.update_land_worth_after_buy(best_position)
            self.context.build_road(self.context.get_adjacent_edges(best_position)[0])

    def drop_resources(self):
        """
        Drops half of all resources
        """
        resources = self.context.get_resource_counts()
        total = sum(resources)
        target_drop = math.floor(total / 2)
        if total < 7:
            return
        dropped_resources = ResourceCounts(0, 0, 0, 0, 0)
        for res_index, res_count in enumerate(resources):
            dropped_resources[res_index] = math.floor(res_count / 2)

        diff = target_drop - sum(dropped_resources)
        while diff > 0:
            dropped_index = random.randrange(0, 5)
            if resources[dropped_index] - dropped_resources[dropped_index] > 0:
                dropped_resources[res_index] += 1
                diff -= 1
        if self.context.set_resources_to_drop(dropped_resources) == Exceptions.NOT_ENOUGH_RESOURCES:
            self.context.log_info("Not enough resources to drop")
            return

    def get_player_terrains(self, player_index: int) -> set[Position]:
        buildings = self.context.get_player_buildings(player_index)
        my_terrains = set()
        for building in buildings:
            building: tuple[Position, Buildings]
            my_terrains = my_terrains.union(self.context.get_adjacent_terrains(building[0]))
        return my_terrains


    def get_other_player_indexes(self) -> list[int]:
        """
        Returns a list of the player indexes that aren't ours
        """
        indexes = []
        for player_index in range(4):
            if player_index == self.context.get_player_index():
                continue
            if len(self.context.get_player_buildings(player_index)) == 0:
                indexes.append(player_index)
        return indexes

    def move_robber(self):
        """
        Generates the set of terrains that we aren't on and the enemy is on
        """
        my_terrains = self.get_player_terrains(self.context.get_player_index())
        target_terrains = set(self.context.get_terrains()).difference(my_terrains)
        target_terrains.remove((0,0))
        self.context.log_info(f"target terrains: {target_terrains}")
        best_score = 0
        best_target = None
        for target_terrain in target_terrains:
            if self.context.get_number(target_terrain) is not None and self.land_num_to_score.get(self.context.get_number(target_terrain)) > best_score:
                best_score = self.land_num_to_score.get(self.context.get_number(target_terrain))
                best_target = target_terrain
        for i in range(-1, 4):
            if self.context.move_robber(best_target, i) != Exceptions.ILLEGAL_PLAYER_INDEX:
                return
            
            