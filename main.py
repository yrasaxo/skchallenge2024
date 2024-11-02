import logging
import numpy as np
import random
from aiogram import types
from aiogram.dispatcher.filters import Text
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardRemove

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Константы
c = 3e8  # скорость света, м/с
h = 6.626e-34  # постоянная Планка, Дж·с

# Токен бота
API_TOKEN = '7941068225:AAF1-ThSI8WLsRD-BjvIxkPM-2XJyBcUzHk'  # замените на свой токен

# Создание бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

# Определение клавиатур
main_menu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
main_menu.add(KeyboardButton("✨ Флюенс"), KeyboardButton("🔄 Конверт"))
main_menu.add(KeyboardButton("💥 Кинетическая Энергия"), KeyboardButton("🧲 Потенциальная Энергия"))
main_menu.add(KeyboardButton("📐 Плотность"), KeyboardButton("🚀 Импульс"))
main_menu.add(KeyboardButton("📕1 Факт о физике"))
main_menu.add(KeyboardButton("ℹ️ Help"))

help_menu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
help_menu.add(KeyboardButton("✨ Флюенс"), KeyboardButton("🔄 Конверт"))
help_menu.add(KeyboardButton("💥 Кинетическая Энергия"), KeyboardButton("🧲 Потенциальная Энергия"))
help_menu.add(KeyboardButton("📐 Плотность"), KeyboardButton("🚀 Импульс"))
help_menu.add(KeyboardButton("📕1 Факт о физике"))

# Классы для состояний
class FluenceStates(StatesGroup):
    power = State()       # ожидание ввода мощности
    diameter = State()    # ожидание ввода диаметра

class ConvertStates(StatesGroup):
    convert_choice = State()   # выбор типа конвертации
    value_input = State()      # ввод значения

class EnergyStates(StatesGroup):
    mass = State()            # ожидание массы для энергии
    velocity = State()        # ожидание скорости для кинетической энергии
    height = State()          # ожидание высоты для потенциальной энергии

class DensityState(StatesGroup):
    mass = State()            # ожидание массы для плотности
    volume = State()          # ожидание объема для плотности

class ImpulseState(StatesGroup):
    mass = State()            # ожидание массы для импульса
    velocity = State()        # ожидание скорости для импульса

# Приветственное сообщение
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply(
        "Привет!\n"
        "🧐Я PhysiCalcBot. Могу помочь тебе с расчетами по физике\n"
        "🤩Меня создал Ярослав Пановский для SK Chalenge 2024\n"
        "😎Смотри что я могу:\n"
        "✨ Конвертировать длину волны, частоту и энергию фотона.\n"
        "✨ Анализировать спектры и вычислять положение пика и ширину на полувысоте.\n"
        "✨ Вычислять флюенс лазерной системы.\n"
        "✨ Вычислять кинетическую и потенциальную энергию, плотность и импульс.\n\n"
        "Нажмите 'ℹ️ Help' для подсказки.", reply_markup=main_menu
    )

# Обработка кнопки Help
@dp.message_handler(lambda message: message.text.lower() == "ℹ️ help")
async def show_help(message: types.Message):
    await message.reply(
        "Вот команды, которые я поддерживаю:\n"
"✨ Флюенс - Параметр, показывающий плотность энергии лазерного излучения на единицу площади. Помогает вычислить флюенс лазерной системы, исходя из мощности и площади облучения.\n"
"🔄 Конверт - Функция для перевода физических величин: длина волны, частота или энергия фотона, что позволяет преобразовать одни значения в другие.\n"
"💥 Кинетическая Энергия - Расчет кинетической энергии, которая показывает, сколько энергии имеет объект благодаря своему движению (масса и скорость).\n"
"🧲 Потенциальная Энергия - Вычисление потенциальной энергии, указывающей, сколько энергии запасено в теле, находящемся в гравитационном поле.\n"
"📐 Плотность - Определение плотности вещества через массу и объем — параметр, показывающий, насколько вещество «плотное».\n"
"🚀 Импульс - Расчет импульса, характеризующего движение тела с определенной массой и скоростью, то есть «количество движения».\n"
, reply_markup=help_menu
    )

# Функции для расчёта физических величин
def calculate_kinetic_energy(mass, velocity):
    return 0.5 * mass * velocity**2

def calculate_potential_energy(mass, height, g=9.81):
    return mass * g * height

def calculate_density(mass, volume):
    return mass / volume

def calculate_impulse(mass, velocity):
    return mass * velocity

# Обработка кнопки Флюенс
@dp.message_handler(lambda message: message.text.lower() == "✨ флюенс")
async def fluence_start(message: types.Message):
    await message.reply("Введите мощность в Ваттах:", reply_markup=ReplyKeyboardRemove())
    await FluenceStates.power.set()

