"""
A set of database queries to retrieve essential information about the Atlas
"""
from sqlalchemy import create_engine
import geopandas as gpd
import pandas as pd


def get_engine():
    engine = create_engine("postgresql://niamoto:niamoto@localhost:5432/atlas_tsetse")
    return engine

def get_regions():
    engine = get_engine()
    regions = gpd.read_postgis(
        "SELECT * FROM region;", engine, geom_col="geometry"
    )
    return regions

def get_prefectures(region_id):
    engine = get_engine()
    prefectures = gpd.read_postgis(
        "SELECT * FROM prefecture WHERE region_id = {};".format(region_id), engine, geom_col="geometry"
    )
    return prefectures

def get_all_prefectures():
    engine = get_engine()
    prefectures = gpd.read_postgis(
        "SELECT * FROM prefecture;", engine, geom_col="geometry"
    )
    return prefectures

def get_all_traps():
    engine = get_engine()
    traps = gpd.read_postgis(
        """
        SELECT code, start_date, end_date, MIN(locality.name) as locality_name, location,
               SUM(tsetse_catch.count) as total_tsetse FROM tsetse_trap
        INNER JOIN locality ON locality.id = tsetse_trap.locality_id
        LEFT JOIN tsetse_catch ON tsetse_catch.trap_id = tsetse_trap.id
        GROUP BY tsetse_trap.id;
        """, engine, geom_col="location"
    )
    return traps

def get_total_tsetse_species():
    engine = get_engine()
    res = pd.read_sql(
        """
        SELECT COUNT(DISTINCT tsetse_catch.species) as nb_species FROM tsetse_catch;
        """, engine
    )
    return res["nb_species"].iloc[0]

def get_region_traps(region_id):
    engine = get_engine()
    traps = gpd.read_postgis(
        """
        SELECT code, start_date, end_date, MIN(locality.name) as locality_name, location,
                SUM(tsetse_catch.count) as total_tsetse FROM tsetse_trap
            INNER JOIN locality ON locality.id = tsetse_trap.locality_id
            INNER JOIN sous_prefecture ON sous_prefecture.id = locality.sous_prefecture_id
            INNER JOIN prefecture ON prefecture.id = sous_prefecture.prefecture_id
            LEFT JOIN tsetse_catch ON tsetse_catch.trap_id = tsetse_trap.id
            WHERE prefecture.region_id = {}
            GROUP BY tsetse_trap.id;
        """.format(region_id), engine, geom_col="location"
    )
    return traps

def get_region_tsetse_species(region_id):
    engine = get_engine()
    res = pd.read_sql(
        """
        SELECT COUNT(DISTINCT tsetse_catch.species) as nb_species FROM tsetse_catch
            INNER JOIN tsetse_trap ON tsetse_trap.id = tsetse_catch.trap_id
            INNER JOIN locality ON locality.id = tsetse_trap.locality_id
            INNER JOIN sous_prefecture ON sous_prefecture.id = locality.sous_prefecture_id
            INNER JOIN prefecture ON prefecture.id = sous_prefecture.prefecture_id
            WHERE prefecture.region_id = {};
        """.format(region_id), engine
    )
    return res["nb_species"].iloc[0]

def get_prefecture_traps(prefecture_id):
    engine = get_engine()
    traps = gpd.read_postgis(
        """
        SELECT code, start_date, end_date, MIN(locality.name) as locality_name, location,
            SUM(tsetse_catch.count) as total_tsetse FROM tsetse_trap
            INNER JOIN locality ON locality.id = tsetse_trap.locality_id
            INNER JOIN sous_prefecture ON sous_prefecture.id = locality.sous_prefecture_id
            LEFT JOIN tsetse_catch ON tsetse_catch.trap_id = tsetse_trap.id
            WHERE sous_prefecture.prefecture_id = {}
            GROUP BY tsetse_trap.id;
        """.format(prefecture_id), engine, geom_col="location"
    )
    return traps

def get_prefecture_tsetse_species(prefecture_id):
    engine = get_engine()
    res = pd.read_sql(
        """
        SELECT COUNT(DISTINCT tsetse_catch.species) as nb_species FROM tsetse_catch
            INNER JOIN tsetse_trap ON tsetse_trap.id = tsetse_catch.trap_id
            INNER JOIN locality ON locality.id = tsetse_trap.locality_id
            INNER JOIN sous_prefecture ON sous_prefecture.id = locality.sous_prefecture_id
            WHERE sous_prefecture.prefecture_id = {};
        """.format(prefecture_id), engine
    )
    return res["nb_species"].iloc[0]

def get_trap(trap_key):
    engine = get_engine()
    res = gpd.read_postgis(
        """
            SELECT tsetse_trap.*, habitat.*, SUM(tsetse_catch.count) as total_tsetse FROM tsetse_trap
                INNER JOIN habitat ON tsetse_trap.id = habitat.trap_id
                LEFT JOIN tsetse_catch ON tsetse_catch.trap_id = tsetse_trap.id
            WHERE tsetse_trap.code = '{}'
            GROUP BY (tsetse_trap.id, habitat.trap_id);
        """.format(trap_key), engine, geom_col="location"
    )
    res.drop(columns=["notes"], inplace=True)
    return res

def get_trap_tsetse_species(trap_code):
    engine = get_engine()
    res = pd.read_sql(
        """
        SELECT COUNT(DISTINCT tsetse_catch.species) as nb_species FROM tsetse_catch
            INNER JOIN tsetse_trap ON tsetse_trap.id = tsetse_catch.trap_id
            WHERE tsetse_trap.code = '{}';
        """.format(trap_code), engine
    )
    return res["nb_species"].iloc[0]