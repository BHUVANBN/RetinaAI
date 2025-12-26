from pymongo import MongoClient
from django.conf import settings
from datetime import datetime
import hashlib
import secrets
import logging

logger = logging.getLogger(__name__)

class MongoDBManager:
    def __init__(self):
        self.client = MongoClient(settings.MONGODB_URI)
        self.db = self.client['DR']
        self.users = self.db['users']
        self.analyses = self.db['analyses']
        
        # Create indexes for better performance
        self._create_indexes()
    
    def _create_indexes(self):
        """Create database indexes for better query performance"""
        try:
            # Index for user analyses queries
            self.analyses.create_index([('user_id', 1), ('created_at', -1)])
            
            # Index for stats queries
            self.analyses.create_index([('prediction_result', 1)])
            self.analyses.create_index([('created_at', -1)])
            
            # Index for user lookups
            self.users.create_index([('username', 1)], unique=True)
            self.users.create_index([('email', 1)], unique=True)
        except Exception as e:
            logger.warning(f"Could not create indexes: {e}")
        
    def hash_password(self, password):
        """Hash password using SHA-256 with salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return password_hash, salt
    
    def verify_password(self, password, stored_hash, salt):
        """Verify password against stored hash"""
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return password_hash == stored_hash
    
    def create_user(self, username, email, password):
        """Create a new user in MongoDB"""
        try:
            # Check if user already exists
            if self.users.find_one({'username': username}):
                return False, "Username already exists"
            if self.users.find_one({'email': email}):
                return False, "Email already exists"
            
            # Hash password
            password_hash, salt = self.hash_password(password)
            
            # Create user document
            user_doc = {
                'username': username,
                'email': email,
                'password_hash': password_hash,
                'salt': salt,
                'created_at': datetime.utcnow(),
                'is_active': True,
                'profile': {
                    'first_name': '',
                    'last_name': '',
                    'phone': '',
                    'date_of_birth': None
                }
            }
            
            # Insert user
            result = self.users.insert_one(user_doc)
            return True, str(result.inserted_id)
            
        except Exception as e:
            return False, str(e)
    
    def authenticate_user(self, username, password):
        """Authenticate user credentials"""
        try:
            # Find user by username or email
            user = self.users.find_one({
                '$or': [
                    {'username': username},
                    {'email': username}
                ]
            })
            
            if not user:
                return None, "Invalid credentials"
            
            if not user.get('is_active', True):
                return None, "Account is disabled"
            
            # Verify password
            if self.verify_password(password, user['password_hash'], user['salt']):
                # Convert ObjectId to string for session
                user['_id'] = str(user['_id'])
                return user, "Authentication successful"
            else:
                return None, "Invalid credentials"
                
        except Exception as e:
            return None, str(e)
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        try:
            from bson.objectid import ObjectId
            user = self.users.find_one({'_id': ObjectId(user_id)})
            if user:
                user['_id'] = str(user['_id'])
                return user
            return None
        except Exception as e:
            return None
    
    def update_user_profile(self, user_id, profile_data):
        """Update user profile information"""
        try:
            from bson.objectid import ObjectId
            result = self.users.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': {'profile': profile_data}}
            )
            return result.modified_count > 0
        except Exception as e:
            return False
    
    def save_analysis(self, user_id, image_path, prediction_result, confidence_scores):
        """Save analysis result to MongoDB"""
        try:
            from bson.objectid import ObjectId
            
            analysis_doc = {
                'user_id': ObjectId(user_id),
                'image_path': image_path,
                'prediction_result': prediction_result,
                'confidence_scores': confidence_scores,
                'created_at': datetime.utcnow(),
                'status': 'completed'
            }
            
            result = self.analyses.insert_one(analysis_doc)
            return str(result.inserted_id)
            
        except Exception as e:
            return None
    
    def get_user_analyses(self, user_id, limit=10):
        """Get user's analysis history"""
        try:
            from bson.objectid import ObjectId
            from datetime import datetime
            
            analyses = list(self.analyses.find(
                {'user_id': ObjectId(user_id)}
            ).sort('created_at', -1).limit(limit))
            
            # Convert ObjectId to string and handle datetime
            for analysis in analyses:
                analysis['_id'] = str(analysis['_id'])
                analysis['user_id'] = str(analysis['user_id'])
                
                # Convert MongoDB datetime to Python datetime if needed
                if 'created_at' in analysis and hasattr(analysis['created_at'], 'strftime'):
                    # It's already a datetime object, keep it as is
                    pass
                elif 'created_at' in analysis:
                    # Convert to datetime if it's not already
                    analysis['created_at'] = datetime.fromtimestamp(analysis['created_at'].timestamp())
                
            return analyses
        except Exception as e:
            return []
    
    def get_analysis_stats_fast(self):
        """Get simplified analysis statistics for faster loading"""
        try:
            # Use count_documents with index - much faster than distinct
            total_analyses = self.analyses.count_documents({})
            
            # For unique users, use a simple count estimate instead of distinct
            # This is much faster for large collections
            unique_users_estimate = min(100, max(1, total_analyses // 10))  # Simple estimation
            
            return {
                'total_analyses': total_analyses,
                'unique_users': unique_users_estimate,
            }
        except Exception as e:
            return {
                'total_analyses': 0,
                'unique_users': 0,
            }
    
    def get_analysis_stats(self):
        """Get overall analysis statistics"""
        try:
            total_analyses = self.analyses.count_documents({})
            unique_users = self.analyses.distinct('user_id')
            
            # Get prediction result distribution
            pipeline = [
                {'$group': {'_id': '$prediction_result', 'count': {'$sum': 1}}},
                {'$sort': {'count': -1}}
            ]
            distribution = list(self.analyses.aggregate(pipeline))
            
            return {
                'total_analyses': total_analyses,
                'unique_users': len(unique_users),
                'distribution': distribution
            }
        except Exception as e:
            return {
                'total_analyses': 0,
                'unique_users': 0,
                'distribution': []
            }

# Global MongoDB manager instance
mongodb_manager = MongoDBManager()
