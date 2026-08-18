"""Comprehensive database seeding script for Federated Shield."""

import os
import sys
import json
import random
from datetime import datetime, timedelta

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base, SessionLocal
from app.models.org import Organization
from app.models.user import User
from app.models.dataset import LocalDataset, ClinicalSample
from app.models.round import RoundHistory


def seed_database():
    """Wipes and seeds the SQLite database with Indian healthcare entities and training history."""
    print("Initializing tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Tables created.")

    db = SessionLocal()
    try:
        # 1. Seed Organizations
        org1 = Organization(
            name="AIIMS New Delhi (Cardiology)",
            description="National apex cardiology institute with local differential privacy.",
            status="idle",
        )
        org2 = Organization(
            name="Apollo Hospitals Chennai (Oncology)",
            description="Comprehensive oncology clinical research node with secure multi-party aggregation.",
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
        print(f"Seeded Organizations: {org1.name}, {org2.name}, {org3.name}")

        # 2. Seed Users
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
                username="org_lead_fortis",
                full_name="Dr. Meera Sengupta",
                email="meera.s@fortishealthcare.com",
                role="org_admin",
                org_id=org3.id,
                department="Neuro-Diagnostics & Imaging",
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
        print(f"Seeded {len(users)} Indian healthcare users & clinicians.")

        # 3. Seed Datasets
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
        print("Seeded Local Datasets.")

        # 4. Seed Clinical Samples
        samples = []
        for org in [org1, org2, org3]:
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
                    contributed_by="dr_priya_nair" if org.id == 1 else "researcher_kavita",
                )
                samples.append(s)
        db.add_all(samples)
        db.commit()
        print(f"Seeded {len(samples)} private clinical records.")

        # 5. Seed Training History Rounds
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
        print("Seeded 5 baseline federated training convergence rounds.")

        print("\nDatabase seeded successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
