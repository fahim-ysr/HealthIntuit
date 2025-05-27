# Importing modules
import gradio as gd
from typing import Callable, Tuple, Any
from config.languages import get_language_manager
from services.medical_services import FollowUpService
from config.settings import get_config


def create_interface(process_function: Callable) -> gd.Blocks:
    """Creates Gradio UI with multilingual support and follow-up chat capabilities"""
    lang_manager = get_language_manager()

    # Initialize global follow_up_service
    global follow_up_service
    follow_up_service= None

    print("DEBUG: Follow-up service initialized as None - chat should be hidden")

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
    
    # For image presentation
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
    
    /* Fixed Popup Modal Styles - Remove display: flex !important */
    .popup-overlay {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100% !important;
        height: 100% !important;
        background-color: rgba(0, 0, 0, 0.5) !important;
        z-index: 1000 !important;
        /* REMOVED: display: flex !important; */
        align-items: center !important;
        justify-content: center !important;
    }

    /* Add this new rule for when popup is visible */
    .popup-overlay[style*="display: block"] {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    .popup-chatbot {
        background: white !important;
        border-radius: 12px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3) !important;
        width: 500px !important;
        max-height: 600px !important;
        padding: 20px !important;
        max-width: 90vw !important;
    }

    .chat-toggle-btn {
        position: fixed !important;
        bottom: 20px !important;
        right: 20px !important;
        width: 60px !important;
        height: 60px !important;
        border-radius: 50% !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        color: white !important;
        font-size: 24px !important;
        cursor: pointer !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
        z-index: 999 !important;
        transition: transform 0.2s ease !important;
    }

    .chat-toggle-btn:hover {
        transform: scale(1.1) !important;
    }
    """


    def handle_submission(name: str, audio_path: str, image_files) -> Tuple[str, str, Any, str, str, gd.update]:
        """Handles form submission and enables follow up chat button (Emergency Detection Enabled)"""
        
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

            # Handling emergency cases differently
            if result.get("is_emergency", False):
                # For emergencies
                emergency_analysis= result.get("emergency_analysis", {})
                confidence= emergency_analysis.get("confidence_score", 0)
                emergency_type= emergency_analysis.get("emergency_type", 'unknown')

                emergency_diagnosis= f"MEDICAL EMERGENCY DETECTED \nType: {emergency_type.upper()}\nConfidence: {confidence}%\n\n{result['diagnosis']}"

                # Doesn't initialize follow-ups for emergency cases
                return (
                    result["transcription"],
                    emergency_diagnosis,
                    result["voice_response"],
                    result["prescription_text"],
                    result["prescription_file"],
                    gd.update(visible=False)  # Don't show chat for emergencies
                    )
            
            else:

                # Initializes follow-up service with context and stores in global variable (Since this function only supports 6 inputs)
                global follow_up_service
                follow_up_service = FollowUpService(get_config(), lang_manager)

                follow_up_service.initialize_follow_up(
                    result["diagnosis"],
                    result["prescription_text"],
                    name
                )
                
                return (
                    result["transcription"],
                    result["diagnosis"],
                    result["voice_response"],
                    result["prescription_text"],
                    result["prescription_file"],
                    gd.update(visible=True),     # Shows up the follow up section after successful completion
                )
        
        except Exception as e:
            error_msg = lang_manager.get_text("error_analysis_failed").format(error=str(e))
            raise gd.Error(error_msg)
        
    
    def handle_follow_up(question: str, chat_history):
        """Handles follow up questions using global variable"""
        global follow_up_service
        if follow_up_service and question.strip():
            try:
                response = follow_up_service.process_follow_up_question(question)
                chat_history.append([question, response])
                return "", chat_history
            
            except Exception as e:
                chat_history.append([question, f"Error: {str(e)}"])
                return "", chat_history
            
        return question, chat_history
    

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

        # Floating chat button (initially hidden)
        chat_toggle_btn = gd.Button(
            "💬", 
            elem_classes=["chat-toggle-btn"],
            visible=False,
            variant="primary"
        )

        # Popup chatbot modal (initially hidden)
        with gd.Column(visible=False, elem_classes=["popup-overlay"]) as chat_popup:
            with gd.Column(elem_classes=["popup-chatbot"]):
                with gd.Row():
                    gd.Markdown("### 💬 Ask Follow-up Questions")
                    close_btn = gd.Button("✕", size="sm", variant="secondary")
                
                chatbot = gd.Chatbot(
                    label="Chat with Doctor",
                    height=350,
                    show_label=False,
                )
                follow_up_input = gd.Textbox(
                    label="",
                    placeholder="Ask about your diagnosis or prescription...",
                    lines=2
                )
                follow_up_btn = gd.Button("Send", variant="primary")
        
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
            outputs=[stt_output, doctors_response, voice_output, prescription_output, download_btn, chat_toggle_btn]
        )

        # Chat popup controls
        chat_toggle_btn.click(
            lambda: gd.update(visible=True),
            outputs=[chat_popup]
        )

        close_btn.click(
            lambda: gd.update(visible=False),
            outputs=[chat_popup]
        )

        # Follow-up chat functionality
        follow_up_btn.click(
            handle_follow_up,
            inputs=[follow_up_input, chatbot],
            outputs=[follow_up_input, chatbot]
        )

        follow_up_input.submit(
            handle_follow_up,
            inputs=[follow_up_input, chatbot],
            outputs=[follow_up_input, chatbot]
        )
    
    return interface