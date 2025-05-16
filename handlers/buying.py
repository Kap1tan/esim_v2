# handlers/buying.py

from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile, InputMediaPhoto, Message
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from keyboards.inline import (
    get_buy_esim_keyboard,
    get_countries_keyboard,
    get_packages_keyboard,
    get_confirm_keyboard,
    get_payment_done_keyboard,
    get_back_to_countries_keyboard,
    get_back_to_main_keyboard
)
from config import TEXTS, REGIONS, COUNTRY_CODES
from utils.esim_client import ESIMAccessClient
from config import ESIM_ACCESS_CODE
import asyncio
from handlers.profile import save_order

router = Router()

# Создаем экземпляр клиента eSIM Access
esim_client = ESIMAccessClient(ESIM_ACCESS_CODE)


# Определяем состояния FSM для процесса покупки
class BuyingStates(StatesGroup):
    selecting_country = State()
    selecting_package = State()
    confirming_purchase = State()
    payment_processing = State()


@router.callback_query(F.data == "buy_esim")
async def buy_esim(callback: CallbackQuery, state: FSMContext):
    """Обработчик для покупки eSIM - выбор региона"""
    # Очищаем данные состояния
    await state.clear()

    # Отправляем меню выбора региона без картинки
    await callback.message.edit_text(
        text=TEXTS["buy_esim"],
        reply_markup=get_buy_esim_keyboard()
    )

    await callback.answer()


