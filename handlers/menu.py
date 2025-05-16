# handlers/menu.py

from aiogram import Router, F
from aiogram.types import CallbackQuery
from keyboards.inline import (
    get_back_to_main_keyboard,
    get_partner_keyboard,
    get_partner_referral_keyboard,
    get_partner_community_keyboard,
    get_feedback_keyboard,
    get_feedback_no_keyboard
)
from config import TEXTS

router = Router()


@router.callback_query(F.data == "partner")
async def show_partner(callback: CallbackQuery):
    """Показать информацию о партнерстве"""
    await callback.message.edit_text(
        text=TEXTS["partner"],
        reply_markup=get_partner_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "partner_referral")
async def show_partner_referral(callback: CallbackQuery):
    """Показать информацию о партнерской программе"""
    await callback.message.edit_text(
        text=TEXTS["partner_referral"],
        reply_markup=get_partner_referral_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "partner_community")
async def show_partner_community(callback: CallbackQuery):
    """Показать информацию о монетизации сообщества"""
    await callback.message.edit_text(
        text=TEXTS["partner_community"],
        reply_markup=get_partner_community_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "share_referral")
async def share_referral(callback: CallbackQuery):
    """Поделиться реферальной ссылкой"""
    # Здесь будет логика проверки объема покупок и генерации ссылки
    await callback.answer("Функция будет доступна при объеме покупок от 1000₽")


@router.callback_query(F.data.startswith("feedback_"))
async def handle_feedback(callback: CallbackQuery):
    """Обработка обратной связи"""
    feedback_type = callback.data.replace("feedback_", "")
    
    if feedback_type == "yes":
        await callback.message.edit_text(
            text=TEXTS["feedback_yes"],
            reply_markup=get_back_to_main_keyboard()
        )
    else:
        await callback.message.edit_text(
            text=TEXTS["feedback_no"],
            reply_markup=get_feedback_no_keyboard()
        )
    
    await callback.answer()


@router.callback_query(F.data == "support")
async def show_support(callback: CallbackQuery):
    """Показать контакты поддержки"""
    # Здесь будет логика отображения контактов поддержки
    await callback.answer("Функция поддержки в разработке")