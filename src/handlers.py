import re
import os
import asyncio
from aiogram import Bot, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile, ReplyKeyboardRemove
from aiogram.exceptions import TelegramBadRequest

from . import lexicon
from .states import UserSteps
from .keyboards import get_retry_kb, start_kb, get_actions_kb, get_hypothesis_kb, get_analysis_kb
from .gemini_client import get_socionics_analysis
from .file_utils import save_to_pdf, split_text

router = Router()

# --- Хэндлеры команд ---

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        lexicon.WELCOME,
        reply_markup=start_kb,
        parse_mode="HTML",
        disable_web_page_preview=True
    )
    await state.set_state(UserSteps.WAITING_FOR_FILE)

@router.message(F.text.lower().in_({"🔄 начать заново", "перезапустить"}))
@router.callback_query(F.data == "restart")
async def cmd_restart(update: Message | CallbackQuery, state: FSMContext):
    message = update.message if isinstance(update, CallbackQuery) else update
    await state.clear()
    if isinstance(update, CallbackQuery):
        # Если это нажатие кнопки, удаляем старое сообщение
        try:
            await update.message.delete()
        except TelegramBadRequest:
            pass # Если сообщение уже удалено, ничего страшного
    await message.answer(lexicon.RESTART_MESSAGE, reply_markup=start_kb)
    await message.answer(
        lexicon.WELCOME,
        parse_mode="HTML",
        disable_web_page_preview=True
    )
    await state.set_state(UserSteps.WAITING_FOR_FILE)
    if isinstance(update, CallbackQuery):
        await update.answer()

# --- Основной сценарий ---

@router.message(UserSteps.WAITING_FOR_FILE, F.text == "📥 Загрузить переписку")
async def ask_for_file(message: Message):
    await message.answer(
        lexicon.ASK_FILE_TEXT,
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="HTML",
        disable_web_page_preview=True
    )

@router.message(UserSteps.WAITING_FOR_FILE, F.document)
async def handle_file(message: Message, state: FSMContext):
    if not message.document.file_name.endswith(".txt"):
        await message.answer(lexicon.WRONG_FILE_FORMAT, parse_mode="HTML")
        return
    
    await state.update_data(file_id=message.document.file_id)
    await state.set_state(UserSteps.WAITING_FOR_NAME)
    await message.answer(lexicon.FILE_RECEIVED, parse_mode="HTML")

@router.callback_query(F.data == "extract_another")
async def ask_for_another_name(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(UserSteps.WAITING_FOR_NAME)
    try:
        await call.message.delete()
    except TelegramBadRequest:
        pass
    await call.message.answer(lexicon.WAITING_FOR_NAME, parse_mode="HTML")

@router.message(UserSteps.WAITING_FOR_NAME, F.text)
async def extract_messages(message: Message, state: FSMContext, bot: Bot):
    user_name = message.text.strip()
    await message.answer(f"Ищу сообщения от '{user_name}'... Это может занять до минуты для больших чатов. ⏳")
    
    data = await state.get_data()
    file_id = data.get("file_id")

    if not file_id:
        await message.answer(lexicon.FILE_DOWNLOAD_ERROR, reply_markup=start_kb)
        await state.set_state(UserSteps.WAITING_FOR_FILE)
        return
        
    try:
        file_info = await bot.get_file(file_id)
        downloaded_stream = await bot.download_file(file_info.file_path)
        file_in_bytes = downloaded_stream.read()
        text = file_in_bytes.decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"!!! ОШИБКА ПРИ ОБРАБОТКЕ ФАЙЛА: {type(e)} - {e.args} !!!")
        await message.answer(lexicon.RETRY_PROMPT, reply_markup=get_retry_kb('extract_messages'))
        return

    pattern = re.compile(
        rf"^{re.escape(user_name)} \(([^)]+)\):\s*\n*((?!\[id\d+\|).+)", re.MULTILINE
    )
    
    seen_messages = set()
    unique_messages_list = []
    for match in pattern.finditer(text):
        msg = match.group(2).strip()
        if msg and msg not in seen_messages:
            seen_messages.add(msg)
            unique_messages_list.append(msg)
    
    if not unique_messages_list:
        await message.answer(lexicon.MESSAGES_NOT_FOUND.format(user_name=user_name), parse_mode="HTML")
        return

    full_text = "\n".join(unique_messages_list)
    await state.update_data(extracted_text=full_text, current_user=user_name)
    await state.set_state(UserSteps.MESSAGES_EXTRACTED)

    await message.answer(
        f"✅ Найдено уникальных сообщений: {len(unique_messages_list)}.\n"
        f"Общий объем текста: {len(full_text)} символов.",
        reply_markup=get_actions_kb(user_name)
    )

@router.callback_query(UserSteps.MESSAGES_EXTRACTED, F.data == "start_typing")
async def ask_about_hypothesis(call: CallbackQuery, state: FSMContext):
    await call.answer()
    try:
        await call.message.delete()
    except TelegramBadRequest:
        pass
    await call.message.answer(
        lexicon.ASK_HYPOTHESIS,
        reply_markup=get_hypothesis_kb()
    )
    await state.set_state(UserSteps.WAITING_FOR_HYPOTHESIS)

