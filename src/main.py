
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
            page.clean()
            show_clock()
            page.update()

    def is_video_file(filename):
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
        return os.path.splitext(filename)[1].lower() in video_extensions

    page.pubsub.subscribe(on_settings_update)

    def show_admin_panel():
        page.title = "Admin Panel"
        page.padding = ft.padding.only(left=5, right=5)
        page.scroll = ft.ScrollMode.HIDDEN

        # --- Get available media files ---
        image_files = sorted(get_file_names("src/assets/IMAGE"))
        video_files = sorted([f for f in get_file_names("src/assets/VIDEO") if is_video_file(f)])
        frame_files = sorted(get_file_names("src/assets/FRAME_IMAGE"))
        all_timezones = pytz.all_timezones

        # --- State Management for selections ---
        admin_state = {
            "bg_image": None,
            "frame_image": None,
            "video": None,
        }

        # --- UI Controls ---
        id_input = ft.TextField(width=250, border_radius=12)
        status_text = ft.Text()



        def filter_timezone_options(e):
            """Filters the timezone dropdown based on user input."""
            search_term = e.control.value.lower()
            if not search_term:
                filtered_options = [ft.dropdown.Option(tz) for tz in all_timezones]
                # timezone_dropdown.options = [ft.dropdown.Option(tz) for tz in all_timezones]
            else:
                filtered_options = [
                    ft.dropdown.Option(tz) for tz in all_timezones if search_term in tz.lower()
                ]
            timezone_dropdown.options = filtered_options

            if timezone_dropdown.options:
                timezone_dropdown.value = timezone_dropdown.options[0].key
            else:
                timezone_dropdown.value = None
            
            page.update()


        search_timezone = ft.TextField(
            label="Search Timezone",
            width=300,
            border_radius=20,
            on_change=filter_timezone_options
        )

        timezone_dropdown = ft.Dropdown(
            label="Timezone",
            options=[ft.dropdown.Option(tz) for tz in all_timezones],
            width=300,
            border_radius=20
        )
        
        # Rows for horizontal lists
        bg_image_row = ft.Row(scroll=ft.ScrollMode.HIDDEN)
        frame_image_row = ft.Row(scroll=ft.ScrollMode.HIDDEN)
        video_row = ft.Row(scroll=ft.ScrollMode.HIDDEN)

        # --- Core Functions for UI Update and Selection ---

        # def create_thumbnail(file_path, filename, on_click_handler, is_selected):
        #     return ft.GestureDetector(
        #         on_tap=on_click_handler,
        #         data=filename,
        #         content=ft.Container(
        #             content=ft.Image(src=file_path, width=200, height=120, fit=ft.ImageFit.FILL, border_radius=ft.border_radius.all(10)),
        #             width=205,
        #             height=125,
        #             border=ft.border.all(5, ft.Colors.BLUE) if is_selected else None,
        #             border_radius=ft.border_radius.all(12),
        #         )
        #     )

        def create_thumbnail(file_path, filename, on_click_handler, is_selected):
            # Основной виджет изображения
            image_widget = ft.Image(
                src=file_path, 
                width=200, 
                height=120, 
                fit=ft.ImageFit.FILL, 
                border_radius=ft.border_radius.all(10)
            )

            # Иконка галочки, которая будет накладываться
            checkmark_icon = ft.Icon(
                ft.Icons.CHECK_CIRCLE,
                color=ft.Colors.GREEN,
                size=30
            )

            # Используем Stack, чтобы расположить иконку поверх изображения
            content_stack = ft.Stack(
                [
                    image_widget,
                    # Контейнер для иконки позволяет точно ее позиционировать
                    ft.Container(
                        content=checkmark_icon,
                        alignment=ft.alignment.bottom_left, # Позиция в правом нижнем углу
                        visible=is_selected # Видимость зависит от того, выбран ли элемент
                    )
                ]
            )

            # Основная кликабельная область
            return ft.GestureDetector(
                on_tap=on_click_handler,
                data=filename,
                content=ft.Container(
                    content=content_stack,
                    width=200,
                    height=120,
                    alignment=ft.alignment.center,
                    border_radius=ft.border_radius.all(12),
                )
            )

        def update_watch_page_ui():
            '''Rebuilds the content of the media selection rows based on the current state.'''
            bg_image_row.controls = [
                create_thumbnail(f"/THUMBNAILS/{f}", f, select_bg_image, f == admin_state["bg_image"])
                for f in image_files
            ]
            frame_image_row.controls = [
                create_thumbnail(f"/THUMBNAILS/{f}", f, select_frame_image, f == admin_state["frame_image"])
                for f in frame_files
            ]
            video_row.controls = [
                create_thumbnail(f"/THUMBNAILS/{os.path.splitext(f)[0]}.png", f, select_video, f == admin_state["video"])
                for f in video_files
            ]
            page.update()

        def select_bg_image(e):
            filename = e.control.data
            admin_state["bg_image"] = filename if admin_state["bg_image"] != filename else None
            if admin_state["bg_image"]:
                admin_state["video"] = None  # Deselect video
            update_watch_page_ui()

        def select_frame_image(e):
            filename = e.control.data
            admin_state["frame_image"] = filename if admin_state["frame_image"] != filename else None
            update_watch_page_ui()

        def select_video(e):
            filename = e.control.data
            admin_state["video"] = filename if admin_state["video"] != filename else None
            if admin_state["video"]:
                admin_state["bg_image"] = None # Deselect background image
            update_watch_page_ui()
            
        # --- Load/Save Functions ---
        def load_settings(e):
            display_id = id_input.value
            settings = get_settings_by_id(display_id)
            if settings:
                admin_state["bg_image"] = settings.get('bg_image_url') or None
                admin_state["frame_image"] = settings.get('frame_image_url') or None
                admin_state["video"] = settings.get('video_url') or None
                timezone_dropdown.value = settings.get('timezone', DEFAULT_TIMEZONE)
                status_text.value = f"Loaded settings for ID: {display_id}"
                status_text.color = ft.Colors.GREEN
            else:
                admin_state["bg_image"] = None
                admin_state["frame_image"] = None
                admin_state["video"] = None
                timezone_dropdown.value = DEFAULT_TIMEZONE
                status_text.value = f"No settings found for ID: {display_id}. You can create new settings."
                status_text.color = ft.Colors.ORANGE
            update_watch_page_ui()
            page.update()

        def save_settings(e):
            display_id = id_input.value
            if not display_id:
                status_text.value = "Please enter a Display ID before saving."
                status_text.color = ft.Colors.RED
                page.update()
                return

            settings = {
                'bg_image_url': admin_state["bg_image"],
                'frame_image_url': admin_state["frame_image"],
                'video_url': admin_state["video"],
                'timezone': timezone_dropdown.value
            }
            update_or_create_settings(display_id, settings)
            status_text.value = f"Settings for ID: {display_id} saved successfully!"
            status_text.color = ft.Colors.GREEN
            page.pubsub.send_all(message=display_id)
            page.update()
        
        # load_button = ft.ElevatedButton(text="Load", on_click=load_settings)

        load_button = ft.CupertinoButton(
            content=ft.Text("Load", color=ft.Colors.GREY_300),
            bgcolor=ft.Colors.GREEN_400,
            alignment=ft.alignment.top_left,
            border_radius=ft.border_radius.all(12),
            opacity_on_click=0.7,
            on_click=load_settings,
        )

        # save_button = ft.ElevatedButton(text="Save", on_click=save_settings)

        save_button = ft.CupertinoButton(
            content=ft.Text("Save", color=ft.Colors.GREY_300),
            bgcolor=ft.Colors.GREEN_400,
            alignment=ft.alignment.top_left,
            border_radius=ft.border_radius.all(12),
            opacity_on_click=0.7,
            on_click=save_settings,
        )


        

        # --- Page Content Definitions ---
        def get_watch_page():
            # Initial build of the rows
            update_watch_page_ui()
            return ft.Column(
                [   
                    ft.Container(),
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("ID app TV", size=18, theme_style=ft.TextThemeStyle.HEADLINE_SMALL),
                                    ft.Row([id_input, load_button], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                ]
                            ),
                            # width=400,
                            padding=10,
                        ),
                        shadow_color=ft.Colors.ON_SURFACE_VARIANT,
                    ),
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("Background Image", size=18),
                                    bg_image_row,
                                ]
                            ),
                            # width=400,
                            padding=10,
                        ),
                        shadow_color=ft.Colors.ON_SURFACE_VARIANT,
                    ),
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("Frame Image", size=18),
                                    frame_image_row,
                                ]
                            ),
                            # width=400,
                            padding=10,
                        ),
                        shadow_color=ft.Colors.ON_SURFACE_VARIANT,
                    ),
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("Background Video", size=18),
                                    video_row,
                                ]
                            ),
                            # width=400,
                            padding=10,
                        ),
                        shadow_color=ft.Colors.ON_SURFACE_VARIANT,
                    ),
                    
                    
                    
                    save_button,
                    status_text
                ],
                spacing=15,
            )

        def get_widget_page():
            return ft.Column([ft.Text("Widget Page - Placeholder", size=20)])

        def get_settings_page():
            return ft.Column(
                [
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("Settings Page - Placeholder", size=20),
                                    search_timezone,
                                    timezone_dropdown, 
                                ]
                            ),
                            width=600,
                            padding=10,
                        ),
                        shadow_color=ft.Colors.ON_SURFACE_VARIANT,
                    ),
                    
                    
                    save_button,
                    status_text
                    
                ]
            )
        
        # --- Main Content Area & Navigation ---
        page_content = ft.Container(content=get_watch_page(), expand=True)

        def on_navigation_change(e):
            selected_index = e.control.selected_index
            if selected_index == 0:
                page_content.content = get_watch_page()
            elif selected_index == 1:
                page_content.content = get_widget_page()
            elif selected_index == 2:
                page_content.content = get_settings_page()
            page.update()

        # --- Page Setup ---
        page.appbar = ft.AppBar(
            # adaptive = True,
            title=ft.Text("Admin Panel"),
            center_title=True,
            bgcolor=ft.Colors.GREEN,
            automatically_imply_leading=False,
        )
        page.navigation_bar = ft.NavigationBar(
            destinations=[
                ft.NavigationBarDestination(icon=ft.Icons.IMAGE_SEARCH, label="Media"),
                ft.NavigationBarDestination(icon=ft.Icons.WIDGETS_OUTLINED, label="Widgets"),
                ft.NavigationBarDestination(icon=ft.Icons.SETTINGS_OUTLINED, label="Settings"),
            ],
            on_change=on_navigation_change,
            selected_index=0
        )

        page.add(page_content)
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
