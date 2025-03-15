from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def create_search_keyboard(
        page: int,
        total_pages: int,
        tag: str,
        data: list,
        title_key: str,
        id_key: str,
        back_callback: str
    ) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        *[
            [InlineKeyboardButton(text=getattr(obj, title_key), callback_data=f"{tag}_{getattr(obj, id_key)}")]
            for obj in data
        ],
        [
            *(
                [InlineKeyboardButton(text="<", callback_data=f"f{tag}_{page - 1}")]
                if page > 1 else
                [InlineKeyboardButton(text="🚫", callback_data=f"null")]
            ),
            InlineKeyboardButton(text=f"📃 {page} / {total_pages}", callback_data="null"),
            *(
                [InlineKeyboardButton(text=">", callback_data=f"f{tag}_{page + 1}")]
                if page != total_pages else
                [InlineKeyboardButton(text="🚫", callback_data=f"null")]
            )
        ],
        [
            InlineKeyboardButton(text="◀️ Назад", callback_data=back_callback)
        ]
    ])