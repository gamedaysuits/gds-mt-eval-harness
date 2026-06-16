#!/usr/bin/env python3
"""
Build tree-data.js for the Champollion Language Family Tree visualization.

Outputs TWO datasets:
  1. window.TREE_BACKBONE — The 519-node rosetta phylogeny (initial view).
     This is the hand-curated deep tree that creates the beautiful cone shape.
  2. window.TREE_EXPANSIONS — Glottolog languages keyed by their rosetta
     parent ID. Loaded on demand when users click to expand a family.

Why split: The backbone (519 nodes) renders beautifully with TubeGeometry
branches and glass nodes. Showing all 2,400 at once kills both aesthetics
and performance. Progressive disclosure is the answer.
"""

import json
import re
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LANG_TREE_PATH = os.path.join(SCRIPT_DIR, '..', '..', '..', '..',
                               'cli', 'shared', 'language-cards', 'language-tree.json')
ROSETTA_PATH = os.path.join(SCRIPT_DIR, '..', '..', '..', '..',
                             'marketing', 'rosetta-homepage-mock.html')
OUTPUT_PATH = os.path.join(SCRIPT_DIR, 'tree-data.js')


# ── Rosetta TREE parser ──
# Parses [id, name, parentId, date, status, code?] entries from the HTML.
def extract_rosetta_tree(html_path):
    """Parse window.TREE entries line-by-line from the rosetta mock."""
    with open(html_path, 'r') as f:
        content = f.read()

    nodes = []
    for line in content.split('\n'):
        line = line.strip()
        if not line.startswith('['):
            continue
        line = line.rstrip(',').strip()
        if not line.endswith(']'):
            continue

        try:
            inner = line[1:-1].strip()

            # ID (first quoted string)
            m = re.match(r"'([^']+)',\s*", inner)
            if not m:
                continue
            node_id = m.group(1)
            rest = inner[m.end():]

            # Name (single or double quoted — double quotes for names with apostrophes)
            if rest.startswith('"'):
                end_q = rest.index('"', 1)
                name = rest[1:end_q]
                rest = rest[end_q+1:].lstrip(',').strip()
            elif rest.startswith("'"):
                end_q = rest.index("'", 1)
                name = rest[1:end_q]
                rest = rest[end_q+1:].lstrip(',').strip()
            else:
                continue

            # Parent
            rest = rest.lstrip(',').strip()
            if rest.startswith('null'):
                parent_id = None
                rest = rest[4:].lstrip(',').strip()
            elif rest.startswith("'"):
                end_q = rest.index("'", 1)
                parent_id = rest[1:end_q]
                rest = rest[end_q+1:].lstrip(',').strip()
            elif rest.startswith('"'):
                end_q = rest.index('"', 1)
                parent_id = rest[1:end_q]
                rest = rest[end_q+1:].lstrip(',').strip()
            else:
                continue

            # Date
            rest = rest.lstrip(',').strip()
            dm = re.match(r'(-?\d+)', rest)
            if not dm:
                continue
            date = int(dm.group(1))
            rest = rest[dm.end():].lstrip(',').strip()

            # Status
            rest = rest.lstrip(',').strip()
            if rest.startswith("'"):
                end_q = rest.index("'", 1)
                status = rest[1:end_q]
                rest = rest[end_q+1:].lstrip(',').strip()
            else:
                continue

            # Optional code
            code = None
            rest = rest.lstrip(',').strip()
            if rest and rest.startswith("'"):
                end_q = rest.index("'", 1)
                code = rest[1:end_q]

            nodes.append({
                'id': node_id, 'name': name, 'parentId': parent_id,
                'date': date, 'status': status, 'code': code
            })
        except (ValueError, IndexError):
            continue

    return nodes


# ── Glottolog parser ──
def parse_glottolog_tree(tree_path):
    """Extract languages with their full family ancestry."""
    with open(tree_path, 'r') as f:
        tree = json.load(f)

    languages = []

    def walk(node, ancestry):
        level = node.get('level', 'unknown')
        name = node.get('name', '?')
        iso = node.get('iso639_3')
        glottocode = node.get('glottocode', '')
        current_path = ancestry + [name]

        if level == 'language':
            languages.append({
                'name': name, 'iso': iso, 'glottocode': glottocode,
                'ancestry': current_path,
                'family': ancestry[0] if ancestry else name,
                'countries': node.get('countries', []),
            })

        for child in node.get('children', []):
            walk(child, current_path)

    for fam in tree['families']:
        walk(fam, [])
    for iso_node in tree.get('isolates', []):
        walk(iso_node, [])

    return languages


