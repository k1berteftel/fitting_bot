from sqlalchemy import select, insert, update, column, text, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from dateutil.relativedelta import relativedelta
from datetime import datetime

from database.model import (UsersTable, UserPhotosTable, DeeplinksTable, AdminsTable,
                            OneTimeLinksIdsTable, RatesTable, VouchersTable, UserVouchersTable, PhotosTable, PriceTable,
                            SubTermsTable, TextsTable, CountsTable)
from utils.build_ids import get_random_id


async def configurate_prices(sessions: async_sessionmaker):
    async with sessions() as session:
        await session.execute(insert(PriceTable).values(
            amount=1
        ))
        await session.execute(insert(SubTermsTable).values(
            watermark=False,
            background=True
        ))
        await session.execute(insert(TextsTable).values(
            sub_text='Условия подписки',
            ref_text='Условия реферальной программы',
            info_text='Текст информации',
            image_text='Работа с фото модели и фоном. Фон меняется при подписке на бота'
        ))
        await session.execute(insert(CountsTable).values(
            images=0,
            background=0
        ))
        await session.commit()


class DataInteraction():
    def __init__(self, session: async_sessionmaker):
        self._sessions = session

    async def check_user(self, user_id: int) -> bool:
        async with self._sessions() as session:
            result = await session.scalar(select(UsersTable).where(UsersTable.user_id == user_id))
        return True if result else False

    async def check_voucher(self, user_id: int, voucher: str) -> bool:
        async with self._sessions() as session:
            result = await session.scalar(select(VouchersTable).where(VouchersTable.code == voucher))
            print(result)
            if not result:
                return False
            result = await session.scalar(select(UserVouchersTable).where(
                and_(
                    UserVouchersTable.user_id == user_id,
                    UserVouchersTable.code == voucher
                )
            ))
            if result:
                return False
            await session.execute(insert(UserVouchersTable).values(
                user_id=user_id,
                code=voucher
            ))
            await session.execute(update(VouchersTable).where(VouchersTable.code == voucher).values(
                inputs=VouchersTable.inputs + 1
            ))
            await session.commit()
            return True

    async def add_entry(self, link: str):
        async with self._sessions() as session:
            await session.execute(update(DeeplinksTable).where(DeeplinksTable.link == link).values(
                entry=DeeplinksTable.entry+1
            ))
            await session.commit()

    async def add_prizes(self, link: str, prize: int):
        async with self._sessions() as session:
            await session.execute(update(UsersTable).where(UsersTable.deeplink == link).values(
                prizes=UsersTable.prizes + prize
            ))
            await session.commit()

    async def update_user_days(self, user_id: int, days: int):
        async with self._sessions() as session:
            await session.execute(update(UsersTable).where(UsersTable.user_id == user_id).values(
                prizes=UsersTable.days + days
            ))
            await session.commit()

    async def add_refs(self, link: str):
        async with self._sessions() as session:
            await session.execute(update(UsersTable).where(UsersTable.deeplink == link).values(
                refs=UsersTable.refs + 1,
            ))
            await session.commit()

    async def add_user(self, user_id: int, username: str, name: str, join: str|None, referral: str|None):
        if await self.check_user(user_id):
            return
        async with self._sessions() as session:
            await session.execute(insert(UsersTable).values(
                user_id=user_id,
                username=username,
                name=name,
                deeplink=get_random_id(),
                join=join,
                referral=referral
            ))
            await session.commit()

    async def add_user_photo(self, user_id: int, photo: str):
        async with self._sessions() as session:
            await session.execute(insert(UserPhotosTable).values(
                user_id=user_id,
                photo=photo
            ))
            await session.commit()

    async def add_deeplink(self, name: str, link: str):
        async with self._sessions() as session:
            await session.execute(insert(DeeplinksTable).values(
                name=name,
                link=link
            ))
            await session.commit()

    async def add_link(self, link: str):
        async with self._sessions() as session:
            await session.execute(insert(OneTimeLinksIdsTable).values(
                link=link
            ))
            await session.commit()

    async def add_admin(self, user_id: int, name: str):
        async with self._sessions() as session:
            await session.execute(insert(AdminsTable).values(
                user_id=user_id,
                name=name
            ))
            await session.commit()

    async def add_rate(self, amount: int, price: int, category: str):
        async with self._sessions() as session:
            await session.execute(insert(RatesTable).values(
                amount=amount,
                price=price,
                category=category
            ))
            await session.commit()

    async def add_voucher(self, code: str, amount: int):
        async with self._sessions() as session:
            await session.execute(insert(VouchersTable).values(
                code=code,
                amount=amount
            ))
            await session.commit()

    async def add_photo(self, photo: str, category: str):
        async with self._sessions() as session:
            await session.execute(insert(PhotosTable).values(
                photo=photo,
                category=category
            ))
            await session.commit()

    async def add_counts_images(self):
        async with self._sessions() as session:
            await session.execute(update(CountsTable).values(
                images=CountsTable.images + 1
            ))
            await session.commit()

    async def add_counts_background(self):
        async with self._sessions() as session:
            await session.execute(update(CountsTable).values(
                background=CountsTable.background + 1
            ))
            await session.commit()

    async def get_gen_amount(self):
        async with self._sessions() as session:
            result = await session.scalar(select(PriceTable.amount))
        return result

    async def get_counts(self):
        async with self._sessions() as session:
            result = await session.scalar(select(CountsTable))
        return result

    async def get_texts(self):
        async with self._sessions() as session:
            result = await session.scalar(select(TextsTable))
        return result

    async def get_sub_terms(self):
        async with self._sessions() as session:
            result = await session.scalar(select(SubTermsTable))
        return result

    async def get_photos_by_category(self, category: str):
        async with self._sessions() as session:
            result = await session.scalars(select(PhotosTable.photo).where(PhotosTable.category == category))
        return result.fetchall()

    async def voucher_amount(self, code: str):
        async with self._sessions() as session:
            result = await session.scalar(select(VouchersTable.amount).where(VouchersTable.code == code))
        return result

    async def get_user_by_deeplink(self, deeplink):
        async with self._sessions() as session:
            result = await session.scalar(select(UsersTable).where(UsersTable.deeplink == deeplink))
        return result

    async def get_users_by_join_link(self, deeplink: str):
        async with self._sessions() as session:
            result = await session.scalars(select(UsersTable).where(UsersTable.join == deeplink))
        return result.fetchall()

    async def get_vouchers(self):
        async with self._sessions() as session:
            result = await session.scalars(select(VouchersTable))
        return result

    async def get_rates_by_category(self, category: str):
        async with self._sessions() as session:
            result = await session.scalars(select(RatesTable).where(RatesTable.category == category))
        return result.fetchall()

    async def get_rate(self, id: int):
        async with self._sessions() as session:
            result = await session.scalar(select(RatesTable).where(RatesTable.id == id))
        return result

    async def get_user(self, user_id: int):
        async with self._sessions() as session:
            result = await session.scalar(select(UsersTable).where(UsersTable.user_id == user_id))
        return result

    async def get_users(self):
        async with self._sessions() as session:
            result = await session.scalars(select(UsersTable))
        return result.fetchall()

    async def get_links(self):
        async with self._sessions() as session:
            result = await session.scalars(select(OneTimeLinksIdsTable))
        return result.fetchall()

    async def get_admins(self):
        async with self._sessions() as session:
            result = await session.scalars(select(AdminsTable))
        return result.fetchall()

    async def get_deeplinks(self):
        async with self._sessions() as session:
            result = await session.scalars(select(DeeplinksTable))
        return result.fetchall()

    async def get_user_photos(self, user_id: int):
        async with self._sessions() as session:
            result = await session.scalars(select(UserPhotosTable).where(UserPhotosTable.user_id == user_id))
        return result.fetchall()

    async def get_user_photo(self, id: int):
        async with self._sessions() as session:
            result = await session.scalar(select(UserPhotosTable).where(UserPhotosTable.id == id))
        return result

    async def update_user_generations(self, user_id: int, amount: int):
        async with self._sessions() as session:
            await session.execute(update(UsersTable).where(UsersTable.user_id == user_id).values(
                generations=UsersTable.generations + amount
            ))
            await session.commit()

    async def set_active(self, user_id: int, active: int):
        async with self._sessions() as session:
            await session.execute(update(UsersTable).where(UsersTable.user_id == user_id).values(
                active=active
            ))
            await session.commit()

    async def set_activity(self, user_id: int):
        async with self._sessions() as session:
            await session.execute(update(UsersTable).where(UsersTable.user_id == user_id).values(
                activity=datetime.today()
            ))
            await session.commit()

    async def set_rate_amount(self, id: int, amount: int):
        async with self._sessions() as session:
            await session.execute(update(RatesTable).where(RatesTable.id == id).values(
                amount=amount
            ))
            await session.commit()

    async def set_rate_price(self, id: int, price: int):
        async with self._sessions() as session:
            await session.execute(update(RatesTable).where(RatesTable.id == id).values(
                price=price
            ))
            await session.commit()

    async def set_text(self, **kwargs):
        async with self._sessions() as session:
            await session.execute(update(TextsTable).values(
                kwargs
            ))
            await session.commit()

    async def update_gen_amount(self, amount: int):
        async with self._sessions() as session:
            await session.execute(update(PriceTable).values(
                amount=amount
            ))
            await session.commit()

    async def update_sub_photos(self, photos):
        async with self._sessions() as session:
            await session.execute(update(SubTermsTable).values(
                photos=photos
            ))
            await session.commit()

    async def update_sub_terms(self, **kwargs):
        async with self._sessions() as session:
            await session.execute(update(SubTermsTable).values(
                kwargs
            ))
            await session.commit()

    async def update_user_sub(self, user_id: int, days: int|None):
        if days is None:
            async with self._sessions() as session:
                await session.execute(update(UsersTable).where(UsersTable.user_id == user_id).values(
                    sub=days
                ))
        if (await self.get_user(user_id)).sub:
            async with self._sessions() as session:
                sub = await session.scalar(select(UsersTable.sub).where(UsersTable.user_id == user_id))
                print(sub)
                await session.execute(update(UsersTable).where(UsersTable.user_id == user_id).values(
                    sub=sub + relativedelta(days=days)
                ))
                await session.commit()
        else:
            async with self._sessions() as session:
                await session.execute(update(UsersTable).where(UsersTable.user_id == user_id).values(
                    sub=datetime.today() + relativedelta(days=days)
                ))
                await session.commit()

    async def del_rate(self, id: int):
        async with self._sessions() as session:
            await session.execute(delete(RatesTable).where(RatesTable.id == id))
            await session.commit()

    async def del_deeplink(self, link: str):
        async with self._sessions() as session:
            await session.execute(delete(DeeplinksTable).where(DeeplinksTable.link == link))
            await session.commit()

    async def del_link(self, link_id: str):
        async with self._sessions() as session:
            await session.execute(delete(OneTimeLinksIdsTable).where(OneTimeLinksIdsTable.link == link_id))
            await session.commit()

    async def del_admin(self, user_id: int):
        async with self._sessions() as session:
            await session.execute(delete(AdminsTable).where(AdminsTable.user_id == user_id))
            await session.commit()

    async def del_voucher(self, id: int):
        async with self._sessions() as session:
            await session.execute(delete(VouchersTable).where(VouchersTable.id == id))
            await session.commit()

    async def del_user_photo(self, id: int):
        async with self._sessions() as session:
            await session.execute(delete(UserPhotosTable).where(UserPhotosTable.id == id))
            await session.commit()

    async def del_photo(self, photo):
        async with self._sessions() as session:
            await session.execute(delete(PhotosTable).where(PhotosTable.photo == photo))
            await session.commit()
