# Ski Piste Recommender

An MVP application that recommends the best groomed ski pistes for each day and time of day based on weather forecasts and piste metadata.

## Features

- **Weather-based recommendations**: Uses real-time weather forecasts from Open-Meteo API
- **Snow condition modeling**: Determines snow surface state (icy, firm groomed, packed powder, soft, slushy)
- **Time-of-day optimization**: Provides recommendations for morning, late morning, and afternoon
- **Skill-level filtering**: Tailors recommendations to beginner, intermediate, or advanced skiers
- **Explainable AI**: Every recommendation includes a clear explanation of the factors
- **Multiple resorts**: Supports 6 major European ski resorts
- **Resort-level recommendations**: Compare resorts to find the best skiing destination for current conditions
- **Piste-level recommendations**: Find the best specific pistes within a chosen resort

## Supported Resorts

- **Val Thorens** (France) - `val_thorens`
- **Zermatt** (Switzerland) - `zermatt`
- **Chamonix** (France) - `chamonix`
- **Courchevel** (France) - `courchevel`
- **Verbier** (Switzerland) - `verbier`
- **St. Anton** (Austria) - `st_anton`

## Installation

```bash
# Clone the repository
git clone https://github.com/SanderWeide/ski-recommender.git
cd ski-recommender

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Piste-Level Recommendations (Single Resort)

Find the best pistes within a specific resort:

```bash
# Basic usage with defaults (Val Thorens, intermediate)
python main.py

# Specify resort and skill level
python main.py val_thorens intermediate

# Different resort
python main.py zermatt advanced

# JSON output
python main.py chamonix beginner json
```

### Resort-Level Recommendations (Compare Resorts)

Compare multiple resorts to find the best one for current conditions:

```bash
# Compare all resorts (default)
python main_resort.py

# Compare specific resorts
python main_resort.py val_thorens,zermatt intermediate

# Compare all resorts for advanced skiers
python main_resort.py all advanced

# JSON output
python main_resort.py all intermediate json
```

### Live API Data Mode

```bash
# Uses real weather data from Open-Meteo API
python main_live.py val_thorens intermediate

# JSON output
python main_live.py zermatt advanced json
```

### Command Line Arguments

**Piste-Level Mode:**
```
python main.py [resort_id] [skill_level] [output_format]

Arguments:
  resort_id      : Resort identifier (val_thorens, zermatt, chamonix, courchevel, verbier, st_anton)
  skill_level    : Skier skill level (beginner, intermediate, advanced)
  output_format  : Output format (text or json)
```

**Resort-Level Mode:**
```
python main_resort.py [resort_selection] [skill_level] [output_format]

Arguments:
  resort_selection : 'all' (default) or comma-separated resort IDs (e.g., 'val_thorens,zermatt')
  skill_level      : Skier skill level (beginner, intermediate, advanced)
  output_format    : Output format (text or json)
```

## How It Works

### Snow Quality Modeling

The system models snow surface conditions based on:

1. **Freeze-thaw cycles**: Detects overnight refreezing quality
2. **Sun exposure**: Calculates solar impact by slope aspect and time of day
3. **Temperature trends**: Monitors warming and cooling patterns
4. **Precipitation**: Tracks fresh snowfall and rain-on-snow events
5. **Wind exposure**: Penalizes high-altitude, wind-exposed pistes

### Scoring Algorithm

Each piste receives a score (0-100) based on:

- **Base score**: From snow surface state (firm groomed = 80, icy = 40, etc.)
- **Altitude bonus**: Higher altitude = more reliable conditions
- **Grooming**: Overnight grooming improves scores
- **Wind penalty**: Strong winds at high altitude reduce scores
- **Temperature factor**: Ideal temps vary by time of day
- **Sun exposure**: Can be positive (softening firm snow) or negative (creating slush)
- **Fresh snow bonus**: Recent snowfall improves conditions
- **Rain penalty**: Rain degrades snow quality

### Time of Day Blocks

- **Morning (08:00-10:30)**: Prefers firm, grippy snow from overnight grooming
- **Late Morning (10:30-12:30)**: Transitional period as snow warms
- **Afternoon (12:30-16:00)**: Accounts for sun softening and potential slush

## Architecture

```
/src
  /services         # External API clients (Open-Meteo)
  /snow_model       # Snow surface state modeling
  /scoring          # Piste scoring engine
  /recommendation   # Main recommendation engine
  /data             # Resort and piste data
/tests              # Test suite
main.py             # CLI with mock data
main_live.py        # CLI with live API data
```

## Testing

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_models.py
```

## Data Sources

- **Weather**: [Open-Meteo API](https://open-meteo.com/) - Free, no API key required
- **Piste data**: Currently uses sample data; can be extended with OSM Overpass API
- **Elevation**: Altitudes from resort documentation

## Example Output

### Piste-Level Recommendations

```
=== Ski Piste Recommendations for Val Thorens ===

============================================================
Date: 2026-01-11
============================================================

Morning (08:00-10:30)
------------------------------------------------------------
Conditions: good overnight refreeze, temperatures stable.
Confidence: HIGH

Top Recommendations:

  1. Cime Caron (Score: 87/100)
     Difficulty: RED
     Altitude: 2800-3200m
     Snow State: Firm Groomed
     N-facing red piste, high altitude, cold overnight refreeze → firm, grippy snow, groomed overnight.

  2. Grand Fond (Score: 85/100)
     Difficulty: BLACK
     Altitude: 2500-3000m
     Snow State: Firm Groomed
     NW-facing black piste, high altitude, cold overnight refreeze → firm, grippy snow, groomed overnight.
```

### Resort-Level Recommendations

```
=== Ski Resort Recommendations ===

============================================================
Date: 2026-01-11
============================================================

Morning (08:00-10:30)
------------------------------------------------------------
Confidence: HIGH

Top Resorts:

  1. Val Thorens, France (Score: 100/100)
     Conditions: Fresh snow (3cm), temperatures warming.
     5 suitable pistes, altitude range 2300-3200m, top pistes averaging 100/100.
     Top Pistes:
       1. Cime Caron (RED, 100/100)
       2. Cascades (BLUE, 100/100)
       3. Moraine (GREEN, 100/100)

  2. Zermatt, Switzerland (Score: 98/100)
     Conditions: Fresh snow (3cm), temperatures warming.
     3 suitable pistes, altitude range 2500-3800m, top pistes averaging 92/100.
     Top Pistes:
       1. Blauherd (BLUE, 100/100)
       2. Stockhorn (RED, 91/100)
       3. Plateau Rosa (BLUE, 85/100)
```


## Design Philosophy

- **Explainability first**: Every recommendation must be understandable
- **Rule-based logic**: No black-box ML models
- **On-piste only**: No backcountry or avalanche considerations
- **Fast execution**: < 5 seconds per resort/week
- **Graceful degradation**: Works with mock data when APIs unavailable

## Future Enhancements

- Real OSM piste data integration
- Real-time grooming status
- Crowd density predictions
- Multi-day snow accumulation tracking
- Historical accuracy validation
- Mobile app interface
- Lift status integration

## License

MIT

## Contributing

Contributions welcome! Please open an issue or submit a pull request.