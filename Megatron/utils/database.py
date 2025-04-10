import datetime
import logging
import motor.motor_asyncio

# Global singleton instance
_db_instance = None

class Database:
    def __init__(self, uri, database_name):
        try:
            self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
            self.db = self._client[database_name]
            self.col = self.db.users
            logging.info(f"Database initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing database: {e}")
            self._client = None
            self.db = None
            self.col = None

    @staticmethod
    def get_instance(uri=None, database_name=None):
        """Get the singleton database instance."""
        global _db_instance
        if _db_instance is None and uri and database_name:
            _db_instance = Database(uri, database_name)
        elif _db_instance is not None:
            logging.debug("Returning existing database instance")
        return _db_instance

    def new_user(self, id):
        return dict(
            id=id,
            join_date=datetime.date.today().isoformat()
        )

    async def add_user(self, id):
        if self.col is None:
            logging.warning("Database not available, skipping add_user")
            return
        user = self.new_user(id)
        try:
            await self.col.insert_one(user)
        except Exception as e:
            logging.error(f"Error adding user {id}: {e}")

    async def is_user_exist(self, id):
        if self.col is None:
            return False
        try:
            user = await self.col.find_one({'id': int(id)})
            return True if user else False
        except Exception as e:
            logging.error(f"Error checking if user {id} exists: {e}")
            return False

    async def total_users_count(self):
        if self.col is None:
            logging.warning("Database not available, returning 0 users")
            return 0
        try:
            count = await self.col.count_documents({})
            return count
        except Exception as e:
            logging.error(f"Error getting total users count: {e}")
            return 0

    async def get_all_users(self):
        if self.col is None:
            logging.warning("Database not available, returning empty list")
            return []
        try:
            all_users = self.col.find({})
            return all_users
        except Exception as e:
            logging.error(f"Error getting all users: {e}")
            return []

    async def delete_user(self, user_id):
        if self.col is None:
            logging.warning("Database not available, skipping delete_user")
            return
        try:
            await self.col.delete_many({'id': int(user_id)})
        except Exception as e:
            logging.error(f"Error deleting user {user_id}: {e}")

    async def create_index(self):
        """Create indexes for better query performance."""
        # Skip if database is not available
        if self.col is None:
            logging.warning("Database not available, skipping index creation")
            return

        try:
            # Check if index already exists
            existing_indexes = await self.col.index_information()
            if 'id_1' not in existing_indexes:
                # Create index if it doesn't exist
                await self.col.create_index("id", unique=True, background=True)
                logging.info("Created 'id_1' index successfully")
            else:
                logging.info("Index 'id_1' already exists, skipping creation")

            if 'join_date_1' not in existing_indexes:
                await self.col.create_index("join_date", background=True)
                logging.info("Created 'join_date_1' index successfully")
            else:
                logging.info("Index 'join_date_1' already exists, skipping creation")
        except Exception as e:
            # Log the error but continue - indexes are not critical
            logging.warning(f"Error creating database indexes: {e}")
            logging.info("Continuing without indexes - this may affect performance but not functionality")
