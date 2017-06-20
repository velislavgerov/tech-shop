from app import db

class Test(db.Model):
    __tablename__ = 'test'

    test = db.Column(db.Text, primary_key=True)
    
    @staticmethod
    def get_all():
        return Test.query.all()

    def __repr__(self):
        return '<Test: {}>'.format(self.test)
