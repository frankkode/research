from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task
def schedule_transfer_quiz_notification(user_id, scheduled_time, user_email):
    """
    Schedule a transfer quiz notification to be sent 24 hours after post-quiz completion
    """
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Parse the scheduled time
        scheduled_datetime = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
        
        # Wait until the scheduled time (this would be handled by Celery Beat in production)
        # For now, we'll use countdown parameter
        now = timezone.now()
        if scheduled_datetime > now:
            countdown_seconds = (scheduled_datetime - now).total_seconds()
            # Re-schedule this task to run at the right time
            return schedule_transfer_quiz_notification.apply_async(
                args=[user_id, scheduled_time, user_email],
                countdown=countdown_seconds
            )
        
        # Get the user
        user = User.objects.get(id=user_id)
        
        # Generate transfer quiz link
        transfer_quiz_url = f"{settings.FRONTEND_URL}/quiz/transfer"
        
        # Email subject and body
        subject = "Transfer Knowledge Quiz Available - Research Study"
        
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
                .cta-button {{ display: inline-block; background: #28a745; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; margin: 20px 0; }}
                .info-box {{ background: #e3f2fd; border-left: 4px solid #2196f3; padding: 15px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #6c757d; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Transfer Quiz Now Available!</h1>
                    <p>Your 24-hour waiting period is complete</p>
                </div>
                
                <div class="content">
                    <h2>Hello {user.first_name or user.username}!</h2>
                    
                    <p>Great news! You can now access the <strong>Transfer Knowledge Quiz</strong> - the final assessment in our research study.</p>
                    
                    <div class="info-box">
                        <h3>📋 About the Transfer Quiz:</h3>
                        <ul>
                            <li>Apply your Linux knowledge to new scenarios</li>
                            <li>5 questions testing knowledge transfer</li>
                            <li>Approximately 10 minutes to complete</li>
                            <li>This is the final step in the study</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center;">
                        <a href="{transfer_quiz_url}" class="cta-button">
                            Start Transfer Quiz
                        </a>
                    </div>
                    
                    <div class="info-box">
                        <h3>⏰ Important Notes:</h3>
                        <ul>
                            <li>This link will remain active for 7 days</li>
                            <li>You can only take this quiz once</li>
                            <li>Make sure you have a stable internet connection</li>
                            <li>Set aside 15 minutes of uninterrupted time</li>
                        </ul>
                    </div>
                    
                    <p>Thank you for your participation in this research study!</p>
                    
                    <p><strong>Need help?</strong> If you experience any issues accessing the quiz, please contact the research team.</p>
                </div>
                
                <div class="footer">
                    <p>This email was sent as part of the Linux Learning Research Study</p>
                    <p>Study ID: {user.participant_id}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        plain_message = f"""
        Transfer Quiz Now Available!
        
        Hello {user.first_name or user.username}!
        
        Great news! You can now access the Transfer Knowledge Quiz - the final assessment in our research study.
        
        About the Transfer Quiz:
        • Apply your Linux knowledge to new scenarios
        • 5 questions testing knowledge transfer  
        • Approximately 10 minutes to complete
        • This is the final step in the study
        
        Access your quiz here: {transfer_quiz_url}
        
        Important Notes:
        • This link will remain active for 7 days
        • You can only take this quiz once
        • Make sure you have a stable internet connection
        • Set aside 15 minutes of uninterrupted time
        
        Thank you for your participation in this research study!
        
        Need help? If you experience any issues accessing the quiz, please contact the research team.
        
        Study ID: {user.participant_id}
        """
        
        # Send the email
        try:
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user_email],
                html_message=html_message,
                fail_silently=False
            )
            
            logger.info(f"Transfer quiz notification sent successfully to user {user_id} ({user_email})")
            
            # Update user record to indicate notification was sent
            user.transfer_quiz_notification_sent = True
            user.transfer_quiz_notification_sent_at = timezone.now()
            user.save()
            
            return f"Transfer quiz notification sent to {user_email}"
            
        except Exception as email_error:
            logger.error(f"Failed to send transfer quiz notification email to {user_email}: {str(email_error)}")
            return f"Failed to send email: {str(email_error)}"
            
    except Exception as e:
        logger.error(f"Error in schedule_transfer_quiz_notification task: {str(e)}")
        return f"Task failed: {str(e)}"


@shared_task
def send_manual_transfer_quiz_link(user_id, admin_message=None):
    """
    Manually send transfer quiz link (for admin use when automated system fails)
    """
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        user = User.objects.get(id=user_id)
        
        # Check if user has completed post-quiz
        if not user.post_quiz_completed:
            return "User has not completed post-quiz yet"
        
        # Check if 24 hours have passed
        if user.post_quiz_completed_at:
            time_diff = timezone.now() - user.post_quiz_completed_at
            if time_diff.total_seconds() < 24 * 3600:  # 24 hours in seconds
                hours_remaining = 24 - (time_diff.total_seconds() / 3600)
                return f"Transfer quiz not available yet. {hours_remaining:.1f} hours remaining."
        
        # Send the notification immediately
        return schedule_transfer_quiz_notification(
            user_id=user_id,
            scheduled_time=timezone.now().isoformat(),
            user_email=user.email
        )
        
    except Exception as e:
        logger.error(f"Error in send_manual_transfer_quiz_link task: {str(e)}")
        return f"Manual send failed: {str(e)}"