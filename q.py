import nest_asyncio
nest_asyncio.apply()

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler,
    ConversationHandler, MessageHandler, filters
)
import asyncio

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Стани для ConversationHandler
(
    LANG, MAIN_MENU,
    CALL_ROLE_MENU,
    MASTER_REPAIR_MENU,
    ADD_PERSON,
    ADD_PERSON_NAME,
    PROJECT_NAME,
    DETAIL_INPUT,
    WAIT_MASTER_CONFIRM
) = range(9)

# Токен бота
TOKEN = "7293478972:AAFvn2bWgxYbvSvAdAe7-jVVk1CpQMcIjco"

# Тексти меню різними мовами
texts = {
    "uk": {
        "welcome": "Виберіть мову / Wybierz język / Выберите язык:",
        "main_menu": "Головне меню:",
        "call_help": "Викликати допомогу",
        "add_person": "Додати людину",
        "done_project": "Виконаний проект (вписати назву)",
        "back": "⬅ Назад",
        "main": "🏠 Головне меню",
        "language_selected": "Обрано українську мову.",
        "choose_role": "Оберіть роль:",
        "call_sent": "Повідомлення надіслано: ",
        "enter_project_name": "Введіть назву проекту:",
        "added_person": "Введіть ім'я людини для додавання:",
        "enter_detail": "Введіть назву деталі та розмір (за бажанням):",
        "master_repair_menu_text": "Оберіть обладнання для ремонту:",
        "master_confirm_text": "Майстер {}: {} хоче ремонтувати '{}'. Натисніть кнопку підтвердження.",
        "master_confirm_button": "Зрозумів - принесіть вибрану річ у майстерню",
        "master_confirmed_user": "Майстер {} підтвердив: принесіть '{}' у майстерню.",
        "role_added": "Додано користувача '{}' з роллю '{}'.",
        "choose_role_add": "Оберіть роль для нової людини:",
        "unknown_command": "Будь ласка, користуйтеся меню.",
    },
    "pl": {
        "welcome": "Wybierz język / Виберіть мову / Выберите язык:",
        "main_menu": "Menu główne:",
        "call_help": "Zawołaj pomoc",
        "add_person": "Dodaj osobę",
        "done_project": "Wykonany projekt (wpisz nazwę)",
        "back": "⬅ Wstecz",
        "main": "🏠 Menu główne",
        "language_selected": "Wybrano język polski.",
        "choose_role": "Wybierz rolę:",
        "call_sent": "Wysłano wiadomość: ",
        "enter_project_name": "Wpisz nazwę projektu:",
        "added_person": "Wpisz imię osoby do dodania:",
        "enter_detail": "Wpisz nazwę części i rozmiar (opcjonalnie):",
        "master_repair_menu_text": "Wybierz sprzęt do naprawy:",
        "master_confirm_text": "Mistrz {}: {} chce naprawiać '{}'. Naciśnij przycisk potwierdzenia.",
        "master_confirm_button": "Zrozumiałem - przynieś wybraną rzecz do warsztatu",
        "master_confirmed_user": "Mistrz {} potwierdził: przynieś '{}' do warsztatu.",
        "role_added": "Dodano użytkownika '{}' z rolą '{}'.",
        "choose_role_add": "Wybierz rolę dla nowej osoby:",
        "unknown_command": "Proszę korzystać z menu.",
    },
    "ru": {
        "welcome": "Выберите язык / Wybierz język / Виберіть мову:",
        "main_menu": "Главное меню:",
        "call_help": "Вызвать помощь",
        "add_person": "Добавить человека",
        "done_project": "Выполненный проект (введите название)",
        "back": "⬅ Назад",
        "main": "🏠 Главное меню",
        "language_selected": "Выбран русский язык.",
        "choose_role": "Выберите роль:",
        "call_sent": "Сообщение отправлено: ",
        "enter_project_name": "Введите название проекта:",
        "added_person": "Введите имя человека для добавления:",
        "enter_detail": "Введите название детали и размер (по желанию):",
        "master_repair_menu_text": "Выберите оборудование для ремонта:",
        "master_confirm_text": "Мастер {}: {} хочет ремонтировать '{}'. Нажмите кнопку подтверждения.",
        "master_confirm_button": "Понял - принесите выбранную вещь в мастерскую",
        "master_confirmed_user": "Мастер {} подтвердил: принесите '{}' в мастерскую.",
        "role_added": "Добавлен пользователь '{}' с ролью '{}'.",
        "choose_role_add": "Выберите роль для нового человека:",
        "unknown_command": "Пожалуйста, используйте меню.",
    }
}

