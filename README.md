# Ski Piste Recommender

An MVP application that recommends the best groomed ski pistes for each day and time of day based on weather forecasts and piste metadata.

## Features

- **Weather-based recommendations**: Uses real-time weather forecasts from Open-Meteo API
- **Snow condition modeling**: Determines snow surface state (icy, firm groomed, packed powder, soft, slushy)
- **Time-of-day optimization**: Provides recommendations for morning, late morning, and afternoon
- **Skill-level filtering**: Tailors recommendations to beginner, intermediate, or advanced skiers
- **Explainable AI**: Every recommendation includes a clear explanation of the factors
- **Multiple resorts**: Supports 7 major European ski resorts
- **Resort-level recommendations**: Compare resorts to find the best skiing destination for current conditions
- **Piste-level recommendations**: Find the best specific pistes within a chosen resort

## Supported Resorts

- **Val Thorens** (France) - `val_thorens` - 8 pistes
- **Zermatt** (Switzerland) - `zermatt` - 7 pistes
- **Chamonix** (France) - `chamonix` - 7 pistes
- **Courchevel** (France) - `courchevel` - 7 pistes
- **Verbier** (Switzerland) - `verbier` - 7 pistes
- **St. Anton** (Austria) - `st_anton` - 7 pistes
- **Silvretta Arena** (Austria/Switzerland) - `silvretta_arena` - 8 pistes

## Installation

```bash
# Clone the repository
git clone https://github.com/SanderWeide/ski-recommender.git
cd ski-recommender

# Install dependencies
pip install -r requirements.txt
```

### Weekly Resort Recommendations

```
=== Weekly Ski Resort Recommendation ===

============================================================
Week: 2026-01-11 to 2026-01-17
============================================================
Confidence: MEDIUM

Top Resorts for the Week:

  1. Val Thorens, France (Score: 98/100)
     Conditions: Fresh snow (2cm), good overnight refreeze, temperatures warming.
     Average conditions over 7 days, 8 suitable pistes, altitude range 2300-3200m, top pistes averaging 100/100.
     Best Pistes for the Week:
       1. Cime Caron (RED, 100/100)
       2. Cascades (BLUE, 100/100)
       3. Moraine (GREEN, 100/100)

  2. Zermatt, Switzerland (Score: 94/100)
     Conditions: Fresh snow (2cm), good overnight refreeze, temperatures warming.
     Average conditions over 7 days, 7 suitable pistes, altitude range 2500-3800m, top pistes averaging 100/100.
     Best Pistes for the Week:
       1. Blauherd (BLUE, 100/100)
       2. Gornergrat (BLUE, 100/100)
       3. Stockhorn (RED, 100/100)
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

### Weekly Resort Recommendations

```
=== Weekly Ski Resort Recommendation ===

============================================================
Week: 2026-01-11 to 2026-01-17
============================================================
Confidence: MEDIUM

Top Resorts for the Week:

  1. Val Thorens, France (Score: 98/100)
     Conditions: Fresh snow (2cm), good overnight refreeze, temperatures warming.
     Average conditions over 7 days, 8 suitable pistes, altitude range 2300-3200m, top pistes averaging 100/100.
     Best Pistes for the Week:
       1. Cime Caron (RED, 100/100)
       2. Cascades (BLUE, 100/100)
       3. Moraine (GREEN, 100/100)

  2. Zermatt, Switzerland (Score: 94/100)
     Conditions: Fresh snow (2cm), good overnight refreeze, temperatures warming.
     Average conditions over 7 days, 7 suitable pistes, altitude range 2500-3800m, top pistes averaging 100/100.
     Best Pistes for the Week:
       1. Blauherd (BLUE, 100/100)
       2. Gornergrat (BLUE, 100/100)
       3. Stockhorn (RED, 100/100)
```


### Resort-Level Recommendations (Compare Resorts)

Compare multiple resorts to find the best one for current conditions:

**Time Block Mode** (default - shows recommendations for morning, late morning, and afternoon):
```bash
# Compare all resorts
python main_resort.py all intermediate

# Compare specific resorts
python main_resort.py val_thorens,zermatt intermediate

