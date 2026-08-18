"""SQLAlchemy database engine, sessions, and initial schema migration."""

import json
import random
import logging
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

logger = logging.getLogger(__name__)

# Use SQLite path from config or fallback
DATABASE_URL = settings.DATABASE_URL

# SQLite requires check_same_thread=False for FastAPI concurrency
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db():
    """FastAPI Dependency for obtaining a transactional database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db(force_reseed: bool = False):
    """Initializes tables and seeds development data with Indian healthcare entities."""
    from app.models.org import Organization
    from app.models.user import User
    from app.models.dataset import LocalDataset, ClinicalSample
    from app.models.round import RoundHistory

    try:
        if force_reseed:
            Base.metadata.drop_all(bind=engine)
            logger.info("Existing database tables dropped for reseed.")

        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully.")

        db = SessionLocal()
        try:
            # 1. Seed Organizations if empty or force_reseed
            if db.query(Organization).count() == 0:
                org1 = Organization(
                    name="AIIMS New Delhi (Cardiology)",
                    description="National apex cardiology institute with local differential privacy.",
                    status="idle",
                )
                org2 = Organization(
                    name="Apollo Hospitals Chennai (Oncology)",
                    description="Comprehensive oncology clinical research node with secure aggregation.",
                    status="idle",
                )
                org3 = Organization(
                    name="Fortis Healthcare Bengaluru (Neurology)",
                    description="Multi-specialty neurology diagnostics silo with Shamir secret sharing.",
                    status="idle",
                )
                db.add_all([org1, org2, org3])
                db.commit()
                db.refresh(org1)
                db.refresh(org2)
                db.refresh(org3)
                logger.info("Seeded Indian healthcare organizations.")
            else:
                org1 = db.query(Organization).first()
                org2 = db.query(Organization).offset(1).first()
                org3 = db.query(Organization).offset(2).first()

            # 2. Seed Users
            if db.query(User).count() == 0 and org1 and org2:
                users = [
                    User(
                        username="admin",
                        full_name="Dr. Ananya Sharma",
                        email="ananya.sharma@federatedshield.gov.in",
                        role="admin",
                        department="National Medical AI Directorate",
                    ),
                    User(
                        username="org_lead_aiims",
                        full_name="Dr. Rajesh Varma",
                        email="rajesh.varma@aiims.edu.in",
                        role="org_admin",
                        org_id=org1.id,
                        department="Cardiology Division & Health Informatics",
                    ),
                    User(
                        username="org_lead_apollo",
                        full_name="Dr. Vikram Rao",
                        email="vikram.rao@apollohospitals.com",
                        role="org_admin",
                        org_id=org2.id,
                        department="Radiation Oncology Department",
                    ),
                    User(
                        username="dr_priya_nair",
                        full_name="Dr. Priya Nair",
                        email="priya.nair@aiims.edu.in",
                        role="staff",
                        org_id=org1.id,
                        department="Cardiovascular Diagnostics",
                    ),
                    User(
                        username="dr_rohan_m",
                        full_name="Dr. Rohan Mehta",
                        email="rohan.mehta@aiims.edu.in",
                        role="staff",
                        org_id=org1.id,
                        department="Interventional Cardiology",
                    ),
                    User(
                        username="intern_aarav",
                        full_name="Aarav Patel",
                        email="aarav.patel@aiims.edu.in",
                        role="staff",
                        org_id=org1.id,
                        department="Cardiology Resident",
                    ),
                    User(
                        username="nurse_sunita",
                        full_name="Sunita Deshmukh",
                        email="sunita.deshmukh@aiims.edu.in",
                        role="staff",
                        org_id=org1.id,
                        department="Clinical ICU Lead",
                    ),
                    User(
                        username="researcher_kavita",
                        full_name="Dr. Kavita Krishnan",
                        email="kavita.k@apollohospitals.com",
                        role="staff",
                        org_id=org2.id,
                        department="Clinical Data Research",
                    ),
                ]
                db.add_all(users)
                db.commit()
                logger.info("Seeded Indian healthcare users.")

            # 3. Seed Datasets
            if db.query(LocalDataset).count() == 0 and org1 and org2 and org3:
                d1 = LocalDataset(
                    org_id=org1.id,
                    name="AIIMS ECG & Cardiovascular Tabular Cohort",
                    modality="tabular_clinical",
                    sample_count=1420,
                    features_schema=json.dumps(["age", "blood_pressure_sys", "cholesterol", "glucose", "heart_rate", "target_risk"]),
                    privacy_status="noise_calibrated (Gaussian σ=1.15)",
                )
                d2 = LocalDataset(
                    org_id=org2.id,
                    name="Apollo Oncology Tumor Response Registry",
                    modality="tabular_clinical",
                    sample_count=980,
                    features_schema=json.dumps(["age", "tumor_marker", "chemo_response", "target_risk"]),
                    privacy_status="noise_calibrated (Gaussian σ=1.15)",
                )
                d3 = LocalDataset(
                    org_id=org3.id,
                    name="Fortis Neurological EEG Biomarkers",
                    modality="tabular_clinical",
                    sample_count=650,
                    features_schema=json.dumps(["age", "eeg_alpha_power", "motor_response", "target_risk"]),
                    privacy_status="noise_calibrated (Gaussian σ=1.15)",
                )
                db.add_all([d1, d2, d3])
                db.commit()

            # 4. Seed Clinical Samples
            if db.query(ClinicalSample).count() == 0:
                all_orgs = db.query(Organization).all()
                samples = []
                for org in all_orgs:
                    for i in range(15):
                        age = random.randint(35, 76)
                        bp = random.randint(112, 168)
                        chol = random.randint(165, 275)
                        gluc = random.randint(85, 155)
                        hr = random.randint(62, 92)
                        risk = round(min(0.92, max(0.08, (bp / 200) * 0.4 + (chol / 300) * 0.4)), 3)
                        s = ClinicalSample(
                            org_id=org.id,
                            patient_identifier_hash=f"IND-{org.id:02d}{i:03d}",
                            age=age,
                            gender="Male" if i % 2 == 0 else "Female",
                            blood_pressure_sys=bp,
                            cholesterol=chol,
                            glucose=gluc,
                            heart_rate=hr,
                            target_risk=risk,
                            contributed_by="dr_priya_nair",
                        )
                        samples.append(s)
                db.add_all(samples)
                db.commit()

            # 5. Seed Training History Rounds
            if db.query(RoundHistory).count() == 0:
                now = datetime.utcnow()
                rounds = [
                    RoundHistory(
                        run_id="fl_run_alpha_01",
                        round_number=1,
                        total_rounds=5,
                        accuracy=0.542,
                        loss=1.821,
                        epsilon_spent=0.44,
                        cumulative_epsilon=0.44,
                        participating_orgs=["AIIMS New Delhi (Cardiology)", "Apollo Hospitals Chennai (Oncology)"],
                        org_statuses={"AIIMS New Delhi (Cardiology)": "completed", "Apollo Hospitals Chennai (Oncology)": "completed"},
                        duration_seconds=2.4,
                        status="completed",
                        timestamp=now - timedelta(minutes=10),
                    ),
                    RoundHistory(
                        run_id="fl_run_alpha_01",
                        round_number=2,
                        total_rounds=5,
                        accuracy=0.695,
                        loss=1.248,
                        epsilon_spent=0.45,
                        cumulative_epsilon=0.89,
                        participating_orgs=["AIIMS New Delhi (Cardiology)", "Apollo Hospitals Chennai (Oncology)"],
                        org_statuses={"AIIMS New Delhi (Cardiology)": "completed", "Apollo Hospitals Chennai (Oncology)": "completed"},
                        duration_seconds=2.5,
                        status="completed",
                        timestamp=now - timedelta(minutes=8),
                    ),
                    RoundHistory(
                        run_id="fl_run_alpha_01",
                        round_number=3,
                        total_rounds=5,
                        accuracy=0.791,
                        loss=0.879,
                        epsilon_spent=0.46,
                        cumulative_epsilon=1.35,
                        participating_orgs=["AIIMS New Delhi (Cardiology)", "Apollo Hospitals Chennai (Oncology)", "Fortis Healthcare Bengaluru (Neurology)"],
                        org_statuses={"AIIMS New Delhi (Cardiology)": "completed", "Apollo Hospitals Chennai (Oncology)": "completed", "Fortis Healthcare Bengaluru (Neurology)": "completed"},
                        duration_seconds=2.4,
                        status="completed",
                        timestamp=now - timedelta(minutes=6),
                    ),
                    RoundHistory(
                        run_id="fl_run_alpha_01",
                        round_number=4,
                        total_rounds=5,
                        accuracy=0.874,
                        loss=0.548,
                        epsilon_spent=0.45,
                        cumulative_epsilon=1.80,
                        participating_orgs=["AIIMS New Delhi (Cardiology)", "Apollo Hospitals Chennai (Oncology)", "Fortis Healthcare Bengaluru (Neurology)"],
                        org_statuses={"AIIMS New Delhi (Cardiology)": "completed", "Apollo Hospitals Chennai (Oncology)": "completed", "Fortis Healthcare Bengaluru (Neurology)": "completed"},
                        duration_seconds=2.5,
                        status="completed",
                        timestamp=now - timedelta(minutes=4),
                    ),
                    RoundHistory(
                        run_id="fl_run_alpha_01",
                        round_number=5,
                        total_rounds=5,
                        accuracy=0.924,
                        loss=0.318,
                        epsilon_spent=0.44,
                        cumulative_epsilon=2.24,
                        participating_orgs=["AIIMS New Delhi (Cardiology)", "Apollo Hospitals Chennai (Oncology)", "Fortis Healthcare Bengaluru (Neurology)"],
                        org_statuses={"AIIMS New Delhi (Cardiology)": "completed", "Apollo Hospitals Chennai (Oncology)": "completed", "Fortis Healthcare Bengaluru (Neurology)": "completed"},
                        duration_seconds=2.6,
                        status="completed",
                        timestamp=now - timedelta(minutes=2),
                    ),
                ]
                for r in rounds:
                    r.participating_orgs = r.participating_orgs
                    r.org_statuses = r.org_statuses
                db.add_all(rounds)
                db.commit()
                logger.info("Seeded initial 5 training rounds.")

        except Exception as seed_err:
            db.rollback()
            logger.warning(f"Data seeding encountered note: {seed_err}")
        finally:
            db.close()

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise e
