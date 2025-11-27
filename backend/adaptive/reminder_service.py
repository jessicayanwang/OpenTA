"""
Reminder Service
Sends daily reminders for pop quizzes, gap checks, and exam prep
"""
from datetime import datetime, timedelta, time
from typing import List, Dict, Optional
from dataclasses import dataclass, field
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

@dataclass
class Reminder:
    """A scheduled reminder"""
    reminder_id: str
    student_id: str
    reminder_type: str  # "daily_quiz", "gap_check", "exam_runway", "refresher"
    scheduled_time: datetime
    message: str
    data: Dict = field(default_factory=dict)
    sent: bool = False
    sent_at: Optional[datetime] = None

class ReminderService:
    """
    Manages reminders and notifications
    Supports email and in-app notifications
    """
    
    def __init__(self):
        self.reminders: Dict[str, List[Reminder]] = {}  # student_id -> [reminders]
        self.daily_quiz_time = time(9, 0)  # 9 AM default
        self.gap_check_time = time(20, 0)  # 8 PM default
        
        # Email configuration (optional)
        self.email_enabled = bool(os.getenv("SMTP_SERVER"))
        if self.email_enabled:
            self.smtp_server = os.getenv("SMTP_SERVER")
            self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
            self.smtp_username = os.getenv("SMTP_USERNAME")
            self.smtp_password = os.getenv("SMTP_PASSWORD")
            self.from_email = os.getenv("FROM_EMAIL", "noreply@openta.edu")
    
    def schedule_daily_quiz_reminder(self, student_id: str):
        """Schedule daily quiz reminder for tomorrow at 9 AM"""
        tomorrow = datetime.now().date() + timedelta(days=1)
        reminder_time = datetime.combine(tomorrow, self.daily_quiz_time)
        
        reminder = Reminder(
            reminder_id=f"daily_quiz_{student_id}_{tomorrow.isoformat()}",
            student_id=student_id,
            reminder_type="daily_quiz",
            scheduled_time=reminder_time,
            message="☀️ Your 3 daily practice items are ready!",
            data={
                "action_url": "/adaptive/daily-quiz",
                "estimated_time": "5 minutes"
            }
        )
        
        self._add_reminder(student_id, reminder)
        return reminder
    
    def schedule_gap_check_reminder(
        self,
        student_id: str,
        exam_type: str,
        day_number: int,
        num_questions: int
    ):
        """Schedule gap check reminder for exam runway"""
        today = datetime.now().date()
        reminder_time = datetime.combine(today, self.gap_check_time)
        
        reminder = Reminder(
            reminder_id=f"gap_check_{student_id}_{day_number}",
            student_id=student_id,
            reminder_type="gap_check",
            scheduled_time=reminder_time,
            message=f"📊 Day {day_number} Gap Check: {num_questions} questions",
            data={
                "action_url": f"/adaptive/gap-check?exam_type={exam_type}&day={day_number}",
                "exam_type": exam_type,
                "day_number": day_number,
                "num_questions": num_questions
            }
        )
        
        self._add_reminder(student_id, reminder)
        return reminder
    
    def schedule_exam_countdown_reminder(
        self,
        student_id: str,
        exam_type: str,
        exam_date: datetime,
        days_until: int
    ):
        """Schedule exam countdown reminder (7 days, 3 days, 1 day before)"""
        if days_until not in [7, 3, 1]:
            return None
        
        now = datetime.now()
        
        messages = {
            7: f"🎯 7 days until {exam_type}! Ready to start your exam prep runway?",
            3: f"⚡ 3 days until {exam_type}! Time for your mock exam",
            1: f"📚 Tomorrow is your {exam_type}! Light review and rest today"
        }
        
        reminder = Reminder(
            reminder_id=f"exam_countdown_{student_id}_{exam_type}_{days_until}d",
            student_id=student_id,
            reminder_type="exam_runway",
            scheduled_time=now,
            message=messages[days_until],
            data={
                "action_url": f"/adaptive/exam-runway?exam_type={exam_type}",
                "exam_type": exam_type,
                "days_until": days_until
            }
        )
        
        self._add_reminder(student_id, reminder)
        return reminder
    
    def schedule_refresher_reminder(
        self,
        student_id: str,
        topic: str,
        scheduled_for: str = "tonight"
    ):
        """Schedule refresher topic reminder"""
        if scheduled_for == "tonight":
            reminder_time = datetime.combine(datetime.now().date(), self.gap_check_time)
        else:
            # Parse other formats if needed
            reminder_time = datetime.now() + timedelta(hours=2)
        
        reminder = Reminder(
            reminder_id=f"refresher_{student_id}_{topic}_{datetime.now().timestamp()}",
            student_id=student_id,
            reminder_type="refresher",
            scheduled_time=reminder_time,
            message=f"🔄 Time to refresh your understanding of {topic}",
            data={
                "action_url": f"/study-plan?highlight={topic}",
                "topic": topic
            }
        )
        
        self._add_reminder(student_id, reminder)
        return reminder
    
    def get_pending_reminders(self, student_id: str) -> List[Reminder]:
        """Get all pending reminders for a student"""
        if student_id not in self.reminders:
            return []
        
        now = datetime.now()
        pending = [
            r for r in self.reminders[student_id]
            if not r.sent and r.scheduled_time <= now
        ]
        
        return pending
    
    def get_upcoming_reminders(
        self,
        student_id: str,
        hours_ahead: int = 24
    ) -> List[Reminder]:
        """Get upcoming reminders within next N hours"""
        if student_id not in self.reminders:
            return []
        
        now = datetime.now()
        cutoff = now + timedelta(hours=hours_ahead)
        
        upcoming = [
            r for r in self.reminders[student_id]
            if not r.sent and now < r.scheduled_time <= cutoff
        ]
        
        # Sort by scheduled time
        upcoming.sort(key=lambda r: r.scheduled_time)
        
        return upcoming
    
    def mark_as_sent(self, reminder_id: str, student_id: str):
        """Mark a reminder as sent"""
        if student_id not in self.reminders:
            return
        
        for reminder in self.reminders[student_id]:
            if reminder.reminder_id == reminder_id:
                reminder.sent = True
                reminder.sent_at = datetime.now()
                break
    
    def send_email_reminder(self, reminder: Reminder, student_email: str):
        """Send email reminder (if email is configured)"""
        if not self.email_enabled:
            return False
        
        try:
            # Create email
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"OpenTA: {reminder.message}"
            msg["From"] = self.from_email
            msg["To"] = student_email
            
            # Plain text version
            text = f"""
{reminder.message}

{reminder.data.get('estimated_time', '')}

Take action: {os.getenv('APP_URL', 'http://localhost:3000')}{reminder.data.get('action_url', '')}

---
OpenTA - Your AI Teaching Assistant
            """
            
            # HTML version
            html = f"""
<html>
  <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
      <h2 style="color: #2563eb;">{reminder.message}</h2>
      <p>{reminder.data.get('estimated_time', '')}</p>
      <a href="{os.getenv('APP_URL', 'http://localhost:3000')}{reminder.data.get('action_url', '')}"
         style="display: inline-block; padding: 12px 24px; background-color: #2563eb; color: white; text-decoration: none; border-radius: 8px; margin-top: 16px;">
        Take Action
      </a>
      <hr style="margin: 32px 0; border: none; border-top: 1px solid #e5e7eb;">
      <p style="font-size: 12px; color: #6b7280;">OpenTA - Your AI Teaching Assistant</p>
    </div>
  </body>
</html>
            """
            
            msg.attach(MIMEText(text, "plain"))
            msg.attach(MIMEText(html, "html"))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            return True
        
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False
    
    def _add_reminder(self, student_id: str, reminder: Reminder):
        """Add a reminder to the queue"""
        if student_id not in self.reminders:
            self.reminders[student_id] = []
        
        self.reminders[student_id].append(reminder)
    
    def cleanup_old_reminders(self, days_old: int = 7):
        """Remove old sent reminders"""
        cutoff = datetime.now() - timedelta(days=days_old)
        
        for student_id in self.reminders:
            self.reminders[student_id] = [
                r for r in self.reminders[student_id]
                if not r.sent or (r.sent_at and r.sent_at > cutoff)
            ]
