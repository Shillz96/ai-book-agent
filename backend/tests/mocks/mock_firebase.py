"""Mock Firebase service for testing."""

class MockFirestore:
    """Mock Firestore client."""
    
    def __init__(self):
        self._data = {}
    
    def collection(self, name):
        """Get a collection reference."""
        if name not in self._data:
            self._data[name] = {}
        return MockCollection(self._data[name])

class MockCollection:
    """Mock Firestore collection."""
    
    def __init__(self, data):
        self._data = data
    
    def document(self, doc_id):
        """Get a document reference."""
        if doc_id not in self._data:
            self._data[doc_id] = {}
        return MockDocument(self._data[doc_id])

class MockDocument:
    """Mock Firestore document."""
    
    def __init__(self, data):
        self._data = data
        self.exists = bool(data)
    
    def get(self):
        """Get document data."""
        return self
    
    def set(self, data, merge=False):
        """Set document data."""
        if merge:
            self._data.update(data)
        else:
            self._data = data.copy()
        self.exists = True
    
    def to_dict(self):
        """Convert document to dictionary."""
        return self._data.copy()

class MockFirebaseService:
    """Mock Firebase service for testing."""
    
    def __init__(self):
        self.db = MockFirestore()
        self._initialized = True
    
    @property
    def initialized(self):
        """Check if Firebase is initialized."""
        return self._initialized 