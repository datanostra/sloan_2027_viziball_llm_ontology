from collections import defaultdict
from game_time import second_to_game_clock

ONTOLOGY_CONCEPTS = [
    "LateGameSituation",
    "CloseGameSituation",
    "ClutchSituation",

    "ScoringPossession",
    "TurnoverPossession",
    "SecondChancePossession",
    "ThreePointScoringPossession",

    "LeadingPossession",
    "TrailingPossession",
    "TiedPossession",
    "OnePossessionGameSituation",
]

SCORING_EVENTS = {
    "TWO_PT_MADE",
    "THREE_PT_MADE",
    "FT_MADE",
}

def build_ontology_ground_truth(
    possessions,
    game_time,
):

    ground_truth = {
        concept: set()
        for concept in ONTOLOGY_CONCEPTS
    }

    # ==================================================
    # INITIAL SCORE STATE
    # ==================================================

    team_ids = set()

    for possession in possessions:

        team_ids.add(
            possession["offensive_team"]
        )

        team_ids.add(
            possession["defensive_team"]
        )

    team_scores = {
        team_id: 0
        for team_id in team_ids
    }

    # ==================================================
    # POSSESSIONS
    # ==================================================

    for possession_index, possession in enumerate(
        possessions
    ):

        events = possession.get(
            "events",
            []
        )

        # ==================================================
        # GAME CLOCK
        # ==================================================

        clock = second_to_game_clock(
            possession["start_second"],
            game_time,
        )

        period = clock["period"]

        seconds_remaining = (
            clock["remaining_seconds"]
        )

        # ==================================================
        # LATE GAME
        # ==================================================

        is_late_game = (
            period == 4
            and seconds_remaining <= 300
        )

        # ==================================================
        # EVENT-BASED CONCEPTS
        # ==================================================

        event_types = [
            event.get("type")
            for event in events
        ]

        is_scoring = any(
            event_type in SCORING_EVENTS
            for event_type in event_types
        )

        is_turnover = (
            "TURNOVER" in event_types
        )

        is_second_chance = (
            "OFF_REBOUND" in event_types
        )

        is_three_point_scoring = (
            "THREE_PT_MADE"
            in event_types
        )

        # ==================================================
        # SCORE-BASED CONCEPTS
        # ==================================================
        #
        # We reconstruct score independently from raw
        # possession events.
        #
        # start_score_diff is expressed from the
        # OFFENSIVE TEAM perspective.
        #
        # ==================================================

        is_close_game = False

        start_score_diff = None

        offensive_team_id = possession[
            "offensive_team"
        ]

        # ==================================================
        # EVENTS
        # ==================================================

        for event in events:

            event_type = event.get(
                "type"
            )

            event_team_id = event.get(
                "team_id"
            )

            # ----------------------------------------------
            # SCORE BEFORE EVENT
            # ----------------------------------------------

            if event_team_id is not None:

                opponent_ids = [
                    team_id
                    for team_id in team_scores
                    if team_id != event_team_id
                ]

                if opponent_ids:

                    opponent_id = (
                        opponent_ids[0]
                    )

                    score_for = (
                        team_scores[
                            event_team_id
                        ]
                    )

                    score_against = (
                        team_scores[
                            opponent_id
                        ]
                    )

                    score_diff = (
                        score_for
                        - score_against
                    )

                    # --------------------------------------
                    # POSSESSION START SCORE
                    #
                    # Convert event-team perspective
                    # to offensive-team perspective.
                    # --------------------------------------

                    if start_score_diff is None:

                        if (
                            event_team_id
                            == offensive_team_id
                        ):

                            start_score_diff = (
                                score_diff
                            )

                        else:

                            start_score_diff = (
                                -score_diff
                            )

                    # --------------------------------------
                    # CLOSE GAME
                    #
                    # Existing semantic definition:
                    # possession contains at least one
                    # event occurring within +/- 5.
                    # --------------------------------------

                    if abs(score_diff) <= 5:

                        is_close_game = True

            # ----------------------------------------------
            # UPDATE SCORE AFTER EVENT
            # ----------------------------------------------

            points = 0

            if event_type == "TWO_PT_MADE":

                points = 2

            elif event_type == "THREE_PT_MADE":

                points = 3

            elif event_type == "FT_MADE":

                points = 1

            if (
                event_team_id is not None
                and points > 0
            ):

                team_scores[
                    event_team_id
                ] += points

        # ==================================================
        # CLUTCH
        # ==================================================

        is_clutch = (
            is_late_game
            and is_close_game
        )

        # ==================================================
        # SCORE STATE AT POSSESSION START
        # ==================================================

        is_leading = (
            start_score_diff is not None
            and start_score_diff > 0
        )

        is_trailing = (
            start_score_diff is not None
            and start_score_diff < 0
        )

        is_tied = (
            start_score_diff is not None
            and start_score_diff == 0
        )

        # ==================================================
        # ONE POSSESSION GAME
        #
        # Score margin at possession start <= 3.
        # Includes tied situations.
        # ==================================================

        is_one_possession_game = (
            start_score_diff is not None
            and abs(start_score_diff) <= 3
        )

        # ==================================================
        # REFERENCE CLASSIFICATION
        # ==================================================

        if is_late_game:

            ground_truth[
                "LateGameSituation"
            ].add(
                possession_index
            )

        if is_close_game:

            ground_truth[
                "CloseGameSituation"
            ].add(
                possession_index
            )

        if is_clutch:

            ground_truth[
                "ClutchSituation"
            ].add(
                possession_index
            )

        if is_scoring:

            ground_truth[
                "ScoringPossession"
            ].add(
                possession_index
            )

        if is_turnover:

            ground_truth[
                "TurnoverPossession"
            ].add(
                possession_index
            )

        if is_second_chance:

            ground_truth[
                "SecondChancePossession"
            ].add(
                possession_index
            )

        if is_three_point_scoring:

            ground_truth[
                "ThreePointScoringPossession"
            ].add(
                possession_index
            )

        # ==================================================
        # NEW SCORE-STATE CONCEPTS
        # ==================================================

        if is_leading:

            ground_truth[
                "LeadingPossession"
            ].add(
                possession_index
            )

        if is_trailing:

            ground_truth[
                "TrailingPossession"
            ].add(
                possession_index
            )

        if is_tied:

            ground_truth[
                "TiedPossession"
            ].add(
                possession_index
            )

        if is_one_possession_game:

            ground_truth[
                "OnePossessionGameSituation"
            ].add(
                possession_index
            )

    return ground_truth


