import unittest
import mock
import pydealer
import os
import sys

sys.path.append(os.getcwd())
sys.path.append(os.path.abspath(".."))
from card_game import CardGame
from pydealer import Stack, Card


class GameTest(unittest.TestCase):
    def setUp(self):
        self.game = CardGame()

    def test_deal_card(self):
        """Test if house and player each has a single card"""
        self.assertEqual(self.game.deck.size, 52)
        self.assertEqual(self.game.house_card.size, 0)
        self.assertEqual(self.game.player_card.size, 0)
        self.game.deal_card()
        self.assertEqual(self.game.deck.size, 50)
        self.assertEqual(self.game.house_card.size, 1)
        self.assertEqual(self.game.player_card.size, 1)

    def test_reveal_card(self):
        """Test if house card is revealed correctly"""
        side_effects = [
            # 1st game
            Stack(cards=[Card("Ace", "Spades")]),
            Stack(cards=[Card("2", "Hearts")])
        ]
        self.game.deck.deal = mock.Mock(side_effect=side_effects)
        self.game.deal_card()
        with mock.patch("builtins.print") as fake_print:
            self.game.reveal_house_card()
            fake_print.assert_called_with("House has A♠")

    @mock.patch("builtins.print")
    def test_player_guess(self, fake_print):
        input_side_effects = ["l", "h", "abc", "higher"]
        with mock.patch("builtins.input", side_effect=input_side_effects):
            self.game.house_card = Stack(cards=[Card("Ace", "Spades")])
            guess = self.game.player_guess()
            self.assertEqual(guess, "lower")
            guess = self.game.player_guess()
            self.assertEqual(guess, "higher")
            guess = self.game.player_guess()
            self.assertEqual(guess, "higher")

    def test_compare_card(self):
        side_effects = [
            # 1st game
            Stack(cards=[Card("Ace", "Spades")]), Stack(cards=[Card("2", "Spades")]),
            # 2nd game
            Stack(cards=[Card("King", "Spades")]), Stack(cards=[Card("8", "Hearts")]),
            # 3rd game
            Stack(cards=[Card("Ace", "Hearts")]), Stack(cards=[Card("King", "Clubs")]),
            # 4th game
            Stack(cards=[Card("5", "Hearts")]), Stack(cards=[Card("5", "Diamonds")])
        ]
        with mock.patch.object(pydealer.Deck, "deal", side_effect=side_effects):
            result = self.game.compare_card(self.game.deck.deal(1), self.game.deck.deal(1))
            self.assertEqual(result, "higher")
            result = self.game.compare_card(self.game.deck.deal(1), self.game.deck.deal(1))
            self.assertEqual(result, "lower")
            result = self.game.compare_card(self.game.deck.deal(1), self.game.deck.deal(1))
            self.assertEqual(result, "higher")
            result = self.game.compare_card(self.game.deck.deal(1), self.game.deck.deal(1))
            self.assertEqual(result, "equal")

    @mock.patch("builtins.input")
    @mock.patch("builtins.print")
    def test_stop_continue(self, fake_print, fake_inputs):
        fake_inputs.side_effect = ["c", "conTinue", "S", "sto", "Stop"]
        stop_or_continue = self.game.player_continue()
        self.assertEqual(stop_or_continue, "continue")
        stop_or_continue = self.game.player_continue()
        self.assertEqual(stop_or_continue, "continue")
        stop_or_continue = self.game.player_continue()
        self.assertEqual(stop_or_continue, "stop")
        stop_or_continue = self.game.player_continue()
        self.assertEqual(stop_or_continue, "stop")

    @mock.patch("builtins.print")
    @mock.patch("builtins.input")
    def test_start_game(self, fake_input, fake_print):
        fake_input.side_effect = ["l", "c", "h", "c", "h", "s", "l", "c", "h"]
        deal_side_effects = [
            # 1st match
            Stack(cards=[Card("8", "Spades")]), Stack(cards=[Card("2", "Hearts")]),
            # 2nd match
            Stack(cards=[Card("Ace", "Clubs")]), Stack(cards=[Card("Ace", "Hearts")]),
            # 3rd match
            Stack(cards=[Card("Ace", "Spades")]), Stack(cards=[Card("Jack", "Hearts")]),
            # 4th match
            Stack(cards=[Card("9", "Diamonds")]), Stack(cards=[Card("5", "Diamonds")]),
            # 5th match
            Stack(cards=[Card("3", "Hearts")]), Stack(cards=[Card("2", "Diamonds")]),
        ]
        self.game.deck.deal = mock.Mock(side_effect=deal_side_effects)
        self.assertRaises(StopIteration, self.game.start_game)
        self.assertEqual(self.game.player_score, 10)

    def test_deal_return_card(self):
        self.assertEqual(self.game.deck.size, 52)
        self.game.deal_card()
        tmp_house_card = "%s of %s" % (self.game.house_card[0].value, self.game.house_card[0].suit)
        tmp_player_card = "%s of %s" % (self.game.player_card[0].value, self.game.player_card[0].suit)
        self.assertEqual(self.game.deck.size, 50)
        self.assertEqual(self.game.deck.find(tmp_house_card), [])
        self.assertEqual(self.game.deck.find(tmp_player_card), [])
        self.game.return_card()
        self.assertEqual(self.game.deck.size, 52)
        self.assertNotEqual(self.game.deck.find(tmp_house_card), [])
        self.assertNotEqual(self.game.deck.find(tmp_player_card), [])
        self.game.deal_card()
        self.game.deal_card()
        self.assertEqual(self.game.deck.size, 48)
        self.game.return_card()
        self.assertEqual(self.game.deck.size, 52)

    @mock.patch("builtins.input")
    @mock.patch("builtins.print")
    def test_lose(self, fake_print, fake_input):
        deal_side_effects = [
            # 1st match
            Stack(cards=[Card("3", "Spades")]), Stack(cards=[Card("2", "Hearts")]),
            # 2nd match
            Stack(cards=[Card("Queen", "Clubs")]), Stack(cards=[Card("King", "Hearts")]),
        ]
        fake_input.side_effect = ["h", "l"]
        game = CardGame()
        game.deck.deal = mock.Mock(side_effect=deal_side_effects)
        game.start_game()
        # After 1st match (Lose): 60 - 30 + 0 = 30
        # After 2nd match (Lose): 30 - 30 + 0 = 0
        self.assertEqual(game.player_score, 0)
        fake_print.assert_called_with("You lost with 0 points.")

    @mock.patch("builtins.input")
    @mock.patch("builtins.print")
    def test_win(self, fake_print, fake_input):
        deal_side_effects = [
            # 1st match
            Stack(cards=[Card("3", "Spades")]), Stack(cards=[Card("Ace", "Hearts")]),
            # 2nd match
            Stack(cards=[Card("8", "Clubs")]), Stack(cards=[Card("King", "Hearts")]),
            # 3rd match
            Stack(cards=[Card("Ace", "Spades")]), Stack(cards=[Card("Queen", "Hearts")]),
            # 4th match
            Stack(cards=[Card("9", "Diamonds")]), Stack(cards=[Card("5", "Diamonds")]),
        ]
        fake_input.side_effect = ["l", "c", "h", "c", "h", "c", "l", "s"]
        game = CardGame()
        game.deck.deal = mock.Mock(side_effect=deal_side_effects)
        game.player_score = 990
        game.start_game()
        # After 1st match: 990 - 30 + 20
        # After 2nd match: 990 - 30 + (20 * 2) (Already at 1000 here, but can still keep playing)
        # After 3rd match: 990 - 30 + (20 * 2 * 2)
        # After 4th match: 990 - 30 + (20 * 2 * 2 * 2) = 1120
        self.assertEqual(game.player_score, 1120)
        fake_print.assert_called_with("Congratulations! You won with 1120 points!")

    def test_suit_error(self):
        side_effects = [
            # 1st game
            Stack(cards=[Card("Ace", "NO SUIT")]),
            Stack(cards=[Card("Ace", "Hearts")])
        ]
        self.game.deck.deal = mock.Mock(side_effect=side_effects)
        self.game.deal_card()
        self.assertRaises(Exception, self.game.reveal_house_card)

    @mock.patch("builtins.input")
    @mock.patch("builtins.print")
    def test_equal_stop(self, fake_print, fake_input):
        deal_side_effects = [
            # 1st match
            Stack(cards=[Card("3", "Spades")]), Stack(cards=[Card("King", "Hearts")]),
            # 2nd match
            Stack(cards=[Card("Queen", "Clubs")]), Stack(cards=[Card("Queen", "Hearts")]),
        ]

        fake_input.side_effect = ["h", "c", "l", "s"]
        self.game.deck.deal = mock.Mock(side_effect=deal_side_effects)
        self.assertRaises(StopIteration, self.game.start_game)
        # After 1st match: 60 - 30 + 20
        # After 2nd match: 60 - 30 + (20 * 2) = 70
        # Stop before 5th match (Lose): 70 - 30 = 40
        self.assertEqual(self.game.player_score, 40)

        
if __name__ == '__main__':
    unittest.main()