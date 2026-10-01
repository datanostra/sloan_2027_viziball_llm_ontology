from rdflib import Namespace, RDF, RDFS, OWL

VZ = Namespace("https://viziball.io/ontology/")

from rdflib import Namespace, RDF, RDFS, OWL


VZ = Namespace(
    "https://viziball.io/ontology/"
)


def add_viziball_ontology(graph):
    """
    Add the Viziball basketball ontology to an RDF graph.

    The ontology currently models two complementary
    semantic dimensions:

    1. Game context:
       - LateGameSituation
       - CloseGameSituation
       - ClutchSituation

    2. Possession outcome / structure:
       - ScoringPossession
       - TurnoverPossession
       - SecondChancePossession
       - ThreePointScoringPossession

    This function only declares the ontology.
    Instance classification is performed separately
    by infer_game_situations().
    """

    # ==================================================
    # CORE BASKETBALL CLASSES
    # ==================================================

    graph.add((
        VZ.Game,
        RDF.type,
        OWL.Class,
    ))

    graph.add((
        VZ.Possession,
        RDF.type,
        OWL.Class,
    ))

    graph.add((
        VZ.Event,
        RDF.type,
        OWL.Class,
    ))

    graph.add((
        VZ.Player,
        RDF.type,
        OWL.Class,
    ))

    graph.add((
        VZ.Team,
        RDF.type,
        OWL.Class,
    ))

    graph.add((
        VZ.Lineup,
        RDF.type,
        OWL.Class,
    ))

    # ==================================================
    # GAME SITUATIONS
    #
    # Semantic dimension describing WHEN / UNDER
    # WHICH GAME CONTEXT a possession occurs.
    # ==================================================

    graph.add((
        VZ.GameSituation,
        RDF.type,
        OWL.Class,
    ))

    # ------------------------------------------
    # LATE GAME
    # ------------------------------------------

    graph.add((
        VZ.LateGameSituation,
        RDF.type,
        OWL.Class,
    ))

    graph.add((
        VZ.LateGameSituation,
        RDFS.subClassOf,
        VZ.GameSituation,
    ))

    # ------------------------------------------
    # CLOSE GAME
    # ------------------------------------------

    graph.add((
        VZ.CloseGameSituation,
        RDF.type,
        OWL.Class,
    ))

    graph.add((
        VZ.CloseGameSituation,
        RDFS.subClassOf,
        VZ.GameSituation,
    ))

    # ------------------------------------------
    # CLUTCH
    #
    # Operational semantics:
    #
    # ClutchSituation =
    #     LateGameSituation
    #     AND
    #     CloseGameSituation
    #
    # The actual instance inference is performed
    # by infer_game_situations().
    # ------------------------------------------

    graph.add((
        VZ.ClutchSituation,
        RDF.type,
        OWL.Class,
    ))

    graph.add((
        VZ.ClutchSituation,
        RDFS.subClassOf,
        VZ.LateGameSituation,
    ))

    graph.add((
        VZ.ClutchSituation,
        RDFS.subClassOf,
        VZ.CloseGameSituation,
    ))

    # ==================================================
    # POSSESSION OUTCOMES / STRUCTURE
    #
    # Semantic dimension describing WHAT HAPPENS
    # during a possession.
    # ==================================================

    graph.add((
        VZ.PossessionOutcome,
        RDF.type,
        OWL.Class,
    ))

    # ------------------------------------------
    # SCORING POSSESSION
    # ------------------------------------------

    graph.add((
        VZ.ScoringPossession,
        RDF.type,
        OWL.Class,
    ))

    graph.add((
        VZ.ScoringPossession,
        RDFS.subClassOf,
        VZ.PossessionOutcome,
    ))

    # ------------------------------------------
    # TURNOVER POSSESSION
    # ------------------------------------------

    graph.add((
        VZ.TurnoverPossession,
        RDF.type,
        OWL.Class,
    ))

    graph.add((
        VZ.TurnoverPossession,
        RDFS.subClassOf,
        VZ.PossessionOutcome,
    ))

    # ------------------------------------------
    # SECOND-CHANCE POSSESSION
    #
    # Current POC operational definition:
    # possession containing an offensive rebound.
    # ------------------------------------------

    graph.add((
        VZ.SecondChancePossession,
        RDF.type,
        OWL.Class,
    ))

    graph.add((
        VZ.SecondChancePossession,
        RDFS.subClassOf,
        VZ.PossessionOutcome,
    ))

    # ------------------------------------------
    # THREE-POINT SCORING POSSESSION
    #
    # More specific form of ScoringPossession.
    # ------------------------------------------

    graph.add((
        VZ.ThreePointScoringPossession,
        RDF.type,
        OWL.Class,
    ))

    graph.add((
        VZ.ThreePointScoringPossession,
        RDFS.subClassOf,
        VZ.ScoringPossession,
    ))

    # ==================================================
    # SCORE SITUATION CLASSES
    # ==================================================

    graph.add((
        VZ.LeadingPossession,
        RDF.type,
        OWL.Class,
    ))

    graph.add((
        VZ.TrailingPossession,
        RDF.type,
        OWL.Class,
    ))

    graph.add((
        VZ.TiedPossession,
        RDF.type,
        OWL.Class,
    ))

    graph.add((
        VZ.OnePossessionGameSituation,
        RDF.type,
        OWL.Class,
    ))

    graph.add((
        VZ.OnePossessionGameSituation,
        RDFS.subClassOf,
        VZ.CloseGameSituation,
    ))

    return graph


