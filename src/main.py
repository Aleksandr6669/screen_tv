import flet as ft
import asyncio
from datetime import datetime
import locale
import platform
import flet_video as fv 
import pytz

# --- 1. НАСТРОЙКА ЛОКАЛИ (Для Русской Даты) ---
# Устанавливаем русскую локаль для корректного отображения даты
if platform.system() == "Windows":
    locale.setlocale(locale.LC_TIME, "Russian_Russia.1251")
else:
    try:
        locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")
    except locale.Error:
        try:
            locale.setlocale(locale.LC_TIME, "ru_RU")
        except locale.Error:
            pass 


def main(page: ft.Page):
    page.title = "Цифровые Часы (Видео-Фон)"
    page.bgcolor = ft.Colors.BLACK 
    page.padding = 0 
    page.window_full_screen = True 
    
    # --- 2. ЭЛЕМЕНТЫ ТЕКСТА ---
    
    # Время: Крупный, жирный шрифт в левом нижнем углу
    time_text = ft.Text(
        "00:00:00", 
        color=ft.Colors.WHITE, 
        size=60,
        # weight=ft.FontWeight.w900, 
        font_family="Inter",
    )
    
    # Дата: Более тонкий шрифт в правом нижнем углу
    date_text = ft.Text(
        "Дата", 
        color=ft.Colors.WHITE, 
        size=18, 
        # weight=ft.FontWeight.w300, 
        font_family="Inter",
    )

    # --- 3. НАСТРОЙКА ВИДЕОПЛЕЕРА ---
    
    # Создаем плейлист из одного медиа-источника
    video_playlist = [
        fv.VideoMedia(
            # Используем YouTube ссылку, как в вашем примере
            # Для локального файла используйте: fv.VideoMedia("/assets/your_video.mp4")
            # "https://cdn.pixabay.com/video/2024/06/20/217489.mp4",
            # "https://cdn.pixabay.com/video/2022/12/01/141309-777508139.mp4",
            "https://cdn.pixabay.com/video/2024/06/23/217932.mp4",
            # Добавляем кэширование, чтобы видео не перезагружалось при повторах
            # http_headers={"Cache-Control": "max-age=31536000"} 
        )
    ]
    
    # Инициализация плеера
    video_player = fv.Video(
        playlist=video_playlist, 
        playlist_mode=fv.PlaylistMode.LOOP, # Зацикливание видео
        fit=ft.ImageFit.COVER, 
        muted=False,
        volume=0,             # Без звука
        autoplay=True,        # Автозапуск
        expand=True,          # Растягиваем на весь доступный размер
    )

    image_url = "/IMAGE/ai-generated-9387013_1920.png" 
    
    background_image = ft.Image(
        src=image_url,
        # Указываем конкретную ширину и высоту для 4K
        width=3840, 
        height=2160,
        fit=ft.ImageFit.FILL, # Растягиваем на весь доступный размер
        expand=True,
    )

    FRAME_IMAGE_URL = "/FRAME_IMAGE/border-318820_1920.png" 

    frame_overlay = ft.Image(
        src=FRAME_IMAGE_URL,
        width=3840, 
        height=2160,
        fit=ft.ImageFit.FILL, # Растягиваем изображение рамки, чтобы оно заполнило контейнер
        expand=True,
    )

    framed_picture_stack = ft.Stack(
        [
            background_image,     # Слой 1: Видео (фон картины)
            # video_player,
            frame_overlay,    # Слой 2: Изображение рамки (поверх видео)
        ],
        expand=True
    )

    # --- 4. АСИНХРОННЫЙ ЦИКЛ ОБНОВЛЕНИЯ ЧАСОВ ---
    async def update_time_loop():
        local_timezone = pytz.timezone('Europe/Kiev') 
        """Бесконечный цикл, обновляющий время и дату каждую секунду."""
        while True:
            utc_now = datetime.now(pytz.utc)
            now = utc_now.astimezone(local_timezone) 
            # now = datetime.now()
            
            time_text.value = now.strftime("%H:%M") 
            
            # Форматирование: 'Среда, 02 Октябрь 2025 г.'
            formatted_date = now.strftime("%A, %d %B %Y г.").capitalize()
            date_text.value = formatted_date
            
            page.update() 
            await asyncio.sleep(1) 

    # --- 5. РАЗМЕЩЕНИЕ КОНТЕНТА (Stack) ---

    # Элемент для позиционирования времени и даты по углам
    bottom_bar = ft.Row(
        [
            date_text,
            time_text,
            
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN, 
        vertical_alignment=ft.CrossAxisAlignment.END,
    )

    # Контейнер-накладка для прижимания bottom_bar вниз
    content_overlay = ft.Container(
        content=bottom_bar,
        alignment=ft.alignment.bottom_center, 
        expand=True,
        # Отступы от краев экрана
        padding=ft.padding.only(bottom=50, left=70, right=70) 
    )

    # Stack: Наложение видео (1-й слой) и контента (2-й слой)
    page.add(
        ft.Stack(
            [   
                framed_picture_stack ,
                content_overlay,
            ],
            expand=True 
        )
    )
    
    # Запуск цикла обновления времени в фоновом режиме
    page.run_task(update_time_loop)

if __name__ == "__main__":
    # Убедитесь, что плагин flet_video установлен: pip install flet-video
    ft.app(target=main)