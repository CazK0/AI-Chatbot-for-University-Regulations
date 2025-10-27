from datetime import datetime
import uuid

class ChatSession:
    def __init__(self, session_id=None):
        self.session_id = session_id or str(uuid.uuid4())
        self.created_at = self.last_activity = datetime.now()
        self.messages = []
        self.user_context = {}

    def add_message(self, user_message, bot_response, intent=None):
        message_data = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.now(),
            'user_message': user_message,
            'bot_response': bot_response,
            'intent': intent
        }
        self.messages.append(message_data)
        self.last_activity = datetime.now()
        return message_data

    def get_conversation_history(self, limit=None):
        return self.messages[-limit:] if limit else self.messages

    def clear_history(self):
        self.messages = []
        self.last_activity = datetime.now()

    def set_user_context(self, key, value):
        self.user_context[key] = value

    def get_user_context(self, key, default=None):
        return self.user_context.get(key, default)

    def to_dict(self):
        return {
            'session_id': self.session_id,
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'message_count': len(self.messages),
            'user_context': self.user_context
        }

class KnowledgeBase:
    def __init__(self):
        self.documents = {}
        self.last_updated = datetime.now()

    def add_document(self, doc_id, title, content):
        self.documents[doc_id] = {
            'title': title,
            'content': content,
            'added_at': datetime.now(),
            'document_id': doc_id
        }
        self.last_updated = datetime.now()

    def get_document(self, doc_id):
        return self.documents.get(doc_id)

    def search_documents(self, query):
        results = []
        query_lower = query.lower()
        for doc_id, doc_data in self.documents.items():
            if (query_lower in doc_data['title'].lower() or
                    query_lower in doc_data['content'].lower()):
                results.append({
                    'document_id': doc_id,
                    'title': doc_data['title'],
                    'content': doc_data['content'][:500]
                })
        return results

    def get_all_documents(self):
        return self.documents