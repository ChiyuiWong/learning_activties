from mongoengine import Document, StringField, DateTimeField, ListField, ReferenceField, IntField, BooleanField, EmbeddedDocument, EmbeddedDocumentField
from datetime import datetime

# Option model as embedded document
class Option(EmbeddedDocument):
	text = StringField(required=True)
	votes = IntField(default=0)

# Poll model
class Poll(Document):
	question = StringField(required=True, max_length=300)
	options = ListField(EmbeddedDocumentField(Option), required=True)
	created_by = StringField(required=True)  # teacher user_id
	is_active = BooleanField(default=True)
	created_at = DateTimeField(default=datetime.utcnow)
	expires_at = DateTimeField()
	course_id = StringField(required=True)

	meta = {
		'collection': 'polls',
		'indexes': ['course_id', 'created_by', 'is_active', 'expires_at']
	}

# Vote model
class Vote(Document):
	poll = ReferenceField(Poll, required=True, reverse_delete_rule=2)  # CASCADE
	student_id = StringField(required=True)
	option_index = IntField(required=True)  # index of the chosen option
	voted_at = DateTimeField(default=datetime.utcnow)

	meta = {
		'collection': 'votes',
		'indexes': [
			{'fields': ['poll', 'student_id'], 'unique': True},  # Prevent multiple votes per poll per student
			'poll',
			'student_id'
		]
	}

