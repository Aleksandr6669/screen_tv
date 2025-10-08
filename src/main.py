
import flet as ft
import asyncio
from datetime import datetime
import locale
import platform
import flet_video as fv
import pytz
import os
from database import get_settings_by_id, update_or_create_settings

# --- 1. НАСТРОЙКА ЛОКАЛИ (Для Русской Даты) ---
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

DEFAULT_TIMEZONE = 'Europe/Kiev'

def main(page: ft.Page):

    def get_file_names(directory):
        if not os.path.exists(directory):
            return []
        return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

    def get_last_path_segment(page: ft.Page) -> str | None:
        route_path = page.route.split('?')[0]
        segments = [s for s in route_path.split('/') if s]
        if segments:
            return segments[-1]
        return None

    # --- Pub/Sub Handler for Live Reload ---
    def on_settings_update(message):
        display_id = get_last_path_segment(page)
        if message == display_id:
            # Clear the page and redraw the clock to reflect new settings
            page.clean()
            show_clock()
            page.update()

    def is_video_file(filename):
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm'] # Add more video extensions if needed
        return os.path.splitext(filename)[1].lower() in video_extensions

    page.pubsub.subscribe(on_settings_update)

    def show_admin_panel():
        page.title = "Admin Panel"
        page.padding = 20
        page.window_width = 500
        page.window_height = 800
        page.scroll = ft.ScrollMode.AUTO

        image_files = get_file_names("src/assets/IMAGE")
        video_files = get_file_names("src/assets/VIDEO")
        video_files = [f for f in video_files if is_video_file(f)] # Filter for actual video files
        frame_files = get_file_names("src/assets/FRAME_IMAGE")
        all_timezones = pytz.all_timezones
    
        def create_thumbnail_preview(file_path):
            # Construct the full path for the thumbnail. Assuming thumbnails are in the same directory as the source file
            # and for videos, there is a .png thumbnail with the same name.
            full_path = os.path.join("src/assets", file_path.lstrip('/'))
            if os.path.exists(full_path):
                # Use a Container with a border and specific size for consistent display
                return ft.Container(content=ft.Image(src=file_path, width=50, height=50, fit=ft.ImageFit.COVER), width=50, height=50, bgcolor=ft.Colors.BLUE_GREY_700 )
            return ft.Container() # Return empty container if no file or "None"

        def on_bg_image_change(e):
            bg_image_preview.content = create_thumbnail_preview(f"/IMAGE/{bg_image_dropdown.value}")
            page.update()
            if bg_image_dropdown.value != "None":
                video_dropdown.value = "None"  # Clear video selection
                on_video_change(None)  # Update video preview

        def on_frame_image_change(e):
            frame_image_preview.content = create_thumbnail_preview(f"/FRAME_IMAGE/{frame_image_dropdown.value}")
            page.update()

        def on_video_change(e):
            # Construct the path for the video thumbnail (assuming .png extension)
            video_filename = video_dropdown.value
            if video_filename and video_filename != "None":
                thumbnail_path = f"/VIDEO/{os.path.splitext(video_filename)[0]}.png"
                video_preview.content = create_thumbnail_preview(thumbnail_path)
                bg_image_dropdown.value = "None"  # Clear background image selection
                on_bg_image_change(None)  # Update background image preview
            else:
                video_preview.content = ft.Container() # Display empty container if no video selected
            page.update()

        id_input = ft.TextField(label="Display ID", width=250)

        bg_image_options = [ft.dropdown.Option("None")] + [
            ft.dropdown.Option(
                key=file,
                content=ft.Row([create_thumbnail_preview(f"/IMAGE/{file}"), ft.Text(file)]), # Combine thumbnail and text
                data=file # Store file name in data
            ) for file in sorted(image_files)
            ]
        bg_image_dropdown = ft.Dropdown(label="Background Image", options=bg_image_options, width=300, on_change=on_bg_image_change)
        bg_image_preview = ft.Container()

        # Need to define video_preview here so it's accessible in on_bg_image_change
        
        video_dropdown = ft.Dropdown(label="Video", options=[], width=300, on_change=on_video_change) # Define video_dropdown early
        video_preview = ft.Container()

        frame_image_options = [ft.dropdown.Option("None")] + [
            ft.dropdown.Option(
                key=file,
                content=ft.Row([create_thumbnail_preview(f"/FRAME_IMAGE/{file}"), ft.Text(file)]), # Combine thumbnail and text
                data=file
            ) for file in sorted(frame_files)
            ]
        frame_image_dropdown = ft.Dropdown(label="Frame Image", options=frame_image_options, width=300, on_change=on_frame_image_change)
        frame_image_preview = ft.Container()

        video_options = [ft.dropdown.Option("None")] + [
            ft.dropdown.Option(
                key=file,
                content=ft.Row([create_thumbnail_preview(f"/VIDEO/{os.path.splitext(file)[0]}.png"), ft.Text(file)]), # Use video thumbnail
                data=file
             ) for file in sorted(video_files)
            ]

        timezone_options = [ft.dropdown.Option(tz) for tz in all_timezones]
        timezone_dropdown = ft.Dropdown(label="Timezone", options=timezone_options, width=400)
        status_text = ft.Text()
    
        def load_settings(e):
            display_id = id_input.value

            settings = get_settings_by_id(display_id)
            if settings:
                # Update dropdown options before setting value to ensure options exist
                bg_image_dropdown.value = settings.get('bg_image_url') or "None"
                frame_image_dropdown.value = settings.get('frame_image_url') or "None"
                video_dropdown.value = settings.get('video_url') or "None"
                # Trigger the change events to update previews on load
                on_bg_image_change(None) # Update preview on load
                on_frame_image_change(None) # Update preview on load
                on_video_change(None) # Update preview on load
                timezone_dropdown.value = settings.get('timezone', DEFAULT_TIMEZONE)
                status_text.value = f"Loaded settings for ID: {display_id}"
                status_text.color = ft.Colors.GREEN

            else:
                bg_image_dropdown.value = "None"
                frame_image_dropdown.value = "None"
                video_dropdown.value = "None"
                timezone_dropdown.value = DEFAULT_TIMEZONE
                status_text.value = f"No settings found for ID: {display_id}. You can create new settings."
                status_text.color = ft.Colors.ORANGE
            page.update()

        def save_settings(e):
            display_id = id_input.value
            settings = {
                'bg_image_url': bg_image_dropdown.value if bg_image_dropdown.value != "None" else "",
                'frame_image_url': frame_image_dropdown.value if frame_image_dropdown.value != "None" else "",
                'video_url': video_dropdown.value if video_dropdown.value != "None" else "",
                'timezone': timezone_dropdown.value
            }

            update_or_create_settings(display_id, settings)
            status_text.value = f"Settings for ID: {display_id} saved successfully!"
            status_text.color = ft.Colors.GREEN

            page.pubsub.send_all(message=display_id)
            page.update()

        # Set video dropdown options after defining video_dropdown and video_files
        video_dropdown.options = video_options

        # Initial update of previews
        on_bg_image_change(None)
        on_video_change(None)
        load_button = ft.ElevatedButton(text="Load", on_click=load_settings)
        save_button = ft.ElevatedButton(text="Save", on_click=save_settings)

        page.add(
            ft.Column(
                [
                    ft.Row([id_input, load_button], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Row([bg_image_dropdown, bg_image_preview]),
                    ft.Row([frame_image_dropdown, frame_image_preview]), # Display frame preview
                    ft.Row([video_dropdown, video_preview]), # Placeholder for video selection
                    timezone_dropdown,
                    save_button,
                    status_text
                ],
                spacing=20,
                scroll=ft.ScrollMode.AUTO
            )
        )
        page.update()

    def show_clock():
        page.title = "Заставка"
        page.bgcolor = ft.Colors.BLACK
        page.theme_mode = ft.ThemeMode.DARK
        page.padding = 0
        page.window_full_screen = True
        page.window_width = 3840
        page.window_height = 2160
        page.window_min_width = 3840
        page.window_min_height = 2160

        display_id = get_last_path_segment(page)
        settings = get_settings_by_id(display_id) if display_id else {}

        frame_image_url = settings.get("frame_image_url")
        bg_image_url = settings.get("bg_image_url")
        video_url = settings.get("video_url")
        local_time_zone = settings.get("timezone", DEFAULT_TIMEZONE)

        none = ft.Text("")
        time_text = ft.Text("00:00", color=ft.Colors.WHITE, size=60, font_family="Inter")
        date_text = ft.Text("Дата", color=ft.Colors.WHITE, size=18, font_family="Inter")
        id_text = ft.Text(f"ID: {display_id}" if display_id else "ID: Not Found", color=ft.Colors.with_opacity(0.5, ft.Colors.WHITE), size=16, font_family="Inter")

        content_to_show = []

        if video_url:
            video_player = fv.Video(
                playlist=[fv.VideoMedia(f"/VIDEO/{video_url}")],
                playlist_mode=fv.PlaylistMode.LOOP,
                fit=ft.ImageFit.FILL,
                width = 3840,
                height = 2160,
                muted=True, # Muted for autoplay
                autoplay=True,
                expand=True,
            )
            content_to_show.append(video_player)
        elif bg_image_url:
            background_image = ft.Image(src=f"/IMAGE/{bg_image_url}", width = 3840, height = 2160, fit=ft.ImageFit.FILL, expand=True)
            content_to_show.append(background_image)

        if frame_image_url:
            frame_overlay = ft.Image(src=f"/FRAME_IMAGE/{frame_image_url}", width = 3840, height = 2160, fit=ft.ImageFit.FILL, expand=True)
            content_to_show.append(frame_overlay)

        media_stack = ft.Stack(content_to_show, expand=True)

        async def update_time_loop():
            local_timezone = pytz.timezone(local_time_zone)
            while True:
                try:
                    now = datetime.now(local_timezone)
                    time_text.value = now.strftime("%H:%M")
                    formatted_date = now.strftime("%A, %d %B %Y г.").capitalize()
                    date_text.value = formatted_date

                    page.update()
                    await asyncio.sleep(1)
                except Exception:
                    # Stop the loop if controls are no longer on the page
                    break
        
        #Widges
        top_left_cornet= none
        top_center_cide= none
        top_right_cornet= id_text

        center_left_cidet= none
        center_center= none
        center_right_cide= none

        bottom_left_cornet= date_text 
        bottom_center_cide= none
        bottom_right_cornet= time_text

        top_bar = ft.Row([top_left_cornet, top_center_cide,  top_right_cornet], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.END)
        center_bar = ft.Row([center_left_cidet, center_center ,center_right_cide], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.END)
        bottom_bar = ft.Row([bottom_left_cornet, bottom_center_cide, bottom_right_cornet], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.END)

        top_overlay = ft.Container(content=top_bar, alignment=ft.alignment.top_center, expand=True, padding=ft.padding.only(top=50, left=70, right=70))
        center_overlay = ft.Container(content=center_bar, alignment=ft.alignment.center, expand=True, padding=ft.padding.only(left=70, right=70))
        bottom_overlay = ft.Container(content=bottom_bar, alignment=ft.alignment.bottom_center, expand=True, padding=ft.padding.only(bottom=50, left=70, right=70))
        # top_overlay = ft.Container(content=id_text, alignment=ft.alignment.top_right, expand=True, padding=ft.padding.only(top=50, left=70, right=70))

        page.add(ft.Stack([media_stack, center_overlay, top_overlay, bottom_overlay], expand=True))
        page.run_task(update_time_loop)
        page.update()

    def route_change(route):
        page.clean()
        if get_last_path_segment(page):
            show_clock()
        else:
            show_admin_panel()
        page.update()

    page.on_route_change = route_change
    page.go(page.route)

if __name__ == "__main__":
    ft.app(target=main, assets_dir="src/assets")
