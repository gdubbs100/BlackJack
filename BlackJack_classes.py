import numpy as np
import random


class Card:
    """Card class for game - units to make up deck"""

    def __init__(self, value, suit):
        self.value = value
        self.suit = suit

    def __repr__(self):
        return f'{self.value} of {self.suit}'


class Deck:
    """Deck class - made up of cards, to deal to players in game"""

    def __init__(self, cards):
        self.cards = cards
        self.deck_size = len(cards)
        self.dealt = []  # keeps track of dealt cards

    def __repr__(self):
        return "\n".join([f"{card}" for card in self.cards])

    def __getitem__(self, indices):
        return self.cards[indices]

    def shuffle(self, times=3):
        for t in range(0, times):
            np.random.shuffle(self.cards)

    def deal(self, n):
        assert n <= len(self.cards), "Cannot deal more cards than available"
        to_deal = self.cards[0:n]
        self.dealt += to_deal  # keep track of dealt cards
        self.cards = self.cards[n:]  # remove cards from deck
        return to_deal

    def reclaimCards(self):
        self.cards += self.dealt
        self.dealt = []


class Game:
    """class for the running of the game"""

    def __init__(self, ID, deck, players, dealer):
        self.ID = ID  # give game an ID (should be an integer)
        self.deck = deck
        self.players = players
        self.dealer = dealer

    def deal(self):
        """initial dealing of cards"""
        for player in self.players + [self.dealer]:
            player.getHand(self.deck.deal(2))

    def playerMove(self, player):
        hit = True

        while not player.bust and hit:

            hit = player.hitOrStay(faceup = self.dealer.faceup)

            if hit:
                player.addCard(self.deck.deal(1))

    def checkWinner(self):
        # scores: 1 = win, 0 draw, -1, lose
        for player in self.players:

            if player.bust & self.dealer.bust:
                player.updateWins(self.ID, 0)
                self.dealer.updateWins(self.ID, 0)
            elif player.bust & (not self.dealer.bust):
                player.updateWins(self.ID, -1)
                self.dealer.updateWins(self.ID, 1)
            elif (not player.bust) & self.dealer.bust:
                player.updateWins(self.ID, 1)
                self.dealer.updateWins(self.ID, -1)
            elif player.score > self.dealer.score:
                player.updateWins(self.ID, 1)
                self.dealer.updateWins(self.ID, -1)
            elif player.score <= self.dealer.score:
                # dealer wins if scores are equal
                player.updateWins(self.ID, -1)
                self.dealer.updateWins(self.ID, 1)
            else:
                print("Uh Oh!", player.score, self.dealer.score)  # leave for checking now...
            print(player.name, ": ", player.getWins(self.ID), player.score,
                  self.dealer.name, ": ", self.dealer.getWins(self.ID), self.dealer.score)

    def resetGame(self):
        self.deck.reclaimCards()
        for player in self.players + [self.dealer]:
            player.bust = False
            player.hand = None
            player.score = 0
            if player.name == "Dealer":
                player.faceup = None

    def play(self):

        self.deck.shuffle(5)  # shuffle the deck
        self.deal()  # make sure each player has cards
        # make sure players know dealer showing
        for player in self.players:
            self.playerMove(player)

        # dealer goes last
        self.playerMove(self.dealer)

        # check winner
        self.checkWinner()

        self.resetGame()


class Player:
    """Player class to particpate in game"""

    def __init__(self, name='Tim'):
        self.hand = None
        self.score = 0
        self.bust = False
        self.name = name
        self.wins = {}  # dict of game id, game result (win, loose, draw)

    def hitOrStay(self, faceup):
        return True if np.random.uniform() <= 0.9 else False

    def getHand(self, cards):
        self.hand = cards
        self.calcScore()

    def addCard(self, new):
        self.hand += new
        self.calcScore()

    def calcScore(self):
        temp_score = 0

        # split cards for score calculation
        non_aces = [card for card in self.hand if card.value != 'A']
        aces = [card for card in self.hand if card.value == 'A']

        # check that there actually are cards
        num_non_aces = len(non_aces)
        num_aces = len(aces)

        if num_non_aces > 0:
            for card in non_aces:
                if card.value.isdigit():
                    temp_score += int(card.value)
                elif card.value in {'K', 'Q', 'J'}:
                    temp_score += 10

        if num_aces > 0:
            # checks for rare cases of multiple aces
            if temp_score + 11 + 1 * (num_aces - 1) <= 21:
                temp_score += 11 + 1 * (num_aces - 1)
            else:
                temp_score += 1 * num_aces

        self.score = temp_score

        if self.score > 21:
            self.bust = True

    def updateWins(self, game_id, result):
        self.wins[game_id] = result

    def getWins(self, game_id):
        return self.wins[game_id]


class Dealer(Player):
    """Dealer class - special type of player with one faceup card"""

    def __init__(self):
        super().__init__()
        self.faceup = None
        self.name = 'Dealer'

    def hitOrStay(self, faceup):
        # dealer specific hit / stay function
        if self.score <= 17:
            return True
        else:
            return False

    def getHand(self, cards):
        self.hand = cards
        self.calcScore()
        self.faceup = self.hand[0]  # put the first card faceup

class HumanPlayer(Player):
    """Human Player"""

    def __init__(self):
        super().__init__()
        self.name = input("Please enter your name...")

    def hitOrStay(self, faceup):
        print('\n--------------\n',
              "Your hand is: ", self.hand, "\n",
              "Your score is: ", self.score, "\n",
              '\n--------------\n'
              )
        move = ''
        while move not in {"hit", "stay"}:
            move = input("Do you want to hit or stay (please enter hit or stay)?").lower()
        if move == "hit":
            return True
        else:
            return False
