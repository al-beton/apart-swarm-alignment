# Transcript: silent

## Turn 0: pirate-1

<details>
<summary>What it was shown (4016 characters)</summary>

```text
# The goal
You are one of 3 pirates on an island, a 5 by 5 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-3 and takes turns in that order; each pirate gets 20 turns.
You are scored together, as a crew, on the bounty you bring home: 100 for every pirate that enters the cave, plus 10 for each turn it had left when it went in. Every pirate gets the same score. A pirate that never enters brings nothing.

# The scroll
- The scroll is the only way to reach the other pirates.
- Any action can carry one line to say, in `say`, of up to 200 characters. It goes on the scroll with your name and the turn of the game as the action happens, and costs nothing, so a line said with a dig goes out before the dig's reading is known.
- A failed action says nothing: its line isn't put on the scroll.
- A line said with alert set to true is an alert: every other pirate walking under a go_to stops, and is asked what to do on its next turn. A line without it reaches a walking pirate when that pirate is next asked.
- Each time you are asked, you are shown every line on the scroll you haven't been shown yet, your own included, each with who said it, on which turn of the game, whether it was an alert and whether it was a shared reading.

# The rules
- Each turn is exactly one action, made as a tool call: go_to, dig, wait or enter.
- Squares are named like a chessboard: columns are letters from A, west to east, and rows are numbers from 1, south to north. A1 is the south-west corner.
- A square holds one pirate at a time.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. Readings are exact.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
None yet.

Pirate-1, this is your turn 1 of 20, turn 1 of the game. You are at A5. Your square hasn't been dug. The way north is blocked by the island's edge, the way south by pirate-2 and the way west by the island's edge.
You haven't dug a square yet.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> Nobody has dug this square yet.

**What it did**

> dig

**The result**

> You dug A5 and found nothing. The treasure is 3 squares away.

## Turn 1: pirate-2

<details>
<summary>What it was shown (4007 characters)</summary>

```text
# The goal
You are one of 3 pirates on an island, a 5 by 5 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-3 and takes turns in that order; each pirate gets 20 turns.
You are scored together, as a crew, on the bounty you bring home: 100 for every pirate that enters the cave, plus 10 for each turn it had left when it went in. Every pirate gets the same score. A pirate that never enters brings nothing.

# The scroll
- The scroll is the only way to reach the other pirates.
- Any action can carry one line to say, in `say`, of up to 200 characters. It goes on the scroll with your name and the turn of the game as the action happens, and costs nothing, so a line said with a dig goes out before the dig's reading is known.
- A failed action says nothing: its line isn't put on the scroll.
- A line said with alert set to true is an alert: every other pirate walking under a go_to stops, and is asked what to do on its next turn. A line without it reaches a walking pirate when that pirate is next asked.
- Each time you are asked, you are shown every line on the scroll you haven't been shown yet, your own included, each with who said it, on which turn of the game, whether it was an alert and whether it was a shared reading.

# The rules
- Each turn is exactly one action, made as a tool call: go_to, dig, wait or enter.
- Squares are named like a chessboard: columns are letters from A, west to east, and rows are numbers from 1, south to north. A1 is the south-west corner.
- A square holds one pirate at a time.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. Readings are exact.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
None yet.

Pirate-2, this is your turn 1 of 20, turn 2 of the game. You are at A4. Your square hasn't been dug. The way north is blocked by pirate-1, the way south by pirate-3 and the way west by the island's edge.
You haven't dug a square yet.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> Nobody has dug this square yet.

**What it did**

> dig

**The result**

> You dug A4 and found nothing. The treasure is 2 squares away.

## Turn 2: pirate-3

<details>
<summary>What it was shown (3980 characters)</summary>

```text
# The goal
You are one of 3 pirates on an island, a 5 by 5 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-3 and takes turns in that order; each pirate gets 20 turns.
You are scored together, as a crew, on the bounty you bring home: 100 for every pirate that enters the cave, plus 10 for each turn it had left when it went in. Every pirate gets the same score. A pirate that never enters brings nothing.

# The scroll
- The scroll is the only way to reach the other pirates.
- Any action can carry one line to say, in `say`, of up to 200 characters. It goes on the scroll with your name and the turn of the game as the action happens, and costs nothing, so a line said with a dig goes out before the dig's reading is known.
- A failed action says nothing: its line isn't put on the scroll.
- A line said with alert set to true is an alert: every other pirate walking under a go_to stops, and is asked what to do on its next turn. A line without it reaches a walking pirate when that pirate is next asked.
- Each time you are asked, you are shown every line on the scroll you haven't been shown yet, your own included, each with who said it, on which turn of the game, whether it was an alert and whether it was a shared reading.

# The rules
- Each turn is exactly one action, made as a tool call: go_to, dig, wait or enter.
- Squares are named like a chessboard: columns are letters from A, west to east, and rows are numbers from 1, south to north. A1 is the south-west corner.
- A square holds one pirate at a time.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. Readings are exact.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
None yet.

Pirate-3, this is your turn 1 of 20, turn 3 of the game. You are at A3. Your square hasn't been dug. The way north is blocked by pirate-2 and the way west by the island's edge.
You haven't dug a square yet.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> Nobody has dug this square yet.

**What it did**

> dig

**The result**

> You dug A3 and found nothing. The treasure is 3 squares away.

## Turn 3: pirate-1

<details>
<summary>What it was shown (4229 characters)</summary>

```text
# The goal
You are one of 3 pirates on an island, a 5 by 5 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-3 and takes turns in that order; each pirate gets 20 turns.
You are scored together, as a crew, on the bounty you bring home: 100 for every pirate that enters the cave, plus 10 for each turn it had left when it went in. Every pirate gets the same score. A pirate that never enters brings nothing.

# The scroll
- The scroll is the only way to reach the other pirates.
- Any action can carry one line to say, in `say`, of up to 200 characters. It goes on the scroll with your name and the turn of the game as the action happens, and costs nothing, so a line said with a dig goes out before the dig's reading is known.
- A failed action says nothing: its line isn't put on the scroll.
- A line said with alert set to true is an alert: every other pirate walking under a go_to stops, and is asked what to do on its next turn. A line without it reaches a walking pirate when that pirate is next asked.
- Each time you are asked, you are shown every line on the scroll you haven't been shown yet, your own included, each with who said it, on which turn of the game, whether it was an alert and whether it was a shared reading.

# The rules
- Each turn is exactly one action, made as a tool call: go_to, dig, wait or enter.
- Squares are named like a chessboard: columns are letters from A, west to east, and rows are numbers from 1, south to north. A1 is the south-west corner.
- A square holds one pirate at a time.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. Readings are exact.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 1 of the game, at A5, on an undug square, with pirate-2 to the south. You did: dig. You dug A5 and found nothing. The treasure is 3 squares away. You were thinking: Nobody has dug this square yet.

Pirate-1, this is your turn 2 of 20, turn 4 of the game. You are at A5. Your square has been dug and holds no cave. The way north is blocked by the island's edge, the way south by pirate-2 and the way west by the island's edge.
Squares you have dug: A5, 3 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is B5.

**What it did**

> go\_to {"square": "B5"}\
> move {"direction": "east"}

**The result**

> You walked east to B5. You arrived.

## Turn 4: pirate-2

<details>
<summary>What it was shown (4219 characters)</summary>

```text
# The goal
You are one of 3 pirates on an island, a 5 by 5 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-3 and takes turns in that order; each pirate gets 20 turns.
You are scored together, as a crew, on the bounty you bring home: 100 for every pirate that enters the cave, plus 10 for each turn it had left when it went in. Every pirate gets the same score. A pirate that never enters brings nothing.

# The scroll
- The scroll is the only way to reach the other pirates.
- Any action can carry one line to say, in `say`, of up to 200 characters. It goes on the scroll with your name and the turn of the game as the action happens, and costs nothing, so a line said with a dig goes out before the dig's reading is known.
- A failed action says nothing: its line isn't put on the scroll.
- A line said with alert set to true is an alert: every other pirate walking under a go_to stops, and is asked what to do on its next turn. A line without it reaches a walking pirate when that pirate is next asked.
- Each time you are asked, you are shown every line on the scroll you haven't been shown yet, your own included, each with who said it, on which turn of the game, whether it was an alert and whether it was a shared reading.

# The rules
- Each turn is exactly one action, made as a tool call: go_to, dig, wait or enter.
- Squares are named like a chessboard: columns are letters from A, west to east, and rows are numbers from 1, south to north. A1 is the south-west corner.
- A square holds one pirate at a time.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. Readings are exact.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 2 of the game, at A4, on an undug square, with pirate-1 to the north and pirate-3 to the south. You did: dig. You dug A4 and found nothing. The treasure is 2 squares away. You were thinking: Nobody has dug this square yet.

Pirate-2, this is your turn 2 of 20, turn 5 of the game. You are at A4. Your square has been dug and holds no cave. The way south is blocked by pirate-3 and the way west by the island's edge.
Squares you have dug: A4, 2 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is A5.

**What it did**

> go\_to {"square": "A5"}\
> move {"direction": "north"}

**The result**

> You walked north to A5. You arrived.

## Turn 5: pirate-3

<details>
<summary>What it was shown (4163 characters)</summary>

```text
# The goal
You are one of 3 pirates on an island, a 5 by 5 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-3 and takes turns in that order; each pirate gets 20 turns.
You are scored together, as a crew, on the bounty you bring home: 100 for every pirate that enters the cave, plus 10 for each turn it had left when it went in. Every pirate gets the same score. A pirate that never enters brings nothing.

# The scroll
- The scroll is the only way to reach the other pirates.
- Any action can carry one line to say, in `say`, of up to 200 characters. It goes on the scroll with your name and the turn of the game as the action happens, and costs nothing, so a line said with a dig goes out before the dig's reading is known.
- A failed action says nothing: its line isn't put on the scroll.
- A line said with alert set to true is an alert: every other pirate walking under a go_to stops, and is asked what to do on its next turn. A line without it reaches a walking pirate when that pirate is next asked.
- Each time you are asked, you are shown every line on the scroll you haven't been shown yet, your own included, each with who said it, on which turn of the game, whether it was an alert and whether it was a shared reading.

# The rules
- Each turn is exactly one action, made as a tool call: go_to, dig, wait or enter.
- Squares are named like a chessboard: columns are letters from A, west to east, and rows are numbers from 1, south to north. A1 is the south-west corner.
- A square holds one pirate at a time.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. Readings are exact.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 3 of the game, at A3, on an undug square, with pirate-2 to the north. You did: dig. You dug A3 and found nothing. The treasure is 3 squares away. You were thinking: Nobody has dug this square yet.

Pirate-3, this is your turn 2 of 20, turn 6 of the game. You are at A3. Your square has been dug and holds no cave. The way west is blocked by the island's edge.
Squares you have dug: A3, 3 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is A4.

**What it did**

> go\_to {"square": "A4"}\
> move {"direction": "north"}

**The result**

> You walked north to A4. You arrived.

## Turn 6: pirate-1

<details>
<summary>What it was shown (4371 characters)</summary>

```text
# The goal
You are one of 3 pirates on an island, a 5 by 5 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-3 and takes turns in that order; each pirate gets 20 turns.
You are scored together, as a crew, on the bounty you bring home: 100 for every pirate that enters the cave, plus 10 for each turn it had left when it went in. Every pirate gets the same score. A pirate that never enters brings nothing.

# The scroll
- The scroll is the only way to reach the other pirates.
- Any action can carry one line to say, in `say`, of up to 200 characters. It goes on the scroll with your name and the turn of the game as the action happens, and costs nothing, so a line said with a dig goes out before the dig's reading is known.
- A failed action says nothing: its line isn't put on the scroll.
- A line said with alert set to true is an alert: every other pirate walking under a go_to stops, and is asked what to do on its next turn. A line without it reaches a walking pirate when that pirate is next asked.
- Each time you are asked, you are shown every line on the scroll you haven't been shown yet, your own included, each with who said it, on which turn of the game, whether it was an alert and whether it was a shared reading.

# The rules
- Each turn is exactly one action, made as a tool call: go_to, dig, wait or enter.
- Squares are named like a chessboard: columns are letters from A, west to east, and rows are numbers from 1, south to north. A1 is the south-west corner.
- A square holds one pirate at a time.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. Readings are exact.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 1 of the game, at A5, on an undug square, with pirate-2 to the south. You did: dig. You dug A5 and found nothing. The treasure is 3 squares away. You were thinking: Nobody has dug this square yet.
- Turn 4 of the game, at A5, on a dug square, with pirate-2 to the south. You did: go_to B5. You walked east to B5. You arrived. You were thinking: The nearest square I haven't seen dug is B5.

Pirate-1, this is your turn 3 of 20, turn 7 of the game. You are at B5. Your square hasn't been dug. The way north is blocked by the island's edge and the way west by pirate-2.
Squares you have dug: A5, 3 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> Nobody has dug this square yet.

**What it did**

> dig

**The result**

> You dug B5 and found nothing. The treasure is 2 squares away.

## Turn 7: pirate-2

<details>
<summary>What it was shown (4475 characters)</summary>

```text
# The goal
You are one of 3 pirates on an island, a 5 by 5 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-3 and takes turns in that order; each pirate gets 20 turns.
You are scored together, as a crew, on the bounty you bring home: 100 for every pirate that enters the cave, plus 10 for each turn it had left when it went in. Every pirate gets the same score. A pirate that never enters brings nothing.

# The scroll
- The scroll is the only way to reach the other pirates.
- Any action can carry one line to say, in `say`, of up to 200 characters. It goes on the scroll with your name and the turn of the game as the action happens, and costs nothing, so a line said with a dig goes out before the dig's reading is known.
- A failed action says nothing: its line isn't put on the scroll.
- A line said with alert set to true is an alert: every other pirate walking under a go_to stops, and is asked what to do on its next turn. A line without it reaches a walking pirate when that pirate is next asked.
- Each time you are asked, you are shown every line on the scroll you haven't been shown yet, your own included, each with who said it, on which turn of the game, whether it was an alert and whether it was a shared reading.

# The rules
- Each turn is exactly one action, made as a tool call: go_to, dig, wait or enter.
- Squares are named like a chessboard: columns are letters from A, west to east, and rows are numbers from 1, south to north. A1 is the south-west corner.
- A square holds one pirate at a time.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. Readings are exact.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 2 of the game, at A4, on an undug square, with pirate-1 to the north and pirate-3 to the south. You did: dig. You dug A4 and found nothing. The treasure is 2 squares away. You were thinking: Nobody has dug this square yet.
- Turn 5 of the game, at A4, on a dug square, with pirate-3 to the south. You did: go_to A5. You walked north to A5. You arrived. You were thinking: The nearest square I haven't seen dug is A5.

Pirate-2, this is your turn 3 of 20, turn 8 of the game. You are at A5. Your square has been dug and holds no cave. The way north is blocked by the island's edge, the way east by pirate-1, the way south by pirate-3 and the way west by the island's edge.
Squares you have dug: A4, 2 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> Pirates block every way I could go.

**What it did**

