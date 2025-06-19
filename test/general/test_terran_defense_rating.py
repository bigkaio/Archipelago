import pytest
from unittest.mock import Mock

from worlds.sc2.Rules import SC2Logic
from worlds.sc2.Items import ItemNames, defense_ratings, zerg_defense_ratings, air_defense_ratings
from worlds.sc2.Options import RequiredTactics


class MockCollectionState:
    def __init__(self, parent_world, items=None):
        self.parent_world = parent_world
        self.has_items = items if items is not None else set()

    def has(self, item_name, player):
        return item_name in self.has_items

    def has_any(self, item_names, player):
        return any(item_name in self.has_items for item_name in item_names)

    def has_all(self, item_names, player):
        return all(item_name in self.has_items for item_name in item_names)


class TestTerranDefenseRating:
    @pytest.fixture
    def sc2_logic(self):
        mock_world = Mock()
        mock_world.player = 1  # Adicionado para simular self.player
        mock_world.options.required_tactics.value = RequiredTactics.option_standard
        logic = SC2Logic(mock_world)
        logic.advanced_tactics = False
        return logic

    @pytest.fixture(autouse=True)
    def setup(self, sc2_logic):
        self.sc2_logic = sc2_logic

    def test_initial_defense_score(self):
        state = MockCollectionState(parent_world=self.sc2_logic.world, items={})
        initial_score = self.sc2_logic.terran_defense_rating(state, False, False)
        assert initial_score == 0

    # Testes para a decisão 1: Manned Bunker
    # if state.has_any({ItemNames.MARINE, ItemNames.MARAUDER}, self.player) and state.has(ItemNames.BUNKER, self.player):
    #     defense_score += 3
    def test_d1_ct1_1(self):
        # CT_D1_1 (V): C1.1 (true) e C1.2 (true). Marine e Bunker.
        state = MockCollectionState(parent_world=self.sc2_logic.world, items={ItemNames.MARINE, ItemNames.BUNKER})
        initial_score = self.sc2_logic.terran_defense_rating(state, False, False)
        expected_score = defense_ratings.get(ItemNames.MARINE, 0) + defense_ratings.get(ItemNames.BUNKER, 0) + 3
        assert initial_score == expected_score

    def test_d1_ct1_2(self):
        # CT_D1_2 (F): C1.1 (false) e C1.2 (true). Sem Marine/Marauder, mas com Bunker.
        state = MockCollectionState(parent_world=self.sc2_logic.world, items={ItemNames.BUNKER})
        initial_score = self.sc2_logic.terran_defense_rating(state, False, False)
        expected_score = defense_ratings.get(ItemNames.BUNKER, 0)
        assert initial_score == expected_score

    def test_d1_ct1_3(self):
        # CT_D1_3 (F): C1.1 (true) e C1.2 (false). Com Marine, mas sem Bunker.
        state = MockCollectionState(parent_world=self.sc2_logic.world, items={ItemNames.MARINE})
        initial_score = self.sc2_logic.terran_defense_rating(state, False, False)
        expected_score = defense_ratings.get(ItemNames.MARINE, 0)
        assert initial_score == expected_score

    # Testes para a decisão 2: Zerg Enemy Manned Bunker
    # elif zerg_enemy and state.has(ItemNames.FIREBAT, self.player) and state.has(ItemNames.BUNKER, self.player):
    #     defense_score += 2
    def test_d2_ct2_1(self):
        # CT_D2_1 (V): C2.1 (true), C2.2 (true) e C2.3 (true). Zerg Enemy, Firebat e Bunker.
        state = MockCollectionState(parent_world=self.sc2_logic.world, items={ItemNames.FIREBAT, ItemNames.BUNKER})
        initial_score = self.sc2_logic.terran_defense_rating(state, True, False)
        expected_score = defense_ratings.get(ItemNames.FIREBAT, 0) + defense_ratings.get(ItemNames.BUNKER, 0) + zerg_defense_ratings.get(ItemNames.FIREBAT, 0) + 2
        assert initial_score == expected_score

    def test_d2_ct2_2(self):
        # CT_D2_2 (F): C2.1 (false), C2.2 (true) e C2.3 (true). Sem Zerg Enemy, com Firebat e Bunker.
        state = MockCollectionState(parent_world=self.sc2_logic.world, items={ItemNames.FIREBAT, ItemNames.BUNKER})
        initial_score = self.sc2_logic.terran_defense_rating(state, False, False)
        expected_score = defense_ratings.get(ItemNames.FIREBAT, 0) + defense_ratings.get(ItemNames.BUNKER, 0)
        assert initial_score == expected_score

    def test_d2_ct2_3(self):
        # CT_D2_3 (F): C2.1 (true), C2.2 (false) e C2.3 (true). Zerg Enemy, sem Firebat, com Bunker.
        state = MockCollectionState(parent_world=self.sc2_logic.world, items={ItemNames.BUNKER})
        initial_score = self.sc2_logic.terran_defense_rating(state, True, False)
        expected_score = defense_ratings.get(ItemNames.BUNKER, 0) + zerg_defense_ratings.get(ItemNames.BUNKER, 0)
        assert initial_score == expected_score

    def test_d2_ct2_4(self):
        # CT_D2_4 (F): C2.1 (true), C2.2 (true) e C2.3 (false). Zerg Enemy, com Firebat, sem Bunker.
        state = MockCollectionState(parent_world=self.sc2_logic.world, items={ItemNames.FIREBAT})
        initial_score = self.sc2_logic.terran_defense_rating(state, True, False)
        expected_score = defense_ratings.get(ItemNames.FIREBAT, 0) + zerg_defense_ratings.get(ItemNames.FIREBAT, 0)
        assert initial_score == expected_score

    # Testes para a decisão 3: Siege Tank Maelstrom Rounds
    # if state.has_all({ItemNames.SIEGE_TANK, ItemNames.SIEGE_TANK_MAELSTROM_ROUNDS}, self.player):
    #     defense_score += 2
    def test_d3_ct3_1(self):
        # CT_D3_1 (V): C3.1 (true) e C3.2 (true). Siege Tank e Maelstrom Rounds.
        state = MockCollectionState(parent_world=self.sc2_logic.world, items={ItemNames.SIEGE_TANK, ItemNames.SIEGE_TANK_MAELSTROM_ROUNDS})
        initial_score = self.sc2_logic.terran_defense_rating(state, False, False)
        expected_score = defense_ratings.get(ItemNames.SIEGE_TANK, 0) + defense_ratings.get(ItemNames.SIEGE_TANK_MAELSTROM_ROUNDS, 0) + 2
        assert initial_score == expected_score

    def test_d3_ct3_2(self):
        # CT_D3_2 (F): C3.1 (false) e C3.2 (true). Sem Siege Tank, com Maelstrom Rounds.
        state = MockCollectionState(parent_world=self.sc2_logic.world, items={ItemNames.SIEGE_TANK_MAELSTROM_ROUNDS})
        initial_score = self.sc2_logic.terran_defense_rating(state, False, False)
        expected_score = defense_ratings.get(ItemNames.SIEGE_TANK_MAELSTROM_ROUNDS, 0)
        assert initial_score == expected_score

    def test_d3_ct3_3(self):
        # CT_D3_3 (F): C3.1 (true) e C3.2 (false). Com Siege Tank, sem Maelstrom Rounds.
        state = MockCollectionState(parent_world=self.sc2_logic.world, items={ItemNames.SIEGE_TANK})
        initial_score = self.sc2_logic.terran_defense_rating(state, False, False)
        expected_score = defense_ratings.get(ItemNames.SIEGE_TANK, 0)
        assert initial_score == expected_score

    # Testes para a decisão 4: Siege Tank Graduating Range
    # if state.has_all({ItemNames.SIEGE_TANK, ItemNames.SIEGE_TANK_GRADUATING_RANGE}, self.player):
    #     defense_score += 1
    def test_d4_ct4_1(self):
        # CT_D4_1 (V): C4.1 (true) e C4.2 (true). Siege Tank e Graduating Range.
        state = MockCollectionState(parent_world=self.sc2_logic.world, items={ItemNames.SIEGE_TANK, ItemNames.SIEGE_TANK_GRADUATING_RANGE})
        initial_score = self.sc2_logic.terran_defense_rating(state, False, False)
        expected_score = defense_ratings.get(ItemNames.SIEGE_TANK, 0) + defense_ratings.get(ItemNames.SIEGE_TANK_GRADUATING_RANGE, 0) + 1
        assert initial_score == expected_score

    def test_d4_ct4_2(self):
        # CT_D4_2 (F): C4.1 (false) e C4.2 (true). Sem Siege Tank, com Graduating Range.
        state = MockCollectionState(parent_world=self.sc2_logic.world, items={ItemNames.SIEGE_TANK_GRADUATING_RANGE})
        initial_score = self.sc2_logic.terran_defense_rating(state, False, False)
        expected_score = defense_ratings.get(ItemNames.SIEGE_TANK_GRADUATING_RANGE, 0)
        assert initial_score == expected_score

    def test_d4_ct4_3(self):
        # CT_D4_3 (F): C4.1 (true) e C4.2 (false). Com Siege Tank, sem Graduating Range.
        state = MockCollectionState(parent_world=self.sc2_logic.world, items={ItemNames.SIEGE_TANK})
        initial_score = self.sc2_logic.terran_defense_rating(state, False, False)
        expected_score = defense_ratings.get(ItemNames.SIEGE_TANK, 0)
        assert initial_score == expected_score

    # Testes para a decisão 5: Widow Mine Concealment
    # if state.has_all({ItemNames.WIDOW_MINE, ItemNames.WIDOW_MINE_CONCEALMENT}, self.player):
    #     defense_score += 1
    def test_d5_ct5_1(self):
        # CT_D5_1 (V): C5.1 (true) e C5.2 (true). Widow Mine e Concealment.
        state = MockCollectionState(parent_world=self.sc2_logic.world, items={ItemNames.WIDOW_MINE, ItemNames.WIDOW_MINE_CONCEALMENT})
        initial_score = self.sc2_logic.terran_defense_rating(state, False, False)
        expected_score = defense_ratings.get(ItemNames.WIDOW_MINE, 0) + defense_ratings.get(ItemNames.WIDOW_MINE_CONCEALMENT, 0) + 1
        assert initial_score == expected_score

    def test_d5_ct5_2(self):
        # CT_D5_2 (F): C5.1 (false) e C5.2 (true). Sem Widow Mine, com Concealment.
        state = MockCollectionState(parent_world=self.sc2_logic.world, items={ItemNames.WIDOW_MINE_CONCEALMENT})
        initial_score = self.sc2_logic.terran_defense_rating(state, False, False)
        expected_score = defense_ratings.get(ItemNames.WIDOW_MINE_CONCEALMENT, 0)
        assert initial_score == expected_score

    def test_d5_ct5_3(self):
        # CT_D5_3 (F): C5.1 (true) e C5.2 (false). Com Widow Mine, sem Concealment.
        state = MockCollectionState(parent_world=self.sc2_logic.world, items={ItemNames.WIDOW_MINE})
        initial_score = self.sc2_logic.terran_defense_rating(state, False, False)
        expected_score = defense_ratings.get(ItemNames.WIDOW_MINE, 0)
        assert initial_score == expected_score

    # Testes para a decisão 6: Viking Shredder Rounds
    # if state.has_all({ItemNames.VIKING, ItemNames.VIKING_SHREDDER_ROUNDS}, self.player):
    #     defense_score += 2
    def test_d6_ct6_1(self):
        # CT_D6_1 (V): C6.1 (true) e C6.2 (true). Viking e Shredder Rounds.
        state = MockCollectionState(parent_world=self.sc2_logic.world, items={ItemNames.VIKING, ItemNames.VIKING_SHREDDER_ROUNDS})
        initial_score = self.sc2_logic.terran_defense_rating(state, False, False)
        expected_score = defense_ratings.get(ItemNames.VIKING, 0) + defense_ratings.get(ItemNames.VIKING_SHREDDER_ROUNDS, 0) + 2
        assert initial_score == expected_score

    def test_d6_ct6_2(self):
        # CT_D6_2 (F): C6.1 (false) e C6.2 (true). Sem Viking, com Shredder Rounds.
        state = MockCollectionState(parent_world=self.sc2_logic.world, items={ItemNames.VIKING_SHREDDER_ROUNDS})
        initial_score = self.sc2_logic.terran_defense_rating(state, False, False)
        expected_score = defense_ratings.get(ItemNames.VIKING_SHREDDER_ROUNDS, 0)
        assert initial_score == expected_score

    def test_d6_ct6_3(self):
        # CT_D6_3 (F): C6.1 (true) e C6.2 (false). Com Viking, sem Shredder Rounds.
        state = MockCollectionState(parent_world=self.sc2_logic.world, items={ItemNames.VIKING})
        initial_score = self.sc2_logic.terran_defense_rating(state, False, False)
        expected_score = defense_ratings.get(ItemNames.VIKING, 0)
        assert initial_score == expected_score

    # Testes para a decisão 7: Zerg Enemy
    # if zerg_enemy:
    #     defense_score += sum((zerg_defense_ratings[item] for item in zerg_defense_ratings if state.has(item, self.player)))
    def test_d7_ct7_1(self):
        # CT_D7_1 (V): C7.1 (true). Zerg Enemy.
        # Usando ItemNames.FIREBAT que está presente em zerg_defense_ratings
        state = MockCollectionState(parent_world=self.sc2_logic.world, items={ItemNames.FIREBAT})
        initial_score = self.sc2_logic.terran_defense_rating(state, True, False)
        expected_score = defense_ratings.get(ItemNames.FIREBAT, 0) + zerg_defense_ratings.get(ItemNames.FIREBAT, 0)
        assert initial_score == expected_score

    def test_d7_ct7_2(self):
        # CT_D7_2 (F): C7.1 (false). Sem Zerg Enemy.
        state = MockCollectionState(parent_world=self.sc2_logic.world, items={ItemNames.FIREBAT})
        initial_score = self.sc2_logic.terran_defense_rating(state, False, False)
        expected_score = defense_ratings.get(ItemNames.FIREBAT, 0)
        assert initial_score == expected_score

    # Testes para a decisão 8: Air Enemy
    # if air_enemy:
    #     defense_score += sum((air_defense_ratings[item] for item in air_defense_ratings if state.has(item, self.player)))
    def test_d8_ct8_1(self):
        # CT_D8_1 (V): C8.1 (true). Air Enemy.
        # Usando ItemNames.VIKING que está presente em air_defense_ratings
        state = MockCollectionState(parent_world=self.sc2_logic.world, items={ItemNames.VIKING})
        initial_score = self.sc2_logic.terran_defense_rating(state, False, True)
        expected_score = defense_ratings.get(ItemNames.VIKING, 0) + air_defense_ratings.get(ItemNames.VIKING, 0)
        assert initial_score == expected_score

    def test_d8_ct8_2(self):
        # CT_D8_2 (F): C8.1 (false). Sem Air Enemy.
        state = MockCollectionState(parent_world=self.sc2_logic.world, items={ItemNames.VIKING})
        initial_score = self.sc2_logic.terran_defense_rating(state, False, False)
        expected_score = defense_ratings.get(ItemNames.VIKING, 0)
        assert initial_score == expected_score

    def test_d9_ct9_1(self):
        # CT_D9_1 (V): C9.1 (true), C9.2 (true) e C9.3 (true). Air Enemy, Zerg Enemy e Valkyrie.
        state = MockCollectionState(parent_world=self.sc2_logic.world, items={ItemNames.VALKYRIE})
        initial_score = self.sc2_logic.terran_defense_rating(state, True, True)
        # A Valkyrie contribui para air_defense_ratings e zerg_defense_ratings
        expected_score = defense_ratings.get(ItemNames.VALKYRIE, 0) + 2 + air_defense_ratings.get(ItemNames.VALKYRIE, 0) + zerg_defense_ratings.get(ItemNames.VALKYRIE, 0)
        assert initial_score == expected_score

    def test_d9_ct9_2(self):
        # CT_D9_2 (F): C9.1 (false), C9.2 (true) e C9.3 (true). Sem Air Enemy, com Zerg Enemy e Valkyrie.
        state = MockCollectionState(parent_world=self.sc2_logic.world, items={ItemNames.VALKYRIE})
        initial_score = self.sc2_logic.terran_defense_rating(state, True, False)
        expected_score = defense_ratings.get(ItemNames.VALKYRIE, 0) + zerg_defense_ratings.get(ItemNames.VALKYRIE, 0)
        assert initial_score == expected_score

    def test_d9_ct9_3(self):
        # CT_D9_3 (F): C9.1 (true), C9.2 (false) e C9.3 (true). Com Air Enemy, sem Zerg Enemy, com Valkyrie.
        state = MockCollectionState(parent_world=self.sc2_logic.world, items={ItemNames.VALKYRIE})
        initial_score = self.sc2_logic.terran_defense_rating(state, False, True)
        expected_score = defense_ratings.get(ItemNames.VALKYRIE, 0) + air_defense_ratings.get(ItemNames.VALKYRIE, 0)
        assert initial_score == expected_score

    def test_d9_ct9_4(self):
        # CT_D9_4 (F): C9.1 (true), C9.2 (true) e C9.3 (false). Com Air Enemy, com Zerg Enemy, sem Valkyrie.
        state = MockCollectionState(parent_world=self.sc2_logic.world, items={})
        initial_score = self.sc2_logic.terran_defense_rating(state, True, True)
        assert initial_score == 0

    # Testes para a decisão 10: Advanced Tactics
    # if self.advanced_tactics:
    #     defense_score += 2
    def test_d10_ct10_1(self):
        # CT_D10_1 (V): C10.1 (true). Advanced Tactics.
        self.sc2_logic.advanced_tactics = True
        state = MockCollectionState(parent_world=self.sc2_logic.world, items={})
        initial_score = self.sc2_logic.terran_defense_rating(state, False, False)
        assert initial_score == 2

    def test_d10_ct10_2(self):
        # CT_D10_2 (F): C10.1 (false). Sem Advanced Tactics.
        self.sc2_logic.advanced_tactics = False
        state = MockCollectionState(parent_world=self.sc2_logic.world, items={})
        initial_score = self.sc2_logic.terran_defense_rating(state, False, False)
        assert initial_score == 0