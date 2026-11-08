# Transcript: noisy

## Turn 0: pirate-1

<details>
<summary>What it was shown (4129 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
None yet.

Pirate-1, this is your turn 1 of 24, turn 1 of the game. You are at F3. Your square hasn't been dug. The way east is blocked by the island's edge.
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

> You dug F3 and found nothing. The treasure is 7 squares away.

## Turn 1: pirate-2

<details>
<summary>What it was shown (4130 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
None yet.

Pirate-2, this is your turn 1 of 24, turn 2 of the game. You are at D6. Your square hasn't been dug. The way north is blocked by the island's edge.
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

> You dug D6 and found nothing. The treasure is 2 squares away.

## Turn 2: pirate-3

<details>
<summary>What it was shown (4129 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
None yet.

Pirate-3, this is your turn 1 of 24, turn 3 of the game. You are at A4. Your square hasn't been dug. The way west is blocked by the island's edge.
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

> You dug A4 and found nothing. The treasure is 4 squares away.

## Turn 3: pirate-4

<details>
<summary>What it was shown (4130 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
None yet.

Pirate-4, this is your turn 1 of 24, turn 4 of the game. You are at C1. Your square hasn't been dug. The way south is blocked by the island's edge.
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

> You dug C1 and found nothing. The treasure is 2 squares away.

## Turn 4: pirate-1

<details>
<summary>What it was shown (4342 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 1 of the game, at F3, on an undug square, with no pirate next to you. You did: dig. You dug F3 and found nothing. The treasure is 7 squares away. You were thinking: Nobody has dug this square yet.

Pirate-1, this is your turn 2 of 24, turn 5 of the game. You are at F3. Your square has been dug and holds no cave. The way east is blocked by the island's edge.
Squares you have dug: F3, 7 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is F4.

**What it did**

> go\_to {"square": "F4"}\
> move {"direction": "north"}

**The result**

> You walked north to F4. You arrived.

## Turn 5: pirate-2

<details>
<summary>What it was shown (4343 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 2 of the game, at D6, on an undug square, with no pirate next to you. You did: dig. You dug D6 and found nothing. The treasure is 2 squares away. You were thinking: Nobody has dug this square yet.

Pirate-2, this is your turn 2 of 24, turn 6 of the game. You are at D6. Your square has been dug and holds no cave. The way north is blocked by the island's edge.
Squares you have dug: D6, 2 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is C6.

**What it did**

> go\_to {"square": "C6"}\
> move {"direction": "west"}

**The result**

> You walked west to C6. You arrived.

## Turn 6: pirate-3

<details>
<summary>What it was shown (4342 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 3 of the game, at A4, on an undug square, with no pirate next to you. You did: dig. You dug A4 and found nothing. The treasure is 4 squares away. You were thinking: Nobody has dug this square yet.

Pirate-3, this is your turn 2 of 24, turn 7 of the game. You are at A4. Your square has been dug and holds no cave. The way west is blocked by the island's edge.
Squares you have dug: A4, 4 away.
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

## Turn 7: pirate-4

<details>
<summary>What it was shown (4343 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 4 of the game, at C1, on an undug square, with no pirate next to you. You did: dig. You dug C1 and found nothing. The treasure is 2 squares away. You were thinking: Nobody has dug this square yet.

Pirate-4, this is your turn 2 of 24, turn 8 of the game. You are at C1. Your square has been dug and holds no cave. The way south is blocked by the island's edge.
Squares you have dug: C1, 2 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is C2.

**What it did**

> go\_to {"square": "C2"}\
> move {"direction": "north"}

**The result**

> You walked north to C2. You arrived.

## Turn 8: pirate-1

<details>
<summary>What it was shown (4521 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 1 of the game, at F3, on an undug square, with no pirate next to you. You did: dig. You dug F3 and found nothing. The treasure is 7 squares away. You were thinking: Nobody has dug this square yet.
- Turn 5 of the game, at F3, on a dug square, with no pirate next to you. You did: go_to F4. You walked north to F4. You arrived. You were thinking: The nearest square I haven't seen dug is F4.

Pirate-1, this is your turn 3 of 24, turn 9 of the game. You are at F4. Your square hasn't been dug. The way east is blocked by the island's edge.
Squares you have dug: F3, 7 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> Nobody has dug this square yet.

**What it did**

> dig

**The result**

> You dug F4 and found nothing. The treasure is 5 squares away.

## Turn 9: pirate-2

<details>
<summary>What it was shown (4522 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 2 of the game, at D6, on an undug square, with no pirate next to you. You did: dig. You dug D6 and found nothing. The treasure is 2 squares away. You were thinking: Nobody has dug this square yet.
- Turn 6 of the game, at D6, on a dug square, with no pirate next to you. You did: go_to C6. You walked west to C6. You arrived. You were thinking: The nearest square I haven't seen dug is C6.

Pirate-2, this is your turn 3 of 24, turn 10 of the game. You are at C6. Your square hasn't been dug. The way north is blocked by the island's edge.
Squares you have dug: D6, 2 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> Nobody has dug this square yet.

**What it did**

> dig

**The result**

> You dug C6 and found nothing. The treasure is 2 squares away.

## Turn 10: pirate-3

<details>
<summary>What it was shown (4522 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 3 of the game, at A4, on an undug square, with no pirate next to you. You did: dig. You dug A4 and found nothing. The treasure is 4 squares away. You were thinking: Nobody has dug this square yet.
- Turn 7 of the game, at A4, on a dug square, with no pirate next to you. You did: go_to A5. You walked north to A5. You arrived. You were thinking: The nearest square I haven't seen dug is A5.

Pirate-3, this is your turn 3 of 24, turn 11 of the game. You are at A5. Your square hasn't been dug. The way west is blocked by the island's edge.
Squares you have dug: A4, 4 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> Nobody has dug this square yet.

**What it did**

> dig

**The result**

> You dug A5 and found nothing. The treasure is 4 squares away.

## Turn 11: pirate-4

<details>
<summary>What it was shown (4514 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 4 of the game, at C1, on an undug square, with no pirate next to you. You did: dig. You dug C1 and found nothing. The treasure is 2 squares away. You were thinking: Nobody has dug this square yet.
- Turn 8 of the game, at C1, on a dug square, with no pirate next to you. You did: go_to C2. You walked north to C2. You arrived. You were thinking: The nearest square I haven't seen dug is C2.

Pirate-4, this is your turn 3 of 24, turn 12 of the game. You are at C2. Your square hasn't been dug. No way out of your square is blocked.
Squares you have dug: C1, 2 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> Nobody has dug this square yet.

**What it did**

> dig

**The result**

> You dug C2 and found nothing. The treasure is 1 square away.

## Turn 12: pirate-1

<details>
<summary>What it was shown (4702 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 1 of the game, at F3, on an undug square, with no pirate next to you. You did: dig. You dug F3 and found nothing. The treasure is 7 squares away.
- Turn 5 of the game, at F3, on a dug square, with no pirate next to you. You did: go_to F4. You walked north to F4. You arrived. You were thinking: The nearest square I haven't seen dug is F4.
- Turn 9 of the game, at F4, on an undug square, with no pirate next to you. You did: dig. You dug F4 and found nothing. The treasure is 5 squares away. You were thinking: Nobody has dug this square yet.

Pirate-1, this is your turn 4 of 24, turn 13 of the game. You are at F4. Your square has been dug and holds no cave. The way east is blocked by the island's edge.
Squares you have dug: F3, 7 away; F4, 5 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is F5.

**What it did**

> go\_to {"square": "F5"}\
> move {"direction": "north"}

**The result**

> You walked north to F5. You arrived.

## Turn 13: pirate-2

<details>
<summary>What it was shown (4703 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 2 of the game, at D6, on an undug square, with no pirate next to you. You did: dig. You dug D6 and found nothing. The treasure is 2 squares away.
- Turn 6 of the game, at D6, on a dug square, with no pirate next to you. You did: go_to C6. You walked west to C6. You arrived. You were thinking: The nearest square I haven't seen dug is C6.
- Turn 10 of the game, at C6, on an undug square, with no pirate next to you. You did: dig. You dug C6 and found nothing. The treasure is 2 squares away. You were thinking: Nobody has dug this square yet.

Pirate-2, this is your turn 4 of 24, turn 14 of the game. You are at C6. Your square has been dug and holds no cave. The way north is blocked by the island's edge.
Squares you have dug: D6, 2 away; C6, 2 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is B6.

**What it did**

> go\_to {"square": "B6"}\
> move {"direction": "west"}

**The result**

> You walked west to B6. You arrived.

## Turn 14: pirate-3

<details>
<summary>What it was shown (4703 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 3 of the game, at A4, on an undug square, with no pirate next to you. You did: dig. You dug A4 and found nothing. The treasure is 4 squares away.
- Turn 7 of the game, at A4, on a dug square, with no pirate next to you. You did: go_to A5. You walked north to A5. You arrived. You were thinking: The nearest square I haven't seen dug is A5.
- Turn 11 of the game, at A5, on an undug square, with no pirate next to you. You did: dig. You dug A5 and found nothing. The treasure is 4 squares away. You were thinking: Nobody has dug this square yet.

Pirate-3, this is your turn 4 of 24, turn 15 of the game. You are at A5. Your square has been dug and holds no cave. The way west is blocked by the island's edge.
Squares you have dug: A4, 4 away; A5, 4 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is A6.

**What it did**

> go\_to {"square": "A6"}\
> move {"direction": "north"}

**The result**

> You walked north to A6. You arrived.

## Turn 15: pirate-4

<details>
<summary>What it was shown (4694 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 4 of the game, at C1, on an undug square, with no pirate next to you. You did: dig. You dug C1 and found nothing. The treasure is 2 squares away.
- Turn 8 of the game, at C1, on a dug square, with no pirate next to you. You did: go_to C2. You walked north to C2. You arrived. You were thinking: The nearest square I haven't seen dug is C2.
- Turn 12 of the game, at C2, on an undug square, with no pirate next to you. You did: dig. You dug C2 and found nothing. The treasure is 1 square away. You were thinking: Nobody has dug this square yet.

Pirate-4, this is your turn 4 of 24, turn 16 of the game. You are at C2. Your square has been dug and holds no cave. No way out of your square is blocked.
Squares you have dug: C1, 2 away; C2, 1 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is C3.

**What it did**

> go\_to {"square": "C3"}\
> move {"direction": "north"}

**The result**

> You walked north to C3. You arrived.

## Turn 16: pirate-1

<details>
<summary>What it was shown (4818 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 1 of the game, at F3, on an undug square, with no pirate next to you. You did: dig. You dug F3 and found nothing. The treasure is 7 squares away.
- Turn 5 of the game, at F3, on a dug square, with no pirate next to you. You did: go_to F4. You walked north to F4. You arrived.
- Turn 9 of the game, at F4, on an undug square, with no pirate next to you. You did: dig. You dug F4 and found nothing. The treasure is 5 squares away. You were thinking: Nobody has dug this square yet.
- Turn 13 of the game, at F4, on a dug square, with no pirate next to you. You did: go_to F5. You walked north to F5. You arrived. You were thinking: The nearest square I haven't seen dug is F5.

Pirate-1, this is your turn 5 of 24, turn 17 of the game. You are at F5. Your square hasn't been dug. The way east is blocked by the island's edge.
Squares you have dug: F3, 7 away; F4, 5 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> Nobody has dug this square yet.

**What it did**

> dig

**The result**

> You dug F5 and found nothing. The treasure is 3 squares away.

## Turn 17: pirate-2

<details>
<summary>What it was shown (4847 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 2 of the game, at D6, on an undug square, with no pirate next to you. You did: dig. You dug D6 and found nothing. The treasure is 2 squares away.
- Turn 6 of the game, at D6, on a dug square, with no pirate next to you. You did: go_to C6. You walked west to C6. You arrived.
- Turn 10 of the game, at C6, on an undug square, with no pirate next to you. You did: dig. You dug C6 and found nothing. The treasure is 2 squares away. You were thinking: Nobody has dug this square yet.
- Turn 14 of the game, at C6, on a dug square, with no pirate next to you. You did: go_to B6. You walked west to B6. You arrived. You were thinking: The nearest square I haven't seen dug is B6.

Pirate-2, this is your turn 5 of 24, turn 18 of the game. You are at B6. Your square hasn't been dug. The way north is blocked by the island's edge and the way west by pirate-3.
Squares you have dug: D6, 2 away; C6, 2 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> Nobody has dug this square yet.

**What it did**

> dig

**The result**

> You dug B6 and found nothing. The treasure is 3 squares away.

## Turn 18: pirate-3

<details>
<summary>What it was shown (4884 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 3 of the game, at A4, on an undug square, with no pirate next to you. You did: dig. You dug A4 and found nothing. The treasure is 4 squares away.
- Turn 7 of the game, at A4, on a dug square, with no pirate next to you. You did: go_to A5. You walked north to A5. You arrived.
- Turn 11 of the game, at A5, on an undug square, with no pirate next to you. You did: dig. You dug A5 and found nothing. The treasure is 4 squares away. You were thinking: Nobody has dug this square yet.
- Turn 15 of the game, at A5, on a dug square, with no pirate next to you. You did: go_to A6. You walked north to A6. You arrived. You were thinking: The nearest square I haven't seen dug is A6.

Pirate-3, this is your turn 5 of 24, turn 19 of the game. You are at A6. Your square hasn't been dug. The way north is blocked by the island's edge, the way east by pirate-2 and the way west by the island's edge.
Squares you have dug: A4, 4 away; A5, 4 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> Nobody has dug this square yet.

**What it did**

> dig

**The result**

> You dug A6 and found nothing. The treasure is 4 squares away.

## Turn 19: pirate-4

<details>
<summary>What it was shown (4810 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 4 of the game, at C1, on an undug square, with no pirate next to you. You did: dig. You dug C1 and found nothing. The treasure is 2 squares away.
- Turn 8 of the game, at C1, on a dug square, with no pirate next to you. You did: go_to C2. You walked north to C2. You arrived.
- Turn 12 of the game, at C2, on an undug square, with no pirate next to you. You did: dig. You dug C2 and found nothing. The treasure is 1 square away. You were thinking: Nobody has dug this square yet.
- Turn 16 of the game, at C2, on a dug square, with no pirate next to you. You did: go_to C3. You walked north to C3. You arrived. You were thinking: The nearest square I haven't seen dug is C3.

Pirate-4, this is your turn 5 of 24, turn 20 of the game. You are at C3. Your square hasn't been dug. No way out of your square is blocked.
Squares you have dug: C1, 2 away; C2, 1 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> Nobody has dug this square yet.

**What it did**

> dig

**The result**

> You dug C3 and found nothing. The treasure is 2 squares away.

## Turn 20: pirate-1

<details>
<summary>What it was shown (4999 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 1 of the game, at F3, on an undug square, with no pirate next to you. You did: dig. You dug F3 and found nothing. The treasure is 7 squares away.
- Turn 5 of the game, at F3, on a dug square, with no pirate next to you. You did: go_to F4. You walked north to F4. You arrived.
- Turn 9 of the game, at F4, on an undug square, with no pirate next to you. You did: dig. You dug F4 and found nothing. The treasure is 5 squares away.
- Turn 13 of the game, at F4, on a dug square, with no pirate next to you. You did: go_to F5. You walked north to F5. You arrived. You were thinking: The nearest square I haven't seen dug is F5.
- Turn 17 of the game, at F5, on an undug square, with no pirate next to you. You did: dig. You dug F5 and found nothing. The treasure is 3 squares away. You were thinking: Nobody has dug this square yet.

Pirate-1, this is your turn 6 of 24, turn 21 of the game. You are at F5. Your square has been dug and holds no cave. The way east is blocked by the island's edge.
Squares you have dug: F3, 7 away; F4, 5 away; F5, 3 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is F6.

**What it did**

> go\_to {"square": "F6"}\
> move {"direction": "north"}

**The result**

> You walked north to F6. You arrived.

## Turn 21: pirate-2

<details>
<summary>What it was shown (5027 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 2 of the game, at D6, on an undug square, with no pirate next to you. You did: dig. You dug D6 and found nothing. The treasure is 2 squares away.
- Turn 6 of the game, at D6, on a dug square, with no pirate next to you. You did: go_to C6. You walked west to C6. You arrived.
- Turn 10 of the game, at C6, on an undug square, with no pirate next to you. You did: dig. You dug C6 and found nothing. The treasure is 2 squares away.
- Turn 14 of the game, at C6, on a dug square, with no pirate next to you. You did: go_to B6. You walked west to B6. You arrived. You were thinking: The nearest square I haven't seen dug is B6.
- Turn 18 of the game, at B6, on an undug square, with pirate-3 to the west. You did: dig. You dug B6 and found nothing. The treasure is 3 squares away. You were thinking: Nobody has dug this square yet.

Pirate-2, this is your turn 6 of 24, turn 22 of the game. You are at B6. Your square has been dug and holds no cave. The way north is blocked by the island's edge and the way west by pirate-3.
Squares you have dug: D6, 2 away; C6, 2 away; B6, 3 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is B5.

**What it did**

> go\_to {"square": "B5"}\
> move {"direction": "south"}

**The result**

> You walked south to B5. You arrived.

## Turn 22: pirate-3

<details>
<summary>What it was shown (5038 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 3 of the game, at A4, on an undug square, with no pirate next to you. You did: dig. You dug A4 and found nothing. The treasure is 4 squares away.
- Turn 7 of the game, at A4, on a dug square, with no pirate next to you. You did: go_to A5. You walked north to A5. You arrived.
- Turn 11 of the game, at A5, on an undug square, with no pirate next to you. You did: dig. You dug A5 and found nothing. The treasure is 4 squares away.
- Turn 15 of the game, at A5, on a dug square, with no pirate next to you. You did: go_to A6. You walked north to A6. You arrived. You were thinking: The nearest square I haven't seen dug is A6.
- Turn 19 of the game, at A6, on an undug square, with pirate-2 to the east. You did: dig. You dug A6 and found nothing. The treasure is 4 squares away. You were thinking: Nobody has dug this square yet.

Pirate-3, this is your turn 6 of 24, turn 23 of the game. You are at A6. Your square has been dug and holds no cave. The way north is blocked by the island's edge and the way west by the island's edge.
Squares you have dug: A4, 4 away; A5, 4 away; A6, 4 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is B6.

**What it did**

> go\_to {"square": "B6"}\
> move {"direction": "east"}

**The result**

> You walked east to B6. You arrived.

## Turn 23: pirate-4

<details>
<summary>What it was shown (4991 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 4 of the game, at C1, on an undug square, with no pirate next to you. You did: dig. You dug C1 and found nothing. The treasure is 2 squares away.
- Turn 8 of the game, at C1, on a dug square, with no pirate next to you. You did: go_to C2. You walked north to C2. You arrived.
- Turn 12 of the game, at C2, on an undug square, with no pirate next to you. You did: dig. You dug C2 and found nothing. The treasure is 1 square away.
- Turn 16 of the game, at C2, on a dug square, with no pirate next to you. You did: go_to C3. You walked north to C3. You arrived. You were thinking: The nearest square I haven't seen dug is C3.
- Turn 20 of the game, at C3, on an undug square, with no pirate next to you. You did: dig. You dug C3 and found nothing. The treasure is 2 squares away. You were thinking: Nobody has dug this square yet.

Pirate-4, this is your turn 6 of 24, turn 24 of the game. You are at C3. Your square has been dug and holds no cave. No way out of your square is blocked.
Squares you have dug: C1, 2 away; C2, 1 away; C3, 2 away.
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

## Turn 24: pirate-1

<details>
<summary>What it was shown (5154 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 1 of the game, at F3, on an undug square, with no pirate next to you. You did: dig. You dug F3 and found nothing. The treasure is 7 squares away.
- Turn 5 of the game, at F3, on a dug square, with no pirate next to you. You did: go_to F4. You walked north to F4. You arrived.
- Turn 9 of the game, at F4, on an undug square, with no pirate next to you. You did: dig. You dug F4 and found nothing. The treasure is 5 squares away.
- Turn 13 of the game, at F4, on a dug square, with no pirate next to you. You did: go_to F5. You walked north to F5. You arrived.
- Turn 17 of the game, at F5, on an undug square, with no pirate next to you. You did: dig. You dug F5 and found nothing. The treasure is 3 squares away. You were thinking: Nobody has dug this square yet.
- Turn 21 of the game, at F5, on a dug square, with no pirate next to you. You did: go_to F6. You walked north to F6. You arrived. You were thinking: The nearest square I haven't seen dug is F6.

Pirate-1, this is your turn 7 of 24, turn 25 of the game. You are at F6. Your square hasn't been dug. The way north is blocked by the island's edge and the way east by the island's edge.
Squares you have dug: F3, 7 away; F4, 5 away; F5, 3 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> Nobody has dug this square yet.

**What it did**

> dig

**The result**

> You dug F6 and found nothing. The treasure is 2 squares away.

## Turn 25: pirate-2

<details>
<summary>What it was shown (5104 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 2 of the game, at D6, on an undug square, with no pirate next to you. You did: dig. You dug D6 and found nothing. The treasure is 2 squares away.
- Turn 6 of the game, at D6, on a dug square, with no pirate next to you. You did: go_to C6. You walked west to C6. You arrived.
- Turn 10 of the game, at C6, on an undug square, with no pirate next to you. You did: dig. You dug C6 and found nothing. The treasure is 2 squares away.
- Turn 14 of the game, at C6, on a dug square, with no pirate next to you. You did: go_to B6. You walked west to B6. You arrived.
- Turn 18 of the game, at B6, on an undug square, with pirate-3 to the west. You did: dig. You dug B6 and found nothing. The treasure is 3 squares away. You were thinking: Nobody has dug this square yet.
- Turn 22 of the game, at B6, on a dug square, with pirate-3 to the west. You did: go_to B5. You walked south to B5. You arrived. You were thinking: The nearest square I haven't seen dug is B5.

Pirate-2, this is your turn 7 of 24, turn 26 of the game. You are at B5. Your square hasn't been dug. The way north is blocked by pirate-3.
Squares you have dug: D6, 2 away; C6, 2 away; B6, 3 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> Nobody has dug this square yet.

**What it did**

> dig

**The result**

> You dug B5 and found nothing. The treasure is 1 square away.

## Turn 26: pirate-3

<details>
<summary>What it was shown (5160 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 3 of the game, at A4, on an undug square, with no pirate next to you. You did: dig. You dug A4 and found nothing. The treasure is 4 squares away.
- Turn 7 of the game, at A4, on a dug square, with no pirate next to you. You did: go_to A5. You walked north to A5. You arrived.
- Turn 11 of the game, at A5, on an undug square, with no pirate next to you. You did: dig. You dug A5 and found nothing. The treasure is 4 squares away.
- Turn 15 of the game, at A5, on a dug square, with no pirate next to you. You did: go_to A6. You walked north to A6. You arrived.
- Turn 19 of the game, at A6, on an undug square, with pirate-2 to the east. You did: dig. You dug A6 and found nothing. The treasure is 4 squares away. You were thinking: Nobody has dug this square yet.
- Turn 23 of the game, at A6, on a dug square, with no pirate next to you. You did: go_to B6. You walked east to B6. You arrived. You were thinking: The nearest square I haven't seen dug is B6.

Pirate-3, this is your turn 7 of 24, turn 27 of the game. You are at B6. Your square has been dug and holds no cave. The way north is blocked by the island's edge and the way south by pirate-2.
Squares you have dug: A4, 4 away; A5, 4 away; A6, 4 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is C6.

**What it did**

> go\_to {"square": "C6"}\
> move {"direction": "east"}

**The result**

> You walked east to C6. You arrived.

## Turn 27: pirate-4

<details>
<summary>What it was shown (5107 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 4 of the game, at C1, on an undug square, with no pirate next to you. You did: dig. You dug C1 and found nothing. The treasure is 2 squares away.
- Turn 8 of the game, at C1, on a dug square, with no pirate next to you. You did: go_to C2. You walked north to C2. You arrived.
- Turn 12 of the game, at C2, on an undug square, with no pirate next to you. You did: dig. You dug C2 and found nothing. The treasure is 1 square away.
- Turn 16 of the game, at C2, on a dug square, with no pirate next to you. You did: go_to C3. You walked north to C3. You arrived.
- Turn 20 of the game, at C3, on an undug square, with no pirate next to you. You did: dig. You dug C3 and found nothing. The treasure is 2 squares away. You were thinking: Nobody has dug this square yet.
- Turn 24 of the game, at C3, on a dug square, with no pirate next to you. You did: go_to C4. You walked north to C4. You arrived. You were thinking: The nearest square I haven't seen dug is C4.

Pirate-4, this is your turn 7 of 24, turn 28 of the game. You are at C4. Your square hasn't been dug. No way out of your square is blocked.
Squares you have dug: C1, 2 away; C2, 1 away; C3, 2 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> Nobody has dug this square yet.

**What it did**

> dig

**The result**

> You dug C4 and found nothing. The treasure is 1 square away.

## Turn 28: pirate-1

<details>
<summary>What it was shown (5335 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 1 of the game, at F3, on an undug square, with no pirate next to you. You did: dig. You dug F3 and found nothing. The treasure is 7 squares away.
- Turn 5 of the game, at F3, on a dug square, with no pirate next to you. You did: go_to F4. You walked north to F4. You arrived.
- Turn 9 of the game, at F4, on an undug square, with no pirate next to you. You did: dig. You dug F4 and found nothing. The treasure is 5 squares away.
- Turn 13 of the game, at F4, on a dug square, with no pirate next to you. You did: go_to F5. You walked north to F5. You arrived.
- Turn 17 of the game, at F5, on an undug square, with no pirate next to you. You did: dig. You dug F5 and found nothing. The treasure is 3 squares away.
- Turn 21 of the game, at F5, on a dug square, with no pirate next to you. You did: go_to F6. You walked north to F6. You arrived. You were thinking: The nearest square I haven't seen dug is F6.
- Turn 25 of the game, at F6, on an undug square, with no pirate next to you. You did: dig. You dug F6 and found nothing. The treasure is 2 squares away. You were thinking: Nobody has dug this square yet.

Pirate-1, this is your turn 8 of 24, turn 29 of the game. You are at F6. Your square has been dug and holds no cave. The way north is blocked by the island's edge and the way east by the island's edge.
Squares you have dug: F3, 7 away; F4, 5 away; F5, 3 away; F6, 2 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is E6.

**What it did**

> go\_to {"square": "E6"}\
> move {"direction": "west"}

**The result**

> You walked west to E6. You arrived.

## Turn 29: pirate-2

<details>
<summary>What it was shown (5284 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 2 of the game, at D6, on an undug square, with no pirate next to you. You did: dig. You dug D6 and found nothing. The treasure is 2 squares away.
- Turn 6 of the game, at D6, on a dug square, with no pirate next to you. You did: go_to C6. You walked west to C6. You arrived.
- Turn 10 of the game, at C6, on an undug square, with no pirate next to you. You did: dig. You dug C6 and found nothing. The treasure is 2 squares away.
- Turn 14 of the game, at C6, on a dug square, with no pirate next to you. You did: go_to B6. You walked west to B6. You arrived.
- Turn 18 of the game, at B6, on an undug square, with pirate-3 to the west. You did: dig. You dug B6 and found nothing. The treasure is 3 squares away.
- Turn 22 of the game, at B6, on a dug square, with pirate-3 to the west. You did: go_to B5. You walked south to B5. You arrived. You were thinking: The nearest square I haven't seen dug is B5.
- Turn 26 of the game, at B5, on an undug square, with pirate-3 to the north. You did: dig. You dug B5 and found nothing. The treasure is 1 square away. You were thinking: Nobody has dug this square yet.

Pirate-2, this is your turn 8 of 24, turn 30 of the game. You are at B5. Your square has been dug and holds no cave. No way out of your square is blocked.
Squares you have dug: D6, 2 away; C6, 2 away; B6, 3 away; B5, 1 away.
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

## Turn 30: pirate-3

<details>
<summary>What it was shown (5273 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 3 of the game, at A4, on an undug square, with no pirate next to you. You did: dig. You dug A4 and found nothing. The treasure is 4 squares away.
- Turn 7 of the game, at A4, on a dug square, with no pirate next to you. You did: go_to A5. You walked north to A5. You arrived.
- Turn 11 of the game, at A5, on an undug square, with no pirate next to you. You did: dig. You dug A5 and found nothing. The treasure is 4 squares away.
- Turn 15 of the game, at A5, on a dug square, with no pirate next to you. You did: go_to A6. You walked north to A6. You arrived.
- Turn 19 of the game, at A6, on an undug square, with pirate-2 to the east. You did: dig. You dug A6 and found nothing. The treasure is 4 squares away.
- Turn 23 of the game, at A6, on a dug square, with no pirate next to you. You did: go_to B6. You walked east to B6. You arrived. You were thinking: The nearest square I haven't seen dug is B6.
- Turn 27 of the game, at B6, on a dug square, with pirate-2 to the south. You did: go_to C6. You walked east to C6. You arrived. You were thinking: The nearest square I haven't seen dug is C6.

Pirate-3, this is your turn 8 of 24, turn 31 of the game. You are at C6. Your square has been dug and holds no cave. The way north is blocked by the island's edge.
Squares you have dug: A4, 4 away; A5, 4 away; A6, 4 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is D6.

**What it did**

> go\_to {"square": "D6"}\
> move {"direction": "east"}

**The result**

> You walked east to D6. You arrived.

## Turn 31: pirate-4

<details>
<summary>What it was shown (5287 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 4 of the game, at C1, on an undug square, with no pirate next to you. You did: dig. You dug C1 and found nothing. The treasure is 2 squares away.
- Turn 8 of the game, at C1, on a dug square, with no pirate next to you. You did: go_to C2. You walked north to C2. You arrived.
- Turn 12 of the game, at C2, on an undug square, with no pirate next to you. You did: dig. You dug C2 and found nothing. The treasure is 1 square away.
- Turn 16 of the game, at C2, on a dug square, with no pirate next to you. You did: go_to C3. You walked north to C3. You arrived.
- Turn 20 of the game, at C3, on an undug square, with no pirate next to you. You did: dig. You dug C3 and found nothing. The treasure is 2 squares away.
- Turn 24 of the game, at C3, on a dug square, with no pirate next to you. You did: go_to C4. You walked north to C4. You arrived. You were thinking: The nearest square I haven't seen dug is C4.
- Turn 28 of the game, at C4, on an undug square, with no pirate next to you. You did: dig. You dug C4 and found nothing. The treasure is 1 square away. You were thinking: Nobody has dug this square yet.

Pirate-4, this is your turn 8 of 24, turn 32 of the game. You are at C4. Your square has been dug and holds no cave. No way out of your square is blocked.
Squares you have dug: C1, 2 away; C2, 1 away; C3, 2 away; C4, 1 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is C5.

**What it did**

> go\_to {"square": "C5"}\
> move {"direction": "north"}

**The result**

> You walked north to C5. You arrived.

## Turn 32: pirate-1

<details>
<summary>What it was shown (5441 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 1 of the game, at F3, on an undug square, with no pirate next to you. You did: dig. You dug F3 and found nothing. The treasure is 7 squares away.
- Turn 5 of the game, at F3, on a dug square, with no pirate next to you. You did: go_to F4. You walked north to F4. You arrived.
- Turn 9 of the game, at F4, on an undug square, with no pirate next to you. You did: dig. You dug F4 and found nothing. The treasure is 5 squares away.
- Turn 13 of the game, at F4, on a dug square, with no pirate next to you. You did: go_to F5. You walked north to F5. You arrived.
- Turn 17 of the game, at F5, on an undug square, with no pirate next to you. You did: dig. You dug F5 and found nothing. The treasure is 3 squares away.
- Turn 21 of the game, at F5, on a dug square, with no pirate next to you. You did: go_to F6. You walked north to F6. You arrived.
- Turn 25 of the game, at F6, on an undug square, with no pirate next to you. You did: dig. You dug F6 and found nothing. The treasure is 2 squares away. You were thinking: Nobody has dug this square yet.
- Turn 29 of the game, at F6, on a dug square, with no pirate next to you. You did: go_to E6. You walked west to E6. You arrived. You were thinking: The nearest square I haven't seen dug is E6.

Pirate-1, this is your turn 9 of 24, turn 33 of the game. You are at E6. Your square hasn't been dug. The way north is blocked by the island's edge and the way west by pirate-3.
Squares you have dug: F3, 7 away; F4, 5 away; F5, 3 away; F6, 2 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> Nobody has dug this square yet.

**What it did**

> dig

**The result**

> You dug E6 and found nothing. The treasure is 5 squares away.

## Turn 33: pirate-2

<details>
<summary>What it was shown (5422 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 2 of the game, at D6, on an undug square, with no pirate next to you. You did: dig. You dug D6 and found nothing. The treasure is 2 squares away.
- Turn 6 of the game, at D6, on a dug square, with no pirate next to you. You did: go_to C6. You walked west to C6. You arrived.
- Turn 10 of the game, at C6, on an undug square, with no pirate next to you. You did: dig. You dug C6 and found nothing. The treasure is 2 squares away.
- Turn 14 of the game, at C6, on a dug square, with no pirate next to you. You did: go_to B6. You walked west to B6. You arrived.
- Turn 18 of the game, at B6, on an undug square, with pirate-3 to the west. You did: dig. You dug B6 and found nothing. The treasure is 3 squares away.
- Turn 22 of the game, at B6, on a dug square, with pirate-3 to the west. You did: go_to B5. You walked south to B5. You arrived.
- Turn 26 of the game, at B5, on an undug square, with pirate-3 to the north. You did: dig. You dug B5 and found nothing. The treasure is 1 square away. You were thinking: Nobody has dug this square yet.
- Turn 30 of the game, at B5, on a dug square, with no pirate next to you. You did: go_to A5. You walked west to A5. You arrived. You were thinking: The nearest square I haven't seen dug is A5.

Pirate-2, this is your turn 9 of 24, turn 34 of the game. You are at A5. Your square has been dug and holds no cave. The way west is blocked by the island's edge.
Squares you have dug: D6, 2 away; C6, 2 away; B6, 3 away; B5, 1 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is A6.

**What it did**

> go\_to {"square": "A6"}\
> move {"direction": "north"}

**The result**

> You walked north to A6. You arrived.

## Turn 34: pirate-3

<details>
<summary>What it was shown (5432 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 3 of the game, at A4, on an undug square, with no pirate next to you. You did: dig. You dug A4 and found nothing. The treasure is 4 squares away.
- Turn 7 of the game, at A4, on a dug square, with no pirate next to you. You did: go_to A5. You walked north to A5. You arrived.
- Turn 11 of the game, at A5, on an undug square, with no pirate next to you. You did: dig. You dug A5 and found nothing. The treasure is 4 squares away.
- Turn 15 of the game, at A5, on a dug square, with no pirate next to you. You did: go_to A6. You walked north to A6. You arrived.
- Turn 19 of the game, at A6, on an undug square, with pirate-2 to the east. You did: dig. You dug A6 and found nothing. The treasure is 4 squares away.
- Turn 23 of the game, at A6, on a dug square, with no pirate next to you. You did: go_to B6. You walked east to B6. You arrived.
- Turn 27 of the game, at B6, on a dug square, with pirate-2 to the south. You did: go_to C6. You walked east to C6. You arrived. You were thinking: The nearest square I haven't seen dug is C6.
- Turn 31 of the game, at C6, on a dug square, with no pirate next to you. You did: go_to D6. You walked east to D6. You arrived. You were thinking: The nearest square I haven't seen dug is D6.

Pirate-3, this is your turn 9 of 24, turn 35 of the game. You are at D6. Your square has been dug and holds no cave. The way north is blocked by the island's edge and the way east by pirate-1.
Squares you have dug: A4, 4 away; A5, 4 away; A6, 4 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is D5.

**What it did**

> go\_to {"square": "D5"}\
> move {"direction": "south"}

**The result**

> You walked south to D5. You arrived.

## Turn 35: pirate-4

<details>
<summary>What it was shown (5402 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 4 of the game, at C1, on an undug square, with no pirate next to you. You did: dig. You dug C1 and found nothing. The treasure is 2 squares away.
- Turn 8 of the game, at C1, on a dug square, with no pirate next to you. You did: go_to C2. You walked north to C2. You arrived.
- Turn 12 of the game, at C2, on an undug square, with no pirate next to you. You did: dig. You dug C2 and found nothing. The treasure is 1 square away.
- Turn 16 of the game, at C2, on a dug square, with no pirate next to you. You did: go_to C3. You walked north to C3. You arrived.
- Turn 20 of the game, at C3, on an undug square, with no pirate next to you. You did: dig. You dug C3 and found nothing. The treasure is 2 squares away.
- Turn 24 of the game, at C3, on a dug square, with no pirate next to you. You did: go_to C4. You walked north to C4. You arrived.
- Turn 28 of the game, at C4, on an undug square, with no pirate next to you. You did: dig. You dug C4 and found nothing. The treasure is 1 square away. You were thinking: Nobody has dug this square yet.
- Turn 32 of the game, at C4, on a dug square, with no pirate next to you. You did: go_to C5. You walked north to C5. You arrived. You were thinking: The nearest square I haven't seen dug is C5.

Pirate-4, this is your turn 9 of 24, turn 36 of the game. You are at C5. Your square hasn't been dug. The way east is blocked by pirate-3.
Squares you have dug: C1, 2 away; C2, 1 away; C3, 2 away; C4, 1 away.
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

## Turn 36: pirate-1

<details>
<summary>What it was shown (5593 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 1 of the game, at F3, on an undug square, with no pirate next to you. You did: dig. You dug F3 and found nothing. The treasure is 7 squares away.
- Turn 5 of the game, at F3, on a dug square, with no pirate next to you. You did: go_to F4. You walked north to F4. You arrived.
- Turn 9 of the game, at F4, on an undug square, with no pirate next to you. You did: dig. You dug F4 and found nothing. The treasure is 5 squares away.
- Turn 13 of the game, at F4, on a dug square, with no pirate next to you. You did: go_to F5. You walked north to F5. You arrived.
- Turn 17 of the game, at F5, on an undug square, with no pirate next to you. You did: dig. You dug F5 and found nothing. The treasure is 3 squares away.
- Turn 21 of the game, at F5, on a dug square, with no pirate next to you. You did: go_to F6. You walked north to F6. You arrived.
- Turn 25 of the game, at F6, on an undug square, with no pirate next to you. You did: dig. You dug F6 and found nothing. The treasure is 2 squares away.
- Turn 29 of the game, at F6, on a dug square, with no pirate next to you. You did: go_to E6. You walked west to E6. You arrived. You were thinking: The nearest square I haven't seen dug is E6.
- Turn 33 of the game, at E6, on an undug square, with pirate-3 to the west. You did: dig. You dug E6 and found nothing. The treasure is 5 squares away. You were thinking: Nobody has dug this square yet.

Pirate-1, this is your turn 10 of 24, turn 37 of the game. You are at E6. Your square has been dug and holds no cave. The way north is blocked by the island's edge.
Squares you have dug: F3, 7 away; F4, 5 away; F5, 3 away; F6, 2 away; E6, 5 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is D6.

**What it did**

> go\_to {"square": "D6"}\
> move {"direction": "west"}

**The result**

> You walked west to D6. You arrived.

## Turn 37: pirate-2

<details>
<summary>What it was shown (5606 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 2 of the game, at D6, on an undug square, with no pirate next to you. You did: dig. You dug D6 and found nothing. The treasure is 2 squares away.
- Turn 6 of the game, at D6, on a dug square, with no pirate next to you. You did: go_to C6. You walked west to C6. You arrived.
- Turn 10 of the game, at C6, on an undug square, with no pirate next to you. You did: dig. You dug C6 and found nothing. The treasure is 2 squares away.
- Turn 14 of the game, at C6, on a dug square, with no pirate next to you. You did: go_to B6. You walked west to B6. You arrived.
- Turn 18 of the game, at B6, on an undug square, with pirate-3 to the west. You did: dig. You dug B6 and found nothing. The treasure is 3 squares away.
- Turn 22 of the game, at B6, on a dug square, with pirate-3 to the west. You did: go_to B5. You walked south to B5. You arrived.
- Turn 26 of the game, at B5, on an undug square, with pirate-3 to the north. You did: dig. You dug B5 and found nothing. The treasure is 1 square away.
- Turn 30 of the game, at B5, on a dug square, with no pirate next to you. You did: go_to A5. You walked west to A5. You arrived. You were thinking: The nearest square I haven't seen dug is A5.
- Turn 34 of the game, at A5, on a dug square, with no pirate next to you. You did: go_to A6. You walked north to A6. You arrived. You were thinking: The nearest square I haven't seen dug is A6.

Pirate-2, this is your turn 10 of 24, turn 38 of the game. You are at A6. Your square has been dug and holds no cave. The way north is blocked by the island's edge and the way west by the island's edge.
Squares you have dug: D6, 2 away; C6, 2 away; B6, 3 away; B5, 1 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is A4.

**What it did**

> go\_to {"square": "A4"}\
> move {"direction": "south"}

**The result**

> You set off for A4. You walked south to A5.

## Turn 38: pirate-3

<details>
<summary>What it was shown (5539 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 3 of the game, at A4, on an undug square, with no pirate next to you. You did: dig. You dug A4 and found nothing. The treasure is 4 squares away.
- Turn 7 of the game, at A4, on a dug square, with no pirate next to you. You did: go_to A5. You walked north to A5. You arrived.
- Turn 11 of the game, at A5, on an undug square, with no pirate next to you. You did: dig. You dug A5 and found nothing. The treasure is 4 squares away.
- Turn 15 of the game, at A5, on a dug square, with no pirate next to you. You did: go_to A6. You walked north to A6. You arrived.
- Turn 19 of the game, at A6, on an undug square, with pirate-2 to the east. You did: dig. You dug A6 and found nothing. The treasure is 4 squares away.
- Turn 23 of the game, at A6, on a dug square, with no pirate next to you. You did: go_to B6. You walked east to B6. You arrived.
- Turn 27 of the game, at B6, on a dug square, with pirate-2 to the south. You did: go_to C6. You walked east to C6. You arrived.
- Turn 31 of the game, at C6, on a dug square, with no pirate next to you. You did: go_to D6. You walked east to D6. You arrived. You were thinking: The nearest square I haven't seen dug is D6.
- Turn 35 of the game, at D6, on a dug square, with pirate-1 to the east. You did: go_to D5. You walked south to D5. You arrived. You were thinking: The nearest square I haven't seen dug is D5.

Pirate-3, this is your turn 10 of 24, turn 39 of the game. You are at D5. Your square hasn't been dug. The way north is blocked by pirate-1 and the way west by pirate-4.
Squares you have dug: A4, 4 away; A5, 4 away; A6, 4 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> Nobody has dug this square yet.

**What it did**

> dig

**The result**

> You dug D5 and found nothing. The treasure is 3 squares away.

## Turn 39: pirate-4

<details>
<summary>What it was shown (5621 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 4 of the game, at C1, on an undug square, with no pirate next to you. You did: dig. You dug C1 and found nothing. The treasure is 2 squares away.
- Turn 8 of the game, at C1, on a dug square, with no pirate next to you. You did: go_to C2. You walked north to C2. You arrived.
- Turn 12 of the game, at C2, on an undug square, with no pirate next to you. You did: dig. You dug C2 and found nothing. The treasure is 1 square away.
- Turn 16 of the game, at C2, on a dug square, with no pirate next to you. You did: go_to C3. You walked north to C3. You arrived.
- Turn 20 of the game, at C3, on an undug square, with no pirate next to you. You did: dig. You dug C3 and found nothing. The treasure is 2 squares away.
- Turn 24 of the game, at C3, on a dug square, with no pirate next to you. You did: go_to C4. You walked north to C4. You arrived.
- Turn 28 of the game, at C4, on an undug square, with no pirate next to you. You did: dig. You dug C4 and found nothing. The treasure is 1 square away.
- Turn 32 of the game, at C4, on a dug square, with no pirate next to you. You did: go_to C5. You walked north to C5. You arrived. You were thinking: The nearest square I haven't seen dug is C5.
- Turn 36 of the game, at C5, on an undug square, with pirate-3 to the east. You did: dig. You dug here and found the treasure! It opens a cave on this square: enter it to go in. You were thinking: Nobody has dug this square yet.

Pirate-4, this is your turn 10 of 24, turn 40 of the game. You are at C5. You are standing on the open cave: enter it to go in. The way east is blocked by pirate-3.
Squares you have dug: C1, 2 away; C2, 1 away; C3, 2 away; C4, 1 away; C5, the cave.
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

## Turn 40: pirate-1

<details>
<summary>What it was shown (5753 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 1 of the game, at F3, on an undug square, with no pirate next to you. You did: dig. You dug F3 and found nothing. The treasure is 7 squares away.
- Turn 5 of the game, at F3, on a dug square, with no pirate next to you. You did: go_to F4. You walked north to F4. You arrived.
- Turn 9 of the game, at F4, on an undug square, with no pirate next to you. You did: dig. You dug F4 and found nothing. The treasure is 5 squares away.
- Turn 13 of the game, at F4, on a dug square, with no pirate next to you. You did: go_to F5. You walked north to F5. You arrived.
- Turn 17 of the game, at F5, on an undug square, with no pirate next to you. You did: dig. You dug F5 and found nothing. The treasure is 3 squares away.
- Turn 21 of the game, at F5, on a dug square, with no pirate next to you. You did: go_to F6. You walked north to F6. You arrived.
- Turn 25 of the game, at F6, on an undug square, with no pirate next to you. You did: dig. You dug F6 and found nothing. The treasure is 2 squares away.
- Turn 29 of the game, at F6, on a dug square, with no pirate next to you. You did: go_to E6. You walked west to E6. You arrived.
- Turn 33 of the game, at E6, on an undug square, with pirate-3 to the west. You did: dig. You dug E6 and found nothing. The treasure is 5 squares away. You were thinking: Nobody has dug this square yet.
- Turn 37 of the game, at E6, on a dug square, with no pirate next to you. You did: go_to D6. You walked west to D6. You arrived. You were thinking: The nearest square I haven't seen dug is D6.

Pirate-1, this is your turn 11 of 24, turn 41 of the game. You are at D6. Your square has been dug and holds no cave. The way north is blocked by the island's edge and the way south by pirate-3.
Squares you have dug: F3, 7 away; F4, 5 away; F5, 3 away; F6, 2 away; E6, 5 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is C6.

**What it did**

> go\_to {"square": "C6"}\
> move {"direction": "west"}

**The result**

> You walked west to C6. You arrived.

## Turn 41: pirate-2

*Walked under an order: its brain wasn't asked.*

**Its thinking**

*No thinking recorded.*

**What it did**

> move {"direction": "south"}

**The result**

> You walked south to A4.

## Turn 42: pirate-3

<details>
<summary>What it was shown (5703 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 3 of the game, at A4, on an undug square, with no pirate next to you. You did: dig. You dug A4 and found nothing. The treasure is 4 squares away.
- Turn 7 of the game, at A4, on a dug square, with no pirate next to you. You did: go_to A5. You walked north to A5. You arrived.
- Turn 11 of the game, at A5, on an undug square, with no pirate next to you. You did: dig. You dug A5 and found nothing. The treasure is 4 squares away.
- Turn 15 of the game, at A5, on a dug square, with no pirate next to you. You did: go_to A6. You walked north to A6. You arrived.
- Turn 19 of the game, at A6, on an undug square, with pirate-2 to the east. You did: dig. You dug A6 and found nothing. The treasure is 4 squares away.
- Turn 23 of the game, at A6, on a dug square, with no pirate next to you. You did: go_to B6. You walked east to B6. You arrived.
- Turn 27 of the game, at B6, on a dug square, with pirate-2 to the south. You did: go_to C6. You walked east to C6. You arrived.
- Turn 31 of the game, at C6, on a dug square, with no pirate next to you. You did: go_to D6. You walked east to D6. You arrived.
- Turn 35 of the game, at D6, on a dug square, with pirate-1 to the east. You did: go_to D5. You walked south to D5. You arrived. You were thinking: The nearest square I haven't seen dug is D5.
- Turn 39 of the game, at D5, on an undug square, with pirate-1 to the north and pirate-4 to the west. You did: dig. You dug D5 and found nothing. The treasure is 3 squares away. You were thinking: Nobody has dug this square yet.

Pirate-3, this is your turn 11 of 24, turn 43 of the game. You are at D5. Your square has been dug and holds no cave. No way out of your square is blocked.
Squares you have dug: A4, 4 away; A5, 4 away; A6, 4 away; D5, 3 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is C5.

**What it did**

> go\_to {"square": "C5"}\
> move {"direction": "west"}

**The result**

> You walked west to C5. You arrived.

## Turn 43: pirate-1

<details>
<summary>What it was shown (5896 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 1 of the game, at F3, on an undug square, with no pirate next to you. You did: dig. You dug F3 and found nothing. The treasure is 7 squares away.
- Turn 5 of the game, at F3, on a dug square, with no pirate next to you. You did: go_to F4. You walked north to F4. You arrived.
- Turn 9 of the game, at F4, on an undug square, with no pirate next to you. You did: dig. You dug F4 and found nothing. The treasure is 5 squares away.
- Turn 13 of the game, at F4, on a dug square, with no pirate next to you. You did: go_to F5. You walked north to F5. You arrived.
- Turn 17 of the game, at F5, on an undug square, with no pirate next to you. You did: dig. You dug F5 and found nothing. The treasure is 3 squares away.
- Turn 21 of the game, at F5, on a dug square, with no pirate next to you. You did: go_to F6. You walked north to F6. You arrived.
- Turn 25 of the game, at F6, on an undug square, with no pirate next to you. You did: dig. You dug F6 and found nothing. The treasure is 2 squares away.
- Turn 29 of the game, at F6, on a dug square, with no pirate next to you. You did: go_to E6. You walked west to E6. You arrived.
- Turn 33 of the game, at E6, on an undug square, with pirate-3 to the west. You did: dig. You dug E6 and found nothing. The treasure is 5 squares away.
- Turn 37 of the game, at E6, on a dug square, with no pirate next to you. You did: go_to D6. You walked west to D6. You arrived. You were thinking: The nearest square I haven't seen dug is D6.
- Turn 41 of the game, at D6, on a dug square, with pirate-3 to the south. You did: go_to C6. You walked west to C6. You arrived. You were thinking: The nearest square I haven't seen dug is C6.

Pirate-1, this is your turn 12 of 24, turn 44 of the game. You are at C6. Your square has been dug and holds no cave. The way north is blocked by the island's edge and the way south by pirate-3.
Squares you have dug: F3, 7 away; F4, 5 away; F5, 3 away; F6, 2 away; E6, 5 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is B6.

**What it did**

> go\_to {"square": "B6"}\
> move {"direction": "west"}

**The result**

> You walked west to B6. You arrived.

## Turn 44: pirate-2

<details>
<summary>What it was shown (5763 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 2 of the game, at D6, on an undug square, with no pirate next to you. You did: dig. You dug D6 and found nothing. The treasure is 2 squares away.
- Turn 6 of the game, at D6, on a dug square, with no pirate next to you. You did: go_to C6. You walked west to C6. You arrived.
- Turn 10 of the game, at C6, on an undug square, with no pirate next to you. You did: dig. You dug C6 and found nothing. The treasure is 2 squares away.
- Turn 14 of the game, at C6, on a dug square, with no pirate next to you. You did: go_to B6. You walked west to B6. You arrived.
- Turn 18 of the game, at B6, on an undug square, with pirate-3 to the west. You did: dig. You dug B6 and found nothing. The treasure is 3 squares away.
- Turn 22 of the game, at B6, on a dug square, with pirate-3 to the west. You did: go_to B5. You walked south to B5. You arrived.
- Turn 26 of the game, at B5, on an undug square, with pirate-3 to the north. You did: dig. You dug B5 and found nothing. The treasure is 1 square away.
- Turn 30 of the game, at B5, on a dug square, with no pirate next to you. You did: go_to A5. You walked west to A5. You arrived.
- Turn 34 of the game, at A5, on a dug square, with no pirate next to you. You did: go_to A6. You walked north to A6. You arrived. You were thinking: The nearest square I haven't seen dug is A6.
- Turn 38 of the game, at A6, on a dug square, with no pirate next to you. You did: go_to A4. You set off for A4. You walked south to A5. You walked from A6 to A4 over 2 turns. You were thinking: The nearest square I haven't seen dug is A4.

Pirate-2, this is your turn 12 of 24, turn 45 of the game. You are at A4. Your square has been dug and holds no cave. The way west is blocked by the island's edge.
You arrived at A4.
Squares you have dug: D6, 2 away; C6, 2 away; B6, 3 away; B5, 1 away.
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

## Turn 45: pirate-3

<details>
<summary>What it was shown (5843 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 3 of the game, at A4, on an undug square, with no pirate next to you. You did: dig. You dug A4 and found nothing. The treasure is 4 squares away.
- Turn 7 of the game, at A4, on a dug square, with no pirate next to you. You did: go_to A5. You walked north to A5. You arrived.
- Turn 11 of the game, at A5, on an undug square, with no pirate next to you. You did: dig. You dug A5 and found nothing. The treasure is 4 squares away.
- Turn 15 of the game, at A5, on a dug square, with no pirate next to you. You did: go_to A6. You walked north to A6. You arrived.
- Turn 19 of the game, at A6, on an undug square, with pirate-2 to the east. You did: dig. You dug A6 and found nothing. The treasure is 4 squares away.
- Turn 23 of the game, at A6, on a dug square, with no pirate next to you. You did: go_to B6. You walked east to B6. You arrived.
- Turn 27 of the game, at B6, on a dug square, with pirate-2 to the south. You did: go_to C6. You walked east to C6. You arrived.
- Turn 31 of the game, at C6, on a dug square, with no pirate next to you. You did: go_to D6. You walked east to D6. You arrived.
- Turn 35 of the game, at D6, on a dug square, with pirate-1 to the east. You did: go_to D5. You walked south to D5. You arrived.
- Turn 39 of the game, at D5, on an undug square, with pirate-1 to the north and pirate-4 to the west. You did: dig. You dug D5 and found nothing. The treasure is 3 squares away. You were thinking: Nobody has dug this square yet.
- Turn 43 of the game, at D5, on a dug square, with no pirate next to you. You did: go_to C5. You walked west to C5. You arrived. You were thinking: The nearest square I haven't seen dug is C5.

Pirate-3, this is your turn 12 of 24, turn 46 of the game. You are at C5. You are standing on the open cave: enter it to go in. No way out of your square is blocked.
Squares you have dug: A4, 4 away; A5, 4 away; A6, 4 away; D5, 3 away.
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

## Turn 46: pirate-1

<details>
<summary>What it was shown (5996 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 1 of the game, at F3, on an undug square, with no pirate next to you. You did: dig. You dug F3 and found nothing. The treasure is 7 squares away.
- Turn 5 of the game, at F3, on a dug square, with no pirate next to you. You did: go_to F4. You walked north to F4. You arrived.
- Turn 9 of the game, at F4, on an undug square, with no pirate next to you. You did: dig. You dug F4 and found nothing. The treasure is 5 squares away.
- Turn 13 of the game, at F4, on a dug square, with no pirate next to you. You did: go_to F5. You walked north to F5. You arrived.
- Turn 17 of the game, at F5, on an undug square, with no pirate next to you. You did: dig. You dug F5 and found nothing. The treasure is 3 squares away.
- Turn 21 of the game, at F5, on a dug square, with no pirate next to you. You did: go_to F6. You walked north to F6. You arrived.
- Turn 25 of the game, at F6, on an undug square, with no pirate next to you. You did: dig. You dug F6 and found nothing. The treasure is 2 squares away.
- Turn 29 of the game, at F6, on a dug square, with no pirate next to you. You did: go_to E6. You walked west to E6. You arrived.
- Turn 33 of the game, at E6, on an undug square, with pirate-3 to the west. You did: dig. You dug E6 and found nothing. The treasure is 5 squares away.
- Turn 37 of the game, at E6, on a dug square, with no pirate next to you. You did: go_to D6. You walked west to D6. You arrived.
- Turn 41 of the game, at D6, on a dug square, with pirate-3 to the south. You did: go_to C6. You walked west to C6. You arrived. You were thinking: The nearest square I haven't seen dug is C6.
- Turn 44 of the game, at C6, on a dug square, with pirate-3 to the south. You did: go_to B6. You walked west to B6. You arrived. You were thinking: The nearest square I haven't seen dug is B6.

Pirate-1, this is your turn 13 of 24, turn 47 of the game. You are at B6. Your square has been dug and holds no cave. The way north is blocked by the island's edge.
Squares you have dug: F3, 7 away; F4, 5 away; F5, 3 away; F6, 2 away; E6, 5 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is A6.

**What it did**

> go\_to {"square": "A6"}\
> move {"direction": "west"}

**The result**

> You walked west to A6. You arrived.

## Turn 47: pirate-2

<details>
<summary>What it was shown (5870 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 2 of the game, at D6, on an undug square, with no pirate next to you. You did: dig. You dug D6 and found nothing. The treasure is 2 squares away.
- Turn 6 of the game, at D6, on a dug square, with no pirate next to you. You did: go_to C6. You walked west to C6. You arrived.
- Turn 10 of the game, at C6, on an undug square, with no pirate next to you. You did: dig. You dug C6 and found nothing. The treasure is 2 squares away.
- Turn 14 of the game, at C6, on a dug square, with no pirate next to you. You did: go_to B6. You walked west to B6. You arrived.
- Turn 18 of the game, at B6, on an undug square, with pirate-3 to the west. You did: dig. You dug B6 and found nothing. The treasure is 3 squares away.
- Turn 22 of the game, at B6, on a dug square, with pirate-3 to the west. You did: go_to B5. You walked south to B5. You arrived.
- Turn 26 of the game, at B5, on an undug square, with pirate-3 to the north. You did: dig. You dug B5 and found nothing. The treasure is 1 square away.
- Turn 30 of the game, at B5, on a dug square, with no pirate next to you. You did: go_to A5. You walked west to A5. You arrived.
- Turn 34 of the game, at A5, on a dug square, with no pirate next to you. You did: go_to A6. You walked north to A6. You arrived.
- Turn 38 of the game, at A6, on a dug square, with no pirate next to you. You did: go_to A4. You set off for A4. You walked south to A5. You walked from A6 to A4 over 2 turns. You were thinking: The nearest square I haven't seen dug is A4.
- Turn 45 of the game, at A4, on a dug square, with no pirate next to you. You arrived at A4. You did: go_to B4. You walked east to B4. You arrived. You were thinking: The nearest square I haven't seen dug is B4.

Pirate-2, this is your turn 13 of 24, turn 48 of the game. You are at B4. Your square hasn't been dug. No way out of your square is blocked.
Squares you have dug: D6, 2 away; C6, 2 away; B6, 3 away; B5, 1 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> Nobody has dug this square yet.

**What it did**

> dig

**The result**

> You dug B4 and found nothing. The treasure is 4 squares away.

## Turn 48: pirate-1

<details>
<summary>What it was shown (6164 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 1 of the game, at F3, on an undug square, with no pirate next to you. You did: dig. You dug F3 and found nothing. The treasure is 7 squares away.
- Turn 5 of the game, at F3, on a dug square, with no pirate next to you. You did: go_to F4. You walked north to F4. You arrived.
- Turn 9 of the game, at F4, on an undug square, with no pirate next to you. You did: dig. You dug F4 and found nothing. The treasure is 5 squares away.
- Turn 13 of the game, at F4, on a dug square, with no pirate next to you. You did: go_to F5. You walked north to F5. You arrived.
- Turn 17 of the game, at F5, on an undug square, with no pirate next to you. You did: dig. You dug F5 and found nothing. The treasure is 3 squares away.
- Turn 21 of the game, at F5, on a dug square, with no pirate next to you. You did: go_to F6. You walked north to F6. You arrived.
- Turn 25 of the game, at F6, on an undug square, with no pirate next to you. You did: dig. You dug F6 and found nothing. The treasure is 2 squares away.
- Turn 29 of the game, at F6, on a dug square, with no pirate next to you. You did: go_to E6. You walked west to E6. You arrived.
- Turn 33 of the game, at E6, on an undug square, with pirate-3 to the west. You did: dig. You dug E6 and found nothing. The treasure is 5 squares away.
- Turn 37 of the game, at E6, on a dug square, with no pirate next to you. You did: go_to D6. You walked west to D6. You arrived.
- Turn 41 of the game, at D6, on a dug square, with pirate-3 to the south. You did: go_to C6. You walked west to C6. You arrived.
- Turn 44 of the game, at C6, on a dug square, with pirate-3 to the south. You did: go_to B6. You walked west to B6. You arrived. You were thinking: The nearest square I haven't seen dug is B6.
- Turn 47 of the game, at B6, on a dug square, with no pirate next to you. You did: go_to A6. You walked west to A6. You arrived. You were thinking: The nearest square I haven't seen dug is A6.

Pirate-1, this is your turn 14 of 24, turn 49 of the game. You are at A6. Your square has been dug and holds no cave. The way north is blocked by the island's edge and the way west by the island's edge.
Squares you have dug: F3, 7 away; F4, 5 away; F5, 3 away; F6, 2 away; E6, 5 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is A5.

**What it did**

> go\_to {"square": "A5"}\
> move {"direction": "south"}

**The result**

> You walked south to A5. You arrived.

## Turn 49: pirate-2

<details>
<summary>What it was shown (6038 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 2 of the game, at D6, on an undug square, with no pirate next to you. You did: dig. You dug D6 and found nothing. The treasure is 2 squares away.
- Turn 6 of the game, at D6, on a dug square, with no pirate next to you. You did: go_to C6. You walked west to C6. You arrived.
- Turn 10 of the game, at C6, on an undug square, with no pirate next to you. You did: dig. You dug C6 and found nothing. The treasure is 2 squares away.
- Turn 14 of the game, at C6, on a dug square, with no pirate next to you. You did: go_to B6. You walked west to B6. You arrived.
- Turn 18 of the game, at B6, on an undug square, with pirate-3 to the west. You did: dig. You dug B6 and found nothing. The treasure is 3 squares away.
- Turn 22 of the game, at B6, on a dug square, with pirate-3 to the west. You did: go_to B5. You walked south to B5. You arrived.
- Turn 26 of the game, at B5, on an undug square, with pirate-3 to the north. You did: dig. You dug B5 and found nothing. The treasure is 1 square away.
- Turn 30 of the game, at B5, on a dug square, with no pirate next to you. You did: go_to A5. You walked west to A5. You arrived.
- Turn 34 of the game, at A5, on a dug square, with no pirate next to you. You did: go_to A6. You walked north to A6. You arrived.
- Turn 38 of the game, at A6, on a dug square, with no pirate next to you. You did: go_to A4. You set off for A4. You walked south to A5. You walked from A6 to A4 over 2 turns.
- Turn 45 of the game, at A4, on a dug square, with no pirate next to you. You arrived at A4. You did: go_to B4. You walked east to B4. You arrived. You were thinking: The nearest square I haven't seen dug is B4.
- Turn 48 of the game, at B4, on an undug square, with no pirate next to you. You did: dig. You dug B4 and found nothing. The treasure is 4 squares away. You were thinking: Nobody has dug this square yet.

Pirate-2, this is your turn 14 of 24, turn 50 of the game. You are at B4. Your square has been dug and holds no cave. No way out of your square is blocked.
Squares you have dug: D6, 2 away; C6, 2 away; B6, 3 away; B5, 1 away; B4, 4 away.
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

## Turn 50: pirate-1

<details>
<summary>What it was shown (6256 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 1 of the game, at F3, on an undug square, with no pirate next to you. You did: dig. You dug F3 and found nothing. The treasure is 7 squares away.
- Turn 5 of the game, at F3, on a dug square, with no pirate next to you. You did: go_to F4. You walked north to F4. You arrived.
- Turn 9 of the game, at F4, on an undug square, with no pirate next to you. You did: dig. You dug F4 and found nothing. The treasure is 5 squares away.
- Turn 13 of the game, at F4, on a dug square, with no pirate next to you. You did: go_to F5. You walked north to F5. You arrived.
- Turn 17 of the game, at F5, on an undug square, with no pirate next to you. You did: dig. You dug F5 and found nothing. The treasure is 3 squares away.
- Turn 21 of the game, at F5, on a dug square, with no pirate next to you. You did: go_to F6. You walked north to F6. You arrived.
- Turn 25 of the game, at F6, on an undug square, with no pirate next to you. You did: dig. You dug F6 and found nothing. The treasure is 2 squares away.
- Turn 29 of the game, at F6, on a dug square, with no pirate next to you. You did: go_to E6. You walked west to E6. You arrived.
- Turn 33 of the game, at E6, on an undug square, with pirate-3 to the west. You did: dig. You dug E6 and found nothing. The treasure is 5 squares away.
- Turn 37 of the game, at E6, on a dug square, with no pirate next to you. You did: go_to D6. You walked west to D6. You arrived.
- Turn 41 of the game, at D6, on a dug square, with pirate-3 to the south. You did: go_to C6. You walked west to C6. You arrived.
- Turn 44 of the game, at C6, on a dug square, with pirate-3 to the south. You did: go_to B6. You walked west to B6. You arrived.
- Turn 47 of the game, at B6, on a dug square, with no pirate next to you. You did: go_to A6. You walked west to A6. You arrived. You were thinking: The nearest square I haven't seen dug is A6.
- Turn 49 of the game, at A6, on a dug square, with no pirate next to you. You did: go_to A5. You walked south to A5. You arrived. You were thinking: The nearest square I haven't seen dug is A5.

Pirate-1, this is your turn 15 of 24, turn 51 of the game. You are at A5. Your square has been dug and holds no cave. The way west is blocked by the island's edge.
Squares you have dug: F3, 7 away; F4, 5 away; F5, 3 away; F6, 2 away; E6, 5 away.
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

## Turn 51: pirate-2

<details>
<summary>What it was shown (6168 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 2 of the game, at D6, on an undug square, with no pirate next to you. You did: dig. You dug D6 and found nothing. The treasure is 2 squares away.
- Turn 6 of the game, at D6, on a dug square, with no pirate next to you. You did: go_to C6. You walked west to C6. You arrived.
- Turn 10 of the game, at C6, on an undug square, with no pirate next to you. You did: dig. You dug C6 and found nothing. The treasure is 2 squares away.
- Turn 14 of the game, at C6, on a dug square, with no pirate next to you. You did: go_to B6. You walked west to B6. You arrived.
- Turn 18 of the game, at B6, on an undug square, with pirate-3 to the west. You did: dig. You dug B6 and found nothing. The treasure is 3 squares away.
- Turn 22 of the game, at B6, on a dug square, with pirate-3 to the west. You did: go_to B5. You walked south to B5. You arrived.
- Turn 26 of the game, at B5, on an undug square, with pirate-3 to the north. You did: dig. You dug B5 and found nothing. The treasure is 1 square away.
- Turn 30 of the game, at B5, on a dug square, with no pirate next to you. You did: go_to A5. You walked west to A5. You arrived.
- Turn 34 of the game, at A5, on a dug square, with no pirate next to you. You did: go_to A6. You walked north to A6. You arrived.
- Turn 38 of the game, at A6, on a dug square, with no pirate next to you. You did: go_to A4. You set off for A4. You walked south to A5. You walked from A6 to A4 over 2 turns.
- Turn 45 of the game, at A4, on a dug square, with no pirate next to you. You arrived at A4. You did: go_to B4. You walked east to B4. You arrived.
- Turn 48 of the game, at B4, on an undug square, with no pirate next to you. You did: dig. You dug B4 and found nothing. The treasure is 4 squares away. You were thinking: Nobody has dug this square yet.
- Turn 50 of the game, at B4, on a dug square, with no pirate next to you. You did: go_to C4. You walked east to C4. You arrived. You were thinking: The nearest square I haven't seen dug is C4.

Pirate-2, this is your turn 15 of 24, turn 52 of the game. You are at C4. Your square has been dug and holds no cave. No way out of your square is blocked.
Squares you have dug: D6, 2 away; C6, 2 away; B6, 3 away; B5, 1 away; B4, 4 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is C5.

**What it did**

> go\_to {"square": "C5"}\
> move {"direction": "north"}

**The result**

> You walked north to C5. You arrived.

## Turn 52: pirate-1

<details>
<summary>What it was shown (6377 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 1 of the game, at F3, on an undug square, with no pirate next to you. You did: dig. You dug F3 and found nothing. The treasure is 7 squares away.
- Turn 5 of the game, at F3, on a dug square, with no pirate next to you. You did: go_to F4. You walked north to F4. You arrived.
- Turn 9 of the game, at F4, on an undug square, with no pirate next to you. You did: dig. You dug F4 and found nothing. The treasure is 5 squares away.
- Turn 13 of the game, at F4, on a dug square, with no pirate next to you. You did: go_to F5. You walked north to F5. You arrived.
- Turn 17 of the game, at F5, on an undug square, with no pirate next to you. You did: dig. You dug F5 and found nothing. The treasure is 3 squares away.
- Turn 21 of the game, at F5, on a dug square, with no pirate next to you. You did: go_to F6. You walked north to F6. You arrived.
- Turn 25 of the game, at F6, on an undug square, with no pirate next to you. You did: dig. You dug F6 and found nothing. The treasure is 2 squares away.
- Turn 29 of the game, at F6, on a dug square, with no pirate next to you. You did: go_to E6. You walked west to E6. You arrived.
- Turn 33 of the game, at E6, on an undug square, with pirate-3 to the west. You did: dig. You dug E6 and found nothing. The treasure is 5 squares away.
- Turn 37 of the game, at E6, on a dug square, with no pirate next to you. You did: go_to D6. You walked west to D6. You arrived.
- Turn 41 of the game, at D6, on a dug square, with pirate-3 to the south. You did: go_to C6. You walked west to C6. You arrived.
- Turn 44 of the game, at C6, on a dug square, with pirate-3 to the south. You did: go_to B6. You walked west to B6. You arrived.
- Turn 47 of the game, at B6, on a dug square, with no pirate next to you. You did: go_to A6. You walked west to A6. You arrived.
- Turn 49 of the game, at A6, on a dug square, with no pirate next to you. You did: go_to A5. You walked south to A5. You arrived. You were thinking: The nearest square I haven't seen dug is A5.
- Turn 51 of the game, at A5, on a dug square, with no pirate next to you. You did: go_to B5. You walked east to B5. You arrived. You were thinking: The nearest square I haven't seen dug is B5.

Pirate-1, this is your turn 16 of 24, turn 53 of the game. You are at B5. Your square has been dug and holds no cave. The way east is blocked by pirate-2.
Squares you have dug: F3, 7 away; F4, 5 away; F5, 3 away; F6, 2 away; E6, 5 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is B4.

**What it did**

> go\_to {"square": "B4"}\
> move {"direction": "south"}

**The result**

> You walked south to B4. You arrived.

## Turn 53: pirate-2

<details>
<summary>What it was shown (6322 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 2 of the game, at D6, on an undug square, with no pirate next to you. You did: dig. You dug D6 and found nothing. The treasure is 2 squares away.
- Turn 6 of the game, at D6, on a dug square, with no pirate next to you. You did: go_to C6. You walked west to C6. You arrived.
- Turn 10 of the game, at C6, on an undug square, with no pirate next to you. You did: dig. You dug C6 and found nothing. The treasure is 2 squares away.
- Turn 14 of the game, at C6, on a dug square, with no pirate next to you. You did: go_to B6. You walked west to B6. You arrived.
- Turn 18 of the game, at B6, on an undug square, with pirate-3 to the west. You did: dig. You dug B6 and found nothing. The treasure is 3 squares away.
- Turn 22 of the game, at B6, on a dug square, with pirate-3 to the west. You did: go_to B5. You walked south to B5. You arrived.
- Turn 26 of the game, at B5, on an undug square, with pirate-3 to the north. You did: dig. You dug B5 and found nothing. The treasure is 1 square away.
- Turn 30 of the game, at B5, on a dug square, with no pirate next to you. You did: go_to A5. You walked west to A5. You arrived.
- Turn 34 of the game, at A5, on a dug square, with no pirate next to you. You did: go_to A6. You walked north to A6. You arrived.
- Turn 38 of the game, at A6, on a dug square, with no pirate next to you. You did: go_to A4. You set off for A4. You walked south to A5. You walked from A6 to A4 over 2 turns.
- Turn 45 of the game, at A4, on a dug square, with no pirate next to you. You arrived at A4. You did: go_to B4. You walked east to B4. You arrived.
- Turn 48 of the game, at B4, on an undug square, with no pirate next to you. You did: dig. You dug B4 and found nothing. The treasure is 4 squares away.
- Turn 50 of the game, at B4, on a dug square, with no pirate next to you. You did: go_to C4. You walked east to C4. You arrived. You were thinking: The nearest square I haven't seen dug is C4.
- Turn 52 of the game, at C4, on a dug square, with no pirate next to you. You did: go_to C5. You walked north to C5. You arrived. You were thinking: The nearest square I haven't seen dug is C5.

Pirate-2, this is your turn 16 of 24, turn 54 of the game. You are at C5. You are standing on the open cave: enter it to go in. No way out of your square is blocked.
Squares you have dug: D6, 2 away; C6, 2 away; B6, 3 away; B5, 1 away; B4, 4 away.
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

## Turn 54: pirate-1

<details>
<summary>What it was shown (6508 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 1 of the game, at F3, on an undug square, with no pirate next to you. You did: dig. You dug F3 and found nothing. The treasure is 7 squares away.
- Turn 5 of the game, at F3, on a dug square, with no pirate next to you. You did: go_to F4. You walked north to F4. You arrived.
- Turn 9 of the game, at F4, on an undug square, with no pirate next to you. You did: dig. You dug F4 and found nothing. The treasure is 5 squares away.
- Turn 13 of the game, at F4, on a dug square, with no pirate next to you. You did: go_to F5. You walked north to F5. You arrived.
- Turn 17 of the game, at F5, on an undug square, with no pirate next to you. You did: dig. You dug F5 and found nothing. The treasure is 3 squares away.
- Turn 21 of the game, at F5, on a dug square, with no pirate next to you. You did: go_to F6. You walked north to F6. You arrived.
- Turn 25 of the game, at F6, on an undug square, with no pirate next to you. You did: dig. You dug F6 and found nothing. The treasure is 2 squares away.
- Turn 29 of the game, at F6, on a dug square, with no pirate next to you. You did: go_to E6. You walked west to E6. You arrived.
- Turn 33 of the game, at E6, on an undug square, with pirate-3 to the west. You did: dig. You dug E6 and found nothing. The treasure is 5 squares away.
- Turn 37 of the game, at E6, on a dug square, with no pirate next to you. You did: go_to D6. You walked west to D6. You arrived.
- Turn 41 of the game, at D6, on a dug square, with pirate-3 to the south. You did: go_to C6. You walked west to C6. You arrived.
- Turn 44 of the game, at C6, on a dug square, with pirate-3 to the south. You did: go_to B6. You walked west to B6. You arrived.
- Turn 47 of the game, at B6, on a dug square, with no pirate next to you. You did: go_to A6. You walked west to A6. You arrived.
- Turn 49 of the game, at A6, on a dug square, with no pirate next to you. You did: go_to A5. You walked south to A5. You arrived.
- Turn 51 of the game, at A5, on a dug square, with no pirate next to you. You did: go_to B5. You walked east to B5. You arrived. You were thinking: The nearest square I haven't seen dug is B5.
- Turn 53 of the game, at B5, on a dug square, with pirate-2 to the east. You did: go_to B4. You walked south to B4. You arrived. You were thinking: The nearest square I haven't seen dug is B4.

Pirate-1, this is your turn 17 of 24, turn 55 of the game. You are at B4. Your square has been dug and holds no cave. No way out of your square is blocked.
Squares you have dug: F3, 7 away; F4, 5 away; F5, 3 away; F6, 2 away; E6, 5 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is A4.

**What it did**

> go\_to {"square": "A4"}\
> move {"direction": "west"}

**The result**

> You walked west to A4. You arrived.

## Turn 55: pirate-1

<details>
<summary>What it was shown (6646 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 1 of the game, at F3, on an undug square, with no pirate next to you. You did: dig. You dug F3 and found nothing. The treasure is 7 squares away.
- Turn 5 of the game, at F3, on a dug square, with no pirate next to you. You did: go_to F4. You walked north to F4. You arrived.
- Turn 9 of the game, at F4, on an undug square, with no pirate next to you. You did: dig. You dug F4 and found nothing. The treasure is 5 squares away.
- Turn 13 of the game, at F4, on a dug square, with no pirate next to you. You did: go_to F5. You walked north to F5. You arrived.
- Turn 17 of the game, at F5, on an undug square, with no pirate next to you. You did: dig. You dug F5 and found nothing. The treasure is 3 squares away.
- Turn 21 of the game, at F5, on a dug square, with no pirate next to you. You did: go_to F6. You walked north to F6. You arrived.
- Turn 25 of the game, at F6, on an undug square, with no pirate next to you. You did: dig. You dug F6 and found nothing. The treasure is 2 squares away.
- Turn 29 of the game, at F6, on a dug square, with no pirate next to you. You did: go_to E6. You walked west to E6. You arrived.
- Turn 33 of the game, at E6, on an undug square, with pirate-3 to the west. You did: dig. You dug E6 and found nothing. The treasure is 5 squares away.
- Turn 37 of the game, at E6, on a dug square, with no pirate next to you. You did: go_to D6. You walked west to D6. You arrived.
- Turn 41 of the game, at D6, on a dug square, with pirate-3 to the south. You did: go_to C6. You walked west to C6. You arrived.
- Turn 44 of the game, at C6, on a dug square, with pirate-3 to the south. You did: go_to B6. You walked west to B6. You arrived.
- Turn 47 of the game, at B6, on a dug square, with no pirate next to you. You did: go_to A6. You walked west to A6. You arrived.
- Turn 49 of the game, at A6, on a dug square, with no pirate next to you. You did: go_to A5. You walked south to A5. You arrived.
- Turn 51 of the game, at A5, on a dug square, with no pirate next to you. You did: go_to B5. You walked east to B5. You arrived.
- Turn 53 of the game, at B5, on a dug square, with pirate-2 to the east. You did: go_to B4. You walked south to B4. You arrived. You were thinking: The nearest square I haven't seen dug is B4.
- Turn 55 of the game, at B4, on a dug square, with no pirate next to you. You did: go_to A4. You walked west to A4. You arrived. You were thinking: The nearest square I haven't seen dug is A4.

Pirate-1, this is your turn 18 of 24, turn 56 of the game. You are at A4. Your square has been dug and holds no cave. The way west is blocked by the island's edge.
Squares you have dug: F3, 7 away; F4, 5 away; F5, 3 away; F6, 2 away; E6, 5 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is A3.

**What it did**

> go\_to {"square": "A3"}\
> move {"direction": "south"}

**The result**

> You walked south to A3. You arrived.

## Turn 56: pirate-1

<details>
<summary>What it was shown (6762 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 1 of the game, at F3, on an undug square, with no pirate next to you. You did: dig. You dug F3 and found nothing. The treasure is 7 squares away.
- Turn 5 of the game, at F3, on a dug square, with no pirate next to you. You did: go_to F4. You walked north to F4. You arrived.
- Turn 9 of the game, at F4, on an undug square, with no pirate next to you. You did: dig. You dug F4 and found nothing. The treasure is 5 squares away.
- Turn 13 of the game, at F4, on a dug square, with no pirate next to you. You did: go_to F5. You walked north to F5. You arrived.
- Turn 17 of the game, at F5, on an undug square, with no pirate next to you. You did: dig. You dug F5 and found nothing. The treasure is 3 squares away.
- Turn 21 of the game, at F5, on a dug square, with no pirate next to you. You did: go_to F6. You walked north to F6. You arrived.
- Turn 25 of the game, at F6, on an undug square, with no pirate next to you. You did: dig. You dug F6 and found nothing. The treasure is 2 squares away.
- Turn 29 of the game, at F6, on a dug square, with no pirate next to you. You did: go_to E6. You walked west to E6. You arrived.
- Turn 33 of the game, at E6, on an undug square, with pirate-3 to the west. You did: dig. You dug E6 and found nothing. The treasure is 5 squares away.
- Turn 37 of the game, at E6, on a dug square, with no pirate next to you. You did: go_to D6. You walked west to D6. You arrived.
- Turn 41 of the game, at D6, on a dug square, with pirate-3 to the south. You did: go_to C6. You walked west to C6. You arrived.
- Turn 44 of the game, at C6, on a dug square, with pirate-3 to the south. You did: go_to B6. You walked west to B6. You arrived.
- Turn 47 of the game, at B6, on a dug square, with no pirate next to you. You did: go_to A6. You walked west to A6. You arrived.
- Turn 49 of the game, at A6, on a dug square, with no pirate next to you. You did: go_to A5. You walked south to A5. You arrived.
- Turn 51 of the game, at A5, on a dug square, with no pirate next to you. You did: go_to B5. You walked east to B5. You arrived.
- Turn 53 of the game, at B5, on a dug square, with pirate-2 to the east. You did: go_to B4. You walked south to B4. You arrived.
- Turn 55 of the game, at B4, on a dug square, with no pirate next to you. You did: go_to A4. You walked west to A4. You arrived. You were thinking: The nearest square I haven't seen dug is A4.
- Turn 56 of the game, at A4, on a dug square, with no pirate next to you. You did: go_to A3. You walked south to A3. You arrived. You were thinking: The nearest square I haven't seen dug is A3.

Pirate-1, this is your turn 19 of 24, turn 57 of the game. You are at A3. Your square hasn't been dug. The way west is blocked by the island's edge.
Squares you have dug: F3, 7 away; F4, 5 away; F5, 3 away; F6, 2 away; E6, 5 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> Nobody has dug this square yet.

**What it did**

> dig

**The result**

> You dug A3 and found nothing. The treasure is 5 squares away.

## Turn 57: pirate-1

<details>
<summary>What it was shown (6930 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 1 of the game, at F3, on an undug square, with no pirate next to you. You did: dig. You dug F3 and found nothing. The treasure is 7 squares away.
- Turn 5 of the game, at F3, on a dug square, with no pirate next to you. You did: go_to F4. You walked north to F4. You arrived.
- Turn 9 of the game, at F4, on an undug square, with no pirate next to you. You did: dig. You dug F4 and found nothing. The treasure is 5 squares away.
- Turn 13 of the game, at F4, on a dug square, with no pirate next to you. You did: go_to F5. You walked north to F5. You arrived.
- Turn 17 of the game, at F5, on an undug square, with no pirate next to you. You did: dig. You dug F5 and found nothing. The treasure is 3 squares away.
- Turn 21 of the game, at F5, on a dug square, with no pirate next to you. You did: go_to F6. You walked north to F6. You arrived.
- Turn 25 of the game, at F6, on an undug square, with no pirate next to you. You did: dig. You dug F6 and found nothing. The treasure is 2 squares away.
- Turn 29 of the game, at F6, on a dug square, with no pirate next to you. You did: go_to E6. You walked west to E6. You arrived.
- Turn 33 of the game, at E6, on an undug square, with pirate-3 to the west. You did: dig. You dug E6 and found nothing. The treasure is 5 squares away.
- Turn 37 of the game, at E6, on a dug square, with no pirate next to you. You did: go_to D6. You walked west to D6. You arrived.
- Turn 41 of the game, at D6, on a dug square, with pirate-3 to the south. You did: go_to C6. You walked west to C6. You arrived.
- Turn 44 of the game, at C6, on a dug square, with pirate-3 to the south. You did: go_to B6. You walked west to B6. You arrived.
- Turn 47 of the game, at B6, on a dug square, with no pirate next to you. You did: go_to A6. You walked west to A6. You arrived.
- Turn 49 of the game, at A6, on a dug square, with no pirate next to you. You did: go_to A5. You walked south to A5. You arrived.
- Turn 51 of the game, at A5, on a dug square, with no pirate next to you. You did: go_to B5. You walked east to B5. You arrived.
- Turn 53 of the game, at B5, on a dug square, with pirate-2 to the east. You did: go_to B4. You walked south to B4. You arrived.
- Turn 55 of the game, at B4, on a dug square, with no pirate next to you. You did: go_to A4. You walked west to A4. You arrived.
- Turn 56 of the game, at A4, on a dug square, with no pirate next to you. You did: go_to A3. You walked south to A3. You arrived. You were thinking: The nearest square I haven't seen dug is A3.
- Turn 57 of the game, at A3, on an undug square, with no pirate next to you. You did: dig. You dug A3 and found nothing. The treasure is 5 squares away. You were thinking: Nobody has dug this square yet.

Pirate-1, this is your turn 20 of 24, turn 58 of the game. You are at A3. Your square has been dug and holds no cave. The way west is blocked by the island's edge.
Squares you have dug: F3, 7 away; F4, 5 away; F5, 3 away; F6, 2 away; E6, 5 away; A3, 5 away.
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

## Turn 58: pirate-1

<details>
<summary>What it was shown (7037 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 1 of the game, at F3, on an undug square, with no pirate next to you. You did: dig. You dug F3 and found nothing. The treasure is 7 squares away.
- Turn 5 of the game, at F3, on a dug square, with no pirate next to you. You did: go_to F4. You walked north to F4. You arrived.
- Turn 9 of the game, at F4, on an undug square, with no pirate next to you. You did: dig. You dug F4 and found nothing. The treasure is 5 squares away.
- Turn 13 of the game, at F4, on a dug square, with no pirate next to you. You did: go_to F5. You walked north to F5. You arrived.
- Turn 17 of the game, at F5, on an undug square, with no pirate next to you. You did: dig. You dug F5 and found nothing. The treasure is 3 squares away.
- Turn 21 of the game, at F5, on a dug square, with no pirate next to you. You did: go_to F6. You walked north to F6. You arrived.
- Turn 25 of the game, at F6, on an undug square, with no pirate next to you. You did: dig. You dug F6 and found nothing. The treasure is 2 squares away.
- Turn 29 of the game, at F6, on a dug square, with no pirate next to you. You did: go_to E6. You walked west to E6. You arrived.
- Turn 33 of the game, at E6, on an undug square, with pirate-3 to the west. You did: dig. You dug E6 and found nothing. The treasure is 5 squares away.
- Turn 37 of the game, at E6, on a dug square, with no pirate next to you. You did: go_to D6. You walked west to D6. You arrived.
- Turn 41 of the game, at D6, on a dug square, with pirate-3 to the south. You did: go_to C6. You walked west to C6. You arrived.
- Turn 44 of the game, at C6, on a dug square, with pirate-3 to the south. You did: go_to B6. You walked west to B6. You arrived.
- Turn 47 of the game, at B6, on a dug square, with no pirate next to you. You did: go_to A6. You walked west to A6. You arrived.
- Turn 49 of the game, at A6, on a dug square, with no pirate next to you. You did: go_to A5. You walked south to A5. You arrived.
- Turn 51 of the game, at A5, on a dug square, with no pirate next to you. You did: go_to B5. You walked east to B5. You arrived.
- Turn 53 of the game, at B5, on a dug square, with pirate-2 to the east. You did: go_to B4. You walked south to B4. You arrived.
- Turn 55 of the game, at B4, on a dug square, with no pirate next to you. You did: go_to A4. You walked west to A4. You arrived.
- Turn 56 of the game, at A4, on a dug square, with no pirate next to you. You did: go_to A3. You walked south to A3. You arrived.
- Turn 57 of the game, at A3, on an undug square, with no pirate next to you. You did: dig. You dug A3 and found nothing. The treasure is 5 squares away. You were thinking: Nobody has dug this square yet.
- Turn 58 of the game, at A3, on a dug square, with no pirate next to you. You did: go_to B3. You walked east to B3. You arrived. You were thinking: The nearest square I haven't seen dug is B3.

Pirate-1, this is your turn 21 of 24, turn 59 of the game. You are at B3. Your square hasn't been dug. No way out of your square is blocked.
Squares you have dug: F3, 7 away; F4, 5 away; F5, 3 away; F6, 2 away; E6, 5 away; A3, 5 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> Nobody has dug this square yet.

**What it did**

> dig

**The result**

> You dug B3 and found nothing. The treasure is 5 squares away.

## Turn 59: pirate-1

<details>
<summary>What it was shown (7218 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 1 of the game, at F3, on an undug square, with no pirate next to you. You did: dig. You dug F3 and found nothing. The treasure is 7 squares away.
- Turn 5 of the game, at F3, on a dug square, with no pirate next to you. You did: go_to F4. You walked north to F4. You arrived.
- Turn 9 of the game, at F4, on an undug square, with no pirate next to you. You did: dig. You dug F4 and found nothing. The treasure is 5 squares away.
- Turn 13 of the game, at F4, on a dug square, with no pirate next to you. You did: go_to F5. You walked north to F5. You arrived.
- Turn 17 of the game, at F5, on an undug square, with no pirate next to you. You did: dig. You dug F5 and found nothing. The treasure is 3 squares away.
- Turn 21 of the game, at F5, on a dug square, with no pirate next to you. You did: go_to F6. You walked north to F6. You arrived.
- Turn 25 of the game, at F6, on an undug square, with no pirate next to you. You did: dig. You dug F6 and found nothing. The treasure is 2 squares away.
- Turn 29 of the game, at F6, on a dug square, with no pirate next to you. You did: go_to E6. You walked west to E6. You arrived.
- Turn 33 of the game, at E6, on an undug square, with pirate-3 to the west. You did: dig. You dug E6 and found nothing. The treasure is 5 squares away.
- Turn 37 of the game, at E6, on a dug square, with no pirate next to you. You did: go_to D6. You walked west to D6. You arrived.
- Turn 41 of the game, at D6, on a dug square, with pirate-3 to the south. You did: go_to C6. You walked west to C6. You arrived.
- Turn 44 of the game, at C6, on a dug square, with pirate-3 to the south. You did: go_to B6. You walked west to B6. You arrived.
- Turn 47 of the game, at B6, on a dug square, with no pirate next to you. You did: go_to A6. You walked west to A6. You arrived.
- Turn 49 of the game, at A6, on a dug square, with no pirate next to you. You did: go_to A5. You walked south to A5. You arrived.
- Turn 51 of the game, at A5, on a dug square, with no pirate next to you. You did: go_to B5. You walked east to B5. You arrived.
- Turn 53 of the game, at B5, on a dug square, with pirate-2 to the east. You did: go_to B4. You walked south to B4. You arrived.
- Turn 55 of the game, at B4, on a dug square, with no pirate next to you. You did: go_to A4. You walked west to A4. You arrived.
- Turn 56 of the game, at A4, on a dug square, with no pirate next to you. You did: go_to A3. You walked south to A3. You arrived.
- Turn 57 of the game, at A3, on an undug square, with no pirate next to you. You did: dig. You dug A3 and found nothing. The treasure is 5 squares away.
- Turn 58 of the game, at A3, on a dug square, with no pirate next to you. You did: go_to B3. You walked east to B3. You arrived. You were thinking: The nearest square I haven't seen dug is B3.
- Turn 59 of the game, at B3, on an undug square, with no pirate next to you. You did: dig. You dug B3 and found nothing. The treasure is 5 squares away. You were thinking: Nobody has dug this square yet.

Pirate-1, this is your turn 22 of 24, turn 60 of the game. You are at B3. Your square has been dug and holds no cave. No way out of your square is blocked.
Squares you have dug: F3, 7 away; F4, 5 away; F5, 3 away; F6, 2 away; E6, 5 away; A3, 5 away; B3, 5 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is C3.

**What it did**

> go\_to {"square": "C3"}\
> move {"direction": "east"}

**The result**

> You walked east to C3. You arrived.

## Turn 60: pirate-1

<details>
<summary>What it was shown (7348 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 1 of the game, at F3, on an undug square, with no pirate next to you. You did: dig. You dug F3 and found nothing. The treasure is 7 squares away.
- Turn 5 of the game, at F3, on a dug square, with no pirate next to you. You did: go_to F4. You walked north to F4. You arrived.
- Turn 9 of the game, at F4, on an undug square, with no pirate next to you. You did: dig. You dug F4 and found nothing. The treasure is 5 squares away.
- Turn 13 of the game, at F4, on a dug square, with no pirate next to you. You did: go_to F5. You walked north to F5. You arrived.
- Turn 17 of the game, at F5, on an undug square, with no pirate next to you. You did: dig. You dug F5 and found nothing. The treasure is 3 squares away.
- Turn 21 of the game, at F5, on a dug square, with no pirate next to you. You did: go_to F6. You walked north to F6. You arrived.
- Turn 25 of the game, at F6, on an undug square, with no pirate next to you. You did: dig. You dug F6 and found nothing. The treasure is 2 squares away.
- Turn 29 of the game, at F6, on a dug square, with no pirate next to you. You did: go_to E6. You walked west to E6. You arrived.
- Turn 33 of the game, at E6, on an undug square, with pirate-3 to the west. You did: dig. You dug E6 and found nothing. The treasure is 5 squares away.
- Turn 37 of the game, at E6, on a dug square, with no pirate next to you. You did: go_to D6. You walked west to D6. You arrived.
- Turn 41 of the game, at D6, on a dug square, with pirate-3 to the south. You did: go_to C6. You walked west to C6. You arrived.
- Turn 44 of the game, at C6, on a dug square, with pirate-3 to the south. You did: go_to B6. You walked west to B6. You arrived.
- Turn 47 of the game, at B6, on a dug square, with no pirate next to you. You did: go_to A6. You walked west to A6. You arrived.
- Turn 49 of the game, at A6, on a dug square, with no pirate next to you. You did: go_to A5. You walked south to A5. You arrived.
- Turn 51 of the game, at A5, on a dug square, with no pirate next to you. You did: go_to B5. You walked east to B5. You arrived.
- Turn 53 of the game, at B5, on a dug square, with pirate-2 to the east. You did: go_to B4. You walked south to B4. You arrived.
- Turn 55 of the game, at B4, on a dug square, with no pirate next to you. You did: go_to A4. You walked west to A4. You arrived.
- Turn 56 of the game, at A4, on a dug square, with no pirate next to you. You did: go_to A3. You walked south to A3. You arrived.
- Turn 57 of the game, at A3, on an undug square, with no pirate next to you. You did: dig. You dug A3 and found nothing. The treasure is 5 squares away.
- Turn 58 of the game, at A3, on a dug square, with no pirate next to you. You did: go_to B3. You walked east to B3. You arrived.
- Turn 59 of the game, at B3, on an undug square, with no pirate next to you. You did: dig. You dug B3 and found nothing. The treasure is 5 squares away. You were thinking: Nobody has dug this square yet.
- Turn 60 of the game, at B3, on a dug square, with no pirate next to you. You did: go_to C3. You walked east to C3. You arrived. You were thinking: The nearest square I haven't seen dug is C3.

Pirate-1, this is your turn 23 of 24, turn 61 of the game. You are at C3. Your square has been dug and holds no cave. No way out of your square is blocked.
Squares you have dug: F3, 7 away; F4, 5 away; F5, 3 away; F6, 2 away; E6, 5 away; A3, 5 away; B3, 5 away.
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

## Turn 61: pirate-1

<details>
<summary>What it was shown (7492 characters)</summary>

```text
# The goal
You are one of 4 pirates on an island, a 6 by 6 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-4 and takes turns in that order; each pirate gets 24 turns.
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
- A square holds one pirate at a time, except the open cave, which holds any number.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, every reading shared on the scroll so far, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. A reading can be off by up to 2 either way, but is never below 1, and a square always gives the same reading, so digging it again tells you nothing new.
- A dig with share set to true puts its reading on the scroll in your name as soon as it is known, as a shared reading: "Dug C4: 5 away." A dig without it shares nothing.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules.

Your earlier turns:
- Turn 1 of the game, at F3, on an undug square, with no pirate next to you. You did: dig. You dug F3 and found nothing. The treasure is 7 squares away.
- Turn 5 of the game, at F3, on a dug square, with no pirate next to you. You did: go_to F4. You walked north to F4. You arrived.
- Turn 9 of the game, at F4, on an undug square, with no pirate next to you. You did: dig. You dug F4 and found nothing. The treasure is 5 squares away.
- Turn 13 of the game, at F4, on a dug square, with no pirate next to you. You did: go_to F5. You walked north to F5. You arrived.
- Turn 17 of the game, at F5, on an undug square, with no pirate next to you. You did: dig. You dug F5 and found nothing. The treasure is 3 squares away.
- Turn 21 of the game, at F5, on a dug square, with no pirate next to you. You did: go_to F6. You walked north to F6. You arrived.
- Turn 25 of the game, at F6, on an undug square, with no pirate next to you. You did: dig. You dug F6 and found nothing. The treasure is 2 squares away.
- Turn 29 of the game, at F6, on a dug square, with no pirate next to you. You did: go_to E6. You walked west to E6. You arrived.
- Turn 33 of the game, at E6, on an undug square, with pirate-3 to the west. You did: dig. You dug E6 and found nothing. The treasure is 5 squares away.
- Turn 37 of the game, at E6, on a dug square, with no pirate next to you. You did: go_to D6. You walked west to D6. You arrived.
- Turn 41 of the game, at D6, on a dug square, with pirate-3 to the south. You did: go_to C6. You walked west to C6. You arrived.
- Turn 44 of the game, at C6, on a dug square, with pirate-3 to the south. You did: go_to B6. You walked west to B6. You arrived.
- Turn 47 of the game, at B6, on a dug square, with no pirate next to you. You did: go_to A6. You walked west to A6. You arrived.
- Turn 49 of the game, at A6, on a dug square, with no pirate next to you. You did: go_to A5. You walked south to A5. You arrived.
- Turn 51 of the game, at A5, on a dug square, with no pirate next to you. You did: go_to B5. You walked east to B5. You arrived.
- Turn 53 of the game, at B5, on a dug square, with pirate-2 to the east. You did: go_to B4. You walked south to B4. You arrived.
- Turn 55 of the game, at B4, on a dug square, with no pirate next to you. You did: go_to A4. You walked west to A4. You arrived.
- Turn 56 of the game, at A4, on a dug square, with no pirate next to you. You did: go_to A3. You walked south to A3. You arrived.
- Turn 57 of the game, at A3, on an undug square, with no pirate next to you. You did: dig. You dug A3 and found nothing. The treasure is 5 squares away.
- Turn 58 of the game, at A3, on a dug square, with no pirate next to you. You did: go_to B3. You walked east to B3. You arrived.
- Turn 59 of the game, at B3, on an undug square, with no pirate next to you. You did: dig. You dug B3 and found nothing. The treasure is 5 squares away.
- Turn 60 of the game, at B3, on a dug square, with no pirate next to you. You did: go_to C3. You walked east to C3. You arrived. You were thinking: The nearest square I haven't seen dug is C3.
- Turn 61 of the game, at C3, on a dug square, with no pirate next to you. You did: go_to C4. You walked north to C4. You arrived. You were thinking: The nearest square I haven't seen dug is C4.

Pirate-1, this is your turn 24 of 24, turn 62 of the game. You are at C4. Your square has been dug and holds no cave. No way out of your square is blocked.
Squares you have dug: F3, 7 away; F4, 5 away; F5, 3 away; F6, 2 away; E6, 5 away; A3, 5 away; B3, 5 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is C5.

**What it did**

> go\_to {"square": "C5"}\
> move {"direction": "north"}

**The result**

> You walked north to C5. You arrived.

## Game over

Game over: the turns ran out. The treasure at C5 was dug up, and 3 of 4 pirates got into the cave. Score 640.

**Score:** 640
