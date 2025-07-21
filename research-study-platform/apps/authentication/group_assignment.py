from django.db import transaction
from apps.core.models import User


def get_balanced_study_group():
    """
    Assign users to study groups in a balanced way.
    Returns the group with fewer participants to maintain balance.
    """
    with transaction.atomic():
        # Count current users in each group
        pdf_count = User.objects.filter(study_group='PDF').count()
        chatgpt_count = User.objects.filter(study_group='CHATGPT').count()
        
        print(f"📊 Current group distribution - PDF: {pdf_count}, ChatGPT: {chatgpt_count}")
        
        # Assign to the group with fewer participants
        if pdf_count <= chatgpt_count:
            assigned_group = 'PDF'
        else:
            assigned_group = 'CHATGPT'
        
        print(f"🎯 Assigned to group: {assigned_group}")
        return assigned_group


def get_group_statistics():
    """
    Get current group distribution statistics for monitoring.
    """
    pdf_count = User.objects.filter(study_group='PDF').count()
    chatgpt_count = User.objects.filter(study_group='CHATGPT').count()
    total_users = pdf_count + chatgpt_count
    
    return {
        'pdf_count': pdf_count,
        'chatgpt_count': chatgpt_count,
        'total_users': total_users,
        'pdf_percentage': (pdf_count / total_users * 100) if total_users > 0 else 0,
        'chatgpt_percentage': (chatgpt_count / total_users * 100) if total_users > 0 else 0,
        'balance_difference': abs(pdf_count - chatgpt_count)
    }