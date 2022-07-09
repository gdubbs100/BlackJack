# BlackJack
Coding up BlackJack Game and testing Reinforcement Learning Algorithms 

## Rules of Black Jack
To win you need to acquire more points than the dealer, but less than 21.

Players are each dealt two cards. The Dealer has one card face down. If the Player has an Ace and any 10-point card (i.e. K, Q, J) - Player with this automatically wins unless the Dealer also has this, in which case the result is a draw.

Once cards have been dealt each player takes a turn - in a turn a player either 'hits' or 'stays'. If the player hits, then the dealer provides them with a card. If the player stays, then the player recieves no additional cards and their turn ends. The player can hit as many times as they like unless their score exceeds 21, upon which they 'bust'. A player who busts loses the game.

Number cards have a score equal to their number. Face cards (K, Q, J) have a score = 10. Aces have a value of 1 or 11. An ace is always worth 11 unless the player holding it would be bust, in which case it must take a value of 1.