# ── Family name → rosetta ID mapping ──
FAMILY_MAP = {
    'Atlantic-Congo': 'nc', 'Niger-Congo': 'nc',
    'Austronesian': 'an', 'Austroasiatic': 'aas',
    'Indo-European': 'ie', 'Sino-Tibetan': 'st',
    'Afro-Asiatic': 'aa', 'Turkic': 'tu', 'Uralic': 'ur',
    'Dravidian': 'dr', 'Mongolic': 'mo', 'Mongolic-Khitan': 'mo',
    'Japonic': 'jp', 'Koreanic': 'ko', 'Eskimo-Aleut': 'ea',
    'Kartvelian': 'kv', 'Tai-Kadai': 'tk', 'Kra-Dai': 'tk',
    'Algic': 'alg', 'Uto-Aztecan': 'ua', 'Siouan-Catawban': 'si',
    'Siouan': 'si.sio', 'Iroquoian': 'ir', 'Muskogean': 'mk',
    'Oto-Manguean': 'om', 'Mayan': 'my', 'Arawakan': 'aw',
    'Cariban': 'cb', 'Tupian': 'tp', 'Quechuan': 'qe',
    'Aymaran': 'ay', 'Chibchan': 'chb', 'Salishan': 'sal',
    'Nilotic': 'ns.nil', 'Nilo-Saharan': 'ns',
    'Semitic': 'aa.sem', 'Berber': 'aa.ber', 'Cushitic': 'aa.cush',
    'Chadic': 'aa.chad', 'Germanic': 'ie.gmc',
    'Romance': 'ie.ita.rom', 'Italic': 'ie.ita',
    'Slavic': 'ie.bs.slav', 'Baltic': 'ie.bs.balt',
    'Celtic': 'ie.cel', 'Indo-Iranian': 'ie.ii',
    'Indo-Aryan': 'ie.ii.ia', 'Iranian': 'ie.ii.ir',
    'Hellenic': 'ie.hel', 'Armenian': 'ie.arm', 'Albanian': 'ie.alb',
    'Bantu': 'nc.vc.bc.ban', 'Narrow Bantu': 'nc.vc.bc.ban',
    'Southern Bantoid': 'nc.vc.bc.ban', 'Bantoid': 'nc.vc.bc',
    'Benue-Congo': 'nc.vc.bc', 'Volta-Congo': 'nc.vc',
    'Mande': 'nc.man', 'Atlantic': 'nc.atl',
    'Sinitic': 'st.sin', 'Tibeto-Burman': 'st.tb',
    'Athabaskan': 'dy.nd.ae.ath', 'Athabaskan-Eyak-Tlingit': 'dy.nd',
    'Na-Dene': 'dy.nd', 'Yeniseian': 'dy.yen',
    'North Caucasian': 'dc.ncau', 'Northeast Caucasian': 'dc.ncau.nec',
    'Nakh-Daghestanian': 'dc.ncau.nec', 'Northwest Caucasian': 'dc.ncau.nwc',
    'Oceanic': 'an.mp.oc', 'Polynesian': 'an.mp.oc.pn',
    'Malayo-Polynesian': 'an.mp', 'Western Malayo-Polynesian': 'an.mp',
    'Algonquian': 'alg.algn', 'Tupí-Guaraní': 'tp.tg', 'Tupi-Guarani': 'tp.tg',
    'Nahuan': 'ua.s.nah', 'Numic': 'ua.n.num',
    'Oghuz': 'tu.ogh', 'Kipchak': 'tu.kip', 'Karluk': 'tu.kar',
    'Finnic': 'ur.fu.fin', 'Ugric': 'ur.fu.ug', 'Sami': 'ur.fu.sam',
    'Samoyedic': 'ur.sam', 'South Dravidian': 'dr.s',
    'Goidelic': 'ie.cel.ins.goi', 'Brythonic': 'ie.cel.ins.bry',
    'Formosan': 'an.fm', 'Zapotecan': 'om.zap', 'Mixtecan': 'om.mix',
    'Tuu': 'kh.tuu', "Kx'a": 'kh.kxa', 'Khoe-Kwadi': 'kh.khoe',
    'Hmong-Mien': 'st',  # close enough for visual grouping
    'Tungusic': 'mo',     # Altaic neighbor
}

# Geographic fallback keywords for unmatched families
GEO_REGIONS = {
    'africa': ['Nigeria','Cameroon','Kenya','Tanzania','Ethiopia','Congo',
               'Ghana','Senegal','Mali','Niger','Chad','Sudan','Uganda',
               'Mozambique','Angola','Zimbabwe','Zambia','Malawi','Benin',
               'Togo','Guinea','Burkina','Sierra','Liberia','Gabon',
               'Rwanda','Burundi','Somalia','Eritrea','Madagascar',
               'Mauritania','Namibia','Botswana','South Africa'],
    'oceania': ['Papua','Solomon','Vanuatu','New Caledonia','Timor','Fiji'],
    'australia': ['Australia'],
    'americas': ['Brazil','Colombia','Peru','Bolivia','Ecuador','Venezuela',
                 'Paraguay','Argentina','Chile','Mexico','Guatemala',
                 'Honduras','Nicaragua','Panama','United States','Canada',
                 'Guyana','Suriname','Costa Rica'],
    'asia': ['Indonesia','Malaysia','Philippines','Myanmar','Thailand',
             'Vietnam','Cambodia','Laos','China','India','Nepal',
             'Bangladesh','Pakistan','Afghanistan','Iran','Russia',
             'Mongolia','Japan','Korea','Taiwan','Sri Lanka'],
}

