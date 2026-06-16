#!/usr/bin/env python3
"""
Merge the rosetta mock's deep phylogeny (519 nodes, 7+ levels) with 
Glottolog's language-tree.json (1,652 languages, 3 levels shallow).

Strategy:
  1. Parse the rosetta TREE as the backbone (deep structure with 
     Proto-IE → Core IE → Germanic → West Germanic → English, etc.)
  2. Parse language-tree.json families as a lookup
  3. For each Glottolog language, walk up its ancestors to find a matching
     family node in the rosetta tree (by name similarity)
  4. Graft unplaced languages onto the best-matching rosetta ancestor
  5. Output a merged window.TREE with ~700-1000 nodes

Why: The rosetta tree has DEPTH (proper tree shape for visualization),
Glottolog has BREADTH (1,652 real languages). Neither alone is sufficient.
"""

import json
import re
import os
from difflib import SequenceMatcher

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LANG_TREE_PATH = os.path.join(SCRIPT_DIR, '..', '..', '..', '..', 
                               'cli', 'shared', 'language-cards', 'language-tree.json')
ROSETTA_PATH = os.path.join(SCRIPT_DIR, '..', '..', '..', '..', 
                             'marketing', 'rosetta-homepage-mock.html')
OUTPUT_PATH = os.path.join(SCRIPT_DIR, 'tree-data.js')

# ── Step 1: Extract rosetta TREE from the HTML ──
# The TREE is in a <script> block as a JS array assigned to window.TREE
def extract_rosetta_tree(html_path):
    """Parse the window.TREE array entries from the rosetta mock HTML.
    
    Uses regex directly on the full file content to extract each 
    [id, name, parent, date, status, code?] entry. No bracket matching needed.
    """
    with open(html_path, 'r') as f:
        content = f.read()
    
    # Each entry is: ['id', 'Name', 'parentId'|null, date, 'status', 'code'?]
    # Names can contain apostrophes (Ge'ez), pipes (Ju|'hoan), special chars
    # Use a pattern that captures the whole bracketed entry then parses fields
    pattern = re.compile(
        r"""\['([^']+)',\s*'((?:[^'\\]|\\.)*)(',\s*'([^']+)'|',\s*null),\s*"""
        r"""(-?\d+),\s*'(\w+)'"""
        r"""(?:,\s*'([^']*)')?\s*\]"""
    )
    
    # Simpler approach: split by lines, find lines that match the entry format
    nodes = []
    for line in content.split('\n'):
        line = line.strip()
        if not line.startswith('['):
            continue
        # Remove trailing comma
        line = line.rstrip(',').strip()
        if not line.endswith(']'):
            continue
            
        # Try to parse: ['id', 'name', 'parent'|null, date, 'status', 'code'?]
        try:
            # Extract fields manually to handle embedded quotes
            inner = line[1:-1].strip()  # Remove outer brackets
            
            # Split carefully: fields are comma-separated but names can have commas
            # Format is always: 'id', 'name', 'parent'|null, number, 'status'[, 'code']
            
            # Find the ID (first quoted string)
            m = re.match(r"'([^']+)',\s*", inner)
            if not m:
                continue
            node_id = m.group(1)
            rest = inner[m.end():]
            
            # Find the name (second quoted string - may contain escaped chars)
            # Handle names like: "Ge'ez", "Ju|'hoan", "K'iche'"
            # Names are wrapped in single quotes, but some contain single quotes
            # In JS, these use \" or the quote is part of a different delimiter
            # Actually looking at the data: "Ge'ez" uses escaped quote or double quote
            # Let's check: the mock uses  ['aa.sem.s.gez', "Ge'ez", ...]
            # So names with apostrophes use DOUBLE quotes!
            
            if rest.startswith('"'):
                # Double-quoted name
                end_q = rest.index('"', 1)
                name = rest[1:end_q]
                rest = rest[end_q+1:].lstrip(',').strip()
            elif rest.startswith("'"):
                # Single-quoted name — find closing quote (no embedded quotes)
                end_q = rest.index("'", 1)
                name = rest[1:end_q]
                rest = rest[end_q+1:].lstrip(',').strip()
            else:
                continue
            
            # Parent: 'parentId' or null
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
            
            # Date: integer
            rest = rest.lstrip(',').strip()
            dm = re.match(r'(-?\d+)', rest)
            if not dm:
                continue
            date = int(dm.group(1))
            rest = rest[dm.end():].lstrip(',').strip()
            
            # Status: quoted string
            rest = rest.lstrip(',').strip()
            if rest.startswith("'"):
                end_q = rest.index("'", 1)
                status = rest[1:end_q]
                rest = rest[end_q+1:].lstrip(',').strip()
            else:
                continue
            
            # Optional code: quoted string
            code = None
            rest = rest.lstrip(',').strip()
            if rest and rest.startswith("'"):
                end_q = rest.index("'", 1)
                code = rest[1:end_q]
            
            nodes.append({
                'id': node_id,
                'name': name,
                'parentId': parent_id,
                'date': date,
                'status': status,
                'code': code
            })
        except (ValueError, IndexError):
            # Skip unparseable lines
            continue
    
    return nodes


