from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import csv


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Score all songs and return top k recommendations."""
        scored_songs = [
            (song, self._score_song(user, song))
            for song in self.songs
        ]
        # Sort by score descending
        scored_songs.sort(key=lambda x: x[1], reverse=True)
        return [song for song, score in scored_songs[:k]]

    def _score_song(self, user: UserProfile, song: Song) -> float:
        """Calculate a score for how well a song matches the user's preferences."""
        score = 0.0

        # Genre match (weight: 3.0)
        if song.genre.lower() == user.favorite_genre.lower():
            score += 3.0

        # Mood match (weight: 2.5)
        if song.mood.lower() == user.favorite_mood.lower():
            score += 2.5

        # Energy proximity (weight: 2.0) - penalty for difference
        energy_diff = abs(song.energy - user.target_energy)
        energy_score = 2.0 * (1.0 - energy_diff)
        score += max(0, energy_score)

        # Acoustic preference (weight: 1.5)
        if user.likes_acoustic and song.acousticness > 0.5:
            score += 1.5
        elif not user.likes_acoustic and song.acousticness <= 0.5:
            score += 1.5

        return score

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Generate a natural language explanation for why a song is recommended."""
        reasons = []

        if song.genre.lower() == user.favorite_genre.lower():
            reasons.append(f"matches your {song.genre} preference")

        if song.mood.lower() == user.favorite_mood.lower():
            reasons.append(f"has the {song.mood} mood you enjoy")

        energy_diff = abs(song.energy - user.target_energy)
        if energy_diff < 0.2:
            reasons.append(f"matches your energy preference ({song.energy:.2f})")

        if user.likes_acoustic and song.acousticness > 0.5:
            reasons.append("features acoustic elements you like")

        if not reasons:
            reasons.append(f"combines {song.genre} and {song.mood} qualities")

        return "Because it " + ", ".join(reasons)


def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    print(f"Loading songs from {csv_path}...")
    songs = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert numeric fields
                song = {
                    'id': int(row['id']),
                    'title': row['title'],
                    'artist': row['artist'],
                    'genre': row['genre'],
                    'mood': row['mood'],
                    'energy': float(row['energy']),
                    'tempo_bpm': float(row['tempo_bpm']),
                    'valence': float(row['valence']),
                    'danceability': float(row['danceability']),
                    'acousticness': float(row['acousticness']),
                }
                songs.append(song)
    except FileNotFoundError:
        print(f"Error: Could not find {csv_path}")
        return []

    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py
    Returns: (score, reasons)
    """
    score = 0.0
    reasons = []

    # Genre match (weight: 3.0)
    if song['genre'].lower() == user_prefs.get('genre', '').lower():
        score += 3.0
        reasons.append(f"matches your {song['genre']} preference")

    # Mood match (weight: 2.5)
    if song['mood'].lower() == user_prefs.get('mood', '').lower():
        score += 2.5
        reasons.append(f"has the {song['mood']} mood you enjoy")

    # Energy proximity (weight: 2.0)
    target_energy = user_prefs.get('energy', 0.5)
    energy_diff = abs(float(song['energy']) - float(target_energy))
    energy_score = 2.0 * (1.0 - energy_diff)
    score += max(0, energy_score)
    if energy_diff < 0.2:
        reasons.append(f"matches your energy preference")

    # Danceability bonus
    if float(song['danceability']) > 0.7:
        score += 0.5
        reasons.append("is very danceable")

    # Valence (positivity) bonus
    if float(song['valence']) > 0.7:
        score += 0.5
        reasons.append("has an uplifting vibe")

    if not reasons:
        reasons.append(f"is a {song['genre']} track with {song['mood']} qualities")

    return (score, reasons)


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Returns: list of (song_dict, score, explanation)
    """
    # Score all songs
    scored_songs = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = "Because it " + ", ".join(reasons)
        scored_songs.append((song, score, explanation))

    # Sort by score descending and return top k
    scored_songs.sort(key=lambda x: x[1], reverse=True)
    return scored_songs[:k]