def infer_game_situations(graph):

    possessions = set(
        graph.subjects(
            RDF.type,
            VZ.Possession,
        )
    )

    for possession in possessions:

        # ==================================================
        # READ POSSESSION CONTEXT
        # ==================================================

        period = graph.value(
            possession,
            VZ.startPeriod,
        )

        seconds_remaining = graph.value(
            possession,
            VZ.startSecondsRemaining,
        )

        # ==================================================
        # READ POSSESSION EVENTS ONCE
        # ==================================================

        events = list(
            graph.objects(
                possession,
                VZ.hasEvent,
            )
        )

        event_types = []

        for event in events:

            event_type = graph.value(
                event,
                VZ.eventType,
            )

            if event_type is not None:
                event_types.append(
                    str(event_type)
                )

        # ==================================================
        # 1. LATE GAME SITUATION
        #
        # Q4 + final 5 minutes
        # ==================================================

        is_late_game = (
            period is not None
            and seconds_remaining is not None
            and int(period) == 4
            and int(seconds_remaining) <= 300
        )

        if is_late_game:
            graph.add((
                possession,
                RDF.type,
                VZ.LateGameSituation,
            ))

        # ==================================================
        # 2. CLOSE GAME SITUATION
        #
        # At least one event in possession has
        # |score differential| <= 5
        # ==================================================

        is_close_game = False

        for event in events:

            score_diff = graph.value(
                event,
                VZ.scoreDifferential,
            )

            if score_diff is None:
                continue

            score_diff_value = int(
                score_diff
            )

            if abs(score_diff_value) <= 5:
                is_close_game = True
                break

        if is_close_game:
            graph.add((
                possession,
                RDF.type,
                VZ.CloseGameSituation,
            ))

        # ==================================================
        # 3. SCORE STATE AT POSSESSION START
        #
        # Perspective: offensive team
        # ==================================================

        offensive_team = graph.value(
            possession,
            VZ.offensiveTeam,
        )

        start_score_diff = None

        for event in events:

            perspective_team = graph.value(
                event,
                VZ.scorePerspectiveTeam,
            )

            score_diff = graph.value(
                event,
                VZ.scoreDifferential,
            )

            if (
                perspective_team is None
                or score_diff is None
            ):
                continue

            score_diff_value = int(
                score_diff
            )

            # scoreDifferential is stored from
            # the event team's perspective.
            #
            # Convert it to the offensive team's
            # perspective.

            if perspective_team == offensive_team:

                start_score_diff = (
                    score_diff_value
                )

            else:

                start_score_diff = (
                    -score_diff_value
                )

            # First event carrying score information
            # represents possession-start state.
            break

        # ==================================================
        # 4. LEADING / TRAILING / TIED
        # ==================================================

        if start_score_diff is not None:

            if start_score_diff > 0:

                graph.add((
                    possession,
                    RDF.type,
                    VZ.LeadingPossession,
                ))

            elif start_score_diff < 0:

                graph.add((
                    possession,
                    RDF.type,
                    VZ.TrailingPossession,
                ))

            else:

                graph.add((
                    possession,
                    RDF.type,
                    VZ.TiedPossession,
                ))

            # ==============================================
            # 5. ONE-POSSESSION GAME
            #
            # Margin <= 3 points at possession start.
            # Includes tied situations.
            # ==============================================

            if abs(start_score_diff) <= 3:

                graph.add((
                    possession,
                    RDF.type,
                    VZ.OnePossessionGameSituation,
                ))

        # ==================================================
        # 6. CLUTCH SITUATION
        #
        # LateGame AND CloseGame
        # ==================================================

        is_clutch = (
            is_late_game
            and is_close_game
        )

        if is_clutch:
            graph.add((
                possession,
                RDF.type,
                VZ.ClutchSituation,
            ))

        # ==================================================
        # 7. SCORING POSSESSION
        # ==================================================

        scoring_event_types = {
            "TWO_PT_MADE",
            "THREE_PT_MADE",
            "FT_MADE",
        }

        is_scoring = any(
            event_type in scoring_event_types
            for event_type in event_types
        )

        if is_scoring:
            graph.add((
                possession,
                RDF.type,
                VZ.ScoringPossession,
            ))

        # ==================================================
        # 8. TURNOVER POSSESSION
        # ==================================================

        is_turnover = (
            "TURNOVER" in event_types
        )

        if is_turnover:
            graph.add((
                possession,
                RDF.type,
                VZ.TurnoverPossession,
            ))

        # ==================================================
        # 9. THREE-POINT SCORING POSSESSION
        # ==================================================

        is_three_point_scoring = (
            "THREE_PT_MADE" in event_types
        )

        if is_three_point_scoring:
            graph.add((
                possession,
                RDF.type,
                VZ.ThreePointScoringPossession,
            ))

        # ==================================================
        # 10. SECOND-CHANCE POSSESSION
        #
        # POC definition:
        # possession containing an offensive rebound
        # ==================================================

        is_second_chance = (
            "OFF_REBOUND" in event_types
        )

        if is_second_chance:
            graph.add((
                possession,
                RDF.type,
                VZ.SecondChancePossession,
            ))

    return graph