# JSON output
python main_resort.py all intermediate json
```

### Weekly Resort Recommendations

```
=== Weekly Ski Resort Recommendation ===

============================================================
Week: 2026-01-11 to 2026-01-17
============================================================
Confidence: MEDIUM

Top Resorts for the Week:

  1. Val Thorens, France (Score: 98/100)
     Conditions: Fresh snow (2cm), good overnight refreeze, temperatures warming.
     Average conditions over 7 days, 8 suitable pistes, altitude range 2300-3200m, top pistes averaging 100/100.
     Best Pistes for the Week:
       1. Cime Caron (RED, 100/100)
       2. Cascades (BLUE, 100/100)
       3. Moraine (GREEN, 100/100)

  2. Zermatt, Switzerland (Score: 94/100)
     Conditions: Fresh snow (2cm), good overnight refreeze, temperatures warming.
     Average conditions over 7 days, 7 suitable pistes, altitude range 2500-3800m, top pistes averaging 100/100.
     Best Pistes for the Week:
       1. Blauherd (BLUE, 100/100)
       2. Gornergrat (BLUE, 100/100)
       3. Stockhorn (RED, 100/100)
```


**Daily Mode** (aggregates recommendations over 24 hours):
```bash
# Compare all resorts with daily aggregation
python main_resort.py all intermediate daily

# Compare specific resorts with daily recommendations
python main_resort.py val_thorens,zermatt advanced daily

# JSON output
python main_resort.py all intermediate daily json
```

### Weekly Resort Recommendations

```
=== Weekly Ski Resort Recommendation ===

============================================================
Week: 2026-01-11 to 2026-01-17
============================================================
Confidence: MEDIUM

Top Resorts for the Week:

  1. Val Thorens, France (Score: 98/100)
     Conditions: Fresh snow (2cm), good overnight refreeze, temperatures warming.
     Average conditions over 7 days, 8 suitable pistes, altitude range 2300-3200m, top pistes averaging 100/100.
     Best Pistes for the Week:
       1. Cime Caron (RED, 100/100)
       2. Cascades (BLUE, 100/100)
       3. Moraine (GREEN, 100/100)

  2. Zermatt, Switzerland (Score: 94/100)
     Conditions: Fresh snow (2cm), good overnight refreeze, temperatures warming.
     Average conditions over 7 days, 7 suitable pistes, altitude range 2500-3800m, top pistes averaging 100/100.
     Best Pistes for the Week:
       1. Blauherd (BLUE, 100/100)
       2. Gornergrat (BLUE, 100/100)
       3. Stockhorn (RED, 100/100)
```


**Weekly Mode** (aggregates recommendations over 7 days):
```bash
# Compare all resorts with weekly aggregation
python main_resort.py all intermediate weekly

# Compare specific resorts with weekly recommendation
python main_resort.py val_thorens,zermatt advanced weekly

# JSON output
python main_resort.py all intermediate weekly json
```

### Weekly Resort Recommendations

```
=== Weekly Ski Resort Recommendation ===

============================================================
Week: 2026-01-11 to 2026-01-17
============================================================
Confidence: MEDIUM

Top Resorts for the Week:

  1. Val Thorens, France (Score: 98/100)
     Conditions: Fresh snow (2cm), good overnight refreeze, temperatures warming.
     Average conditions over 7 days, 8 suitable pistes, altitude range 2300-3200m, top pistes averaging 100/100.
     Best Pistes for the Week:
       1. Cime Caron (RED, 100/100)
       2. Cascades (BLUE, 100/100)
       3. Moraine (GREEN, 100/100)

  2. Zermatt, Switzerland (Score: 94/100)
     Conditions: Fresh snow (2cm), good overnight refreeze, temperatures warming.
     Average conditions over 7 days, 7 suitable pistes, altitude range 2500-3800m, top pistes averaging 100/100.
     Best Pistes for the Week:
       1. Blauherd (BLUE, 100/100)
       2. Gornergrat (BLUE, 100/100)
       3. Stockhorn (RED, 100/100)
```


### Live API Data Mode

**Piste-Level with Live Data:**
```bash
# Uses real weather data from Open-Meteo API
python main_live.py val_thorens intermediate

