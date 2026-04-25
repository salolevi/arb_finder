"""Canonical alias dictionaries for Argentine football.

Keys are (operator_brand, raw_name_as_scraped).
Values are stable slugs used as canonical IDs throughout the system.

Extend these dictionaries as new operators are onboarded and scraping reveals
real spelling variations. Never remove an existing entry — only add or remap.
"""

# (operator_brand, raw_competition_name) -> canonical_competition_id
COMPETITION_ALIASES: dict[tuple[str, str], str] = {
    # ── bplay ────────────────────────────────────────────────────────────────
    ("bplay", "Liga Profesional"): "arg_primera_division",
    ("bplay", "Liga Prof."): "arg_primera_division",
    ("bplay", "Copa Argentina"): "arg_copa_argentina",
    ("bplay", "Copa de la Liga"): "arg_copa_de_la_liga",
    ("bplay", "Primera Nacional"): "arg_primera_nacional",
    # ── Betsson ───────────────────────────────────────────────────────────────
    ("betsson", "Liga Profesional"): "arg_primera_division",
    ("betsson", "Primera División"): "arg_primera_division",
    ("betsson", "Copa Argentina"): "arg_copa_argentina",
    ("betsson", "Copa de la Liga Profesional"): "arg_copa_de_la_liga",
    # ── Betano ────────────────────────────────────────────────────────────────
    ("betano", "Argentina - Liga Profesional"): "arg_primera_division",
    ("betano", "Argentina - Copa Argentina"): "arg_copa_argentina",
    ("betano", "Argentina - Copa de la Liga"): "arg_copa_de_la_liga",
    ("betano", "Argentina - Primera Nacional"): "arg_primera_nacional",
    # ── Jugadón ───────────────────────────────────────────────────────────────
    ("jugadon", "Liga Profesional"): "arg_primera_division",
    ("jugadon", "Copa Argentina"): "arg_copa_argentina",
    ("jugadon", "Copa de la Liga"): "arg_copa_de_la_liga",
}

