import os
from enum import IntEnum,Enum
from typing import List
import curses
import time

class LetterStates(IntEnum):
    NOTGUESSEDYET = 0
    NOTPRESENT = 1
    INCORRECTPOSITION = 2
    CORRECTPOSITION = 3

class Game:
    GUESSES = []#['WHISK', 'WHITE']
    ROUNDS = 6
    LENGTH = 5
    WIN_STATES = [LetterStates.CORRECTPOSITION for _ in range(LENGTH)]
    SHARE_EMOJI = {
        LetterStates.CORRECTPOSITION:    "🟩",
        LetterStates.INCORRECTPOSITION:  "🟨",
        LetterStates.NOTPRESENT:         "⬛"
        }
    def __init__(self, 
        path_solutions="data/solutions.txt",
        path_guesses="data/guesses.txt",
        path_clues="data/clues.txt",
        path_possible="data/possible.txt"
        ):
        with open(os.path.join(os.path.dirname(__file__), path_solutions), "r") as f:
            self.VALID_SOLUTIONS = tuple(l.upper() for l in f.read().splitlines() if len(l) == self.LENGTH)

        with open(os.path.join(os.path.dirname(__file__), path_guesses), "r") as f:
            self.VALID_GUESSES = tuple(l.upper() for l in f.read().splitlines() if len(l) == self.LENGTH)

        with open(os.path.join(os.path.dirname(__file__), path_clues), "r") as f:
            self.VALID_CLUES = tuple(l.upper() for l in f.read().splitlines() if len(l) == self.LENGTH)

        with open(os.path.join(os.path.dirname(__file__), path_possible), "r") as f:
            self.VALID_POSSIBLE = tuple(l.upper() for l in f.read().splitlines() if len(l) == self.LENGTH)

        # official list of guesses does not include solutions, so add them, ignoring duplicates (albeit no duplicates in official lists)
        self.VALID_GUESSES = tuple(set(self.VALID_SOLUTIONS + self.VALID_GUESSES))
        self.VALID_GUESSES = list(self.VALID_GUESSES)
        self.VALID_GUESSES.sort()
        self.VALID_GUESSES = tuple(self.VALID_GUESSES)

        self.VALID_CLUES = tuple(set(self.VALID_CLUES))

        self.POSSIBLE_WORDS = list(self.VALID_GUESSES)
        self.POSSIBLE_WORDS.sort()
        self.POSSIBLE_CLUES = []

    def getPlayerGuess(self, player, round, auto):
        player.out ('round = %s ' % round)
        guess = self.GUESSES[round-1] if len(self.GUESSES) >= round else None
        if auto: 
            guess = self.POSSIBLE_WORDS[0]
        if guess is None:
            while True:
                guess = player.guess(round)
                if player.ASSUME_GUESSES_VALID:
                    break
                elif len(guess) != self.LENGTH or not guess.isalpha():
                    guess = guess.strip()
                    player.warn(f"{ guess[:5]+'..' if len(guess) > self.LENGTH else guess } invalid")
                elif guess not in self.VALID_GUESSES:
                    player.warn(f"{ guess } not in dict".strip())
                else:
                    player.out ('\n')
                    break
        player.out ('guess = %s' % guess)
        return guess

    def generateClues(self, solution):
        clues = []
        # loop_list = self.VALID_POSSIBLE if len(self.VALID_POSSIBLE) > 1 else self.VALID_GUESSES
        loop_list = self.VALID_GUESSES
        for i,w in enumerate(loop_list):  # TODO USE VALID_GUESSES instead of VALID_SOLUTIONS
            clues += [Game.check_guess(w, solution)]
            # print("Guess:%s ClueGen:%s" % (w,clues[-1]))
        print("")

        # Remove duplicates and sort
        clues = [ tuple(c) for c in clues ]
        clues = set(clues)
        clues = list(clues)
        clues.sort()
        clues.reverse()
        
        clues.pop(0)   # empty clue
        clues.pop(-1)  # WINNING MATCH

        # Remove all with less than 2 (GREEN) 
        # clues = list(filter(lambda e: 
        #      2 <= sum([s==LetterStates.CORRECTPOSITION for s in e]),
        #      clues
        # ))

        # print("len(CLUES) = %s" % len(clues))

        textfile = open("data/clues.txt", "w")
        for element in clues:
            str = ''.join([self.SHARE_EMOJI[e] for e in element])
            textfile.write(str + "\n")
        textfile.close()

        return clues

    def useClues(self, player):
        clues = self.POSSIBLE_CLUES if len(self.POSSIBLE_CLUES) >= 1 else self.read_clues(self.VALID_CLUES)
        print ("We have %s clues" % len(clues))

        POSSIBLE_WORDS = []
        loop_list = self.VALID_POSSIBLE if len(self.VALID_POSSIBLE) > 1 else self.VALID_GUESSES
        print("Checking %s words for clues" % len(loop_list))

        for i,w in enumerate(loop_list):
            # update(progressWin, 0.5+(0.01*i/len(loop_list) )   )
            if ((i % 500) == 0):
                print("Checked %s/%s words for clues." % (i,len(loop_list)))
            search = list(self.VALID_GUESSES)
            search.remove(w)

            s_p = len(clues)
            s_m = []
            for c in clues:
                for s in search: 
                    if Game.is_same_response(s,w,c):
                        s_m += [s]
                        break
                else:
                    s_p -= 1
                    break
            else:
                POSSIBLE_WORDS += [w]
                print ('Adding %s to POSSIBLE_CLUE_WORDS with these matches %s' % (w, s_m[:10]))
            
        hint = len(POSSIBLE_WORDS) 
        hint_str = (', '.join(POSSIBLE_WORDS))[:200]
        print()
        player.warn(f"\n { hint } Possible: { hint_str }".strip())
        print()
        if 1:
            textfile = open("data/possible.txt", "w")
            for element in POSSIBLE_WORDS:
                textfile.write(element + "\n")
            textfile.close()
        return POSSIBLE_WORDS
    
    def play(self, player, solution, hints=False, clueGen=False, clueUse=False, auto=False):
        player.start()
        
        if clueGen:
            self.POSSIBLE_CLUES = self.generateClues(solution)

        round = 1
        while round <= self.ROUNDS:

            if round == 1: 
                self.POSSIBLE_WORDS = self.useClues(player) if clueUse else self.VALID_GUESSES
                print("POSSIBLE_WORDS = %s" % len(self.POSSIBLE_WORDS))
            
            guess = self.getPlayerGuess(player, round, auto)
            states = Game.check_guess(guess, solution)
            
            if hints: 
                self.POSSIBLE_WORDS = [w for w in self.POSSIBLE_WORDS if Game.is_same_response(guess, w, states)]
                hint = len(self.POSSIBLE_WORDS) 
                hint_str = (', '.join(self.POSSIBLE_WORDS))[:200]
                player.warn(f"\n{ hint } Possible: { hint_str }".strip())
           
            else:
                hint = -1

            player.handle_response(guess, states, hint)
            if states == Game.WIN_STATES:
                if hasattr(player, "handle_win"):
                    player.handle_win(round)
                return round

            round += 1

        if hasattr(player, "handle_loss"):
            player.handle_loss(solution)
        return None

    @staticmethod
    def read_clues(clue_list: list) -> List[List[LetterStates]]:
        transform = {
            'X':LetterStates.NOTPRESENT, 
            'Y':LetterStates.INCORRECTPOSITION, 
            'G':LetterStates.CORRECTPOSITION,
            '⬜':LetterStates.NOTPRESENT, 
            '🟨':LetterStates.INCORRECTPOSITION, 
            '🟩':LetterStates.CORRECTPOSITION, 
            '⬛':LetterStates.NOTPRESENT, 
            '🟨':LetterStates.INCORRECTPOSITION, 
            '🟩':LetterStates.CORRECTPOSITION, 
        }

        clue_states = []
        for c in clue_list:
            clue_states += [[ transform[l] for l in c ]]
        return clue_states

    @staticmethod
    def check_guess(guess: str, solution: str) -> List[LetterStates]:
        if guess == solution:
            return Game.WIN_STATES
        
        # https://mathspp.com/blog/solving-wordle-with-python
        # pool is set of letters in the solution available for INCORRECTPOSITION
        pool = {}
        for g, s in zip(guess, solution):
            if g == s:
                continue
            if s in pool:
                pool[s] += 1
            else: 
                pool[s] = 1

        states = []
        for guess_letter, solution_letter in zip(guess, solution):
            if guess_letter == solution_letter:
                states.append(LetterStates.CORRECTPOSITION)
            elif guess_letter in solution and guess_letter in pool and pool[guess_letter] > 0:
                states.append(LetterStates.INCORRECTPOSITION)
                pool[guess_letter] -= 1
            else:
                states.append(LetterStates.NOTPRESENT)
        return states

    @staticmethod
    def is_same_response(guess: str, solution: str, other_response: List[LetterStates]) -> bool:
        if guess == solution:
            return other_response == Game.WIN_STATES
        
        # https://mathspp.com/blog/solving-wordle-with-python
        # pool is set of letters in the solution available for INCORRECTPOSITION 
        pool = {}
        for g, s in zip(guess, solution):
            if g == s:
                continue
            if s in pool:
                pool[s] += 1
            else: 
                pool[s] = 1

        for guess_letter, solution_letter, other_state in zip(guess, solution, other_response):
            if guess_letter == solution_letter:
                if other_state != LetterStates.CORRECTPOSITION:
                    return False
            elif guess_letter in solution and guess_letter in pool and pool[guess_letter] > 0:
                if other_state != LetterStates.INCORRECTPOSITION:
                    return False
                pool[guess_letter] -= 1
            else:
                if other_state != LetterStates.NOTPRESENT:
                    return False
        
        return True
