from rdflib import Graph, Namespace, RDF, Literal
from rdflib.namespace import XSD
from game_time import second_to_game_clock


VZ = Namespace("https://viziball.io/ontology/")
RES = Namespace("https://viziball.io/resource/")
TEAM = Namespace("https://viziball.io/resource/team/")


def build_rdf_graph(game, possessions, game_time):

    graph = Graph()

    graph.bind("vz", VZ)
    graph.bind("res", RES)

    game_uri = RES[f"game/{game['gid']}"]

    # --------------------------------------------------
    # PLAYER INDEX
    # --------------------------------------------------

    player_index = {}

    for team in game.get("teams", []):
        for player in team.get("players", []):
            player_index[player["pid"]] = player

    graph.add((
        game_uri,
        RDF.type,
        VZ.Game
    ))

    graph.add((
    game_uri,
    VZ.regulationPeriodCount,
    Literal(
        game_time["regulation_period_count"],
        datatype=XSD.integer,
        )
    ))

    graph.add((
        game_uri,
        VZ.regulationPeriodSeconds,
        Literal(
            game_time["regulation_period_seconds"],
            datatype=XSD.integer,
        )
    ))

    graph.add((
        game_uri,
        VZ.regulationEndSecond,
        Literal(
            game_time["regulation_end_second"],
            datatype=XSD.integer,
        )
    ))

    graph.add((
        game_uri,
        VZ.overtimePeriodSeconds,
        Literal(
            game_time["overtime_period_seconds"],
            datatype=XSD.integer,
        )
    ))

    graph.add((
        game_uri,
        VZ.overtimeCount,
        Literal(
            game_time["overtime_count"],
            datatype=XSD.integer,
        )
    ))

    # --------------------------------------------------
    # HELPERS
    # --------------------------------------------------

    def add_team(team_id):

        team_uri = RES[f"team/{team_id}"]

        graph.add((
            team_uri,
            RDF.type,
            VZ.Team
        ))

        return team_uri


    def add_player(player_id):

        player_uri = RES[f"player/{player_id}"]

        graph.add((
            player_uri,
            RDF.type,
            VZ.Player
        ))

        graph.add((
            player_uri,
            VZ.playerId,
            Literal(player_id, datatype=XSD.integer)
        ))

        player = player_index.get(player_id)

        if player:

            first_name = player.get("fn")
            last_name = player.get("ln")

            if first_name:
                graph.add((
                    player_uri,
                    VZ.firstName,
                    Literal(first_name)
                ))

            if last_name:
                graph.add((
                    player_uri,
                    VZ.lastName,
                    Literal(last_name)
                ))

            display_name = " ".join(
                x for x in [first_name, last_name] if x
            )

            if display_name:
                graph.add((
                    player_uri,
                    VZ.displayName,
                    Literal(display_name)
                ))

        return player_uri


    def add_lineup(lineup):

        lineup_uri = RES[
            f"lineup/{lineup['lineup_id']}"
        ]

        graph.add((
            lineup_uri,
            RDF.type,
            VZ.Lineup
        ))

        for player_id in lineup["players"]:

            player_uri = add_player(player_id)

            graph.add((
                lineup_uri,
                VZ.hasPlayer,
                player_uri
            ))

        return lineup_uri


    # --------------------------------------------------
    # SCORE STATE
    # --------------------------------------------------

    team_scores = {
        team["tid"]: 0
        for team in game["teams"]
    }

    # --------------------------------------------------
    # POSSESSIONS
    # --------------------------------------------------

    for possession in possessions:

        possession_uri = RES[
            f"possession/{game['gid']}/{possession['id']}"
        ]

        graph.add((
            possession_uri,
            RDF.type,
            VZ.Possession
        ))

        graph.add((
            game_uri,
            VZ.hasPossession,
            possession_uri
        ))

        graph.add((
            possession_uri,
            VZ.possessionNumber,
            Literal(
                possession["id"],
                datatype=XSD.integer
            )
        ))

        graph.add((
            possession_uri,
            VZ.startSecond,
            Literal(
                possession["start_second"],
                datatype=XSD.integer
            )
        ))

        graph.add((
            possession_uri,
            VZ.endSecond,
            Literal(
                possession["end_second"],
                datatype=XSD.integer
            )
        ))

        # --------------------------------------------------
        # POSSESSION GAME CLOCK
        # --------------------------------------------------

        start_clock = second_to_game_clock(
            possession["start_second"],
            game_time,
        )

        end_clock = second_to_game_clock(
            possession["end_second"],
            game_time,
        )

        graph.add((
            possession_uri,
            VZ.startPeriod,
            Literal(
                start_clock["period"],
                datatype=XSD.integer,
            )
        ))

        graph.add((
            possession_uri,
            VZ.endPeriod,
            Literal(
                end_clock["period"],
                datatype=XSD.integer,
            )
        ))

        graph.add((
            possession_uri,
            VZ.startSecondsRemaining,
            Literal(
                start_clock["remaining_seconds"],
                datatype=XSD.integer,
            )
        ))

        graph.add((
            possession_uri,
            VZ.endSecondsRemaining,
            Literal(
                end_clock["remaining_seconds"],
                datatype=XSD.integer,
            )
        ))

        graph.add((
            possession_uri,
            VZ.isOvertime,
            Literal(
                start_clock["is_overtime"],
                datatype=XSD.boolean,
            )
        ))        

        graph.add((
            possession_uri,
            VZ.endReason,
            Literal(possession["end_reason"])
        ))

        # --------------------------------------------------
        # TEAMS
        # --------------------------------------------------

        offensive_team_uri = add_team(
            possession["offensive_team"]
        )

        defensive_team_uri = add_team(
            possession["defensive_team"]
        )

        graph.add((
            possession_uri,
            VZ.offensiveTeam,
            offensive_team_uri
        ))

        graph.add((
            possession_uri,
            VZ.defensiveTeam,
            defensive_team_uri
        ))

        # --------------------------------------------------
        # TEAMS / ROSTERS
        # --------------------------------------------------

        for team in game["teams"]:

            team_uri = add_team(team["tid"])

            for player in team["players"]:

                player_uri = add_player(player["pid"])

                graph.add((
                    team_uri,
                    VZ.hasPlayer,
                    player_uri
                ))

        # --------------------------------------------------
        # LINEUPS
        # --------------------------------------------------

        offensive_lineup_uri = add_lineup(
            possession["offensive_lineup"]
        )

        defensive_lineup_uri = add_lineup(
            possession["defensive_lineup"]
        )

        graph.add((
            possession_uri,
            VZ.offensiveLineup,
            offensive_lineup_uri
        ))

        graph.add((
            possession_uri,
            VZ.defensiveLineup,
            defensive_lineup_uri
        ))

        # --------------------------------------------------
        # EVENTS
        # --------------------------------------------------

        for event_index, event in enumerate(
            possession["events"]
        ):

            event_uri = RES[
                f"event/{game['gid']}/"
                f"{possession['id']}/{event_index}"
            ]

            graph.add((
                event_uri,
                RDF.type,
                VZ.Event
            ))

            graph.add((
                possession_uri,
                VZ.hasEvent,
                event_uri
            ))

            graph.add((
                event_uri,
                VZ.eventType,
                Literal(event["type"])
            ))

            graph.add((
                event_uri,
                VZ.second,
                Literal(
                    event["second"],
                    datatype=XSD.integer
                )
            ))

            game_clock = second_to_game_clock(
                event["second"],
                game_time,
            )

            graph.add((
                event_uri,
                VZ.period,
                Literal(
                    game_clock["period"],
                    datatype=XSD.integer,
                )
            ))

            graph.add((
                event_uri,
                VZ.secondsRemaining,
                Literal(
                    game_clock["remaining_seconds"],
                    datatype=XSD.integer,
                )
            ))

            graph.add((
                event_uri,
                VZ.isOvertime,
                Literal(
                    game_clock["is_overtime"],
                    datatype=XSD.boolean,
                )
            ))

            if event["team_id"] is not None:

                event_team_uri = add_team(
                    event["team_id"]
                )

                graph.add((
                    event_uri,
                    VZ.team,
                    event_team_uri
                ))

            # --------------------------------------------------
            # SCORE STATE BEFORE EVENT
            # --------------------------------------------------

            event_team_id = event.get("team_id")

            if event_team_id is not None:

                graph.add((
                    event_uri,
                    VZ.scorePerspectiveTeam,
                    TEAM[str(event_team_id)]
                ))

                opponent_ids = [
                    tid
                    for tid in team_scores
                    if tid != event_team_id
                ]

                if opponent_ids:

                    opponent_id = opponent_ids[0]

                    score_for = team_scores[event_team_id]
                    score_against = team_scores[opponent_id]

                    score_diff = score_for - score_against

                    graph.add((
                        event_uri,
                        VZ.scoreForBefore,
                        Literal(
                            score_for,
                            datatype=XSD.integer,
                        )
                    ))

                    graph.add((
                        event_uri,
                        VZ.scoreAgainstBefore,
                        Literal(
                            score_against,
                            datatype=XSD.integer,
                        )
                    ))

                    graph.add((
                        event_uri,
                        VZ.scoreDifferential,
                        Literal(
                            score_diff,
                            datatype=XSD.integer,
                        )
                    ))

            # --------------------------------------------------
            # UPDATE SCORE AFTER EVENT
            # --------------------------------------------------

            points = 0

            if event["type"] == "TWO_PT_MADE":
                points = 2

            elif event["type"] == "THREE_PT_MADE":
                points = 3

            elif event["type"] == "FT_MADE":
                points = 1

            if (
                event_team_id is not None
                and points > 0
            ):
                team_scores[event_team_id] += points

            # ----------------------------------------------
            # PLAYERS / ROLES
            # ----------------------------------------------

            role_predicates = {
                "shooter": VZ.shooter,
                "assist": VZ.assistedBy,
                "turnover": VZ.turnoverBy,
                "steal": VZ.stolenBy,
                "rebounder": VZ.rebounder,
                "fouler": VZ.foulBy,
                "block": VZ.blockedBy,
            }

            for role, player_id in event["players"].items():

                predicate = role_predicates.get(role)

                if predicate is None:
                    continue

                player_uri = add_player(player_id)

                graph.add((
                    event_uri,
                    predicate,
                    player_uri
                ))

    return graph