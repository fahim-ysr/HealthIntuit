# Importing modules
import gradio as gd
from typing import Callable, Tuple, Any
from config.languages import get_language_manager


def create_interface(process_function: Callable) -> gd.Blocks:
    """Creates Gradio UI with multilingual support"""
    lang_manager = get_language_manager()

    # JavaScript to set light mode as default
    default_light_js = """
    function() {
        const url = new URL(window.location);
        if (!url.searchParams.has('__theme')) {
            url.searchParams.set('__theme', 'light');
            window.location.href = url.href;
        }
    }
    """
    
    custom_css = """
    #image-gallery {
        border: 2px dashed #e5e7eb;
        border-radius: 8px;
        padding: 10px;
    }

    #image-gallery .grid-wrap {
        gap: 10px;
    }

    #image-gallery img {
        border-radius: 6px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.2s ease;
    }

    #image-gallery img:hover {
        transform: scale(1.05);
    }
    """


    def handle_submission(name: str, audio_path: str, image_files) -> Tuple[str, str, Any, str, str]:
        """Handles form submission with error handling"""
        try:

            # Extracts file paths from uploaded files
            if image_files:
                if isinstance(image_files, list):
                    image_paths = [file.name for file in image_files if file is not None]
                else:
                    image_paths = [image_files.name] if image_files else []
            else:
                image_paths = []

            result = process_function(name, audio_path, image_paths)
            return (
                result["transcription"],
                result["diagnosis"],
                result["voice_response"],
                result["prescription_text"],
                result["prescription_file"]
            )
        except Exception as e:
            error_msg = lang_manager.get_text("error_analysis_failed").format(error=str(e))
            raise gd.Error(error_msg)
    

    def enable_inputs(name: str) -> Tuple[gd.update, gd.update]:
        """Enables/Disables inputs based on name entry"""
        is_enabled = bool(name and name.strip())
        return (
            gd.update(interactive=is_enabled),
            gd.update(interactive=is_enabled)
        )
    
    def update_language(lang_code: str):
        """Updates language"""
        
        lang_manager.set_language(lang_code)
        return [
            gd.update(value=f"<h1 style='font-size:2.5em; text-align:center; margin-bottom: 0.5em;'>{lang_manager.get_text('app_title')}</h1><p style='text-align:center; color: #666;'>{lang_manager.get_text('app_subtitle')}</p>"),
            gd.update(label=lang_manager.get_text("full_name_label"), placeholder=lang_manager.get_text("full_name_placeholder")),
            gd.update(label=lang_manager.get_text("audio_input_label")),
            gd.update(label=lang_manager.get_text("image_input_label")),
            gd.update(label=lang_manager.get_text("transcribed_query_label")),
            gd.update(label=lang_manager.get_text("doctors_analysis_label")),
            gd.update(label=lang_manager.get_text("voice_response_label")),
            gd.update(label=lang_manager.get_text("prescription_label")),
            gd.update(label=lang_manager.get_text("download_prescription_label")),
            gd.update(value=lang_manager.get_text("analyze_button"))
            ]
    
    def update_image_preview(files):
        """Update image preview gallery when files are uploaded"""
        if files and len(files) > 0:
            # Extracts file paths for gallery display
            image_paths = [file.name for file in files if file is not None]
            return gd.update(value=image_paths, visible=True)
        else:
            return gd.update(value=[], visible=False)

    
    with gd.Blocks(theme=gd.themes.Ocean(), js= default_light_js, css= custom_css) as interface:   #Theme: Ocean
        #  Compact language selector at top-right
        with gd.Row():
            gd.HTML("")  # Spacer
            with gd.Column(scale=0, min_width=150):
                with gd.Row():
                    language_selector = gd.Radio(
                        choices=[("🇺🇸", "en"), ("🇫🇷", "fr")],
                        value="en",
                        label="",
                        interactive=True,
                        container=False
                        )
        
        # Headers (Title and disclaimer)
        title_md = gd.Markdown(
            f"</br><h1 style='font-size:2.5em; text-align:center; margin-bottom: 0.5em;'>{lang_manager.get_text('app_title')}</h1>"
            f"<p style='text-align:center; color: #666;'>{lang_manager.get_text('app_subtitle')}</p>"
        )
        
        # Name input box
        name_box = gd.Textbox(
            label=lang_manager.get_text("full_name_label"),
            placeholder=lang_manager.get_text("full_name_placeholder")
        )
        
        # Main UI
        with gd.Row():
            # Input column
            with gd.Column(scale=2):
                audio_input = gd.Audio(
                    sources=["microphone"],
                    type="filepath",
                    label=lang_manager.get_text("audio_input_label"),
                    interactive=False
                )

                # Allows multiple images
                image_input = gd.File(
                    file_count= "multiple",
                    file_types= ["image"],
                    label=lang_manager.get_text("image_input_label"),
                    interactive=False
                )

                # Image preview gallery (slideshow)
                image_gallery = gd.Gallery(
                    label="Uploaded Images Preview",
                    show_label=True,
                    elem_id="image-gallery",
                    columns=2,
                    rows=2,
                    height="300px",
                    visible=False,
                    allow_preview=True,
                    show_share_button=False
                )
            
            # Output column
            with gd.Column(scale=2):
                stt_output = gd.Textbox(label=lang_manager.get_text("transcribed_query_label"))
                doctors_response = gd.Textbox(label=lang_manager.get_text("doctors_analysis_label"))
                voice_output = gd.Audio(label=lang_manager.get_text("voice_response_label"), type="numpy")
                prescription_output = gd.Textbox(label=lang_manager.get_text("prescription_label"), lines=8)
                download_btn = gd.File(label=lang_manager.get_text("download_prescription_label"), file_count="single")
        
        # Submit button
        submit_btn = gd.Button(lang_manager.get_text("analyze_button"), variant="primary")
        
        # Event handlers
        
        # Image preview update when files are uploaded
        image_input.change(
            update_image_preview,
            inputs=[image_input],
            outputs=[image_gallery]
        )

        language_selector.change(
            update_language,
            inputs=[language_selector],
            outputs=[title_md, name_box, audio_input, image_input, stt_output, 
                    doctors_response, voice_output, prescription_output, download_btn, submit_btn]
        )
        
        name_box.change(
            enable_inputs,
            inputs=name_box,
            outputs=[audio_input, image_input]
        )
        
        submit_btn.click(
            handle_submission,
            inputs=[name_box, audio_input, image_input],
            outputs=[stt_output, doctors_response, voice_output, prescription_output, download_btn]
        )
    
    return interface