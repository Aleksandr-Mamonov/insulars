"""
There are 2 types of results that we apply after round ended: immediate and future.
Immediate: for example, add 10 points to each player on_success.
Future: for example, add 5 points each round in next 3 rounds.
Initial conditions for all players:
    "add_each_next_round": [],
    "can_be_leader_next_round": True,
    "can_select_team_as_leader": True,
    "can_select_cards_as_leader": True,

After 1st round those conditions for each player changed.
And at the beginning of each new round (starting from round #2) we apply conditions accordingly 
to this "future_effects_on_players_to_apply" object.

"""
