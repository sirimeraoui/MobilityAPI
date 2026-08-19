import duckdb

print(duckdb.__version__)

con = duckdb.connect(
        "../mobilityapi.duckdb",
        config={
            "allow_unsigned_extensions": "true"
        },
    )

con.load_extension(
    "../extensions/mobilityduck.duckdb_extension"
)


print(con.execute("SHOW TABLES").fetchall())
print(con.execute("SELECT * FROM COLLECTIONS").fetchall())
