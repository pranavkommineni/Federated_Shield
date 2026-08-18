"""Database configuration, engine setup, and session lifecycle management."""

import logging
import random
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from app.config import settings

logger = logging.getLogger(__name__)

# SQLite connection configuration
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False,
)

# Create session maker factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base model class
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency for obtaining database sessions per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all database tables and seed default role users and organizations if empty."""
    try:
        import app.models  # noqa: F401
        from app.models.org import Organization
        from app.models.user import User
        from app.models.dataset import LocalDataset, ClinicalSample

        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully.")

        # Seed initial data for out-of-the-box multi-role testing
        db = SessionLocal()
        try:
            # 1. Seed Organizations
            if db.query(Organization).count() == 0:
                org1 = Organization(name="Hospital Alpha (Cardiology)", description="Regional Cardiology Edge Silo", status="idle")
                org2 = Organization(name="Medical Center Beta (Oncology)", description="Oncology Clinical Research Node", status="idle")
                org3 = Organization(name="Apex Health Network", description="Multi-Specialty Diagnostics Silo", status="idle")
                db.add_all([org1, org2, org3])
                db.commit()
                logger.info("Seeded default organizations.")

            # 2. Seed Users across all 4 roles
            if db.query(User).count() == 0:
                org_alpha = db.query(Organization).filter(Organization.name.like("%Alpha%")).first()
                org_beta = db.query(Organization).filter(Organization.name.like("%Beta%")).first()
                alpha_id = org_alpha.id if org_alpha else None
                beta_id = org_beta.id if org_beta else None

                users = [
                    User(username="admin", full_name="Global FL Coordinator", email="admin@federix.shield", role="admin", department="Federated Learning Core"),
                    User(username="org_lead_alpha", full_name="Dr. Rajesh Varma", email="varma@hospital-alpha.org", role="org_admin", org_id=alpha_id, department="Cardiology Division"),
                    User(username="org_lead_beta", full_name="Dr. Elena Rostova", email="elena@med-beta.org", role="org_admin", org_id=beta_id, department="Oncology Division"),
                    User(username="staff_dr_sharma", full_name="Aarav Sharma", email="sharma.data@hospital-alpha.org", role="staff", org_id=alpha_id, department="Data Engineering & Imaging"),
                    User(username="customer_dr_doe", full_name="Dr. Sarah Jenkins", email="jenkins.md@metro-health.org", role="customer", department="Cardiovascular Outpatient Clinic"),
                ]
                db.add_all(users)
                db.commit()
                logger.info("Seeded default users for Admin, Org Admin, Staff, and Customer roles.")

            # 3. Seed Clinical Samples for edge silos
            if db.query(ClinicalSample).count() == 0:
                all_orgs = db.query(Organization).all()
                samples = []
                for org in all_orgs:
                    for i in range(12):
                        age = random.randint(32, 75)
                        bp = random.randint(110, 165)
                        chol = random.randint(160, 280)
                        gluc = random.randint(80, 160)
                        hr = random.randint(60, 95)
                        risk = round(min(0.92, max(0.08, (bp / 200) * 0.4 + (chol / 300) * 0.4)), 3)
                        sample = ClinicalSample(
                            org_id=org.id,
                            patient_identifier_hash=f"PT-{org.id:02d}{i:03d}",
                            age=age,
                            gender="Male" if i % 2 == 0 else "Female",
                            blood_pressure_sys=bp,
                            cholesterol=chol,
                            glucose=gluc,
                            heart_rate=hr,
                            target_risk=risk,
                            contributed_by="staff_dr_sharma",
                        )
                        samples.append(sample)
                db.add_all(samples)
                db.commit()
                logger.info("Seeded initial edge clinical samples.")

        except Exception as seed_err:
            db.rollback()
            logger.warning(f"Note during database seeding: {seed_err}")
        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error initializing database tables: {e}", exc_info=True)
        raise
