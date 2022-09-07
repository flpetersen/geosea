import sqlite3
import pandas as pd


def sql2df (name, pathname):

    conn = sqlite3.connect(pathname + str(name) + '.sqlite')

    df = pd.read_sql('SELECT * FROM "network"', conn).set_index(['node_id','rec_time'])

    return (df)


def df2sql (df, name, pathname):

    conn = sqlite3.connect(pathname + str(name) + '.sqlite')

    df.to_sql('network', conn)