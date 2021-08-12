import pydealer

class CardGame:
    CARD_RANK = {
        "values": {
            "King": 13,
            "Queen": 12,
            "Jack": 11,
            "10": 10,
            "9": 9,
            "8": 8,
            "7": 7,
            "6": 6,
            "5": 5,
            "4": 4,
            "3": 3,
            "2": 2,
            "Ace": 1,
        },
        "suits": {
            "Spades": 1,
            "Hearts": 1,
            "Clubs": 1,
            "Diamonds": 1
        }
    }

    def __init__(self):
        self.player_score = 60
        self.reward = 20
        self.cost = 30
        self.deck = pydealer.Deck()
        self.house_card = pydealer.Stack()
        self.player_card = pydealer.Stack()

    def deal_card(self):
        self.deck.shuffle()
        self.house_card.add(self.deck.deal(1))
        self.player_card.add(self.deck.deal(1))

    @staticmethod
    def get_suit_symbol(card):
        if card.suit == "Spades":
            return "♠"
        elif card.suit == "Hearts":
            return "♥"
        elif card.suit == "Clubs":
            return "♣"
        elif card.suit == "Diamonds":
            return "♦"
        else:
            raise Exception("Cannot map suit to symbol, unknown suit %s" % card.suit)

    @staticmethod
    def get_abbrv_card_value(card):
        if card.value == "Ace":
            return "A"
        elif card.value == "King":
            return "K"
        elif card.value == "Queen":
            return "Q"
        elif card.value == "Jack":
            return "J"
        else:
            return card.value

    def get_card_info(self, card):
        card_value = CardGame.get_abbrv_card_value(card)
        suit_symbol = CardGame.get_suit_symbol(card)
        return "%s%s" % (card_value, suit_symbol)

    def reveal_house_card(self):
        house_card_info = self.get_card_info(self.house_card[0])
        print("House has %s" % house_card_info)

    def process_guess(self, guess):
        if guess.lower() == "lower" or guess.lower() == "l":
            return "lower"
        elif guess.lower() == "higher" or guess.lower() == "h":
            return "higher"
        else:
            return guess

    def player_guess(self):
        house_card_info = self.get_card_info(self.house_card[0])
        print("Is your card lower(l) or higher(h) than %s" % house_card_info)
        guess = input()
        guess = self.process_guess(guess)
        while guess != "lower" and guess != "higher":
            print("Invalid input '%s', type 'lower(l)' or 'higher(h)':" % guess)
            guess = input()
            guess = self.process_guess(guess)
        return guess

    def compare_card(self, house_card, player_card):
        if player_card[0].gt(house_card[0], CardGame.CARD_RANK):
            return "higher"
        elif player_card[0].eq(house_card[0], CardGame.CARD_RANK):
            return "equal"
        else:
            return "lower"

    def process_stop_or_continue(self, command):
        if command.lower() == "stop" or command.lower() == "s":
            return "stop"
        elif command.lower() == "continue" or command.lower() == "c":
            return "continue"
        else:
            return command

    def process_input(self, user_input, pos_inputs):
        for pos_input in pos_inputs:
            if user_input.lower() == pos_input or user_input.lower() == pos_input[0]:
                return pos_input
        return user_input
    
    def get_player_input(self, possible_inputs):
        player_input = input()
        player_input = self.process_input(player_input, possible_inputs)
        while player_input not in possible_inputs:
            possible_inputs_str = " or ".join([pos_input + "(" + pos_input[0] + ")" for pos_input in possible_inputs])
            invalid_msg = "Invalid input '%s', type %s" % (player_input, possible_inputs_str)
            print(invalid_msg)
            player_input = input()
            player_input = self.process_input(player_input, possible_inputs)
        return player_input

    def player_guess(self):
        house_card_info = self.get_card_info(self.house_card[0])
        print("Is your card lower(l) or higher(h) than %s" % house_card_info)
        possible_inputs = ["lower", "higher"]
        guess = self.get_player_input(possible_inputs)
        return guess

    def player_continue(self):
        print("Would you like to continue(c) or stop(s)?")
        possible_inputs = ["continue", "stop"]
        stop_or_continue = self.get_player_input(possible_inputs)
        return stop_or_continue          

    def reveal_house_card(self):
        house_card_info = self.get_card_info(self.house_card[0])
        print("House has %s" % house_card_info)

    def reveal_player_card(self):
        player_card_info = self.get_card_info(self.player_card[0])
        print("You have %s" % player_card_info)

    def return_card(self):
        house_cards = self.house_card.empty(return_cards=True)
        player_cards = self.player_card.empty(return_cards=True)
        self.deck.add(cards=house_cards)
        self.deck.add(cards=player_cards)
        self.deck.shuffle()

    def play_match(self):
        player_continue = True
        tmp_reward = self.reward
        while player_continue:
            print("\nYour current score is: %d" % self.player_score)
            self.deal_card()
            self.reveal_house_card()
            guess = self.player_guess()
            result = self.compare_card(self.house_card, self.player_card)
            self.reveal_player_card()
            self.return_card()
            if guess == result:
                print("Correct! You earned +%d reward points" % (tmp_reward))
                player_continue = self.player_continue()
                if player_continue == "stop":
                    self.player_score += tmp_reward
                    break
                else:
                    tmp_reward = tmp_reward * 2
            elif guess != result and result == "equal":
                print("Cards were equal. Your reward points is still %s" % tmp_reward)
                player_continue = self.player_continue()
                if player_continue == "stop":
                    self.player_score += tmp_reward
                    break
            else:
                print("Incorrect! You lose -%d reward points " % (tmp_reward))
                break
                
    def start_game(self):
        print("Game Start!")
        print("You have %d points" % self.player_score)
        print("Cost for playing is %d points" % self.cost)
        print("Initial reward is %d points" % self.reward)
        matches = 1
        game_over = False
        while not game_over:
            print("\nMatch %d" % matches)
            print("Start new match, -%d cost for playing" % self.cost)
            self.player_score -= 30
            self.play_match()
            matches += 1
            game_over = self.check_game_over()

    def check_game_over(self):
        if self.player_score >= 1000:
            print("Congratulations! You won with %s points!" % self.player_score)
            return True
        elif self.player_score < 30:
            print("You lost with %s points." % self.player_score)
            return True
        else:
            return False


if __name__ == '__main__':
    game = CardGame()
    game.start_game()
