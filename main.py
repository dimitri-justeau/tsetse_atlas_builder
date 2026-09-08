import os.path
import shutil
from os import mkdir

import pandas as pd
from jinja2 import Environment, FileSystemLoader

from config import Config
from db_query import get_regions, get_prefectures, get_all_prefectures, get_all_traps, get_region_traps, \
    get_prefecture_traps, get_total_tsetse_species, get_region_tsetse_species, get_prefecture_tsetse_species

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
    for index, region in regions.iterrows():
        r = regions[regions["name"] == region["name"]]
        r.to_file(os.path.join(Config.ASSETS_ROOT, "geojson", "r_{}.geojson".format(region["name"])), driver="GeoJSON")
        r_traps = get_region_traps(region["id"])
        region_traps[index] = r_traps
        r_traps.to_file(os.path.join(Config.ASSETS_ROOT, "geojson", "r_{}_traps.geojson".format(region["name"])), driver="GeoJSON")
    ## Individual prefectures
    prefecture_traps = {}
    for index, pref in all_prefectures.iterrows():
        p = all_prefectures[all_prefectures["name"] == pref["name"]]
        p.to_file(os.path.join(Config.ASSETS_ROOT, "geojson", "p_{}.geojson".format(pref["name"])), driver="GeoJSON")
        p_traps = get_prefecture_traps(pref["id"])
        prefecture_traps[index] = p_traps
        p_traps.to_file(os.path.join(Config.ASSETS_ROOT, "geojson", "p_{}_traps.geojson".format(pref["name"])), driver="GeoJSON")
    ## All tsetse traps
    all_traps.to_file(os.path.join(Config.ASSETS_ROOT, "geojson", "all_traps.geojson"), driver="GeoJSON")
    # Clear output dir
    if os.path.exists("output"):
        shutil.rmtree("output")
    mkdir("output")
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
        current="national"
    )
    with open("output/index.html", "w") as html_file:
        html_file.write(html_output)
    # Region pages
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
            current="r_{}".format(region["name"])
        )
        with open("output/{}.html".format(region["name"]), "w") as html_file:
            html_file.write(html_output)
    # Prefecture pages
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
            current="p_{}".format(pref["name"])
        )
        with open("output/{}_p.html".format(pref["name"]), "w") as html_file:
            html_file.write(html_output)
    # Copy static resources
    shutil.copytree("static", "output/static")