from ..extensions import db

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey("store.id"), nullable=False)
    store = db.relationship("Store", back_populates="categories")
    products = db.relationship("Product", back_populates="category", cascade="all, delete-orphan")