# ── Step 2: Parse language-tree.json ──
def parse_glottolog_tree(tree_path):
    """Extract all languages with their family ancestry paths."""
    with open(tree_path, 'r') as f:
        tree = json.load(f)
    
    languages = []
    
    def walk(node, ancestry):
        """Walk the tree, collecting languages with their full ancestry."""
        level = node.get('level', 'unknown')
        name = node.get('name', '?')
        iso = node.get('iso639_3')
        glottocode = node.get('glottocode', '')
        current_path = ancestry + [name]
        
        if level == 'language':
            languages.append({
                'name': name,
                'iso': iso,
                'glottocode': glottocode,
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


# ── Step 3: Build name-matching index from rosetta tree ──
def build_rosetta_index(rosetta_nodes):
    """Create lookup maps for matching Glottolog families to rosetta nodes."""
    by_name = {}  # lowercase name → rosetta node id
    by_id = {}    # node id → node
    
    for node in rosetta_nodes:
        by_id[node['id']] = node
        # Index by cleaned name for fuzzy matching
        clean = node['name'].lower().strip()
        # Remove "proto-" prefix for matching
        clean_no_proto = re.sub(r'^proto-?', '', clean)
        by_name[clean] = node['id']
        if clean_no_proto != clean:
            by_name[clean_no_proto] = node['id']
    
    return by_name, by_id


# ── Step 4: Map Glottolog family names to rosetta node IDs ──
# Hardcoded mappings for well-known families
FAMILY_MAP = {
    # Glottolog family name → rosetta node ID
    'Atlantic-Congo': 'nc',
    'Niger-Congo': 'nc',
    'Austronesian': 'an',
    'Austroasiatic': 'aas',
    'Indo-European': 'ie',
    'Sino-Tibetan': 'st',
    'Afro-Asiatic': 'aa',
    'Turkic': 'tu',
    'Uralic': 'ur',
    'Dravidian': 'dr',
    'Mongolic': 'mo',  
    'Mongolic-Khitan': 'mo',
    'Japonic': 'jp',
    'Koreanic': 'ko',
    'Eskimo-Aleut': 'ea',
    'Kartvelian': 'kv',
    'Tai-Kadai': 'tk',
    'Kra-Dai': 'tk',
    'Algic': 'alg',
    'Uto-Aztecan': 'ua',
    'Siouan-Catawban': 'si',
    'Siouan': 'si.sio',
    'Iroquoian': 'ir',
    'Muskogean': 'mk',
    'Oto-Manguean': 'om',
    'Mayan': 'my',
    'Arawakan': 'aw',
    'Cariban': 'cb',
    'Tupian': 'tp',
    'Quechuan': 'qe',
    'Aymaran': 'ay',
    'Chibchan': 'chb',
    'Salishan': 'sal',
    'Nilotic': 'ns.nil',
    'Nilo-Saharan': 'ns',
    'Semitic': 'aa.sem',
    'Berber': 'aa.ber',
    'Cushitic': 'aa.cush',
    'Chadic': 'aa.chad',
    'Germanic': 'ie.gmc',
    'Romance': 'ie.ita.rom',
    'Italic': 'ie.ita',
    'Slavic': 'ie.bs.slav',
    'Baltic': 'ie.bs.balt',
    'Celtic': 'ie.cel',
    'Indo-Iranian': 'ie.ii',
    'Indo-Aryan': 'ie.ii.ia',
    'Iranian': 'ie.ii.ir',
    'Hellenic': 'ie.hel',
    'Armenian': 'ie.arm',
    'Albanian': 'ie.alb',
    'Bantu': 'nc.vc.bc.ban',
    'Narrow Bantu': 'nc.vc.bc.ban',
    'Southern Bantoid': 'nc.vc.bc.ban',
    'Bantoid': 'nc.vc.bc',
    'Benue-Congo': 'nc.vc.bc',
    'Volta-Congo': 'nc.vc',
    'Mande': 'nc.man',
    'Atlantic': 'nc.atl',
    'Sinitic': 'st.sin',
    'Tibeto-Burman': 'st.tb',
    'Athabaskan': 'dy.nd.ae.ath',
    'Athabaskan-Eyak-Tlingit': 'dy.nd',
    'Na-Dene': 'dy.nd',
    'Yeniseian': 'dy.yen',
    'North Caucasian': 'dc.ncau',
    'Northeast Caucasian': 'dc.ncau.nec',
    'Nakh-Daghestanian': 'dc.ncau.nec',
    'Northwest Caucasian': 'dc.ncau.nwc',
    'Oceanic': 'an.mp.oc',
    'Polynesian': 'an.mp.oc.pn',
    'Malayo-Polynesian': 'an.mp',
    'Western Malayo-Polynesian': 'an.mp',
    'Algonquian': 'alg.algn',
    'Tupí-Guaraní': 'tp.tg',
    'Tupi-Guarani': 'tp.tg',
    'Nahuan': 'ua.s.nah',
    'Numic': 'ua.n.num',
    'Oghuz': 'tu.ogh',
    'Kipchak': 'tu.kip',
    'Karluk': 'tu.kar',
    'Finnic': 'ur.fu.fin',
    'Ugric': 'ur.fu.ug',
    'Sami': 'ur.fu.sam',
    'Samoyedic': 'ur.sam',
    'South Dravidian': 'dr.s',
    'Goidelic': 'ie.cel.ins.goi',
    'Brythonic': 'ie.cel.ins.bry',
    'Formosan': 'an.fm',
    'Zapotecan': 'om.zap',
    'Mixtecan': 'om.mix',
    'Tuu': 'kh.tuu',
    "Kx'a": 'kh.kxa',
    'Khoe-Kwadi': 'kh.khoe',
}

# ── Geographic grouping for families NOT in the rosetta backbone ──
# Creates intermediate "region" nodes so orphan families cluster 
# as branches on the tree instead of dangling off root.
REGION_FAMILIES = {
    # Papuan / Oceania
    'papuan': {
        'name': 'Papuan & Oceanian',
        'parent': 'root',
        'date': -40000,
        'families': [
            'Nuclear Trans New Guinea', 'Trans-New Guinea', 'Nuclear Torricelli',
            'Sepik', 'Ramu', 'Border', 'Tor-Orya', 'Anim', 'Yam',
            'Lakes Plain', 'Geelvink Bay', 'Angan', 'Dagan',
            'Torricelli', 'Kainantu-Goroka', 'Chimbu-Wahgi',
            'Engan', 'Eleman', 'Bosavi', 'Turama-Kikorian',
            'Bulaka River', 'Pahoturi', 'Eastern Trans-Fly',
            'Yuat', 'Piawi', 'Senagi', 'Left May', 'Kwomtari',
            'South Bougainville', 'North Bougainville', 'Fas',
            'Ndu', 'Sko', 'Kwalean', 'Koiarian', 'Mailuan',
            'South-Central Papuan', 'Kaure-Kosare',
        ],
    },
    # Australian
    'australian': {
        'name': 'Australian',
        'parent': 'root',
        'date': -60000,
        'families': [
            'Pama-Nyungan', 'Gunwinyguan', 'Western Daly',
            'Nyulnyulan', 'Worrorran', 'Bunuban', 'Jarrakan',
            'Mirndi', 'Tangkic', 'Garrwan', 'Mangarrayi-Maran',
            'Darwin Region', 'Iwaidjan', 'Yolngu',
            'Eastern Daly', 'Northern Daly', 'Southern Daly',
        ],
    },
    # African (non-NC, non-AA, non-NS)
    'african.other': {
        'name': 'Other African',
        'parent': 'root',
        'date': -15000,
        'families': [
            'Dogon', 'Central Sudanic', 'Ta-Ne-Omotic', 'Songhay',
            'Saharan', 'Maban', 'Fur', 'Koman', 'Gumuz',
            'Kunama', 'Berta', 'Shabo', 'Laal', 'Bangime',
            'Ijoid', 'Ubangian', 'Kordofanian',
        ],
    },
    # Americas (non-rosetta families)
    'americas.other': {
        'name': 'Other American',
        'parent': 'root',
        'date': -15000,
        'families': [
            'Miwok-Costanoan', 'Penutian', 'Hokan',
            'Totonacan', 'Mixe-Zoque', 'Chinookan',
            'Wakashan', 'Tsimshianic', 'Haida',
            'Pomoan', 'Yokutsan', 'Wintuan', 'Maiduan',
            'Kiowa-Tanoan', 'Caddoan', 'Pano-Tacanan',
            'Tacanan', 'Panoan', 'Yanomamic', 'Jivaroan',
            'Zaparoan', 'Boran', 'Witotoan', 'Naduhup',
            'Guaicuruan', 'Matacoan', 'Mascoian', 'Zamucoan',
            'Chapacuran', 'Nambikwaran', 'Arawan',
            'Cahuapanan', 'Peba-Yaguan', 'Cholonan',
            'Barbacoan', 'Chocoan', 'Misumalpan',
            'Otomanguean', 'Tequistlatecan',
        ],
    },
    # SE Asia (non-rosetta)
    'seasia.other': {
        'name': 'Other SE Asian',
        'parent': 'root',
        'date': -8000,
        'families': [
            'Hmong-Mien', 'Andamanese', 'Ongan', 'Great Andamanese',
            'Tungusic', 'Chukotko-Kamchatkan', 'Nivkh',
            'Yukaghir',
        ],
    },
    # Catch-all for truly unplaced languages
    'isolates': {
        'name': 'Isolates & Unclassified',
        'parent': 'root',
        'date': -50000,
        'families': [],
    },
}


def find_rosetta_parent(lang, name_index, rosetta_by_id):
    """
    Walk up a Glottolog language's ancestry to find the best 
    matching rosetta tree node to attach it to.
    """
    # Try direct family mapping first (most specific match first)
    for ancestor_name in reversed(lang['ancestry']):
        if ancestor_name in FAMILY_MAP:
            target = FAMILY_MAP[ancestor_name]
            if target in rosetta_by_id:
                return target
    
    # Try fuzzy name matching against rosetta nodes
    for ancestor_name in reversed(lang['ancestry']):
        clean = ancestor_name.lower().strip()
        clean_no_proto = re.sub(r'^proto-?', '', clean)
        
        if clean in name_index:
            return name_index[clean]
        if clean_no_proto in name_index:
            return name_index[clean_no_proto]
    
    # Try region grouping: check if top-level family is in a region group
    top_family = lang['family']
    for region_id, region in REGION_FAMILIES.items():
        if top_family in region['families']:
            return f'_reg.{region_id}'
    
    # Geographic fallback: assign to a region based on country data
    countries = lang.get('countries', [])
    if countries:
        # Simple continent mapping from country names
        africa_kw = ['Nigeria', 'Cameroon', 'Kenya', 'Tanzania', 'Ethiopia', 'Congo',
                     'Ghana', 'Senegal', 'Mali', 'Niger', 'Chad', 'Sudan', 'Uganda',
                     'Mozambique', 'Angola', 'Zimbabwe', 'Zambia', 'Malawi', 'Benin',
                     'Togo', 'Guinea', 'Burkina', 'Ivory', 'Sierra', 'Liberia',
                     'Gabon', 'Rwanda', 'Burundi', 'Somalia', 'Eritrea', 'Djibouti',
                     'Madagascar', 'Mauritania', 'Namibia', 'Botswana', 'South Africa',
                     'Central African', 'Equatorial']
        papuan_kw = ['Papua', 'Solomon', 'Vanuatu', 'New Caledonia', 'Timor']
        aus_kw = ['Australia']
        americas_kw = ['Brazil', 'Colombia', 'Peru', 'Bolivia', 'Ecuador', 'Venezuela',
                       'Paraguay', 'Argentina', 'Chile', 'Mexico', 'Guatemala', 'Honduras',
                       'Nicaragua', 'Panama', 'Costa Rica', 'Guyana', 'Suriname',
                       'United States', 'Canada']
        asia_kw = ['Indonesia', 'Malaysia', 'Philippines', 'Myanmar', 'Thailand',
                   'Vietnam', 'Cambodia', 'Laos', 'China', 'India', 'Nepal',
                   'Bangladesh', 'Pakistan', 'Afghanistan', 'Iran', 'Russia',
                   'Mongolia', 'Japan', 'Korea', 'Taiwan', 'Sri Lanka']
        
        country_str = ' '.join(countries)
        if any(k in country_str for k in africa_kw):
            return '_reg.african.other'
        if any(k in country_str for k in papuan_kw):
            return '_reg.papuan'
        if any(k in country_str for k in aus_kw):
            return '_reg.australian'
        if any(k in country_str for k in americas_kw):
            return '_reg.americas.other'
        if any(k in country_str for k in asia_kw):
            return '_reg.seasia.other'
    
    # True last resort: "Other Isolates" catch-all node
    return '_reg.isolates'


def main():
    print("═══ Merging rosetta phylogeny + Glottolog languages ═══\n")
    
    # Parse both sources
    rosetta_nodes = extract_rosetta_tree(ROSETTA_PATH)
    print(f"Rosetta backbone: {len(rosetta_nodes)} nodes")
    
    glottolog_langs = parse_glottolog_tree(LANG_TREE_PATH)
    print(f"Glottolog languages: {len(glottolog_langs)} languages")
    
    # Build index
    name_index, rosetta_by_id = build_rosetta_index(rosetta_nodes)
    
    # Pre-register region grouping nodes so they're valid parent targets
    for region_id, region in REGION_FAMILIES.items():
        rid = f'_reg.{region_id}'
        rosetta_by_id[rid] = {
            'id': rid, 'name': region['name'],
            'parentId': region['parent'],
            'date': region['date'], 'status': 'proto', 'code': None
        }
    
    # Also create per-family grouping nodes under region nodes,
    # so languages cluster by their specific Glottolog family
    glottolog_family_nodes = {}  # family_name → created node id
    
    # Track which rosetta names/codes already exist (for dedup)
    rosetta_names = set()
    rosetta_codes = set()
    for n in rosetta_nodes:
        rosetta_names.add(n['name'].lower())
        if n['code']:
            rosetta_codes.add(n['code'])
    
    # Map each Glottolog language to a rosetta parent
    grafted = []
    placement_stats = {}
    skipped_dups = 0
    
    for lang in glottolog_langs:
        # Skip if this language is already in the rosetta tree
        if lang['name'].lower() in rosetta_names:
            skipped_dups += 1
            continue
        
        # Find where to graft this language
        parent_id = find_rosetta_parent(lang, name_index, rosetta_by_id)
        
        # If landing on a region node, create an intermediate family node
        if parent_id.startswith('_reg.'):
            fam_name = lang['family']
            if fam_name not in glottolog_family_nodes:
                fam_id = f'_fam.{fam_name[:20].lower().replace(" ", "_")}'
                glottolog_family_nodes[fam_name] = fam_id
                rosetta_by_id[fam_id] = {
                    'id': fam_id, 'name': fam_name,
                    'parentId': parent_id,
                    'date': -3000, 'status': 'proto', 'code': None
                }
            parent_id = glottolog_family_nodes[fam_name]
        
        placement_stats[parent_id] = placement_stats.get(parent_id, 0) + 1
        
        # Create a unique ID for the grafted node
        node_id = f"g.{lang['glottocode']}" if lang['glottocode'] else f"g.{lang['name'][:8].lower()}"
        
        # Determine status: 'common' for living languages
        status = 'common'
        code = None
        
        grafted.append({
            'id': node_id,
            'name': lang['name'],
            'parentId': parent_id,
            'date': 0,
            'status': status,
            'code': code,
        })
    
    print(f"\nSkipped (already in rosetta): {skipped_dups}")
    print(f"Grafted onto rosetta tree: {len(grafted)}")
    
    # Show placement distribution
    print(f"\nTop placement targets:")
    sorted_placements = sorted(placement_stats.items(), key=lambda x: -x[1])
    for parent_id, count in sorted_placements[:25]:
        parent_name = rosetta_by_id.get(parent_id, {}).get('name', parent_id)
        print(f"  {parent_name}: {count} languages")
    
    orphans = placement_stats.get('root', 0)
    print(f"\nOrphans (still on root): {orphans}")
    
    # Combine: rosetta backbone + region nodes + family nodes + grafted languages
    merged = []
    
    # 1. Rosetta backbone
    for n in rosetta_nodes:
        entry = [n['id'], n['name'], n['parentId'], n['date'], n['status']]
        if n['code']:
            entry.append(n['code'])
        merged.append(entry)
    
    # 2. Region grouping nodes
    for region_id, region in REGION_FAMILIES.items():
        rid = f'_reg.{region_id}'
        merged.append([rid, region['name'], region['parent'], region['date'], 'proto'])
    
    # 3. Auto-created family nodes under regions
    for fam_name, fam_id in glottolog_family_nodes.items():
        n = rosetta_by_id[fam_id]
        merged.append([n['id'], n['name'], n['parentId'], n['date'], n['status']])
    
    # 4. Grafted languages
    for n in grafted:
        entry = [n['id'], n['name'], n['parentId'], n['date'], n['status']]
        if n['code']:
            entry.append(n['code'])
        merged.append(entry)
    
    # Write output
    with open(OUTPUT_PATH, 'w') as f:
        f.write('// Auto-generated: rosetta phylogeny + Glottolog languages merged\n')
        f.write(f'// {len(rosetta_nodes)} backbone + {len(REGION_FAMILIES)} regions + '
                f'{len(glottolog_family_nodes)} families + {len(grafted)} languages = '
                f'{len(merged)} total\n')
        f.write('window.TREE = ')
        f.write(json.dumps(merged, ensure_ascii=False))
        f.write(';\n')
    
    size_kb = os.path.getsize(OUTPUT_PATH) // 1024
    print(f"\nWrote {OUTPUT_PATH}")
    print(f"  {len(merged)} total nodes, {size_kb}KB")
    
    # Verify tree integrity
    ids = set(e[0] for e in merged)
    broken = [e for e in merged if e[2] is not None and e[2] not in ids]
    if broken:
        print(f"\n⚠ {len(broken)} orphaned nodes (parent not found):")
        for b in broken[:10]:
            print(f"  {b[1]} → parent '{b[2]}'")
    else:
        print("\n✓ Tree integrity OK — all parents found")


if __name__ == '__main__':
    main()

