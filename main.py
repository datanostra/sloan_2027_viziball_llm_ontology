import sys
import os
from dotenv import load_dotenv

import app.util as util
import app.graph.util as gu

from itertools import groupby

from rdflib import Namespace, RDF

from rdf_builder import (
    build_rdf_graph,
)

from ontology.viziball_ontology import (
    add_viziball_ontology,
    infer_game_situations,
)

from ontology_benchmark import (
    run_ontology_benchmark,
)

load_dotenv()

# ============================================================
# CONFIG
# ============================================================

NEO4J_URI = os.environ["NEO4J_URI"]
NEO4J_USER = os.environ["NEO4J_USER"]
NEO4J_PASSWORD = os.environ["NEO4J_PASSWORD"]

CHAMPIONSHIP = "nba"
VZ = Namespace("https://viziball.io/ontology/")
RES = Namespace("https://viziball.io/resource/")

BENCHMARK_GAMES = {
    f"bcl_{i:03d}": {
        "game_id": game_id,
        "db": "BCL",
    }
    for i, game_id in enumerate(
        [
            "202510070PROM",
            "202510070WUE",
            "202510070NYMB",
            "202510070GALA",
            "202510070SLB",
            "202510070RIGA",
            "202510070CJB",
            "202510070VILN",
            "202510080UNIC",
            "202510080SPAR",
            "202510080HOLO",
            "202510080OOST",
            "202510080ALBA",
            "202510080TPS",
            "202510080TOFA",
            "202510080OLAJ",
            "202510150DGC",
            "202510150OOST",
            "202510150HDB",
            "202510140RIGA",
            "202510140KARD",
            "202510140TENE",
            "202510140BURS",
            "202510140HOLO",
            "202510140WUE",
            "202510140TPS",
            "202510140NYMB",
            "202510150TS",
            "202510150SLB",
            "202510150AEK",
            "202510150SAB",
            "202510150WARS",
            "202510220VILN",
            "202510210GALA",
            "202510210MSB",
            "202510210IGOK",
            "202510210SPAR",
            "202511040HOLO",
            "202511040TS",
            "202511040WUE",
            "202510290ELAN",
            "202510290MSK",
            "202510290UNIC",
            "202510290OLAJ",
            "202510280TOFA",
            "202510280ALBA",
            "202510280LEV",
            "202510280HERZ",
            "202510220CHO",
            "202510220HDB",
            "202510220CJB",
            "202511050SLB",
            "202511050BURS",
            "202511050DGC",
            "202511050VILN",
            "202511050PROM",
            "202511110LEV",
            "202511110KARD",
            "202511110TENE",
            "202511110TPS",
            "202511120AEK",
            "202511120SAB",
            "202511120MSK",
            "202511180WARS",
            "202511180HDB",
            "202511180GALA",
            "202511180MSB",
            "202511120NYMB",
            "202512090OOST",
            "202512090KARD",
            "202512090ELAN",
            "202512090HERZ",
            "202512090SAB",
            "202511190CJB",
            "202511190CHO",
            "202511190IGOK",
            "202511190SPAR",
            "202512160TOFA",
            "202512160DGC",
            "202512160ALBA",
            "202512160ELAN",
            "202512160LEV",
            "202512170WARS",
            "202512100TENE",
            "202512100RIGA",
            "202512100AEK",
            "202512160OLAJ",
            "202512160HERZ",
            "202512160MSB",
            "202512170PROM",
            "202512170UNIC",
            "202512170MSK",
            "202512170TS",
            "202512170IGOK",
            "202512170BURS",
            "202512170CHO",
            "202601060MSK",
            "202601060OLAJ",
            "202601060WUE",
            "202601060HDB",
            "202601060TOFA",
            "202601060HOLO",
            "202601060SPAR",
            "202601060ELAN",
            "202601090CHO",
            "202601140TOFA",
            "202601080LEV",
            "202601080TS",
            "202601080PROM",
            "202601080MSB",
            "202601080NYMB",
            "202601080KARD",
            "202601140WUE",
            "202601130OLAJ",
            "202512100SAB",
            "202601080TPS",
            "202601080CHO",
            "202601130ELAN",
            "202601130MSK",
            "202601130HDB",
            "202601140SPAR",
            "202601280NYMB",
            "202602110KARD",
            "202602030TS",
            "202601200VILN",
            "202601200TENE",
            "202601200DGC",
            "202601200TOFA",
            "202602040GALA",
            "202601210GALA",
            "202601210CJB",
            "202601210AEK",
            "202601270HOLO",
            "202602030UNIC",
            "202602040MSB",
            "202602040ALBA",
            "202602100NYMB",
            "202602100ELAN",
            "202602110MSB",
            "202602100KARD",
            "202601270NYMB",
            "202601280TENE",
            "202602110TS",
            "202601210UNIC",
            "202601270ELAN",
            "202601270KARD",
            "202602030WUE",
            "202602030TOFA",
            "202602110WUE",
            "202602040TS",
            "202602100ALBA",
            "202601270VILN",
            "202601280AEK",
            "202602040DGC",
            "202601280CJB",
            "202602100HOLO",
            "202603100HOLO",
            "202603100ELAN",
            "202603100CJB",
            "202603110TENE",
            "202603110KARD",
            "202603110VILN",
            "202603110NYMB",
            "202603110AEK",
            "202603170UNIC",
            "202603170DGC",
            "202603170TS",
            "202603170WUE",
            "202603180TOFA",
            "202603180GALA",
            "202604010VILN",
            "202604010AEK",
            "202604010TENE",
            "202604010UNIC",
            "202603180ALBA",
            "202603180MSB",
            "202604080GALA",
            "202604070NYMB",
            "202604070CJB",
            "202604080ALBA",
            "202604150AEK",
            "202605070UNIC",
            "202605070VILN",
            "202604150TENE",
            "202605090UNIC",
            "202605090AEK",
        ],
        start=1,
    )
}

