from metrics.models import MetricSnapshot
from analytics.models import Insight

class InsightEngine:

    def __init__(self, snapshot):
        self.snapshot = snapshot

    def run(self):

        insights = []

        insights += self.detect_high_cpc()
        insights += self.detect_low_ctr()

        return insights

    def detect_high_cpc(self):

        if self.snapshot.clicks == 0:
            return []

        cpc = self.snapshot.spend / self.snapshot.clicks

        if cpc > 5:

            return [
                {
                    "type": "high_cpc",
                    "severity": "warning",
                    "message": f"CPC is high: {round(cpc,2)}",
                    "recommendation": "Review your ad targeting"
                }
            ]

        return []

    def detect_low_ctr(self):

        if self.snapshot.impressions == 0:
            return []

        ctr = (self.snapshot.clicks / self.snapshot.impressions) * 100

        if ctr < 1:

            return [
                {
                    "type": "low_ctr",
                    "severity": "critical",
                    "message": f"CTR is low: {round(ctr,2)}%",
                    "recommendation": "Test new creatives"
                }
            ]

        return []


def generate_and_store_insights(snapshot):

    engine = InsightEngine(snapshot)

    insights = engine.run()

    for insight in insights:

        Insight.objects.create(
            integration=snapshot.integration,
            type=insight["type"],
            severity=insight["severity"],
            message=insight["message"],
            recommendation=insight["recommendation"],
        )