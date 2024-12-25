from datetime import datetime
from sqlalchemy import BigInteger, VARCHAR, ForeignKey, DateTime, Boolean, Column, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(AsyncAttrs, DeclarativeBase):
    pass


class UsersTable(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    username: Mapped[str] = mapped_column(VARCHAR)
    name: Mapped[str] = mapped_column(VARCHAR)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    generations: Mapped[int] = mapped_column(Integer, default=1)
    sub: Mapped[datetime] = mapped_column(DateTime, default=None, nullable=True)
    entry: Mapped[datetime] = mapped_column(DateTime, default=datetime.today())
    deeplink: Mapped[str] = mapped_column(VARCHAR)
    join: Mapped[str] = mapped_column(VARCHAR, nullable=True, default=None) # диплинк по которому юзер первый раз зашел в бота
    referral: Mapped[str] = mapped_column(VARCHAR, nullable=True, default=None)
    refs: Mapped[int] = mapped_column(BigInteger, default=0)  # Кол-во зашедших рефералов
    active: Mapped[int] = mapped_column(Integer, default=1)
    activity: Mapped[DateTime] = mapped_column(DateTime, default=datetime.today())


class UserPhotosTable(Base):
    __tablename__ = 'user_photos'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(BigInteger)
    photo: Mapped[int] = mapped_column(VARCHAR)


class DeeplinksTable(Base):
    __tablename__ = 'deeplinks'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    link: Mapped[str] = mapped_column(VARCHAR)
    entry: Mapped[int] = mapped_column(BigInteger, default=0)


class AdminsTable(Base):
    __tablename__ = 'admins'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(BigInteger)
    name: Mapped[str] = mapped_column(VARCHAR)


class OneTimeLinksIdsTable(Base):
    __tablename__ = 'links'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    link: Mapped[str] = mapped_column(VARCHAR)


class RatesTable(Base):
    __tablename__ = 'rates'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    amount: Mapped[int] = mapped_column(Integer)
    price: Mapped[int] = mapped_column(Integer)
    category: Mapped[str] = mapped_column(VARCHAR)


class VouchersTable(Base):
    __tablename__ = 'vouchers'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    code: Mapped[str] = mapped_column(String, unique=True)
    amount: Mapped[int] = mapped_column(Integer, unique=True)
    inputs: Mapped[int] = mapped_column(Integer, default=0)


class UserVouchersTable(Base):
    __tablename__ = 'user-vouchers'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    code: Mapped[str] = mapped_column(ForeignKey('vouchers.code', ondelete='CASCADE'))


class PhotosTable(Base):
    __tablename__ = 'photos'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    photo: Mapped[str] = mapped_column(VARCHAR)
    category: Mapped[str] = mapped_column(VARCHAR)


class PriceTable(Base):
    __tablename__ = 'gen_price'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    amount: Mapped[int] = mapped_column(Integer)


class SubTermsTable(Base):
    __tablename__ = 'subterms'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    watermark: Mapped[bool] = mapped_column(Boolean)
    background: Mapped[bool] = mapped_column(Boolean)
    photos: Mapped[int] = mapped_column(Integer, default=3)
