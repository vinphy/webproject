from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import pymysql

MYSQL_HOST = os.environ.get("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = os.environ.get("MYSQL_PORT", "3306")
MYSQL_DB = os.environ.get("MYSQL_DB", "webproject")
MYSQL_USER = os.environ.get("MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "123456")

DATABASE_URL = (
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_database_exists():
    try:
        conn = pymysql.connect(host=MYSQL_HOST, port=int(MYSQL_PORT), user=MYSQL_USER, password=MYSQL_PASSWORD, charset="utf8mb4")
        try:
            with conn.cursor() as cur:
                cur.execute(f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DB}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;")
            conn.commit()
        finally:
            conn.close()
    except Exception as e:
        print(f"[DB INIT] ensure_database_exists failed: {e}")
        raise


def ensure_users_schema():
    try:
        conn = pymysql.connect(host=MYSQL_HOST, port=int(MYSQL_PORT), user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DB, charset="utf8mb4")
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cur:
                cur.execute("""
                    SELECT COLUMN_NAME FROM information_schema.COLUMNS 
                    WHERE TABLE_SCHEMA=%s AND TABLE_NAME='users'
                """, (MYSQL_DB,))
                existing = {row['COLUMN_NAME'] for row in cur.fetchall()}
                if not existing:
                    return  # table may not exist yet; SQLAlchemy will create
                # columns to ensure
                migrations = []
                if 'hashed_password' not in existing:
                    migrations.append("ADD COLUMN `hashed_password` VARCHAR(255) NOT NULL AFTER `email`")
                if 'is_active' not in existing:
                    migrations.append("ADD COLUMN `is_active` TINYINT(1) NOT NULL DEFAULT 1 AFTER `hashed_password`")
                if 'role_id' not in existing:
                    migrations.append("ADD COLUMN `role_id` INT NULL AFTER `is_active`")
                if 'created_at' not in existing:
                    migrations.append("ADD COLUMN `created_at` DATETIME NULL AFTER `role_id`")
                # add unique indexes if missing
                if 'username' in existing:
                    cur.execute("SHOW INDEX FROM `users` WHERE Key_name='uq_users_username'")
                    if cur.fetchone() is None:
                        migrations.append("ADD UNIQUE KEY `uq_users_username` (`username`)")
                if 'email' in existing:
                    cur.execute("SHOW INDEX FROM `users` WHERE Key_name='uq_users_email'")
                    if cur.fetchone() is None:
                        migrations.append("ADD UNIQUE KEY `uq_users_email` (`email`)")
                if migrations:
                    alter_sql = "ALTER TABLE `users` " + ", ".join(migrations) + ";"
                    cur.execute(alter_sql)
                    conn.commit()
        finally:
            conn.close()
    except Exception as e:
        print(f"[DB INIT] ensure_users_schema failed: {e}")
        # don't re-raise to avoid blocking startup


def init_db(metadata_base: Base.__class__):
    ensure_database_exists()
    metadata_base.metadata.create_all(bind=engine)
    ensure_users_schema() 