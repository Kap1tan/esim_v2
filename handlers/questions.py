# handlers/questions.py

from aiogram import Router, F
from aiogram.types import CallbackQuery
from keyboards.inline import get_questions_keyboard, get_qa_back_keyboard, get_feedback_keyboard
from config import TEXTS, QA_ITEMS

router = Router()


@router.callback_query(F.data == "questions")
async def show_questions(callback: CallbackQuery):
    """Показать меню вопросов и ответов"""
    await callback.message.edit_text(
        text=TEXTS["questions"],
        reply_markup=get_questions_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("qa_"))
async def show_answer(callback: CallbackQuery):
    """Показать ответ на выбранный вопрос"""
    qa_key = callback.data.replace("qa_", "")

    if qa_key in QA_ITEMS:
        qa_item = QA_ITEMS[qa_key]
        await callback.message.edit_text(
            text=f"❓ {qa_item['text']}\n\n{qa_item['answer']}\n\n{TEXTS['feedback_question']}",
            reply_markup=get_feedback_keyboard()
        )

    await callback.answer()