# Ролі та їх ключі
roles = {
    "brigadier": {"name": {"uk": "Бригадир", "pl": "Brygadzista", "ru": "Бригадир"}},
    "repair_master_welding": {"name": {"uk": "Майстер ремонту (зварка)", "pl": "Mistrz napraw (spawanie)", "ru": "Мастер ремонта (сварка)"}},
    "repair_master_grinder": {"name": {"uk": "Майстер ремонту (болгарка)", "pl": "Mistrz napraw (szlifierka)", "ru": "Мастер ремонта (болгарка)"}},
    "repair_master_drill": {"name": {"uk": "Майстер ремонту (дрелька магнітна)", "pl": "Mistrz napraw (wiertarka magnetyczna)", "ru": "Мастер ремонта (дрелька магнитная)"}},
    "repair_master_extender": {"name": {"uk": "Майстер ремонту (подовжувач)", "pl": "Mistrz napraw (przedłużacz)", "ru": "Мастер ремонта (удлинитель)"}},
    "metal_cutter": {"name": {"uk": "Різчик металу", "pl": "Rzeźnik metalu", "ru": "Резчик металла"}},
    "office_worker": {"name": {"uk": "Працівник офісу", "pl": "Pracownik biura", "ru": "Работник офиса"}},
    "designer": {"name": {"uk": "Проектант", "pl": "Projektant", "ru": "Проектант"}},
    "laser_worker": {"name": {"uk": "Працівник лазера", "pl": "Operator lasera", "ru": "Работник лазера"}},
}

# Зберігаємо користувачів по ролях
users_by_role = {key: [] for key in roles.keys()}

# Допоміжна функція для локалізації тексту
def get_text(user_data, key):
    lang = user_data.get("lang", "uk")
    return texts.get(lang, texts["uk"]).get(key, key)

def get_role_name(role_key, lang):
    return roles[role_key]["name"].get(lang, roles[role_key]["name"]["uk"])

# Start - вибір мови
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("Українська 🇺🇦", callback_data="lang_uk"),
            InlineKeyboardButton("Polski 🇵🇱", callback_data="lang_pl"),
            InlineKeyboardButton("Русский 🇷🇺", callback_data="lang_ru"),
        ]
    ]
    await update.message.reply_text(
        texts["uk"]["welcome"],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return LANG

# Обробка вибору мови
async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang_code = query.data.split("_")[1]
    context.user_data["lang"] = lang_code

    await query.edit_message_text(get_text(context.user_data, "language_selected"))
    return await main_menu(update, context)

# Головне меню
async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(get_text(context.user_data, "call_help"), callback_data="call_help")],
        [InlineKeyboardButton(get_text(context.user_data, "add_person"), callback_data="add_person")],
        [InlineKeyboardButton(get_text(context.user_data, "done_project"), callback_data="done_project")],
    ]
    if update.callback_query:
        await update.callback_query.edit_message_text(
            get_text(context.user_data, "main_menu"),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text(
            get_text(context.user_data, "main_menu"),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    return MAIN_MENU

# Меню вибору ролі виклику допомоги
async def call_help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = []
    row = []
    lang = context.user_data.get("lang", "uk")

    # Виключаємо майстрів ремонту, бо окремо будуть
    for i, (key, role) in enumerate(roles.items()):
        if key.startswith("repair_master"):
            continue
        row.append(InlineKeyboardButton(get_role_name(key, lang), callback_data=f"call_{key}"))
        if (i + 1) % 2 == 0:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    buttons.append([InlineKeyboardButton("Майстер ремонту" if lang == "uk" else ("Mistrz napraw" if lang == "pl" else "Мастер ремонта"), callback_data="master_repair")])
    buttons.append([InlineKeyboardButton(get_text(context.user_data, "back"), callback_data="main")])

    await update.callback_query.edit_message_text(
        get_text(context.user_data, "choose_role"),
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return CALL_ROLE_MENU

# Меню майстра ремонту (підменю)
async def master_repair_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang", "uk")
    keyboard = [
        [
            InlineKeyboardButton(get_role_name("repair_master_welding", lang), callback_data="call_repair_master_welding"),
            InlineKeyboardButton(get_role_name("repair_master_grinder", lang), callback_data="call_repair_master_grinder")
        ],
        [
            InlineKeyboardButton(get_role_name("repair_master_drill", lang), callback_data="call_repair_master_drill"),
            InlineKeyboardButton(get_role_name("repair_master_extender", lang), callback_data="call_repair_master_extender")
        ],
        [InlineKeyboardButton(get_text(context.user_data, "back"), callback_data="call_help")],
    ]
    await update.callback_query.edit_message_text(
        get_text(context.user_data, "master_repair_menu_text"),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return MASTER_REPAIR_MENU

# Обробка вибору ролі виклику
async def handle_call_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data  # наприклад call_brigadier, call_repair_master_welding
    user_name = update.effective_user.first_name or "Користувач"
    lang = context.user_data.get("lang", "uk")

    if data == "master_repair":
        return await master_repair_menu(update, context)

    # Якщо роль - майстер ремонту (зварка, болгарка, дрелька, подовжувач)
    if data.startswith("call_repair_master_"):
        # Запитуємо деталі що ремонтувати
        context.user_data["repair_type"] = data.replace("call_", "")
        await query.edit_message_text(get_text(context.user_data, "enter_detail"),
                                      reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(context.user_data, "back"), callback_data="call_help")]]))
        return DETAIL_INPUT

    # Якщо роль - різчик металу - теж вводимо деталі
    if data == "call_metal_cutter":
        await query.edit_message_text(get_text(context.user_data, "enter_detail"),
                                      reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(context.user_data, "back"), callback_data="call_help")]]))
        return DETAIL_INPUT

    # Звичайний виклик ролі - надсилаємо повідомлення всім доданим користувачам з цією роллю
    role_key = data.replace("call_", "")
    if role_key in roles:
        message = f"{user_name} потребує допомоги як {get_role_name(role_key, lang)}."
        # Надіслати повідомлення всім користувачам цієї ролі
        recipients = users_by_role.get(role_key, [])
        if not recipients:
            await query.edit_message_text(get_text(context.user_data, "call_sent") + "(немає користувачів цієї ролі)")
        else:
            for user_id in recipients:
                try:
                    await context.bot.send_message(user_id, message)
                except Exception as e:
                    logger.warning(f"Не вдалося надіслати повідомлення {user_id}: {e}")
            await query.edit_message_text(get_text(context.user_data, "call_sent") + message)
        return await main_menu(update, context)

    if data == "call_help":
        return await call_help_menu(update, context)
    if data == "main":
        return await main_menu(update, context)

    await query.edit_message_text("Невідома роль.")
    return await main_menu(update, context)

