"""
Research utilities for ID generation, random assignment, and data validation
"""

import random
import string
import secrets
import hashlib
import json
import uuid
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import ResearchStudy, ParticipantProfile, InteractionLog
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class ResearchUtilities:
    """Comprehensive research utilities service"""
    
    def __init__(self):
        self.default_id_length = 8
        self.default_prefix = "P"
        self.available_groups = ["PDF", "CHATGPT"]
    
    def generate_participant_id(self, prefix: str = None, length: int = None,
                              exclude_existing: bool = True) -> str:
        """
        Generate a unique participant ID
        
        Args:
            prefix: ID prefix (default: "P")
            length: ID length (default: 8)
            exclude_existing: Check against existing IDs
        
        Returns:
            str: Generated participant ID
        """
        if prefix is None:
            prefix = self.default_prefix
        if length is None:
            length = self.default_id_length
        
        # Generate random alphanumeric string
        max_attempts = 1000
        attempts = 0
        
        while attempts < max_attempts:
            # Generate random string
            random_part = ''.join(
                secrets.choice(string.ascii_uppercase + string.digits) 
                for _ in range(length)
            )
            participant_id = f"{prefix}{random_part}"
            
            # Check if ID already exists
            if exclude_existing:
                if not User.objects.filter(participant_id=participant_id).exists():
                    return participant_id
            else:
                return participant_id
            
            attempts += 1
        
        # If we couldn't generate a unique ID, add timestamp
        timestamp = int(datetime.now().timestamp())
        return f"{prefix}{timestamp}"
    
    def generate_session_id(self, participant_id: str) -> str:
        """
        Generate a unique session ID for a participant
        
        Args:
            participant_id: Participant's ID
        
        Returns:
            str: Generated session ID
        """
        timestamp = int(datetime.now().timestamp())
        random_part = secrets.token_hex(4)
        return f"{participant_id}_{timestamp}_{random_part}"
    
    def assign_group_random(self, study_id: str, participant_count: int = 1,
                           group_ratios: Dict[str, float] = None) -> List[str]:
        """
        Randomly assign participants to groups
        
        Args:
            study_id: Study identifier
            participant_count: Number of participants to assign
            group_ratios: Desired group ratios (default: equal distribution)
        
        Returns:
            List[str]: List of assigned groups
        """
        try:
            study = ResearchStudy.objects.get(id=study_id)
            
            # Use study configuration or defaults
            if group_ratios is None:
                group_ratios = study.group_balance_ratio if study.group_balance_ratio else {
                    "PDF": 0.5,
                    "CHATGPT": 0.5
                }
            
            # Validate ratios sum to 1.0
            total_ratio = sum(group_ratios.values())
            if abs(total_ratio - 1.0) > 0.01:
                # Normalize ratios
                group_ratios = {k: v/total_ratio for k, v in group_ratios.items()}
            
            # Calculate assignments
            assignments = []
            groups = list(group_ratios.keys())
            
            for i in range(participant_count):
                # Use weighted random selection
                rand_val = random.random()
                cumulative = 0
                
                for group, ratio in group_ratios.items():
                    cumulative += ratio
                    if rand_val <= cumulative:
                        assignments.append(group)
                        break
                else:
                    # Fallback to first group
                    assignments.append(groups[0])
            
            return assignments
            
        except ResearchStudy.DoesNotExist:
            logger.error(f"Study not found: {study_id}")
            # Return default assignments
            return ["PDF" if i % 2 == 0 else "CHATGPT" for i in range(participant_count)]
    
    def assign_group_balanced(self, study_id: str, participant_count: int = 1) -> List[str]:
        """
        Assign participants to groups with balanced distribution
        
        Args:
            study_id: Study identifier
            participant_count: Number of participants to assign
        
        Returns:
            List[str]: List of assigned groups
        """
        try:
            study = ResearchStudy.objects.get(id=study_id)
            
            # Get current group distribution
            current_counts = {}
            existing_participants = ParticipantProfile.objects.filter(study=study)
            
            for participant in existing_participants:
                group = participant.assigned_group
                current_counts[group] = current_counts.get(group, 0) + 1
            
            # Get available groups
            available_groups = list(study.group_balance_ratio.keys()) if study.group_balance_ratio else self.available_groups
            
            # Initialize counts for missing groups
            for group in available_groups:
                if group not in current_counts:
                    current_counts[group] = 0
            
            # Assign to maintain balance
            assignments = []
            for i in range(participant_count):
                # Find group with minimum count
                min_group = min(current_counts.keys(), key=lambda g: current_counts[g])
                assignments.append(min_group)
                current_counts[min_group] += 1
            
            return assignments
            
        except ResearchStudy.DoesNotExist:
            logger.error(f"Study not found: {study_id}")
            # Return alternating assignments
            return ["PDF" if i % 2 == 0 else "CHATGPT" for i in range(participant_count)]
    
    def bulk_generate_participants(self, study_id: str, count: int,
                                 assignment_method: str = "balanced",
                                 id_prefix: str = None) -> Dict[str, Any]:
        """
        Bulk generate participants with automatic assignment
        
        Args:
            study_id: Study identifier
            count: Number of participants to generate
            assignment_method: "random" or "balanced"
            id_prefix: Participant ID prefix
        
        Returns:
            Dict containing generation results
        """
        try:
            with transaction.atomic():
                study = ResearchStudy.objects.get(id=study_id)
                
                # Validate participant limit
                current_count = ParticipantProfile.objects.filter(study=study).count()
                if current_count + count > study.max_participants:
                    return {
                        'success': False,
                        'error': f'Would exceed maximum participants ({study.max_participants})',
                        'current_count': current_count,
                        'requested_count': count
                    }
                
                # Generate participant IDs
                participant_ids = []
                for i in range(count):
                    participant_id = self.generate_participant_id(
                        prefix=id_prefix or self.default_prefix
                    )
                    participant_ids.append(participant_id)
                
                # Assign groups
                if assignment_method == "random":
                    group_assignments = self.assign_group_random(study_id, count)
                else:
                    group_assignments = self.assign_group_balanced(study_id, count)
                
                # Create participants
                created_participants = []
                for i, participant_id in enumerate(participant_ids):
                    # Create user
                    user = User.objects.create_user(
                        username=participant_id,
                        email=f"{participant_id}@study.local",
                        participant_id=participant_id,
                        study_group=group_assignments[i]
                    )
                    
                    # Create participant profile
                    participant = ParticipantProfile.objects.create(
                        user=user,
                        study=study,
                        assigned_group=group_assignments[i]
                    )
                    
                    created_participants.append({
                        'participant_id': participant_id,
                        'anonymized_id': participant.anonymized_id,
                        'assigned_group': group_assignments[i],
                        'created_at': participant.created_at.isoformat()
                    })
                
                return {
                    'success': True,
                    'count': count,
                    'study_id': study_id,
                    'assignment_method': assignment_method,
                    'participants': created_participants,
                    'group_distribution': self._calculate_group_distribution(created_participants)
                }
                
        except ResearchStudy.DoesNotExist:
            return {
                'success': False,
                'error': 'Study not found',
                'study_id': study_id
            }
        except Exception as e:
            logger.error(f"Error bulk generating participants: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def validate_data_integrity(self, study_id: str = None) -> Dict[str, Any]:
        """
        Validate data integrity across the research platform
        
        Args:
            study_id: Validate specific study (optional)
        
        Returns:
            Dict containing validation results
        """
        try:
            validation_results = {
                'timestamp': timezone.now().isoformat(),
                'study_id': study_id,
                'checks_performed': [],
                'issues_found': [],
                'statistics': {}
            }
            
            # Build participant queryset
            participants = ParticipantProfile.objects.all()
            if study_id:
                participants = participants.filter(study_id=study_id)
            
            # Check 1: Duplicate participant IDs
            validation_results['checks_performed'].append('duplicate_participant_ids')
            duplicate_ids = []
            participant_ids = []
            for participant in participants:
                if participant.user.participant_id in participant_ids:
                    duplicate_ids.append(participant.user.participant_id)
                participant_ids.append(participant.user.participant_id)
            
            if duplicate_ids:
                validation_results['issues_found'].append({
                    'type': 'duplicate_participant_ids',
                    'count': len(duplicate_ids),
                    'details': duplicate_ids
                })
            
            # Check 2: Orphaned interaction logs
            validation_results['checks_performed'].append('orphaned_interaction_logs')
            orphaned_logs = InteractionLog.objects.exclude(
                participant__in=participants
            ).count()
            
            if orphaned_logs > 0:
                validation_results['issues_found'].append({
                    'type': 'orphaned_interaction_logs',
                    'count': orphaned_logs
                })
            
            # Check 3: Inconsistent group assignments
            validation_results['checks_performed'].append('inconsistent_group_assignments')
            inconsistent_groups = []
            for participant in participants:
                if participant.assigned_group != participant.user.study_group:
                    inconsistent_groups.append({
                        'participant_id': participant.anonymized_id,
                        'profile_group': participant.assigned_group,
                        'user_group': participant.user.study_group
                    })
            
            if inconsistent_groups:
                validation_results['issues_found'].append({
                    'type': 'inconsistent_group_assignments',
                    'count': len(inconsistent_groups),
                    'details': inconsistent_groups
                })
            
            # Check 4: Missing anonymized IDs
            validation_results['checks_performed'].append('missing_anonymized_ids')
            missing_anonymized = participants.filter(
                anonymized_id__isnull=True
            ).count()
            
            if missing_anonymized > 0:
                validation_results['issues_found'].append({
                    'type': 'missing_anonymized_ids',
                    'count': missing_anonymized
                })
            
            # Check 5: Data completeness
            validation_results['checks_performed'].append('data_completeness')
            incomplete_data = []
            for participant in participants:
                issues = []
                if not participant.consent_given:
                    issues.append('no_consent')
                if not participant.user.consent_completed:
                    issues.append('consent_not_completed')
                if participant.user.study_completed and not participant.user.post_quiz_completed:
                    issues.append('study_completed_without_post_quiz')
                
                if issues:
                    incomplete_data.append({
                        'participant_id': participant.anonymized_id,
                        'issues': issues
                    })
            
            if incomplete_data:
                validation_results['issues_found'].append({
                    'type': 'incomplete_data',
                    'count': len(incomplete_data),
                    'details': incomplete_data[:10]  # Limit to first 10
                })
            
            # Calculate statistics
            validation_results['statistics'] = {
                'total_participants': participants.count(),
                'total_checks': len(validation_results['checks_performed']),
                'total_issues': len(validation_results['issues_found']),
                'integrity_score': max(0, 100 - (len(validation_results['issues_found']) * 10))
            }
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error validating data integrity: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_randomization_seed(self, study_id: str, participant_id: str) -> str:
        """
        Generate a deterministic randomization seed for a participant
        
        Args:
            study_id: Study identifier
            participant_id: Participant identifier
        
        Returns:
            str: Generated seed
        """
        # Combine study and participant ID for deterministic randomization
        combined = f"{study_id}_{participant_id}_{timezone.now().date().isoformat()}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]
    
    def calculate_sample_size(self, effect_size: float, alpha: float = 0.05,
                            power: float = 0.8, two_tailed: bool = True) -> int:
        """
        Calculate required sample size for statistical power
        
        Args:
            effect_size: Expected effect size (Cohen's d)
            alpha: Significance level (default: 0.05)
            power: Statistical power (default: 0.8)
            two_tailed: Two-tailed test (default: True)
        
        Returns:
            int: Required sample size per group
        """
        # Simplified sample size calculation
        # For more accurate calculation, use scipy.stats or specialized library
        
        # Z-scores for common values
        z_alpha = 1.96 if two_tailed else 1.645  # alpha = 0.05
        z_beta = 0.842  # power = 0.8
        
        # Sample size formula for two-sample t-test
        n = 2 * ((z_alpha + z_beta) / effect_size) ** 2
        
        return int(n) + 1  # Round up
    
    def estimate_study_duration(self, total_participants: int,
                              enrollment_rate_per_day: float,
                              avg_session_duration_hours: float = 1.0) -> Dict[str, Any]:
        """
        Estimate study duration based on parameters
        
        Args:
            total_participants: Total number of participants needed
            enrollment_rate_per_day: Expected enrollment rate per day
            avg_session_duration_hours: Average session duration
        
        Returns:
            Dict containing duration estimates
        """
        if enrollment_rate_per_day <= 0:
            return {
                'error': 'Enrollment rate must be positive'
            }
        
        enrollment_days = total_participants / enrollment_rate_per_day
        total_session_hours = total_participants * avg_session_duration_hours
        
        return {
            'total_participants': total_participants,
            'enrollment_rate_per_day': enrollment_rate_per_day,
            'estimated_enrollment_days': enrollment_days,
            'estimated_enrollment_weeks': enrollment_days / 7,
            'total_session_hours': total_session_hours,
            'avg_session_duration_hours': avg_session_duration_hours,
            'estimated_completion_date': (
                timezone.now() + timedelta(days=enrollment_days + 7)  # +7 for buffer
            ).isoformat()
        }
    
    def _calculate_group_distribution(self, participants: List[Dict]) -> Dict[str, int]:
        """Calculate group distribution from participant list"""
        distribution = {}
        for participant in participants:
            group = participant['assigned_group']
            distribution[group] = distribution.get(group, 0) + 1
        return distribution
    
    def generate_study_summary(self, study_id: str) -> Dict[str, Any]:
        """
        Generate comprehensive study summary
        
        Args:
            study_id: Study identifier
        
        Returns:
            Dict containing study summary
        """
        try:
            study = ResearchStudy.objects.get(id=study_id)
            participants = ParticipantProfile.objects.filter(study=study)
            
            # Basic statistics
            total_participants = participants.count()
            completed_participants = participants.filter(user__study_completed=True).count()
            withdrawn_participants = participants.filter(withdrawn=True).count()
            
            # Group distribution
            group_distribution = {}
            for participant in participants:
                group = participant.assigned_group
                group_distribution[group] = group_distribution.get(group, 0) + 1
            
            # Completion rates by phase
            phase_completion = {
                'consent': participants.filter(user__consent_completed=True).count(),
                'pre_quiz': participants.filter(user__pre_quiz_completed=True).count(),
                'interaction': participants.filter(user__interaction_completed=True).count(),
                'post_quiz': participants.filter(user__post_quiz_completed=True).count(),
            }
            
            # Data collection statistics
            total_interactions = sum(p.interaction_logs.count() for p in participants)
            total_chat_messages = sum(p.chat_interactions.count() for p in participants)
            total_pdf_views = sum(p.pdf_behaviors.count() for p in participants)
            total_quiz_responses = sum(p.quiz_responses.count() for p in participants)
            
            # Time-based statistics
            study_duration_days = (timezone.now() - study.created_at).days
            avg_completion_time = None
            if completed_participants > 0:
                # This would need to be calculated from session data
                pass
            
            return {
                'study_id': study_id,
                'study_name': study.name,
                'study_description': study.description,
                'created_at': study.created_at.isoformat(),
                'is_active': study.is_active,
                'study_duration_days': study_duration_days,
                'participant_statistics': {
                    'total_participants': total_participants,
                    'completed_participants': completed_participants,
                    'withdrawn_participants': withdrawn_participants,
                    'active_participants': total_participants - completed_participants - withdrawn_participants,
                    'completion_rate': (completed_participants / total_participants * 100) if total_participants > 0 else 0,
                    'withdrawal_rate': (withdrawn_participants / total_participants * 100) if total_participants > 0 else 0,
                    'max_participants': study.max_participants,
                    'enrollment_progress': (total_participants / study.max_participants * 100) if study.max_participants > 0 else 0
                },
                'group_distribution': group_distribution,
                'phase_completion': {
                    'consent': (phase_completion['consent'] / total_participants * 100) if total_participants > 0 else 0,
                    'pre_quiz': (phase_completion['pre_quiz'] / total_participants * 100) if total_participants > 0 else 0,
                    'interaction': (phase_completion['interaction'] / total_participants * 100) if total_participants > 0 else 0,
                    'post_quiz': (phase_completion['post_quiz'] / total_participants * 100) if total_participants > 0 else 0,
                },
                'data_collection': {
                    'total_interactions': total_interactions,
                    'total_chat_messages': total_chat_messages,
                    'total_pdf_views': total_pdf_views,
                    'total_quiz_responses': total_quiz_responses,
                    'avg_interactions_per_participant': total_interactions / total_participants if total_participants > 0 else 0,
                    'avg_chat_messages_per_participant': total_chat_messages / total_participants if total_participants > 0 else 0,
                    'avg_pdf_views_per_participant': total_pdf_views / total_participants if total_participants > 0 else 0,
                    'avg_quiz_responses_per_participant': total_quiz_responses / total_participants if total_participants > 0 else 0,
                },
                'study_configuration': {
                    'requires_consent': study.requires_consent,
                    'has_pre_quiz': study.has_pre_quiz,
                    'has_post_quiz': study.has_post_quiz,
                    'auto_assign_groups': study.auto_assign_groups,
                    'group_balance_ratio': study.group_balance_ratio,
                    'estimated_duration_minutes': study.estimated_duration_minutes
                }
            }
            
        except ResearchStudy.DoesNotExist:
            return {
                'success': False,
                'error': 'Study not found',
                'study_id': study_id
            }
        except Exception as e:
            logger.error(f"Error generating study summary: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


# Global instance
research_utilities = ResearchUtilities()


# Convenience functions
def generate_participant_id(prefix: str = None, length: int = None) -> str:
    return research_utilities.generate_participant_id(prefix, length)

def generate_session_id(participant_id: str) -> str:
    return research_utilities.generate_session_id(participant_id)

def assign_group_random(study_id: str, participant_count: int = 1) -> List[str]:
    return research_utilities.assign_group_random(study_id, participant_count)

def assign_group_balanced(study_id: str, participant_count: int = 1) -> List[str]:
    return research_utilities.assign_group_balanced(study_id, participant_count)

def bulk_generate_participants(study_id: str, count: int, assignment_method: str = "balanced") -> Dict[str, Any]:
    return research_utilities.bulk_generate_participants(study_id, count, assignment_method)

def validate_data_integrity(study_id: str = None) -> Dict[str, Any]:
    return research_utilities.validate_data_integrity(study_id)

def generate_study_summary(study_id: str) -> Dict[str, Any]:
    return research_utilities.generate_study_summary(study_id)