# Map region labels to rosetta backbone nodes they should attach to
# These are the closest "geographic neighbor" families in the rosetta tree
REGION_TO_PARENT = {
    'africa': 'nc',      # Niger-Congo (largest African family)
    'oceania': 'an',     # Austronesian (closest large family)
    'australia': 'root', # no close relative in rosetta
    'americas': 'root',  # diverse, attach to root
    'asia': 'st',        # Sino-Tibetan (largest Asian family)
}


def find_best_parent(lang, rosetta_ids):
    """Find the best rosetta backbone node to attach this language to."""
    # Walk ancestry from most specific to least
    for ancestor in reversed(lang['ancestry']):
        if ancestor in FAMILY_MAP and FAMILY_MAP[ancestor] in rosetta_ids:
            return FAMILY_MAP[ancestor]

    # Geographic fallback
    countries = lang.get('countries', [])
    if countries:
        country_str = ' '.join(countries)
        for region, keywords in GEO_REGIONS.items():
            if any(k in country_str for k in keywords):
                return REGION_TO_PARENT[region]

    return 'root'


def main():
    print("═══ Building tree-data.js (backbone + expansions) ═══\n")

    # Parse rosetta backbone
    backbone = extract_rosetta_tree(ROSETTA_PATH)
    print(f"Rosetta backbone: {len(backbone)} nodes")

    rosetta_ids = set(n['id'] for n in backbone)
    rosetta_names = set(n['name'].lower() for n in backbone)

    # Parse Glottolog languages
    glottolog = parse_glottolog_tree(LANG_TREE_PATH)
    print(f"Glottolog languages: {len(glottolog)}")

    # Build expansions: group languages by their rosetta parent
    expansions = {}  # parent_id → list of [id, name, status, code]
    skipped = 0

    for lang in glottolog:
        # Skip if already in backbone (by name match)
        if lang['name'].lower() in rosetta_names:
            skipped += 1
            continue

        parent_id = find_best_parent(lang, rosetta_ids)
        gid = f"g.{lang['glottocode']}" if lang['glottocode'] else f"g.{lang['name'][:12].lower()}"

        if parent_id not in expansions:
            expansions[parent_id] = []
        expansions[parent_id].append([gid, lang['name'], 'common', lang.get('iso')])

    total_expansion = sum(len(v) for v in expansions.values())
    print(f"\nSkipped (already in backbone): {skipped}")
    print(f"Expansion languages: {total_expansion}")
    print(f"Expansion groups: {len(expansions)}")

    # Count how many backbone nodes have expansions
    expandable = sum(1 for pid in expansions if pid in rosetta_ids)
    print(f"Expandable backbone nodes: {expandable}")

    # Show top expansion targets
    print("\nLargest expansion groups:")
    sorted_exp = sorted(expansions.items(), key=lambda x: -len(x[1]))
    for pid, langs in sorted_exp[:15]:
        pname = next((n['name'] for n in backbone if n['id'] == pid), pid)
        print(f"  {pname} ({pid}): {len(langs)} languages")

    # Format backbone as arrays: [id, name, parentId, date, status, code?]
    backbone_arr = []
    for n in backbone:
        entry = [n['id'], n['name'], n['parentId'], n['date'], n['status']]
        if n['code']:
            entry.append(n['code'])
        # Mark expandable nodes by adding expansion count as 7th element
        exp_count = len(expansions.get(n['id'], []))
        if exp_count > 0:
            if len(entry) == 5:
                entry.append(None)  # no code
            entry.append(exp_count)
        backbone_arr.append(entry)

    # Write output
    with open(OUTPUT_PATH, 'w') as f:
        f.write('// Auto-generated by build-tree-data.py\n')
        f.write(f'// Backbone: {len(backbone)} nodes (rosetta phylogeny)\n')
        f.write(f'// Expansions: {total_expansion} languages across {len(expansions)} groups\n\n')

        f.write('// The initial tree view — 519 hand-curated nodes with 8 levels of depth.\n')
        f.write('// Format: [id, name, parentId, date, status, code?, expandCount?]\n')
        f.write('window.TREE_BACKBONE = ')
        f.write(json.dumps(backbone_arr, ensure_ascii=False))
        f.write(';\n\n')

        f.write('// Glottolog languages grouped by their rosetta parent node ID.\n')
        f.write('// Loaded on demand when users click to expand a family.\n')
        f.write('// Format per entry: [id, name, status, isoCode]\n')
        f.write('window.TREE_EXPANSIONS = ')
        f.write(json.dumps(expansions, ensure_ascii=False))
        f.write(';\n')

    size_kb = os.path.getsize(OUTPUT_PATH) // 1024
    print(f"\nWrote {OUTPUT_PATH}")
    print(f"  {size_kb}KB total")


if __name__ == '__main__':
    main()