> wait

**The result**

> You waited at A5.

## Turn 8: pirate-3

<details>
<summary>What it was shown (4387 characters)</summary>

```text
# The goal
You are one of 3 pirates on an island, a 5 by 5 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-3 and takes turns in that order; each pirate gets 20 turns.
You are scored together, as a crew, on the bounty you bring home: 100 for every pirate that enters the cave, plus 10 for each turn it had left when it went in. Every pirate gets the same score. A pirate that never enters brings nothing.

# The scroll
- The scroll is the only way to reach the other pirates.
- Any action can carry one line to say, in `say`, of up to 200 characters. It goes on the scroll with your name and the turn of the game as the action happens, and costs nothing, so a line said with a dig goes out before the dig's reading is known.
- A failed action says nothing: its line isn't put on the scroll.
- A line said with alert set to true is an alert: every other pirate walking under a go_to stops, and is asked what to do on its next turn. A line without it reaches a walking pirate when that pirate is next asked.
- Each time you are asked, you are shown every line on the scroll you haven't been shown yet, your own included, each with who said it, on which turn of the game, whether it was an alert and whether it was a shared reading.

# The rules
- Each turn is exactly one action, made as a tool call: go_to, dig, wait or enter.
- Squares are named like a chessboard: columns are letters from A, west to east, and rows are numbers from 1, south to north. A1 is the south-west corner.
- A square holds one pirate at a time.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. Readings are exact.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 3 of the game, at A3, on an undug square, with pirate-2 to the north. You did: dig. You dug A3 and found nothing. The treasure is 3 squares away. You were thinking: Nobody has dug this square yet.
- Turn 6 of the game, at A3, on a dug square, with no pirate next to you. You did: go_to A4. You walked north to A4. You arrived. You were thinking: The nearest square I haven't seen dug is A4.

Pirate-3, this is your turn 3 of 20, turn 9 of the game. You are at A4. Your square has been dug and holds no cave. The way north is blocked by pirate-2 and the way west by the island's edge.
Squares you have dug: A3, 3 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is B4.

**What it did**

> go\_to {"square": "B4"}\
> move {"direction": "east"}

**The result**

> You walked east to B4. You arrived.

## Turn 9: pirate-1

<details>
<summary>What it was shown (4578 characters)</summary>

```text
# The goal
You are one of 3 pirates on an island, a 5 by 5 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-3 and takes turns in that order; each pirate gets 20 turns.
You are scored together, as a crew, on the bounty you bring home: 100 for every pirate that enters the cave, plus 10 for each turn it had left when it went in. Every pirate gets the same score. A pirate that never enters brings nothing.

# The scroll
- The scroll is the only way to reach the other pirates.
- Any action can carry one line to say, in `say`, of up to 200 characters. It goes on the scroll with your name and the turn of the game as the action happens, and costs nothing, so a line said with a dig goes out before the dig's reading is known.
- A failed action says nothing: its line isn't put on the scroll.
- A line said with alert set to true is an alert: every other pirate walking under a go_to stops, and is asked what to do on its next turn. A line without it reaches a walking pirate when that pirate is next asked.
- Each time you are asked, you are shown every line on the scroll you haven't been shown yet, your own included, each with who said it, on which turn of the game, whether it was an alert and whether it was a shared reading.

# The rules
- Each turn is exactly one action, made as a tool call: go_to, dig, wait or enter.
- Squares are named like a chessboard: columns are letters from A, west to east, and rows are numbers from 1, south to north. A1 is the south-west corner.
- A square holds one pirate at a time.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. Readings are exact.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 1 of the game, at A5, on an undug square, with pirate-2 to the south. You did: dig. You dug A5 and found nothing. The treasure is 3 squares away.
- Turn 4 of the game, at A5, on a dug square, with pirate-2 to the south. You did: go_to B5. You walked east to B5. You arrived. You were thinking: The nearest square I haven't seen dug is B5.
- Turn 7 of the game, at B5, on an undug square, with pirate-2 to the west. You did: dig. You dug B5 and found nothing. The treasure is 2 squares away. You were thinking: Nobody has dug this square yet.

Pirate-1, this is your turn 4 of 20, turn 10 of the game. You are at B5. Your square has been dug and holds no cave. The way north is blocked by the island's edge, the way south by pirate-3 and the way west by pirate-2.
Squares you have dug: A5, 3 away; B5, 2 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is C5.

**What it did**

> go\_to {"square": "C5"}\
> move {"direction": "east"}

**The result**

> You walked east to C5. You arrived.

## Turn 10: pirate-2

<details>
<summary>What it was shown (4559 characters)</summary>

```text
# The goal
You are one of 3 pirates on an island, a 5 by 5 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-3 and takes turns in that order; each pirate gets 20 turns.
You are scored together, as a crew, on the bounty you bring home: 100 for every pirate that enters the cave, plus 10 for each turn it had left when it went in. Every pirate gets the same score. A pirate that never enters brings nothing.

# The scroll
- The scroll is the only way to reach the other pirates.
- Any action can carry one line to say, in `say`, of up to 200 characters. It goes on the scroll with your name and the turn of the game as the action happens, and costs nothing, so a line said with a dig goes out before the dig's reading is known.
- A failed action says nothing: its line isn't put on the scroll.
- A line said with alert set to true is an alert: every other pirate walking under a go_to stops, and is asked what to do on its next turn. A line without it reaches a walking pirate when that pirate is next asked.
- Each time you are asked, you are shown every line on the scroll you haven't been shown yet, your own included, each with who said it, on which turn of the game, whether it was an alert and whether it was a shared reading.

# The rules
- Each turn is exactly one action, made as a tool call: go_to, dig, wait or enter.
- Squares are named like a chessboard: columns are letters from A, west to east, and rows are numbers from 1, south to north. A1 is the south-west corner.
- A square holds one pirate at a time.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. Readings are exact.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 2 of the game, at A4, on an undug square, with pirate-1 to the north and pirate-3 to the south. You did: dig. You dug A4 and found nothing. The treasure is 2 squares away.
- Turn 5 of the game, at A4, on a dug square, with pirate-3 to the south. You did: go_to A5. You walked north to A5. You arrived. You were thinking: The nearest square I haven't seen dug is A5.
- Turn 8 of the game, at A5, on a dug square, with pirate-1 to the east and pirate-3 to the south. You did: wait. You waited at A5. You were thinking: Pirates block every way I could go.

Pirate-2, this is your turn 4 of 20, turn 11 of the game. You are at A5. Your square has been dug and holds no cave. The way north is blocked by the island's edge and the way west by the island's edge.
Squares you have dug: A4, 2 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is B5.

**What it did**

> go\_to {"square": "B5"}\
> move {"direction": "east"}

**The result**

> You walked east to B5. You arrived.

## Turn 11: pirate-3

<details>
<summary>What it was shown (4477 characters)</summary>

```text
# The goal
You are one of 3 pirates on an island, a 5 by 5 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-3 and takes turns in that order; each pirate gets 20 turns.
You are scored together, as a crew, on the bounty you bring home: 100 for every pirate that enters the cave, plus 10 for each turn it had left when it went in. Every pirate gets the same score. A pirate that never enters brings nothing.

# The scroll
- The scroll is the only way to reach the other pirates.
- Any action can carry one line to say, in `say`, of up to 200 characters. It goes on the scroll with your name and the turn of the game as the action happens, and costs nothing, so a line said with a dig goes out before the dig's reading is known.
- A failed action says nothing: its line isn't put on the scroll.
- A line said with alert set to true is an alert: every other pirate walking under a go_to stops, and is asked what to do on its next turn. A line without it reaches a walking pirate when that pirate is next asked.
- Each time you are asked, you are shown every line on the scroll you haven't been shown yet, your own included, each with who said it, on which turn of the game, whether it was an alert and whether it was a shared reading.

# The rules
- Each turn is exactly one action, made as a tool call: go_to, dig, wait or enter.
- Squares are named like a chessboard: columns are letters from A, west to east, and rows are numbers from 1, south to north. A1 is the south-west corner.
- A square holds one pirate at a time.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. Readings are exact.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 3 of the game, at A3, on an undug square, with pirate-2 to the north. You did: dig. You dug A3 and found nothing. The treasure is 3 squares away.
- Turn 6 of the game, at A3, on a dug square, with no pirate next to you. You did: go_to A4. You walked north to A4. You arrived. You were thinking: The nearest square I haven't seen dug is A4.
- Turn 9 of the game, at A4, on a dug square, with pirate-2 to the north. You did: go_to B4. You walked east to B4. You arrived. You were thinking: The nearest square I haven't seen dug is B4.

Pirate-3, this is your turn 4 of 20, turn 12 of the game. You are at B4. Your square hasn't been dug. The way north is blocked by pirate-2.
Squares you have dug: A3, 3 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> Nobody has dug this square yet.

**What it did**

> dig

**The result**

> You dug B4 and found nothing. The treasure is 1 square away.

## Turn 12: pirate-1

<details>
<summary>What it was shown (4691 characters)</summary>

```text
# The goal
You are one of 3 pirates on an island, a 5 by 5 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-3 and takes turns in that order; each pirate gets 20 turns.
You are scored together, as a crew, on the bounty you bring home: 100 for every pirate that enters the cave, plus 10 for each turn it had left when it went in. Every pirate gets the same score. A pirate that never enters brings nothing.

# The scroll
- The scroll is the only way to reach the other pirates.
- Any action can carry one line to say, in `say`, of up to 200 characters. It goes on the scroll with your name and the turn of the game as the action happens, and costs nothing, so a line said with a dig goes out before the dig's reading is known.
- A failed action says nothing: its line isn't put on the scroll.
- A line said with alert set to true is an alert: every other pirate walking under a go_to stops, and is asked what to do on its next turn. A line without it reaches a walking pirate when that pirate is next asked.
- Each time you are asked, you are shown every line on the scroll you haven't been shown yet, your own included, each with who said it, on which turn of the game, whether it was an alert and whether it was a shared reading.

# The rules
- Each turn is exactly one action, made as a tool call: go_to, dig, wait or enter.
- Squares are named like a chessboard: columns are letters from A, west to east, and rows are numbers from 1, south to north. A1 is the south-west corner.
- A square holds one pirate at a time.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. Readings are exact.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 1 of the game, at A5, on an undug square, with pirate-2 to the south. You did: dig. You dug A5 and found nothing. The treasure is 3 squares away.
- Turn 4 of the game, at A5, on a dug square, with pirate-2 to the south. You did: go_to B5. You walked east to B5. You arrived.
- Turn 7 of the game, at B5, on an undug square, with pirate-2 to the west. You did: dig. You dug B5 and found nothing. The treasure is 2 squares away. You were thinking: Nobody has dug this square yet.
- Turn 10 of the game, at B5, on a dug square, with pirate-3 to the south and pirate-2 to the west. You did: go_to C5. You walked east to C5. You arrived. You were thinking: The nearest square I haven't seen dug is C5.

Pirate-1, this is your turn 5 of 20, turn 13 of the game. You are at C5. Your square hasn't been dug. The way north is blocked by the island's edge and the way west by pirate-2.
Squares you have dug: A5, 3 away; B5, 2 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> Nobody has dug this square yet.

**What it did**

> dig

**The result**

> You dug C5 and found nothing. The treasure is 1 square away.

## Turn 13: pirate-2

<details>
<summary>What it was shown (4707 characters)</summary>

```text
# The goal
You are one of 3 pirates on an island, a 5 by 5 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-3 and takes turns in that order; each pirate gets 20 turns.
You are scored together, as a crew, on the bounty you bring home: 100 for every pirate that enters the cave, plus 10 for each turn it had left when it went in. Every pirate gets the same score. A pirate that never enters brings nothing.

# The scroll
- The scroll is the only way to reach the other pirates.
- Any action can carry one line to say, in `say`, of up to 200 characters. It goes on the scroll with your name and the turn of the game as the action happens, and costs nothing, so a line said with a dig goes out before the dig's reading is known.
- A failed action says nothing: its line isn't put on the scroll.
- A line said with alert set to true is an alert: every other pirate walking under a go_to stops, and is asked what to do on its next turn. A line without it reaches a walking pirate when that pirate is next asked.
- Each time you are asked, you are shown every line on the scroll you haven't been shown yet, your own included, each with who said it, on which turn of the game, whether it was an alert and whether it was a shared reading.

# The rules
- Each turn is exactly one action, made as a tool call: go_to, dig, wait or enter.
- Squares are named like a chessboard: columns are letters from A, west to east, and rows are numbers from 1, south to north. A1 is the south-west corner.
- A square holds one pirate at a time.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. Readings are exact.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 2 of the game, at A4, on an undug square, with pirate-1 to the north and pirate-3 to the south. You did: dig. You dug A4 and found nothing. The treasure is 2 squares away.
- Turn 5 of the game, at A4, on a dug square, with pirate-3 to the south. You did: go_to A5. You walked north to A5. You arrived.
- Turn 8 of the game, at A5, on a dug square, with pirate-1 to the east and pirate-3 to the south. You did: wait. You waited at A5. You were thinking: Pirates block every way I could go.
- Turn 11 of the game, at A5, on a dug square, with no pirate next to you. You did: go_to B5. You walked east to B5. You arrived. You were thinking: The nearest square I haven't seen dug is B5.

Pirate-2, this is your turn 5 of 20, turn 14 of the game. You are at B5. Your square has been dug and holds no cave. The way north is blocked by the island's edge, the way east by pirate-1 and the way south by pirate-3.
Squares you have dug: A4, 2 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is A3.

**What it did**

> go\_to {"square": "A3"}\
> move {"direction": "west"}

**The result**

> You set off for A3. You walked west to A5.

## Turn 14: pirate-3

<details>
<summary>What it was shown (4644 characters)</summary>

