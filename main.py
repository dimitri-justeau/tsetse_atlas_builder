import os.path
import shutil
from pathlib import Path

import pandas as pd
from jinja2 import Environment, FileSystemLoader

from config import Config
from db_query import get_regions, get_prefectures, get_all_prefectures, get_all_traps, get_region_traps, \
    get_prefecture_traps, get_total_tsetse_species, get_region_tsetse_species, get_prefecture_tsetse_species, get_trap, \
    get_trap_tsetse_species

labels = {
    'urban_populated': "Zone urbaine",
    'rural_populated': "Zone rurale",
    'agricultural': "Zone agricole",
    'forest_dominated': "Zone forestière",
    'woodland_dominated': "Zone boisée",
    'grassland_dominated': "Zone de prairie",
    'rain_forest': "Forêt humide",
    'short_forest': "Forêt basse",
    'gallery_forest': "Forêt galerie",
    'woodland': "Forêt claire",
    'bushland': "Formation buissonnante",
    'thicket': "Fourré",
    'shrubland': "Formation arbustive",
    'grassland': "Formation herbeuse",
    'wooded_grassland': "Formation herbeuse boisée",
    'mangrove': "Mangrove",
    'lowland': "Bas-fond",
    'swamp': "Marais",
    'palm_plantation': "Palmeraie",
    'timber_plantation': "Plantation sylvicole",
    'hevea_plantation': "Plantation d'hévea",
    'fruit_tree_plantation': "Vergers",
    'agroforestry': "Agroforesterie",
    'banana_plantation': "Bananeraie",
    'vegetable_field': "Maraichage",
    'rice_field': "Rizière",
    'cultivated_lowland': "Bas-fond cultivé",
    'fallow': "Jachère",
    'sandy': "Sableux",
    'clayey': "Argileux",
    'silty': "Limoneux",
    'sandy_clay': "Sablo-limoneux",
    'clayey_sand': "Argilo-sableux",
    'silty_clay': "Limono-argileux",
    'clayey_silt': "Argilo-limoneux",
    'sandy_silt': "Sablo-limoneux",
    'silty_sand': "Limono-sableux",
    'lateritic': "Latéritique",
    'rocky': "Rocheux",
    'hydromorphic': "Hydromorphique",
    'silty_rock': "Limono-rocheux",
    'very_low': "Très faible",
    'low': "Faible",
    'moderate': "Modéré",
    'high': "Élevé",
    'very_high': "Très élevé",
    True: "Oui",
    False: "Non",
}

def translate_label(text):
    if text in labels:
        return labels[text]
    return text

