"""Sample resort data with coordinates and pistes."""

from src.models import Resort, Piste, Difficulty, Aspect


# Resort coordinates and basic information
RESORTS = {
    "val_thorens": {
        "id": "val_thorens",
        "name": "Val Thorens",
        "country": "France",
        "latitude": 45.2974,
        "longitude": 6.5803,
    },
    "zermatt": {
        "id": "zermatt",
        "name": "Zermatt",
        "country": "Switzerland",
        "latitude": 45.9763,
        "longitude": 7.6586,
    },
    "chamonix": {
        "id": "chamonix",
        "name": "Chamonix",
        "country": "France",
        "latitude": 45.9237,
        "longitude": 6.8694,
    },
    "courchevel": {
        "id": "courchevel",
        "name": "Courchevel",
        "country": "France",
        "latitude": 45.4153,
        "longitude": 6.6347,
    },
    "verbier": {
        "id": "verbier",
        "name": "Verbier",
        "country": "Switzerland",
        "latitude": 46.0964,
        "longitude": 7.2281,
    },
    "st_anton": {
        "id": "st_anton",
        "name": "St. Anton",
        "country": "Austria",
        "latitude": 47.1275,
        "longitude": 10.2617,
    },
}


def get_sample_pistes(resort_id: str) -> list:
    """Get sample pistes for a resort.
    
    In a real implementation, this would fetch from OSM Overpass API.
    For now, we return representative sample pistes.
    """
    if resort_id == "val_thorens":
        return [
            Piste(
                id="vt_1",
                name="Cime Caron",
                difficulty=Difficulty.RED,
                altitude_min=2800,
                altitude_max=3200,
                aspect=Aspect.N,
                groomed=True,
                snowmaking=False,
            ),
            Piste(
                id="vt_2",
                name="Cascades",
                difficulty=Difficulty.BLUE,
                altitude_min=2600,
                altitude_max=2900,
                aspect=Aspect.E,
                groomed=True,
                snowmaking=True,
            ),
            Piste(
                id="vt_3",
                name="Moraine",
                difficulty=Difficulty.GREEN,
                altitude_min=2300,
                altitude_max=2500,
                aspect=Aspect.SE,
                groomed=True,
                snowmaking=True,
            ),
            Piste(
                id="vt_4",
                name="Grand Fond",
                difficulty=Difficulty.BLACK,
                altitude_min=2500,
                altitude_max=3000,
                aspect=Aspect.NW,
                groomed=True,
                snowmaking=False,
            ),
            Piste(
                id="vt_5",
                name="Plein Sud",
                difficulty=Difficulty.RED,
                altitude_min=2400,
                altitude_max=2700,
                aspect=Aspect.S,
                groomed=True,
                snowmaking=True,
            ),
        ]
    elif resort_id == "zermatt":
        return [
            Piste(
                id="zm_1",
                name="Plateau Rosa",
                difficulty=Difficulty.BLUE,
                altitude_min=3400,
                altitude_max=3800,
                aspect=Aspect.N,
                groomed=True,
                snowmaking=False,
            ),
            Piste(
                id="zm_2",
                name="Stockhorn",
                difficulty=Difficulty.RED,
                altitude_min=3200,
                altitude_max=3400,
                aspect=Aspect.E,
                groomed=True,
                snowmaking=False,
            ),
            Piste(
                id="zm_3",
                name="Blauherd",
                difficulty=Difficulty.BLUE,
                altitude_min=2500,
                altitude_max=2800,
                aspect=Aspect.SE,
                groomed=True,
                snowmaking=True,
            ),
            Piste(
                id="zm_4",
                name="Triftji",
                difficulty=Difficulty.BLACK,
                altitude_min=2900,
                altitude_max=3300,
                aspect=Aspect.N,
                groomed=False,
                snowmaking=False,
            ),
        ]
    elif resort_id == "chamonix":
        return [
            Piste(
                id="ch_1",
                name="Verte",
                difficulty=Difficulty.GREEN,
                altitude_min=1800,
                altitude_max=2000,
                aspect=Aspect.N,
                groomed=True,
                snowmaking=True,
            ),
            Piste(
                id="ch_2",
                name="Les Planards",
                difficulty=Difficulty.BLUE,
                altitude_min=1900,
                altitude_max=2200,
                aspect=Aspect.NE,
                groomed=True,
                snowmaking=True,
            ),
            Piste(
                id="ch_3",
                name="Grands Montets",
                difficulty=Difficulty.RED,
                altitude_min=2400,
                altitude_max=3200,
                aspect=Aspect.N,
                groomed=True,
                snowmaking=False,
            ),
        ]
    elif resort_id == "courchevel":
        return [
            Piste(
                id="cv_1",
                name="Bellecôte",
                difficulty=Difficulty.BLUE,
                altitude_min=2700,
                altitude_max=3000,
                aspect=Aspect.N,
                groomed=True,
                snowmaking=True,
            ),
            Piste(
                id="cv_2",
                name="Saulire",
                difficulty=Difficulty.RED,
                altitude_min=2500,
                altitude_max=2700,
                aspect=Aspect.E,
                groomed=True,
                snowmaking=True,
            ),
            Piste(
                id="cv_3",
                name="Chanrossa",
                difficulty=Difficulty.BLACK,
                altitude_min=2300,
                altitude_max=2600,
                aspect=Aspect.S,
                groomed=True,
                snowmaking=False,
            ),
        ]
    elif resort_id == "verbier":
        return [
            Piste(
                id="vb_1",
                name="Mont Fort",
                difficulty=Difficulty.RED,
                altitude_min=2800,
                altitude_max=3300,
                aspect=Aspect.N,
                groomed=True,
                snowmaking=False,
            ),
            Piste(
                id="vb_2",
                name="Savoleyres",
                difficulty=Difficulty.BLUE,
                altitude_min=2200,
                altitude_max=2400,
                aspect=Aspect.W,
                groomed=True,
                snowmaking=True,
            ),
            Piste(
                id="vb_3",
                name="Attelas",
                difficulty=Difficulty.RED,
                altitude_min=2400,
                altitude_max=2700,
                aspect=Aspect.SE,
                groomed=True,
                snowmaking=True,
            ),
        ]
    elif resort_id == "st_anton":
        return [
            Piste(
                id="sa_1",
                name="Valluga",
                difficulty=Difficulty.RED,
                altitude_min=2500,
                altitude_max=2800,
                aspect=Aspect.N,
                groomed=True,
                snowmaking=False,
            ),
            Piste(
                id="sa_2",
                name="Galzig",
                difficulty=Difficulty.BLUE,
                altitude_min=2000,
                altitude_max=2300,
                aspect=Aspect.E,
                groomed=True,
                snowmaking=True,
            ),
            Piste(
                id="sa_3",
                name="Schindler",
                difficulty=Difficulty.BLACK,
                altitude_min=2200,
                altitude_max=2650,
                aspect=Aspect.NE,
                groomed=True,
                snowmaking=False,
            ),
        ]
    else:
        return []


def get_resort(resort_id: str) -> Resort:
    """Get a resort with sample pistes."""
    if resort_id not in RESORTS:
        raise ValueError(f"Unknown resort: {resort_id}")
    
    resort_data = RESORTS[resort_id]
    pistes = get_sample_pistes(resort_id)
    
    return Resort(
        id=resort_data["id"],
        name=resort_data["name"],
        country=resort_data["country"],
        latitude=resort_data["latitude"],
        longitude=resort_data["longitude"],
        pistes=pistes,
    )


def list_resorts() -> list:
    """List all available resorts."""
    return [
        {"id": r["id"], "name": r["name"], "country": r["country"]}
        for r in RESORTS.values()
    ]
