import re
from ..extensions import db

_TRANSLIT = str.maketrans({
    "а":"a","б":"b","в":"v","г":"g","д":"d","е":"e","ё":"e","ж":"zh","з":"z","и":"i",
    "й":"y","к":"k","л":"l","м":"m","н":"n","о":"o","п":"p","р":"r","с":"s","т":"t",
    "у":"u","ф":"f","х":"h","ц":"c","ч":"ch","ш":"sh","щ":"shch","ъ":"","ы":"y","ь":"",
    "э":"e","ю":"yu","я":"ya"
})

def slugify(value):
    value = (value or "").strip().lower().translate(_TRANSLIT)
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value or "catalog"

class Store(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(160), unique=True, nullable=False, default="catalog")
    name = db.Column(db.String(120), nullable=False, default="Мой каталог")
    whatsapp_number = db.Column(db.String(30), nullable=False, default="")
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True, nullable=False)
    owner = db.relationship("User", back_populates="store")
    categories = db.relationship("Category", back_populates="store", cascade="all, delete-orphan")

    @staticmethod
    def make_unique_slug(name, current_store_id=None):
        base = slugify(name)
        slug = base
        n = 2
        while True:
            q = Store.query.filter_by(slug=slug)
            if current_store_id:
                q = q.filter(Store.id != current_store_id)
            if not q.first():
                return slug
            slug = f"{base}-{n}"
            n += 1
