from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from codomyrmex.logging_monitoring.logger_config import get_logger

"""Security awareness training."""

logger = get_logger(__name__)


class TrainingTopic(Enum):
    """Topics available for security awareness training."""
    PHISHING = "phishing"
    SOCIAL_ENGINEERING = "social_engineering"
    PASSWORD_SECURITY = "password_security"
    DATA_HANDLING = "data_handling"
    PHYSICAL_SECURITY = "physical_security"
    INCIDENT_REPORTING = "incident_reporting"
    REMOTE_WORK = "remote_work"
    INSIDER_THREATS = "insider_threats"


class TrainingDifficulty(Enum):
    """Difficulty levels for training modules."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class TrainingModule:
    """Represents a security awareness training module."""

    module_id: str
    title: str
    description: str
    content: str
    created_at: datetime
    difficulty: str  # beginner, intermediate, advanced


@dataclass
class TrainingResult:
    """Results from training assessment."""

    user_id: str
    module_id: str
    score: float  # 0.0 to 1.0
    completed_at: datetime
    effectiveness: str  # low, medium, high


class AwarenessTrainer:
    """Manages security awareness training."""

    TRAINING_TEMPLATES: dict[TrainingTopic, dict] = {
        TrainingTopic.PHISHING: {
            "title": "Phishing Awareness",
            "description": "Learn to identify and avoid phishing emails, links, and attachments",
            "content": "Phishing attacks use deceptive emails to trick users into revealing sensitive information. Look for suspicious sender addresses, urgency tactics, mismatched URLs, and requests for credentials.",
            "difficulty": TrainingDifficulty.BEGINNER,
        },
        TrainingTopic.SOCIAL_ENGINEERING: {
            "title": "Social Engineering Defense",
            "description": "Recognize and resist social engineering manipulation techniques",
            "content": "Social engineering exploits human psychology. Common tactics include pretexting, baiting, tailgating, and quid pro quo attacks. Always verify identities and follow established procedures.",
            "difficulty": TrainingDifficulty.INTERMEDIATE,
        },
        TrainingTopic.PASSWORD_SECURITY: {
            "title": "Password Security Best Practices",
            "description": "Create and manage strong passwords and authentication methods",
            "content": "Use unique, complex passwords for each account. Enable multi-factor authentication. Use a password manager. Never share credentials. Rotate passwords periodically.",
            "difficulty": TrainingDifficulty.BEGINNER,
        },
        TrainingTopic.DATA_HANDLING: {
            "title": "Secure Data Handling",
            "description": "Properly classify, store, transmit, and dispose of sensitive data",
            "content": "Classify data by sensitivity level. Encrypt data at rest and in transit. Follow data retention policies. Use secure channels for sharing. Properly dispose of physical and digital media.",
            "difficulty": TrainingDifficulty.INTERMEDIATE,
        },
        TrainingTopic.PHYSICAL_SECURITY: {
            "title": "Physical Security Awareness",
            "description": "Maintain physical security of workspaces, devices, and facilities",
            "content": "Lock workstations when away. Secure portable devices. Report tailgating. Challenge unknown visitors. Protect printed materials. Use clean desk policy.",
            "difficulty": TrainingDifficulty.BEGINNER,
        },
        TrainingTopic.INCIDENT_REPORTING: {
            "title": "Security Incident Reporting",
            "description": "Identify, report, and respond to security incidents effectively",
            "content": "Know your incident reporting channels. Report suspicious activity immediately. Preserve evidence. Document timeline of events. Cooperate with incident response teams.",
            "difficulty": TrainingDifficulty.INTERMEDIATE,
        },
        TrainingTopic.REMOTE_WORK: {
            "title": "Secure Remote Work Practices",
            "description": "Maintain security while working remotely or from public locations",
            "content": "Use VPN for all work connections. Secure home Wi-Fi with strong passwords. Avoid public Wi-Fi for sensitive work. Use privacy screens. Separate work and personal devices.",
            "difficulty": TrainingDifficulty.ADVANCED,
        },
        TrainingTopic.INSIDER_THREATS: {
            "title": "Insider Threat Awareness",
            "description": "Recognize and mitigate risks from insider threats",
            "content": "Insider threats come from current or former employees, contractors, or partners. Watch for unusual data access patterns, policy violations, and behavioral changes. Report concerns through proper channels.",
            "difficulty": TrainingDifficulty.ADVANCED,
        },
    }

    def __init__(self):

        self.modules: dict[str, TrainingModule] = {}
        self.results: list[TrainingResult] = []
        logger.info("AwarenessTrainer initialized")

    def create_module(
        self,
        module_id: str,
        title: str,
        description: str,
        content: str,
        difficulty: str = "intermediate",
    ) -> TrainingModule:
        """Create a new training module."""
        module = TrainingModule(
            module_id=module_id,
            title=title,
            description=description,
            content=content,
            created_at=datetime.now(),
            difficulty=difficulty,
        )
        self.modules[module_id] = module
        logger.info(f"Created training module: {title}")
        return module

    def assess_effectiveness(self, user_id: str) -> dict:
        """Assess training effectiveness for a user."""
        user_results = [r for r in self.results if r.user_id == user_id]

        if not user_results:
            return {
                "user_id": user_id,
                "modules_completed": 0,
                "average_score": 0.0,
                "effectiveness": "unknown",
            }

        avg_score = sum(r.score for r in user_results) / len(user_results)

        effectiveness = "high" if avg_score > 0.8 else "medium" if avg_score > 0.6 else "low"

        return {
            "user_id": user_id,
            "modules_completed": len(user_results),
            "average_score": avg_score,
            "effectiveness": effectiveness,
        }


def create_training_module(
    module_id: str,
    title: str,
    description: str,
    content: str,
    difficulty: str = "intermediate",
    trainer: AwarenessTrainer | None = None,
) -> TrainingModule:
    """Create a training module."""
    if trainer is None:
        trainer = AwarenessTrainer()
    return trainer.create_module(module_id, title, description, content, difficulty)


def assess_training_effectiveness(
    user_id: str,
    trainer: AwarenessTrainer | None = None,
) -> dict:
    """Assess training effectiveness."""
    if trainer is None:
        trainer = AwarenessTrainer()
    return trainer.assess_effectiveness(user_id)

