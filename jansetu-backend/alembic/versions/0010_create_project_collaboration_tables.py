"""create project collaboration tables (Phases 2.6 to 2.10)

Revision ID: 0010_project_collaboration
Revises: 0009_institutional
Create Date: 2026-09-18 03:00:00.000000

Purpose:
Creates tables for institutional collaboration and project execution:
- project_teams
- project_team_members
- proposals
- milestones
- deliverables
- project_partners
- partner_support
- project_risks
- project_activities
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0010_project_collaboration"
down_revision: Union[str, None] = "0009_institutional"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. project_teams
    op.create_table(
        "project_teams",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_by_user_id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_project_teams_id"), "project_teams", ["id"], unique=False)
    op.create_index(op.f("ix_project_teams_project_id"), "project_teams", ["project_id"], unique=False)
    op.create_index(op.f("ix_project_teams_created_by_user_id"), "project_teams", ["created_by_user_id"], unique=False)
    op.create_index(op.f("ix_project_teams_created_at"), "project_teams", ["created_at"], unique=False)

    # 2. project_team_members
    op.create_table(
        "project_team_members",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("team_id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["team_id"], ["project_teams.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("team_id", "user_id", name="uq_project_team_member_team_user"),
    )
    op.create_index(op.f("ix_project_team_members_id"), "project_team_members", ["id"], unique=False)
    op.create_index(op.f("ix_project_team_members_team_id"), "project_team_members", ["team_id"], unique=False)
    op.create_index(op.f("ix_project_team_members_user_id"), "project_team_members", ["user_id"], unique=False)
    op.create_index(op.f("ix_project_team_members_is_active"), "project_team_members", ["is_active"], unique=False)

    # 3. proposals
    op.create_table(
        "proposals",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("submitted_by_team_id", sa.String(length=36), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("detailed_description", sa.Text(), nullable=False),
        sa.Column("methodology", sa.Text(), nullable=True),
        sa.Column("expected_outcomes", sa.Text(), nullable=True),
        sa.Column("estimated_budget", sa.String(length=100), nullable=True),
        sa.Column("required_resources", sa.Text(), nullable=True),
        sa.Column("implementation_timeline", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewed_by_user_id", sa.String(length=36), nullable=True),
        sa.Column("review_comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["submitted_by_team_id"], ["project_teams.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["reviewed_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_proposals_id"), "proposals", ["id"], unique=False)
    op.create_index(op.f("ix_proposals_project_id"), "proposals", ["project_id"], unique=False)
    op.create_index(op.f("ix_proposals_submitted_by_team_id"), "proposals", ["submitted_by_team_id"], unique=False)
    op.create_index(op.f("ix_proposals_status"), "proposals", ["status"], unique=False)
    op.create_index(op.f("ix_proposals_reviewed_by_user_id"), "proposals", ["reviewed_by_user_id"], unique=False)
    op.create_index(op.f("ix_proposals_created_at"), "proposals", ["created_at"], unique=False)

    # 4. milestones
    op.create_table(
        "milestones",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("sequence_number", sa.Integer(), server_default="1", nullable=False),
        sa.Column("planned_start_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("planned_end_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_start_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_end_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("completion_percentage", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_by_user_id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_milestones_id"), "milestones", ["id"], unique=False)
    op.create_index(op.f("ix_milestones_project_id"), "milestones", ["project_id"], unique=False)
    op.create_index(op.f("ix_milestones_status"), "milestones", ["status"], unique=False)
    op.create_index(op.f("ix_milestones_created_by_user_id"), "milestones", ["created_by_user_id"], unique=False)
    op.create_index(op.f("ix_milestones_created_at"), "milestones", ["created_at"], unique=False)

    # 5. deliverables
    op.create_table(
        "deliverables",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("milestone_id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("file_attachment_id", sa.String(length=36), nullable=True),
        sa.Column("submitted_by_user_id", sa.String(length=36), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewed_by_user_id", sa.String(length=36), nullable=True),
        sa.Column("review_comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["milestone_id"], ["milestones.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["file_attachment_id"], ["attachments.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["submitted_by_user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["reviewed_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_deliverables_id"), "deliverables", ["id"], unique=False)
    op.create_index(op.f("ix_deliverables_milestone_id"), "deliverables", ["milestone_id"], unique=False)
    op.create_index(op.f("ix_deliverables_file_attachment_id"), "deliverables", ["file_attachment_id"], unique=False)
    op.create_index(op.f("ix_deliverables_submitted_by_user_id"), "deliverables", ["submitted_by_user_id"], unique=False)
    op.create_index(op.f("ix_deliverables_status"), "deliverables", ["status"], unique=False)
    op.create_index(op.f("ix_deliverables_reviewed_by_user_id"), "deliverables", ["reviewed_by_user_id"], unique=False)
    op.create_index(op.f("ix_deliverables_created_at"), "deliverables", ["created_at"], unique=False)

    # 6. project_partners
    op.create_table(
        "project_partners",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("organization_id", sa.String(length=36), nullable=False),
        sa.Column("partner_type", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("invited_by_user_id", sa.String(length=36), nullable=False),
        sa.Column("invitation_message", sa.Text(), nullable=True),
        sa.Column("response_message", sa.Text(), nullable=True),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["invited_by_user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "organization_id", name="uq_project_partner_project_org"),
    )
    op.create_index(op.f("ix_project_partners_id"), "project_partners", ["id"], unique=False)
    op.create_index(op.f("ix_project_partners_project_id"), "project_partners", ["project_id"], unique=False)
    op.create_index(op.f("ix_project_partners_organization_id"), "project_partners", ["organization_id"], unique=False)
    op.create_index(op.f("ix_project_partners_partner_type"), "project_partners", ["partner_type"], unique=False)
    op.create_index(op.f("ix_project_partners_status"), "project_partners", ["status"], unique=False)
    op.create_index(op.f("ix_project_partners_invited_by_user_id"), "project_partners", ["invited_by_user_id"], unique=False)
    op.create_index(op.f("ix_project_partners_created_at"), "project_partners", ["created_at"], unique=False)

    # 7. partner_support
    op.create_table(
        "partner_support",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_partner_id", sa.String(length=36), nullable=False),
        sa.Column("support_type", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("estimated_value", sa.String(length=100), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_partner_id"], ["project_partners.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_partner_support_id"), "partner_support", ["id"], unique=False)
    op.create_index(op.f("ix_partner_support_project_partner_id"), "partner_support", ["project_partner_id"], unique=False)
    op.create_index(op.f("ix_partner_support_support_type"), "partner_support", ["support_type"], unique=False)
    op.create_index(op.f("ix_partner_support_status"), "partner_support", ["status"], unique=False)
    op.create_index(op.f("ix_partner_support_created_at"), "partner_support", ["created_at"], unique=False)

    # 8. project_risks
    op.create_table(
        "project_risks",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("severity", sa.String(length=50), nullable=False),
        sa.Column("likelihood", sa.String(length=50), nullable=False),
        sa.Column("risk_score", sa.Integer(), server_default="4", nullable=False),
        sa.Column("mitigation_plan", sa.Text(), nullable=True),
        sa.Column("owner_user_id", sa.String(length=36), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("identified_by_user_id", sa.String(length=36), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["identified_by_user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_project_risks_id"), "project_risks", ["id"], unique=False)
    op.create_index(op.f("ix_project_risks_project_id"), "project_risks", ["project_id"], unique=False)
    op.create_index(op.f("ix_project_risks_severity"), "project_risks", ["severity"], unique=False)
    op.create_index(op.f("ix_project_risks_likelihood"), "project_risks", ["likelihood"], unique=False)
    op.create_index(op.f("ix_project_risks_status"), "project_risks", ["status"], unique=False)
    op.create_index(op.f("ix_project_risks_owner_user_id"), "project_risks", ["owner_user_id"], unique=False)
    op.create_index(op.f("ix_project_risks_identified_by_user_id"), "project_risks", ["identified_by_user_id"], unique=False)
    op.create_index(op.f("ix_project_risks_created_at"), "project_risks", ["created_at"], unique=False)

    # 9. project_activities
    op.create_table(
        "project_activities",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("actor_user_id", sa.String(length=36), nullable=True),
        sa.Column("activity_type", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("related_entity_type", sa.String(length=50), nullable=True),
        sa.Column("related_entity_id", sa.String(length=36), nullable=True),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_project_activities_id"), "project_activities", ["id"], unique=False)
    op.create_index(op.f("ix_project_activities_project_id"), "project_activities", ["project_id"], unique=False)
    op.create_index(op.f("ix_project_activities_actor_user_id"), "project_activities", ["actor_user_id"], unique=False)
    op.create_index(op.f("ix_project_activities_activity_type"), "project_activities", ["activity_type"], unique=False)
    op.create_index(op.f("ix_project_activities_created_at"), "project_activities", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_table("project_activities")
    op.drop_table("project_risks")
    op.drop_table("partner_support")
    op.drop_table("project_partners")
    op.drop_table("deliverables")
    op.drop_table("milestones")
    op.drop_table("proposals")
    op.drop_table("project_team_members")
    op.drop_table("project_teams")
