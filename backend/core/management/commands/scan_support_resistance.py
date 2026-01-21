from __future__ import annotations

import json

from django.core.management.base import BaseCommand

from core.trading.bot import SupportResistanceBot


class Command(BaseCommand):
    help = "Identify intraday support/resistance zones using Capital.com price data."

    def add_arguments(self, parser):
        parser.add_argument("epic", help="Capital.com epic (e.g. US500)")
        parser.add_argument("--resolution", default="MINUTE", help="Price resolution")
        parser.add_argument("--max-points", type=int, default=200, help="Number of candles to request")

    def handle(self, *args, **options):
        bot = SupportResistanceBot()
        payload = bot.analyze_payload(
            epic=options["epic"],
            resolution=options["resolution"],
            max_points=options["max_points"],
        )
        self.stdout.write(json.dumps(payload, indent=2))