BENCHMARK_GAMES = dict(
    list(
        BENCHMARK_GAMES.items()
    )[:2]
)

# ============================================================
# ACTION TYPES
# ============================================================

ACTION_TYPES = {
    0: "TWO_PT_MISSED",
    1: "TWO_PT_MADE",
    2: "THREE_PT_MISSED",
    3: "THREE_PT_MADE",
    4: "FT_MISSED",
    5: "FT_MADE",
    6: "ASSIST",
    7: "BLOCK",
    8: "DEF_REBOUND",
    9: "OFF_REBOUND",
    10: "TURNOVER",
    11: "SHOOTING_FOUL",
    12: "PERSONAL_FOUL",
    13: "TECHNICAL_FOUL",
    14: "OFFENSIVE_FOUL",
    15: "IN",
    16: "OUT",
    17: "TIMEOUT",
    18: "STEAL",
    19: "DEFENSIVE_FOUL",
}

POSSESSION_END_ACTIONS = {
    "TURNOVER",
    "TWO_PT_MADE",
    "THREE_PT_MADE",
}

SHOT_ACTIONS = {
    "TWO_PT_MISSED",
    "TWO_PT_MADE",
    "THREE_PT_MISSED",
    "THREE_PT_MADE",
}

OFFENSIVE_ACTIONS = SHOT_ACTIONS | {
    "TURNOVER",
    "OFF_REBOUND",
}

SECONDARY_ACTIONS = {
    "ASSIST",
    "STEAL",
    "BLOCK",
}

# ============================================================
# NEO4J
# ============================================================

QUERY = """
MATCH (g:Game {gid: $gid})

MATCH (t:Team)-[:BOXSCORE]->(g)

MATCH (p:Player)-[r:PLAYS]->(g)
WHERE r.tid = t.tid

WITH
    g,
    t,
    collect({
        pid: p.pid,
        fn: p.fn,
        ln: p.ln,
        prds: r.prds
    }) AS players

RETURN
    g.gid AS gid,
    g.pbp AS pbp,
    collect({
        tid: t.tid,
        players: players
    }) AS teams
"""

def ingest_game_raw(
    raw_path,
):

    # ==================================================
    # LOAD GAME FROM RAW FILE
    # ==================================================

    game = load_raw_game(
        raw_path
    )

    # ==================================================
    # PLAY-BY-PLAY PROCESSING
    # ==================================================

    actions = enrich_actions(
        game["pbp"],
        game["teams"],
    )

    actions = add_team_to_actions(
        actions,
        game["teams"],
    )

    possessions = build_possessions(
        actions,
        game["teams"],
    )

    # Make actions available to game-time inference
    game["actions"] = actions

    game_time = infer_game_time_structure(
        game
    )

    # ==================================================
    # BUILD FACTUAL RDF GRAPH
    # ==================================================

    rdf_graph = build_rdf_graph(
        game,
        possessions,
        game_time,
    )

    # ==================================================
    # ONTOLOGY + SEMANTIC INFERENCE
    # ==================================================

    add_viziball_ontology(
        rdf_graph
    )

    infer_game_situations(
        rdf_graph
    )

    # ==================================================
    # RESULT
    # ==================================================

    return {
        "game": game,
        "actions": actions,
        "possessions": possessions,
        "game_time": game_time,
        "rdf_graph": rdf_graph,
    }