# JSON output
python main_live.py zermatt advanced json
```

### Weekly Resort Recommendations

```
=== Weekly Ski Resort Recommendation ===

============================================================
Week: 2026-01-11 to 2026-01-17
============================================================
Confidence: MEDIUM

Top Resorts for the Week:

  1. Val Thorens, France (Score: 98/100)
     Conditions: Fresh snow (2cm), good overnight refreeze, temperatures warming.
     Average conditions over 7 days, 8 suitable pistes, altitude range 2300-3200m, top pistes averaging 100/100.
     Best Pistes for the Week:
       1. Cime Caron (RED, 100/100)
       2. Cascades (BLUE, 100/100)
       3. Moraine (GREEN, 100/100)

  2. Zermatt, Switzerland (Score: 94/100)
     Conditions: Fresh snow (2cm), good overnight refreeze, temperatures warming.
     Average conditions over 7 days, 7 suitable pistes, altitude range 2500-3800m, top pistes averaging 100/100.
     Best Pistes for the Week:
       1. Blauherd (BLUE, 100/100)
       2. Gornergrat (BLUE, 100/100)
       3. Stockhorn (RED, 100/100)
```


**Resort-Level with Live Data:**
```bash
# Compare all resorts with live weather data
python main_resort_live.py all intermediate

# Compare specific resorts with live data (time blocks)
python main_resort_live.py val_thorens,zermatt intermediate

# Daily mode with live data
python main_resort_live.py all advanced daily

# Weekly mode with live data
python main_resort_live.py all intermediate weekly

# JSON output
python main_resort_live.py all intermediate weekly json
```

### Weekly Resort Recommendations

```
=== Weekly Ski Resort Recommendation ===

============================================================
Week: 2026-01-11 to 2026-01-17
============================================================
Confidence: MEDIUM

Top Resorts for the Week:

  1. Val Thorens, France (Score: 98/100)
     Conditions: Fresh snow (2cm), good overnight refreeze, temperatures warming.
     Average conditions over 7 days, 8 suitable pistes, altitude range 2300-3200m, top pistes averaging 100/100.
     Best Pistes for the Week:
       1. Cime Caron (RED, 100/100)
       2. Cascades (BLUE, 100/100)
       3. Moraine (GREEN, 100/100)

  2. Zermatt, Switzerland (Score: 94/100)
     Conditions: Fresh snow (2cm), good overnight refreeze, temperatures warming.
     Average conditions over 7 days, 7 suitable pistes, altitude range 2500-3800m, top pistes averaging 100/100.
     Best Pistes for the Week:
       1. Blauherd (BLUE, 100/100)
       2. Gornergrat (BLUE, 100/100)
       3. Stockhorn (RED, 100/100)
```


### Command Line Arguments

**Piste-Level Mode:**
```

### Weekly Resort Recommendations

```
=== Weekly Ski Resort Recommendation ===

============================================================
Week: 2026-01-11 to 2026-01-17
============================================================
Confidence: MEDIUM

Top Resorts for the Week:

  1. Val Thorens, France (Score: 98/100)
     Conditions: Fresh snow (2cm), good overnight refreeze, temperatures warming.
     Average conditions over 7 days, 8 suitable pistes, altitude range 2300-3200m, top pistes averaging 100/100.
     Best Pistes for the Week:
       1. Cime Caron (RED, 100/100)
       2. Cascades (BLUE, 100/100)
       3. Moraine (GREEN, 100/100)

  2. Zermatt, Switzerland (Score: 94/100)
     Conditions: Fresh snow (2cm), good overnight refreeze, temperatures warming.
     Average conditions over 7 days, 7 suitable pistes, altitude range 2500-3800m, top pistes averaging 100/100.
     Best Pistes for the Week:
       1. Blauherd (BLUE, 100/100)
       2. Gornergrat (BLUE, 100/100)
       3. Stockhorn (RED, 100/100)
```

python main.py [resort_id] [skill_level] [output_format]

Arguments:
  resort_id      : Resort identifier (val_thorens, zermatt, chamonix, courchevel, verbier, st_anton, silvretta_arena)
  skill_level    : Skier skill level (beginner, intermediate, advanced)
  output_format  : Output format (text or json)
