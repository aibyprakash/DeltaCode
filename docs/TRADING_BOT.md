# Capital.com Intraday Support/Resistance Bot

This module adds a lightweight intraday bot that fetches Capital.com price data, detects
support/resistance zones, and highlights breakout or trend-reversal signals.

## Environment variables

Set the following variables before running the command:

- `CAPITAL_API_KEY`
- `CAPITAL_IDENTIFIER`
- `CAPITAL_PASSWORD`
- `CAPITAL_API_URL` (optional, defaults to `https://api-capital.backend-capital.com`)

## Usage

Run the Django management command from `backend/`:

```bash
python manage.py scan_support_resistance US500 --resolution MINUTE --max-points 200
```

The command prints a JSON payload containing:

- `zones`: clustered support/resistance zones with strength counts.
- `breakout`: breakout direction and level.
- `trend`: moving-average trend and reversal hint.
```