def compare_ingestions(
    neo4j_data,
    raw_data,
):

    print("\n")
    print("=" * 70)
    print("NEO4J VS RAW INGESTION")
    print("=" * 70)

    # --------------------------------------------------
    # COUNTS
    # --------------------------------------------------

    metrics = {
        "actions": (
            len(neo4j_data["actions"]),
            len(raw_data["actions"]),
        ),
        "possessions": (
            len(neo4j_data["possessions"]),
            len(raw_data["possessions"]),
        ),
        "events": (
            sum(
                len(p["events"])
                for p in neo4j_data["possessions"]
            ),
            sum(
                len(p["events"])
                for p in raw_data["possessions"]
            ),
        ),
        "rdf_triples": (
            len(neo4j_data["rdf_graph"]),
            len(raw_data["rdf_graph"]),
        ),
    }

    all_ok = True

    for name, (neo_value, raw_value) in metrics.items():

        status = (
            "PASS"
            if neo_value == raw_value
            else "FAIL"
        )

        if status == "FAIL":
            all_ok = False

        print(
            f"{name:15}"
            f" NEO4J={neo_value:<8}"
            f" RAW={raw_value:<8}"
            f" {status}"
        )

    # --------------------------------------------------
    # GAME TIME
    # --------------------------------------------------

    same_game_time = (
        neo4j_data["game_time"]
        == raw_data["game_time"]
    )

    print(
        f"{'game_time':15}",
        "PASS"
        if same_game_time
        else "FAIL"
    )

    if not same_game_time:

        all_ok = False

        print(
            "NEO4J:",
            neo4j_data["game_time"],
        )

        print(
            "RAW:  ",
            raw_data["game_time"],
        )

    # --------------------------------------------------
    # ONTOLOGY COUNTS
    # --------------------------------------------------

    ontology_classes = [
        VZ.LateGameSituation,
        VZ.CloseGameSituation,
        VZ.ClutchSituation,
        VZ.ScoringPossession,
        VZ.TurnoverPossession,
        VZ.SecondChancePossession,
        VZ.ThreePointScoringPossession,
        VZ.LeadingPossession,
        VZ.TrailingPossession,
        VZ.TiedPossession,
        VZ.OnePossessionGameSituation,
    ]

    print("\nONTOLOGY")

    for ontology_class in ontology_classes:

        neo_instances = set(
            neo4j_data["rdf_graph"].subjects(
                RDF.type,
                ontology_class,
            )
        )

        raw_instances = set(
            raw_data["rdf_graph"].subjects(
                RDF.type,
                ontology_class,
            )
        )

        neo_count = len(neo_instances)
        raw_count = len(raw_instances)

        status = (
            "PASS"
            if neo_count == raw_count
            else "FAIL"
        )

        if status == "FAIL":
            all_ok = False

        print(
            f"{ontology_class.split('/')[-1]:35}"
            f" NEO4J={neo_count:<5}"
            f" RAW={raw_count:<5}"
            f" {status}"
        )

    # --------------------------------------------------
    # FINAL
    # --------------------------------------------------

    print("-" * 70)

    print(
        "INGESTION EQUIVALENCE:",
        "PASS"
        if all_ok
        else "FAIL"
    )

    return all_ok

def ingest_game(
    logger,
    ctx,
    db,
    game_id,
):

    # ==================================================
    # LOAD GAME
    # ==================================================

    game = get_game(
        logger,
        ctx,
        db,
        game_id,
    )

    # ==================================================
    # PLAY-BY-PLAY PROCESSING
    # ==================================================

    actions = enrich_actions(
        game["pbp"],
        game["teams"],
    )

    actions = add_team_to_actions(
        actions,
        game["teams"],
    )

    possessions = build_possessions(
        actions,
        game["teams"],
    )

    game_time = infer_game_time_structure(
        game
    )

    # ==================================================
    # BUILD FACTUAL RDF GRAPH
    # ==================================================

    rdf_graph = build_rdf_graph(
        game,
        possessions,
        game_time,
    )

    # ==================================================
    # ONTOLOGY + SEMANTIC INFERENCE
    # ==================================================

    add_viziball_ontology(
        rdf_graph
    )

    infer_game_situations(
        rdf_graph
    )

    # ==================================================
    # ONTOLOGY DEBUG
    # ==================================================

    ontology_classes = [
        VZ.LateGameSituation,
        VZ.CloseGameSituation,
        VZ.ClutchSituation,
        VZ.ScoringPossession,
        VZ.TurnoverPossession,
        VZ.SecondChancePossession,
        VZ.ThreePointScoringPossession,
    ]

    # ==================================================
    # RESULT
    # ==================================================

    return {
        "game": game,
        "actions": actions,
        "possessions": possessions,
        "game_time": game_time,
        "rdf_graph": rdf_graph,
    }