```

### Weekly Resort Recommendations

```
=== Weekly Ski Resort Recommendation ===

============================================================
Week: 2026-01-11 to 2026-01-17
============================================================
Confidence: MEDIUM

Top Resorts for the Week:

  1. Val Thorens, France (Score: 98/100)
     Conditions: Fresh snow (2cm), good overnight refreeze, temperatures warming.
     Average conditions over 7 days, 8 suitable pistes, altitude range 2300-3200m, top pistes averaging 100/100.
     Best Pistes for the Week:
       1. Cime Caron (RED, 100/100)
       2. Cascades (BLUE, 100/100)
       3. Moraine (GREEN, 100/100)

  2. Zermatt, Switzerland (Score: 94/100)
     Conditions: Fresh snow (2cm), good overnight refreeze, temperatures warming.
     Average conditions over 7 days, 7 suitable pistes, altitude range 2500-3800m, top pistes averaging 100/100.
     Best Pistes for the Week:
       1. Blauherd (BLUE, 100/100)
       2. Gornergrat (BLUE, 100/100)
       3. Stockhorn (RED, 100/100)
```


**Resort-Level Mode:**
```

### Weekly Resort Recommendations

```
=== Weekly Ski Resort Recommendation ===

============================================================
Week: 2026-01-11 to 2026-01-17
============================================================
Confidence: MEDIUM

Top Resorts for the Week:

  1. Val Thorens, France (Score: 98/100)
     Conditions: Fresh snow (2cm), good overnight refreeze, temperatures warming.
     Average conditions over 7 days, 8 suitable pistes, altitude range 2300-3200m, top pistes averaging 100/100.
     Best Pistes for the Week:
       1. Cime Caron (RED, 100/100)
       2. Cascades (BLUE, 100/100)
       3. Moraine (GREEN, 100/100)

  2. Zermatt, Switzerland (Score: 94/100)
     Conditions: Fresh snow (2cm), good overnight refreeze, temperatures warming.
     Average conditions over 7 days, 7 suitable pistes, altitude range 2500-3800m, top pistes averaging 100/100.
     Best Pistes for the Week:
       1. Blauherd (BLUE, 100/100)
       2. Gornergrat (BLUE, 100/100)
       3. Stockhorn (RED, 100/100)
```

python main_resort.py [resort_selection] [skill_level] [mode] [output_format]

Arguments:
  resort_selection : 'all' (default) or comma-separated resort IDs (e.g., 'val_thorens,zermatt')
  skill_level      : Skier skill level (beginner, intermediate, advanced)
  mode             : 'time_blocks' (default, shows morning/late morning/afternoon), 
                     'daily' (24-hour aggregation), or 
                     'weekly' (7-day aggregation)
  output_format    : Output format (text or json)

Note: mode and output_format are optional. If only 3 arguments provided, the 3rd can be either mode or format.
```

### Weekly Resort Recommendations

```
=== Weekly Ski Resort Recommendation ===

============================================================
Week: 2026-01-11 to 2026-01-17
============================================================
Confidence: MEDIUM

Top Resorts for the Week:

  1. Val Thorens, France (Score: 98/100)
     Conditions: Fresh snow (2cm), good overnight refreeze, temperatures warming.
     Average conditions over 7 days, 8 suitable pistes, altitude range 2300-3200m, top pistes averaging 100/100.
     Best Pistes for the Week:
       1. Cime Caron (RED, 100/100)
       2. Cascades (BLUE, 100/100)
       3. Moraine (GREEN, 100/100)

  2. Zermatt, Switzerland (Score: 94/100)
     Conditions: Fresh snow (2cm), good overnight refreeze, temperatures warming.
     Average conditions over 7 days, 7 suitable pistes, altitude range 2500-3800m, top pistes averaging 100/100.
     Best Pistes for the Week:
       1. Blauherd (BLUE, 100/100)
       2. Gornergrat (BLUE, 100/100)
       3. Stockhorn (RED, 100/100)
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

### Weekly Resort Recommendations

