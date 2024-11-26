class Config:
    SQLALCHEMY_DATABASE_URI = (
        "mssql+pyodbc://sqlhanggame:HangG%40me1@hanggame.database.windows.net:1433/hang?driver=ODBC+Driver+18+for+SQL+Server"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
