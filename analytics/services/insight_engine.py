"""
Insight engine responsible for analyzing MetricSnapshot data
and generating actionable marketing insights.
"""

from metrics.models import MetricSnapshot
from analytics.models import Insight


class InsightEngine:
    """
    Analyze a MetricSnapshot and produce insights based on rule detection.
    """

    def __init__(self, snapshot: MetricSnapshot):
        self.snapshot = snapshot

    def run(self):
        """
        Execute all detection rules and return a list of insights.
        """

        rules = [
            self.detect_high_cpc,
            self.detect_low_ctr,
        ]

        insights = []

        for rule in rules:
            insights += rule()

        return insights

    def detect_high_cpc(self):
        """
        Detect if Cost Per Click is above expected threshold.
        """

        if self.snapshot.clicks == 0:
            return []

        cpc = self.snapshot.spend / self.snapshot.clicks

        if cpc > 5:
            return [
                {
                    "type": "high_cpc",
                    "severity": "warning",
                    "message": f"CPC is high: {round(cpc, 2)}",
                    "recommendation": "Review your ad targeting"
                }
            ]

        return []

    def detect_low_ctr(self):
        """
        Detect if Click Through Rate is below acceptable threshold.
        """

        if self.snapshot.impressions == 0:
            return []

        ctr = (self.snapshot.clicks / self.snapshot.impressions) * 100

        if ctr < 1:
            return [
                {
                    "type": "low_ctr",
                    "severity": "critical",
                    "message": f"CTR is low: {round(ctr, 2)}%",
                    "recommendation": "Test new creatives"
                }
            ]

        return []


def generate_and_store_insights(snapshot: MetricSnapshot):
    """
    Run the InsightEngine and persist generated insights to the database.
    """

    engine = InsightEngine(snapshot)

    insights = engine.run()

    for insight in insights:
        # Avoid duplicate insights for the same snapshot
        already_exists = Insight.objects.filter(
            integration=snapshot.integration,
            metric_snapshot=snapshot,
            type=insight["type"],
            message=insight["message"],
        ).exists()

        if not already_exists:
            Insight.objects.create(
                integration=snapshot.integration,
                metric_snapshot=snapshot,
                type=insight["type"],
                severity=insight["severity"],
                message=insight["message"],
                recommendation=insight["recommendation"],
            )