def get_ground_truth_instances(
    ground_truth,
    concepts,
):

    if not concepts:
        return set()

    sets = [
        ground_truth[concept]
        for concept in concepts
    ]

    return set.intersection(
        *sets
    )

def get_ground_truth_clutch_player_ranking(
    possessions,
    game_time,
):

    # ==================================================
    # INITIAL SCORE STATE
    # ==================================================

    team_ids = set()

    for possession in possessions:

        team_ids.add(
            possession["offensive_team"]
        )

        team_ids.add(
            possession["defensive_team"]
        )

    team_scores = {
        team_id: 0
        for team_id in team_ids
    }

    player_points = {}

    # ==================================================
    # POSSESSIONS
    # ==================================================

    for possession in possessions:

        events = possession.get(
            "events",
            []
        )

        # ----------------------------------------------
        # GAME CLOCK
        # ----------------------------------------------

        clock = second_to_game_clock(
            possession["start_second"],
            game_time,
        )

        is_late_game = (
            clock["period"] == 4
            and clock["remaining_seconds"] <= 300
        )

        # ----------------------------------------------
        # CLOSE GAME
        # ----------------------------------------------

        is_close_game = False

        # We need to know whether each scoring event
        # belongs to a clutch possession.
        scoring_events = []

        for event in events:

            event_type = event.get(
                "type"
            )

            event_team_id = event.get(
                "team_id"
            )

            # ------------------------------------------
            # SCORE BEFORE EVENT
            # ------------------------------------------

            if event_team_id is not None:

                opponent_ids = [
                    team_id
                    for team_id in team_scores
                    if team_id != event_team_id
                ]

                if opponent_ids:

                    opponent_id = opponent_ids[0]

                    score_diff = (
                        team_scores[event_team_id]
                        - team_scores[opponent_id]
                    )

                    if abs(score_diff) <= 5:
                        is_close_game = True

            # Keep raw scoring event for later.
            if event_type in (
                "TWO_PT_MADE",
                "THREE_PT_MADE",
                "FT_MADE",
            ):
                scoring_events.append(
                    event
                )

            # ------------------------------------------
            # UPDATE SCORE
            # ------------------------------------------

            points = 0

            if event_type == "TWO_PT_MADE":
                points = 2

            elif event_type == "THREE_PT_MADE":
                points = 3

            elif event_type == "FT_MADE":
                points = 1

            if (
                event_team_id is not None
                and points > 0
            ):
                team_scores[
                    event_team_id
                ] += points

        # ----------------------------------------------
        # CLUTCH
        # ----------------------------------------------

        is_clutch = (
            is_late_game
            and is_close_game
        )

        if not is_clutch:
            continue

        # ----------------------------------------------
        # PLAYER POINTS
        # ----------------------------------------------

        for event in scoring_events:

            event_type = event.get(
                "type"
            )

            players = event.get(
                "players",
                {},
            )

            shooter = players.get(
                "shooter"
            )

            if shooter is None:
                continue

            if event_type == "TWO_PT_MADE":
                points = 2

            elif event_type == "THREE_PT_MADE":
                points = 3

            elif event_type == "FT_MADE":
                points = 1

            else:
                continue

            player_points[shooter] = (
                player_points.get(
                    shooter,
                    0,
                )
                + points
            )

    # ==================================================
    # RANKING
    # ==================================================

    ranking = sorted(
        player_points.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    return ranking


def execute_ground_truth_query(
    ground_truth,
    concepts,
    operation,
    denominator_concepts=None,
    entity=None,
    metric=None,
    order=None,
    limit=None,
    possessions=None,
    game_time=None,
):

    # ==================================================
    # COUNT / RATIO INSTANCES
    # ==================================================

    numerator_instances = (
        get_ground_truth_instances(
            ground_truth,
            concepts,
        )
    )

    # ==================================================
    # COUNT
    # ==================================================

    if operation == "COUNT":

        return len(
            numerator_instances
        )

    # ==================================================
    # RATIO
    # ==================================================

    if operation == "RATIO":

        if not denominator_concepts:
            raise ValueError(
                "RATIO requires "
                "denominator_concepts"
            )

        denominator_instances = (
            get_ground_truth_instances(
                ground_truth,
                denominator_concepts,
            )
        )

        numerator = len(
            numerator_instances
        )

        denominator = len(
            denominator_instances
        )

        return (
            numerator / denominator
            if denominator > 0
            else None
        )

    # ==================================================
    # RANK
    #
    # Independent ground truth implementation.
    #
    # Currently supported:
    #
    # concepts = ["ClutchSituation"]
    # entity   = PLAYER
    # metric   = PTS
    # ==================================================

    if operation == "RANK":

        if entity != "PLAYER":
            raise ValueError(
                "Ground truth RANK currently "
                "supports entity=PLAYER only"
            )

        if metric != "PTS":
            raise ValueError(
                "Ground truth RANK currently "
                "supports metric=PTS only"
            )

        if concepts != [
            "ClutchSituation"
        ]:
            raise ValueError(
                "Ground truth RANK currently "
                "supports ClutchSituation only"
            )

        if possessions is None:
            raise ValueError(
                "RANK ground truth requires "
                "possessions"
            )

        if game_time is None:
            raise ValueError(
                "RANK ground truth requires "
                "game_time"
            )

        # ----------------------------------------------
        # INDEPENDENT RAW-DATA RANKING
        # ----------------------------------------------

        ranking = (
            get_ground_truth_clutch_player_ranking(
                possessions,
                game_time,
            )
        )

        # ----------------------------------------------
        # ORDER
        # ----------------------------------------------

        if order == "ASC":

            ranking = sorted(
                ranking,
                key=lambda item: item[1],
            )

        else:

            ranking = sorted(
                ranking,
                key=lambda item: item[1],
                reverse=True,
            )

        # ----------------------------------------------
        # LIMIT
        # ----------------------------------------------

        if limit is not None:

            ranking = ranking[
                :limit
            ]

        # ----------------------------------------------
        # SAME LOGICAL FORMAT AS RDF RESULT
        # ----------------------------------------------

        return [
            {
                "player": str(
                    player_id
                ),
                "value": points,
            }
            for player_id, points
            in ranking
        ]

    # ==================================================
    # UNSUPPORTED
    # ==================================================

    raise ValueError(
        f"Unsupported operation: "
        f"{operation}"
    )