# Обробка введення деталей для ремонту
async def detail_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    user_name = update.effective_user.first_name or "Користувач"
    lang = context.user_data.get("lang", "uk")

    repair_type = context.user_data.get("repair_type")
    if not repair_type:
        await update.message.reply_text(get_text(context.user_data, "unknown_command"))
        return await main_menu(update, context)

    # Надіслати майстру ремонту повідомлення з кнопкою підтвердження
    # Шукаємо всіх майстрів ремонту відповідного типу
    masters_role = repair_type
    masters = users_by_role.get(masters_role, [])

    if not masters:
        await update.message.reply_text("Немає майстрів ремонту для цієї ролі.")
        return await main_menu(update, context)

    for master_id in masters:
        try:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(get_text(context.user_data, "master_confirm_button"), callback_data=f"master_confirm:{update.effective_user.id}:{text}")]
            ])
            await context.bot.send_message(
                master_id,
                texts[lang]["master_confirm_text"].format(get_role_name(masters_role, lang), user_name, text),
                reply_markup=keyboard
            )
        except Exception as e:
            logger.warning(f"Не вдалося надіслати майстру {master_id}: {e}")

    await update.message.reply_text(get_text(context.user_data, "call_sent") + f"Запит на ремонт: {text}")
    return await main_menu(update, context)

# Обробка відповіді майстра ремонту
async def master_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "uk")

    data = query.data  # формат master_confirm:<user_id>:<item>
    parts = data.split(":")
    if len(parts) != 3:
        await query.edit_message_text("Невірний формат підтвердження.")
        return

    _, user_id_str, item = parts
    user_id = int(user_id_str)

    master_name = update.effective_user.first_name or "Майстер"
    role_of_master = None
    # Визначити роль майстра (має бути одна з repair_master_*)
    for role_key, users in users_by_role.items():
        if update.effective_user.id in users:
            role_of_master = role_key
            break

    if not role_of_master:
        await query.edit_message_text("Ви не зареєстровані як майстер ремонту.")
        return

    # Надіслати користувачу повідомлення що майстер підтвердив
    try:
        await context.bot.send_message(
            user_id,
            texts[lang]["master_confirmed_user"].format(get_role_name(role_of_master, lang), item)
        )
    except Exception as e:
        logger.warning(f"Не вдалося надіслати користувачу {user_id}: {e}")

    await query.edit_message_text("Підтверджено, користувачу надіслано повідомлення.")
    return

