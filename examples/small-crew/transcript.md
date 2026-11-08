# Transcript: small-crew

## Turn 0: pirate-1

<details>
<summary>What it was shown (3987 characters)</summary>

```text
# The goal
You are one of 2 pirates on an island, a 3 by 3 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-2 and takes turns in that order; each pirate gets 4 turns.
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

Pirate-1, this is your turn 1 of 4, turn 1 of the game. You are at C3. Your square hasn't been dug. The way north is blocked by the island's edge and the way east by the island's edge.
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

> You dug C3 and found nothing. The treasure is 1 square away.

## Turn 1: pirate-2

<details>
<summary>What it was shown (3987 characters)</summary>

```text
# The goal
You are one of 2 pirates on an island, a 3 by 3 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-2 and takes turns in that order; each pirate gets 4 turns.
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

Pirate-2, this is your turn 1 of 4, turn 2 of the game. You are at A1. Your square hasn't been dug. The way south is blocked by the island's edge and the way west by the island's edge.
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

> You dug A1 and found nothing. The treasure is 3 squares away.

## Turn 2: pirate-1

<details>
<summary>What it was shown (4199 characters)</summary>

```text
# The goal
You are one of 2 pirates on an island, a 3 by 3 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-2 and takes turns in that order; each pirate gets 4 turns.
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
- Turn 1 of the game, at C3, on an undug square, with no pirate next to you. You did: dig. You dug C3 and found nothing. The treasure is 1 square away. You were thinking: Nobody has dug this square yet.

Pirate-1, this is your turn 2 of 4, turn 3 of the game. You are at C3. Your square has been dug and holds no cave. The way north is blocked by the island's edge and the way east by the island's edge.
Squares you have dug: C3, 1 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is B3.

**What it did**

> go\_to {"square": "B3"}\
> move {"direction": "west"}

**The result**

> You walked west to B3. You arrived.

## Turn 3: pirate-2

<details>
<summary>What it was shown (4200 characters)</summary>

```text
# The goal
You are one of 2 pirates on an island, a 3 by 3 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-2 and takes turns in that order; each pirate gets 4 turns.
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
- Turn 2 of the game, at A1, on an undug square, with no pirate next to you. You did: dig. You dug A1 and found nothing. The treasure is 3 squares away. You were thinking: Nobody has dug this square yet.

Pirate-2, this is your turn 2 of 4, turn 4 of the game. You are at A1. Your square has been dug and holds no cave. The way south is blocked by the island's edge and the way west by the island's edge.
Squares you have dug: A1, 3 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is A2.

**What it did**

> go\_to {"square": "A2"}\
> move {"direction": "north"}

**The result**

> You walked north to A2. You arrived.

## Turn 4: pirate-1

<details>
<summary>What it was shown (4339 characters)</summary>

```text
# The goal
You are one of 2 pirates on an island, a 3 by 3 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-2 and takes turns in that order; each pirate gets 4 turns.
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
- Turn 1 of the game, at C3, on an undug square, with no pirate next to you. You did: dig. You dug C3 and found nothing. The treasure is 1 square away. You were thinking: Nobody has dug this square yet.
- Turn 3 of the game, at C3, on a dug square, with no pirate next to you. You did: go_to B3. You walked west to B3. You arrived. You were thinking: The nearest square I haven't seen dug is B3.

Pirate-1, this is your turn 3 of 4, turn 5 of the game. You are at B3. Your square hasn't been dug. The way north is blocked by the island's edge.
Squares you have dug: C3, 1 away.
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

## Turn 5: pirate-2

<details>
<summary>What it was shown (4340 characters)</summary>

```text
# The goal
You are one of 2 pirates on an island, a 3 by 3 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-2 and takes turns in that order; each pirate gets 4 turns.
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
- Turn 2 of the game, at A1, on an undug square, with no pirate next to you. You did: dig. You dug A1 and found nothing. The treasure is 3 squares away. You were thinking: Nobody has dug this square yet.
- Turn 4 of the game, at A1, on a dug square, with no pirate next to you. You did: go_to A2. You walked north to A2. You arrived. You were thinking: The nearest square I haven't seen dug is A2.

Pirate-2, this is your turn 3 of 4, turn 6 of the game. You are at A2. Your square hasn't been dug. The way west is blocked by the island's edge.
Squares you have dug: A1, 3 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> Nobody has dug this square yet.

**What it did**

> dig

**The result**

> You dug A2 and found nothing. The treasure is 2 squares away.

## Turn 6: pirate-1

<details>
<summary>What it was shown (4557 characters)</summary>

```text
# The goal
You are one of 2 pirates on an island, a 3 by 3 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-2 and takes turns in that order; each pirate gets 4 turns.
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
- Turn 1 of the game, at C3, on an undug square, with no pirate next to you. You did: dig. You dug C3 and found nothing. The treasure is 1 square away.
- Turn 3 of the game, at C3, on a dug square, with no pirate next to you. You did: go_to B3. You walked west to B3. You arrived. You were thinking: The nearest square I haven't seen dug is B3.
- Turn 5 of the game, at B3, on an undug square, with no pirate next to you. You did: dig. You dug here and found the treasure! It opens a cave on this square: enter it to go in. You were thinking: Nobody has dug this square yet.

Pirate-1, this is your turn 4 of 4, turn 7 of the game. You are at B3. You are standing on the open cave: enter it to go in. The way north is blocked by the island's edge.
Squares you have dug: C3, 1 away; B3, the cave.
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

## Turn 7: pirate-2

<details>
<summary>What it was shown (4520 characters)</summary>

```text
# The goal
You are one of 2 pirates on an island, a 3 by 3 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-2 and takes turns in that order; each pirate gets 4 turns.
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
- Turn 2 of the game, at A1, on an undug square, with no pirate next to you. You did: dig. You dug A1 and found nothing. The treasure is 3 squares away.
- Turn 4 of the game, at A1, on a dug square, with no pirate next to you. You did: go_to A2. You walked north to A2. You arrived. You were thinking: The nearest square I haven't seen dug is A2.
- Turn 6 of the game, at A2, on an undug square, with no pirate next to you. You did: dig. You dug A2 and found nothing. The treasure is 2 squares away. You were thinking: Nobody has dug this square yet.

Pirate-2, this is your turn 4 of 4, turn 8 of the game. You are at A2. Your square has been dug and holds no cave. The way west is blocked by the island's edge.
Squares you have dug: A1, 3 away; A2, 2 away.
No reading has been shared on the scroll yet.
Nothing new on the scroll.
```

</details>

**Its thinking**

> The nearest square I haven't seen dug is A3.

**What it did**

> go\_to {"square": "A3"}\
> move {"direction": "north"}

**The result**

> You walked north to A3. You arrived.

## Game over

Game over: the turns ran out. The treasure at B3 was dug up, and 1 of 2 pirates got into the cave. Score 100.

**Score:** 100
