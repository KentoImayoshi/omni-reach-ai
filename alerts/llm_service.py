def generate_insight(impressions, clicks, spend):
    ctr = (clicks / impressions) * 100 if impressions else 0

    return (
        f"Campaign generated {impressions} impressions and {clicks} clicks. "
        f"CTR is {ctr:.2f}%. Total spend was ${spend}."
    )