def get_game(logger, ctx, db, gid):

    result = gu.execute_query(
        logger,
        ctx,
        db,
        "single",
        QUERY,
        gid=gid
    )

    if result is None:
        raise ValueError(f"Game not found: {gid}")

    return {
        "gid": result["gid"],
        "pbp": result["pbp"],
        "teams": result["teams"]
    }


# ============================================================
# PBP
# ============================================================

def parse_pbp(pbp):

    actions = []

    if not pbp:
        return actions

    for index, raw in enumerate(pbp.split(";")):

        fields = raw.split("|")

        action_id = int(fields[0])

        actions.append({
            "index": index,
            "action_id": action_id,
            "action_type": ACTION_TYPES[action_id],
            "entity_id": int(fields[1]),
            "second": int(fields[2]),
            "detail": fields[3] or None,
            "feet": float(fields[4]) if fields[4] else None,
            "x": float(fields[5]) if fields[5] else None,
            "y": float(fields[6]) if fields[6] else None,
        })

    return actions


# ============================================================
# POSSESSIONS
# ============================================================
def build_possessions(actions, teams):

    team_ids = [int(team["tid"]) for team in teams]

    possessions = []
    current = []

    possession_id = 0
    offensive_team = None

    CLEAR_OFFENSIVE_ACTIONS = {
        "TWO_PT_MISSED",
        "TWO_PT_MADE",
        "THREE_PT_MISSED",
        "THREE_PT_MADE",
        "OFF_REBOUND",
        "TURNOVER",
    }

    FT_ACTIONS = {
        "FT_MADE",
        "FT_MISSED",
    }

    # --------------------------------------------------
    # HELPERS
    # --------------------------------------------------

    def opponent(tid):

        for team_id in team_ids:
            if team_id != tid:
                return team_id

        return None

    def close_possession(end_reason, confidence="high"):

        nonlocal possession_id
        nonlocal current

        if not current or offensive_team is None:
            return

        possession_id += 1

        defensive_team = opponent(offensive_team)

        # On prend le lineup au début de la possession
        lineups = get_lineups(
            teams,
            current[0]["second"]
        )

        possessions.append({
            "id": possession_id,

            "offensive_team": offensive_team,
            "defensive_team": defensive_team,

            "offensive_lineup": lineups[offensive_team],
            "defensive_lineup": lineups[defensive_team],

            "start_second": current[0]["second"],
            "end_second": current[-1]["second"],

            "end_reason": end_reason,
            "confidence": confidence,

            "actions": current,
        })

        current = []

    def is_and_one(index):
        """
        Détecte :

        TWO_PT_MADE / THREE_PT_MADE
        [ASSIST éventuelle]
        faute défensive
        FT du même joueur

        au même timestamp.
        """

        shot = actions[index]

        if shot["action_type"] not in {
            "TWO_PT_MADE",
            "THREE_PT_MADE",
        }:
            return False

        shot_team = shot["team_id"]
        shooter = shot["entity_id"]
        second = shot["second"]

        foul_found = False

        j = index + 1

        while j < len(actions):

            candidate = actions[j]

            # Dès qu'on change de timestamp,
            # ce n'est plus un and-one.
            if candidate["second"] != second:
                break

            candidate_type = candidate["action_type"]

            # Assist du panier
            if candidate_type == "ASSIST":
                j += 1
                continue

            # Faute de l'équipe adverse
            if (
                candidate_type in {
                    "DEFENSIVE_FOUL",
                    "SHOOTING_FOUL",
                    "PERSONAL_FOUL",
                }
                and candidate["team_id"] == opponent(shot_team)
            ):
                foul_found = True
                j += 1
                continue

            # Substitutions éventuellement présentes
            if candidate_type in {"IN", "OUT"}:
                j += 1
                continue

            # FT du joueur qui vient de marquer
            if (
                candidate_type in FT_ACTIONS
                and candidate["team_id"] == shot_team
                and candidate["entity_id"] == shooter
            ):
                return foul_found

            j += 1

        return False


    def is_technical_ft(index):
        """
        Détermine si le FT courant est associé à une faute technique.

        On cherche une TECHNICAL_FOUL juste avant le FT,
        en autorisant les substitutions entre les deux.
        """

        ft = actions[index]
        ft_second = ft["second"]

        j = index - 1

        while j >= 0:

            candidate = actions[j]

            # On ne remonte pas au-delà du timestamp du FT.
            if candidate["second"] != ft_second:
                break

            candidate_type = candidate["action_type"]

            if candidate_type == "TECHNICAL_FOUL":
                return True

            # Actions pouvant se trouver entre la faute et le FT.
            if candidate_type in {"IN", "OUT"}:
                j -= 1
                continue

            # Un autre FT peut appartenir à la même séquence.
            if candidate_type in FT_ACTIONS:
                j -= 1
                continue

            j -= 1

        return False

    # --------------------------------------------------
    # MAIN LOOP
    # --------------------------------------------------

    i = 0

    while i < len(actions):

        action = actions[i]

        action_type = action["action_type"]
        action_team = action["team_id"]
        second = action["second"]

        # --------------------------------------------------
        # 1. ASSIST / STEAL
        #
        # Ils peuvent être générés juste après l'action
        # ayant terminé la possession.
        # --------------------------------------------------

        if (
            action_type in {"ASSIST", "STEAL"}
            and possessions
            and not current
            and second == possessions[-1]["end_second"]
        ):

            possessions[-1]["actions"].append(action)

            i += 1
            continue

        # --------------------------------------------------
        # 2. SEQUENCE DE LANCERS FRANCS
        # --------------------------------------------------

        if action_type in FT_ACTIONS:

            ft_team = action_team
            ft_player = action["entity_id"]
            ft_second = second
            technical_ft = is_technical_ft(i)

            ft_sequence = []
            sequence_actions = []

            j = i

            while j < len(actions):

                candidate = actions[j]
                candidate_type = candidate["action_type"]

                # FT du même joueur / équipe / timestamp
                if (
                    candidate_type in FT_ACTIONS
                    and candidate["team_id"] == ft_team
                    and candidate["entity_id"] == ft_player
                    and candidate["second"] == ft_second
                ):

                    ft_sequence.append(candidate)
                    sequence_actions.append(candidate)

                    j += 1
                    continue

                # Substitution au même timestamp
                if (
                    candidate_type in {"IN", "OUT"}
                    and candidate["second"] == ft_second
                ):

                    sequence_actions.append(candidate)

                    j += 1
                    continue

                break

            # ----------------------------------------------
            # Identification de l'équipe offensive
            # ----------------------------------------------

            if offensive_team is None:

                offensive_team = ft_team

            elif ft_team != offensive_team:

                if current:

                    close_possession(
                        "IMPLICIT_CHANGE",
                        confidence="low"
                    )

                offensive_team = ft_team

            current.extend(sequence_actions)

            last_ft = ft_sequence[-1]

            # ----------------------------------------------
            # Dernier FT marqué
            # ----------------------------------------------

            if last_ft["action_type"] == "FT_MADE":

                previous_offensive_team = offensive_team

                close_possession(
                    "FT_MADE",
                    confidence="high"
                )

                offensive_team = opponent(
                    previous_offensive_team
                )

            # ----------------------------------------------
            # Dernier FT raté :
            # on attend le rebond.
            # ----------------------------------------------

            i = j
            continue

        # --------------------------------------------------
        # 3. INITIALISATION
        # --------------------------------------------------

        if offensive_team is None:

            if (
                action_type in CLEAR_OFFENSIVE_ACTIONS
                and action_team is not None
            ):

                offensive_team = action_team

            current.append(action)

            i += 1
            continue

        # --------------------------------------------------
        # 4. RESYNCHRONISATION
        #
        # Une action offensive explicite d'une autre équipe
        # indique qu'une transition manque dans le PBP.
        # --------------------------------------------------

        if (
            action_type in CLEAR_OFFENSIVE_ACTIONS
            and action_team is not None
            and action_team != offensive_team
        ):

            if current:

                close_possession(
                    "IMPLICIT_CHANGE",
                    confidence="low"
                )

            offensive_team = action_team

        # --------------------------------------------------
        # 5. AJOUT ACTION
        # --------------------------------------------------

        current.append(action)

        defensive_team = opponent(offensive_team)

        end_reason = None

        # --------------------------------------------------
        # 6. TURNOVER
        # --------------------------------------------------

        if (
            action_type == "TURNOVER"
            and action_team == offensive_team
        ):

            end_reason = "TURNOVER"

        # --------------------------------------------------
        # 7. PANIER MARQUE
        #
        # IMPORTANT :
        # on vérifie maintenant le AND-ONE avant de fermer.
        # --------------------------------------------------

        elif (
            action_type in {
                "TWO_PT_MADE",
                "THREE_PT_MADE",
            }
            and action_team == offensive_team
        ):

            if is_and_one(i):

                # Ne surtout pas fermer ici.
                # La possession sera fermée par le FT.
                end_reason = None

            else:

                end_reason = "MADE_SHOT"

        # --------------------------------------------------
        # 8. REBOND DEFENSIF
        # --------------------------------------------------

        elif (
            action_type == "DEF_REBOUND"
            and action_team == defensive_team
        ):

            end_reason = "DEF_REBOUND"

        # OFF_REBOUND :
        # rien à faire -> la possession continue.

        # --------------------------------------------------
        # 9. FIN DE POSSESSION
        # --------------------------------------------------

        if end_reason is not None:

            previous_offensive_team = offensive_team

            close_possession(
                end_reason,
                confidence="high"
            )

            offensive_team = opponent(
                previous_offensive_team
            )

        i += 1

    # --------------------------------------------------
    # 10. POSSESSION NON TERMINEE
    # --------------------------------------------------

    if current:

        print(
            "UNFINISHED POSSESSION:",
            "OFF =", offensive_team,
            "|",
            current[0]["second"],
            "->",
            current[-1]["second"],
            "| actions =", len(current)
        )

    for possession in possessions:
        possession["events"] = build_events(possession)

    return possessions