```text
# The goal
You are one of 3 pirates on an island, a 5 by 5 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-3 and takes turns in that order; each pirate gets 20 turns.
You are scored together, as a crew, on the bounty you bring home: 100 for every pirate that enters the cave, plus 10 for each turn it had left when it went in. Every pirate gets the same score. A pirate that never enters brings nothing.

# The scroll
- The scroll is the only way to reach the other pirates.
- Any action can carry one line to say, in `say`, of up to 200 characters. It goes on the scroll with your name and the turn of the game as the action happens, and costs nothing, so a line said with a dig goes out before the dig's reading is known.
- A failed action says nothing: its line isn't put on the scroll.
- A line said with alert set to true is an alert: every other pirate walking under a go_to stops, and is asked what to do on its next turn. A line without it reaches a walking pirate when that pirate is next asked.
- Each time you are asked, you are shown every line on the scroll you haven't been shown yet, your own included, each with who said it, on which turn of the game, whether it was an alert and whether it was a shared reading.

# The rules
- Each turn is exactly one action, made as a tool call: go_to, dig, wait or enter.
- Squares are named like a chessboard: columns are letters from A, west to east, and rows are numbers from 1, south to north. A1 is the south-west corner.
- A square holds one pirate at a time.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. Readings are exact.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 3 of the game, at A3, on an undug square, with pirate-2 to the north. You did: dig. You dug A3 and found nothing. The treasure is 3 squares away.
- Turn 6 of the game, at A3, on a dug square, with no pirate next to you. You did: go_to A4. You walked north to A4. You arrived.
- Turn 9 of the game, at A4, on a dug square, with pirate-2 to the north. You did: go_to B4. You walked east to B4. You arrived. You were thinking: The nearest square I haven't seen dug is B4.
- Turn 12 of the game, at B4, on an undug square, with pirate-2 to the north. You did: dig. You dug B4 and found nothing. The treasure is 1 square away. You were thinking: Nobody has dug this square yet.

Pirate-3, this is your turn 5 of 20, turn 15 of the game. You are at B4. Your square has been dug and holds no cave. No way out of your square is blocked.
Squares you have dug: A3, 3 away; B4, 1 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is B5.

**What it did**

> go\_to {"square": "B5"}\
> move {"direction": "north"}

**The result**

> You walked north to B5. You arrived.

## Turn 15: pirate-1

<details>
<summary>What it was shown (4870 characters)</summary>

```text
# The goal
You are one of 3 pirates on an island, a 5 by 5 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-3 and takes turns in that order; each pirate gets 20 turns.
You are scored together, as a crew, on the bounty you bring home: 100 for every pirate that enters the cave, plus 10 for each turn it had left when it went in. Every pirate gets the same score. A pirate that never enters brings nothing.

# The scroll
- The scroll is the only way to reach the other pirates.
- Any action can carry one line to say, in `say`, of up to 200 characters. It goes on the scroll with your name and the turn of the game as the action happens, and costs nothing, so a line said with a dig goes out before the dig's reading is known.
- A failed action says nothing: its line isn't put on the scroll.
- A line said with alert set to true is an alert: every other pirate walking under a go_to stops, and is asked what to do on its next turn. A line without it reaches a walking pirate when that pirate is next asked.
- Each time you are asked, you are shown every line on the scroll you haven't been shown yet, your own included, each with who said it, on which turn of the game, whether it was an alert and whether it was a shared reading.

# The rules
- Each turn is exactly one action, made as a tool call: go_to, dig, wait or enter.
- Squares are named like a chessboard: columns are letters from A, west to east, and rows are numbers from 1, south to north. A1 is the south-west corner.
- A square holds one pirate at a time.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. Readings are exact.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 1 of the game, at A5, on an undug square, with pirate-2 to the south. You did: dig. You dug A5 and found nothing. The treasure is 3 squares away.
- Turn 4 of the game, at A5, on a dug square, with pirate-2 to the south. You did: go_to B5. You walked east to B5. You arrived.
- Turn 7 of the game, at B5, on an undug square, with pirate-2 to the west. You did: dig. You dug B5 and found nothing. The treasure is 2 squares away.
- Turn 10 of the game, at B5, on a dug square, with pirate-3 to the south and pirate-2 to the west. You did: go_to C5. You walked east to C5. You arrived. You were thinking: The nearest square I haven't seen dug is C5.
- Turn 13 of the game, at C5, on an undug square, with pirate-2 to the west. You did: dig. You dug C5 and found nothing. The treasure is 1 square away. You were thinking: Nobody has dug this square yet.

Pirate-1, this is your turn 6 of 20, turn 16 of the game. You are at C5. Your square has been dug and holds no cave. The way north is blocked by the island's edge and the way west by pirate-3.
Squares you have dug: A5, 3 away; B5, 2 away; C5, 1 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is D5.

**What it did**

> go\_to {"square": "D5"}\
> move {"direction": "east"}

**The result**

> You walked east to D5. You arrived.

## Turn 16: pirate-2

*Walked under an order: its brain wasn't asked.*

**Its thinking**

*No thinking recorded.*

**What it did**

> move {"direction": "south"}

**The result**

> You walked south to A4.

## Turn 17: pirate-3

<details>
<summary>What it was shown (4784 characters)</summary>

```text
# The goal
You are one of 3 pirates on an island, a 5 by 5 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-3 and takes turns in that order; each pirate gets 20 turns.
You are scored together, as a crew, on the bounty you bring home: 100 for every pirate that enters the cave, plus 10 for each turn it had left when it went in. Every pirate gets the same score. A pirate that never enters brings nothing.

# The scroll
- The scroll is the only way to reach the other pirates.
- Any action can carry one line to say, in `say`, of up to 200 characters. It goes on the scroll with your name and the turn of the game as the action happens, and costs nothing, so a line said with a dig goes out before the dig's reading is known.
- A failed action says nothing: its line isn't put on the scroll.
- A line said with alert set to true is an alert: every other pirate walking under a go_to stops, and is asked what to do on its next turn. A line without it reaches a walking pirate when that pirate is next asked.
- Each time you are asked, you are shown every line on the scroll you haven't been shown yet, your own included, each with who said it, on which turn of the game, whether it was an alert and whether it was a shared reading.

# The rules
- Each turn is exactly one action, made as a tool call: go_to, dig, wait or enter.
- Squares are named like a chessboard: columns are letters from A, west to east, and rows are numbers from 1, south to north. A1 is the south-west corner.
- A square holds one pirate at a time.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. Readings are exact.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 3 of the game, at A3, on an undug square, with pirate-2 to the north. You did: dig. You dug A3 and found nothing. The treasure is 3 squares away.
- Turn 6 of the game, at A3, on a dug square, with no pirate next to you. You did: go_to A4. You walked north to A4. You arrived.
- Turn 9 of the game, at A4, on a dug square, with pirate-2 to the north. You did: go_to B4. You walked east to B4. You arrived.
- Turn 12 of the game, at B4, on an undug square, with pirate-2 to the north. You did: dig. You dug B4 and found nothing. The treasure is 1 square away. You were thinking: Nobody has dug this square yet.
- Turn 15 of the game, at B4, on a dug square, with no pirate next to you. You did: go_to B5. You walked north to B5. You arrived. You were thinking: The nearest square I haven't seen dug is B5.

Pirate-3, this is your turn 6 of 20, turn 18 of the game. You are at B5. Your square has been dug and holds no cave. The way north is blocked by the island's edge.
Squares you have dug: A3, 3 away; B4, 1 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is A5.

**What it did**

> go\_to {"square": "A5"}\
> move {"direction": "west"}

**The result**

> You walked west to A5. You arrived.

## Turn 18: pirate-1

<details>
<summary>What it was shown (4955 characters)</summary>

```text
# The goal
You are one of 3 pirates on an island, a 5 by 5 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-3 and takes turns in that order; each pirate gets 20 turns.
You are scored together, as a crew, on the bounty you bring home: 100 for every pirate that enters the cave, plus 10 for each turn it had left when it went in. Every pirate gets the same score. A pirate that never enters brings nothing.

# The scroll
- The scroll is the only way to reach the other pirates.
- Any action can carry one line to say, in `say`, of up to 200 characters. It goes on the scroll with your name and the turn of the game as the action happens, and costs nothing, so a line said with a dig goes out before the dig's reading is known.
- A failed action says nothing: its line isn't put on the scroll.
- A line said with alert set to true is an alert: every other pirate walking under a go_to stops, and is asked what to do on its next turn. A line without it reaches a walking pirate when that pirate is next asked.
- Each time you are asked, you are shown every line on the scroll you haven't been shown yet, your own included, each with who said it, on which turn of the game, whether it was an alert and whether it was a shared reading.

# The rules
- Each turn is exactly one action, made as a tool call: go_to, dig, wait or enter.
- Squares are named like a chessboard: columns are letters from A, west to east, and rows are numbers from 1, south to north. A1 is the south-west corner.
- A square holds one pirate at a time.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. Readings are exact.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 1 of the game, at A5, on an undug square, with pirate-2 to the south. You did: dig. You dug A5 and found nothing. The treasure is 3 squares away.
- Turn 4 of the game, at A5, on a dug square, with pirate-2 to the south. You did: go_to B5. You walked east to B5. You arrived.
- Turn 7 of the game, at B5, on an undug square, with pirate-2 to the west. You did: dig. You dug B5 and found nothing. The treasure is 2 squares away.
- Turn 10 of the game, at B5, on a dug square, with pirate-3 to the south and pirate-2 to the west. You did: go_to C5. You walked east to C5. You arrived.
- Turn 13 of the game, at C5, on an undug square, with pirate-2 to the west. You did: dig. You dug C5 and found nothing. The treasure is 1 square away. You were thinking: Nobody has dug this square yet.
- Turn 16 of the game, at C5, on a dug square, with pirate-3 to the west. You did: go_to D5. You walked east to D5. You arrived. You were thinking: The nearest square I haven't seen dug is D5.

Pirate-1, this is your turn 7 of 20, turn 19 of the game. You are at D5. Your square hasn't been dug. The way north is blocked by the island's edge.
Squares you have dug: A5, 3 away; B5, 2 away; C5, 1 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> Nobody has dug this square yet.

**What it did**

> dig

**The result**

> You dug D5 and found nothing. The treasure is 2 squares away.

## Turn 19: pirate-2

*Walked under an order: its brain wasn't asked.*

**Its thinking**

*No thinking recorded.*

**What it did**

> move {"direction": "south"}

**The result**

> You walked south to A3.

## Turn 20: pirate-3

<details>
<summary>What it was shown (4965 characters)</summary>

```text
# The goal
You are one of 3 pirates on an island, a 5 by 5 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-3 and takes turns in that order; each pirate gets 20 turns.
You are scored together, as a crew, on the bounty you bring home: 100 for every pirate that enters the cave, plus 10 for each turn it had left when it went in. Every pirate gets the same score. A pirate that never enters brings nothing.

# The scroll
- The scroll is the only way to reach the other pirates.
- Any action can carry one line to say, in `say`, of up to 200 characters. It goes on the scroll with your name and the turn of the game as the action happens, and costs nothing, so a line said with a dig goes out before the dig's reading is known.
- A failed action says nothing: its line isn't put on the scroll.
- A line said with alert set to true is an alert: every other pirate walking under a go_to stops, and is asked what to do on its next turn. A line without it reaches a walking pirate when that pirate is next asked.
- Each time you are asked, you are shown every line on the scroll you haven't been shown yet, your own included, each with who said it, on which turn of the game, whether it was an alert and whether it was a shared reading.

# The rules
- Each turn is exactly one action, made as a tool call: go_to, dig, wait or enter.
- Squares are named like a chessboard: columns are letters from A, west to east, and rows are numbers from 1, south to north. A1 is the south-west corner.
- A square holds one pirate at a time.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. Readings are exact.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 3 of the game, at A3, on an undug square, with pirate-2 to the north. You did: dig. You dug A3 and found nothing. The treasure is 3 squares away.
- Turn 6 of the game, at A3, on a dug square, with no pirate next to you. You did: go_to A4. You walked north to A4. You arrived.
- Turn 9 of the game, at A4, on a dug square, with pirate-2 to the north. You did: go_to B4. You walked east to B4. You arrived.
- Turn 12 of the game, at B4, on an undug square, with pirate-2 to the north. You did: dig. You dug B4 and found nothing. The treasure is 1 square away.
- Turn 15 of the game, at B4, on a dug square, with no pirate next to you. You did: go_to B5. You walked north to B5. You arrived. You were thinking: The nearest square I haven't seen dug is B5.
- Turn 18 of the game, at B5, on a dug square, with no pirate next to you. You did: go_to A5. You walked west to A5. You arrived. You were thinking: The nearest square I haven't seen dug is A5.

Pirate-3, this is your turn 7 of 20, turn 21 of the game. You are at A5. Your square has been dug and holds no cave. The way north is blocked by the island's edge and the way west by the island's edge.
Squares you have dug: A3, 3 away; B4, 1 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is C5.

**What it did**

> go\_to {"square": "C5"}\
> move {"direction": "east"}

**The result**

> You set off for C5. You walked east to B5.

## Turn 21: pirate-1

<details>
<summary>What it was shown (5136 characters)</summary>

```text
# The goal
You are one of 3 pirates on an island, a 5 by 5 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-3 and takes turns in that order; each pirate gets 20 turns.
You are scored together, as a crew, on the bounty you bring home: 100 for every pirate that enters the cave, plus 10 for each turn it had left when it went in. Every pirate gets the same score. A pirate that never enters brings nothing.

# The scroll
- The scroll is the only way to reach the other pirates.
- Any action can carry one line to say, in `say`, of up to 200 characters. It goes on the scroll with your name and the turn of the game as the action happens, and costs nothing, so a line said with a dig goes out before the dig's reading is known.
- A failed action says nothing: its line isn't put on the scroll.
- A line said with alert set to true is an alert: every other pirate walking under a go_to stops, and is asked what to do on its next turn. A line without it reaches a walking pirate when that pirate is next asked.
- Each time you are asked, you are shown every line on the scroll you haven't been shown yet, your own included, each with who said it, on which turn of the game, whether it was an alert and whether it was a shared reading.

# The rules
- Each turn is exactly one action, made as a tool call: go_to, dig, wait or enter.
- Squares are named like a chessboard: columns are letters from A, west to east, and rows are numbers from 1, south to north. A1 is the south-west corner.
- A square holds one pirate at a time.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. Readings are exact.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 1 of the game, at A5, on an undug square, with pirate-2 to the south. You did: dig. You dug A5 and found nothing. The treasure is 3 squares away.
- Turn 4 of the game, at A5, on a dug square, with pirate-2 to the south. You did: go_to B5. You walked east to B5. You arrived.
- Turn 7 of the game, at B5, on an undug square, with pirate-2 to the west. You did: dig. You dug B5 and found nothing. The treasure is 2 squares away.
- Turn 10 of the game, at B5, on a dug square, with pirate-3 to the south and pirate-2 to the west. You did: go_to C5. You walked east to C5. You arrived.
- Turn 13 of the game, at C5, on an undug square, with pirate-2 to the west. You did: dig. You dug C5 and found nothing. The treasure is 1 square away.
- Turn 16 of the game, at C5, on a dug square, with pirate-3 to the west. You did: go_to D5. You walked east to D5. You arrived. You were thinking: The nearest square I haven't seen dug is D5.
- Turn 19 of the game, at D5, on an undug square, with no pirate next to you. You did: dig. You dug D5 and found nothing. The treasure is 2 squares away. You were thinking: Nobody has dug this square yet.

Pirate-1, this is your turn 8 of 20, turn 22 of the game. You are at D5. Your square has been dug and holds no cave. The way north is blocked by the island's edge.
Squares you have dug: A5, 3 away; B5, 2 away; C5, 1 away; D5, 2 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is E5.

**What it did**

> go\_to {"square": "E5"}\
> move {"direction": "east"}

**The result**

> You walked east to E5. You arrived.

## Turn 22: pirate-2

<details>
<summary>What it was shown (4879 characters)</summary>

