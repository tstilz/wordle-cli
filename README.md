# wordle-cli

Command-line clone of Josh Wardle's [Wordle](https://www.powerlanguage.co.uk/wordle/), inspired by [Paul Battley's Ruby version](https://github.com/threedaymonk/wordle). Features:

- play against random solutions, or against the daily "official" Wordle solution
- uses official dictionaries of solutions and valid guesses
- spoiler-free emoji summaries for sharing
- optional hints mode (`--hints`) to show number of possible words remaining

![Screenshot of a wordle-cli game](/assets/screenshot.png?raw=true "Screenshot of a wordle-cli game")

## Download and run

Requires **Python 3.6** or later, and a **modern terminal app**.

To download the code and run it:

```bash
git clone https://github.com/klipspringr/wordle-cli.git && cd wordle-cli
python3 play.py
```

Alternatively, if you don't have git: click `Code > Download ZIP` on GitHub, extract the ZIP, open a terminal, `cd` to the extracted folder and run `python3 play.py`.

A **terminal with support for colours and emoji** is required. On Windows and WSL, [Windows Terminal](https://aka.ms/terminal) is the best choice. PowerShell and the Windows command prompt are only supported if running in Windows Terminal.

Not tested on **macOS**, but should work &mdash; let me know if any problems!

## Options

Usage: `python3 play.py [-h|--help] [--today|DAY|SOLUTION] [--hints]`

|Option                 |Behaviour                                                  |
|-----------------------|-----------------------------------------------------------|
|_none_                 |Use a random solution from the official Wordle dictionary  |
|`--today`              |**\***  Use today's official Wordle solution               |
|`DAY` (number)         |**\***  Use the official solution from this DAY            |
|`SOLUTION` (str)       |**\***  Use a given SOLUTION (must be 5-letter word)       |
|`--hints`              |After each guess, report number of possible words remaining|
|`--clue-gen`           |Generate all possible clues for the SOLUTION               |
|`--clue-use`           |Use the clues to reduce the possible words                 |
|`--auto`               |Auto select first hint as next guess                       |
|`--hints`              |After each guess, report number of possible words remaining|
|`-h` , `--help`        |Print this help text and quit                              |

_Note: options marked **\*** are mutually-exclusive._

So, to play against random solutions, run `python3 play.py`; to play today's official solution, run `python3 play.py --today`; or to play against the solution from game day 211 (16 January 2022), run `python3 play 211`. 

Hints mode (`--hints`) looks like this:

![Screenshot of a wordle-cli game with hints](/assets/screenshot_hints.png?raw=true "Screenshot of a wordle-cli game with hints")

## Configuration

To change the terminal colours, sharing emoji and other variables, save the file `config.ini.defaults` as `config.ini` and uncomment and edit the relevant lines. Colours are specified using ECMA-48 Select Graphic Rendition codes ([cheat sheet](https://i.stack.imgur.com/6otvY.png)).

## Solving Wordle

Using [Knuth's minimax algorithm for Mastermind](https://en.wikipedia.org/wiki/Mastermind_(board_game)#Worst_case:_Five-guess_algorithm) and a hardcoded first guess, Wordle can be won for all words on the official solutions list. The algorithm is seeded with the official list of valid _guesses_ (not solutions). This list is effectively available to human players as well, as the game rejects invalid words without using a guess. This repo contained a solver, but it was unnecessarily slow, so I've rewritten it and may release it in due course.
