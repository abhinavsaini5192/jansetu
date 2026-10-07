"""create institutional collaboration tables (Phases 2.1 to 2.5)

Revision ID: 0009_institutional
Revises: 0008_audit_logs
Create Date: 2026-09-18 02:00:00.000000

Purpose:
Creates tables for institutional collaboration:
- university_profiles
- departments
- capabilities
- department_capabilities
- challenge_assignments
- projects
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0009_institutional"
down_revision: Union[str, None] = "0008_audit_logs"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. university_profiles
    op.create_table(
        "university_profiles",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("organization_id", sa.String(length=36), nullable=False),
        sa.Column("institution_code", sa.String(length=50), nullable=True),
        sa.Column("institution_category", sa.String(length=50), nullable=False),
        sa.Column("accreditation_details", sa.String(length=255), nullable=True),
        sa.Column("established_year", sa.Integer(), nullable=True),
        sa.Column("official_contact_email", sa.String(length=255), nullable=True),
        sa.Column("official_website", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("address", sa.String(length=500), nullable=True),
        sa.Column("district", sa.String(length=100), nullable=True),
        sa.Column("state", sa.String(length=100), server_default="Jharkhand", nullable=False),
        sa.Column("pincode", sa.String(length=20), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("is_verified", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id"),
    )
    op.create_index(op.f("ix_university_profiles_id"), "university_profiles", ["id"], unique=False)
    op.create_index(op.f("ix_university_profiles_organization_id"), "university_profiles", ["organization_id"], unique=True)
    op.create_index(op.f("ix_university_profiles_institution_category"), "university_profiles", ["institution_category"], unique=False)
    op.create_index(op.f("ix_university_profiles_district"), "university_profiles", ["district"], unique=False)

    # 2. departments
    op.create_table(
        "departments",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("organization_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("contact_email", sa.String(length=255), nullable=True),
        sa.Column("contact_phone", sa.String(length=50), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_departments_id"), "departments", ["id"], unique=False)
    op.create_index(op.f("ix_departments_organization_id"), "departments", ["organization_id"], unique=False)
    op.create_index(op.f("ix_departments_name"), "departments", ["name"], unique=False)

    # 3. capabilities
    op.create_table(
        "capabilities",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("domain", sa.String(length=50), nullable=False),
        sa.Column("keywords", sa.String(length=500), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_capabilities_id"), "capabilities", ["id"], unique=False)
    op.create_index(op.f("ix_capabilities_name"), "capabilities", ["name"], unique=False)
    op.create_index(op.f("ix_capabilities_domain"), "capabilities", ["domain"], unique=False)

    # 4. department_capabilities
    op.create_table(
        "department_capabilities",
        sa.Column("department_id", sa.String(length=36), nullable=False),
        sa.Column("capability_id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(["capability_id"], ["capabilities.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["department_id"], ["departments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("department_id", "capability_id"),
    )
    op.create_index(op.f("ix_department_capabilities_department_id"), "department_capabilities", ["department_id"], unique=False)
    op.create_index(op.f("ix_department_capabilities_capability_id"), "department_capabilities", ["capability_id"], unique=False)

    # 5. challenge_assignments
    op.create_table(
        "challenge_assignments",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("challenge_id", sa.String(length=36), nullable=False),
        sa.Column("university_id", sa.String(length=36), nullable=False),
        sa.Column("department_id", sa.String(length=36), nullable=True),
        sa.Column("assigned_by_user_id", sa.String(length=36), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("invitation_message", sa.Text(), nullable=True),
        sa.Column("response_message", sa.Text(), nullable=True),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("responded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["assigned_by_user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["challenge_id"], ["challenges.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["department_id"], ["departments.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["university_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_challenge_assignments_id"), "challenge_assignments", ["id"], unique=False)
    op.create_index(op.f("ix_challenge_assignments_challenge_id"), "challenge_assignments", ["challenge_id"], unique=False)
    op.create_index(op.f("ix_challenge_assignments_university_id"), "challenge_assignments", ["university_id"], unique=False)
    op.create_index(op.f("ix_challenge_assignments_department_id"), "challenge_assignments", ["department_id"], unique=False)
    op.create_index(op.f("ix_challenge_assignments_assigned_by_user_id"), "challenge_assignments", ["assigned_by_user_id"], unique=False)
    op.create_index(op.f("ix_challenge_assignments_status"), "challenge_assignments", ["status"], unique=False)

    # 6. projects
    op.create_table(
        "projects",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_code", sa.String(length=32), nullable=False),
        sa.Column("challenge_id", sa.String(length=36), nullable=False),
        sa.Column("assignment_id", sa.String(length=36), nullable=True),
        sa.Column("university_id", sa.String(length=36), nullable=False),
        sa.Column("department_id", sa.String(length=36), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("created_by_user_id", sa.String(length=36), nullable=False),
        sa.Column("lead_faculty", sa.String(length=255), nullable=True),
        sa.Column("student_lead", sa.String(length=255), nullable=True),
        sa.Column("budget", sa.String(length=100), nullable=True),
        sa.Column("progress_percentage", sa.Integer(), server_default="0", nullable=False),
        sa.Column("start_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("target_completion_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["assignment_id"], ["challenge_assignments.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["challenge_id"], ["challenges.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["department_id"], ["departments.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["university_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_code"),
    )
    op.create_index(op.f("ix_projects_id"), "projects", ["id"], unique=False)
    op.create_index(op.f("ix_projects_project_code"), "projects", ["project_code"], unique=True)
    op.create_index(op.f("ix_projects_challenge_id"), "projects", ["challenge_id"], unique=False)
    op.create_index(op.f("ix_projects_assignment_id"), "projects", ["assignment_id"], unique=False)
    op.create_index(op.f("ix_projects_university_id"), "projects", ["university_id"], unique=False)
    op.create_index(op.f("ix_projects_department_id"), "projects", ["department_id"], unique=False)
    op.create_index(op.f("ix_projects_created_by_user_id"), "projects", ["created_by_user_id"], unique=False)
    op.create_index(op.f("ix_projects_status"), "projects", ["status"], unique=False)
    op.create_index(op.f("ix_projects_created_at"), "projects", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_table("projects")
    op.drop_table("challenge_assignments")
    op.drop_table("department_capabilities")
    op.drop_table("capabilities")
    op.drop_table("departments")
    op.drop_table("university_profiles")
