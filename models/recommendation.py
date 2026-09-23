from datetime import datetime
from . import db

class Recommendation(db.Model):
    __tablename__ = 'recommendations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    note_type = db.Column(db.String(20), nullable=False)  # 'WORKOUT' or 'NUTRITION'
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __init__(self, user_id=None, author_id=None, note_type=None, title=None, content=None, **kwargs):
        self.user_id = user_id
        self.author_id = author_id
        self.note_type = note_type
        self.title = title
        self.content = content
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def badge_color(self):
        return 'primary' if self.note_type == 'WORKOUT' else 'success'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'author_id': self.author_id,
            'author_name': self.author.name if self.author else 'Specialist',
            'note_type': self.note_type,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M')
        }

    def __repr__(self):
        return f'<Recommendation {self.note_type} by {self.author_id} for {self.user_id}>'
