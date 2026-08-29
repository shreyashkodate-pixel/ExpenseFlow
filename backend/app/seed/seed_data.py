import logging
from sqlalchemy.orm import Session
from ..core.database import SessionLocal
from ..models.category import Category

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed_data")

STARTER_CATEGORIES = [
    "Food",
    "Transport",
    "Rent",
    "Shopping",
    "Bills",
    "Entertainment",
    "Health",
    "Education",
    "Other",
]


def seed_initial_categories(db: Session) -> None:
    """Idempotently seed default categories into the database."""
    logger.info("Starting initial category seeding...")
    added_count = 0
    for cat_name in STARTER_CATEGORIES:
        existing = db.query(Category).filter(Category.name == cat_name).first()
        if not existing:
            new_cat = Category(name=cat_name)
            db.add(new_cat)
            added_count += 1

    if added_count > 0:
        db.commit()
        logger.info(f"Successfully seeded {added_count} new categories.")
    else:
        logger.info("Starter categories already present. No action required.")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_initial_categories(db)
    finally:
        db.close()
