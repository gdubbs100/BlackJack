import numpy as np
import random
from collections import namedtuple

# tuple for recording states / actions
sa_tuple = namedtuple(typename="state_action_tuple",
                      field_names=('state', 'action'))

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

    def __init__(self, ID, deck, players, dealer, VERBOSE = True):
        self.ID = ID  # give game an ID (should be an integer)
        self.deck = deck
        self.players = players
        self.dealer = dealer
        self.VERBOSE = VERBOSE

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
        # scores: 1 = win, 0 = draw, -1 = lose
        for player in self.players:

            if player.bust & self.dealer.bust:
                player.updateWins(self.ID, -1)
                self.dealer.updateWins(self.ID, -1)
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
            if self.VERBOSE:
                # print out if setting verbose
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
        # 50 / 50 hit or stay
        return True if np.random.uniform() <= 0.5 else False

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


class RL_Player(Player):
    """A reinforcement learning agent that uses a policy to determine moves"""

    def __init__(self, name, lr):
        super().__init__()
        self.name = name
        self.lr = lr
        self.state_actions = []
        # player score: [0,31]
        # dealer score of faceup: [1,10] => Ace =1
        # has useable ace: [0, 1] if has Ace and score + 11 <= 21
        self.Q = np.random.rand(32, 10, 2, 2)  # action value function
        self.pi = np.round(np.random.rand(32, 10, 2, 1), 0)  # policy - last array is only action to choose (1, 0)

        self.useable_ace = False

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
                self.useable_ace = True

            else:
                temp_score += 1 * num_aces
                self.useable_ace = False

        self.score = temp_score

        if self.score > 21:
            self.bust = True

    def getDealerCardScore(self, card):
        if card.value.isdigit():
            score = int(card.value)
        elif card.value in {'K', 'Q', 'J'}:
            score = 10
        elif card.value == 'A':
            score = 1
        return score

    def hitOrStay(self, faceup):
        score_idx = self.score
        faceup_idx = self.getDealerCardScore(faceup) - 1  # minus one for idx
        useable_ace = int(self.useable_ace)
        move = self.pi[score_idx, faceup_idx, useable_ace, 0]

        # record your moves here for MC update function
        # state = (score_idx, faceup_idx, useable_ace)
        # action = move
        self.state_actions.insert(
            0,  # insert state_action at first index
            sa_tuple(
                (int(score_idx), int(faceup_idx), int(useable_ace)),
                int(move)
            )
        )

        # hit is 0, stay is 1
        if move == 0:
            return True
        elif move == 1:
            return False

    def updateWins(self, game_id, result):
        self.wins[game_id] = result
        self.updatePolicy(game_id)

    def updatePolicy(self, game_id):
        # most recent action at start
        # only winning / loosing / drawing contains a score.
        # no discounting

        for val in self.state_actions:
            action = val.action
            state = val.state

            old = self.Q[state[0], state[1], state[2], action]
            new = old + self.lr * (self.wins[game_id] - old)

            self.Q[state[0], state[1], state[2], action] = new

            self.pi[state[0], state[1], state[2], 0] = np.argmax(self.Q[state[0], state[1], state[2],])

        self.state_actions = []  # reset state actions
        self.useable_ace = False  # reset useable ace


class softRL_Player(RL_Player):
    """RL player that uses a soft-epsilon policy"""

    def __init__(self, name, lr, epsilon):
        super().__init__(name, lr)
        # self.name = name
        # self.lr = lr
        self.epsilon = epsilon
        raw_pi = np.random.rand(32, 10, 2, 2)

        # ensure pi is normalised for probs
        raw_total = np.sum(raw_pi, axis=3)
        self.pi = raw_pi / raw_total[:, :, :, np.newaxis]  # policy - last array is probs for each action

    def hitOrStay(self, faceup):
        score_idx = self.score
        faceup_idx = self.getDealerCardScore(faceup) - 1  # minus one for idx
        useable_ace = int(self.useable_ace)  # get function to determine this
        probs = self.pi[score_idx, faceup_idx, useable_ace,]
        move = np.random.choice([0, 1], p=probs)

        # record your moves here for MC update function
        # state = (score_idx, faceup_idx)
        # action = move
        self.state_actions.insert(
            0,  # insert state_action at first index
            sa_tuple(
                (int(score_idx), int(faceup_idx), int(useable_ace)),
                int(move)
            )
        )

        # hit is 0, stay is 1
        if move == 0:
            return True
        elif move == 1:
            return False

    def updateWins(self, game_id, result):
        self.wins[game_id] = result
        self.updatePolicy(game_id)

    def updatePolicy(self, game_id):
        # most recent action at start
        # only winning / loosing / drawing contains a score.
        # no discounting

        for val in self.state_actions:
            action = val.action
            state = val.state

            old = self.Q[state[0], state[1], state[2], action]
            new = old + self.lr * (self.wins[game_id] - old)

            self.Q[state[0], state[1], state[2], action] = new

            a_star = np.argmax(self.Q[state[0], state[1], state[2],])
            not_a_star = np.abs(a_star - 1)  # gives 1 if 0, 0 if 1

            self.pi[state[0], state[1], state[2], a_star] = 1 - self.epsilon + self.epsilon / 2
            self.pi[state[0], state[1], state[2], not_a_star] = self.epsilon / 2

        self.state_actions = []  # reset state actions
        self.useable_ace = False  # reset useable ace


class Test_Player(Player):
    """Player with test strategies for benchmarking - random guess (50/50)
    Always Hit, Always Stay"""

    def __init__(self, name, strat):
        super().__init__()
        self.name = name
        self.strat = strat

    def HitOrStay(self):
        if self.strat == 'RANDOM':
            return True if np.random.uniform() <= 0.5 else False
        elif self.strat == 'HIT':
            return True
        elif self.strat == 'STAY':
            return False
