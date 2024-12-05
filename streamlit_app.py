import streamlit as st
import sqlite3
from PIL import Image
import os
from datetime import datetime
import pandas as pd

# Set page config
st.set_page_config(
    page_title="Image Gallery",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database connection
@st.cache_resource
def get_database_connection():
    return sqlite3.connect('image_tags.sqlite', check_same_thread=False)

# Load all tags
def load_all_tags(conn):
    return pd.read_sql_query("SELECT DISTINCT name FROM tags ORDER BY name", conn)['name'].tolist()

# Load images with filters
def load_images(conn, selected_tags=None, date_range=None, filename_search=None):
    query = """
        SELECT DISTINCT 
            i.id, 
            i.file_path, 
            i.original_filename, 
            i.created_at,
            i.md5_hash,
            GROUP_CONCAT(t.name) as tags
        FROM images i
        LEFT JOIN image_tags it ON i.id = it.image_id
        LEFT JOIN tags t ON it.tag_id = t.id
    """
    
    conditions = []
    params = []
    
    if selected_tags:
        placeholders = ','.join(['?' for _ in selected_tags])
        conditions.append(f"""
            i.id IN (
                SELECT image_id 
                FROM image_tags it2 
                JOIN tags t2 ON it2.tag_id = t2.id 
                WHERE t2.name IN ({placeholders})
                GROUP BY image_id 
                HAVING COUNT(DISTINCT t2.name) = {len(selected_tags)}
            )
        """)
        params.extend(selected_tags)
    
    if date_range:
        start_date, end_date = date_range
        conditions.append("DATE(i.created_at) BETWEEN DATE(?) AND DATE(?)")
        params.extend([start_date, end_date])
    
    if filename_search:
        conditions.append("i.original_filename LIKE ?")
        params.append(f"%{filename_search}%")
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " GROUP BY i.id ORDER BY i.created_at DESC"
    
    return pd.read_sql_query(query, conn, params=params)

# Main app
def main():
    conn = get_database_connection()
    
    # Main content
    st.title("Image Gallery")
    
    # Tag filter
    all_tags = load_all_tags(conn)
    selected_tags = st.multiselect("Select Tags", all_tags)
    
    # Date filter
    all_dates = pd.read_sql_query(
        "SELECT MIN(DATE(created_at)) as min_date, MAX(DATE(created_at)) as max_date FROM images",
        conn
    ).iloc[0]
    
    # date_range = st.sidebar.date_input(
    #     "Date Range",
    #     value=(all_dates['min_date'], all_dates['max_date']),
    #     # min_value=all_dates['min_date'],
    #     min_value=datetime(2024, 1, 1),
    #     # max_value=all_dates['max_date']
    #     max_value=datetime(2024, 12, 1)
    # )
    
    # Load filtered images
    df = load_images(conn, selected_tags)
    
    if df.empty:
        st.warning("No images found matching the selected filters.")
        return
    
    # Display images in a grid
    columns = 4
    cols = st.columns(columns)
    for idx, row in df.iterrows():
        col = cols[idx % columns]
        with col:
            try:
                image = Image.open(row['file_path'])
                st.image(
                    image,
                    # caption=row['original_filename'],
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"Error loading image: {row['file_path']}")

if __name__ == "__main__":
    main()