@router.callback_query(F.data.startswith("region_"))
async def select_region(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора региона"""
    region_key = callback.data.split("_")[1]

    if region_key in REGIONS:
        region_data = REGIONS[region_key]
        try:
            photo = FSInputFile(region_data["image"])
            # Пробуем отредактировать сообщение
            await callback.message.edit_media(
                media=InputMediaPhoto(
                    media=photo,
                    caption=TEXTS["select_country"]
                ),
                reply_markup=get_countries_keyboard(region_key, region_data["countries"])
            )
        except Exception as e:
            # Если не удается отредактировать, отправляем новое сообщение
            await callback.message.delete()
            try:
                photo = FSInputFile(region_data["image"])
                await callback.message.answer_photo(
                    photo=photo,
                    caption=TEXTS["select_country"],
                    reply_markup=get_countries_keyboard(region_key, region_data["countries"])
                )
            except:
                # Если нет картинки, отправляем текст
                await callback.message.answer(
                    text=TEXTS["select_country"],
                    reply_markup=get_countries_keyboard(region_key, region_data["countries"])
                )

    await callback.answer()
    await state.set_state(BuyingStates.selecting_country)


@router.callback_query(BuyingStates.selecting_country, F.data.startswith("country_"))
async def select_country(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора страны"""
    country_name = callback.data.replace("country_", "")

    # Проверяем, есть ли код страны
    if country_name in COUNTRY_CODES:
        country_code = COUNTRY_CODES[country_name]

        # Сохраняем информацию о стране
        await state.update_data(
            country_name=country_name,
            country_code=country_code
        )

        # Отправляем сообщение о загрузке
        loading_text = TEXTS["loading_packages"].format(country_name=country_name)

        if callback.message.photo:
            # Удаляем сообщение с фото и отправляем текст
            await callback.message.delete()
            message = await callback.message.answer(text=loading_text)
        else:
            # Редактируем текущее сообщение
            message = await callback.message.edit_text(text=loading_text)

        # Получаем пакеты для выбранной страны
        packages = esim_client.get_packages_by_country(country_code)

        # Сохраняем пакеты в состоянии
        await state.update_data(packages=packages)

        if not packages:
            # Если пакеты не найдены
            no_packages_text = TEXTS["no_packages"].format(country_name=country_name)
            await message.edit_text(
                text=no_packages_text,
                reply_markup=get_back_to_countries_keyboard(callback.data.split("_")[0])
            )
            await callback.answer()
            return

        # Отображаем тарифы
        packages_text = TEXTS["choose_package"].format(country_name=country_name)
        await message.edit_text(
            text=packages_text,
            reply_markup=get_packages_keyboard(packages, country_code)
        )
        await state.set_state(BuyingStates.selecting_package)
    else:
        # Если код страны не найден
        if callback.message.photo:
            await callback.message.delete()
            await callback.message.answer(
                text=TEXTS["nothing_found"],
                reply_markup=get_buy_esim_keyboard()
            )
        else:
            await callback.message.edit_text(
                text=TEXTS["nothing_found"],
                reply_markup=get_buy_esim_keyboard()
            )

    await callback.answer()


@router.callback_query(BuyingStates.selecting_package, F.data.startswith("package_"))
async def select_package(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора тарифа"""
    # Получаем индекс выбранного пакета
    package_index = int(callback.data.split("_")[1])

    # Получаем данные из состояния
    data = await state.get_data()
    packages = data.get("packages", [])
    country_name = data.get("country_name", "")
    country_code = data.get("country_code", "")

    if not packages or package_index >= len(packages):
        # Если пакет не найден
        await callback.message.edit_text(
            text="Ошибка: выбранный тариф не найден. Попробуйте снова.",
            reply_markup=get_back_to_countries_keyboard(f"region_{country_code}")
        )
        await callback.answer()
        return

    # Получаем выбранный пакет
    package = packages[package_index]

    # Сохраняем выбранный пакет
    await state.update_data(selected_package=package)

    # Форматируем детали пакета
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

    # Формируем текст подтверждения
    confirmation_text = TEXTS["confirm_purchase"].format(
        country=country_name,
        package_name=package_name,
        volume=volume_str,
        duration=duration_str,
        price=price
    )

    # Отправляем подтверждение
    await callback.message.edit_text(
        text=confirmation_text,
        reply_markup=get_confirm_keyboard(country_code)
    )

    await state.set_state(BuyingStates.confirming_purchase)
    await callback.answer()


@router.callback_query(BuyingStates.confirming_purchase, F.data == "confirm_purchase")
async def process_payment(callback: CallbackQuery, state: FSMContext):
    """Обработчик подтверждения покупки и оплаты"""
    # Отправляем сообщение о обработке платежа
    await callback.message.edit_text(text=TEXTS["processing_payment"])
    await callback.answer()

    # Получаем данные из состояния
    data = await state.get_data()
    package = data.get("selected_package", {})

    if not package:
        await callback.message.edit_text(
            text="Ошибка: информация о выбранном тарифе не найдена. Попробуйте снова.",
            reply_markup=get_back_to_main_keyboard()
        )
        return

    # Заказываем eSIM
    package_code = package.get("packageCode", "")
    price = package.get("price", 0)

    order_no = esim_client.order_profile(
        package_code=package_code,
        price=price,
        count=1
    )

    if not order_no:
        # Если заказ не удался
        await callback.message.edit_text(
            text=TEXTS["payment_error"],
            reply_markup=get_back_to_main_keyboard()
        )
        return

    # Сохраняем номер заказа
    await state.update_data(order_no=order_no)

    # Сохраняем информацию о заказе в профиле пользователя
    user_id = callback.from_user.id
    country_name = data.get("country_name", "")
    package_name = package.get("name", "")
    save_order(user_id, order_no, country_name, package_name)

    # Отправляем сообщение об успешной оплате
    await callback.message.edit_text(
        text=TEXTS["payment_success"],
        reply_markup=get_payment_done_keyboard()
    )

    await state.set_state(BuyingStates.payment_processing)


@router.callback_query(BuyingStates.payment_processing, F.data == "show_esim_details")
async def show_esim_details(callback: CallbackQuery, state: FSMContext):
    """Показать детали купленной eSIM"""
    await callback.answer()

    # Отправляем сообщение о получении данных
    await callback.message.edit_text(text=TEXTS["getting_esim_details"])

    # Получаем номер заказа
    data = await state.get_data()
    order_no = data.get("order_no", "")

    if not order_no:
        await callback.message.edit_text(
            text="Ошибка: информация о заказе не найдена.",
            reply_markup=get_back_to_main_keyboard()
        )
        await state.clear()
        return

    # Ждем, пока eSIM будет готова (может занять некоторое время)
    profiles = []
    for _ in range(5):  # Максимум 5 попыток
        profiles = esim_client.query_order(order_no)
        if profiles:
            break
        await asyncio.sleep(2)  # Ждем 2 секунды между попытками

    if not profiles:
        await callback.message.edit_text(
            text=TEXTS["esim_not_ready"],
            reply_markup=get_back_to_main_keyboard()
        )
        await state.clear()
        return

    # Берем первый профиль из заказа
    profile = profiles[0]

    # Формируем информацию о профиле
    ac = profile.get("ac", "")  # Activation Code
    qr_code_url = profile.get("qrCodeUrl", "")
    iccid = profile.get("iccid", "")

    esim_details = TEXTS["esim_details"].format(
        iccid=iccid,
        ac=ac,
        qr_code_url=qr_code_url
    )

    # Отправляем детали eSIM
    await callback.message.edit_text(
        text=esim_details,
        reply_markup=get_back_to_main_keyboard(),
        disable_web_page_preview=False  # Показываем QR-код, если URL указывает на изображение
    )

    # Очищаем состояние
    await state.clear()


@router.callback_query(F.data == "cancel_purchase")
async def cancel_purchase(callback: CallbackQuery, state: FSMContext):
    """Отмена покупки"""
    await callback.message.edit_text(
        text=TEXTS["operation_cancelled"],
        reply_markup=get_back_to_main_keyboard()
    )
    await state.clear()
    await callback.answer()


# Обработчик вввода страны текстом
@router.message(BuyingStates.selecting_country)
async def process_country_text(message: Message, state: FSMContext):
    """Обработка ввода названия страны текстом"""
    country_name = message.text.strip().capitalize()

    # Проверяем, есть ли код страны
    if country_name in COUNTRY_CODES:
        country_code = COUNTRY_CODES[country_name]

        # Сохраняем информацию о стране
        await state.update_data(
            country_name=country_name,
            country_code=country_code
        )

        # Отправляем сообщение о загрузке
        loading_message = await message.answer(
            text=TEXTS["loading_packages"].format(country_name=country_name)
        )

        # Получаем пакеты для выбранной страны
        packages = esim_client.get_packages_by_country(country_code)

        # Сохраняем пакеты в состоянии
        await state.update_data(packages=packages)

        if not packages:
            # Если пакеты не найдены
            no_packages_text = TEXTS["no_packages"].format(country_name=country_name)
            await loading_message.edit_text(
                text=no_packages_text,
                reply_markup=get_buy_esim_keyboard()
            )
            return

        # Отображаем тарифы
        packages_text = TEXTS["choose_package"].format(country_name=country_name)
        await loading_message.edit_text(
            text=packages_text,
            reply_markup=get_packages_keyboard(packages, country_code)
        )
        await state.set_state(BuyingStates.selecting_package)
    else:
        # Если код страны не найден
        await message.answer(
            text=TEXTS["nothing_found"],
            reply_markup=get_buy_esim_keyboard()
        )