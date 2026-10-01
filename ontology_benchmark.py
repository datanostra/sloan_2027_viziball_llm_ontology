from ontology_ground_truth import (
    build_ontology_ground_truth,
    execute_ground_truth_query,
)

from ontology_query import (
    OntologyQuery,
    OntologyOperation,
    OntologyEntity,
    OntologyMetric,
    OntologyOrder,
)

ONTOLOGY_BENCHMARK = [

    # ==================================================
    # BASELINE — DIRECT ONTOLOGY QUESTIONS
    # ==================================================

    {
        "id": "ONT_001",
        "question": "How many clutch possessions occurred in the game?",
        "expected_query": {
            "concepts": ["ClutchSituation"],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_002",
        "question": "How many close-game possessions occurred?",
        "expected_query": {
            "concepts": ["CloseGameSituation"],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_003",
        "question": "How many late-game possessions occurred?",
        "expected_query": {
            "concepts": ["LateGameSituation"],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_004",
        "question": "How many scoring possessions occurred?",
        "expected_query": {
            "concepts": ["ScoringPossession"],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_005",
        "question": "How many turnover possessions occurred?",
        "expected_query": {
            "concepts": ["TurnoverPossession"],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_006",
        "question": "How many second-chance possessions occurred?",
        "expected_query": {
            "concepts": ["SecondChancePossession"],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_007",
        "question": "How many possessions resulted in a made three-pointer?",
        "expected_query": {
            "concepts": ["ThreePointScoringPossession"],
            "operation": "COUNT",
        },
    },

    # ==================================================
    # BASELINE — TWO-CONCEPT COMPOSITION
    # ==================================================

    {
        "id": "ONT_008",
        "question": "How many clutch possessions resulted in points?",
        "expected_query": {
            "concepts": [
                "ClutchSituation",
                "ScoringPossession",
            ],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_009",
        "question": "How many clutch possessions resulted in a made three-pointer?",
        "expected_query": {
            "concepts": [
                "ClutchSituation",
                "ThreePointScoringPossession",
            ],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_010",
        "question": "How many clutch possessions contained a turnover?",
        "expected_query": {
            "concepts": [
                "ClutchSituation",
                "TurnoverPossession",
            ],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_011",
        "question": "How many close-game possessions resulted in points?",
        "expected_query": {
            "concepts": [
                "CloseGameSituation",
                "ScoringPossession",
            ],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_012",
        "question": "How many close-game possessions contained a turnover?",
        "expected_query": {
            "concepts": [
                "CloseGameSituation",
                "TurnoverPossession",
            ],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_013",
        "question": "How many late-game possessions were second-chance possessions?",
        "expected_query": {
            "concepts": [
                "LateGameSituation",
                "SecondChancePossession",
            ],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_014",
        "question": "How many late-game possessions resulted in a made three-pointer?",
        "expected_query": {
            "concepts": [
                "LateGameSituation",
                "ThreePointScoringPossession",
            ],
            "operation": "COUNT",
        },
    },

    # ==================================================
    # BASELINE — RATIO
    # ==================================================

    {
        "id": "ONT_015",
        "question": "What proportion of clutch possessions resulted in points?",
        "expected_query": {
            "concepts": [
                "ClutchSituation",
                "ScoringPossession",
            ],
            "operation": "RATIO",
            "denominator_concepts": [
                "ClutchSituation",
            ],
        },
    },

    # ==================================================
    # SCORE-STATE CONCEPTS
    # ==================================================

    {
        "id": "ONT_016",
        "question": (
            "How many possessions started with "
            "the offensive team leading?"
        ),
        "expected_query": {
            "concepts": [
                "LeadingPossession",
            ],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_017",
        "question": (
            "How many possessions started with "
            "the offensive team trailing?"
        ),
        "expected_query": {
            "concepts": [
                "TrailingPossession",
            ],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_018",
        "question": (
            "How many possessions started "
            "with the score tied?"
        ),
        "expected_query": {
            "concepts": [
                "TiedPossession",
            ],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_019",
        "question": (
            "How many possessions occurred "
            "in a one-possession game situation?"
        ),
        "expected_query": {
            "concepts": [
                "OnePossessionGameSituation",
            ],
            "operation": "COUNT",
        },
    },

    # ==================================================
    # SCORE STATE + EVENT COMPOSITION
    # ==================================================

    {
        "id": "ONT_020",
        "question": (
            "How many possessions while trailing "
            "resulted in points?"
        ),
        "expected_query": {
            "concepts": [
                "TrailingPossession",
                "ScoringPossession",
            ],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_021",
        "question": (
            "How many possessions while leading "
            "ended in a turnover?"
        ),
        "expected_query": {
            "concepts": [
                "LeadingPossession",
                "TurnoverPossession",
            ],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_022",
        "question": (
            "How many tied possessions resulted "
            "in a made three-pointer?"
        ),
        "expected_query": {
            "concepts": [
                "TiedPossession",
                "ThreePointScoringPossession",
            ],
            "operation": "COUNT",
        },
    },
    # ==================================================
    # LINGUISTIC VARIATIONS — SINGLE CONCEPT
    # ==================================================
    {
        "id": "ONT_023",
        "question": (
            "How many one-possession-game possessions "
            "resulted in points?"
        ),
        "expected_query": {
            "concepts": [
                "OnePossessionGameSituation",
                "ScoringPossession",
            ],
            "operation": "COUNT",
        },
    },

    # ==================================================
    # SCORE-STATE RATIOS
    # ==================================================

    {
        "id": "ONT_024",
        "question": (
            "What proportion of possessions while "
            "trailing resulted in points?"
        ),
        "expected_query": {
            "concepts": [
                "TrailingPossession",
                "ScoringPossession",
            ],
            "operation": "RATIO",
            "denominator_concepts": [
                "TrailingPossession",
            ],
        },
    },

    {
        "id": "ONT_025",
        "question": (
            "What proportion of one-possession-game "
            "possessions resulted in points?"
        ),
        "expected_query": {
            "concepts": [
                "OnePossessionGameSituation",
                "ScoringPossession",
            ],
            "operation": "RATIO",
            "denominator_concepts": [
                "OnePossessionGameSituation",
            ],
        },
    },

    # ==================================================
    # BASELINE ENTITY RANKING
    # ==================================================

    {
        "id": "ONT_026",
        "question": "Who was the most clutch player?",
        "expected_query": {
            "concepts": [
                "ClutchSituation",
            ],
            "operation": "RANK",
            "entity": "PLAYER",
            "metric": "PTS",
            "order": "DESC",
            "limit": 1,
        },
    },
    {
        "id": "ONT_027",
        "question": "How many times did the game enter a clutch possession?",
        "expected_query": {
            "concepts": ["ClutchSituation"],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_028",
        "question": "Count the possessions played late in the game.",
        "expected_query": {
            "concepts": ["LateGameSituation"],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_029",
        "question": "How many possessions took place while the game was close?",
        "expected_query": {
            "concepts": ["CloseGameSituation"],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_030",
        "question": "On how many possessions did either team put points on the board?",
        "expected_query": {
            "concepts": ["ScoringPossession"],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_031",
        "question": "How many possessions featured a giveaway?",
        "expected_query": {
            "concepts": ["TurnoverPossession"],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_032",
        "question": "How many possessions included an offensive rebound and another opportunity?",
        "expected_query": {
            "concepts": ["SecondChancePossession"],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_033",
        "question": "How many possessions produced a successful shot from beyond the arc?",
        "expected_query": {
            "concepts": ["ThreePointScoringPossession"],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_034",
        "question": "How often did the offense begin a possession ahead on the scoreboard?",
        "expected_query": {
            "concepts": ["LeadingPossession"],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_035",
        "question": "How often did the offense start a possession from behind?",
        "expected_query": {
            "concepts": ["TrailingPossession"],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_036",
        "question": "How many possessions began with neither team ahead?",
        "expected_query": {
            "concepts": ["TiedPossession"],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_037",
        "question": "How many possessions began with the teams separated by no more than one possession?",
        "expected_query": {
            "concepts": ["OnePossessionGameSituation"],
            "operation": "COUNT",
        },
    },

    # ==================================================
    # TWO-CONCEPT COMPOSITION
    # ==================================================

    {
        "id": "ONT_038",
        "question": "How many late-game possessions resulted in points?",
        "expected_query": {
            "concepts": [
                "LateGameSituation",
                "ScoringPossession",
            ],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_039",
        "question": "How many late-game possessions contained a turnover?",
        "expected_query": {
            "concepts": [
                "LateGameSituation",
                "TurnoverPossession",
            ],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_040",
        "question": "How many close-game possessions produced a made three-pointer?",
        "expected_query": {
            "concepts": [
                "CloseGameSituation",
                "ThreePointScoringPossession",
            ],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_041",
        "question": "How many close-game possessions were second-chance possessions?",
        "expected_query": {
            "concepts": [
                "CloseGameSituation",
                "SecondChancePossession",
            ],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_042",
        "question": "How many clutch possessions included a second chance?",
        "expected_query": {
            "concepts": [
                "ClutchSituation",
                "SecondChancePossession",
            ],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_043",
        "question": "How many possessions starting from behind ended with a turnover?",
        "expected_query": {
            "concepts": [
                "TrailingPossession",
                "TurnoverPossession",
            ],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_044",
        "question": "How many possessions starting from behind produced a made three?",
        "expected_query": {
            "concepts": [
                "TrailingPossession",
                "ThreePointScoringPossession",
            ],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_045",
        "question": "How many possessions starting with the offense ahead resulted in points?",
        "expected_query": {
            "concepts": [
                "LeadingPossession",
                "ScoringPossession",
            ],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_046",
        "question": "How many possessions starting with the offense ahead produced a made three?",
        "expected_query": {
            "concepts": [
                "LeadingPossession",
                "ThreePointScoringPossession",
            ],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_047",
        "question": "How many tied possessions resulted in points?",
        "expected_query": {
            "concepts": [
                "TiedPossession",
                "ScoringPossession",
            ],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_048",
        "question": "How many tied possessions contained a turnover?",
        "expected_query": {
            "concepts": [
                "TiedPossession",
                "TurnoverPossession",
            ],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_049",
        "question": "How many one-possession-game possessions ended in a turnover?",
        "expected_query": {
            "concepts": [
                "OnePossessionGameSituation",
                "TurnoverPossession",
            ],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_050",
        "question": "How many one-possession-game possessions produced a made three?",
        "expected_query": {
            "concepts": [
                "OnePossessionGameSituation",
                "ThreePointScoringPossession",
            ],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_051",
        "question": "How many one-possession-game possessions included a second chance?",
        "expected_query": {
            "concepts": [
                "OnePossessionGameSituation",
                "SecondChancePossession",
            ],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_052",
        "question": "How many late-game possessions began with the offense trailing?",
        "expected_query": {
            "concepts": [
                "LateGameSituation",
                "TrailingPossession",
            ],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_053",
        "question": "How many late-game possessions began with the offense leading?",
        "expected_query": {
            "concepts": [
                "LateGameSituation",
                "LeadingPossession",
            ],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_054",
        "question": "How many late-game possessions began with the score tied?",
        "expected_query": {
            "concepts": [
                "LateGameSituation",
                "TiedPossession",
            ],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_055",
        "question": "How many close-game possessions began with the offense trailing?",
        "expected_query": {
            "concepts": [
                "CloseGameSituation",
                "TrailingPossession",
            ],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_056",
        "question": "How many close-game possessions began with the offense leading?",
        "expected_query": {
            "concepts": [
                "CloseGameSituation",
                "LeadingPossession",
            ],
            "operation": "COUNT",
        },
    },

    # ==================================================
    # IMPLICIT / NATURAL LANGUAGE COMPOSITION
    # ==================================================

    {
        "id": "ONT_057",
        "question": "How often did a team score during clutch possessions?",
        "expected_query": {
            "concepts": [
                "ClutchSituation",
                "ScoringPossession",
            ],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_058",
        "question": "How many times was the ball turned over in the clutch?",
        "expected_query": {
            "concepts": [
                "ClutchSituation",
                "TurnoverPossession",
            ],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_059",
        "question": "How many possessions produced points when the offense began behind?",
        "expected_query": {
            "concepts": [
                "TrailingPossession",
                "ScoringPossession",
            ],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_060",
        "question": "How often did the offense give the ball away after starting the possession ahead?",
        "expected_query": {
            "concepts": [
                "LeadingPossession",
                "TurnoverPossession",
            ],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_061",
        "question": "How often did teams score when the margin was within one possession?",
        "expected_query": {
            "concepts": [
                "OnePossessionGameSituation",
                "ScoringPossession",
            ],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_062",
        "question": "How many threes were made on possessions that began with neither side ahead?",
        "expected_query": {
            "concepts": [
                "TiedPossession",
                "ThreePointScoringPossession",
            ],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_063",
        "question": "How many scoring possessions happened with the game still tight?",
        "expected_query": {
            "concepts": [
                "CloseGameSituation",
                "ScoringPossession",
            ],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_064",
        "question": "How many giveaways happened while the game was still close?",
        "expected_query": {
            "concepts": [
                "CloseGameSituation",
                "TurnoverPossession",
            ],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_065",
        "question": "How many possessions produced a three late in the game?",
        "expected_query": {
            "concepts": [
                "LateGameSituation",
                "ThreePointScoringPossession",
            ],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_066",
        "question": "How many second opportunities occurred late in the game?",
        "expected_query": {
            "concepts": [
                "LateGameSituation",
                "SecondChancePossession",
            ],
            "operation": "COUNT",
        },
    },

    # ==================================================
    # THREE-CONCEPT COMPOSITION
    # ==================================================

    {
        "id": "ONT_067",
        "question": "How many late-game possessions while trailing resulted in points?",
        "expected_query": {
            "concepts": [
                "LateGameSituation",
                "TrailingPossession",
                "ScoringPossession",
            ],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_068",
        "question": "How many late-game possessions while leading resulted in points?",
        "expected_query": {
            "concepts": [
                "LateGameSituation",
                "LeadingPossession",
                "ScoringPossession",
            ],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_069",
        "question": "How many late-game possessions while trailing ended in a turnover?",
        "expected_query": {
            "concepts": [
                "LateGameSituation",
                "TrailingPossession",
                "TurnoverPossession",
            ],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_070",
        "question": "How many late-game possessions while leading ended in a turnover?",
        "expected_query": {
            "concepts": [
                "LateGameSituation",
                "LeadingPossession",
                "TurnoverPossession",
            ],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_071",
        "question": "How many close-game possessions while trailing resulted in points?",
        "expected_query": {
            "concepts": [
                "CloseGameSituation",
                "TrailingPossession",
                "ScoringPossession",
            ],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_072",
        "question": "How many close-game possessions while leading resulted in points?",
        "expected_query": {
            "concepts": [
                "CloseGameSituation",
                "LeadingPossession",
                "ScoringPossession",
            ],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_073",
        "question": "How many close-game possessions while trailing contained a turnover?",
        "expected_query": {
            "concepts": [
                "CloseGameSituation",
                "TrailingPossession",
                "TurnoverPossession",
            ],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_074",
        "question": "How many one-possession-game possessions while trailing resulted in points?",
        "expected_query": {
            "concepts": [
                "OnePossessionGameSituation",
                "TrailingPossession",
                "ScoringPossession",
            ],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_075",
        "question": "How many one-possession-game possessions while leading resulted in points?",
        "expected_query": {
            "concepts": [
                "OnePossessionGameSituation",
                "LeadingPossession",
                "ScoringPossession",
            ],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_076",
        "question": "How many one-possession-game possessions while trailing ended in a turnover?",
        "expected_query": {
            "concepts": [
                "OnePossessionGameSituation",
                "TrailingPossession",
                "TurnoverPossession",
            ],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_077",
        "question": "How many clutch possessions while trailing resulted in points?",
        "expected_query": {
            "concepts": [
                "ClutchSituation",
                "TrailingPossession",
                "ScoringPossession",
            ],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_078",
        "question": "How many clutch possessions while leading resulted in points?",
        "expected_query": {
            "concepts": [
                "ClutchSituation",
                "LeadingPossession",
                "ScoringPossession",
            ],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_079",
        "question": "How many clutch possessions while trailing produced a made three?",
        "expected_query": {
            "concepts": [
                "ClutchSituation",
                "TrailingPossession",
                "ThreePointScoringPossession",
            ],
            "operation": "COUNT",
        },
    },

    {
        "id": "ONT_080",
        "question": "How many close-game second-chance possessions resulted in points?",
        "expected_query": {
            "concepts": [
                "CloseGameSituation",
                "SecondChancePossession",
                "ScoringPossession",
            ],
            "operation": "COUNT",
        },
    },

    # ==================================================
    # RATIOS — DIRECT + PARAPHRASED
    # ==================================================

    {
        "id": "ONT_081",
        "question": "What proportion of late-game possessions resulted in points?",
        "expected_query": {
            "concepts": [
                "LateGameSituation",
                "ScoringPossession",
            ],
            "operation": "RATIO",
            "denominator_concepts": [
                "LateGameSituation",
            ],
        },
    },

    {
        "id": "ONT_082",
        "question": "What proportion of close-game possessions resulted in points?",
        "expected_query": {
            "concepts": [
                "CloseGameSituation",
                "ScoringPossession",
            ],
            "operation": "RATIO",
            "denominator_concepts": [
                "CloseGameSituation",
            ],
        },
    },

    {
        "id": "ONT_083",
        "question": "What fraction of clutch possessions ended in a turnover?",
        "expected_query": {
            "concepts": [
                "ClutchSituation",
                "TurnoverPossession",
            ],
            "operation": "RATIO",
            "denominator_concepts": [
                "ClutchSituation",
            ],
        },
    },

    {
        "id": "ONT_084",
        "question": "What share of clutch possessions produced a made three?",
        "expected_query": {
            "concepts": [
                "ClutchSituation",
                "ThreePointScoringPossession",
            ],
            "operation": "RATIO",
            "denominator_concepts": [
                "ClutchSituation",
            ],
        },
    },

    {
        "id": "ONT_085",
        "question": "What percentage of possessions starting from behind resulted in points?",
        "expected_query": {
            "concepts": [
                "TrailingPossession",
                "ScoringPossession",
            ],
            "operation": "RATIO",
            "denominator_concepts": [
                "TrailingPossession",
            ],
        },
    },

    {
        "id": "ONT_086",
        "question": "What proportion of possessions starting with the offense ahead resulted in points?",
        "expected_query": {
            "concepts": [
                "LeadingPossession",
                "ScoringPossession",
            ],
            "operation": "RATIO",
            "denominator_concepts": [
                "LeadingPossession",
            ],
        },
    },

    {
        "id": "ONT_087",
        "question": "Among possessions that began tied, what proportion resulted in points?",
        "expected_query": {
            "concepts": [
                "TiedPossession",
                "ScoringPossession",
            ],
            "operation": "RATIO",
            "denominator_concepts": [
                "TiedPossession",
            ],
        },
    },

    {
        "id": "ONT_088",
        "question": "Of possessions beginning with the offense ahead, what fraction ended in a turnover?",
        "expected_query": {
            "concepts": [
                "LeadingPossession",
                "TurnoverPossession",
            ],
            "operation": "RATIO",
            "denominator_concepts": [
                "LeadingPossession",
            ],
        },
    },

    {
        "id": "ONT_089",
        "question": "Among possessions starting from behind, what share produced a made three?",
        "expected_query": {
            "concepts": [
                "TrailingPossession",
                "ThreePointScoringPossession",
            ],
            "operation": "RATIO",
            "denominator_concepts": [
                "TrailingPossession",
            ],
        },
    },

    {
        "id": "ONT_090",
        "question": "What fraction of close-game possessions ended in a turnover?",
        "expected_query": {
            "concepts": [
                "CloseGameSituation",
                "TurnoverPossession",
            ],
            "operation": "RATIO",
            "denominator_concepts": [
                "CloseGameSituation",
            ],
        },
    },

    {
        "id": "ONT_091",
        "question": "What share of late-game possessions produced a made three?",
        "expected_query": {
            "concepts": [
                "LateGameSituation",
                "ThreePointScoringPossession",
            ],
            "operation": "RATIO",
            "denominator_concepts": [
                "LateGameSituation",
            ],
        },
    },

    {
        "id": "ONT_092",
        "question": "How often did teams score when the game was within one possession?",
        "expected_query": {
            "concepts": [
                "OnePossessionGameSituation",
                "ScoringPossession",
            ],
            "operation": "RATIO",
            "denominator_concepts": [
                "OnePossessionGameSituation",
            ],
        },
    },

    {
        "id": "ONT_093",
        "question": "What proportion of one-possession-game possessions ended in a turnover?",
        "expected_query": {
            "concepts": [
                "OnePossessionGameSituation",
                "TurnoverPossession",
            ],
            "operation": "RATIO",
            "denominator_concepts": [
                "OnePossessionGameSituation",
            ],
        },
    },

    {
        "id": "ONT_094",
        "question": "Among late-game possessions while trailing, what proportion resulted in points?",
        "expected_query": {
            "concepts": [
                "LateGameSituation",
                "TrailingPossession",
                "ScoringPossession",
            ],
            "operation": "RATIO",
            "denominator_concepts": [
                "LateGameSituation",
                "TrailingPossession",
            ],
        },
    },

    {
        "id": "ONT_095",
        "question": "Among close-game possessions while leading, what proportion resulted in points?",
        "expected_query": {
            "concepts": [
                "CloseGameSituation",
                "LeadingPossession",
                "ScoringPossession",
            ],
            "operation": "RATIO",
            "denominator_concepts": [
                "CloseGameSituation",
                "LeadingPossession",
            ],
        },
    },

    # ==================================================
    # ENTITY RANKING — LINGUISTIC ROBUSTNESS
    #
    # Same analytical definition:
    # most clutch = most PTS in ClutchSituation
    # ==================================================

    {
        "id": "ONT_096",
        "question": "Who scored the most clutch points?",
        "expected_query": {
            "concepts": ["ClutchSituation"],
            "operation": "RANK",
            "entity": "PLAYER",
            "metric": "PTS",
            "order": "DESC",
            "limit": 1,
        },
    },

    {
        "id": "ONT_097",
        "question": "Which player scored the most during clutch situations?",
        "expected_query": {
            "concepts": ["ClutchSituation"],
            "operation": "RANK",
            "entity": "PLAYER",
            "metric": "PTS",
            "order": "DESC",
            "limit": 1,
        },
    },

    {
        "id": "ONT_098",
        "question": "Who was the leading scorer in the clutch?",
        "expected_query": {
            "concepts": ["ClutchSituation"],
            "operation": "RANK",
            "entity": "PLAYER",
            "metric": "PTS",
            "order": "DESC",
            "limit": 1,
        },
    },

    {
        "id": "ONT_099",
        "question": "Which player put up the most points in clutch possessions?",
        "expected_query": {
            "concepts": ["ClutchSituation"],
            "operation": "RANK",
            "entity": "PLAYER",
            "metric": "PTS",
            "order": "DESC",
            "limit": 1,
        },
    },

    {
        "id": "ONT_100",
        "question": "Who led all players in scoring when the game was in a clutch situation?",
        "expected_query": {
            "concepts": ["ClutchSituation"],
            "operation": "RANK",
            "entity": "PLAYER",
            "metric": "PTS",
            "order": "DESC",
            "limit": 1,
        },
    },
]

from ontology_query import (
    OntologyQuery,
    OntologyOperation,
    execute_ontology_query,
)

from ontology_parser import (
    parse_ontology_intent,
    build_ontology_query,
)


def _normalize_query(query):

    return {
        "concepts": sorted(
            query["concepts"]
        ),

        "operation": query[
            "operation"
        ],

        "denominator_concepts": sorted(
            query.get(
                "denominator_concepts"
            )
            or []
        ),

        "entity": query.get(
            "entity"
        ),

        "metric": query.get(
            "metric"
        ),

        "order": query.get(
            "order"
        ),

        "limit": query.get(
            "limit"
        ),
    }


def _ontology_query_to_dict(
    query,
):

    return {
        "concepts": list(
            query.concepts
        ),

        "operation": (
            query.operation.value
        ),

        "denominator_concepts": (
            list(
                query.denominator_concepts
            )
            if query.denominator_concepts
            else None
        ),

        "entity": (
            query.entity.value
            if query.entity is not None
            else None
        ),

        "metric": (
            query.metric.value
            if query.metric is not None
            else None
        ),

        "order": (
            query.order.value
            if query.order is not None
            else None
        ),

        "limit": query.limit,
    }

def _benchmark_output_paths():

    from pathlib import Path

    output_dir = Path(
        "poc_llm/benchmark_results"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    return (
        output_dir
        / "ontology_benchmark_results.csv",
        output_dir
        / "ontology_benchmark_results.jsonl",
    )


def append_benchmark_result(row):

    import csv
    import json
    import os

    csv_path, jsonl_path = (
        _benchmark_output_paths()
    )

    # ==================================================
    # CSV
    # ==================================================

    csv_exists = (
        csv_path.exists()
        and csv_path.stat().st_size > 0
    )

    csv_row = dict(row)

    for key, value in csv_row.items():

        if isinstance(
            value,
            (list, dict),
        ):

            csv_row[key] = json.dumps(
                value,
                ensure_ascii=False,
            )

    with open(
        csv_path,
        "a",
        newline="",
        encoding="utf-8",
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=list(
                row.keys()
            ),
        )

        if not csv_exists:
            writer.writeheader()

        writer.writerow(
            csv_row
        )

        f.flush()
        os.fsync(
            f.fileno()
        )

    # ==================================================
    # JSONL
    # ==================================================

    with open(
        jsonl_path,
        "a",
        encoding="utf-8",
    ) as f:

        f.write(
            json.dumps(
                row,
                ensure_ascii=False,
                default=str,
            )
            + "\n"
        )

        f.flush()
        os.fsync(
            f.fileno()
        )


def load_completed_benchmark_items():

    import csv

    csv_path, _ = (
        _benchmark_output_paths()
    )

    completed = set()

    if not csv_path.exists():
        return completed

    with open(
        csv_path,
        "r",
        encoding="utf-8",
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:

            game_id = row.get(
                "game_id"
            )

            question_id = row.get(
                "question_id"
            )

            if (
                game_id
                and question_id
            ):

                completed.add(
                    (
                        game_id,
                        question_id,
                    )
                )

    return completed

def run_ontology_benchmark(
    games_data,
):

    from collections import defaultdict

    # ==================================================
    # COUNTERS
    # ==================================================

    total = 0

    semantic_pass = 0
    ontology_pass = 0
    end_to_end_pass = 0

    parsing_errors = 0
    semantic_errors = 0
    ontology_errors = 0
    end_to_end_errors = 0

    benchmark_results = []

    # ==================================================
    # RESUME
    # ==================================================

    completed_items = (
        load_completed_benchmark_items()
    )

    print(
        "ALREADY COMPLETED:",
        len(completed_items),
    )

    # ==================================================
    # HELPER — QUESTION TAXONOMY
    # ==================================================

    def classify_benchmark_item(
        item,
    ):

        expected = item[
            "expected_query"
        ]

        concepts = expected.get(
            "concepts",
            [],
        )

        operation = expected[
            "operation"
        ]

        question = item[
            "question"
        ].lower()

        # ------------------------------------------
        # QUERY TYPE
        # ------------------------------------------

        if operation == "RANK":

            query_type = "RANKING"

        elif operation == "RATIO":

            query_type = "RATIO"

        elif len(concepts) == 1:

            query_type = (
                "SINGLE_CONCEPT"
            )

        elif len(concepts) == 2:

            query_type = (
                "COMPOSITION_2"
            )

        else:

            query_type = (
                "COMPOSITION_3_PLUS"
            )

        # ------------------------------------------
        # LINGUISTIC TYPE
        # ------------------------------------------

        ambiguous_markers = [
            "how often",
        ]

        implicit_markers = [
            "from behind",
            "neither team ahead",
            "neither side ahead",
            "put points on the board",
            "giveaway",
            "give the ball away",
            "beyond the arc",
            "margin was within",
            "within one possession",
            "second opportunities",
            "still tight",
        ]

        if any(
            marker in question
            for marker
            in ambiguous_markers
        ):

            linguistic_type = (
                "AMBIGUOUS"
            )

        elif any(
            marker in question
            for marker
            in implicit_markers
        ):

            linguistic_type = (
                "IMPLICIT"
            )

        elif item["id"] >= "ONT_027":

            linguistic_type = (
                "PARAPHRASE"
            )

        else:

            linguistic_type = (
                "DIRECT"
            )

        # ------------------------------------------
        # DIFFICULTY
        # ------------------------------------------

        if operation == "RANK":

            difficulty = 4

        elif (
            linguistic_type
            == "AMBIGUOUS"
        ):

            difficulty = 4

        elif operation == "RATIO":

            difficulty = 3

        elif len(concepts) >= 3:

            difficulty = 3

        elif len(concepts) == 2:

            difficulty = 2

        else:

            difficulty = 1

        return {
            "query_type":
                query_type,
            "linguistic_type":
                linguistic_type,
            "difficulty":
                difficulty,
            "concept_count":
                len(concepts),
        }

    # ==================================================
    # HELPER — ERROR CLASSIFICATION
    # ==================================================

    def classify_semantic_error(
        expected_normalized,
        actual_normalized,
    ):

        expected_operation = (
            expected_normalized.get(
                "operation"
            )
        )

        actual_operation = (
            actual_normalized.get(
                "operation"
            )
        )

        if (
            expected_operation
            != actual_operation
        ):

            return "OPERATION_ERROR"

        expected_concepts = set(
            expected_normalized.get(
                "concepts",
                [],
            )
        )

        actual_concepts = set(
            actual_normalized.get(
                "concepts",
                [],
            )
        )

        if (
            expected_concepts
            != actual_concepts
        ):

            missing = (
                expected_concepts
                - actual_concepts
            )

            extra = (
                actual_concepts
                - expected_concepts
            )

            if missing and extra:

                return (
                    "CONCEPT_SUBSTITUTION"
                )

            if missing:

                return (
                    "CONCEPT_MISSING"
                )

            if extra:

                return (
                    "CONCEPT_EXTRA"
                )

        expected_denominator = set(
            expected_normalized.get(
                "denominator_concepts",
                [],
            )
            or []
        )

        actual_denominator = set(
            actual_normalized.get(
                "denominator_concepts",
                [],
            )
            or []
        )

        if (
            expected_denominator
            != actual_denominator
        ):

            return "DENOMINATOR_ERROR"

        if (
            expected_normalized.get(
                "entity"
            )
            != actual_normalized.get(
                "entity"
            )
        ):

            return "ENTITY_ERROR"

        if (
            expected_normalized.get(
                "metric"
            )
            != actual_normalized.get(
                "metric"
            )
        ):

            return "METRIC_ERROR"

        if (
            expected_normalized.get(
                "order"
            )
            != actual_normalized.get(
                "order"
            )
        ):

            return "ORDER_ERROR"

        if (
            expected_normalized.get(
                "limit"
            )
            != actual_normalized.get(
                "limit"
            )
        ):

            return "LIMIT_ERROR"

        return "SEMANTIC_ERROR"

    # ==================================================
    # BUILD INDEPENDENT GROUND TRUTH
    # ==================================================

    ground_truth_by_game = {}

    for (
        game_id,
        game_data,
    ) in games_data.items():

        ground_truth_by_game[
            game_id
        ] = build_ontology_ground_truth(
            game_data[
                "possessions"
            ],
            game_data[
                "game_time"
            ],
        )

    # ==================================================
    # BENCHMARK
    # ==================================================

    for (
        game_id,
        game_data,
    ) in games_data.items():

        rdf_graph = game_data[
            "rdf_graph"
        ]

        ground_truth = (
            ground_truth_by_game[
                game_id
            ]
        )

        for item in ONTOLOGY_BENCHMARK:

            # ==========================================
            # QUESTION IDENTIFICATION
            # ==========================================

            question_id = item[
                "id"
            ]

            question = item[
                "question"
            ]

            # ==========================================
            # RESUME
            # ==========================================

            result_key = (
                game_id,
                question_id,
            )

            if (
                result_key
                in completed_items
            ):

                print(
                    f"\n[{question_id}] "
                    f"[GAME={game_id}] "
                    f"SKIP — ALREADY COMPLETED"
                )

                continue

            total += 1

            expected_dict = item[
                "expected_query"
            ]

            metadata = (
                classify_benchmark_item(
                    item
                )
            )

            print(
                f"\n[{question_id}] "
                f"[GAME={game_id}]"
            )

            print(question)

            # ==========================================
            # EXPECTED QUERY
            # ==========================================

            expected_query = OntologyQuery(

                concepts=expected_dict[
                    "concepts"
                ],

                operation=OntologyOperation(
                    expected_dict[
                        "operation"
                    ]
                ),

                denominator_concepts=(
                    expected_dict.get(
                        "denominator_concepts"
                    )
                ),

                entity=(
                    OntologyEntity(
                        expected_dict[
                            "entity"
                        ]
                    )
                    if expected_dict.get(
                        "entity"
                    )
                    else None
                ),

                metric=(
                    OntologyMetric(
                        expected_dict[
                            "metric"
                        ]
                    )
                    if expected_dict.get(
                        "metric"
                    )
                    else None
                ),

                order=(
                    OntologyOrder(
                        expected_dict[
                            "order"
                        ]
                    )
                    if expected_dict.get(
                        "order"
                    )
                    else None
                ),

                limit=expected_dict.get(
                    "limit"
                ),
            )

            expected_normalized = (
                _normalize_query(
                    expected_dict
                )
            )

            # ==========================================
            # INDEPENDENT GROUND TRUTH
            # ==========================================

            expected_answer = (
                execute_ground_truth_query(

                    ground_truth=(
                        ground_truth
                    ),

                    concepts=(
                        expected_dict[
                            "concepts"
                        ]
                    ),

                    operation=(
                        expected_dict[
                            "operation"
                        ]
                    ),

                    denominator_concepts=(
                        expected_dict.get(
                            "denominator_concepts"
                        )
                    ),

                    entity=(
                        expected_dict.get(
                            "entity"
                        )
                    ),

                    metric=(
                        expected_dict.get(
                            "metric"
                        )
                    ),

                    order=(
                        expected_dict.get(
                            "order"
                        )
                    ),

                    limit=(
                        expected_dict.get(
                            "limit"
                        )
                    ),

                    possessions=(
                        game_data[
                            "possessions"
                        ]
                    ),

                    game_time=(
                        game_data[
                            "game_time"
                        ]
                    ),
                )
            )

            # ==========================================
            # REFERENCE ONTOLOGY EXECUTION
            # ==========================================

            reference_result = (
                execute_ontology_query(
                    rdf_graph,
                    expected_query,
                )
            )

            reference_answer = (
                extract_ontology_answer(
                    reference_result
                )
            )

            ontology_correct = (
                _answers_equal(
                    reference_answer,
                    expected_answer,
                )
            )

            if ontology_correct:

                ontology_pass += 1

            else:

                ontology_errors += 1

            # ==========================================
            # LLM SEMANTIC PARSING
            # ==========================================

            try:

                parsed = (
                    parse_ontology_intent(
                        question
                    )
                )

                actual_query = (
                    build_ontology_query(
                        parsed
                    )
                )

            except Exception as exc:

                parsing_errors += 1
                end_to_end_errors += 1

                print(
                    "PARSING_ERROR |",
                    type(exc).__name__,
                    str(exc),
                )

                print(
                    "ONTOLOGY:",
                    (
                        "PASS"
                        if ontology_correct
                        else "FAIL"
                    ),
                    "| GT =",
                    expected_answer,
                    "| RESULT =",
                    reference_answer,
                )

                print(
                    "END-TO-END: FAIL"
                )

                # --------------------------------------
                # RESULT ROW
                # --------------------------------------

                result_row = {

                    "game_id":
                        game_id,

                    "question_id":
                        question_id,

                    "question":
                        question,

                    "query_type":
                        metadata[
                            "query_type"
                        ],

                    "linguistic_type":
                        metadata[
                            "linguistic_type"
                        ],

                    "difficulty":
                        metadata[
                            "difficulty"
                        ],

                    "concept_count":
                        metadata[
                            "concept_count"
                        ],

                    "expected_operation":
                        expected_normalized.get(
                            "operation"
                        ),

                    "expected_concepts":
                        expected_normalized.get(
                            "concepts"
                        ),

                    "expected_denominator":
                        expected_normalized.get(
                            "denominator_concepts"
                        ),

                    "expected_entity":
                        expected_normalized.get(
                            "entity"
                        ),

                    "expected_metric":
                        expected_normalized.get(
                            "metric"
                        ),

                    "actual_operation":
                        None,

                    "actual_concepts":
                        None,

                    "actual_denominator":
                        None,

                    "actual_entity":
                        None,

                    "actual_metric":
                        None,

                    "ground_truth_answer":
                        expected_answer,

                    "ontology_answer":
                        reference_answer,

                    "llm_answer":
                        None,

                    "semantic_correct":
                        False,

                    "ontology_correct":
                        ontology_correct,

                    "answer_correct":
                        False,

                    "end_to_end_correct":
                        False,

                    "error_stage":
                        "PARSING",

                    "error_type":
                        "PARSING_ERROR",

                    "error_message":
                        str(exc),
                }

                benchmark_results.append(
                    result_row
                )

                # --------------------------------------
                # IMMEDIATE DISK CHECKPOINT
                # --------------------------------------

                append_benchmark_result(
                    result_row
                )

                completed_items.add(
                    result_key
                )

                continue

            # ==========================================
            # SEMANTIC ACCURACY
            # ==========================================

            actual_normalized = (
                _normalize_query(
                    _ontology_query_to_dict(
                        actual_query
                    )
                )
            )

            semantic_correct = (
                expected_normalized
                == actual_normalized
            )

            if semantic_correct:

                semantic_pass += 1

            else:

                semantic_errors += 1

            # ==========================================
            # EXECUTE LLM QUERY
            # ==========================================

            actual_result = (
                execute_ontology_query(
                    rdf_graph,
                    actual_query,
                )
            )

            actual_answer = (
                extract_ontology_answer(
                    actual_result
                )
            )

            # ==========================================
            # ANSWER ACCURACY
            # ==========================================

            answer_correct = (
                _answers_equal(
                    actual_answer,
                    expected_answer,
                )
            )

            # ==========================================
            # END-TO-END
            # ==========================================

            end_to_end_correct = (
                semantic_correct
                and
                answer_correct
            )

            if end_to_end_correct:

                end_to_end_pass += 1

            else:

                end_to_end_errors += 1

            # ==========================================
            # ERROR CLASSIFICATION
            # ==========================================

            error_stage = None
            error_type = None

            if not semantic_correct:

                error_stage = "SEMANTIC"

                error_type = (
                    classify_semantic_error(
                        expected_normalized,
                        actual_normalized,
                    )
                )

            elif not ontology_correct:

                error_stage = "ONTOLOGY"

                error_type = (
                    "ONTOLOGY_ERROR"
                )

            elif not answer_correct:

                error_stage = "ANSWER"

                error_type = (
                    "ANSWER_ERROR"
                )

            # ==========================================
            # CONSOLE OUTPUT
            # ==========================================

            print(
                "SEMANTIC:",
                (
                    "PASS"
                    if semantic_correct
                    else "FAIL"
                ),
            )

            print(
                "ONTOLOGY:",
                (
                    "PASS"
                    if ontology_correct
                    else "FAIL"
                ),
                "| GT =",
                expected_answer,
                "| RESULT =",
                reference_answer,
            )

            print(
                "END-TO-END:",
                (
                    "PASS"
                    if end_to_end_correct
                    else "FAIL"
                ),
                "| RESULT =",
                actual_answer,
            )

            if not semantic_correct:

                print(
                    "  expected_query =",
                    expected_normalized,
                )

                print(
                    "  actual_query   =",
                    actual_normalized,
                )

                print(
                    "  error_type     =",
                    error_type,
                )

            if not answer_correct:

                print(
                    "  expected_answer =",
                    expected_answer,
                )

                print(
                    "  actual_answer   =",
                    actual_answer,
                )

            # ==========================================
            # STORE RESULT
            # ==========================================

            result_row = {

                "game_id":
                    game_id,

                "question_id":
                    question_id,

                "question":
                    question,

                # --------------------------------------
                # TAXONOMY
                # --------------------------------------

                "query_type":
                    metadata[
                        "query_type"
                    ],

                "linguistic_type":
                    metadata[
                        "linguistic_type"
                    ],

                "difficulty":
                    metadata[
                        "difficulty"
                    ],

                "concept_count":
                    metadata[
                        "concept_count"
                    ],

                # --------------------------------------
                # EXPECTED
                # --------------------------------------

                "expected_operation":
                    expected_normalized.get(
                        "operation"
                    ),

                "expected_concepts":
                    expected_normalized.get(
                        "concepts"
                    ),

                "expected_denominator":
                    expected_normalized.get(
                        "denominator_concepts"
                    ),

                "expected_entity":
                    expected_normalized.get(
                        "entity"
                    ),

                "expected_metric":
                    expected_normalized.get(
                        "metric"
                    ),

                # --------------------------------------
                # ACTUAL
                # --------------------------------------

                "actual_operation":
                    actual_normalized.get(
                        "operation"
                    ),

                "actual_concepts":
                    actual_normalized.get(
                        "concepts"
                    ),

                "actual_denominator":
                    actual_normalized.get(
                        "denominator_concepts"
                    ),

                "actual_entity":
                    actual_normalized.get(
                        "entity"
                    ),

                "actual_metric":
                    actual_normalized.get(
                        "metric"
                    ),

                # --------------------------------------
                # ANSWERS
                # --------------------------------------

                "ground_truth_answer":
                    expected_answer,

                "ontology_answer":
                    reference_answer,

                "llm_answer":
                    actual_answer,

                # --------------------------------------
                # RESULTS
                # --------------------------------------

                "semantic_correct":
                    semantic_correct,

                "ontology_correct":
                    ontology_correct,

                "answer_correct":
                    answer_correct,

                "end_to_end_correct":
                    end_to_end_correct,

                # --------------------------------------
                # ERRORS
                # --------------------------------------

                "error_stage":
                    error_stage,

                "error_type":
                    error_type,

                "error_message":
                    None,
            }

            benchmark_results.append(
                result_row
            )

            # ==========================================
            # IMMEDIATE DISK CHECKPOINT
            # ==========================================

            append_benchmark_result(
                result_row
            )

            completed_items.add(
                result_key
            )

    # ==================================================
    # GLOBAL SUMMARY FOR THIS CALL
    # ==================================================

    semantic_accuracy = (
        semantic_pass / total
        if total
        else 0
    )

    ontology_accuracy = (
        ontology_pass / total
        if total
        else 0
    )

    end_to_end_accuracy = (
        end_to_end_pass / total
        if total
        else 0
    )

    print("\n")
    print("=" * 70)
    print(
        "ONTOLOGY BENCHMARK SUMMARY"
    )
    print("=" * 70)

    print(
        f"INSTANCES:              "
        f"{total}"
    )

    print(
        f"SEMANTIC PASS:          "
        f"{semantic_pass} / {total}"
    )

    print(
        f"ONTOLOGY PASS:          "
        f"{ontology_pass} / {total}"
    )

    print(
        f"END-TO-END PASS:        "
        f"{end_to_end_pass} / {total}"
    )

    print(
        f"PARSING ERROR:          "
        f"{parsing_errors}"
    )

    print(
        f"SEMANTIC ERROR:         "
        f"{semantic_errors}"
    )

    print(
        f"ONTOLOGY ERROR:         "
        f"{ontology_errors}"
    )

    print(
        f"END-TO-END ERROR:       "
        f"{end_to_end_errors}"
    )

    print("-" * 70)

    print(
        "Semantic parsing accuracy:",
        f"{semantic_accuracy:.1%}",
    )

    print(
        "Ontology inference accuracy:",
        f"{ontology_accuracy:.1%}",
    )

    print(
        "End-to-end accuracy:",
        f"{end_to_end_accuracy:.1%}",
    )

    # ==================================================
    # BREAKDOWN HELPER
    # ==================================================

    def print_breakdown(
        field,
    ):

        groups = defaultdict(
            list
        )

        for row in benchmark_results:

            groups[
                row[field]
            ].append(
                row
            )

        print("\n")
        print("=" * 70)

        print(
            f"RESULTS BY "
            f"{field.upper()}"
        )

        print("=" * 70)

        for (
            group,
            rows,
        ) in sorted(
            groups.items(),
            key=lambda x: str(
                x[0]
            ),
        ):

            group_total = len(
                rows
            )

            group_semantic = sum(
                1
                for row in rows
                if row[
                    "semantic_correct"
                ]
            )

            group_ontology = sum(
                1
                for row in rows
                if row[
                    "ontology_correct"
                ]
            )

            group_e2e = sum(
                1
                for row in rows
                if row[
                    "end_to_end_correct"
                ]
            )

            print(
                f"{str(group):25}"
                f" N={group_total:3} | "
                f"SEM="
                f"{group_semantic / group_total:6.1%}"
                f" | "
                f"ONT="
                f"{group_ontology / group_total:6.1%}"
                f" | "
                f"E2E="
                f"{group_e2e / group_total:6.1%}"
            )

    # ==================================================
    # BREAKDOWNS
    # ==================================================

    print_breakdown(
        "query_type"
    )

    print_breakdown(
        "linguistic_type"
    )

    print_breakdown(
        "difficulty"
    )

    # ==================================================
    # ERROR DISTRIBUTION
    # ==================================================

    error_counts = defaultdict(
        int
    )

    for row in benchmark_results:

        if row[
            "error_type"
        ]:

            error_counts[
                row["error_type"]
            ] += 1

    print("\n")
    print("=" * 70)
    print(
        "ERROR DISTRIBUTION"
    )
    print("=" * 70)

    if error_counts:

        for (
            error_type,
            count,
        ) in sorted(
            error_counts.items(),
            key=lambda x: (
                -x[1],
                x[0],
            ),
        ):

            print(
                f"{error_type:30}"
                f"{count}"
            )

    else:

        print(
            "No errors."
        )

    # ==================================================
    # SUMMARY OBJECT
    #
    # This is the summary for THIS invocation.
    # With the new main this normally means one game.
    # Final season statistics will be reconstructed
    # from the persistent CSV / JSONL.
    # ==================================================

    summary = {

        "games":
            len(games_data),

        "questions":
            len(
                ONTOLOGY_BENCHMARK
            ),

        "instances":
            total,

        "semantic_pass":
            semantic_pass,

        "ontology_pass":
            ontology_pass,

        "end_to_end_pass":
            end_to_end_pass,

        "parsing_errors":
            parsing_errors,

        "semantic_errors":
            semantic_errors,

        "ontology_errors":
            ontology_errors,

        "end_to_end_errors":
            end_to_end_errors,

        "semantic_accuracy":
            semantic_accuracy,

        "ontology_accuracy":
            ontology_accuracy,

        "end_to_end_accuracy":
            end_to_end_accuracy,

        "error_distribution":
            dict(
                error_counts
            ),
    }

    # ==================================================
    # CHECKPOINT INFO
    #
    # DO NOT rewrite the global CSV here.
    # Every result has already been appended.
    # ==================================================

    csv_path, jsonl_path = (
        _benchmark_output_paths()
    )

    print("\n")
    print("=" * 70)
    print(
        "BENCHMARK CHECKPOINT"
    )
    print("=" * 70)

    print(
        "CSV:   ",
        csv_path,
    )

    print(
        "JSONL: ",
        jsonl_path,
    )

    return {
        "results":
            benchmark_results,
        "summary":
            summary,
    }


def extract_ontology_answer(
    result,
):

    operation = result[
        "operation"
    ]

    if operation == "COUNT":
        return result["count"]

    if operation == "RATIO":
        return result["ratio"]

    raise ValueError(
        f"Unsupported operation: {operation}"
    )


def _answers_equal(
    actual,
    expected,
    tolerance=1e-9,
):

    # ==================================================
    # NONE
    # ==================================================

    if (
        actual is None
        or expected is None
    ):
        return actual is expected

    # ==================================================
    # NUMERIC
    # COUNT / RATIO
    # ==================================================

    if (
        isinstance(actual, (int, float))
        and
        isinstance(expected, (int, float))
    ):
        return (
            abs(actual - expected)
            <= tolerance
        )

    # ==================================================
    # RANKING
    #
    # For a top-player query, two different players
    # are considered equivalent when they have the
    # same ranking value.
    #
    # This handles ties where GT and RDF may select
    # different players because LIMIT 1 does not
    # define a deterministic tie-break.
    # ==================================================

    if (
        isinstance(actual, list)
        and isinstance(expected, list)
        and len(actual) == 1
        and len(expected) == 1
        and isinstance(actual[0], dict)
        and isinstance(expected[0], dict)
        and "player" in actual[0]
        and "player" in expected[0]
        and "value" in actual[0]
        and "value" in expected[0]
    ):

        actual_value = actual[0][
            "value"
        ]

        expected_value = expected[0][
            "value"
        ]

        if (
            isinstance(
                actual_value,
                (int, float),
            )
            and isinstance(
                expected_value,
                (int, float),
            )
        ):

            return (
                abs(
                    actual_value
                    - expected_value
                )
                <= tolerance
            )

        return (
            actual_value
            == expected_value
        )

    # ==================================================
    # DEFAULT
    # ==================================================

    return actual == expected

def normalize_ontology_answer(
    result,
):

    # ==================================================
    # RANK RESULT
    # ==================================================

    if (
        isinstance(result, dict)
        and result.get("operation") == "RANK"
    ):

        normalized = []

        for item in result.get(
            "ranking",
            []
        ):

            player = str(
                item["player"]
            )

            # RDF:
            # https://viziball.io/resource/player/293
            #
            # becomes:
            # 293

            player_id = (
                player
                .rstrip("/")
                .split("/")[-1]
            )

            normalized.append({
                "player": player_id,
                "value": item["value"],
            })

        return normalized

    # ==================================================
    # COUNT / RATIO
    #
    # Already handled by the existing benchmark logic.
    # ==================================================

    return result

def extract_ontology_answer(
    result,
):

    operation = result.get(
        "operation"
    )

    # ==================================================
    # COUNT
    # ==================================================

    if operation == "COUNT":
        return result["count"]

    # ==================================================
    # RATIO
    # ==================================================

    if operation == "RATIO":
        return result["ratio"]

    # ==================================================
    # RANK
    # ==================================================

    if operation == "RANK":

        normalized = []

        for item in result.get(
            "ranking",
            []
        ):

            player_id = (
                str(item["player"])
                .rstrip("/")
                .split("/")[-1]
            )

            normalized.append({
                "player": player_id,
                "value": item["value"],
            })

        return normalized

    raise ValueError(
        f"Unsupported result operation: "
        f"{operation}"
    )

def classify_benchmark_item(item):

    expected = item["expected_query"]

    concepts = expected.get(
        "concepts",
        [],
    )

    operation = expected[
        "operation"
    ]

    question = item[
        "question"
    ].lower()

    # ==========================================
    # QUERY TYPE
    # ==========================================

    if operation == "RANK":
        query_type = "RANKING"

    elif operation == "RATIO":
        query_type = "RATIO"

    elif len(concepts) == 1:
        query_type = "SINGLE_CONCEPT"

    elif len(concepts) == 2:
        query_type = "COMPOSITION_2"

    else:
        query_type = "COMPOSITION_3_PLUS"

    # ==========================================
    # LINGUISTIC TYPE
    #
    # Fixed heuristic taxonomy for this POC.
    # ==========================================

    ambiguous_markers = [
        "how often",
    ]

    implicit_markers = [
        "from behind",
        "neither team ahead",
        "neither side ahead",
        "put points on the board",
        "giveaway",
        "give the ball away",
        "beyond the arc",
        "margin was within",
        "within one possession",
        "second opportunities",
        "still tight",
    ]

    if any(
        marker in question
        for marker in ambiguous_markers
    ):
        linguistic_type = "AMBIGUOUS"

    elif any(
        marker in question
        for marker in implicit_markers
    ):
        linguistic_type = "IMPLICIT"

    elif item["id"] >= "ONT_027":
        linguistic_type = "PARAPHRASE"

    else:
        linguistic_type = "DIRECT"

    # ==========================================
    # COMPLEXITY
    # ==========================================

    if operation == "RANK":
        difficulty = 4

    elif linguistic_type == "AMBIGUOUS":
        difficulty = 4

    elif operation == "RATIO":
        difficulty = 3

    elif len(concepts) >= 3:
        difficulty = 3

    elif len(concepts) == 2:
        difficulty = 2

    else:
        difficulty = 1

    return {
        "query_type": query_type,
        "linguistic_type": linguistic_type,
        "difficulty": difficulty,
        "concept_count": len(concepts),
    }