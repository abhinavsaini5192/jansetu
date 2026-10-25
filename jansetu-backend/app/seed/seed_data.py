"""
Database Seeding Script for JanSetu.
Populates jansetu.db with realistic Jharkhand civic data, universities,
industry partners, projects, and impact records.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, engine, Base
from app.core.security import hash_password
from app.models.user import User
from app.models.organization import Organization
from app.models.university_profile import UniversityProfile
from app.models.department import Department
from app.models.capability import Capability
from app.models.challenge import Challenge
from app.models.project import Project
from app.models.proposal import Proposal
from app.models.milestone import Milestone
from app.models.project_risk import ProjectRisk
from app.models.project_partner import ProjectPartner
from app.models.impact_record import ImpactRecord
from app.utils.enums import (
    ChallengeStatus,
    ImpactStatus,
    ImpactType,
    InstitutionCategory,
    MilestoneStatus,
    OrganizationType,
    PartnerStatus,
    PartnerType,
    PriorityLevel,
    ProjectStatus,
    ProposalStatus,
    RiskSeverity,
    RiskStatus,
    SocietalDomain,
    UrgencyLevel,
    UserRole,
    ValidationStatus,
)


def seed_database():
    print("[*] Starting JanSetu Database Seeding...")
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # 1. Users
        users = [
            {
                "email": "admin@jansetu.gov.in",
                "full_name": "Chief Platform Administrator",
                "role": UserRole.PLATFORM_ADMIN,
                "password": "AdminPassword123!",
            },
            {
                "email": "nodal.officer@jharkhand.gov.in",
                "full_name": "Er. Rajesh Verma (Nodal Officer, DWSD)",
                "role": UserRole.GOVERNMENT_ADMIN,
                "password": "GovPassword123!",
            },
            {
                "email": "faculty.bit@mesra.ac.in",
                "full_name": "Dr. Alok Kumar (Professor, BIT Mesra)",
                "role": UserRole.FACULTY,
                "password": "FacultyPassword123!",
            },
            {
                "email": "csr.lead@tatasteel.com",
                "full_name": "Sourav Roy (Chief CSR, Tata Steel Foundation)",
                "role": UserRole.CSR_PARTNER,
                "password": "CsrPassword123!",
            },
            {
                "email": "citizen@jansetu.gov.in",
                "full_name": "Citizen Submitter",
                "role": UserRole.CITIZEN,
                "password": "CitizenPassword123!",
            },
        ]

        created_users = {}
        for u in users:
            existing = db.query(User).filter(User.email == u["email"]).first()
            if not existing:
                user = User(
                    id=str(uuid.uuid4()),
                    email=u["email"],
                    full_name=u["full_name"],
                    password_hash=hash_password(u["password"]),
                    role=u["role"],
                    is_active=True,
                    is_verified=True,
                )
                db.add(user)
                created_users[u["email"]] = user
            else:
                created_users[u["email"]] = existing

        db.flush()
        print(f"[+] Users checked/created: {len(created_users)}")

        # 2. Universities & Capabilities
        cap_water = db.query(Capability).filter(Capability.name == "Water & Fluoride Purification").first()
        if not cap_water:
            cap_water = Capability(
                id=str(uuid.uuid4()),
                name="Water & Fluoride Purification",
                description="Heavy metal chemical adsorption and groundwater telemetry testing.",
                domain=SocietalDomain.WATER,
                keywords="arsenic, fluoride, filtration, adsorption, potable",
                is_active=True,
            )
            db.add(cap_water)

        cap_agri = db.query(Capability).filter(Capability.name == "Plant Pathology & Bio-Pesticides").first()
        if not cap_agri:
            cap_agri = Capability(
                id=str(uuid.uuid4()),
                name="Plant Pathology & Bio-Pesticides",
                description="Bio-control of bacterial leaf blight and drought micro-irrigation.",
                domain=SocietalDomain.AGRICULTURE,
                keywords="blight, bio-pesticide, paddy, drip, irrigation",
                is_active=True,
            )
            db.add(cap_agri)

        db.flush()

        universities_data = [
            {
                "name": "Birla Institute of Technology (BIT) Mesra",
                "code": "BIT-MESRA",
                "district": "Ranchi",
                "category": InstitutionCategory.UNIVERSITY,
                "dept_name": "Department of Chemical & Environmental Engineering",
                "faculty_email": "faculty.bit@mesra.ac.in",
            },
            {
                "name": "Indian Institute of Technology (IIT ISM) Dhanbad",
                "code": "IIT-ISM",
                "district": "Dhanbad",
                "category": InstitutionCategory.RESEARCH_INSTITUTE,
                "dept_name": "Centre of Mining & Environmental Engineering",
                "faculty_email": "env.chem@iitism.ac.in",
            },
            {
                "name": "National Institute of Technology (NIT) Jamshedpur",
                "code": "NIT-JSR",
                "district": "East Singhbhum",
                "category": InstitutionCategory.TECHNICAL_INSTITUTE,
                "dept_name": "Department of Civil & Infrastructure Engineering",
                "faculty_email": "civil@nitjsr.ac.in",
            },
            {
                "name": "Birsa Agricultural University (BAU) Kanke",
                "code": "BAU-RANCHI",
                "district": "Ranchi",
                "category": InstitutionCategory.UNIVERSITY,
                "dept_name": "Faculty of Agriculture & Soil Sciences",
                "faculty_email": "agronomy@bau.ac.in",
            },
        ]

        for udata in universities_data:
            org = db.query(Organization).filter(Organization.name == udata["name"]).first()
            if not org:
                org = Organization(
                    id=str(uuid.uuid4()),
                    name=udata["name"],
                    organization_type=OrganizationType.UNIVERSITY,
                    district=udata["district"],
                    state="Jharkhand",
                    is_active=True,
                    is_verified=True,
                )
                db.add(org)
                db.flush()

                profile = UniversityProfile(
                    id=str(uuid.uuid4()),
                    organization_id=org.id,
                    institution_code=udata["code"],
                    institution_category=udata["category"],
                    district=udata["district"],
                    state="Jharkhand",
                    is_active=True,
                    is_verified=True,
                )
                db.add(profile)

                dept = Department(
                    id=str(uuid.uuid4()),
                    organization_id=org.id,
                    name=udata["dept_name"],
                    contact_email=udata["faculty_email"],
                    is_active=True,
                )
                dept.capabilities.append(cap_water if "Ranchi" in udata["district"] else cap_agri)
                db.add(dept)

        db.flush()
        print("[+] Universities & research faculties verified.")

        # 3. Industry Partners
        industry_data = [
            {"name": "Tata Steel Foundation (TSF)", "district": "East Singhbhum"},
            {"name": "Coal India Limited (BCCL CSR)", "district": "Dhanbad"},
            {"name": "Jindal Steel & Power (JSPL) Foundation", "district": "Ramgarh"},
            {"name": "Adani Foundation Jharkhand", "district": "Godda"},
        ]

        for ind in industry_data:
            org = db.query(Organization).filter(Organization.name == ind["name"]).first()
            if not org:
                org = Organization(
                    id=str(uuid.uuid4()),
                    name=ind["name"],
                    organization_type=OrganizationType.INDUSTRY,
                    district=ind["district"],
                    state="Jharkhand",
                    is_active=True,
                    is_verified=True,
                )
                db.add(org)

        db.flush()
        print("[+] Industry CSR partners verified.")

        # 4. Societal Challenges
        citizen_user = created_users.get("citizen@jansetu.gov.in")
        chal1 = db.query(Challenge).filter(Challenge.title.like("%Arsenic & Fluoride%")).first()
        if not chal1:
            chal1 = Challenge(
                id="c-arsenic-ranchi",
                reference_code="JS-2026-W001",
                submitted_by_user_id=citizen_user.id if citizen_user else None,
                title="Severe Arsenic & Fluoride Contamination in Kanke Groundwater Wells",
                title_hi="कांके के भूजल कुओं में गंभीर आर्सेनिक और फ्लोराइड संदूषण",
                description="Groundwater wells across 8 tribal villages in Kanke block have tested positive for excessive fluoride (3.4 mg/L) and toxic arsenic levels, causing dental and skeletal fluorosis among over 4,500 residents. Immediate low-cost adsorption filtration and community IoT water telemetry are required.",
                problem_statement="Drinking groundwater exceeds permissible fluoride and arsenic thresholds, requiring a decentralized, energy-efficient filtration solution capable of being maintained by village water committees.",
                expected_outcome="Deploy gravity-fed indigenous adsorbent filter reducing fluoride to < 0.8 mg/L with real-time IoT water quality sensors.",
                district="Ranchi",
                block="Kanke",
                village_or_ward="Arsande & Pithoria",
                domain=SocietalDomain.WATER,
                subdomain="Arsenic & Fluoride Chemical Filtration",
                priority=PriorityLevel.CRITICAL,
                urgency=UrgencyLevel.CRITICAL,
                status=ChallengeStatus.VALIDATED,
                validation_status=ValidationStatus.VALIDATED,
                assigned_department="Drinking Water and Sanitation Department (DWSD), Govt of Jharkhand",
                affected_population="4,500+ residents across 8 habitations",
                estimated_beneficiaries=4500,
            )
            db.add(chal1)

        db.flush()
        db.commit()
        print("[OK] JanSetu database seeded successfully!")
    except Exception as e:
        db.rollback()
        print(f"[!] Error seeding database: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
