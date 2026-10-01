def infer_game_time_structure(game):
    # ta fonction actuelle
    ...


def second_to_game_clock(second, game_time):
    regulation_periods = game_time["regulation_period_count"]
    regulation_period_seconds = game_time["regulation_period_seconds"]
    regulation_end = game_time["regulation_end_second"]
    overtime_period_seconds = game_time["overtime_period_seconds"]

    if second <= regulation_end:

        if second == 0:
            period = 1
            elapsed = 0
        else:
            period = (
                (second - 1) // regulation_period_seconds
            ) + 1

            period_start = (
                (period - 1)
                * regulation_period_seconds
            )

            elapsed = second - period_start

        remaining = max(
            0,
            regulation_period_seconds - elapsed
        )

        return {
            "period": period,
            "is_overtime": False,
            "elapsed_seconds": elapsed,
            "remaining_seconds": remaining,
        }

    overtime_elapsed = second - regulation_end

    overtime_index = (
        (overtime_elapsed - 1)
        // overtime_period_seconds
    )

    period = (
        regulation_periods
        + overtime_index
        + 1
    )

    overtime_start = (
        regulation_end
        + overtime_index * overtime_period_seconds
    )

    elapsed = second - overtime_start

    remaining = max(
        0,
        overtime_period_seconds - elapsed
    )

    return {
        "period": period,
        "is_overtime": True,
        "elapsed_seconds": elapsed,
        "remaining_seconds": remaining,
    }