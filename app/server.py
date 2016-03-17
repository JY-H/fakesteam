import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

class test_server:
    def __init__(self):
        self.DATABASEURI = "sqlite:///test.db"
        self.engine = self.init_db()

    def init_db(self):
        # The following uses the sqlite3 database test.db -- you can use this for debugging purposes
        # However for the project you will need to connect to your Part 2 database in order to use the
        # data
        #
        # XXX: The URI should be in the format of:
        #
        #     postgresql://USER:PASSWORD@w4111db.eastus.cloudapp.azure.com/username
        #
        # For example, if you had username ewu2493, password foobar, then the following line would be:
        #
        #     DATABASEURI = "postgresql://ewu2493:foobar@w4111db.eastus.cloudapp.azure.com/ewu2493"
        #


        #
        # This line creates a database engine that knows how to connect to the URI above
        #
        engine = create_engine(self.DATABASEURI)

        engine.execute("""DROP TABLE IF EXISTS test;""")
        engine.execute("""CREATE TABLE IF NOT EXISTS test (
          id serial,
          name text
        );""")
        engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")

        return engine


class fakesteam_server:
    def __init__(self):
        self.DATABASEURI = "postgresql://jh3541:ZNTPYR@w4111db.eastus.cloudapp.azure.com/jh3541"
        self.engine = self.init_db()

    def init_db(self):
        engine = create_engine(self.DATABASEURI)

        return engine