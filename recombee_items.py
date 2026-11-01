import os
from pathlib import Path

import dotenv
import pandas as pd
from recombee_api_client.api_client import RecombeeClient, Region
from recombee_api_client.api_requests import Batch, SetItemValues
from recombee_api_client.exceptions import APIException


PROJECT_DIR = Path(__file__).resolve().parent
dotenv.load_dotenv(PROJECT_DIR / ".env")

DB_NAME = os.getenv("DB_NAME")
PRIVATE_TOKEN = os.getenv("PRIVATE_TOKEN")
REGION_NAME = os.getenv("REGION", "").strip().upper().replace("-", "_")

if not DB_NAME or not PRIVATE_TOKEN:
    raise ValueError("DB_NAME si PRIVATE_TOKEN trebuie definite in fisierul .env.")

try:
    REGION = Region[REGION_NAME] if REGION_NAME else None
except KeyError as error:
    accepted_regions = ", ".join(
        region.name.lower().replace("_", "-") for region in Region
    )
    raise ValueError(
        f"Regiune Recombee invalida: '{REGION_NAME}'. "
        f"Folositi una dintre: {accepted_regions}."
    ) from error

client = RecombeeClient(DB_NAME, PRIVATE_TOKEN, region=REGION)
PATH_DATASET = PROJECT_DIR / "dataset.csv"
BATCH_SIZE = 100

PROPERTY_COLUMNS = (
    "artists",
    "album_name",
    "track_name",
    "popularity",
    "duration_ms",
    "explicit",
    "danceability",
    "energy",
    "key",
    "loudness",
    "mode",
    "speechiness",
    "acousticness",
    "instrumentalness",
    "liveness",
    "valence",
    "tempo",
    "time_signature",
    "track_genre",
)


def build_properties(row: pd.Series) -> dict:
    """Converteste un rand CSV in proprietati compatibile cu Recombee."""
    return {
        "artists": str(row["artists"]),
        "album_name": str(row["album_name"]),
        "track_name": str(row["track_name"]),
        "popularity": int(row["popularity"]),
        "duration_ms": int(row["duration_ms"]),
        "explicit": bool(row["explicit"]),
        "danceability": float(row["danceability"]),
        "energy": float(row["energy"]),
        "key": int(row["key"]),
        "loudness": float(row["loudness"]),
        "mode": int(row["mode"]),
        "speechiness": float(row["speechiness"]),
        "acousticness": float(row["acousticness"]),
        "instrumentalness": float(row["instrumentalness"]),
        "liveness": float(row["liveness"]),
        "valence": float(row["valence"]),
        "tempo": float(row["tempo"]),
        "time_signature": int(row["time_signature"]),
        "track_genre": str(row["track_genre"]),
    }


def send_batch(requests: list[SetItemValues], batch_number: int) -> None:
    """Trimite un lot si raporteaza explicit erorile API."""
    try:
        client.send(Batch(requests))
    except APIException as error:
        raise RuntimeError(
            f"Trimiterea lotului {batch_number} ({len(requests)} item-uri) a esuat: "
            f"{error}"
        ) from error
    print(f"Lotul {batch_number} trimis: {len(requests)} item-uri.")


def send_items() -> None:
    """Citeste datasetul si trimite itemii in loturi catre Recombee."""
    if not PATH_DATASET.exists():
        raise FileNotFoundError(f"Datasetul nu a fost gasit: {PATH_DATASET}")

    df = pd.read_csv(PATH_DATASET)
    required_columns = {"track_id", *PROPERTY_COLUMNS}
    missing_columns = required_columns.difference(df.columns)
    if missing_columns:
        raise ValueError(
            f"Lipsesc coloanele necesare din dataset: {sorted(missing_columns)}"
        )

    if df[list(required_columns)].isna().any().any():
        raise ValueError("Datasetul contine valori lipsa in coloanele necesare.")

    initial_count = len(df)
    df = df.drop_duplicates(subset=["track_id"], keep="first").reset_index(drop=True)
    duplicate_count = initial_count - len(df)
    if duplicate_count:
        print(
            f"Au fost ignorate {duplicate_count} randuri cu track_id duplicat. "
            f"Se trimit {len(df)} item-uri unice."
        )

    requests: list[SetItemValues] = []
    batch_number = 0
    for _, row in df.iterrows():
        item_id = str(row["track_id"])
        requests.append(
            SetItemValues(
                item_id,
                build_properties(row),
                cascade_create=True,
            )
        )

        if len(requests) == BATCH_SIZE:
            batch_number += 1
            send_batch(requests, batch_number)
            requests = []

    if requests:
        batch_number += 1
        send_batch(requests, batch_number)

    print(f"Toate cele {len(df)} de item-uri au fost trimise cu succes.")


if __name__ == "__main__":
    send_items()