def infer_game_time_structure(game):
    """
    Infer the temporal structure of a basketball game from player
    presence intervals (prds), without relying on the competition name.

    Supports:
    - 4 x 12 min regulation
    - 4 x 10 min regulation
    - overtime detection
    """

    boundaries = set()

    for team in game.get("teams", []):
        for player in team.get("players", []):
            for second in player.get("prds", []):
                boundaries.add(int(second))

    # --------------------------------------------------
    # REGULATION PERIOD DURATION
    # --------------------------------------------------

    candidates = [
        {
            "period_seconds": 720,
            "boundaries": {720, 1440, 2160, 2880},
        },
        {
            "period_seconds": 600,
            "boundaries": {600, 1200, 1800, 2400},
        },
    ]

    matches = []

    for candidate in candidates:

        expected = candidate["boundaries"]

        score = len(
            expected.intersection(boundaries)
        )

        matches.append((
            score,
            candidate["period_seconds"],
        ))

    matches.sort(reverse=True)

    best_score, period_seconds = matches[0]

    # Require at least several observed period boundaries.
    if best_score < 3:
        raise ValueError(
            "Unable to infer game period duration "
            f"from player presence data. "
            f"Candidate scores: {matches}"
        )

    regulation_period_count = 4

    regulation_end_second = (
        regulation_period_count
        * period_seconds
    )

    # --------------------------------------------------
    # MAXIMUM OBSERVED GAME SECOND
    # --------------------------------------------------

    observed_seconds = []

    for action in game.get("actions", []):
        if action.get("second") is not None:
            observed_seconds.append(
                int(action["second"])
            )

    # game["actions"] may not exist at this stage.
    # Fall back to player presence intervals.
    observed_seconds.extend(boundaries)

    if not observed_seconds:
        raise ValueError(
            "Unable to determine game duration"
        )

    max_second = max(observed_seconds)

    # --------------------------------------------------
    # OVERTIME
    # --------------------------------------------------

    overtime_period_seconds = 300

    if max_second <= regulation_end_second:
        overtime_count = 0
    else:
        overtime_elapsed = (
            max_second
            - regulation_end_second
        )

        overtime_count = (
            overtime_elapsed
            + overtime_period_seconds
            - 1
        ) // overtime_period_seconds

    return {
        "regulation_period_count":
            regulation_period_count,

        "regulation_period_seconds":
            period_seconds,

        "regulation_end_second":
            regulation_end_second,

        "overtime_period_seconds":
            overtime_period_seconds,

        "overtime_count":
            overtime_count,

        "total_period_count":
            regulation_period_count
            + overtime_count,

        "max_observed_second":
            max_second,
    }

