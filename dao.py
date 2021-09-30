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
            "source_id", "ra", "ra_error", "dec", "dec_error", "parallax", "pmra", "pmra_error", "pmdec",
            "pmdec_error", "duplicated_source", "phot_g_mean_flux", "phot_g_mean_flux_error",
            "phot_g_mean_mag", "phot_variable_flag"
        ]

        # Quantas posições por query.
        self.POSITION_GROUP = 5

    def chunks_positions(self, l, n):
        n = max(1, n)
        return (l[i:i+n] for i in range(0, len(l), n))

    def q3c_clause(self, ra, dec, radius):

        clause = 'q3c_radial_query("%s", "%s", %s, %s, %s)' % (
            self.catalog["ra_property"], self.catalog["dec_property"], ra, dec, radius)

        return clause

    def catalog_by_positions(self, positions, radius=0.15):

        try:
            print("Abriu conexao")

            if self.catalog["schema"] is not None:
                tablename = "%s.%s" % (
                    self.catalog["schema"], self.catalog["tablename"])
            else:
                tablename = self.catalog["tablename"]

            columns = ", ".join(self.gaia_properties)

            # results = []

            # # Agrupar clausulas em grupos para diminuir a quantidade de querys
            # for gpos in dao.chunks_positions(positions, self.POSITION_GROUP):

            #     clauses = list()

            #     for pos in gpos:
            #         clauses.append(self.q3c_clause(pos[0], pos[1], radius))

            #     where = " OR ".join(clauses)
            #     stm = """SELECT %s FROM %s WHERE %s """ % (
            #         columns, tablename, where)

            #     print(stm)

            #     rows = self.fetch_all_dict(text(stm))
            #     results += rows

            #     del rows
            #     del clauses

            # return results

            df_results = None

            # Agrupar clausulas em grupos para diminuir a quantidade de querys
            for gpos in dao.chunks_positions(positions, self.POSITION_GROUP):

                clauses = list()

                for pos in gpos:
                    clauses.append(self.q3c_clause(pos[0], pos[1], radius))

                where = " OR ".join(clauses)
                stm = """SELECT %s FROM %s WHERE %s """ % (
                    columns, tablename, where)

                df_rows = pd.read_sql(text(stm), con=self.get_db_engine())

                if df_results is None:
                    df_results = df_rows
                else:
                    # Concatena o resultado da nova query com os resultados anteriores.
                    # Tratando possiveis duplicatas.
                    df_results = pd.concat(
                        [df_results, df_rows]).drop_duplicates().reset_index(drop=True)

                del df_rows
                del clauses

            if df_results.shape[0] >= 2100000:
                pass
                # self.logger.warning("Stellar Catalog too big")
                # TODO marcar o status do Asteroid como warning.
                # TODO implementar funcao para dividir o resutado em lista menores e executar em loop.

            return df_results

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

    df_catalog = dao.catalog_by_positions(positions, radius=0.15)

    print(df_catalog.shape[0])
    print(df_catalog.head())
