import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


@st.cache_resource
def get_engine():
    """Create and cache a SQLAlchemy engine for the session."""
    cfg = st.secrets["postgres"]
    url = URL.create(
        drivername="postgresql+psycopg2",
        username=cfg["user"],
        password=cfg["password"],
        host=cfg["host"],
        port=int(cfg["port"]),
        database=cfg["dbname"],
    )
    return create_engine(url, connect_args={"sslmode": "require"})


def run_query(sql: str, params: dict = None) -> pd.DataFrame:
    """Execute a parameterised SELECT and return a DataFrame."""
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql_query(text(sql), conn, params=params)