def build_events(possession):

    actions = possession["actions"]
    events = []

    i = 0

    while i < len(actions):

        action = actions[i]
        action_type = action["action_type"]

        # Pas des événements constitutifs de la possession
        if action_type in {"IN", "OUT", "TIMEOUT"}:
            i += 1
            continue

        # Les actions secondaires seront rattachées
        # à l'événement principal précédent.
        if action_type in SECONDARY_ACTIONS:
            i += 1
            continue

        event = {
            "type": action_type,
            "second": action["second"],
            "team_id": action["team_id"],
            "players": {},
            "actions": [action],
        }

        # Joueur principal
        if action["entity_id"] is not None:

            role = {
                "TWO_PT_MADE": "shooter",
                "TWO_PT_MISSED": "shooter",
                "THREE_PT_MADE": "shooter",
                "THREE_PT_MISSED": "shooter",
                "FT_MADE": "shooter",
                "FT_MISSED": "shooter",
                "TURNOVER": "turnover",
                "OFF_REBOUND": "rebounder",
                "DEF_REBOUND": "rebounder",
                "SHOOTING_FOUL": "fouler",
                "PERSONAL_FOUL": "fouler",
                "DEFENSIVE_FOUL": "fouler",
                "OFFENSIVE_FOUL": "fouler",
                "TECHNICAL_FOUL": "fouler",
            }.get(action_type)

            if role:
                event["players"][role] = action["entity_id"]

        # Cherche les actions secondaires appartenant
        # au même événement.
        j = i + 1

        while j < len(actions):

            secondary = actions[j]

            if secondary["second"] != action["second"]:
                break

            secondary_type = secondary["action_type"]

            if secondary_type not in SECONDARY_ACTIONS:
                break

            if secondary_type == "ASSIST":
                event["players"]["assist"] = secondary["entity_id"]

            elif secondary_type == "STEAL":
                event["players"]["steal"] = secondary["entity_id"]

            elif secondary_type == "BLOCK":
                event["players"]["block"] = secondary["entity_id"]

            event["actions"].append(secondary)

            j += 1

        events.append(event)

        i = j

    return events

