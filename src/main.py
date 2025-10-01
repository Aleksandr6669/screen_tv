import flet as ft

# Константы для сетки и цветов
GRID_SIZE = 3 # Размер сетки (3x3)
TOTAL_ITEMS = GRID_SIZE * GRID_SIZE
BASE_COLOR = ft.Colors.BLUE_GREY_700 # Базовый цвет невыбранного элемента
SELECTED_COLOR = ft.Colors.YELLOW_600 # Цвет выбранного элемента

def create_menu_item(index: int) -> ft.Container:
    """Создает контейнер для одного пункта меню."""
    return ft.Container(
        content=ft.Text(f"Канал {index + 1}", color=ft.Colors.WHITE, size=18, weight=ft.FontWeight.W_500),
        width=150,
        height=100,
        bgcolor=BASE_COLOR,
        border_radius=ft.border_radius.all(10),
        alignment=ft.alignment.center,
        data=index, # Храним индекс для идентификации
        # Обработчик клика/Enter (в консоль будет выведено сообщение)
        on_click=lambda e: print(f"Выбран канал: {e.control.data + 1}"),
        # Добавляем тень для лучшего вида
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=5,
            color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK),
            offset=ft.Offset(0, 2),
            blur_style=ft.ShadowBlurStyle.OUTER,
        )
    )

def main(page: ft.Page):
    page.title = "TV Menu Simulator"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = ft.Colors.BLUE_GREY_900
    
    # Сбрасываем лишние элементы из вашего шаблона
    page.floating_action_button = None

    # --- Инициализация состояния и элементов ---
    
    # selected_index будет хранить текущий выбранный индекс (от 0 до 8)
    page.selected_index = 0 
    menu_items = [create_menu_item(i) for i in range(TOTAL_ITEMS)]

    # Сетка для отображения меню
    menu_grid = ft.GridView(
        controls=menu_items,
        runs_count=GRID_SIZE,
        child_aspect_ratio=1.5,
        spacing=20,
        run_spacing=20,
        width=550, # Ширина для 3 колонок с отступами
        height=350, # Высота для 3 рядов с отступами
    )
    
    # --- Логика обновления интерфейса ---

    def update_selection_ui(new_index: int):
        """Обновляет визуальное состояние элементов при смене выбора."""
        
        # Снимаем выделение со старого элемента
        if 0 <= page.selected_index < TOTAL_ITEMS:
            old_item = menu_items[page.selected_index]
            old_item.bgcolor = BASE_COLOR
            old_item.content.weight = ft.FontWeight.W_500
            old_item.content.scale = 1.0
            old_item.update()

        # Выделяем новый элемент
        page.selected_index = new_index
        new_item = menu_items[page.selected_index]
        new_item.bgcolor = SELECTED_COLOR
        new_item.content.weight = ft.FontWeight.BOLD # Жирный шрифт
        new_item.content.scale = 1.1 # Немного увеличиваем
        new_item.update()

    # Начальное выделение первого элемента
    # update_selection_ui(0)

    # --- Обработчик нажатий клавиш ("пульта") ---
    
    def on_keyboard(e: ft.KeyboardEvent):
        """Обрабатывает нажатия стрелок для навигации."""
        key = e.key
        current_index = page.selected_index
        new_index = current_index

        if key == "Arrow Right":
            # Вправо: если не в конце текущего ряда
            if (current_index + 1) % GRID_SIZE != 0:
                new_index = current_index + 1
        elif key == "Arrow Left":
            # Влево: если не в начале текущего ряда
            if current_index % GRID_SIZE != 0:
                new_index = current_index - 1
        elif key == "Arrow Down":
            # Вниз: если не в нижнем ряду
            if current_index + GRID_SIZE < TOTAL_ITEMS:
                new_index = current_index + GRID_SIZE
        elif key == "Arrow Up":
            # Вверх: если не в верхнем ряду
            if current_index - GRID_SIZE >= 0:
                new_index = current_index - GRID_SIZE
        elif key == "Enter":
            # Нажатие Enter симулирует выбор
            print(f"ENTER (Выбор) на канале: {current_index + 1}")
            # Выполняем логику, которая была бы при клике
            menu_items[current_index].on_click(None) 

        # Обновляем UI, если индекс изменился
        if new_index != current_index:
            update_selection_ui(new_index)
        
        # Предотвращаем стандартное поведение браузера (например, прокрутку страницы)
        if key in ["Arrow Right", "Arrow Left", "Arrow Down", "Arrow Up", "Enter"]:
            e.preventDefault = True
            page.update()

    # Привязываем обработчик к странице
    page.on_keyboard_event = on_keyboard

    # Инструкции для пользователя
    instructions = ft.Text(
        "Управляйте меню с помощью клавиш-стрелок (↑, ↓, ←, →) и 'Enter' для выбора.",
        color=ft.Colors.WHITE,
        size=16,
        weight=ft.FontWeight.W_300,
        font_family="Inter",
    )
    
    # Главный контейнер для центрирования
    main_content = ft.Column(
        [
            instructions,
            ft.Container(height=20),
            menu_grid
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER
    )

    page.add(
        ft.SafeArea(
            ft.Container(
                main_content,
                alignment=ft.alignment.center,
                expand=True,
                padding=ft.padding.all(20),
            ),
            expand=True,
        )
    )

if __name__ == "__main__":
    ft.app(target=main, assets_dir='assets')