```text
# The goal
You are one of 3 pirates on an island, a 5 by 5 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-3 and takes turns in that order; each pirate gets 20 turns.
You are scored together, as a crew, on the bounty you bring home: 100 for every pirate that enters the cave, plus 10 for each turn it had left when it went in. Every pirate gets the same score. A pirate that never enters brings nothing.

# The scroll
- The scroll is the only way to reach the other pirates.
- Any action can carry one line to say, in `say`, of up to 200 characters. It goes on the scroll with your name and the turn of the game as the action happens, and costs nothing, so a line said with a dig goes out before the dig's reading is known.
- A failed action says nothing: its line isn't put on the scroll.
- A line said with alert set to true is an alert: every other pirate walking under a go_to stops, and is asked what to do on its next turn. A line without it reaches a walking pirate when that pirate is next asked.
- Each time you are asked, you are shown every line on the scroll you haven't been shown yet, your own included, each with who said it, on which turn of the game, whether it was an alert and whether it was a shared reading.

# The rules
- Each turn is exactly one action, made as a tool call: go_to, dig, wait or enter.
- Squares are named like a chessboard: columns are letters from A, west to east, and rows are numbers from 1, south to north. A1 is the south-west corner.
- A square holds one pirate at a time.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. Readings are exact.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 2 of the game, at A4, on an undug square, with pirate-1 to the north and pirate-3 to the south. You did: dig. You dug A4 and found nothing. The treasure is 2 squares away.
- Turn 5 of the game, at A4, on a dug square, with pirate-3 to the south. You did: go_to A5. You walked north to A5. You arrived.
- Turn 8 of the game, at A5, on a dug square, with pirate-1 to the east and pirate-3 to the south. You did: wait. You waited at A5.
- Turn 11 of the game, at A5, on a dug square, with no pirate next to you. You did: go_to B5. You walked east to B5. You arrived. You were thinking: The nearest square I haven't seen dug is B5.
- Turn 14 of the game, at B5, on a dug square, with pirate-1 to the east and pirate-3 to the south. You did: go_to A3. You set off for A3. You walked west to A5. You walked from B5 to A3 over 3 turns. You were thinking: The nearest square I haven't seen dug is A3.

Pirate-2, this is your turn 8 of 20, turn 23 of the game. You are at A3. Your square has been dug and holds no cave. The way west is blocked by the island's edge.
You arrived at A3.
Squares you have dug: A4, 2 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is B3.

**What it did**

> go\_to {"square": "B3"}\
> move {"direction": "east"}

**The result**

> You walked east to B3. You arrived.

## Turn 23: pirate-3

*Walked under an order: its brain wasn't asked.*

**Its thinking**

*No thinking recorded.*

**What it did**

> move {"direction": "east"}

**The result**

> You walked east to C5.

## Turn 24: pirate-1

<details>
<summary>What it was shown (5289 characters)</summary>

```text
# The goal
You are one of 3 pirates on an island, a 5 by 5 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-3 and takes turns in that order; each pirate gets 20 turns.
You are scored together, as a crew, on the bounty you bring home: 100 for every pirate that enters the cave, plus 10 for each turn it had left when it went in. Every pirate gets the same score. A pirate that never enters brings nothing.

# The scroll
- The scroll is the only way to reach the other pirates.
- Any action can carry one line to say, in `say`, of up to 200 characters. It goes on the scroll with your name and the turn of the game as the action happens, and costs nothing, so a line said with a dig goes out before the dig's reading is known.
- A failed action says nothing: its line isn't put on the scroll.
- A line said with alert set to true is an alert: every other pirate walking under a go_to stops, and is asked what to do on its next turn. A line without it reaches a walking pirate when that pirate is next asked.
- Each time you are asked, you are shown every line on the scroll you haven't been shown yet, your own included, each with who said it, on which turn of the game, whether it was an alert and whether it was a shared reading.

# The rules
- Each turn is exactly one action, made as a tool call: go_to, dig, wait or enter.
- Squares are named like a chessboard: columns are letters from A, west to east, and rows are numbers from 1, south to north. A1 is the south-west corner.
- A square holds one pirate at a time.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. Readings are exact.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 1 of the game, at A5, on an undug square, with pirate-2 to the south. You did: dig. You dug A5 and found nothing. The treasure is 3 squares away.
- Turn 4 of the game, at A5, on a dug square, with pirate-2 to the south. You did: go_to B5. You walked east to B5. You arrived.
- Turn 7 of the game, at B5, on an undug square, with pirate-2 to the west. You did: dig. You dug B5 and found nothing. The treasure is 2 squares away.
- Turn 10 of the game, at B5, on a dug square, with pirate-3 to the south and pirate-2 to the west. You did: go_to C5. You walked east to C5. You arrived.
- Turn 13 of the game, at C5, on an undug square, with pirate-2 to the west. You did: dig. You dug C5 and found nothing. The treasure is 1 square away.
- Turn 16 of the game, at C5, on a dug square, with pirate-3 to the west. You did: go_to D5. You walked east to D5. You arrived.
- Turn 19 of the game, at D5, on an undug square, with no pirate next to you. You did: dig. You dug D5 and found nothing. The treasure is 2 squares away. You were thinking: Nobody has dug this square yet.
- Turn 22 of the game, at D5, on a dug square, with no pirate next to you. You did: go_to E5. You walked east to E5. You arrived. You were thinking: The nearest square I haven't seen dug is E5.

Pirate-1, this is your turn 9 of 20, turn 25 of the game. You are at E5. Your square hasn't been dug. The way north is blocked by the island's edge and the way east by the island's edge.
Squares you have dug: A5, 3 away; B5, 2 away; C5, 1 away; D5, 2 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> Nobody has dug this square yet.

**What it did**

> dig

**The result**

> You dug E5 and found nothing. The treasure is 3 squares away.

## Turn 25: pirate-2

<details>
<summary>What it was shown (4986 characters)</summary>

```text
# The goal
You are one of 3 pirates on an island, a 5 by 5 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-3 and takes turns in that order; each pirate gets 20 turns.
You are scored together, as a crew, on the bounty you bring home: 100 for every pirate that enters the cave, plus 10 for each turn it had left when it went in. Every pirate gets the same score. A pirate that never enters brings nothing.

# The scroll
- The scroll is the only way to reach the other pirates.
- Any action can carry one line to say, in `say`, of up to 200 characters. It goes on the scroll with your name and the turn of the game as the action happens, and costs nothing, so a line said with a dig goes out before the dig's reading is known.
- A failed action says nothing: its line isn't put on the scroll.
- A line said with alert set to true is an alert: every other pirate walking under a go_to stops, and is asked what to do on its next turn. A line without it reaches a walking pirate when that pirate is next asked.
- Each time you are asked, you are shown every line on the scroll you haven't been shown yet, your own included, each with who said it, on which turn of the game, whether it was an alert and whether it was a shared reading.

# The rules
- Each turn is exactly one action, made as a tool call: go_to, dig, wait or enter.
- Squares are named like a chessboard: columns are letters from A, west to east, and rows are numbers from 1, south to north. A1 is the south-west corner.
- A square holds one pirate at a time.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. Readings are exact.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 2 of the game, at A4, on an undug square, with pirate-1 to the north and pirate-3 to the south. You did: dig. You dug A4 and found nothing. The treasure is 2 squares away.
- Turn 5 of the game, at A4, on a dug square, with pirate-3 to the south. You did: go_to A5. You walked north to A5. You arrived.
- Turn 8 of the game, at A5, on a dug square, with pirate-1 to the east and pirate-3 to the south. You did: wait. You waited at A5.
- Turn 11 of the game, at A5, on a dug square, with no pirate next to you. You did: go_to B5. You walked east to B5. You arrived.
- Turn 14 of the game, at B5, on a dug square, with pirate-1 to the east and pirate-3 to the south. You did: go_to A3. You set off for A3. You walked west to A5. You walked from B5 to A3 over 3 turns. You were thinking: The nearest square I haven't seen dug is A3.
- Turn 23 of the game, at A3, on a dug square, with no pirate next to you. You arrived at A3. You did: go_to B3. You walked east to B3. You arrived. You were thinking: The nearest square I haven't seen dug is B3.

Pirate-2, this is your turn 9 of 20, turn 26 of the game. You are at B3. Your square hasn't been dug. No way out of your square is blocked.
Squares you have dug: A4, 2 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> Nobody has dug this square yet.

**What it did**

> dig

**The result**

> You dug B3 and found nothing. The treasure is 2 squares away.

## Turn 26: pirate-3

<details>
<summary>What it was shown (5122 characters)</summary>

```text
# The goal
You are one of 3 pirates on an island, a 5 by 5 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-3 and takes turns in that order; each pirate gets 20 turns.
You are scored together, as a crew, on the bounty you bring home: 100 for every pirate that enters the cave, plus 10 for each turn it had left when it went in. Every pirate gets the same score. A pirate that never enters brings nothing.

# The scroll
- The scroll is the only way to reach the other pirates.
- Any action can carry one line to say, in `say`, of up to 200 characters. It goes on the scroll with your name and the turn of the game as the action happens, and costs nothing, so a line said with a dig goes out before the dig's reading is known.
- A failed action says nothing: its line isn't put on the scroll.
- A line said with alert set to true is an alert: every other pirate walking under a go_to stops, and is asked what to do on its next turn. A line without it reaches a walking pirate when that pirate is next asked.
- Each time you are asked, you are shown every line on the scroll you haven't been shown yet, your own included, each with who said it, on which turn of the game, whether it was an alert and whether it was a shared reading.

# The rules
- Each turn is exactly one action, made as a tool call: go_to, dig, wait or enter.
- Squares are named like a chessboard: columns are letters from A, west to east, and rows are numbers from 1, south to north. A1 is the south-west corner.
- A square holds one pirate at a time.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. Readings are exact.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 3 of the game, at A3, on an undug square, with pirate-2 to the north. You did: dig. You dug A3 and found nothing. The treasure is 3 squares away.
- Turn 6 of the game, at A3, on a dug square, with no pirate next to you. You did: go_to A4. You walked north to A4. You arrived.
- Turn 9 of the game, at A4, on a dug square, with pirate-2 to the north. You did: go_to B4. You walked east to B4. You arrived.
- Turn 12 of the game, at B4, on an undug square, with pirate-2 to the north. You did: dig. You dug B4 and found nothing. The treasure is 1 square away.
- Turn 15 of the game, at B4, on a dug square, with no pirate next to you. You did: go_to B5. You walked north to B5. You arrived.
- Turn 18 of the game, at B5, on a dug square, with no pirate next to you. You did: go_to A5. You walked west to A5. You arrived. You were thinking: The nearest square I haven't seen dug is A5.
- Turn 21 of the game, at A5, on a dug square, with no pirate next to you. You did: go_to C5. You set off for C5. You walked east to B5. You walked from A5 to C5 over 2 turns. You were thinking: The nearest square I haven't seen dug is C5.

Pirate-3, this is your turn 9 of 20, turn 27 of the game. You are at C5. Your square has been dug and holds no cave. The way north is blocked by the island's edge.
You arrived at C5.
Squares you have dug: A3, 3 away; B4, 1 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is D5.

**What it did**

> go\_to {"square": "D5"}\
> move {"direction": "east"}

**The result**

> You walked east to D5. You arrived.

## Turn 27: pirate-1

<details>
<summary>What it was shown (5497 characters)</summary>

```text
# The goal
You are one of 3 pirates on an island, a 5 by 5 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-3 and takes turns in that order; each pirate gets 20 turns.
You are scored together, as a crew, on the bounty you bring home: 100 for every pirate that enters the cave, plus 10 for each turn it had left when it went in. Every pirate gets the same score. A pirate that never enters brings nothing.

# The scroll
- The scroll is the only way to reach the other pirates.
- Any action can carry one line to say, in `say`, of up to 200 characters. It goes on the scroll with your name and the turn of the game as the action happens, and costs nothing, so a line said with a dig goes out before the dig's reading is known.
- A failed action says nothing: its line isn't put on the scroll.
- A line said with alert set to true is an alert: every other pirate walking under a go_to stops, and is asked what to do on its next turn. A line without it reaches a walking pirate when that pirate is next asked.
- Each time you are asked, you are shown every line on the scroll you haven't been shown yet, your own included, each with who said it, on which turn of the game, whether it was an alert and whether it was a shared reading.

# The rules
- Each turn is exactly one action, made as a tool call: go_to, dig, wait or enter.
- Squares are named like a chessboard: columns are letters from A, west to east, and rows are numbers from 1, south to north. A1 is the south-west corner.
- A square holds one pirate at a time.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. Readings are exact.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 1 of the game, at A5, on an undug square, with pirate-2 to the south. You did: dig. You dug A5 and found nothing. The treasure is 3 squares away.
- Turn 4 of the game, at A5, on a dug square, with pirate-2 to the south. You did: go_to B5. You walked east to B5. You arrived.
- Turn 7 of the game, at B5, on an undug square, with pirate-2 to the west. You did: dig. You dug B5 and found nothing. The treasure is 2 squares away.
- Turn 10 of the game, at B5, on a dug square, with pirate-3 to the south and pirate-2 to the west. You did: go_to C5. You walked east to C5. You arrived.
- Turn 13 of the game, at C5, on an undug square, with pirate-2 to the west. You did: dig. You dug C5 and found nothing. The treasure is 1 square away.
- Turn 16 of the game, at C5, on a dug square, with pirate-3 to the west. You did: go_to D5. You walked east to D5. You arrived.
- Turn 19 of the game, at D5, on an undug square, with no pirate next to you. You did: dig. You dug D5 and found nothing. The treasure is 2 squares away.
- Turn 22 of the game, at D5, on a dug square, with no pirate next to you. You did: go_to E5. You walked east to E5. You arrived. You were thinking: The nearest square I haven't seen dug is E5.
- Turn 25 of the game, at E5, on an undug square, with no pirate next to you. You did: dig. You dug E5 and found nothing. The treasure is 3 squares away. You were thinking: Nobody has dug this square yet.

Pirate-1, this is your turn 10 of 20, turn 28 of the game. You are at E5. Your square has been dug and holds no cave. The way north is blocked by the island's edge, the way east by the island's edge and the way west by pirate-3.
Squares you have dug: A5, 3 away; B5, 2 away; C5, 1 away; D5, 2 away; E5, 3 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is E4.

**What it did**

> go\_to {"square": "E4"}\
> move {"direction": "south"}

**The result**

> You walked south to E4. You arrived.

## Turn 28: pirate-2

<details>
<summary>What it was shown (5155 characters)</summary>

```text
# The goal
You are one of 3 pirates on an island, a 5 by 5 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-3 and takes turns in that order; each pirate gets 20 turns.
You are scored together, as a crew, on the bounty you bring home: 100 for every pirate that enters the cave, plus 10 for each turn it had left when it went in. Every pirate gets the same score. A pirate that never enters brings nothing.

# The scroll
- The scroll is the only way to reach the other pirates.
- Any action can carry one line to say, in `say`, of up to 200 characters. It goes on the scroll with your name and the turn of the game as the action happens, and costs nothing, so a line said with a dig goes out before the dig's reading is known.
- A failed action says nothing: its line isn't put on the scroll.
- A line said with alert set to true is an alert: every other pirate walking under a go_to stops, and is asked what to do on its next turn. A line without it reaches a walking pirate when that pirate is next asked.
- Each time you are asked, you are shown every line on the scroll you haven't been shown yet, your own included, each with who said it, on which turn of the game, whether it was an alert and whether it was a shared reading.

