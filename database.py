from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import datetime

Base = declarative_base()
engine = create_engine('sqlite:///rug_store.db')
Session = sessionmaker(bind=engine)
session = Session()

class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    contact_info = Column(String)

class Rug(Base):
    __tablename__ = 'rugs'
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    type = Column(String)
    size = Column(String)
    photo_path = Column(String)
    received_date = Column(Date)
    due_date = Column(Date)
    price = Column(Float)
    status = Column(String, default="Not Started")
    customer = relationship('Customer', back_populates='rugs')

Customer.rugs = relationship('Rug', order_by=Rug.id, back_populates='customer')


Base.metadata.create_all(engine)


def add_rug(customer_name, contact_info, rug_type, size, price, received_date, due_date, photo_path=None):

    customer = session.query(Customer).filter_by(name=customer_name).first()
    if not customer:
        customer = Customer(name=customer_name, contact_info=contact_info)
        session.add(customer)
        session.commit()


    new_rug = Rug(
        customer_id=customer.id,
        type=rug_type,
        size=size,
        photo_path=photo_path,
        received_date=received_date,
        due_date=due_date,
        price=price,
        status="Not Started"
    )
    session.add(new_rug)
    session.commit()