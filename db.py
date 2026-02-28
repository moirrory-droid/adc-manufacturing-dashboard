import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text


@st.cache_resource
def get_engine():
    """Create and cache a SQLAlchemy engine for the session."""
    cfg = st.secrets["postgres"]
    url = (
        f"postgresql+psycopg2://{cfg['user']}:{cfg['password']}"
        f"@{cfg['host']}:{cfg['port']}/{cfg['dbname']}"
    )
    return create_engine(url)


def run_query(sql: str, params: dict = None) -> pd.DataFrame:
    """Execute a parameterised SELECT and return a DataFrame."""
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql_query(text(sql), conn, params=params)