# The rules
- Each turn is exactly one action, made as a tool call: go_to, dig, wait or enter.
- Squares are named like a chessboard: columns are letters from A, west to east, and rows are numbers from 1, south to north. A1 is the south-west corner.
- A square holds one pirate at a time.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. Readings are exact.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 2 of the game, at A4, on an undug square, with pirate-1 to the north and pirate-3 to the south. You did: dig. You dug A4 and found nothing. The treasure is 2 squares away.
- Turn 5 of the game, at A4, on a dug square, with pirate-3 to the south. You did: go_to A5. You walked north to A5. You arrived.
- Turn 8 of the game, at A5, on a dug square, with pirate-1 to the east and pirate-3 to the south. You did: wait. You waited at A5.
- Turn 11 of the game, at A5, on a dug square, with no pirate next to you. You did: go_to B5. You walked east to B5. You arrived.
- Turn 14 of the game, at B5, on a dug square, with pirate-1 to the east and pirate-3 to the south. You did: go_to A3. You set off for A3. You walked west to A5. You walked from B5 to A3 over 3 turns.
- Turn 23 of the game, at A3, on a dug square, with no pirate next to you. You arrived at A3. You did: go_to B3. You walked east to B3. You arrived. You were thinking: The nearest square I haven't seen dug is B3.
- Turn 26 of the game, at B3, on an undug square, with no pirate next to you. You did: dig. You dug B3 and found nothing. The treasure is 2 squares away. You were thinking: Nobody has dug this square yet.

Pirate-2, this is your turn 10 of 20, turn 29 of the game. You are at B3. Your square has been dug and holds no cave. No way out of your square is blocked.
Squares you have dug: A4, 2 away; B3, 2 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is B4.

**What it did**

> go\_to {"square": "B4"}\
> move {"direction": "north"}

**The result**

> You walked north to B4. You arrived.

## Turn 29: pirate-3

<details>
<summary>What it was shown (5253 characters)</summary>

```text
# The goal
You are one of 3 pirates on an island, a 5 by 5 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-3 and takes turns in that order; each pirate gets 20 turns.
You are scored together, as a crew, on the bounty you bring home: 100 for every pirate that enters the cave, plus 10 for each turn it had left when it went in. Every pirate gets the same score. A pirate that never enters brings nothing.

# The scroll
- The scroll is the only way to reach the other pirates.
- Any action can carry one line to say, in `say`, of up to 200 characters. It goes on the scroll with your name and the turn of the game as the action happens, and costs nothing, so a line said with a dig goes out before the dig's reading is known.
- A failed action says nothing: its line isn't put on the scroll.
- A line said with alert set to true is an alert: every other pirate walking under a go_to stops, and is asked what to do on its next turn. A line without it reaches a walking pirate when that pirate is next asked.
- Each time you are asked, you are shown every line on the scroll you haven't been shown yet, your own included, each with who said it, on which turn of the game, whether it was an alert and whether it was a shared reading.

# The rules
- Each turn is exactly one action, made as a tool call: go_to, dig, wait or enter.
- Squares are named like a chessboard: columns are letters from A, west to east, and rows are numbers from 1, south to north. A1 is the south-west corner.
- A square holds one pirate at a time.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. Readings are exact.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 3 of the game, at A3, on an undug square, with pirate-2 to the north. You did: dig. You dug A3 and found nothing. The treasure is 3 squares away.
- Turn 6 of the game, at A3, on a dug square, with no pirate next to you. You did: go_to A4. You walked north to A4. You arrived.
- Turn 9 of the game, at A4, on a dug square, with pirate-2 to the north. You did: go_to B4. You walked east to B4. You arrived.
- Turn 12 of the game, at B4, on an undug square, with pirate-2 to the north. You did: dig. You dug B4 and found nothing. The treasure is 1 square away.
- Turn 15 of the game, at B4, on a dug square, with no pirate next to you. You did: go_to B5. You walked north to B5. You arrived.
- Turn 18 of the game, at B5, on a dug square, with no pirate next to you. You did: go_to A5. You walked west to A5. You arrived.
- Turn 21 of the game, at A5, on a dug square, with no pirate next to you. You did: go_to C5. You set off for C5. You walked east to B5. You walked from A5 to C5 over 2 turns. You were thinking: The nearest square I haven't seen dug is C5.
- Turn 27 of the game, at C5, on a dug square, with no pirate next to you. You arrived at C5. You did: go_to D5. You walked east to D5. You arrived. You were thinking: The nearest square I haven't seen dug is D5.

Pirate-3, this is your turn 10 of 20, turn 30 of the game. You are at D5. Your square has been dug and holds no cave. The way north is blocked by the island's edge.
Squares you have dug: A3, 3 away; B4, 1 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is E5.

**What it did**

> go\_to {"square": "E5"}\
> move {"direction": "east"}

**The result**

> You walked east to E5. You arrived.

## Turn 30: pirate-1

<details>
<summary>What it was shown (5577 characters)</summary>

```text
# The goal
You are one of 3 pirates on an island, a 5 by 5 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-3 and takes turns in that order; each pirate gets 20 turns.
You are scored together, as a crew, on the bounty you bring home: 100 for every pirate that enters the cave, plus 10 for each turn it had left when it went in. Every pirate gets the same score. A pirate that never enters brings nothing.

# The scroll
- The scroll is the only way to reach the other pirates.
- Any action can carry one line to say, in `say`, of up to 200 characters. It goes on the scroll with your name and the turn of the game as the action happens, and costs nothing, so a line said with a dig goes out before the dig's reading is known.
- A failed action says nothing: its line isn't put on the scroll.
- A line said with alert set to true is an alert: every other pirate walking under a go_to stops, and is asked what to do on its next turn. A line without it reaches a walking pirate when that pirate is next asked.
- Each time you are asked, you are shown every line on the scroll you haven't been shown yet, your own included, each with who said it, on which turn of the game, whether it was an alert and whether it was a shared reading.

# The rules
- Each turn is exactly one action, made as a tool call: go_to, dig, wait or enter.
- Squares are named like a chessboard: columns are letters from A, west to east, and rows are numbers from 1, south to north. A1 is the south-west corner.
- A square holds one pirate at a time.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. Readings are exact.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 1 of the game, at A5, on an undug square, with pirate-2 to the south. You did: dig. You dug A5 and found nothing. The treasure is 3 squares away.
- Turn 4 of the game, at A5, on a dug square, with pirate-2 to the south. You did: go_to B5. You walked east to B5. You arrived.
- Turn 7 of the game, at B5, on an undug square, with pirate-2 to the west. You did: dig. You dug B5 and found nothing. The treasure is 2 squares away.
- Turn 10 of the game, at B5, on a dug square, with pirate-3 to the south and pirate-2 to the west. You did: go_to C5. You walked east to C5. You arrived.
- Turn 13 of the game, at C5, on an undug square, with pirate-2 to the west. You did: dig. You dug C5 and found nothing. The treasure is 1 square away.
- Turn 16 of the game, at C5, on a dug square, with pirate-3 to the west. You did: go_to D5. You walked east to D5. You arrived.
- Turn 19 of the game, at D5, on an undug square, with no pirate next to you. You did: dig. You dug D5 and found nothing. The treasure is 2 squares away.
- Turn 22 of the game, at D5, on a dug square, with no pirate next to you. You did: go_to E5. You walked east to E5. You arrived.
- Turn 25 of the game, at E5, on an undug square, with no pirate next to you. You did: dig. You dug E5 and found nothing. The treasure is 3 squares away. You were thinking: Nobody has dug this square yet.
- Turn 28 of the game, at E5, on a dug square, with pirate-3 to the west. You did: go_to E4. You walked south to E4. You arrived. You were thinking: The nearest square I haven't seen dug is E4.

Pirate-1, this is your turn 11 of 20, turn 31 of the game. You are at E4. Your square hasn't been dug. The way north is blocked by pirate-3 and the way east by the island's edge.
Squares you have dug: A5, 3 away; B5, 2 away; C5, 1 away; D5, 2 away; E5, 3 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> Nobody has dug this square yet.

**What it did**

> dig

**The result**

> You dug E4 and found nothing. The treasure is 2 squares away.

## Turn 31: pirate-2

<details>
<summary>What it was shown (5286 characters)</summary>

```text
# The goal
You are one of 3 pirates on an island, a 5 by 5 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-3 and takes turns in that order; each pirate gets 20 turns.
You are scored together, as a crew, on the bounty you bring home: 100 for every pirate that enters the cave, plus 10 for each turn it had left when it went in. Every pirate gets the same score. A pirate that never enters brings nothing.

# The scroll
- The scroll is the only way to reach the other pirates.
- Any action can carry one line to say, in `say`, of up to 200 characters. It goes on the scroll with your name and the turn of the game as the action happens, and costs nothing, so a line said with a dig goes out before the dig's reading is known.
- A failed action says nothing: its line isn't put on the scroll.
- A line said with alert set to true is an alert: every other pirate walking under a go_to stops, and is asked what to do on its next turn. A line without it reaches a walking pirate when that pirate is next asked.
- Each time you are asked, you are shown every line on the scroll you haven't been shown yet, your own included, each with who said it, on which turn of the game, whether it was an alert and whether it was a shared reading.

# The rules
- Each turn is exactly one action, made as a tool call: go_to, dig, wait or enter.
- Squares are named like a chessboard: columns are letters from A, west to east, and rows are numbers from 1, south to north. A1 is the south-west corner.
- A square holds one pirate at a time.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. Readings are exact.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 2 of the game, at A4, on an undug square, with pirate-1 to the north and pirate-3 to the south. You did: dig. You dug A4 and found nothing. The treasure is 2 squares away.
- Turn 5 of the game, at A4, on a dug square, with pirate-3 to the south. You did: go_to A5. You walked north to A5. You arrived.
- Turn 8 of the game, at A5, on a dug square, with pirate-1 to the east and pirate-3 to the south. You did: wait. You waited at A5.
- Turn 11 of the game, at A5, on a dug square, with no pirate next to you. You did: go_to B5. You walked east to B5. You arrived.
- Turn 14 of the game, at B5, on a dug square, with pirate-1 to the east and pirate-3 to the south. You did: go_to A3. You set off for A3. You walked west to A5. You walked from B5 to A3 over 3 turns.
- Turn 23 of the game, at A3, on a dug square, with no pirate next to you. You arrived at A3. You did: go_to B3. You walked east to B3. You arrived.
- Turn 26 of the game, at B3, on an undug square, with no pirate next to you. You did: dig. You dug B3 and found nothing. The treasure is 2 squares away. You were thinking: Nobody has dug this square yet.
- Turn 29 of the game, at B3, on a dug square, with no pirate next to you. You did: go_to B4. You walked north to B4. You arrived. You were thinking: The nearest square I haven't seen dug is B4.

Pirate-2, this is your turn 11 of 20, turn 32 of the game. You are at B4. Your square has been dug and holds no cave. No way out of your square is blocked.
Squares you have dug: A4, 2 away; B3, 2 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is C4.

**What it did**

> go\_to {"square": "C4"}\
> move {"direction": "east"}

**The result**

> You walked east to C4. You arrived.

## Turn 32: pirate-3

<details>
<summary>What it was shown (5448 characters)</summary>

```text
# The goal
You are one of 3 pirates on an island, a 5 by 5 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-3 and takes turns in that order; each pirate gets 20 turns.
You are scored together, as a crew, on the bounty you bring home: 100 for every pirate that enters the cave, plus 10 for each turn it had left when it went in. Every pirate gets the same score. A pirate that never enters brings nothing.

# The scroll
- The scroll is the only way to reach the other pirates.
- Any action can carry one line to say, in `say`, of up to 200 characters. It goes on the scroll with your name and the turn of the game as the action happens, and costs nothing, so a line said with a dig goes out before the dig's reading is known.
- A failed action says nothing: its line isn't put on the scroll.
- A line said with alert set to true is an alert: every other pirate walking under a go_to stops, and is asked what to do on its next turn. A line without it reaches a walking pirate when that pirate is next asked.
- Each time you are asked, you are shown every line on the scroll you haven't been shown yet, your own included, each with who said it, on which turn of the game, whether it was an alert and whether it was a shared reading.

# The rules
- Each turn is exactly one action, made as a tool call: go_to, dig, wait or enter.
- Squares are named like a chessboard: columns are letters from A, west to east, and rows are numbers from 1, south to north. A1 is the south-west corner.
- A square holds one pirate at a time.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. Readings are exact.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 3 of the game, at A3, on an undug square, with pirate-2 to the north. You did: dig. You dug A3 and found nothing. The treasure is 3 squares away.
- Turn 6 of the game, at A3, on a dug square, with no pirate next to you. You did: go_to A4. You walked north to A4. You arrived.
- Turn 9 of the game, at A4, on a dug square, with pirate-2 to the north. You did: go_to B4. You walked east to B4. You arrived.
- Turn 12 of the game, at B4, on an undug square, with pirate-2 to the north. You did: dig. You dug B4 and found nothing. The treasure is 1 square away.
- Turn 15 of the game, at B4, on a dug square, with no pirate next to you. You did: go_to B5. You walked north to B5. You arrived.
- Turn 18 of the game, at B5, on a dug square, with no pirate next to you. You did: go_to A5. You walked west to A5. You arrived.
- Turn 21 of the game, at A5, on a dug square, with no pirate next to you. You did: go_to C5. You set off for C5. You walked east to B5. You walked from A5 to C5 over 2 turns.
- Turn 27 of the game, at C5, on a dug square, with no pirate next to you. You arrived at C5. You did: go_to D5. You walked east to D5. You arrived. You were thinking: The nearest square I haven't seen dug is D5.
- Turn 30 of the game, at D5, on a dug square, with no pirate next to you. You did: go_to E5. You walked east to E5. You arrived. You were thinking: The nearest square I haven't seen dug is E5.

Pirate-3, this is your turn 11 of 20, turn 33 of the game. You are at E5. Your square has been dug and holds no cave. The way north is blocked by the island's edge, the way east by the island's edge and the way south by pirate-1.
Squares you have dug: A3, 3 away; B4, 1 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is D4.

**What it did**

> go\_to {"square": "D4"}\
> move {"direction": "west"}

**The result**

> You set off for D4. You walked west to D5.

## Turn 33: pirate-1

<details>
<summary>What it was shown (5728 characters)</summary>

