import sqlite3
from typing import List, Dict
import logging
import os

class DatabaseManager:
    """Manages SQLite database operations for image tags."""

    def __init__(self, db_path: str = "image_tags.sqlite"):
        """Initialize database connection and create tables if they don't exist."""
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._init_database()

    def _init_database(self):
        """Initialize the database schema."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create images table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS images (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        file_path TEXT UNIQUE NOT NULL,
                        md5_hash TEXT UNIQUE NOT NULL,
                        original_filename TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        process_count INTEGER DEFAULT 0
                    )
                """)
                
                # Create tags table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tags (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL
                    )
                """)
                
                # Create image_tags junction table with confidence metrics
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS image_tags (
                        image_id INTEGER,
                        tag_id INTEGER,
                        occurrence_count INTEGER DEFAULT 1,
                        FOREIGN KEY (image_id) REFERENCES images (id),
                        FOREIGN KEY (tag_id) REFERENCES tags (id),
                        UNIQUE(image_id, tag_id)
                    )
                """)
                
                conn.commit()
                self.logger.info("Database initialized successfully")
                
        except sqlite3.Error as e:
            self.logger.error(f"Error initializing database: {e}")
            raise

    def add_image(self, file_path: str, md5_hash: str, original_filename: str) -> int:
        """
        Add an image to the database.
        
        Args:
            file_path: Path where the image is stored
            md5_hash: MD5 hash of the image
            original_filename: Original filename of the image
            
        Returns:
            int: ID of the inserted image
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR IGNORE INTO images (file_path, md5_hash, original_filename)
                    VALUES (?, ?, ?)
                """, (file_path, md5_hash, original_filename))
                
                if cursor.rowcount == 0:  # Image already exists
                    cursor.execute("SELECT id FROM images WHERE md5_hash = ?", (md5_hash,))
                    return cursor.fetchone()[0]
                
                return cursor.lastrowid
                
        except sqlite3.Error as e:
            self.logger.error(f"Error adding image: {e}")
            raise

    def add_tags(self, image_id: int, tags: List[str]):
        """
        Add tags for an image and update confidence metrics.
        
        Args:
            image_id: ID of the image
            tags: List of tags to add
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Increment the process count for the image
                cursor.execute("""
                    UPDATE images 
                    SET process_count = process_count + 1 
                    WHERE id = ?
                """, (image_id,))
                
                for tag in tags:
                    # Insert or get tag
                    cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag,))
                    cursor.execute("SELECT id FROM tags WHERE name = ?", (tag,))
                    tag_id = cursor.fetchone()[0]
                    
                    # Update tag occurrence count or insert new relationship
                    cursor.execute("""
                        INSERT INTO image_tags (image_id, tag_id, occurrence_count)
                        VALUES (?, ?, 1)
                        ON CONFLICT(image_id, tag_id) DO UPDATE SET
                        occurrence_count = occurrence_count + 1
                    """, (image_id, tag_id))

                conn.commit()
                
        except sqlite3.Error as e:
            self.logger.error(f"Error adding tags: {e}")
            raise

    def get_image_tags(self, image_id: int) -> List[dict]:
        """
        Get all tags and their confidence metrics for an image.
        
        Args:
            image_id: ID of the image
            
        Returns:
            List[dict]: List of tags with confidence metrics
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        t.name,
                        it.occurrence_count,
                        i.process_count,
                        CAST(it.occurrence_count AS FLOAT) / i.process_count AS confidence
                    FROM tags t
                    JOIN image_tags it ON t.id = it.tag_id
                    JOIN images i ON it.image_id = i.id
                    WHERE it.image_id = ?
                    ORDER BY confidence DESC
                """, (image_id,))
                
                return [{
                    'name': row[0],
                    'occurrence_count': row[1],
                    'process_count': row[2],
                    'confidence': row[3]
                } for row in cursor.fetchall()]
                
        except sqlite3.Error as e:
            self.logger.error(f"Error getting image tags: {e}")
            raise

    def get_image_by_hash(self, md5_hash: str) -> Dict:
        """
        Get image information by MD5 hash.
        
        Args:
            md5_hash: MD5 hash of the image
            
        Returns:
            Dict: Image information or None if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, file_path, original_filename, created_at
                    FROM images
                    WHERE md5_hash = ?
                """, (md5_hash,))
                
                result = cursor.fetchone()
                if result:
                    return {
                        "id": result[0],
                        "file_path": result[1],
                        "original_filename": result[2],
                        "created_at": result[3]
                    }
                return None
                
        except sqlite3.Error as e:
            self.logger.error(f"Error getting image by hash: {e}")
            raise 