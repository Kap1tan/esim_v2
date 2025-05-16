# keyboards/inline.py

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Dict, Any


def get_start_keyboard():
    """Клавиатура для стартового меню"""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="💳 Купить eSIM", callback_data="buy_esim"),
        InlineKeyboardButton(text="👤 Профиль", callback_data="profile")
    )
    builder.row(
        InlineKeyboardButton(text="📱 Как установить eSIM", callback_data="setup"),
        InlineKeyboardButton(text="❓ Вопросы и ответы", callback_data="questions")
    )
    builder.row(
        InlineKeyboardButton(text="💰 Зарабатывай с WorldWideSim", callback_data="partner")
    )

    return builder.as_markup()


def get_buy_esim_keyboard():
    """Клавиатура для выбора региона"""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="🐼 Азия", callback_data="region_asia")
    )
    builder.row(
        InlineKeyboardButton(text="🐪 Ближний восток", callback_data="region_middle_east")
    )
    builder.row(
        InlineKeyboardButton(text="🐌 Европа", callback_data="region_europe")
    )
    builder.row(
        InlineKeyboardButton(text="🦅 Америка", callback_data="region_americas")
    )
    builder.row(
        InlineKeyboardButton(text="🐻 СНГ", callback_data="region_cis")
    )
    builder.row(
        InlineKeyboardButton(text="🦁 Африка", callback_data="region_africa")
    )
    builder.row(
        InlineKeyboardButton(text="🐨 Океания", callback_data="region_oceania")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")
    )

    return builder.as_markup()


def get_countries_keyboard(region, countries):
    """Клавиатура со странами для выбранного региона"""
    builder = InlineKeyboardBuilder()

    for country in countries:
        builder.row(
            InlineKeyboardButton(text=country, callback_data=f"country_{country}")
        )

    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="buy_esim")
    )

    return builder.as_markup()


def format_package_button_text(package: Dict[str, Any]) -> str:
    """Форматирует текст кнопки для пакета"""
    package_name = package.get("name", "Неизвестный тариф")
    volume_bytes = package.get("volume", 0)
    duration = package.get("duration", 0)
    duration_unit = package.get("durationUnit", "DAY")
    price = package.get("price", 0) / 10000  # Преобразование в доллары

    # Преобразование байтов в МБ или ГБ
    if volume_bytes >= 1073741824:  # 1 ГБ
        volume_str = f"{volume_bytes / 1073741824:.1f} ГБ"
    else:
        volume_str = f"{volume_bytes / 1048576:.0f} МБ"

    # Форматирование срока действия
    if duration_unit == "DAY":
        duration_str = f"{duration} дней"
    elif duration_unit == "MONTH":
        duration_str = f"{duration} месяцев"
    else:
        duration_str = f"{duration} {duration_unit}"

    return f"{package_name} ({volume_str}, {duration_str}) - ${price:.2f}"


def get_packages_keyboard(packages: List[Dict[str, Any]], country_code: str):
    """Клавиатура с пакетами для выбранной страны"""
    builder = InlineKeyboardBuilder()

    for i, package in enumerate(packages):
        button_text = format_package_button_text(package)
        builder.row(
            InlineKeyboardButton(text=button_text, callback_data=f"package_{i}")
        )

    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data=f"buy_esim")
    )

    return builder.as_markup()


def get_confirm_keyboard(country_code: str):
    """Клавиатура для подтверждения покупки"""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="✅ Подтвердить и оплатить", callback_data="confirm_purchase")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад к тарифам", callback_data=f"country_{country_code}")
    )
    builder.row(
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_purchase")
    )

    return builder.as_markup()


def get_payment_done_keyboard():
    """Клавиатура после завершения платежа"""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="📱 Показать детали eSIM", callback_data="show_esim_details")
    )

    return builder.as_markup()


def get_back_to_countries_keyboard(region_data: str):
    """Клавиатура для возврата к выбору стран"""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="⬅️ Назад к выбору стран", callback_data=region_data)
    )

    return builder.as_markup()


def get_profile_keyboard():
    """Клавиатура для профиля"""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")
    )

    return builder.as_markup()


def get_setup_keyboard():
    """Клавиатура для установки eSIM"""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")
    )

    return builder.as_markup()


def get_questions_keyboard():
    """Клавиатура для раздела вопросов"""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="Что такое eSIM?", callback_data="qa_what_is_esim")
    )
    builder.row(
        InlineKeyboardButton(text="Как подключить интернет?", callback_data="qa_how_to_connect")
    )
    builder.row(
        InlineKeyboardButton(text="Какой пакет мне выбрать?", callback_data="qa_which_package")
    )
    builder.row(
        InlineKeyboardButton(text="Можно ли звонить и писать SMS?", callback_data="qa_can_call_sms")
    )
    builder.row(
        InlineKeyboardButton(text="Мой телефон поддерживает eSIM?", callback_data="qa_phone_support")
    )
    builder.row(
        InlineKeyboardButton(text="Когда стартует тариф?", callback_data="qa_when_starts")
    )
    builder.row(
        InlineKeyboardButton(text="Как продлить eSIM?", callback_data="qa_how_extend")
    )
    builder.row(
        InlineKeyboardButton(text="Можно ли вернуть деньги?", callback_data="qa_refund")
    )
    builder.row(
        InlineKeyboardButton(text="Насколько безопасна eSIM?", callback_data="qa_is_safe")
    )
    builder.row(
        InlineKeyboardButton(text="Можно ли раздавать интернет?", callback_data="qa_share_internet")
    )
    builder.row(
        InlineKeyboardButton(text="Работают ли WhatsApp и Telegram?", callback_data="qa_messengers_work")
    )
    builder.row(
        InlineKeyboardButton(text="Чем eSIM лучше роуминга?", callback_data="qa_better_than_roaming")
    )
    builder.row(
        InlineKeyboardButton(text="Почему интернет бывает медленным?", callback_data="qa_slow_internet")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")
    )

    return builder.as_markup()


def get_qa_back_keyboard():
    """Клавиатура возврата к вопросам"""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="⬅️ Назад к вопросам", callback_data="questions")
    )

    return builder.as_markup()


def get_back_to_main_keyboard():
    """Клавиатура возврата к главному меню"""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="⬅️ В главное меню", callback_data="back_to_main")
    )

    return builder.as_markup()


def get_partner_keyboard():
    """Клавиатура для выбора типа партнерства"""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="Партнерская программа", callback_data="partner_referral")
    )
    builder.row(
        InlineKeyboardButton(text="Монетизировать сообщество", callback_data="partner_community")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")
    )

    return builder.as_markup()


def get_partner_referral_keyboard():
    """Клавиатура для партнерской программы"""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="📎 Поделиться с другом", callback_data="share_referral")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="partner")
    )

    return builder.as_markup()


def get_partner_community_keyboard():
    """Клавиатура для монетизации сообщества"""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="🛠 Получить партнёрского бота", url="https://t.me/levshurygin")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="partner")
    )

    return builder.as_markup()


def get_feedback_keyboard():
    """Клавиатура для обратной связи"""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="👍 Да", callback_data="feedback_yes"),
        InlineKeyboardButton(text="😕 Нет", callback_data="feedback_no")
    )

    return builder.as_markup()


def get_feedback_no_keyboard():
    """Клавиатура для отрицательной обратной связи"""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="Ответы на частые вопросы", callback_data="questions")
    )
    builder.row(
        InlineKeyboardButton(text="Написать в поддержку", callback_data="support")
    )

    return builder.as_markup()