def group_actions_by_second(actions):

    groups = []

    for second, group in groupby(
        actions,
        key=lambda a: a["second"]
    ):
        groups.append({
            "second": second,
            "actions": list(group)
        })

    return groups

def build_player_to_team(teams):
    player_to_team = {}

    for team in teams:
        tid = int(team["tid"])

        for player in team["players"]:
            player_to_team[int(player["pid"])] = tid

    return player_to_team

def find_offensive_team(actions):

    for action in actions:

        if (
            action["action_type"] in OFFENSIVE_ACTIONS
            and action["team_id"] is not None
        ):
            return action["team_id"]

    return None

def add_team_to_actions(actions, teams):

    player_to_team = build_player_to_team(teams)

    for action in actions:

        # TIMEOUT : entity_id est déjà un team_id
        if action["action_type"] == "TIMEOUT":
            action["team_id"] = action["entity_id"]

        else:
            action["team_id"] = player_to_team.get(
                action["entity_id"]
            )

    return actions

# ============================================================
# LINEUPS
# ============================================================

def get_players_on_court(players, second):

    ids = []

    for player in players:

        periods = player["prds"]

        for start, end in zip(
            periods[0::2],
            periods[1::2]
        ):

            # Même convention que ton code Viziball actuel
            if start < second <= end:

                ids.append(int(player["pid"]))
                break

    return sorted(ids)


def get_lineup_id(player_ids):

    return "_".join(
        map(str, sorted(player_ids))
    )


def get_lineups(teams, second):

    result = {}

    for team in teams:

        tid = int(team["tid"])

        players = get_players_on_court(
            team["players"],
            second
        )

        result[tid] = {
            "players": players,
            "lineup_id": get_lineup_id(players)
        }

    return result


def enrich_actions(pbp, teams):

    actions = parse_pbp(pbp)

    for action in actions:

        action["lineups"] = get_lineups(
            teams,
            action["second"]
        )

    return actions


