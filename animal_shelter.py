from pymongo import MongoClient
from pymongo.errors import PyMongoError

class AnimalShelter:

    def __init__(self, username, password):
        """
        Initialize MongoDB connection using the user's credentials.
        Enhanced for Milestone Four with:
        - Correct cluster hostname
        - Error handling
        - Safe fallback values
        """
        try:
            # Corrected connection string for your Atlas cluster
            self.client = MongoClient(
                f"mongodb+srv://{username}:{password}@aac-cluster.iluq1oe.mongodb.net/aac?retryWrites=true&w=majority"
            )

            self.database = self.client['aac']
            self.collection = self.database['animals']

        except Exception as e:
            print("Error connecting to MongoDB:", e)
            self.client = None
            self.database = None
            self.collection = None

    # -------------------------------------------------------------
    # CREATE
    # -------------------------------------------------------------
    def create(self, data):
        """
        Insert a new document into the database.
        Returns True/False depending on success.
        """
        if not isinstance(data, dict) or not data:
            print("Create failed: data must be a non-empty dictionary.")
            return False

        try:
            result = self.collection.insert_one(data)
            return True if result.inserted_id else False
        except PyMongoError as e:
            print("Create error:", e)
            return False

    # -------------------------------------------------------------
    # READ (Enhanced for Milestone Four)
    # -------------------------------------------------------------
    def read(self, query, projection=None):
        """
        Read documents from MongoDB.
        Enhancements:
        - Input validation
        - Default projection (only return fields the dashboard uses)
        - Safe empty list return
        - Error handling
        """
        if not isinstance(query, dict):
            print("Read failed: query must be a dictionary.")
            return []

        # Default projection to reduce data transfer
        default_projection = {
            "_id": 0,
            "age_upon_outcome": 1,
            "animal_id": 1,
            "animal_type": 1,
            "breed": 1,
            "color": 1,
            "date_of_birth": 1,
            "datetime": 1,
            "monthyear": 1,
            "name": 1,
            "outcome_subtype": 1,
            "outcome_type": 1,
            "sex_upon_outcome": 1,
            "location_lat": 1,
            "location_long": 1
        }

        try:
            results = list(self.collection.find(query, projection or default_projection))
            return results if results else []
        except PyMongoError as e:
            print("Read error:", e)
            return []

    # -------------------------------------------------------------
    # UPDATE
    # -------------------------------------------------------------
    def update(self, query, new_values):
        """
        Update documents matching the query.
        Returns number of modified documents.
        """
        if not isinstance(query, dict) or not isinstance(new_values, dict):
            print("Update failed: query and new_values must be dictionaries.")
            return 0

        try:
            result = self.collection.update_many(query, {"$set": new_values})
            return result.modified_count
        except PyMongoError as e:
            print("Update error:", e)
            return 0

    # -------------------------------------------------------------
    # DELETE
    # -------------------------------------------------------------
    def delete(self, query):
        """
        Delete documents matching the query.
        Returns number of deleted documents.
        """
        if not isinstance(query, dict):
            print("Delete failed: query must be a dictionary.")
            return 0

        try:
            result = self.collection.delete_many(query)
            return result.deleted_count
        except PyMongoError as e:
            print("Delete error:", e)
            return 0