```
=== Weekly Ski Resort Recommendation ===

============================================================
Week: 2026-01-11 to 2026-01-17
============================================================
Confidence: MEDIUM

Top Resorts for the Week:

  1. Val Thorens, France (Score: 98/100)
     Conditions: Fresh snow (2cm), good overnight refreeze, temperatures warming.
     Average conditions over 7 days, 8 suitable pistes, altitude range 2300-3200m, top pistes averaging 100/100.
     Best Pistes for the Week:
       1. Cime Caron (RED, 100/100)
       2. Cascades (BLUE, 100/100)
       3. Moraine (GREEN, 100/100)

  2. Zermatt, Switzerland (Score: 94/100)
     Conditions: Fresh snow (2cm), good overnight refreeze, temperatures warming.
     Average conditions over 7 days, 7 suitable pistes, altitude range 2500-3800m, top pistes averaging 100/100.
     Best Pistes for the Week:
       1. Blauherd (BLUE, 100/100)
       2. Gornergrat (BLUE, 100/100)
       3. Stockhorn (RED, 100/100)
```

/src
  /services         # External API clients (Open-Meteo)
  /snow_model       # Snow surface state modeling
  /scoring          # Piste scoring engine
  /recommendation   # Main recommendation engine (piste & resort)
  /data             # Resort and piste data
/tests              # Test suite
main.py             # Piste CLI with mock data
main_live.py        # Piste CLI with live API data
main_resort.py      # Resort comparison CLI with mock data
main_resort_live.py # Resort comparison CLI with live API data
```

### Weekly Resort Recommendations

```
=== Weekly Ski Resort Recommendation ===

============================================================
Week: 2026-01-11 to 2026-01-17
============================================================
Confidence: MEDIUM

Top Resorts for the Week:

  1. Val Thorens, France (Score: 98/100)
     Conditions: Fresh snow (2cm), good overnight refreeze, temperatures warming.
     Average conditions over 7 days, 8 suitable pistes, altitude range 2300-3200m, top pistes averaging 100/100.
     Best Pistes for the Week:
       1. Cime Caron (RED, 100/100)
       2. Cascades (BLUE, 100/100)
       3. Moraine (GREEN, 100/100)

  2. Zermatt, Switzerland (Score: 94/100)
     Conditions: Fresh snow (2cm), good overnight refreeze, temperatures warming.
     Average conditions over 7 days, 7 suitable pistes, altitude range 2500-3800m, top pistes averaging 100/100.
     Best Pistes for the Week:
       1. Blauherd (BLUE, 100/100)
       2. Gornergrat (BLUE, 100/100)
       3. Stockhorn (RED, 100/100)
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

### Weekly Resort Recommendations

```
=== Weekly Ski Resort Recommendation ===

============================================================
Week: 2026-01-11 to 2026-01-17
============================================================
Confidence: MEDIUM

Top Resorts for the Week:

  1. Val Thorens, France (Score: 98/100)
     Conditions: Fresh snow (2cm), good overnight refreeze, temperatures warming.
     Average conditions over 7 days, 8 suitable pistes, altitude range 2300-3200m, top pistes averaging 100/100.
     Best Pistes for the Week:
       1. Cime Caron (RED, 100/100)
       2. Cascades (BLUE, 100/100)
       3. Moraine (GREEN, 100/100)

  2. Zermatt, Switzerland (Score: 94/100)
     Conditions: Fresh snow (2cm), good overnight refreeze, temperatures warming.
     Average conditions over 7 days, 7 suitable pistes, altitude range 2500-3800m, top pistes averaging 100/100.
     Best Pistes for the Week:
       1. Blauherd (BLUE, 100/100)
       2. Gornergrat (BLUE, 100/100)
       3. Stockhorn (RED, 100/100)
```


## Data Sources