@router.callback_query(UserSteps.WAITING_FOR_HYPOTHESIS, F.data == "hypo_yes")
async def wait_for_hypothesis(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.edit_text(lexicon.WAIT_FOR_HYPOTHESIS_INPUT)
    
@router.callback_query(UserSteps.WAITING_FOR_HYPOTHESIS, F.data == "hypo_no")
async def process_typing_no_hypo(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.edit_text(lexicon.START_ANALYSIS_NO_HYPO)
    data = await state.get_data()
    await run_analysis(call.message, state, data['extracted_text'], None)
    
@router.message(UserSteps.WAITING_FOR_HYPOTHESIS, F.text)
async def process_typing_with_hypo(message: Message, state: FSMContext):
    hypothesis = message.text
    await message.answer(f"Принято! Анализирую с учетом версий: <b>{hypothesis}</b>... 🧠 Это может занять несколько минут.", parse_mode="HTML")
    data = await state.get_data()
    await run_analysis(message, state, data['extracted_text'], hypothesis)

async def run_analysis(message: Message, state: FSMContext, text: str, hypothesis: str | None):
    try:
        analysis_result = await get_socionics_analysis(text, hypothesis)
        await state.update_data(analysis_result=analysis_result)
        await state.set_state(UserSteps.ANALYSIS_DONE)
        
        html_result = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', analysis_result)
        preview = html_result[:1000] + "..." if len(html_result) > 1000 else html_result
        
        await message.answer(
            f"{lexicon.ANALYSIS_PREVIEW_HEADER}{preview}",
            reply_markup=get_analysis_kb(),
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"!!! ОШИБКА ПРИ ВЗАИМОДЕЙСТВИИ С GEMINI: {e} !!!")
        await message.answer(
            "Не удалось получить ответ от нейросети. Возможно, временные неполадки. Попробуйте еще раз.",
            reply_markup=get_retry_kb('run_analysis')
        )

# --- Хэндлеры для работы с результатом ---

@router.callback_query(UserSteps.ANALYSIS_DONE, F.data == "show_full_analysis")
async def show_full_text(call: CallbackQuery, state: FSMContext):
    await call.answer()
    data = await state.get_data()
    full_text = data.get("analysis_result", "Не удалось найти текст анализа.")
    
    html_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', full_text)

    chunks = split_text(html_text)
    for i, chunk in enumerate(chunks):
        try:
            await call.message.answer(chunk, parse_mode="HTML")
        except TelegramBadRequest: 
            await call.message.answer(chunk)
        if i < len(chunks) - 1:
            await asyncio.sleep(0.5)

    await call.message.answer(lexicon.ANALYSIS_ACTION_PROMPT, reply_markup=get_analysis_kb())

@router.callback_query(UserSteps.ANALYSIS_DONE, F.data == "download_pdf")
async def send_pdf(call: CallbackQuery, state: FSMContext):
    await call.answer(lexicon.PDF_PREPARING)
    data = await state.get_data()
    analysis_text = data.get("analysis_result", "Нет текста для сохранения.")
    user_name = data.get("current_user", "analysis")
    
    try:
        pdf_path = save_to_pdf(analysis_text, user_name)
        await call.message.answer_document(FSInputFile(pdf_path), caption=lexicon.PDF_CAPTION)
        os.remove(pdf_path)
    except Exception as e:
        print(f"!!! ОШИБКА ПРИ СОЗДАНИИ PDF: {e} !!!")
        await call.message.answer(lexicon.PDF_ERROR, reply_markup=get_retry_kb('download_pdf'))

# --- Хэндлеры ошибок и служебные ---

@router.callback_query(F.data.startswith("retry:"))
async def retry_action_handler(call: CallbackQuery, state: FSMContext, bot: Bot):
    await call.answer()
    action = call.data.split(":")[1]
    
    try:
        await call.message.delete()
    except TelegramBadRequest:
        pass
    
    if action == 'extract_messages':
        await call.message.answer(lexicon.WAITING_FOR_NAME, parse_mode="HTML")
        await state.set_state(UserSteps.WAITING_FOR_NAME)
        
    elif action == 'download_pdf':
        await send_pdf(call, state)

    elif action == 'run_analysis':
        data = await state.get_data()
        await call.message.answer("Повторный запуск анализа...")
        await run_analysis(call.message, state, data.get('extracted_text'), data.get('hypothesis'))
        
@router.message()
async def fallback(message: Message, state: FSMContext):
    current_state = await state.get_state()
    
    if current_state == UserSteps.MESSAGES_EXTRACTED:
        data = await state.get_data()
        user_name = data.get("current_user", "текущего пользователя")
        await message.answer(lexicon.FALLBACK_ACTIONS, reply_markup=get_actions_kb(user_name))
    elif current_state == UserSteps.ANALYSIS_DONE:
        await message.answer(lexicon.FALLBACK_ANALYSIS, reply_markup=get_analysis_kb())
    else:
        await message.answer(lexicon.FALLBACK_UNKNOWN, reply_markup=start_kb)