@dp.message_handler(state=FluenceStates.power)
async def process_fluence_power(message: types.Message, state: FSMContext):
    try:
        power = float(message.text)
        await state.update_data(power=power)
        await message.reply("Введите диаметр в метрах:")
        await FluenceStates.diameter.set()
    except ValueError:
        await message.reply("Пожалуйста, введите числовое значение.")

@dp.message_handler(state=FluenceStates.diameter)
async def process_fluence_diameter(message: types.Message, state: FSMContext):
    try:
        diameter = float(message.text)
        data = await state.get_data()
        power = data['power']

        fluence = power / (np.pi * (diameter / 2) ** 2)

        await message.reply(f"Флюенс: {fluence:.2f} Дж/м²", reply_markup=main_menu)
        await state.finish()
    except ValueError:
        await message.reply("Пожалуйста, введите числовое значение.")

# Обработка кнопки Конверт
@dp.message_handler(lambda message: message.text.lower() == "🔄 конверт")
async def convert_start(message: types.Message):
    await message.reply("Выберите, что вы хотите конвертировать:\n1 - Длину волны\n2 - Частоту\n3 - Энергию фотона", reply_markup=ReplyKeyboardRemove())
    await ConvertStates.convert_choice.set()

@dp.message_handler(state=ConvertStates.convert_choice)
async def process_convert_choice(message: types.Message, state: FSMContext):
    choice = message.text
    if choice in ['1', '2', '3']:
        await state.update_data(choice=choice)
        await message.reply("Введите значение для конвертации:")
        await ConvertStates.value_input.set()
    else:
        await message.reply("Пожалуйста, выберите корректный вариант: 1, 2 или 3.")

@dp.message_handler(state=ConvertStates.value_input)
async def process_convert_value(message: types.Message, state: FSMContext):
    data = await state.get_data()
    choice = data.get('choice')
    try:
        value = float(message.text)

        if choice == '1':  # Длина волны
            frequency = c / value
            await message.reply(f"Частота: {frequency:.2e} Гц", reply_markup=main_menu)
        elif choice == '2':  # Частота
            energy = h * value
            await message.reply(f"Энергия фотона: {energy:.2e} Дж", reply_markup=main_menu)
        elif choice == '3':  # Энергия фотона
            frequency = value / h
            await message.reply(f"Частота: {frequency:.2e} Гц", reply_markup=main_menu)

        await state.finish()
    except ValueError:
        await message.reply("Пожалуйста, введите числовое значение.")

# Обработка кнопки Кинетическая Энергия
@dp.message_handler(lambda message: message.text.lower() == "💥 кинетическая энергия")
async def kinetic_energy_start(message: types.Message):
    await message.reply("Введите массу (кг):", reply_markup=ReplyKeyboardRemove())
    await EnergyStates.mass.set()

@dp.message_handler(state=EnergyStates.mass)
async def process_kinetic_energy_mass(message: types.Message, state: FSMContext):
    try:
        mass = float(message.text)
        await state.update_data(mass=mass)
        await message.reply("Введите скорость (м/с):")
        await EnergyStates.velocity.set()
    except ValueError:
        await message.reply("Пожалуйста, введите числовое значение.")

@dp.message_handler(state=EnergyStates.velocity)
async def process_kinetic_energy_velocity(message: types.Message, state: FSMContext):
    try:
        velocity = float(message.text)
        data = await state.get_data()
        mass = data['mass']

        energy = calculate_kinetic_energy(mass, velocity)

        await message.reply(f"Кинетическая энергия: {energy:.2f} Дж", reply_markup=main_menu)
        await state.finish()
    except ValueError:
        await message.reply("Пожалуйста, введите числовое значение.")

# Обработка кнопки Потенциальная Энергия
@dp.message_handler(lambda message: message.text.lower() == "🧲 потенциальная энергия")
async def potential_energy_start(message: types.Message):
    await message.reply("Введите массу (кг):", reply_markup=ReplyKeyboardRemove())
    await EnergyStates.mass.set()

@dp.message_handler(state=EnergyStates.mass)
async def process_potential_energy_mass(message: types.Message, state: FSMContext):
    try:
        mass = float(message.text)
        await state.update_data(mass=mass)
        await message.reply("Введите высоту (м):")
        await EnergyStates.height.set()
    except ValueError:
        await message.reply("Пожалуйста, введите числовое значение.")

@dp.message_handler(state=EnergyStates.height)
async def process_potential_energy_height(message: types.Message, state: FSMContext):
    try:
        height = float(message.text)
        data = await state.get_data()
        mass = data['mass']

        energy = calculate_potential_energy(mass, height)

        await message.reply(f"Потенциальная энергия: {energy:.2f} Дж", reply_markup=main_menu)
        await state.finish()
    except ValueError:
        await message.reply("Пожалуйста, введите числовое значение.")