```text
# The goal
You are one of 3 pirates on an island, a 5 by 5 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-3 and takes turns in that order; each pirate gets 20 turns.
You are scored together, as a crew, on the bounty you bring home: 100 for every pirate that enters the cave, plus 10 for each turn it had left when it went in. Every pirate gets the same score. A pirate that never enters brings nothing.

# The scroll
- The scroll is the only way to reach the other pirates.
- Any action can carry one line to say, in `say`, of up to 200 characters. It goes on the scroll with your name and the turn of the game as the action happens, and costs nothing, so a line said with a dig goes out before the dig's reading is known.
- A failed action says nothing: its line isn't put on the scroll.
- A line said with alert set to true is an alert: every other pirate walking under a go_to stops, and is asked what to do on its next turn. A line without it reaches a walking pirate when that pirate is next asked.
- Each time you are asked, you are shown every line on the scroll you haven't been shown yet, your own included, each with who said it, on which turn of the game, whether it was an alert and whether it was a shared reading.

# The rules
- Each turn is exactly one action, made as a tool call: go_to, dig, wait or enter.
- Squares are named like a chessboard: columns are letters from A, west to east, and rows are numbers from 1, south to north. A1 is the south-west corner.
- A square holds one pirate at a time.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. Readings are exact.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 1 of the game, at A5, on an undug square, with pirate-2 to the south. You did: dig. You dug A5 and found nothing. The treasure is 3 squares away.
- Turn 4 of the game, at A5, on a dug square, with pirate-2 to the south. You did: go_to B5. You walked east to B5. You arrived.
- Turn 7 of the game, at B5, on an undug square, with pirate-2 to the west. You did: dig. You dug B5 and found nothing. The treasure is 2 squares away.
- Turn 10 of the game, at B5, on a dug square, with pirate-3 to the south and pirate-2 to the west. You did: go_to C5. You walked east to C5. You arrived.
- Turn 13 of the game, at C5, on an undug square, with pirate-2 to the west. You did: dig. You dug C5 and found nothing. The treasure is 1 square away.
- Turn 16 of the game, at C5, on a dug square, with pirate-3 to the west. You did: go_to D5. You walked east to D5. You arrived.
- Turn 19 of the game, at D5, on an undug square, with no pirate next to you. You did: dig. You dug D5 and found nothing. The treasure is 2 squares away.
- Turn 22 of the game, at D5, on a dug square, with no pirate next to you. You did: go_to E5. You walked east to E5. You arrived.
- Turn 25 of the game, at E5, on an undug square, with no pirate next to you. You did: dig. You dug E5 and found nothing. The treasure is 3 squares away.
- Turn 28 of the game, at E5, on a dug square, with pirate-3 to the west. You did: go_to E4. You walked south to E4. You arrived. You were thinking: The nearest square I haven't seen dug is E4.
- Turn 31 of the game, at E4, on an undug square, with pirate-3 to the north. You did: dig. You dug E4 and found nothing. The treasure is 2 squares away. You were thinking: Nobody has dug this square yet.

Pirate-1, this is your turn 12 of 20, turn 34 of the game. You are at E4. Your square has been dug and holds no cave. The way east is blocked by the island's edge.
Squares you have dug: A5, 3 away; B5, 2 away; C5, 1 away; D5, 2 away; E5, 3 away; E4, 2 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is D4.

**What it did**

> go\_to {"square": "D4"}\
> move {"direction": "west"}

**The result**

> You walked west to D4. You arrived.

## Turn 34: pirate-2

<details>
<summary>What it was shown (5413 characters)</summary>

```text
# The goal
You are one of 3 pirates on an island, a 5 by 5 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-3 and takes turns in that order; each pirate gets 20 turns.
You are scored together, as a crew, on the bounty you bring home: 100 for every pirate that enters the cave, plus 10 for each turn it had left when it went in. Every pirate gets the same score. A pirate that never enters brings nothing.

# The scroll
- The scroll is the only way to reach the other pirates.
- Any action can carry one line to say, in `say`, of up to 200 characters. It goes on the scroll with your name and the turn of the game as the action happens, and costs nothing, so a line said with a dig goes out before the dig's reading is known.
- A failed action says nothing: its line isn't put on the scroll.
- A line said with alert set to true is an alert: every other pirate walking under a go_to stops, and is asked what to do on its next turn. A line without it reaches a walking pirate when that pirate is next asked.
- Each time you are asked, you are shown every line on the scroll you haven't been shown yet, your own included, each with who said it, on which turn of the game, whether it was an alert and whether it was a shared reading.

# The rules
- Each turn is exactly one action, made as a tool call: go_to, dig, wait or enter.
- Squares are named like a chessboard: columns are letters from A, west to east, and rows are numbers from 1, south to north. A1 is the south-west corner.
- A square holds one pirate at a time.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. Readings are exact.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 2 of the game, at A4, on an undug square, with pirate-1 to the north and pirate-3 to the south. You did: dig. You dug A4 and found nothing. The treasure is 2 squares away.
- Turn 5 of the game, at A4, on a dug square, with pirate-3 to the south. You did: go_to A5. You walked north to A5. You arrived.
- Turn 8 of the game, at A5, on a dug square, with pirate-1 to the east and pirate-3 to the south. You did: wait. You waited at A5.
- Turn 11 of the game, at A5, on a dug square, with no pirate next to you. You did: go_to B5. You walked east to B5. You arrived.
- Turn 14 of the game, at B5, on a dug square, with pirate-1 to the east and pirate-3 to the south. You did: go_to A3. You set off for A3. You walked west to A5. You walked from B5 to A3 over 3 turns.
- Turn 23 of the game, at A3, on a dug square, with no pirate next to you. You arrived at A3. You did: go_to B3. You walked east to B3. You arrived.
- Turn 26 of the game, at B3, on an undug square, with no pirate next to you. You did: dig. You dug B3 and found nothing. The treasure is 2 squares away.
- Turn 29 of the game, at B3, on a dug square, with no pirate next to you. You did: go_to B4. You walked north to B4. You arrived. You were thinking: The nearest square I haven't seen dug is B4.
- Turn 32 of the game, at B4, on a dug square, with no pirate next to you. You did: go_to C4. You walked east to C4. You arrived. You were thinking: The nearest square I haven't seen dug is C4.

Pirate-2, this is your turn 12 of 20, turn 35 of the game. You are at C4. Your square hasn't been dug. The way east is blocked by pirate-1.
Squares you have dug: A4, 2 away; B3, 2 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> Nobody has dug this square yet.

**What it did**

> dig

**The result**

> You dug here and found the treasure! It opens a cave on this square: enter it to go in.

## Turn 35: pirate-3

<details>
<summary>What it was shown (5698 characters)</summary>

```text
# The goal
You are one of 3 pirates on an island, a 5 by 5 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-3 and takes turns in that order; each pirate gets 20 turns.
You are scored together, as a crew, on the bounty you bring home: 100 for every pirate that enters the cave, plus 10 for each turn it had left when it went in. Every pirate gets the same score. A pirate that never enters brings nothing.

# The scroll
- The scroll is the only way to reach the other pirates.
- Any action can carry one line to say, in `say`, of up to 200 characters. It goes on the scroll with your name and the turn of the game as the action happens, and costs nothing, so a line said with a dig goes out before the dig's reading is known.
- A failed action says nothing: its line isn't put on the scroll.
- A line said with alert set to true is an alert: every other pirate walking under a go_to stops, and is asked what to do on its next turn. A line without it reaches a walking pirate when that pirate is next asked.
- Each time you are asked, you are shown every line on the scroll you haven't been shown yet, your own included, each with who said it, on which turn of the game, whether it was an alert and whether it was a shared reading.

# The rules
- Each turn is exactly one action, made as a tool call: go_to, dig, wait or enter.
- Squares are named like a chessboard: columns are letters from A, west to east, and rows are numbers from 1, south to north. A1 is the south-west corner.
- A square holds one pirate at a time.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. Readings are exact.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 3 of the game, at A3, on an undug square, with pirate-2 to the north. You did: dig. You dug A3 and found nothing. The treasure is 3 squares away.
- Turn 6 of the game, at A3, on a dug square, with no pirate next to you. You did: go_to A4. You walked north to A4. You arrived.
- Turn 9 of the game, at A4, on a dug square, with pirate-2 to the north. You did: go_to B4. You walked east to B4. You arrived.
- Turn 12 of the game, at B4, on an undug square, with pirate-2 to the north. You did: dig. You dug B4 and found nothing. The treasure is 1 square away.
- Turn 15 of the game, at B4, on a dug square, with no pirate next to you. You did: go_to B5. You walked north to B5. You arrived.
- Turn 18 of the game, at B5, on a dug square, with no pirate next to you. You did: go_to A5. You walked west to A5. You arrived.
- Turn 21 of the game, at A5, on a dug square, with no pirate next to you. You did: go_to C5. You set off for C5. You walked east to B5. You walked from A5 to C5 over 2 turns.
- Turn 27 of the game, at C5, on a dug square, with no pirate next to you. You arrived at C5. You did: go_to D5. You walked east to D5. You arrived.
- Turn 30 of the game, at D5, on a dug square, with no pirate next to you. You did: go_to E5. You walked east to E5. You arrived. You were thinking: The nearest square I haven't seen dug is E5.
- Turn 33 of the game, at E5, on a dug square, with pirate-1 to the south. You did: go_to D4. You set off for D4. You walked west to D5. You walked from E5 to D5 over 1 turn, then stopped: the way south was blocked by pirate-1. You were thinking: The nearest square I haven't seen dug is D4.

Pirate-3, this is your turn 12 of 20, turn 36 of the game. You are at D5. Your square has been dug and holds no cave. The way north is blocked by the island's edge and the way south by pirate-1.
You stopped at D5: the way south is blocked by pirate-1.
Squares you have dug: A3, 3 away; B4, 1 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is C4.

**What it did**

> go\_to {"square": "C4"}\
> move {"direction": "west"}

**The result**

> You set off for C4. You walked west to C5.

## Turn 36: pirate-1

<details>
<summary>What it was shown (5834 characters)</summary>

```text
# The goal
You are one of 3 pirates on an island, a 5 by 5 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-3 and takes turns in that order; each pirate gets 20 turns.
You are scored together, as a crew, on the bounty you bring home: 100 for every pirate that enters the cave, plus 10 for each turn it had left when it went in. Every pirate gets the same score. A pirate that never enters brings nothing.

# The scroll
- The scroll is the only way to reach the other pirates.
- Any action can carry one line to say, in `say`, of up to 200 characters. It goes on the scroll with your name and the turn of the game as the action happens, and costs nothing, so a line said with a dig goes out before the dig's reading is known.
- A failed action says nothing: its line isn't put on the scroll.
- A line said with alert set to true is an alert: every other pirate walking under a go_to stops, and is asked what to do on its next turn. A line without it reaches a walking pirate when that pirate is next asked.
- Each time you are asked, you are shown every line on the scroll you haven't been shown yet, your own included, each with who said it, on which turn of the game, whether it was an alert and whether it was a shared reading.

# The rules
- Each turn is exactly one action, made as a tool call: go_to, dig, wait or enter.
- Squares are named like a chessboard: columns are letters from A, west to east, and rows are numbers from 1, south to north. A1 is the south-west corner.
- A square holds one pirate at a time.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. Readings are exact.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 1 of the game, at A5, on an undug square, with pirate-2 to the south. You did: dig. You dug A5 and found nothing. The treasure is 3 squares away.
- Turn 4 of the game, at A5, on a dug square, with pirate-2 to the south. You did: go_to B5. You walked east to B5. You arrived.
- Turn 7 of the game, at B5, on an undug square, with pirate-2 to the west. You did: dig. You dug B5 and found nothing. The treasure is 2 squares away.
- Turn 10 of the game, at B5, on a dug square, with pirate-3 to the south and pirate-2 to the west. You did: go_to C5. You walked east to C5. You arrived.
- Turn 13 of the game, at C5, on an undug square, with pirate-2 to the west. You did: dig. You dug C5 and found nothing. The treasure is 1 square away.
- Turn 16 of the game, at C5, on a dug square, with pirate-3 to the west. You did: go_to D5. You walked east to D5. You arrived.
- Turn 19 of the game, at D5, on an undug square, with no pirate next to you. You did: dig. You dug D5 and found nothing. The treasure is 2 squares away.
- Turn 22 of the game, at D5, on a dug square, with no pirate next to you. You did: go_to E5. You walked east to E5. You arrived.
- Turn 25 of the game, at E5, on an undug square, with no pirate next to you. You did: dig. You dug E5 and found nothing. The treasure is 3 squares away.
- Turn 28 of the game, at E5, on a dug square, with pirate-3 to the west. You did: go_to E4. You walked south to E4. You arrived.
- Turn 31 of the game, at E4, on an undug square, with pirate-3 to the north. You did: dig. You dug E4 and found nothing. The treasure is 2 squares away. You were thinking: Nobody has dug this square yet.
- Turn 34 of the game, at E4, on a dug square, with no pirate next to you. You did: go_to D4. You walked west to D4. You arrived. You were thinking: The nearest square I haven't seen dug is D4.

Pirate-1, this is your turn 13 of 20, turn 37 of the game. You are at D4. Your square hasn't been dug. The way west is blocked by pirate-2.
Squares you have dug: A5, 3 away; B5, 2 away; C5, 1 away; D5, 2 away; E5, 3 away; E4, 2 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> Nobody has dug this square yet.

**What it did**

> dig

**The result**

> You dug D4 and found nothing. The treasure is 1 square away.

## Turn 37: pirate-2

<details>
<summary>What it was shown (5648 characters)</summary>