# (operator_brand, raw_team_name) -> canonical_team_id
TEAM_ALIASES: dict[tuple[str, str], str] = {
    # ── River Plate ───────────────────────────────────────────────────────────
    ("bplay", "River Plate"): "river_plate",
    ("bplay", "River"): "river_plate",
    ("betsson", "River Plate"): "river_plate",
    ("betsson", "River"): "river_plate",
    ("betano", "River Plate"): "river_plate",
    ("jugadon", "River Plate"): "river_plate",
    # ── Boca Juniors ──────────────────────────────────────────────────────────
    ("bplay", "Boca Juniors"): "boca_juniors",
    ("bplay", "Boca"): "boca_juniors",
    ("betsson", "Boca Juniors"): "boca_juniors",
    ("betano", "Boca Juniors"): "boca_juniors",
    ("jugadon", "Boca Juniors"): "boca_juniors",
    # ── Racing Club ───────────────────────────────────────────────────────────
    ("bplay", "Racing Club"): "racing_club",
    ("bplay", "Racing"): "racing_club",
    ("betsson", "Racing Club"): "racing_club",
    ("betano", "Racing Club"): "racing_club",
    ("jugadon", "Racing Club"): "racing_club",
    # ── Independiente ─────────────────────────────────────────────────────────
    ("bplay", "Independiente"): "independiente",
    ("betsson", "Independiente"): "independiente",
    ("betano", "Independiente"): "independiente",
    ("jugadon", "Independiente"): "independiente",
    # ── San Lorenzo ───────────────────────────────────────────────────────────
    ("bplay", "San Lorenzo"): "san_lorenzo",
    ("betsson", "San Lorenzo"): "san_lorenzo",
    ("betano", "San Lorenzo"): "san_lorenzo",
    ("jugadon", "San Lorenzo"): "san_lorenzo",
    # ── Huracán ───────────────────────────────────────────────────────────────
    ("bplay", "Huracán"): "huracan",
    ("bplay", "Huracan"): "huracan",
    ("betsson", "Huracán"): "huracan",
    ("betano", "Huracán"): "huracan",
    # ── Lanús ─────────────────────────────────────────────────────────────────
    ("bplay", "Lanús"): "lanus",
    ("bplay", "Lanus"): "lanus",
    ("betsson", "Lanús"): "lanus",
    ("betano", "Lanús"): "lanus",
    # ── Vélez Sársfield ───────────────────────────────────────────────────────
    ("bplay", "Vélez Sársfield"): "velez_sarsfield",
    ("bplay", "Velez"): "velez_sarsfield",
    ("bplay", "Vélez"): "velez_sarsfield",
    ("betsson", "Vélez Sársfield"): "velez_sarsfield",
    ("betano", "Vélez Sársfield"): "velez_sarsfield",
    # ── Estudiantes (LP) ──────────────────────────────────────────────────────
    ("bplay", "Estudiantes"): "estudiantes_lp",
    ("bplay", "Estudiantes (LP)"): "estudiantes_lp",
    ("betsson", "Estudiantes"): "estudiantes_lp",
    ("betano", "Estudiantes"): "estudiantes_lp",
    # ── Gimnasia y Esgrima (LP) ───────────────────────────────────────────────
    ("bplay", "Gimnasia"): "gimnasia_lp",
    ("bplay", "Gimnasia y Esgrima"): "gimnasia_lp",
    ("betsson", "Gimnasia y Esgrima LP"): "gimnasia_lp",
    ("betano", "Gimnasia La Plata"): "gimnasia_lp",
    # ── Talleres (CBA) ────────────────────────────────────────────────────────
    ("bplay", "Talleres"): "talleres_cba",
    ("bplay", "Talleres (CBA)"): "talleres_cba",
    ("betsson", "Talleres"): "talleres_cba",
    ("betano", "Talleres"): "talleres_cba",
    # ── Belgrano (CBA) ────────────────────────────────────────────────────────
    ("bplay", "Belgrano"): "belgrano_cba",
    ("bplay", "Belgrano (CBA)"): "belgrano_cba",
    ("betsson", "Belgrano"): "belgrano_cba",
    ("betano", "Belgrano"): "belgrano_cba",
    # ── Rosario Central ───────────────────────────────────────────────────────
    ("bplay", "Rosario Central"): "rosario_central",
    ("betsson", "Rosario Central"): "rosario_central",
    ("betano", "Rosario Central"): "rosario_central",
    ("jugadon", "Rosario Central"): "rosario_central",
    # ── Newell's Old Boys ─────────────────────────────────────────────────────
    ("bplay", "Newell's Old Boys"): "newells_old_boys",
    ("bplay", "Newells"): "newells_old_boys",
    ("betsson", "Newell's Old Boys"): "newells_old_boys",
    ("betano", "Newell's Old Boys"): "newells_old_boys",
    # ── Godoy Cruz ────────────────────────────────────────────────────────────
    ("bplay", "Godoy Cruz"): "godoy_cruz",
    ("betsson", "Godoy Cruz"): "godoy_cruz",
    ("betano", "Godoy Cruz"): "godoy_cruz",
    # ── Colón ─────────────────────────────────────────────────────────────────
    ("bplay", "Colón"): "colon_sf",
    ("bplay", "Colon"): "colon_sf",
    ("betsson", "Colón"): "colon_sf",
    ("betano", "Colón"): "colon_sf",
    # ── Unión (SF) ────────────────────────────────────────────────────────────
    ("bplay", "Unión"): "union_sf",
    ("bplay", "Union"): "union_sf",
    ("betsson", "Unión"): "union_sf",
    ("betano", "Unión"): "union_sf",
    # ── Defensa y Justicia ────────────────────────────────────────────────────
    ("bplay", "Defensa y Justicia"): "defensa_y_justicia",
    ("betsson", "Defensa y Justicia"): "defensa_y_justicia",
    ("betano", "Defensa y Justicia"): "defensa_y_justicia",
    # ── Argentinos Juniors ────────────────────────────────────────────────────
    ("bplay", "Argentinos Juniors"): "argentinos_juniors",
    ("bplay", "Argentinos"): "argentinos_juniors",
    ("betsson", "Argentinos Juniors"): "argentinos_juniors",
    ("betano", "Argentinos Juniors"): "argentinos_juniors",
    # ── Banfield ──────────────────────────────────────────────────────────────
    ("bplay", "Banfield"): "banfield",
    ("betsson", "Banfield"): "banfield",
    ("betano", "Banfield"): "banfield",
    # ── Tigre ─────────────────────────────────────────────────────────────────
    ("bplay", "Tigre"): "tigre",
    ("betsson", "Tigre"): "tigre",
    ("betano", "Tigre"): "tigre",
    # ── Atlético Tucumán ──────────────────────────────────────────────────────
    ("bplay", "Atlético Tucumán"): "atletico_tucuman",
    ("bplay", "At. Tucumán"): "atletico_tucuman",
    ("betsson", "Atlético Tucumán"): "atletico_tucuman",
    ("betano", "Atlético Tucumán"): "atletico_tucuman",
    # ── Platense ──────────────────────────────────────────────────────────────
    ("bplay", "Platense"): "platense",
    ("betsson", "Platense"): "platense",
    ("betano", "Platense"): "platense",
    # ── Instituto (CBA) ───────────────────────────────────────────────────────
    ("bplay", "Instituto"): "instituto_cba",
    ("betsson", "Instituto"): "instituto_cba",
    ("betano", "Instituto"): "instituto_cba",
    # ── Sarmiento (J) ─────────────────────────────────────────────────────────
    ("bplay", "Sarmiento"): "sarmiento_junin",
    ("betsson", "Sarmiento"): "sarmiento_junin",
    ("betano", "Sarmiento"): "sarmiento_junin",
    # ── Central Córdoba (SdE) ─────────────────────────────────────────────────
    ("bplay", "Central Córdoba"): "central_cordoba_sde",
    ("bplay", "Cen. Córdoba"): "central_cordoba_sde",
    ("betsson", "Central Córdoba"): "central_cordoba_sde",
    ("betano", "Central Córdoba"): "central_cordoba_sde",
    # ── Barracas Central ──────────────────────────────────────────────────────
    ("bplay", "Barracas Central"): "barracas_central",
    ("betsson", "Barracas Central"): "barracas_central",
    # ── Deportivo Riestra ─────────────────────────────────────────────────────
    ("bplay", "Riestra"): "deportivo_riestra",
    ("bplay", "Deportivo Riestra"): "deportivo_riestra",
    ("betsson", "Riestra"): "deportivo_riestra",
}