# Обработка кнопки Плотность
@dp.message_handler(lambda message: message.text.lower() == "📐 плотность")
async def density_start(message: types.Message):
    await message.reply("Введите массу (кг):", reply_markup=ReplyKeyboardRemove())
    await DensityState.mass.set()

@dp.message_handler(state=DensityState.mass)
async def process_density_mass(message: types.Message, state: FSMContext):
    try:
        mass = float(message.text)
        await state.update_data(mass=mass)
        await message.reply("Введите объем (м³):")
        await DensityState.volume.set()
    except ValueError:
        await message.reply("Пожалуйста, введите числовое значение.")

@dp.message_handler(state=DensityState.volume)
async def process_density_volume(message: types.Message, state: FSMContext):
    try:
        volume = float(message.text)
        data = await state.get_data()
        mass = data['mass']

        density = calculate_density(mass, volume)

        await message.reply(f"Плотность: {density:.2f} кг/м³", reply_markup=main_menu)
        await state.finish()
    except ValueError:
        await message.reply("Пожалуйста, введите числовое значение.")

# Обработка кнопки Импульс
@dp.message_handler(lambda message: message.text.lower() == "🚀 импульс")
async def impulse_start(message: types.Message):
    await message.reply("Введите массу (кг):", reply_markup=ReplyKeyboardRemove())
    await ImpulseState.mass.set()

@dp.message_handler(state=ImpulseState.mass)
async def process_impulse_mass(message: types.Message, state: FSMContext):
    try:
        mass = float(message.text)
        await state.update_data(mass=mass)
        await message.reply("Введите скорость (м/с):")
        await ImpulseState.velocity.set()
    except ValueError:
        await message.reply("Пожалуйста, введите числовое значение.")

@dp.message_handler(state=ImpulseState.velocity)
async def process_impulse_velocity(message: types.Message, state: FSMContext):
    try:
        velocity = float(message.text)
        data = await state.get_data()
        mass = data['mass']

        impulse = calculate_impulse(mass, velocity)

        await message.reply(f"Импульс: {impulse:.2f} кг·м/с", reply_markup=main_menu)
        await state.finish()
    except ValueError:
        await message.reply("Пожалуйста, введите числовое значение.")


# Функция для получения случайного факта без номера
def get_random_fact():
    with open('facts.doc', 'r', encoding='utf-8') as file:
        facts = file.readlines()
    return random.choice(facts).strip()


# Команда для вывода первого факта с кнопками "📕Еще 1 факт" и "Назад"
@dp.message_handler(Text(equals="📕1 Факт о физике"))
async def send_fact(message: types.Message):
    fact = get_random_fact()

    # Создание клавиатуры с кнопками "📕Еще 1 факт" и "🔙Назад"
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    keyboard.add("📕Еще 1 факт")
    keyboard.add("🔙Назад")

    await message.answer(fact, reply_markup=keyboard)


# Обработка нажатия кнопки "📕Еще 1 факт"
@dp.message_handler(Text(equals="📕Еще 1 факт"))
async def more_fact(message: types.Message):
    fact = get_random_fact()

    # Повторное создание клавиатуры с кнопками "📕Еще 1 факт" и "🔙Назад"
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    keyboard.add("📕Еще 1 факт")
    keyboard.add( "🔙Назад")

    await message.answer(fact, reply_markup=keyboard)


# Обработка нажатия кнопки "Назад"
@dp.message_handler(Text(equals="🔙Назад"))
async def back_to_menu(message: types.Message):
    # Возвращаем пользователя в главное меню с исходными кнопками
    main_menu_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    main_menu_keyboard.add(KeyboardButton("✨ Флюенс"), KeyboardButton("🔄 Конверт"))
    main_menu_keyboard.add(KeyboardButton("💥 Кинетическая Энергия"), KeyboardButton("🧲 Потенциальная Энергия"))
    main_menu_keyboard.add(KeyboardButton("📐 Плотность"), KeyboardButton("🚀 Импульс"))
    main_menu_keyboard.add(KeyboardButton("📕1 Факт о физике"))
    main_menu_keyboard.add(KeyboardButton("ℹ️ Help"))

    await message.answer("Вы вернулись в главное меню.", reply_markup=main_menu_keyboard)

    # Выбираем случайный факт и удаляем номер с точкой в начале строки
    fact = random.choice(facts).strip()
    fact = re.sub(r'^\d+\.\s*', '', fact)  # Удаляет все числа и точку в начале строки

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)