```text
# The goal
You are one of 3 pirates on an island, a 5 by 5 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-3 and takes turns in that order; each pirate gets 20 turns.
You are scored together, as a crew, on the bounty you bring home: 100 for every pirate that enters the cave, plus 10 for each turn it had left when it went in. Every pirate gets the same score. A pirate that never enters brings nothing.

# The scroll
- The scroll is the only way to reach the other pirates.
- Any action can carry one line to say, in `say`, of up to 200 characters. It goes on the scroll with your name and the turn of the game as the action happens, and costs nothing, so a line said with a dig goes out before the dig's reading is known.
- A failed action says nothing: its line isn't put on the scroll.
- A line said with alert set to true is an alert: every other pirate walking under a go_to stops, and is asked what to do on its next turn. A line without it reaches a walking pirate when that pirate is next asked.
- Each time you are asked, you are shown every line on the scroll you haven't been shown yet, your own included, each with who said it, on which turn of the game, whether it was an alert and whether it was a shared reading.

# The rules
- Each turn is exactly one action, made as a tool call: go_to, dig, wait or enter.
- Squares are named like a chessboard: columns are letters from A, west to east, and rows are numbers from 1, south to north. A1 is the south-west corner.
- A square holds one pirate at a time.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. Readings are exact.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 2 of the game, at A4, on an undug square, with pirate-1 to the north and pirate-3 to the south. You did: dig. You dug A4 and found nothing. The treasure is 2 squares away.
- Turn 5 of the game, at A4, on a dug square, with pirate-3 to the south. You did: go_to A5. You walked north to A5. You arrived.
- Turn 8 of the game, at A5, on a dug square, with pirate-1 to the east and pirate-3 to the south. You did: wait. You waited at A5.
- Turn 11 of the game, at A5, on a dug square, with no pirate next to you. You did: go_to B5. You walked east to B5. You arrived.
- Turn 14 of the game, at B5, on a dug square, with pirate-1 to the east and pirate-3 to the south. You did: go_to A3. You set off for A3. You walked west to A5. You walked from B5 to A3 over 3 turns.
- Turn 23 of the game, at A3, on a dug square, with no pirate next to you. You arrived at A3. You did: go_to B3. You walked east to B3. You arrived.
- Turn 26 of the game, at B3, on an undug square, with no pirate next to you. You did: dig. You dug B3 and found nothing. The treasure is 2 squares away.
- Turn 29 of the game, at B3, on a dug square, with no pirate next to you. You did: go_to B4. You walked north to B4. You arrived.
- Turn 32 of the game, at B4, on a dug square, with no pirate next to you. You did: go_to C4. You walked east to C4. You arrived. You were thinking: The nearest square I haven't seen dug is C4.
- Turn 35 of the game, at C4, on an undug square, with pirate-1 to the east. You did: dig. You dug here and found the treasure! It opens a cave on this square: enter it to go in. You were thinking: Nobody has dug this square yet.

Pirate-2, this is your turn 13 of 20, turn 38 of the game. You are at C4. You are standing on the open cave: enter it to go in. The way north is blocked by pirate-3 and the way east by pirate-1.
Squares you have dug: A4, 2 away; B3, 2 away; C4, the cave.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> This is the open cave, so I'm going in.

**What it did**

> enter

**The result**

> You went into the cave. You're out of the game, and your crew scores you.

## Turn 38: pirate-3

*Walked under an order: its brain wasn't asked.*

**Its thinking**

*No thinking recorded.*

**What it did**

> move {"direction": "south"}

**The result**

> You walked south to C4.

## Turn 39: pirate-1

<details>
<summary>What it was shown (6013 characters)</summary>

```text
# The goal
You are one of 3 pirates on an island, a 5 by 5 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-3 and takes turns in that order; each pirate gets 20 turns.
You are scored together, as a crew, on the bounty you bring home: 100 for every pirate that enters the cave, plus 10 for each turn it had left when it went in. Every pirate gets the same score. A pirate that never enters brings nothing.

# The scroll
- The scroll is the only way to reach the other pirates.
- Any action can carry one line to say, in `say`, of up to 200 characters. It goes on the scroll with your name and the turn of the game as the action happens, and costs nothing, so a line said with a dig goes out before the dig's reading is known.
- A failed action says nothing: its line isn't put on the scroll.
- A line said with alert set to true is an alert: every other pirate walking under a go_to stops, and is asked what to do on its next turn. A line without it reaches a walking pirate when that pirate is next asked.
- Each time you are asked, you are shown every line on the scroll you haven't been shown yet, your own included, each with who said it, on which turn of the game, whether it was an alert and whether it was a shared reading.

# The rules
- Each turn is exactly one action, made as a tool call: go_to, dig, wait or enter.
- Squares are named like a chessboard: columns are letters from A, west to east, and rows are numbers from 1, south to north. A1 is the south-west corner.
- A square holds one pirate at a time.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. Readings are exact.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 1 of the game, at A5, on an undug square, with pirate-2 to the south. You did: dig. You dug A5 and found nothing. The treasure is 3 squares away.
- Turn 4 of the game, at A5, on a dug square, with pirate-2 to the south. You did: go_to B5. You walked east to B5. You arrived.
- Turn 7 of the game, at B5, on an undug square, with pirate-2 to the west. You did: dig. You dug B5 and found nothing. The treasure is 2 squares away.
- Turn 10 of the game, at B5, on a dug square, with pirate-3 to the south and pirate-2 to the west. You did: go_to C5. You walked east to C5. You arrived.
- Turn 13 of the game, at C5, on an undug square, with pirate-2 to the west. You did: dig. You dug C5 and found nothing. The treasure is 1 square away.
- Turn 16 of the game, at C5, on a dug square, with pirate-3 to the west. You did: go_to D5. You walked east to D5. You arrived.
- Turn 19 of the game, at D5, on an undug square, with no pirate next to you. You did: dig. You dug D5 and found nothing. The treasure is 2 squares away.
- Turn 22 of the game, at D5, on a dug square, with no pirate next to you. You did: go_to E5. You walked east to E5. You arrived.
- Turn 25 of the game, at E5, on an undug square, with no pirate next to you. You did: dig. You dug E5 and found nothing. The treasure is 3 squares away.
- Turn 28 of the game, at E5, on a dug square, with pirate-3 to the west. You did: go_to E4. You walked south to E4. You arrived.
- Turn 31 of the game, at E4, on an undug square, with pirate-3 to the north. You did: dig. You dug E4 and found nothing. The treasure is 2 squares away.
- Turn 34 of the game, at E4, on a dug square, with no pirate next to you. You did: go_to D4. You walked west to D4. You arrived. You were thinking: The nearest square I haven't seen dug is D4.
- Turn 37 of the game, at D4, on an undug square, with pirate-2 to the west. You did: dig. You dug D4 and found nothing. The treasure is 1 square away. You were thinking: Nobody has dug this square yet.

Pirate-1, this is your turn 14 of 20, turn 40 of the game. You are at D4. Your square has been dug and holds no cave. The way west is blocked by pirate-3.
Squares you have dug: A5, 3 away; B5, 2 away; C5, 1 away; D5, 2 away; E5, 3 away; E4, 2 away; D4, 1 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is D3.

**What it did**

> go\_to {"square": "D3"}\
> move {"direction": "south"}

**The result**

> You walked south to D3. You arrived.

## Turn 40: pirate-3

<details>
<summary>What it was shown (5864 characters)</summary>

```text
# The goal
You are one of 3 pirates on an island, a 5 by 5 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-3 and takes turns in that order; each pirate gets 20 turns.
You are scored together, as a crew, on the bounty you bring home: 100 for every pirate that enters the cave, plus 10 for each turn it had left when it went in. Every pirate gets the same score. A pirate that never enters brings nothing.

# The scroll
- The scroll is the only way to reach the other pirates.
- Any action can carry one line to say, in `say`, of up to 200 characters. It goes on the scroll with your name and the turn of the game as the action happens, and costs nothing, so a line said with a dig goes out before the dig's reading is known.
- A failed action says nothing: its line isn't put on the scroll.
- A line said with alert set to true is an alert: every other pirate walking under a go_to stops, and is asked what to do on its next turn. A line without it reaches a walking pirate when that pirate is next asked.
- Each time you are asked, you are shown every line on the scroll you haven't been shown yet, your own included, each with who said it, on which turn of the game, whether it was an alert and whether it was a shared reading.

# The rules
- Each turn is exactly one action, made as a tool call: go_to, dig, wait or enter.
- Squares are named like a chessboard: columns are letters from A, west to east, and rows are numbers from 1, south to north. A1 is the south-west corner.
- A square holds one pirate at a time.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. Readings are exact.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 3 of the game, at A3, on an undug square, with pirate-2 to the north. You did: dig. You dug A3 and found nothing. The treasure is 3 squares away.
- Turn 6 of the game, at A3, on a dug square, with no pirate next to you. You did: go_to A4. You walked north to A4. You arrived.
- Turn 9 of the game, at A4, on a dug square, with pirate-2 to the north. You did: go_to B4. You walked east to B4. You arrived.
- Turn 12 of the game, at B4, on an undug square, with pirate-2 to the north. You did: dig. You dug B4 and found nothing. The treasure is 1 square away.
- Turn 15 of the game, at B4, on a dug square, with no pirate next to you. You did: go_to B5. You walked north to B5. You arrived.
- Turn 18 of the game, at B5, on a dug square, with no pirate next to you. You did: go_to A5. You walked west to A5. You arrived.
- Turn 21 of the game, at A5, on a dug square, with no pirate next to you. You did: go_to C5. You set off for C5. You walked east to B5. You walked from A5 to C5 over 2 turns.
- Turn 27 of the game, at C5, on a dug square, with no pirate next to you. You arrived at C5. You did: go_to D5. You walked east to D5. You arrived.
- Turn 30 of the game, at D5, on a dug square, with no pirate next to you. You did: go_to E5. You walked east to E5. You arrived.
- Turn 33 of the game, at E5, on a dug square, with pirate-1 to the south. You did: go_to D4. You set off for D4. You walked west to D5. You walked from E5 to D5 over 1 turn, then stopped: the way south was blocked by pirate-1. You were thinking: The nearest square I haven't seen dug is D4.
- Turn 36 of the game, at D5, on a dug square, with pirate-1 to the south. You stopped at D5: the way south is blocked by pirate-1. You did: go_to C4. You set off for C4. You walked west to C5. You walked from D5 to C4 over 2 turns. You were thinking: The nearest square I haven't seen dug is C4.

Pirate-3, this is your turn 14 of 20, turn 41 of the game. You are at C4. You are standing on the open cave: enter it to go in. No way out of your square is blocked.
You arrived at C4.
Squares you have dug: A3, 3 away; B4, 1 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> This is the open cave, so I'm going in.

**What it did**

> enter

**The result**

> You went into the cave. You're out of the game, and your crew scores you.

## Turn 41: pirate-1

<details>
<summary>What it was shown (6129 characters)</summary>

```text
# The goal
You are one of 3 pirates on an island, a 5 by 5 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-3 and takes turns in that order; each pirate gets 20 turns.
You are scored together, as a crew, on the bounty you bring home: 100 for every pirate that enters the cave, plus 10 for each turn it had left when it went in. Every pirate gets the same score. A pirate that never enters brings nothing.

# The scroll
- The scroll is the only way to reach the other pirates.
- Any action can carry one line to say, in `say`, of up to 200 characters. It goes on the scroll with your name and the turn of the game as the action happens, and costs nothing, so a line said with a dig goes out before the dig's reading is known.
- A failed action says nothing: its line isn't put on the scroll.
- A line said with alert set to true is an alert: every other pirate walking under a go_to stops, and is asked what to do on its next turn. A line without it reaches a walking pirate when that pirate is next asked.
- Each time you are asked, you are shown every line on the scroll you haven't been shown yet, your own included, each with who said it, on which turn of the game, whether it was an alert and whether it was a shared reading.

# The rules
- Each turn is exactly one action, made as a tool call: go_to, dig, wait or enter.
- Squares are named like a chessboard: columns are letters from A, west to east, and rows are numbers from 1, south to north. A1 is the south-west corner.
- A square holds one pirate at a time.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. Readings are exact.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 1 of the game, at A5, on an undug square, with pirate-2 to the south. You did: dig. You dug A5 and found nothing. The treasure is 3 squares away.
- Turn 4 of the game, at A5, on a dug square, with pirate-2 to the south. You did: go_to B5. You walked east to B5. You arrived.
- Turn 7 of the game, at B5, on an undug square, with pirate-2 to the west. You did: dig. You dug B5 and found nothing. The treasure is 2 squares away.
- Turn 10 of the game, at B5, on a dug square, with pirate-3 to the south and pirate-2 to the west. You did: go_to C5. You walked east to C5. You arrived.
- Turn 13 of the game, at C5, on an undug square, with pirate-2 to the west. You did: dig. You dug C5 and found nothing. The treasure is 1 square away.
- Turn 16 of the game, at C5, on a dug square, with pirate-3 to the west. You did: go_to D5. You walked east to D5. You arrived.
- Turn 19 of the game, at D5, on an undug square, with no pirate next to you. You did: dig. You dug D5 and found nothing. The treasure is 2 squares away.
- Turn 22 of the game, at D5, on a dug square, with no pirate next to you. You did: go_to E5. You walked east to E5. You arrived.
- Turn 25 of the game, at E5, on an undug square, with no pirate next to you. You did: dig. You dug E5 and found nothing. The treasure is 3 squares away.
- Turn 28 of the game, at E5, on a dug square, with pirate-3 to the west. You did: go_to E4. You walked south to E4. You arrived.
- Turn 31 of the game, at E4, on an undug square, with pirate-3 to the north. You did: dig. You dug E4 and found nothing. The treasure is 2 squares away.
- Turn 34 of the game, at E4, on a dug square, with no pirate next to you. You did: go_to D4. You walked west to D4. You arrived.
- Turn 37 of the game, at D4, on an undug square, with pirate-2 to the west. You did: dig. You dug D4 and found nothing. The treasure is 1 square away. You were thinking: Nobody has dug this square yet.
- Turn 40 of the game, at D4, on a dug square, with pirate-3 to the west. You did: go_to D3. You walked south to D3. You arrived. You were thinking: The nearest square I haven't seen dug is D3.

Pirate-1, this is your turn 15 of 20, turn 42 of the game. You are at D3. Your square hasn't been dug. No way out of your square is blocked.
Squares you have dug: A5, 3 away; B5, 2 away; C5, 1 away; D5, 2 away; E5, 3 away; E4, 2 away; D4, 1 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> Nobody has dug this square yet.

**What it did**

> dig

**The result**

> You dug D3 and found nothing. The treasure is 2 squares away.

## Turn 42: pirate-1

<details>
<summary>What it was shown (6310 characters)</summary>

