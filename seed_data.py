#!/usr/bin/env python3
import sqlite3
from datetime import datetime
import json
import os

# Sample glazes data for the demo user
sample_glazes = [
    {
        "name": "Celadon Green",
        "cone": "10",
        "atmosphere": "reduction",
        "color": "green",
        "surface": "smooth",
        "transparency": "transparent",
        "base_type": "transparent",
        "notes": "Beautiful jade-like green. Best over carved surfaces."
    },
    {
        "name": "Temmoku",
        "cone": "10",
        "atmosphere": "reduction",
        "color": "brown",
        "surface": "smooth",
        "transparency": "semi-opaque",
        "base_type": "gloss",
        "notes": "Classic brown-black with amber breaks. Thicker for darker."
    },
    {
        "name": "Chun Blue",
        "cone": "10",
        "atmosphere": "reduction",
        "color": "blue",
        "surface": "smooth",
        "transparency": "transparent",
        "base_type": "transparent",
        "notes": "Pale blue with opalescent quality. Subtle and elegant."
    },
    {
        "name": "Shino White",
        "cone": "10",
        "atmosphere": "reduction",
        "color": "white",
        "surface": "textured",
        "transparency": "opaque",
        "base_type": "matte",
        "notes": "Carbon trap shino with orange-red flashes."
    },
    {
        "name": "Copper Red",
        "cone": "10",
        "atmosphere": "reduction",
        "color": "red",
        "surface": "smooth",
        "transparency": "semi-opaque",
        "base_type": "gloss",
        "notes": "Oxblood red. Requires heavy reduction."
    },
    {
        "name": "Matte White",
        "cone": "6",
        "atmosphere": "oxidation",
        "color": "white",
        "surface": "smooth",
        "transparency": "opaque",
        "base_type": "matte",
        "notes": "Soft matte white. Great for electric kilns."
    },
    {
        "name": "Glossy Turquoise",
        "cone": "6",
        "atmosphere": "oxidation",
        "color": "turquoise",
        "surface": "smooth",
        "transparency": "semi-opaque",
        "base_type": "gloss",
        "notes": "Bright turquoise with copper. Electric kiln friendly."
    },
    {
        "name": "Honey Amber",
        "cone": "6",
        "atmosphere": "oxidation",
        "color": "amber",
        "surface": "smooth",
        "transparency": "transparent",
        "base_type": "gloss",
        "notes": "Warm amber from iron. Reliable in oxidation."
    },
    {
        "name": "Forest Green",
        "cone": "6",
        "atmosphere": "oxidation",
        "color": "green",
        "surface": "smooth",
        "transparency": "semi-opaque",
        "base_type": "gloss",
        "notes": "Deep forest green. Copper-based formulation."
    },
    {
        "name": "Satin Black",
        "cone": "6",
        "atmosphere": "oxidation",
        "color": "black",
        "surface": "smooth",
        "transparency": "opaque",
        "base_type": "matte",
        "notes": "Satin black with subtle sheen. Great for contrast."
    },
]

DEMO_USER_ID = "demo-user-001"

def get_db():
    """Get database connection."""
    db_path = 'glazelab.db'
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    else:
        print(f"Database not found at {db_path}")
        return None

def add_samples():
    conn = get_db()
    if not conn:
        print("Could not connect to database")
        return False

    try:
        cursor = conn.cursor()

        # Check if demo user already has glazes
        cursor.execute("SELECT COUNT(*) FROM glazes WHERE user_id = ?", (DEMO_USER_ID,))
        count = cursor.fetchone()[0]

        if count > 0:
            print(f"Demo user already has {count} glazes")
            return True

        # Add sample glazes
        for glaze in sample_glazes:
            cursor.execute('''
                INSERT INTO glazes (user_id, name, cone, atmosphere, color, surface, transparency, base_type, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                DEMO_USER_ID,
                glaze['name'],
                glaze['cone'],
                glaze['atmosphere'],
                glaze['color'],
                glaze['surface'],
                glaze['transparency'],
                glaze['base_type'],
                glaze['notes']
            ))

        conn.commit()
        print(f"Added {len(sample_glazes)} sample glazes to database")

        # Verify
        cursor.execute("SELECT name, cone, color FROM glazes WHERE user_id = ? LIMIT 5", (DEMO_USER_ID,))
        rows = cursor.fetchall()
        print("Sample glazes:")
        for row in rows:
            print(f"  - {row[0]} (Cone {row[1]}, {row[2]})")

        return True

    except Exception as e:
        print(f"Error seeding database: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("Seeding database with sample glazes...")
    add_samples()
    print("Done!")