def main():

    logger = util.get_logger("task")
    ctx = util.get_graph_database_driver(logger)

    total_games = len(BENCHMARK_GAMES)

    successful_games = 0
    ingestion_errors = 0
    benchmark_errors = 0

    try:

        # ==================================================
        # PROCESS ONE GAME AT A TIME
        # ==================================================

        for game_index, (label, config) in enumerate(
            BENCHMARK_GAMES.items(),
            start=1,
        ):

            game_id = config["game_id"]
            db = config["db"]

            print("\n")
            print("=" * 70)
            print(
                f"GAME {game_index}/{total_games}"
                f" | {label}"
                f" | {game_id}"
                f" | DB={db}"
            )
            print("=" * 70)

            if game_id is None:
                print("SKIP | game_id is None")
                continue

            game_data = None

            # ==================================================
            # 1. INGEST CURRENT GAME
            # ==================================================

            try:

                print(
                    f"\nINGESTION START | {game_id}"
                )

                game_data = ingest_game(
                    logger,
                    ctx,
                    db,
                    game_id,
                )

                event_count = sum(
                    len(possession["events"])
                    for possession
                    in game_data["possessions"]
                )

                print(
                    f"\nINGESTION PASS | {game_id}"
                    f" | ACTIONS={len(game_data['actions'])}"
                    f" | POSSESSIONS={len(game_data['possessions'])}"
                    f" | EVENTS={event_count}"
                    f" | TRIPLES={len(game_data['rdf_graph'])}"
                )

                successful_games += 1

            except Exception as exc:

                ingestion_errors += 1

                print("\n")
                print("!" * 70)
                print(
                    f"INGESTION_ERROR"
                    f" | GAME={game_id}"
                    f" | {type(exc).__name__}"
                    f" | {exc}"
                )
                print("!" * 70)

                # ------------------------------------------
                # IMPORTANT:
                # bad game does not stop the season
                # ------------------------------------------

                continue

            # ==================================================
            # 2. RUN ONTOLOGY BENCHMARK FOR CURRENT GAME
            # ==================================================

            try:

                print("\n")
                print("-" * 70)
                print(
                    f"BENCHMARK START | {game_id}"
                )
                print("-" * 70)

                # run_ontology_benchmark still expects
                # a games_data dictionary.
                #
                # We simply give it ONE game.

                current_game_data = {
                    game_id: game_data,
                }

                run_ontology_benchmark(
                    current_game_data,
                )

                print("\n")
                print(
                    f"BENCHMARK PASS | {game_id}"
                )

            except Exception as exc:

                benchmark_errors += 1

                print("\n")
                print("!" * 70)
                print(
                    f"BENCHMARK_ERROR"
                    f" | GAME={game_id}"
                    f" | {type(exc).__name__}"
                    f" | {exc}"
                )
                print("!" * 70)

                # ------------------------------------------
                # Benchmark failure does not stop season.
                # ------------------------------------------

            finally:

                # ==================================================
                # 3. DROP RDF TRIPLES + RELEASE GAME MEMORY
                # ==================================================

                if game_data is not None:

                    rdf_graph = game_data.get(
                        "rdf_graph"
                    )

                    if rdf_graph is not None:

                        triple_count = len(
                            rdf_graph
                        )

                        print(
                            f"\nDROP RDF GRAPH"
                            f" | GAME={game_id}"
                            f" | TRIPLES={triple_count}"
                        )

                        rdf_graph.remove(
                            (
                                None,
                                None,
                                None,
                            )
                        )

                        print(
                            f"RDF GRAPH CLEARED"
                            f" | REMAINING="
                            f"{len(rdf_graph)}"
                        )

                    # Remove references to potentially
                    # large game structures.

                    game_data.clear()

                    del game_data

                if "current_game_data" in locals():

                    current_game_data.clear()

                    del current_game_data

                import gc

                gc.collect()

                print(
                    f"\nGAME COMPLETE"
                    f" | {game_id}"
                )

        # ==================================================
        # FINAL SEASON SUMMARY
        # ==================================================

        print("\n")
        print("=" * 70)
        print("SEASON BENCHMARK COMPLETE")
        print("=" * 70)

        print(
            "TOTAL GAMES:",
            total_games,
        )

        print(
            "SUCCESSFUL INGESTIONS:",
            successful_games,
        )

        print(
            "INGESTION ERRORS:",
            ingestion_errors,
        )

        print(
            "BENCHMARK ERRORS:",
            benchmark_errors,
        )

        print("=" * 70)

    finally:

        ctx.close()


if __name__ == "__main__":
    main()