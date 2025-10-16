
import os
from PIL import Image

# --- Конфигурация ---
ASSETS_DIR = "src/assets"
IMAGE_DIR = os.path.join(ASSETS_DIR, "IMAGE")
FRAME_IMAGE_DIR = os.path.join(ASSETS_DIR, "FRAME_IMAGE")
VIDEO_DIR = os.path.join(ASSETS_DIR, "VIDEO") # Для превью видео (файлы .png)
THUMBNAIL_DIR = os.path.join(ASSETS_DIR, "THUMBNAILS")
THUMBNAIL_SIZE = (200, 120) # (ширина, высота)

def create_thumbnail_for_file(source_path, dest_folder):
    """
    Создает миниатюру для одного файла и сохраняет ее.
    """
    filename = os.path.basename(source_path)
    dest_path = os.path.join(dest_folder, filename)

    # Пропускаем, если миниатюра уже существует
    if os.path.exists(dest_path):
        print(f"Миниатюра уже существует для: {filename}")
        return

    try:
        with Image.open(source_path) as img:
            # Создаем копию, чтобы сохранить исходные пропорции
            thumb_img = img.copy()
            thumb_img.thumbnail(THUMBNAIL_SIZE)
            
            # Сохраняем с оптимизацией
            thumb_img.save(dest_path, optimize=True, quality=85)
            print(f"Создана миниатюра для: {filename}")
    except Exception as e:
        print(f"Не удалось создать миниатюру для {filename}: {e}")

def process_directory(source_dir, dest_folder, file_extensions):
    """
    Обрабатывает директорию, создавая миниатюры для файлов с нужными расширениями.
    """
    if not os.path.exists(source_dir):
        print(f"Директория не найдена, пропускаем: {source_dir}")
        return
        
    for filename in os.listdir(source_dir):
        if any(filename.lower().endswith(ext) for ext in file_extensions):
            source_path = os.path.join(source_dir, filename)
            create_thumbnail_for_file(source_path, dest_folder)

if __name__ == "__main__":
    print("--- Запуск генерации миниатюр ---")
    
    # Убедимся, что папка для миниатюр существует
    os.makedirs(THUMBNAIL_DIR, exist_ok=True)
    
    # 1. Обрабатываем фоновые изображения
    print("\nОбработка папки IMAGE...")
    process_directory(IMAGE_DIR, THUMBNAIL_DIR, ['.jpg', '.jpeg', '.png'])
    
    # 2. Обрабатываем изображения рамок
    print("\nОбработка папки FRAME_IMAGE...")
    process_directory(FRAME_IMAGE_DIR, THUMBNAIL_DIR, ['.png'])

    # 3. Обрабатываем превью для видео (тоже .png)
    print("\nОбработка .png превью из папки VIDEO...")
    process_directory(VIDEO_DIR, THUMBNAIL_DIR, ['.png'])

    print("\n--- Генерация миниатюр завершена ---")