- **Weather**: [Open-Meteo API](https://open-meteo.com/) - Free, no API key required
- **Piste data**: Currently uses sample data; can be extended with OSM Overpass API
- **Elevation**: Altitudes from resort documentation

## Example Output

### Piste-Level Recommendations

```

### Weekly Resort Recommendations

```
=== Weekly Ski Resort Recommendation ===

============================================================
Week: 2026-01-11 to 2026-01-17
============================================================
Confidence: MEDIUM

Top Resorts for the Week:

  1. Val Thorens, France (Score: 98/100)
     Conditions: Fresh snow (2cm), good overnight refreeze, temperatures warming.
     Average conditions over 7 days, 8 suitable pistes, altitude range 2300-3200m, top pistes averaging 100/100.
     Best Pistes for the Week:
       1. Cime Caron (RED, 100/100)
       2. Cascades (BLUE, 100/100)
       3. Moraine (GREEN, 100/100)

  2. Zermatt, Switzerland (Score: 94/100)
     Conditions: Fresh snow (2cm), good overnight refreeze, temperatures warming.
     Average conditions over 7 days, 7 suitable pistes, altitude range 2500-3800m, top pistes averaging 100/100.
     Best Pistes for the Week:
       1. Blauherd (BLUE, 100/100)
       2. Gornergrat (BLUE, 100/100)
       3. Stockhorn (RED, 100/100)
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

### Weekly Resort Recommendations

```
=== Weekly Ski Resort Recommendation ===

============================================================
Week: 2026-01-11 to 2026-01-17
============================================================
Confidence: MEDIUM

Top Resorts for the Week:

  1. Val Thorens, France (Score: 98/100)
     Conditions: Fresh snow (2cm), good overnight refreeze, temperatures warming.
     Average conditions over 7 days, 8 suitable pistes, altitude range 2300-3200m, top pistes averaging 100/100.
     Best Pistes for the Week:
       1. Cime Caron (RED, 100/100)
       2. Cascades (BLUE, 100/100)
       3. Moraine (GREEN, 100/100)

  2. Zermatt, Switzerland (Score: 94/100)
     Conditions: Fresh snow (2cm), good overnight refreeze, temperatures warming.
     Average conditions over 7 days, 7 suitable pistes, altitude range 2500-3800m, top pistes averaging 100/100.
     Best Pistes for the Week:
       1. Blauherd (BLUE, 100/100)
       2. Gornergrat (BLUE, 100/100)
       3. Stockhorn (RED, 100/100)
```


### Resort-Level Recommendations

```

### Weekly Resort Recommendations

```
=== Weekly Ski Resort Recommendation ===

============================================================
Week: 2026-01-11 to 2026-01-17
============================================================
Confidence: MEDIUM

Top Resorts for the Week:

  1. Val Thorens, France (Score: 98/100)
     Conditions: Fresh snow (2cm), good overnight refreeze, temperatures warming.
     Average conditions over 7 days, 8 suitable pistes, altitude range 2300-3200m, top pistes averaging 100/100.
     Best Pistes for the Week:
       1. Cime Caron (RED, 100/100)
       2. Cascades (BLUE, 100/100)
       3. Moraine (GREEN, 100/100)

  2. Zermatt, Switzerland (Score: 94/100)
     Conditions: Fresh snow (2cm), good overnight refreeze, temperatures warming.
     Average conditions over 7 days, 7 suitable pistes, altitude range 2500-3800m, top pistes averaging 100/100.
     Best Pistes for the Week:
       1. Blauherd (BLUE, 100/100)
       2. Gornergrat (BLUE, 100/100)
       3. Stockhorn (RED, 100/100)
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

### Weekly Resort Recommendations

```
=== Weekly Ski Resort Recommendation ===

============================================================
Week: 2026-01-11 to 2026-01-17
============================================================
Confidence: MEDIUM

Top Resorts for the Week:

  1. Val Thorens, France (Score: 98/100)
     Conditions: Fresh snow (2cm), good overnight refreeze, temperatures warming.
     Average conditions over 7 days, 8 suitable pistes, altitude range 2300-3200m, top pistes averaging 100/100.
     Best Pistes for the Week:
       1. Cime Caron (RED, 100/100)
       2. Cascades (BLUE, 100/100)
       3. Moraine (GREEN, 100/100)

  2. Zermatt, Switzerland (Score: 94/100)
     Conditions: Fresh snow (2cm), good overnight refreeze, temperatures warming.
     Average conditions over 7 days, 7 suitable pistes, altitude range 2500-3800m, top pistes averaging 100/100.
     Best Pistes for the Week:
       1. Blauherd (BLUE, 100/100)
       2. Gornergrat (BLUE, 100/100)
       3. Stockhorn (RED, 100/100)
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