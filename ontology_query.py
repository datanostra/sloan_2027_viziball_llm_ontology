from dataclasses import dataclass
from enum import Enum
from typing import List, Optional
from rdflib import RDF, Namespace


class OntologyOperation(str, Enum):
    COUNT = "COUNT"
    RATIO = "RATIO"
    RANK = "RANK"


class OntologyEntity(str, Enum):
    PLAYER = "PLAYER"


class OntologyMetric(str, Enum):
    PTS = "PTS"


class OntologyOrder(str, Enum):
    ASC = "ASC"
    DESC = "DESC"


@dataclass
class OntologyQuery:

    concepts: List[str]

    operation: OntologyOperation

    denominator_concepts: Optional[
        List[str]
    ] = None

    # Used by ranking queries

    entity: Optional[
        OntologyEntity
    ] = None

    metric: Optional[
        OntologyMetric
    ] = None

    order: Optional[
        OntologyOrder
    ] = None

    limit: Optional[int] = None



VZ = Namespace(
    "https://viziball.io/ontology/"
)


def get_concept_instances(
    rdf_graph,
    concepts,
):
    """
    Return resources belonging to ALL requested
    ontology concepts.
    """

    if not concepts:
        return set()

    instance_sets = []

    for concept in concepts:

        instances = set(
            rdf_graph.subjects(
                RDF.type,
                VZ[concept],
            )
        )

        instance_sets.append(
            instances
        )

    return set.intersection(
        *instance_sets
    )


def execute_ontology_query(
    graph,
    query: OntologyQuery,
):

    # ==================================================
    # HELPER — INTERSECTION OF ONTOLOGY CONCEPTS
    # ==================================================

    def get_instances(concepts):

        if not concepts:
            return set()

        concept_sets = []

        for concept in concepts:

            concept_uri = VZ[
                concept
            ]

            instances = set(
                graph.subjects(
                    RDF.type,
                    concept_uri,
                )
            )

            concept_sets.append(
                instances
            )

        if not concept_sets:
            return set()

        return set.intersection(
            *concept_sets
        )

    # ==================================================
    # FILTER POSSESSIONS BY CONCEPTS
    # ==================================================

    numerator_instances = (
        get_instances(
            query.concepts
        )
    )

    # ==================================================
    # COUNT
    # ==================================================

    if (
        query.operation
        == OntologyOperation.COUNT
    ):

        return {
            "operation": "COUNT",
            "concepts": query.concepts,
            "count": len(
                numerator_instances
            ),
        }

    # ==================================================
    # RATIO
    # ==================================================

    if (
        query.operation
        == OntologyOperation.RATIO
    ):

        if not query.denominator_concepts:

            raise ValueError(
                "RATIO requires "
                "denominator_concepts"
            )

        denominator_instances = (
            get_instances(
                query.denominator_concepts
            )
        )

        numerator = len(
            numerator_instances
        )

        denominator = len(
            denominator_instances
        )

        ratio = (
            numerator / denominator
            if denominator > 0
            else None
        )

        return {
            "operation": "RATIO",
            "concepts": query.concepts,
            "denominator_concepts":
                query.denominator_concepts,
            "numerator": numerator,
            "denominator": denominator,
            "ratio": ratio,
        }

    # ==================================================
    # RANK
    #
    # First supported analytical ranking:
    #
    # entity = PLAYER
    # metric = PTS
    #
    # Example:
    # "Who was the most clutch player?"
    #
    # Definition:
    # player scoring the most points in possessions
    # matching the requested ontology concepts.
    # ==================================================

    if (
        query.operation
        == OntologyOperation.RANK
    ):

        if (
            query.entity
            != OntologyEntity.PLAYER
        ):
            raise ValueError(
                "RANK currently supports "
                "entity=PLAYER only"
            )

        if (
            query.metric
            != OntologyMetric.PTS
        ):
            raise ValueError(
                "RANK currently supports "
                "metric=PTS only"
            )

        # ----------------------------------------------
        # PLAYER -> POINTS
        # ----------------------------------------------

        player_points = {}

        for possession in numerator_instances:

            events = graph.objects(
                possession,
                VZ.hasEvent,
            )

            for event in events:

                event_type = graph.value(
                    event,
                    VZ.eventType,
                )

                if event_type is None:
                    continue

                event_type = str(
                    event_type
                )

                # --------------------------------------
                # POINT VALUE
                # --------------------------------------

                if event_type == "TWO_PT_MADE":

                    points = 2

                elif event_type == "THREE_PT_MADE":

                    points = 3

                elif event_type == "FT_MADE":

                    points = 1

                else:

                    continue

                # --------------------------------------
                # SHOOTER
                # --------------------------------------

                player = graph.value(
                    event,
                    VZ.shooter,
                )

                if player is None:
                    continue

                player_points[player] = (
                    player_points.get(
                        player,
                        0,
                    )
                    + points
                )

        # ----------------------------------------------
        # RANK
        # ----------------------------------------------

        reverse = (
            query.order
            != OntologyOrder.ASC
        )

        ranking = sorted(
            player_points.items(),
            key=lambda item: item[1],
            reverse=reverse,
        )

        if query.limit is not None:

            ranking = ranking[
                :query.limit
            ]

        # ----------------------------------------------
        # SERIALIZABLE RESULT
        # ----------------------------------------------

        ranking_result = [
            {
                "player": str(player),
                "value": points,
            }
            for player, points in ranking
        ]

        return {
            "operation": "RANK",
            "concepts": query.concepts,
            "entity": "PLAYER",
            "metric": "PTS",
            "order": (
                query.order.value
                if query.order is not None
                else "DESC"
            ),
            "limit": query.limit,
            "ranking": ranking_result,
        }

    # ==================================================
    # UNSUPPORTED OPERATION
    # ==================================================

    raise ValueError(
        f"Unsupported ontology operation: "
        f"{query.operation}"
    )