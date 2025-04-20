from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

Base = declarative_base()
engine = create_engine("sqlite:///bot.db")
Session = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    username = Column(String)
    balance = Column(Integer, default=0)
    referrer_id = Column(Integer, ForeignKey("users.telegram_id"))
    referrals = relationship("User", backref="referrer", remote_side=[telegram_id])

class SupportTicket(Base):
    __tablename__ = "support_tickets"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    message = Column(String)
    status = Column(String, default="open")

Base.metadata.create_all(engine)
