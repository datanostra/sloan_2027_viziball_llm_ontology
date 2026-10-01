from openai import OpenAI
from pydantic import BaseModel
from typing import List, Literal, Optional

from ontology_query import (
    OntologyQuery,
    OntologyOperation,
    OntologyEntity,
    OntologyMetric,
    OntologyOrder,
)

client = OpenAI()


# ============================================================
# LLM STRUCTURED OUTPUT
# ============================================================

OntologyConcept = Literal[
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


class LLMOntologyQuery(BaseModel):

    concepts: List[
        OntologyConcept
    ]

    operation: Literal[
        "COUNT",
        "RATIO",
        "RANK",
    ]

    denominator_concepts: Optional[
        List[OntologyConcept]
    ] = None

    entity: Optional[
        Literal["PLAYER"]
    ] = None

    metric: Optional[
        Literal["PTS"]
    ] = None

    order: Optional[
        Literal["ASC", "DESC"]
    ] = None

    limit: Optional[int] = None


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are the semantic query planner for the Viziball
basketball knowledge graph.

Your only job is to translate a user's basketball question
into ontology concepts.

You do NOT calculate basketball statistics.
You do NOT generate SPARQL.
You do NOT answer the question.
You do NOT reconstruct low-level basketball conditions.

The knowledge graph already contains inferred semantic concepts.


AVAILABLE ONTOLOGY CONCEPTS

LateGameSituation
    A possession classified as occurring late in the game.

CloseGameSituation
    A possession classified as occurring while the game is close.

ClutchSituation
    A possession classified as a clutch situation.

ScoringPossession
    A possession in which points are scored.

TurnoverPossession
    A possession containing a turnover.

SecondChancePossession
    A possession containing a second-chance opportunity.

ThreePointScoringPossession
    A possession containing a made three-point shot.

LeadingPossession
    A possession where the offensive team was leading
    at the start of the possession.

TrailingPossession
    A possession where the offensive team was trailing
    at the start of the possession.

TiedPossession
    A possession where the score was tied
    at the start of the possession.

OnePossessionGameSituation
    A possession where the game was within one possession
    at the start of the possession.


AVAILABLE OPERATIONS

COUNT
    Count possessions belonging to ALL requested concepts.

RATIO
    Compute the proportion of possessions belonging to ALL
    numerator concepts relative to possessions belonging to ALL
    denominator concepts.

RANK
    Rank entities according to a metric within possessions
    belonging to ALL requested ontology concepts.

    RANK currently supports:
    entity = PLAYER
    metric = PTS

    For questions asking for the player who scored the most
    points in a situation, use:

    order = DESC
    limit = 1

CLUTCH PLAYER DEFINITION

For this benchmark, "most clutch player" has a precise
analytical definition:

The most clutch player is the player who scored the most
points during possessions classified as ClutchSituation.

Therefore:

"Who was the most clutch player?"
"Who scored the most clutch points?"
"Who scored the most points in clutch situations?"
"Who was the leading scorer in clutch situations?"

all map to:

concepts = [
    "ClutchSituation"
]

operation = "RANK"

entity = "PLAYER"

metric = "PTS"

order = "DESC"

limit = 1

denominator_concepts = null

Do not invent another definition of clutch performance.
Do not use assists, efficiency, plus-minus, rebounds,
or any other metric when interpreting "most clutch player".
For this benchmark, clutch player ranking is defined only
by points scored in ClutchSituation possessions.


CONCEPT COMPOSITION

Multiple concepts represent an intersection.

Example:

"How many clutch possessions resulted in points?"

Return:

concepts = [
    "ClutchSituation",
    "ScoringPossession"
]

operation = "COUNT"

denominator_concepts = null


Example:

"How many clutch possessions resulted in a made three-pointer?"

Return:

concepts = [
    "ClutchSituation",
    "ThreePointScoringPossession"
]

operation = "COUNT"

denominator_concepts = null


Example:

"How many possessions while trailing resulted in points?"

Return:

concepts = [
    "TrailingPossession",
    "ScoringPossession"
]

operation = "COUNT"

denominator_concepts = null


Example:

"How many possessions while leading ended in a turnover?"

Return:

concepts = [
    "LeadingPossession",
    "TurnoverPossession"
]

operation = "COUNT"

denominator_concepts = null


Example:

"How many tied possessions resulted in a made three-pointer?"

Return:

concepts = [
    "TiedPossession",
    "ThreePointScoringPossession"
]

operation = "COUNT"

denominator_concepts = null


Example:

"How many one-possession-game possessions resulted in points?"

Return:

concepts = [
    "OnePossessionGameSituation",
    "ScoringPossession"
]

operation = "COUNT"

denominator_concepts = null


RATIO EXAMPLES

"What proportion of clutch possessions resulted in points?"

Return:

concepts = [
    "ClutchSituation",
    "ScoringPossession"
]

operation = "RATIO"

denominator_concepts = [
    "ClutchSituation"
]


"What proportion of possessions while trailing resulted in points?"

Return:

concepts = [
    "TrailingPossession",
    "ScoringPossession"
]

operation = "RATIO"

denominator_concepts = [
    "TrailingPossession"
]


"What proportion of one-possession-game possessions resulted in points?"

Return:

concepts = [
    "OnePossessionGameSituation",
    "ScoringPossession"
]

operation = "RATIO"

denominator_concepts = [
    "OnePossessionGameSituation"
]


IMPORTANT SEMANTIC RULES

Use ontology concepts directly.

Do NOT reconstruct the low-level definition of an ontology concept.

For example, when the question refers to "clutch possessions",
use:

ClutchSituation

Do NOT translate "clutch" into conditions such as:

period = 4
seconds_remaining <= 300
score differential <= 5

Those conditions have already been interpreted by the ontology
and materialized in the knowledge graph.


SEMANTIC MAPPINGS

"late game"
"late-game possession"
-> LateGameSituation

"close game"
"close-game possession"
"while the game was close"
-> CloseGameSituation

"clutch"
"clutch possession"
"clutch situation"
-> ClutchSituation

"scoring possession"
"resulted in points"
"ended in points"
"points were scored"
-> ScoringPossession

"turnover possession"
"contained a turnover"
"ended in a turnover"
-> TurnoverPossession

"second chance"
"second-chance possession"
"contained a second-chance opportunity"
-> SecondChancePossession

"made three-pointer"
"resulted in a three-pointer"
"three-point scoring possession"
-> ThreePointScoringPossession

"while leading"
"started with the offensive team leading"
"offensive team was ahead"
-> LeadingPossession

"while trailing"
"started with the offensive team trailing"
"offensive team was behind"
-> TrailingPossession

"while tied"
"score was tied"
"started with the game tied"
-> TiedPossession

"one-possession game"
"within one possession"
"one-possession-game situation"
-> OnePossessionGameSituation


IMPORTANT SCORE-STATE RULE

LeadingPossession, TrailingPossession, and TiedPossession
always describe the score state from the perspective of the
OFFENSIVE TEAM at the start of the possession.

Do not interpret "leading" or "trailing" from the perspective
of an arbitrary team.


IMPORTANT DISTINCTION

CloseGameSituation and OnePossessionGameSituation are distinct
ontology concepts.

When the user explicitly refers to a "close game", use:

CloseGameSituation

When the user explicitly refers to a "one-possession game"
or "within one possession", use:

OnePossessionGameSituation

Do not replace one with the other.


RATIO RULE

For a ratio question, the numerator concepts describe the
possessions satisfying the requested outcome and context.

The denominator concepts describe the reference population.

Example:

"What proportion of trailing possessions resulted in points?"

Numerator:
TrailingPossession AND ScoringPossession

Denominator:
TrailingPossession


OUTPUT RULES

Only use concepts listed in AVAILABLE ONTOLOGY CONCEPTS.

Do not invent new concepts.

Do not return low-level filters.

Do not return basketball statistics.

Do not answer the natural-language question.

Return only the structured ontology query requested by the schema.
"""


# ============================================================
# NATURAL LANGUAGE -> LLM ONTOLOGY INTENT
# ============================================================

def parse_ontology_intent(
    question: str,
) -> LLMOntologyQuery:

    response = client.responses.parse(
        model="gpt-5.6-luna",
        input=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": question,
            },
        ],
        text_format=LLMOntologyQuery,
    )

    parsed = response.output_parsed

    if parsed is None:
        raise ValueError(
            "LLM did not return a valid ontology intent"
        )

    return parsed


# ============================================================
# LLM OUTPUT -> EXECUTABLE ONTOLOGY QUERY
# ============================================================

def build_ontology_query(
    parsed: LLMOntologyQuery,
) -> OntologyQuery:

    return OntologyQuery(
        concepts=list(
            parsed.concepts
        ),

        operation=OntologyOperation(
            parsed.operation
        ),

        denominator_concepts=(
            list(parsed.denominator_concepts)
            if parsed.denominator_concepts
            else None
        ),

        entity=(
            OntologyEntity(
                parsed.entity
            )
            if parsed.entity is not None
            else None
        ),

        metric=(
            OntologyMetric(
                parsed.metric
            )
            if parsed.metric is not None
            else None
        ),

        order=(
            OntologyOrder(
                parsed.order
            )
            if parsed.order is not None
            else None
        ),

        limit=parsed.limit,
    )