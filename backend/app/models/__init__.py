# Import every model here so Base.metadata.create_all() (used in create_app)
# and Alembic autogeneration (if added later) can discover all tables.
from app.models.college import College  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.company import Company  # noqa: F401
from app.models.role import Role  # noqa: F401
from app.models.experience import Experience  # noqa: F401
from app.models.round import RecruitmentRound  # noqa: F401
from app.models.question import Question  # noqa: F401
from app.models.bookmark import Bookmark  # noqa: F401
from app.models.helpful_vote import HelpfulVote  # noqa: F401
from app.models.report import Report  # noqa: F401
