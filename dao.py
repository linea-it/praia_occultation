#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import collections
from sqlalchemy import MetaData, Table, create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.sql import text
import pandas as pd


class Dao():

    engine = None

    def get_db_uri(self):

        # DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME
        db_uri = "postgresql+psycopg2://%s:%s@%s:%s/%s" % (
            "postgres", "postgres", "172.18.0.2", "5432", "tno_v2")

        return db_uri

    def get_db_engine(self):

        if self.engine is None:

            self.engine = create_engine(
                self.get_db_uri(),
                poolclass=NullPool
            )

        return self.engine

    def get_table(self, tablename, schema=None):
        engine = self.get_db_engine()
        tbl = Table(
            tablename, MetaData(engine), autoload=True, schema=schema)
        return tbl

    def fetch_all_dict(self, stm):
        engine = self.get_db_engine()
        with engine.connect() as con:

            queryset = con.execute(stm)

            rows = list()
            for row in queryset:
                d = dict(collections.OrderedDict(row))
                rows.append(d)

            return rows

    def fetch_one_dict(self, stm):
        engine = self.get_db_engine()
        with engine.connect() as con:

            queryset = con.execute(stm).fetchone()

            if queryset is not None:
                d = dict(collections.OrderedDict(queryset))
                return d
            else:
                return None


class GaiaDao(Dao):
    def __init__(self):
        # super(GaiaDao, self).__init__()

        # self.tbl = self.get_table(tablename="dr2", schema="gaia")
        self.catalog = dict({
            "schema": "gaia",
            "tablename": "dr2",
            "ra_property": "ra",
            "dec_property": "dec"
        })

        self.gaia_properties = [
            "ra", "ra_error", "dec", "dec_error", "parallax", "pmra", "pmra_error", "pmdec",
            "pmdec_error", "duplicated_source", "phot_g_mean_flux", "phot_g_mean_flux_error",
            "phot_g_mean_mag", "phot_variable_flag"
        ]

    def catalog_by_positions(self, positions, radius=0.15):

        try:
            print("Abriu conexao")

            if self.catalog["schema"] is not None:
                tablename = "%s.%s" % (
                    self.catalog["schema"], self.catalog["tablename"])
            else:
                tablename = self.catalog["tablename"]

            columns = ", ".join(self.gaia_properties)

            results = []
            for pos in positions:
                print("Quering for pos %s" % pos)
                where = 'q3c_radial_query("%s", "%s", % s, % s, % s)' % (
                        self.catalog["ra_property"], self.catalog["dec_property"], pos[0], pos[1], radius)

                stm = """SELECT %s FROM %s WHERE %s """ % (
                    columns, tablename, where)

                stm = """SELECT %s FROM %s where q3c_radial_query('ra', 'dec', 36.662958333333336, 5.367043333333333, 0.18) limit 10 """ % (
                    columns, tablename)
                print(stm)

                rows = self.fetch_all_dict(text(stm))
                results += rows

                # temp_df = pd.read_sql(text(stm),
                #                       con=self.get_db_engine())

                # print(temp_df.head())
                # rows = 0

            if len(results) >= 2100000:
                pass
                # self.logger.warning("Stellar Catalog too big")
                # TODO marcar o status do Asteroid como warning.
                # TODO implementar funcao para dividir o resutado em lista menores e executar em loop.

            return results

        except Exception as e:
            # logger.error(e)
            raise e


if __name__ == "__main__":

    dao = GaiaDao()

    print("Teste")

    import csv

    positions = list()
    with open('/data/centers_deg.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            positions.append([row['ra'], row['dec']])
            # a.append('q3c_radial_query("ra", "dec", %s, %s, 0.18)' % (
            #     row['ra'], row['dec']))

    # print(" or ".join(a))

    engine = dao.get_db_engine()
    with engine.connect() as con:
        # stm = 'SELECT * FROM gaia.dr2 WHERE q3c_radial_query("ra", "dec", 36.662958333333336, 5.367043333333333, 0.15) limit 10'
        stm = 'SELECT * FROM gaia.dr2 limit 10'
        queryset = con.execute(stm)
        print(queryset)
    # positions = []
    # catalog = dao.catalog_by_positions(positions[0:2], radius=0.15)

    # print(len(catalog))

    # print("Teste2")

    # dao = GaiaDao()

    # print("Teste")

    # import csv

    # positions = list()
    # with open('/data/centers_deg.csv', 'r') as csvfile:
    #     reader = csv.DictReader(csvfile)
    #     for row in reader:
    #         positions.append([row['ra'], row['dec']])
    #         # a.append('q3c_radial_query("ra", "dec", %s, %s, 0.18)' % (
    #         #     row['ra'], row['dec']))

    # # print(" or ".join(a))

    # # positions = []
    # # catalog = dao.catalog_by_positions(positions, radius=0.15)
