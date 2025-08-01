# Generated by Django 4.2.7 on 2025-07-21 20:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ResearchStudy",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=200)),
                ("description", models.TextField()),
                ("is_active", models.BooleanField(default=True)),
                ("max_participants", models.IntegerField(default=100)),
                ("estimated_duration_minutes", models.IntegerField(default=60)),
                ("requires_consent", models.BooleanField(default=True)),
                ("has_pre_quiz", models.BooleanField(default=True)),
                ("has_post_quiz", models.BooleanField(default=True)),
                ("auto_assign_groups", models.BooleanField(default=True)),
                ("group_balance_ratio", models.JSONField(default=dict)),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="created_studies",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Research Studies",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="ParticipantProfile",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("age_range", models.CharField(blank=True, max_length=20)),
                ("education_level", models.CharField(blank=True, max_length=50)),
                ("technical_background", models.CharField(blank=True, max_length=100)),
                ("assigned_group", models.CharField(max_length=20)),
                ("assignment_timestamp", models.DateTimeField(auto_now_add=True)),
                ("randomization_seed", models.CharField(max_length=32)),
                ("consent_given", models.BooleanField(default=False)),
                ("consent_timestamp", models.DateTimeField(blank=True, null=True)),
                ("gdpr_consent", models.BooleanField(default=False)),
                ("data_processing_consent", models.BooleanField(default=False)),
                ("withdrawn", models.BooleanField(default=False)),
                ("withdrawal_timestamp", models.DateTimeField(blank=True, null=True)),
                ("withdrawal_reason", models.TextField(blank=True)),
                ("anonymized_id", models.CharField(max_length=50, unique=True)),
                ("is_anonymized", models.BooleanField(default=False)),
                (
                    "study",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="participants",
                        to="research.researchstudy",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="research_profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "unique_together": {("user", "study")},
            },
        ),
        migrations.CreateModel(
            name="DataExport",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "export_type",
                    models.CharField(
                        choices=[
                            ("full_dataset", "Full Dataset"),
                            ("participant_data", "Participant Data"),
                            ("interaction_logs", "Interaction Logs"),
                            ("quiz_responses", "Quiz Responses"),
                            ("chat_interactions", "Chat Interactions"),
                            ("pdf_behaviors", "PDF Viewing Behaviors"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "export_format",
                    models.CharField(
                        choices=[("csv", "CSV"), ("json", "JSON"), ("excel", "Excel")],
                        max_length=10,
                    ),
                ),
                ("filters", models.JSONField(default=dict)),
                ("date_range_start", models.DateTimeField(blank=True, null=True)),
                ("date_range_end", models.DateTimeField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("processing", "Processing"),
                            ("completed", "Completed"),
                            ("failed", "Failed"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("file_path", models.CharField(blank=True, max_length=500)),
                ("file_size_bytes", models.BigIntegerField(blank=True, null=True)),
                ("record_count", models.IntegerField(blank=True, null=True)),
                ("exported_at", models.DateTimeField(blank=True, null=True)),
                ("expires_at", models.DateTimeField(blank=True, null=True)),
                ("download_count", models.IntegerField(default=0)),
                (
                    "requested_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="export_requests",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "study",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="exports",
                        to="research.researchstudy",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="ResearcherAccess",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "permission_level",
                    models.CharField(
                        choices=[
                            ("view", "View Only"),
                            ("export", "View and Export"),
                            ("manage", "Full Management"),
                        ],
                        max_length=20,
                    ),
                ),
                ("granted_at", models.DateTimeField(auto_now_add=True)),
                ("last_accessed", models.DateTimeField(blank=True, null=True)),
                ("access_count", models.IntegerField(default=0)),
                (
                    "granted_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="granted_access",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "study",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="researcher_access",
                        to="research.researchstudy",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="researcher_access",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-granted_at"],
                "unique_together": {("user", "study")},
            },
        ),
        migrations.CreateModel(
            name="QuizResponse",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("session_id", models.CharField(max_length=100)),
                (
                    "quiz_type",
                    models.CharField(
                        choices=[("pre_quiz", "Pre-Quiz"), ("post_quiz", "Post-Quiz")],
                        max_length=20,
                    ),
                ),
                ("question_id", models.CharField(max_length=100)),
                ("question_text", models.TextField()),
                ("question_type", models.CharField(max_length=20)),
                ("response_value", models.JSONField()),
                ("response_text", models.TextField(blank=True)),
                ("is_correct", models.BooleanField(blank=True, null=True)),
                ("first_viewed_at", models.DateTimeField()),
                ("submitted_at", models.DateTimeField(auto_now_add=True)),
                ("time_spent_seconds", models.IntegerField(default=0)),
                ("changes_made", models.IntegerField(default=0)),
                (
                    "participant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="quiz_responses",
                        to="research.participantprofile",
                    ),
                ),
            ],
            options={
                "ordering": ["-submitted_at"],
                "unique_together": {
                    ("participant", "session_id", "quiz_type", "question_id")
                },
            },
        ),
        migrations.CreateModel(
            name="PDFViewingBehavior",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("session_id", models.CharField(max_length=100)),
                ("pdf_name", models.CharField(max_length=200)),
                ("pdf_hash", models.CharField(max_length=64)),
                ("page_number", models.IntegerField()),
                ("time_spent_seconds", models.IntegerField(default=0)),
                ("scroll_events", models.JSONField(default=list)),
                ("zoom_events", models.JSONField(default=list)),
                ("search_queries", models.JSONField(default=list)),
                ("first_viewed_at", models.DateTimeField(auto_now_add=True)),
                ("last_viewed_at", models.DateTimeField(auto_now=True)),
                (
                    "participant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="pdf_behaviors",
                        to="research.participantprofile",
                    ),
                ),
            ],
            options={
                "ordering": ["-last_viewed_at"],
                "unique_together": {
                    ("participant", "session_id", "pdf_name", "page_number")
                },
            },
        ),
        migrations.CreateModel(
            name="InteractionLog",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("session_id", models.CharField(max_length=100)),
                (
                    "log_type",
                    models.CharField(
                        choices=[
                            ("session_start", "Session Start"),
                            ("session_end", "Session End"),
                            ("phase_transition", "Phase Transition"),
                            ("chat_message_sent", "Chat Message Sent"),
                            ("chat_message_received", "Chat Message Received"),
                            ("pdf_opened", "PDF Opened"),
                            ("pdf_page_viewed", "PDF Page Viewed"),
                            ("pdf_scroll", "PDF Scroll"),
                            ("pdf_zoom", "PDF Zoom"),
                            ("pdf_search", "PDF Search"),
                            ("quiz_question_viewed", "Quiz Question Viewed"),
                            ("quiz_answer_submitted", "Quiz Answer Submitted"),
                            ("quiz_answer_changed", "Quiz Answer Changed"),
                            ("button_click", "Button Click"),
                            ("form_submit", "Form Submit"),
                            ("navigation", "Navigation"),
                            ("focus_change", "Focus Change"),
                            ("error_occurred", "Error Occurred"),
                        ],
                        max_length=30,
                    ),
                ),
                ("event_data", models.JSONField(default=dict)),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                ("page_url", models.URLField(blank=True)),
                ("user_agent", models.TextField(blank=True)),
                ("screen_resolution", models.CharField(blank=True, max_length=20)),
                ("reaction_time_ms", models.IntegerField(blank=True, null=True)),
                (
                    "time_since_last_action_ms",
                    models.IntegerField(blank=True, null=True),
                ),
                (
                    "participant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="interaction_logs",
                        to="research.participantprofile",
                    ),
                ),
            ],
            options={
                "ordering": ["-timestamp"],
                "indexes": [
                    models.Index(
                        fields=["participant", "log_type"],
                        name="research_in_partici_ad43ec_idx",
                    ),
                    models.Index(
                        fields=["timestamp"], name="research_in_timesta_15bd3e_idx"
                    ),
                    models.Index(
                        fields=["session_id"], name="research_in_session_b2b930_idx"
                    ),
                ],
            },
        ),
        migrations.CreateModel(
            name="ChatInteraction",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("session_id", models.CharField(max_length=100)),
                (
                    "message_type",
                    models.CharField(
                        choices=[
                            ("user_message", "User Message"),
                            ("assistant_response", "Assistant Response"),
                            ("system_message", "System Message"),
                        ],
                        max_length=20,
                    ),
                ),
                ("content", models.TextField()),
                ("content_hash", models.CharField(max_length=64)),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                ("response_time_ms", models.IntegerField(blank=True, null=True)),
                ("token_count", models.IntegerField(blank=True, null=True)),
                (
                    "cost_usd",
                    models.DecimalField(
                        blank=True, decimal_places=6, max_digits=10, null=True
                    ),
                ),
                (
                    "participant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="chat_interactions",
                        to="research.participantprofile",
                    ),
                ),
            ],
            options={
                "ordering": ["-timestamp"],
                "indexes": [
                    models.Index(
                        fields=["participant", "timestamp"],
                        name="research_ch_partici_c06d74_idx",
                    ),
                    models.Index(
                        fields=["session_id"], name="research_ch_session_8165ae_idx"
                    ),
                ],
            },
        ),
    ]