# Додати людину - вибір ролі
async def add_person(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    lang = context.user_data.get("lang", "uk")
    keyboard = []
    row = []
    for i, (key, role) in enumerate(roles.items()):
        row.append(InlineKeyboardButton(get_role_name(key, lang), callback_data=f"addrole_{key}"))
        if (i + 1) % 2 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton(get_text(context.user_data, "back"), callback_data="main")])

    await update.callback_query.edit_message_text(
        get_text(context.user_data, "choose_role_add"),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ADD_PERSON

# Обробка вибору ролі для додавання людини
async def add_person_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    role_key = query.data.replace("addrole_", "")
    context.user_data["adding_role"] = role_key

    await query.edit_message_text(get_text(context.user_data, "added_person"))
    return ADD_PERSON_NAME

# Введення імені людини
async def add_person_name_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()
    role_key = context.user_data.get("adding_role")
    lang = context.user_data.get("lang", "uk")
    user_id = update.effective_user.id

    if not role_key:
        await update.message.reply_text(get_text(context.user_data, "unknown_command"))
        return await main_menu(update, context)

    # Додаємо користувача до ролі (якщо хочеш зберігати інші дані - треба базу)
    if user_id not in users_by_role[role_key]:
        users_by_role[role_key].append(user_id)

    await update.message.reply_text(texts[lang]["role_added"].format(name, get_role_name(role_key, lang)))
    return await main_menu(update, context)

# Обробка виконаного проекту
async def done_project(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    lang = context.user_data.get("lang", "uk")

    await update.callback_query.edit_message_text(get_text(context.user_data, "enter_project_name"))
    return PROJECT_NAME

async def done_project_name_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    project_name = update.message.text.strip()
    lang = context.user_data.get("lang", "uk")
    user_name = update.effective_user.first_name or "Користувач"

    # Логіка збереження чи обробки назви проекту тут...

    await update.message.reply_text(f"{get_text(context.user_data, 'call_sent')} {project_name}")
    return await main_menu(update, context)

# Обробка кнопки назад/головне меню
async def go_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    return await main_menu(update, context)

# Обробка текстових повідомлень поза контекстом
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang", "uk")
    await update.message.reply_text(get_text(context.user_data, "unknown_command"))


async def main():
    application = (
        ApplicationBuilder()
        .token(TOKEN)
        .build()
    )

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANG: [CallbackQueryHandler(choose_language, pattern="^lang_")],
            MAIN_MENU: [
                CallbackQueryHandler(call_help_menu, pattern="^call_help$"),
                CallbackQueryHandler(add_person, pattern="^add_person$"),
                CallbackQueryHandler(done_project, pattern="^done_project$"),
                CallbackQueryHandler(main_menu, pattern="^main$"),
            ],
            CALL_ROLE_MENU: [
                CallbackQueryHandler(handle_call_role, pattern="^call_"),
                CallbackQueryHandler(master_repair_menu, pattern="^master_repair$"),
                CallbackQueryHandler(main_menu, pattern="^main$"),
                CallbackQueryHandler(call_help_menu, pattern="^call_help$"),
            ],
            MASTER_REPAIR_MENU: [
                CallbackQueryHandler(handle_call_role, pattern="^call_repair_master_"),
                CallbackQueryHandler(call_help_menu, pattern="^call_help$"),
                CallbackQueryHandler(call_help_menu, pattern="^call_help$"),
                CallbackQueryHandler(call_help_menu, pattern="^call_help$"),
                CallbackQueryHandler(call_help_menu, pattern="^call_help$"),
                CallbackQueryHandler(call_help_menu, pattern="^call_help$"),
                CallbackQueryHandler(call_help_menu, pattern="^call_help$"),
                CallbackQueryHandler(call_help_menu, pattern="^call_help$"),
                CallbackQueryHandler(main_menu, pattern="^main$"),
            ],
            DETAIL_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, detail_input),
                           CallbackQueryHandler(call_help_menu, pattern="^call_help$"),
                           CallbackQueryHandler(main_menu, pattern="^main$")],
            ADD_PERSON: [CallbackQueryHandler(add_person_role, pattern="^addrole_"),
                         CallbackQueryHandler(main_menu, pattern="^main$")],
            ADD_PERSON_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_person_name_received)],
            PROJECT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, done_project_name_received)],
        },
        fallbacks=[CommandHandler("start", start)],
        per_message=False,
    )

    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(master_confirm, pattern="^master_confirm:"))

    print("Бот запущено!")
    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
