# Event log

- **one-record-per-turn:** A run's event log is a JSON Lines file with one object per turn, in play order, with `turn` counting up from 0, so everything visual can be rebuilt from that one file.
- **who-acted:** Each record names the pirate that took the turn in `agent`, so a reader can follow one pirate through a run.
- **what-they-saw:** Each record's `saw` holds the pirate's `position` as `[x, y]` at the start of its turn and the `prompt` text it was given, so anyone can judge a decision from what the pirate knew.
- **what-they-did:** Each record's `did` lists the turn's actions, each named by `action`: `move` with a `direction` of `north`, `east`, `south` or `west`; `dig`; `read` with a `line` number; or `write` with its `text`, so a viewer can draw any turn, including one with no action.
- **what-the-log-showed:** Each record's `log_shown` lists every log line shown to the pirate that turn, as a `line` number and its `text`, so a reader sees the chat that pirate saw, and any earlier session it reached.
- **the-outcome:** Each record's `outcome` holds the pirate's `position` as `[x, y]` after its turn and whether it has `found_treasure`, so scoring and the animation need no replay of the rules.
- **crew-positions:** Each record's `crew` says where every pirate stands at the start of the turn, so a frame can show the whole crew from the first turn, whether the run is still being played or long finished.
- **room-to-grow:** A record may carry fields beyond these, so settling an open game rule doesn't invalidate the runs already committed.
- **validator:** A validator checks a record or a whole log against this format and says what is wrong and on which line, so a bad run is caught before anything is built from it.

## Where this is enforced

| Statement | Enforced by | Tested by |
|---|---|---|
| `one-record-per-turn` | `src/treasure_island/event_log.py` | `test_one_record_per_turn_accepts_a_log_counting_up_from_zero`, `test_one_record_per_turn_rejects_turns_out_of_order`, `test_one_record_per_turn_rejects_a_turn_that_is_not_a_number`, `test_one_record_per_turn_rejects_an_empty_log` |
| `who-acted` | `src/treasure_island/event_log.py` | `test_who_acted_needs_a_named_agent` |
| `what-they-saw` | `src/treasure_island/event_log.py` | `test_what_they_saw_needs_a_position_and_a_prompt` |
| `what-they-did` | `src/treasure_island/event_log.py` | `test_what_they_did_accepts_each_action`, `test_what_they_did_accepts_a_turn_with_no_action`, `test_what_they_did_rejects_a_malformed_action`, `test_what_they_did_must_be_a_list` |
| `what-the-log-showed` | `src/treasure_island/event_log.py` | `test_what_the_log_showed_needs_numbered_lines`, `test_what_the_log_showed_can_reach_an_earlier_session` |
| `the-outcome` | `src/treasure_island/event_log.py` | `test_the_outcome_needs_a_position_and_whether_treasure_was_found` |
| `crew-positions` | `src/treasure_island/game.py`, `src/treasure_island/viewer.py` | `test_crew_positions_every_record_says_where_the_crew_stands`, `test_crew_positions_a_frame_shows_a_pirate_before_its_first_turn` |
| `room-to-grow` | `src/treasure_island/event_log.py` | `test_room_to_grow_allows_extra_fields` |
| `validator` | `src/treasure_island/event_log.py` | `test_validator_accepts_a_good_record`, `test_validator_rejects_a_bad_record_and_says_what_is_wrong`, `test_validator_rejects_a_record_that_is_not_an_object`, `test_validator_names_the_line_a_log_is_wrong_on`, `test_validator_reports_a_line_that_is_not_json` |
