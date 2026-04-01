def compute_opportunity_score(
    business_value: float,
    traffic_potential: float,
    rankability: float,
    freshness_need: float,
    content_gap: float,
    ease: float,
) -> float:
    return round(
        business_value * 0.30
        + traffic_potential * 0.25
        + rankability * 0.20
        + freshness_need * 0.10
        + content_gap * 0.10
        + ease * 0.05,
        4,
    )
