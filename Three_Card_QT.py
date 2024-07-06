import random
import logging
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout, \
    QWidget, QInputDialog, QMessageBox, QFrame
from PyQt5.QtGui import QFont, QPixmap, QPalette, QBrush
from PyQt5.QtCore import Qt, QSize


class ThreeCardPokerGame(QMainWindow):
    suits = ['♥️', '♦️', '♣️', '♠️']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    # Mapping of card suits for folders finding
    suit_to_folder = {
        '♥️': 'hearts',
        '♦️': 'diamonds',
        '♣️': 'clubs',
        '♠️': 'spades'
    }

    def __init__(self):
        super().__init__()
        self.player_balance = 1000
        self.player_hand = []
        self.dealer_hand = []
        self.deck = self.shuffled_deck()
        self.ante_bet = 0
        self.pair_plus_bet = 0
        self.play_bet = 0
        self.profited = 0
        self.game_round = 1
        self.payout_details = ""
        self.last_ante_bet = 0
        self.last_pair_plus_bet = 0

        # Logger setup
        self.logger = logging.getLogger('ThreeCardPokerGame')
        self.logger.setLevel(logging.INFO)
        file_handler = logging.FileHandler('game.log')
        self.logger.addHandler(file_handler)

        # UI Initialization
        self.initUI()
        self.quick_bet_btn.setVisible(False)

        # Payout for 'Play' bet
        self.play_payout = {
            "High Card": 1,
            "Pair": 1,
            "Flush": 1,
            "Straight": 1,
            "Three of a Kind": 1,
            "Straight Flush": 1
        }

        # Payout for 'Ante' bet
        self.ante_payout = {
            "High Card": 1,
            "Pair": 1,
            "Flush": 1,
            "Straight": 2,
            "Three of a Kind": 4,
            "Straight Flush": 5
        }

        # Payout for 'Pair Plus' bet
        self.pair_plus_payout = {
            "High Card": 0,
            "Pair": 1,
            "Flush": 4,
            "Straight": 6,
            "Three of a Kind": 25,
            "Straight Flush": 40
        }

        # Rank order for cards
        self.rank_order = {
            '2': 2,
            '3': 3,
            '4': 4,
            '5': 5,
            '6': 6,
            '7': 7,
            '8': 8,
            '9': 9,
            '10': 10,
            'J': 11,
            'Q': 12,
            'K': 13,
            'A': 14
        }

    def initUI(self):
        # Window setup
        self.setWindowTitle("Three Card Poker")
        self.setGeometry(100, 100, 600, 900)

        # Background setup
        background = QPixmap("imagaes/UI/1.png")
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(background))
        self.setPalette(palette)

        # Main layout setup
        main_layout = QVBoxLayout()
        top_layout = QVBoxLayout()
        player_layout = QHBoxLayout()
        dealer_layout = QHBoxLayout()
        middle_layout = QGridLayout()
        bottom_layout = QHBoxLayout()
        button_layout = QHBoxLayout()

        # Font setup
        label_font = QFont("Arial", 14)
        button_font = QFont("Arial", 12)

        # Player layout setup
        self.player_text_label = QLabel("Your Cards:")
        self.player_text_label.setFont(QFont("Arial", 30))
        self.player_text_label.setAlignment(Qt.AlignCenter)
        player_layout.addWidget(self.player_text_label)

        self.player_hand_labels = [QLabel() for _ in range(3)]
        for label in self.player_hand_labels:
            label.setFixedSize(QSize(100, 150))
            player_layout.addWidget(label)

        top_layout.addLayout(player_layout)

        # Dealer layout setup
        self.dealer_text_label = QLabel("Dealer's Cards:")
        self.dealer_text_label.setFont(QFont("Arial", 30))
        self.dealer_text_label.setAlignment(Qt.AlignCenter)
        dealer_layout.addWidget(self.dealer_text_label)

        self.dealer_hand_labels = [QLabel() for _ in range(3)]
        for label in self.dealer_hand_labels:
            label.setFixedSize(QSize(100, 150))
            dealer_layout.addWidget(label)

        top_layout.addLayout(dealer_layout)

        # top_layout/middle_layout line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setLineWidth(1)
        line.setStyleSheet("color: grey;")
        main_layout.addLayout(top_layout)
        main_layout.addWidget(line)
        main_layout.addLayout(middle_layout)

        # Middle layout setup
        self.pair_plus_bet_label = QLabel("Pair Plus")
        self.pair_plus_bet_label.setFont(label_font)
        self.pair_plus_bet_label.setAlignment(Qt.AlignCenter)
        self.pair_plus_bet_label.setStyleSheet(
            "border: 2px solid grey; border-radius: 200px; padding: 20px; background-color: #8ebf63;")
        middle_layout.addWidget(self.pair_plus_bet_label, 0, 1, Qt.AlignCenter)

        self.ante_bet_label = QLabel("Ante")
        self.ante_bet_label.setFont(label_font)
        self.ante_bet_label.setAlignment(Qt.AlignCenter)
        self.ante_bet_label.setStyleSheet(
            "border: 2px solid grey; border-radius: 200px; padding: 20px; background-color: #8ebf63;")
        middle_layout.addWidget(self.ante_bet_label, 1, 0, Qt.AlignCenter)

        self.play_bet_label = QLabel("Play")
        self.play_bet_label.setFont(label_font)
        self.play_bet_label.setAlignment(Qt.AlignCenter)
        self.play_bet_label.setStyleSheet(
            "border: 2px solid grey; border-radius: 200px; padding: 20px; background-color: #8ebf63;")
        middle_layout.addWidget(self.play_bet_label, 1, 2, Qt.AlignCenter)

        # Middle_layout/Bottom_layout line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setLineWidth(1)
        line.setStyleSheet("color: grey;")
        main_layout.addWidget(line)
        main_layout.addLayout(bottom_layout)

        # Bottom layout setup for balance and payout details
        self.balance_label = QLabel(f"Balance: ${self.player_balance}")
        self.balance_label.setFont(label_font)
        bottom_layout.addWidget(self.balance_label, alignment=Qt.AlignLeft)

        self.profited_label = QLabel("")
        self.profited_label.setFont(label_font)
        self.profited_label.setAlignment(Qt.AlignCenter)
        bottom_layout.addWidget(self.profited_label, alignment=Qt.AlignLeft)

        self.payout_details_label = QLabel("")
        self.payout_details_label.setFont(label_font)
        bottom_layout.addWidget(self.payout_details_label, alignment=Qt.AlignRight)

        # Button layout setup
        self.bet_btn = QPushButton("Place Bet", self)
        self.bet_btn.setFont(button_font)
        self.bet_btn.clicked.connect(self.place_bet)
        self.bet_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        button_layout.addWidget(self.bet_btn)

        self.play_btn = QPushButton("Play", self)
        self.play_btn.setFont(button_font)
        self.play_btn.clicked.connect(self.play)
        self.play_btn.setEnabled(False)
        self.play_btn.setStyleSheet("background-color: #B0B0B0; color: white;")
        button_layout.addWidget(self.play_btn)

        self.fold_btn = QPushButton("Fold", self)
        self.fold_btn.setFont(button_font)
        self.fold_btn.clicked.connect(self.fold)
        self.fold_btn.setEnabled(False)
        self.fold_btn.setStyleSheet("background-color: #B0B0B0; color: white;")
        button_layout.addWidget(self.fold_btn)

        self.quick_bet_btn = QPushButton("Same Bet Again", self)
        self.quick_bet_btn.setFont(button_font)
        self.quick_bet_btn.clicked.connect(self.quick_bet)
        self.quick_bet_btn.setEnabled(False)
        self.quick_bet_btn.setStyleSheet("background-color: #FF9800; color: white;")
        button_layout.addWidget(self.quick_bet_btn)

        main_layout.addLayout(button_layout)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Set stretch factors
        main_layout.setStretchFactor(top_layout, 20)
        main_layout.setStretchFactor(middle_layout, 15)
        main_layout.setStretchFactor(bottom_layout, 2)

    def get_card_image_path(self, card):
        # Get the image path for a card
        rank = card['rank']
        if rank == 'A':
            rank = 'ace'
        elif rank == 'J':
            rank = 'jack'
        elif rank == 'K':
            rank = 'king'
        elif rank == 'Q':
            rank = 'queen'
        suit = card['suit']
        folder = self.suit_to_folder[suit]
        return f"imagaes/cards/{folder}/ornamental-deck-{rank}-of-{folder}-clipart-xl.png"

    def set_card_images(self, labels, hand):
        # Set the images for the cards
        for i in range(3):
            card = hand[i]
            card_image_path = self.get_card_image_path(card)
            pixmap = QPixmap(card_image_path).scaled(QSize(100, 150), Qt.KeepAspectRatio)
            labels[i].setPixmap(pixmap)
            labels[i].setScaledContents(True)

    def shuffled_deck(self):
        # Create a shuffled deck
        deck = [{'rank': rank, 'suit': suit} for rank in self.ranks for suit in self.suits]
        random.shuffle(deck)
        return deck

    def is_straight(self, cards):
        # Check if the hand is a straight
        rank_values = list(map(lambda card: self.ranks.index(card['rank']), cards))
        rank_values.sort()
        if rank_values == [0, 1, 12]:  # A-2-3 count as a straight but smallest (not defined in the rules)
            return True
        return rank_values[2] - rank_values[0] == 2 and len(set(rank_values)) == 3

    @staticmethod
    def is_flush(cards):
        # Check if the hand is a flush
        return len(set(card['suit'] for card in cards)) == 1

    def hand_strength(self, cards):
        # Determine the strength of the hand
        hand_type = self.evaluate_hand(cards)
        strengths = {
            "High Card": 1,
            "Pair": 2,
            "Flush": 3,
            "Straight": 4,
            "Three of a Kind": 5,
            "Straight Flush": 6
        }
        return strengths.get(hand_type, 0)

    def compare_hands(self, player, dealer):
        # Compare the player's hand to the dealer's hand
        player_strength = self.hand_strength(player)
        dealer_strength = self.hand_strength(dealer)

        if player_strength > dealer_strength:
            return "Player"
        elif player_strength < dealer_strength:
            return "Dealer"
        else:
            player_ranks = sorted([card['rank'] for card in player], key=lambda x: self.rank_order[x], reverse=True)
            dealer_ranks = sorted([card['rank'] for card in dealer], key=lambda x: self.rank_order[x], reverse=True)

            if player_strength == 1:  # High Card
                for p_rank, d_rank in zip(player_ranks, dealer_ranks):
                    if self.rank_order[p_rank] > self.rank_order[d_rank]:
                        return "Player"
                    elif self.rank_order[p_rank] < self.rank_order[d_rank]:
                        return "Dealer"
                return "Tie"

            elif player_strength == 2:  # Pair
                player_pair_rank = max(player_ranks, key=player_ranks.count)
                dealer_pair_rank = max(dealer_ranks, key=dealer_ranks.count)
                if self.rank_order[player_pair_rank] > self.rank_order[dealer_pair_rank]:
                    return "Player"
                elif self.rank_order[player_pair_rank] < self.rank_order[dealer_pair_rank]:
                    return "Dealer"
                else:
                    player_non_pair_rank = min(player_ranks, key=player_ranks.count)
                    dealer_non_pair_rank = min(dealer_ranks, key=dealer_ranks.count)
                    if self.rank_order[player_non_pair_rank] > self.rank_order[dealer_non_pair_rank]:
                        return "Player"
                    elif self.rank_order[player_non_pair_rank] < self.rank_order[dealer_non_pair_rank]:
                        return "Dealer"
                    else:
                        return "Tie"

            else:  # Flush, Straight, Three of a Kind, Straight Flush
                for p_rank, d_rank in zip(player_ranks, dealer_ranks):
                    if self.rank_order[p_rank] > self.rank_order[d_rank]:
                        return "Player"
                    elif self.rank_order[p_rank] < self.rank_order[d_rank]:
                        return "Dealer"
                return "Tie"

    def evaluate_hand(self, cards):
        # Evaluate the type of hand
        if self.is_straight(cards) and self.is_flush(cards):
            return "Straight Flush"
        if len(set(card['rank'] for card in cards)) == 1:
            return "Three of a Kind"
        if self.is_straight(cards):
            return "Straight"
        if self.is_flush(cards):
            return "Flush"
        if len(set(card['rank'] for card in cards)) == 2:
            return "Pair"
        return "High Card"

    def place_bet(self):
        # Place the bet
        ante_bet, ok1 = QInputDialog.getInt(self, "Bet", "Enter your Ante bet (min $1, max $50000):", min=1, max=50000)
        if not ok1:
            return
        pair_plus_bet, ok2 = QInputDialog.getInt(self, "Bet", "Enter your Pair Plus bet (min $0, max $5000):", min=0,
                                                 max=5000)
        if not ok2:
            pair_plus_bet = 0

        if ante_bet + pair_plus_bet > self.player_balance:
            QMessageBox.critical(self, "Error", "You don't have enough balance for this bet!")
            return

        self.ante_bet = ante_bet
        self.pair_plus_bet = pair_plus_bet

        self.profited = - self.ante_bet - self.pair_plus_bet
        self.bet_btn.setEnabled(False)
        self.bet_btn.setStyleSheet("background-color: #B0B0B0; color: white;")
        self.initialize_game()
        self.deal_hand()

        self.last_ante_bet = self.ante_bet
        self.last_pair_plus_bet = self.pair_plus_bet

    def initialize_game(self):
        # Initialize the game
        for label in self.player_hand_labels:
            label.setPixmap(QPixmap())
        for label in self.dealer_hand_labels:
            label.setPixmap(QPixmap())
        self.profited_label.setText("")
        self.ante_bet_label.setText(f"Ante\n${self.ante_bet}")
        self.pair_plus_bet_label.setText(f"Pair Plus\n${self.pair_plus_bet}")
        self.play_bet_label.setText(f"Play\n${self.play_bet}")
        self.play_btn.setEnabled(False)
        self.fold_btn.setEnabled(False)
        self.quick_bet_btn.setVisible(False)
        self.payout_details_label.setText("")

    def draw_cards(self):
        # Draw cards from the deck
        hand = [self.deck.pop(), self.deck.pop(), self.deck.pop()]
        sorted_hand = sorted(hand, key=lambda card: self.rank_order[card['rank']], reverse=True)
        return sorted_hand

    def deal_hand(self):
        # Deal the hand
        self.player_hand = self.draw_cards()
        self.set_card_images(self.player_hand_labels, self.player_hand)

        # Set dealer's cards to back image
        back_image_path = "imagaes/cards/card_back/card-backs-grid-red-clipart-xl.png"
        for label in self.dealer_hand_labels:
            pixmap = QPixmap(back_image_path).scaled(QSize(110, 150), Qt.KeepAspectRatio)
            label.setPixmap(pixmap)
            label.setScaledContents(True)

        self.play_btn.setEnabled(True)
        self.fold_btn.setEnabled(True)
        self.play_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.fold_btn.setStyleSheet("background-color: #F44336; color: white;")

    def quick_bet(self):
        # Place a quick bet
        if self.last_ante_bet + self.last_pair_plus_bet > self.player_balance:
            QMessageBox.critical(self, "Error", "You don't have enough balance for this bet!")
            return

        self.ante_bet = self.last_ante_bet
        self.pair_plus_bet = self.last_pair_plus_bet

        self.profited = - self.ante_bet - self.pair_plus_bet
        self.bet_btn.setEnabled(False)
        self.initialize_game()
        self.deal_hand()
        self.quick_bet_btn.setVisible(False)
        self.bet_btn.setEnabled(False)
        self.bet_btn.setStyleSheet("background-color: #B0B0B0; color: white;")
        self.play_btn.setEnabled(True)
        self.play_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.fold_btn.setEnabled(True)
        self.fold_btn.setStyleSheet("background-color: #F44336; color: white;")
        self.payout_details_label.setText("")

    def play(self):
        if self.ante_bet > self.player_balance:
            QMessageBox.critical(self, "Error", "You don't have enough balance for this bet!")
            return
        else:
            self.play_bet = self.ante_bet
            self.profited -= self.play_bet
            self.play_bet_label.setText(f"Play\n${self.play_bet}")

        self.dealer_hand = self.draw_cards()
        self.set_card_images(self.dealer_hand_labels, self.dealer_hand)

        result = self.compare_hands(self.player_hand, self.dealer_hand)
        player_hand_type = self.evaluate_hand(self.player_hand)

        dealer_qualified = (self.hand_strength(self.dealer_hand) > 1 or self.hand_strength(self.dealer_hand) == 1
                            and self.rank_order[self.dealer_hand[0]['rank']] > 11)

        if not dealer_qualified:
            result = "Player"

        if result == "Player":
            # winning amounts
            ante_winnings = self.ante_bet * (self.ante_payout[player_hand_type] + 1) if dealer_qualified else self.ante_bet * 2
            pair_plus_winnings = self.pair_plus_bet * self.pair_plus_payout[player_hand_type]
            play_winnings = self.ante_bet * (self.play_payout[player_hand_type] + 1) if dealer_qualified else self.ante_bet

            # display payout details
            self.payout_details = f"Ante Win: ${ante_winnings}\nPair Plus Win: ${pair_plus_winnings}\nPlay Win: ${play_winnings}\nTotal Win: ${ante_winnings + pair_plus_winnings + play_winnings}" if dealer_qualified else f"[Dealer Not Qulified]\nAnte Win: ${ante_winnings}\nPair Plus Win: ${pair_plus_winnings}\nPlay Win: ${play_winnings}\nTotal Win: ${ante_winnings + pair_plus_winnings + play_winnings}"

            # update profited amount
            self.profited = self.profited + ante_winnings + pair_plus_winnings + play_winnings

        elif result == "Dealer":
            # winning amounts
            pair_plus_winnings = self.pair_plus_bet * self.pair_plus_payout[player_hand_type]

            # display payout details
            self.payout_details = f"Pair Plus Win: ${pair_plus_winnings}\nTotal Win: ${pair_plus_winnings}"

            # update profited amount
            self.profited = self.profited + pair_plus_winnings

        else:
            # winning amounts
            ante_winnings = self.ante_bet
            pair_plus_winnings = self.pair_plus_bet * self.pair_plus_payout[player_hand_type]

            # display payout details
            self.payout_details = f"Ante Win: ${ante_winnings}\nPair Plus Win: ${pair_plus_winnings}\nTotal Win: ${ante_winnings + pair_plus_winnings}"

            # update profited amount
            self.profited = self.profited + ante_winnings + pair_plus_winnings

        self.player_balance += self.profited
        self.profited_label.setText(f"Profited: ${self.profited}")
        self.payout_details_label.setText(self.payout_details)
        self.finish_game()

    def record(self):
        self.logger.info(f"[Game Round: {self.game_round}   {self.compare_hands(self.player_hand, self.dealer_hand)} wins]")
        player_cards = ', '.join([f"{card['rank']}{card['suit']}" for card in self.player_hand])
        dealer_cards = ', '.join([f"{card['rank']}{card['suit']}" for card in self.dealer_hand])
        self.logger.info(f"Player: {player_cards}, {self.evaluate_hand(self.player_hand)}")
        self.logger.info(f"Dealer: {dealer_cards}, {self.evaluate_hand(self.dealer_hand)}")
        self.logger.info("============= BET ==============")
        self.logger.info(f"Ante: {self.ante_bet}")
        self.logger.info(f"Pair Plus: {self.pair_plus_bet}")
        self.logger.info(f"Play: {self.play_bet}")
        self.logger.info("============= WIN ==============")
        self.logger.info(f"{self.payout_details_label.text()}")
        self.logger.info("============= KEY ==============")
        self.logger.info(f"Balance: {self.player_balance}")
        self.logger.info(f"Profited: {self.profited}\n\n")
        self.game_round += 1

    def fold(self):
        self.player_balance += self.profited
        self.profited_label.setText(f"Profited: ${self.profited}")
        self.payout_details_label.setText("")
        self.finish_game()

    def finish_game(self):
        self.update_balance()
        self.record()  # for testing only (logging)
        self.bet_btn.setEnabled(True)
        self.bet_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.play_btn.setEnabled(False)
        self.play_btn.setStyleSheet("background-color: #B0B0B0; color: white;")
        self.fold_btn.setEnabled(False)
        self.fold_btn.setStyleSheet("background-color: #B0B0B0; color: white;")
        self.quick_bet_btn.setVisible(True)
        self.play_bet = 0
        self.ante_bet = 0
        self.pair_plus_bet = 0
        self.deck = self.shuffled_deck()

        if self.player_balance < 10:
            self.payout_details_label.setText("No Money! Game Over!")
            self.close()
        else:
            self.quick_bet_btn.setVisible(True)
            self.quick_bet_btn.setEnabled(True)

    def update_balance(self):
        self.balance_label.setText(f"Balance: ${self.player_balance}")


if __name__ == "__main__":
    app = QApplication([])
    game = ThreeCardPokerGame()
    game.show()
    app.exec_()
