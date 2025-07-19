from decimal import Decimal
from datetime import datetime, timedelta
from django.db.models import Sum, Avg, Count
from django.conf import settings
from .models import ChatInteraction, ChatSession
from apps.core.models import User
import logging

logger = logging.getLogger(__name__)


class CostManagementService:
    """Service for tracking and managing OpenAI API costs"""
    
    # Cost thresholds
    DAILY_COST_LIMIT = Decimal('10.00')  # $10 per day
    WEEKLY_COST_LIMIT = Decimal('50.00')  # $50 per week
    MONTHLY_COST_LIMIT = Decimal('200.00')  # $200 per month
    
    USER_DAILY_LIMIT = Decimal('5.00')  # $5 per user per day
    USER_WEEKLY_LIMIT = Decimal('20.00')  # $20 per user per week
    
    @classmethod
    def get_cost_stats(cls, start_date=None, end_date=None):
        """Get comprehensive cost statistics"""
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
        
        interactions = ChatInteraction.objects.filter(
            message_timestamp__gte=start_date,
            message_timestamp__lte=end_date,
            estimated_cost_usd__isnull=False
        )
        
        stats = {
            'total_cost': interactions.aggregate(
                total=Sum('estimated_cost_usd')
            )['total'] or Decimal('0'),
            'total_interactions': interactions.count(),
            'total_tokens': interactions.aggregate(
                total=Sum('total_tokens')
            )['total'] or 0,
            'average_cost_per_interaction': interactions.aggregate(
                avg=Avg('estimated_cost_usd')
            )['avg'] or Decimal('0'),
            'cost_by_model': interactions.values('openai_model').annotate(
                total_cost=Sum('estimated_cost_usd'),
                count=Count('id')
            ).order_by('-total_cost'),
            'cost_by_user': interactions.values(
                'user__participant_id',
                'user__study_group'
            ).annotate(
                total_cost=Sum('estimated_cost_usd'),
                count=Count('id')
            ).order_by('-total_cost')[:10],
            'daily_costs': cls._get_daily_costs(interactions),
            'period_start': start_date,
            'period_end': end_date
        }
        
        return stats
    
    @classmethod
    def _get_daily_costs(cls, interactions):
        """Get daily cost breakdown"""
        from django.db.models import Sum
        from django.db.models.functions import TruncDate
        
        daily_costs = interactions.annotate(
            date=TruncDate('message_timestamp')
        ).values('date').annotate(
            total_cost=Sum('estimated_cost_usd'),
            count=Count('id')
        ).order_by('date')
        
        return list(daily_costs)
    
    @classmethod
    def check_user_limits(cls, user_id):
        """Check if user has exceeded cost limits"""
        user = User.objects.get(id=user_id)
        now = datetime.now()
        
        # Daily limit check
        daily_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        daily_cost = ChatInteraction.objects.filter(
            user=user,
            message_timestamp__gte=daily_start,
            estimated_cost_usd__isnull=False
        ).aggregate(total=Sum('estimated_cost_usd'))['total'] or Decimal('0')
        
        # Weekly limit check
        weekly_start = now - timedelta(days=7)
        weekly_cost = ChatInteraction.objects.filter(
            user=user,
            message_timestamp__gte=weekly_start,
            estimated_cost_usd__isnull=False
        ).aggregate(total=Sum('estimated_cost_usd'))['total'] or Decimal('0')
        
        return {
            'daily_cost': daily_cost,
            'weekly_cost': weekly_cost,
            'daily_limit_exceeded': daily_cost >= cls.USER_DAILY_LIMIT,
            'weekly_limit_exceeded': weekly_cost >= cls.USER_WEEKLY_LIMIT,
            'daily_remaining': cls.USER_DAILY_LIMIT - daily_cost,
            'weekly_remaining': cls.USER_WEEKLY_LIMIT - weekly_cost
        }
    
    @classmethod
    def get_system_limits(cls):
        """Check system-wide cost limits"""
        now = datetime.now()
        
        # Daily system cost
        daily_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        daily_cost = ChatInteraction.objects.filter(
            message_timestamp__gte=daily_start,
            estimated_cost_usd__isnull=False
        ).aggregate(total=Sum('estimated_cost_usd'))['total'] or Decimal('0')
        
        # Weekly system cost
        weekly_start = now - timedelta(days=7)
        weekly_cost = ChatInteraction.objects.filter(
            message_timestamp__gte=weekly_start,
            estimated_cost_usd__isnull=False
        ).aggregate(total=Sum('estimated_cost_usd'))['total'] or Decimal('0')
        
        # Monthly system cost
        monthly_start = now - timedelta(days=30)
        monthly_cost = ChatInteraction.objects.filter(
            message_timestamp__gte=monthly_start,
            estimated_cost_usd__isnull=False
        ).aggregate(total=Sum('estimated_cost_usd'))['total'] or Decimal('0')
        
        return {
            'daily_cost': daily_cost,
            'weekly_cost': weekly_cost,
            'monthly_cost': monthly_cost,
            'daily_limit_exceeded': daily_cost >= cls.DAILY_COST_LIMIT,
            'weekly_limit_exceeded': weekly_cost >= cls.WEEKLY_COST_LIMIT,
            'monthly_limit_exceeded': monthly_cost >= cls.MONTHLY_COST_LIMIT,
            'daily_remaining': cls.DAILY_COST_LIMIT - daily_cost,
            'weekly_remaining': cls.WEEKLY_COST_LIMIT - weekly_cost,
            'monthly_remaining': cls.MONTHLY_COST_LIMIT - monthly_cost
        }
    
    @classmethod
    def get_top_users_by_cost(cls, limit=10):
        """Get users with highest costs"""
        return ChatInteraction.objects.filter(
            estimated_cost_usd__isnull=False
        ).values(
            'user__participant_id',
            'user__study_group',
            'user__username'
        ).annotate(
            total_cost=Sum('estimated_cost_usd'),
            total_interactions=Count('id'),
            total_tokens=Sum('total_tokens')
        ).order_by('-total_cost')[:limit]
    
    @classmethod
    def export_cost_report(cls, start_date=None, end_date=None):
        """Export detailed cost report"""
        stats = cls.get_cost_stats(start_date, end_date)
        system_limits = cls.get_system_limits()
        top_users = cls.get_top_users_by_cost()
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'period': {
                'start': stats['period_start'].isoformat(),
                'end': stats['period_end'].isoformat()
            },
            'summary': {
                'total_cost': float(stats['total_cost']),
                'total_interactions': stats['total_interactions'],
                'total_tokens': stats['total_tokens'],
                'average_cost_per_interaction': float(stats['average_cost_per_interaction'])
            },
            'limits': {
                'daily': {
                    'current': float(system_limits['daily_cost']),
                    'limit': float(cls.DAILY_COST_LIMIT),
                    'remaining': float(system_limits['daily_remaining'])
                },
                'weekly': {
                    'current': float(system_limits['weekly_cost']),
                    'limit': float(cls.WEEKLY_COST_LIMIT),
                    'remaining': float(system_limits['weekly_remaining'])
                },
                'monthly': {
                    'current': float(system_limits['monthly_cost']),
                    'limit': float(cls.MONTHLY_COST_LIMIT),
                    'remaining': float(system_limits['monthly_remaining'])
                }
            },
            'cost_by_model': [
                {
                    'model': item['openai_model'],
                    'total_cost': float(item['total_cost']),
                    'count': item['count']
                }
                for item in stats['cost_by_model']
            ],
            'top_users': [
                {
                    'participant_id': user['user__participant_id'],
                    'study_group': user['user__study_group'],
                    'username': user['user__username'],
                    'total_cost': float(user['total_cost']),
                    'total_interactions': user['total_interactions'],
                    'total_tokens': user['total_tokens']
                }
                for user in top_users
            ],
            'daily_breakdown': [
                {
                    'date': item['date'].isoformat(),
                    'cost': float(item['total_cost']),
                    'interactions': item['count']
                }
                for item in stats['daily_costs']
            ]
        }
        
        return report