if __name__ == '__main__':
    # Load environment
    env = Environment(loader=FileSystemLoader('templates'))
    # Query database element
    ## Regions and prefectures
    regions = get_regions()
    all_prefectures = get_all_prefectures()
    prefectures = {}
    for r_id in regions["id"]:
        prefs = get_prefectures(r_id)
        if len(prefs) > 1:
            prefectures[r_id] = get_prefectures(r_id)
        else:
            prefectures[r_id] = pd.DataFrame()
    ## Tsetse traps
    all_traps = get_all_traps()
    # Export geojson
    ## All regions
    regions.to_file(os.path.join(Config.ASSETS_ROOT, "geojson/regions.geojson"), driver="GeoJSON")
    ## Individual regions
    region_traps = {}
    Path(os.path.join(Config.ASSETS_ROOT, "geojson", "regions")).mkdir(exist_ok=True)
    for index, region in regions.iterrows():
        r = regions[regions["name"] == region["name"]]
        r.to_file(os.path.join(Config.ASSETS_ROOT, "geojson", "regions", "r_{}.geojson".format(region["name"])), driver="GeoJSON")
        r_traps = get_region_traps(region["id"])
        region_traps[index] = r_traps
        r_traps.to_file(os.path.join(Config.ASSETS_ROOT, "geojson", "regions", "r_{}_traps.geojson".format(region["name"])), driver="GeoJSON")
    ## Individual prefectures
    prefecture_traps = {}
    Path(os.path.join(Config.ASSETS_ROOT, "geojson", "prefectures")).mkdir(exist_ok=True)
    for index, pref in all_prefectures.iterrows():
        p = all_prefectures[all_prefectures["name"] == pref["name"]]
        p.to_file(os.path.join(Config.ASSETS_ROOT, "geojson", "prefectures", "p_{}.geojson".format(pref["name"])), driver="GeoJSON")
        p_traps = get_prefecture_traps(pref["id"])
        prefecture_traps[index] = p_traps
        p_traps.to_file(os.path.join(Config.ASSETS_ROOT, "geojson", "prefectures", "p_{}_traps.geojson".format(pref["name"])), driver="GeoJSON")
    ## All tsetse traps
    all_traps.to_file(os.path.join(Config.ASSETS_ROOT, "geojson", "all_traps.geojson"), driver="GeoJSON")
    ## Individual traps
    individual_traps = {}
    Path(os.path.join(Config.ASSETS_ROOT, "geojson", "traps")).mkdir(exist_ok=True)
    for index, trap in all_traps.iterrows():
        trap_data = get_trap(trap["code"])
        individual_traps[index] = {
            "zone": translate_label(trap_data["zone"][0]),
            "vegetation": translate_label(trap_data["vegetation"][0]),
            "soil_main": translate_label(trap_data["soil_main"][0]),
            "soil_secondary": translate_label(trap_data["soil_secondary"][0]),
            "river": translate_label(trap_data["river"][0]),
            "waste_pollution": translate_label(trap_data["waste_pollution"][0]),
            "anthropization": translate_label(trap_data["waste_pollution"][0]),
            "phytosanitary_products": translate_label(trap_data["phytosanitary_products"][0]),
            "livestock": translate_label(trap_data["livestock"][0]),
            "logging": translate_label(trap_data["logging"][0]),
            "fire_marks": translate_label(trap_data["fire_marks"][0]),
            "mining_related_activity": translate_label(trap_data["mining_related_activity"][0]),
            "elevation": trap_data["elevation"][0],
            "start_date": trap_data["start_date"][0],
            "end_date": trap_data["end_date"][0],
            "total_tsetse": trap_data["total_tsetse"][0],
        }
        trap_data.to_file(os.path.join(Config.ASSETS_ROOT, "geojson", "traps", "{}.geojson".format(trap["code"])), driver="GeoJSON")
    # Clear output dir
    if os.path.exists("output"):
        shutil.rmtree("output")
    Path("output").mkdir()
    # Load and render templates
    # Index
    template = env.get_template('home/index.html')
    html_output = template.render(
        config=Config,
        regions=regions,
        prefectures=prefectures,
        traps=all_traps,
        total_tsetse=sum(all_traps["total_tsetse"]),
        total_tsetse_species=get_total_tsetse_species(),
        current="national",
        root="."
    )
    with open("output/index.html", "w") as html_file:
        html_file.write(html_output)
    # Region pages
    Path(os.path.join("output", "regions")).mkdir(exist_ok=True)
    for index, region in regions.iterrows():
        template = env.get_template("home/region_index.html")
        html_output = template.render(
            config=Config,
            regions=regions,
            prefectures=prefectures,
            region=region,
            traps=region_traps[index],
            total_tsetse=sum(region_traps[index]["total_tsetse"]),
            total_tsetse_species=get_region_tsetse_species(region["id"]),
            current="r_{}".format(region["name"]),
            root=".."
        )
        with open("output/regions/{}.html".format(region["name"]), "w") as html_file:
            html_file.write(html_output)
    # Prefecture pages
    Path(os.path.join("output", "prefectures")).mkdir(exist_ok=True)
    for index, pref in all_prefectures.iterrows():
        template = env.get_template("home/prefecture_index.html")
        html_output = template.render(
            config=Config,
            regions=regions,
            prefectures=prefectures,
            prefecture=pref,
            traps=prefecture_traps[index],
            total_tsetse=sum(prefecture_traps[index]["total_tsetse"]),
            total_tsetse_species=get_prefecture_tsetse_species(pref["id"]),
            current="p_{}".format(pref["name"]),
            root=".."
        )
        with open("output/prefectures/{}_p.html".format(pref["name"]), "w") as html_file:
            html_file.write(html_output)
    # Trap pages
    Path(os.path.join("output", "traps")).mkdir(exist_ok=True)
    for index, trap in all_traps.iterrows():
        template = env.get_template("home/trap_index.html")
        html_output = template.render(
            config=Config,
            regions=regions,
            prefectures=prefectures,
            trap=individual_traps[index],
            trap_code=trap["code"],
            total_tsetse=individual_traps[index]["total_tsetse"],
            total_tsetse_species=get_trap_tsetse_species(trap["code"]),
            current="{}".format(trap["code"]),
            root=".."
        )
        with open("output/traps/{}.html".format(trap["code"]), "w") as html_file:
            html_file.write(html_output)
    # Copy static resources
    shutil.copytree("static", "output/static")