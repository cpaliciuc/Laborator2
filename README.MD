# Laborator 2 - Sistem de recomandari muzicale

## Dataset

Am folosit un dataset de melodii de pe Spotify, care include informatii
despre artisti, albume, genuri muzicale si caracteristici audio. Dataset-ul initial continea 89741 de intrari, astfel am extras cate 60 de melodii pentru fiecare dintre cele 114 genuri muzicale, rezultand un dataset cu 6840 de melodii.

Link dataset: https://www.kaggle.com/datasets/maharshipandya/-spotify-tracks-dataset

Toate inregistrarile conțin proprietati despre artist, melodie si
caracteristicile audio.

## Proprietati

| Proprietate      | Tip     |
|------------------|---------|
| artists          | string  |
| album_name       | string  |
| track_name       | string  |
| popularity       | int     |
| duration_ms      | int     |
| explicit         | boolean |
| danceability     | double  |
| energy           | double  |
| key              | int     |
| loudness         | double  |
| mode             | int     |
| speechiness      | double  |
| acousticness     | double  |
| instrumentalness | double  |
| liveness         | double  |
| valence          | double  |
| tempo            | double  |
| time_signature   | int     |
| track_genre      | string  |

## Incarcarea item-urilor in Recombee

Item-urile sunt incarcate cu ajutorul scriptului `recombee_items.py`.
Pentru fiecare melodie, valoarea din coloana `track_id` este folosita ca
`itemId`, iar cele 19 proprietati sunt trimise prin cereri `Batch` de cate
100 de item-uri. Datasetul contine 6840 de randuri, dintre care 6719 au
un `track_id` unic; duplicatele sunt ignorate inaintea incarcarii pentru a
evita suprascrierea item-urilor.