```text
# The goal
You are one of 3 pirates on an island, a 5 by 5 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-3 and takes turns in that order; each pirate gets 20 turns.
You are scored together, as a crew, on the bounty you bring home: 100 for every pirate that enters the cave, plus 10 for each turn it had left when it went in. Every pirate gets the same score. A pirate that never enters brings nothing.

# The scroll
- The scroll is the only way to reach the other pirates.
- Any action can carry one line to say, in `say`, of up to 200 characters. It goes on the scroll with your name and the turn of the game as the action happens, and costs nothing, so a line said with a dig goes out before the dig's reading is known.
- A failed action says nothing: its line isn't put on the scroll.
- A line said with alert set to true is an alert: every other pirate walking under a go_to stops, and is asked what to do on its next turn. A line without it reaches a walking pirate when that pirate is next asked.
- Each time you are asked, you are shown every line on the scroll you haven't been shown yet, your own included, each with who said it, on which turn of the game, whether it was an alert and whether it was a shared reading.

# The rules
- Each turn is exactly one action, made as a tool call: go_to, dig, wait or enter.
- Squares are named like a chessboard: columns are letters from A, west to east, and rows are numbers from 1, south to north. A1 is the south-west corner.
- A square holds one pirate at a time.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. Readings are exact.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 1 of the game, at A5, on an undug square, with pirate-2 to the south. You did: dig. You dug A5 and found nothing. The treasure is 3 squares away.
- Turn 4 of the game, at A5, on a dug square, with pirate-2 to the south. You did: go_to B5. You walked east to B5. You arrived.
- Turn 7 of the game, at B5, on an undug square, with pirate-2 to the west. You did: dig. You dug B5 and found nothing. The treasure is 2 squares away.
- Turn 10 of the game, at B5, on a dug square, with pirate-3 to the south and pirate-2 to the west. You did: go_to C5. You walked east to C5. You arrived.
- Turn 13 of the game, at C5, on an undug square, with pirate-2 to the west. You did: dig. You dug C5 and found nothing. The treasure is 1 square away.
- Turn 16 of the game, at C5, on a dug square, with pirate-3 to the west. You did: go_to D5. You walked east to D5. You arrived.
- Turn 19 of the game, at D5, on an undug square, with no pirate next to you. You did: dig. You dug D5 and found nothing. The treasure is 2 squares away.
- Turn 22 of the game, at D5, on a dug square, with no pirate next to you. You did: go_to E5. You walked east to E5. You arrived.
- Turn 25 of the game, at E5, on an undug square, with no pirate next to you. You did: dig. You dug E5 and found nothing. The treasure is 3 squares away.
- Turn 28 of the game, at E5, on a dug square, with pirate-3 to the west. You did: go_to E4. You walked south to E4. You arrived.
- Turn 31 of the game, at E4, on an undug square, with pirate-3 to the north. You did: dig. You dug E4 and found nothing. The treasure is 2 squares away.
- Turn 34 of the game, at E4, on a dug square, with no pirate next to you. You did: go_to D4. You walked west to D4. You arrived.
- Turn 37 of the game, at D4, on an undug square, with pirate-2 to the west. You did: dig. You dug D4 and found nothing. The treasure is 1 square away.
- Turn 40 of the game, at D4, on a dug square, with pirate-3 to the west. You did: go_to D3. You walked south to D3. You arrived. You were thinking: The nearest square I haven't seen dug is D3.
- Turn 42 of the game, at D3, on an undug square, with no pirate next to you. You did: dig. You dug D3 and found nothing. The treasure is 2 squares away. You were thinking: Nobody has dug this square yet.

Pirate-1, this is your turn 16 of 20, turn 43 of the game. You are at D3. Your square has been dug and holds no cave. No way out of your square is blocked.
Squares you have dug: A5, 3 away; B5, 2 away; C5, 1 away; D5, 2 away; E5, 3 away; E4, 2 away; D4, 1 away; D3, 2 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is C3.

**What it did**

> go\_to {"square": "C3"}\
> move {"direction": "west"}

**The result**

> You walked west to C3. You arrived.

## Turn 43: pirate-1

<details>
<summary>What it was shown (6425 characters)</summary>

```text
# The goal
You are one of 3 pirates on an island, a 5 by 5 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-3 and takes turns in that order; each pirate gets 20 turns.
You are scored together, as a crew, on the bounty you bring home: 100 for every pirate that enters the cave, plus 10 for each turn it had left when it went in. Every pirate gets the same score. A pirate that never enters brings nothing.

# The scroll
- The scroll is the only way to reach the other pirates.
- Any action can carry one line to say, in `say`, of up to 200 characters. It goes on the scroll with your name and the turn of the game as the action happens, and costs nothing, so a line said with a dig goes out before the dig's reading is known.
- A failed action says nothing: its line isn't put on the scroll.
- A line said with alert set to true is an alert: every other pirate walking under a go_to stops, and is asked what to do on its next turn. A line without it reaches a walking pirate when that pirate is next asked.
- Each time you are asked, you are shown every line on the scroll you haven't been shown yet, your own included, each with who said it, on which turn of the game, whether it was an alert and whether it was a shared reading.

# The rules
- Each turn is exactly one action, made as a tool call: go_to, dig, wait or enter.
- Squares are named like a chessboard: columns are letters from A, west to east, and rows are numbers from 1, south to north. A1 is the south-west corner.
- A square holds one pirate at a time.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. Readings are exact.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 1 of the game, at A5, on an undug square, with pirate-2 to the south. You did: dig. You dug A5 and found nothing. The treasure is 3 squares away.
- Turn 4 of the game, at A5, on a dug square, with pirate-2 to the south. You did: go_to B5. You walked east to B5. You arrived.
- Turn 7 of the game, at B5, on an undug square, with pirate-2 to the west. You did: dig. You dug B5 and found nothing. The treasure is 2 squares away.
- Turn 10 of the game, at B5, on a dug square, with pirate-3 to the south and pirate-2 to the west. You did: go_to C5. You walked east to C5. You arrived.
- Turn 13 of the game, at C5, on an undug square, with pirate-2 to the west. You did: dig. You dug C5 and found nothing. The treasure is 1 square away.
- Turn 16 of the game, at C5, on a dug square, with pirate-3 to the west. You did: go_to D5. You walked east to D5. You arrived.
- Turn 19 of the game, at D5, on an undug square, with no pirate next to you. You did: dig. You dug D5 and found nothing. The treasure is 2 squares away.
- Turn 22 of the game, at D5, on a dug square, with no pirate next to you. You did: go_to E5. You walked east to E5. You arrived.
- Turn 25 of the game, at E5, on an undug square, with no pirate next to you. You did: dig. You dug E5 and found nothing. The treasure is 3 squares away.
- Turn 28 of the game, at E5, on a dug square, with pirate-3 to the west. You did: go_to E4. You walked south to E4. You arrived.
- Turn 31 of the game, at E4, on an undug square, with pirate-3 to the north. You did: dig. You dug E4 and found nothing. The treasure is 2 squares away.
- Turn 34 of the game, at E4, on a dug square, with no pirate next to you. You did: go_to D4. You walked west to D4. You arrived.
- Turn 37 of the game, at D4, on an undug square, with pirate-2 to the west. You did: dig. You dug D4 and found nothing. The treasure is 1 square away.
- Turn 40 of the game, at D4, on a dug square, with pirate-3 to the west. You did: go_to D3. You walked south to D3. You arrived.
- Turn 42 of the game, at D3, on an undug square, with no pirate next to you. You did: dig. You dug D3 and found nothing. The treasure is 2 squares away. You were thinking: Nobody has dug this square yet.
- Turn 43 of the game, at D3, on a dug square, with no pirate next to you. You did: go_to C3. You walked west to C3. You arrived. You were thinking: The nearest square I haven't seen dug is C3.

Pirate-1, this is your turn 17 of 20, turn 44 of the game. You are at C3. Your square hasn't been dug. No way out of your square is blocked.
Squares you have dug: A5, 3 away; B5, 2 away; C5, 1 away; D5, 2 away; E5, 3 away; E4, 2 away; D4, 1 away; D3, 2 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> Nobody has dug this square yet.

**What it did**

> dig

**The result**

> You dug C3 and found nothing. The treasure is 1 square away.

## Turn 44: pirate-1

<details>
<summary>What it was shown (6605 characters)</summary>

```text
# The goal
You are one of 3 pirates on an island, a 5 by 5 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-3 and takes turns in that order; each pirate gets 20 turns.
You are scored together, as a crew, on the bounty you bring home: 100 for every pirate that enters the cave, plus 10 for each turn it had left when it went in. Every pirate gets the same score. A pirate that never enters brings nothing.

# The scroll
- The scroll is the only way to reach the other pirates.
- Any action can carry one line to say, in `say`, of up to 200 characters. It goes on the scroll with your name and the turn of the game as the action happens, and costs nothing, so a line said with a dig goes out before the dig's reading is known.
- A failed action says nothing: its line isn't put on the scroll.
- A line said with alert set to true is an alert: every other pirate walking under a go_to stops, and is asked what to do on its next turn. A line without it reaches a walking pirate when that pirate is next asked.
- Each time you are asked, you are shown every line on the scroll you haven't been shown yet, your own included, each with who said it, on which turn of the game, whether it was an alert and whether it was a shared reading.

# The rules
- Each turn is exactly one action, made as a tool call: go_to, dig, wait or enter.
- Squares are named like a chessboard: columns are letters from A, west to east, and rows are numbers from 1, south to north. A1 is the south-west corner.
- A square holds one pirate at a time.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. Readings are exact.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 1 of the game, at A5, on an undug square, with pirate-2 to the south. You did: dig. You dug A5 and found nothing. The treasure is 3 squares away.
- Turn 4 of the game, at A5, on a dug square, with pirate-2 to the south. You did: go_to B5. You walked east to B5. You arrived.
- Turn 7 of the game, at B5, on an undug square, with pirate-2 to the west. You did: dig. You dug B5 and found nothing. The treasure is 2 squares away.
- Turn 10 of the game, at B5, on a dug square, with pirate-3 to the south and pirate-2 to the west. You did: go_to C5. You walked east to C5. You arrived.
- Turn 13 of the game, at C5, on an undug square, with pirate-2 to the west. You did: dig. You dug C5 and found nothing. The treasure is 1 square away.
- Turn 16 of the game, at C5, on a dug square, with pirate-3 to the west. You did: go_to D5. You walked east to D5. You arrived.
- Turn 19 of the game, at D5, on an undug square, with no pirate next to you. You did: dig. You dug D5 and found nothing. The treasure is 2 squares away.
- Turn 22 of the game, at D5, on a dug square, with no pirate next to you. You did: go_to E5. You walked east to E5. You arrived.
- Turn 25 of the game, at E5, on an undug square, with no pirate next to you. You did: dig. You dug E5 and found nothing. The treasure is 3 squares away.
- Turn 28 of the game, at E5, on a dug square, with pirate-3 to the west. You did: go_to E4. You walked south to E4. You arrived.
- Turn 31 of the game, at E4, on an undug square, with pirate-3 to the north. You did: dig. You dug E4 and found nothing. The treasure is 2 squares away.
- Turn 34 of the game, at E4, on a dug square, with no pirate next to you. You did: go_to D4. You walked west to D4. You arrived.
- Turn 37 of the game, at D4, on an undug square, with pirate-2 to the west. You did: dig. You dug D4 and found nothing. The treasure is 1 square away.
- Turn 40 of the game, at D4, on a dug square, with pirate-3 to the west. You did: go_to D3. You walked south to D3. You arrived.
- Turn 42 of the game, at D3, on an undug square, with no pirate next to you. You did: dig. You dug D3 and found nothing. The treasure is 2 squares away.
- Turn 43 of the game, at D3, on a dug square, with no pirate next to you. You did: go_to C3. You walked west to C3. You arrived. You were thinking: The nearest square I haven't seen dug is C3.
- Turn 44 of the game, at C3, on an undug square, with no pirate next to you. You did: dig. You dug C3 and found nothing. The treasure is 1 square away. You were thinking: Nobody has dug this square yet.

Pirate-1, this is your turn 18 of 20, turn 45 of the game. You are at C3. Your square has been dug and holds no cave. No way out of your square is blocked.
Squares you have dug: A5, 3 away; B5, 2 away; C5, 1 away; D5, 2 away; E5, 3 away; E4, 2 away; D4, 1 away; D3, 2 away; C3, 1 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is C4.

**What it did**

> go\_to {"square": "C4"}\
> move {"direction": "north"}

**The result**

> You walked north to C4. You arrived.

## Turn 45: pirate-1

<details>
<summary>What it was shown (6746 characters)</summary>

```text
# The goal
You are one of 3 pirates on an island, a 5 by 5 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-3 and takes turns in that order; each pirate gets 20 turns.
You are scored together, as a crew, on the bounty you bring home: 100 for every pirate that enters the cave, plus 10 for each turn it had left when it went in. Every pirate gets the same score. A pirate that never enters brings nothing.

# The scroll
- The scroll is the only way to reach the other pirates.
- Any action can carry one line to say, in `say`, of up to 200 characters. It goes on the scroll with your name and the turn of the game as the action happens, and costs nothing, so a line said with a dig goes out before the dig's reading is known.
- A failed action says nothing: its line isn't put on the scroll.
- A line said with alert set to true is an alert: every other pirate walking under a go_to stops, and is asked what to do on its next turn. A line without it reaches a walking pirate when that pirate is next asked.
- Each time you are asked, you are shown every line on the scroll you haven't been shown yet, your own included, each with who said it, on which turn of the game, whether it was an alert and whether it was a shared reading.

# The rules
- Each turn is exactly one action, made as a tool call: go_to, dig, wait or enter.
- Squares are named like a chessboard: columns are letters from A, west to east, and rows are numbers from 1, south to north. A1 is the south-west corner.
- A square holds one pirate at a time.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. Readings are exact.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 1 of the game, at A5, on an undug square, with pirate-2 to the south. You did: dig. You dug A5 and found nothing. The treasure is 3 squares away.
- Turn 4 of the game, at A5, on a dug square, with pirate-2 to the south. You did: go_to B5. You walked east to B5. You arrived.
- Turn 7 of the game, at B5, on an undug square, with pirate-2 to the west. You did: dig. You dug B5 and found nothing. The treasure is 2 squares away.
- Turn 10 of the game, at B5, on a dug square, with pirate-3 to the south and pirate-2 to the west. You did: go_to C5. You walked east to C5. You arrived.
- Turn 13 of the game, at C5, on an undug square, with pirate-2 to the west. You did: dig. You dug C5 and found nothing. The treasure is 1 square away.
- Turn 16 of the game, at C5, on a dug square, with pirate-3 to the west. You did: go_to D5. You walked east to D5. You arrived.
- Turn 19 of the game, at D5, on an undug square, with no pirate next to you. You did: dig. You dug D5 and found nothing. The treasure is 2 squares away.
- Turn 22 of the game, at D5, on a dug square, with no pirate next to you. You did: go_to E5. You walked east to E5. You arrived.
- Turn 25 of the game, at E5, on an undug square, with no pirate next to you. You did: dig. You dug E5 and found nothing. The treasure is 3 squares away.
- Turn 28 of the game, at E5, on a dug square, with pirate-3 to the west. You did: go_to E4. You walked south to E4. You arrived.
- Turn 31 of the game, at E4, on an undug square, with pirate-3 to the north. You did: dig. You dug E4 and found nothing. The treasure is 2 squares away.
- Turn 34 of the game, at E4, on a dug square, with no pirate next to you. You did: go_to D4. You walked west to D4. You arrived.
- Turn 37 of the game, at D4, on an undug square, with pirate-2 to the west. You did: dig. You dug D4 and found nothing. The treasure is 1 square away.
- Turn 40 of the game, at D4, on a dug square, with pirate-3 to the west. You did: go_to D3. You walked south to D3. You arrived.
- Turn 42 of the game, at D3, on an undug square, with no pirate next to you. You did: dig. You dug D3 and found nothing. The treasure is 2 squares away.
- Turn 43 of the game, at D3, on a dug square, with no pirate next to you. You did: go_to C3. You walked west to C3. You arrived.
- Turn 44 of the game, at C3, on an undug square, with no pirate next to you. You did: dig. You dug C3 and found nothing. The treasure is 1 square away. You were thinking: Nobody has dug this square yet.
- Turn 45 of the game, at C3, on a dug square, with no pirate next to you. You did: go_to C4. You walked north to C4. You arrived. You were thinking: The nearest square I haven't seen dug is C4.

Pirate-1, this is your turn 19 of 20, turn 46 of the game. You are at C4. You are standing on the open cave: enter it to go in. No way out of your square is blocked.
Squares you have dug: A5, 3 away; B5, 2 away; C5, 1 away; D5, 2 away; E5, 3 away; E4, 2 away; D4, 1 away; D3, 2 away; C3, 1 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> This is the open cave, so I'm going in.

**What it did**

> enter

**The result**

> You went into the cave. You're out of the game, and your crew scores you.

## Game over

Game over: everyone is in the cave. The treasure at C4 was dug up, and 3 of 3 pirates got into the cave. Score 440.

**Score:** 440
