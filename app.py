import streamlit as st
import json
import gemma_client

# Set page config
st.set_page_config(
    page_title="VaachaTask — Gujarati Business Instruction Assistant",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium CSS injection for aesthetics
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=Noto+Sans+Gujarati:wght@300;400;600;700&display=swap');
    
    /* Overall Fonts */
    html, body, [class*="css"], .stApp {
        font-family: 'Outfit', 'Noto Sans Gujarati', sans-serif;
    }
    
    /* Title Styling with vibrant gradient */
    .main-title {
        background: linear-gradient(135deg, #FF4B4B, #FF8008);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 2.8rem;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        color: #6c757d;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Card/Glassmorphism Container */
    .premium-card {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
        backdrop-filter: blur(4px);
        -webkit-backdrop-filter: blur(4px);
        margin-bottom: 1.5rem;
    }
    
    /* Preset Button Styling */
    .stButton>button {
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1) !important;
    }
    
    /* Generated Box Styling */
    .output-box {
        background-color: #e8f5e9;
        border-left: 5px solid #2e7d32;
        padding: 15px;
        border-radius: 4px;
        color: #1b5e20;
        font-size: 1.15rem;
        line-height: 1.6;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "extracted_data" not in st.session_state:
    st.session_state.extracted_data = None
if "generated_message" not in st.session_state:
    st.session_state.generated_message = None
if "preset_selected" not in st.session_state:
    st.session_state.preset_selected = ""

# Presets Definition
presets = [
    {
        "label": "🚚 Delivery Example (કાલે મનોજભાઈને...)",
        "text": "કાલે મનોજભાઈને 25 box મોકલવાના છે, ₹12,500 payment pending છે."
    },
    {
        "label": "💳 Payment Reminder (કિરણભાઈ સાથે ગુરુવારે...)",
        "text": "કિરણભાઈ સાથે ગુરુવારે પેમેન્ટ બાબતે મીટીંગ રાખજો, ₹50,000 લેવાના બાકી છે."
    },
    {
        "label": "📝 Order Example (આજે સુરેશભાઈને ત્યાંથી...)",
        "text": "આજે સાંજે સુરેશભાઈને ત્યાંથી 10 લીટર દૂધ લેવાનું છે."
    }
]

# Sidebar layout
with st.sidebar:
    st.image("https://img.icons8.com/clouds/150/000000/assistant.png", width=120)
    st.markdown("### Settings & Config")
    
    # API Key Input
    api_key_input = st.text_input(
        "Enter GEMINI_API_KEY (Optional)",
        type="password",
        help="If not provided, the app will check the .env file or run in offline mockup fallback mode."
    )
    
    # Configure API dynamically so we can check key validity
    api_ready = gemma_client.configure_api(api_key_input)
    if api_ready:
        st.success("API Status: Connected 🟢 (Realtime Mode)")
    else:
        st.error("API Status: Offline 🔴 (Static Mock Fallback)")
        
    st.markdown("---")

    st.markdown("### About VaachaTask")
    st.write(
        "VaachaTask uses Gemini/Gemma models to turn messy, informal Gujarati-English business instructions "
        "into structured database records and natural WhatsApp follow-up messages."
    )
    st.write("💡 *Made for Gujarati shopkeepers, distributors, and micro-businesses.*")

# Main Page Layout
st.markdown('<div class="main-title">VaachaTask — વાચાટાસ્ક</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Convert Gujarati business voice/text instructions into structured tasks & WhatsApp messages</div>', unsafe_allow_html=True)

# Row for Presets
st.markdown("### Quick Examples / Preset Prompts")
col_p1, col_p2, col_p3 = st.columns(3)
with col_p1:
    if st.button(presets[0]["label"], use_container_width=True):
        st.session_state.preset_selected = presets[0]["text"]
with col_p2:
    if st.button(presets[1]["label"], use_container_width=True):
        st.session_state.preset_selected = presets[1]["text"]
with col_p3:
    if st.button(presets[2]["label"], use_container_width=True):
        st.session_state.preset_selected = presets[2]["text"]

st.markdown("---")

# Input Section
st.markdown("### Step 1: Enter Business Instruction")

tab_text, tab_voice = st.tabs(["✍️ Type Instruction", "🎙️ Record Voice Instruction"])

with tab_text:
    instruction_input = st.text_area(
        "Type or paste informal Gujarati / Gujlish instruction here:",
        value=st.session_state.preset_selected,
        placeholder="e.g. કાલે રાકેશભાઇને ત્યાં 15 નંગ મશીન મોકલી દેજો...",
        height=100
    )

with tab_voice:
    audio_file = st.audio_input("Record your voice instruction in Gujarati:")
    if audio_file is not None:
        if st.button("🔊 Transcribe & Extract Task", type="secondary"):
            with st.spinner("Transcribing audio..."):
                transcription = gemma_client.transcribe_audio(audio_file, api_key=api_key_input)
                st.session_state.preset_selected = transcription
            
            if transcription and not transcription.startswith("ઑડિઓ ટ્રાન્સક્રિપ્શનમાં ભૂલ"):
                with st.spinner("Analyzing instruction with Gemma..."):
                    extracted = gemma_client.extract_fields(transcription, api_key=api_key_input)
                    st.session_state.extracted_data = extracted
                    st.session_state.generated_message = None
                st.success("Audio transcribed and task card built successfully!")
            else:
                st.error(f"Transcription failed: {transcription}")
            st.rerun()


# Extract Action
if st.button("🔍 Extract & Build Task Card", type="primary", use_container_width=True):

    if instruction_input.strip() == "":
        st.warning("Please enter some instruction first!")
    else:
        with st.spinner("Analyzing instruction with Gemma..."):
            extracted = gemma_client.extract_fields(instruction_input, api_key=api_key_input)
            st.session_state.extracted_data = extracted
            st.session_state.generated_message = None # Reset previous message

# Form Section (Editable Task Card)
if st.session_state.extracted_data:
    st.markdown("### Step 2: Review & Edit Task Card (Human-in-the-Loop)")
    
    # Access state fields safely
    data = st.session_state.extracted_data
    
    with st.container():
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            customer = st.text_input("Customer Name / પક્ષકાર", value=data.get("customer") or "")
            action_options = ["delivery", "payment reminder", "order", "follow-up", "other"]
            current_action = data.get("action")
            action_index = action_options.index(current_action) if current_action in action_options else 4
            action = st.selectbox("Action / ક્રિયા", options=action_options, index=action_index)
            
        with col2:
            quantity = st.text_input("Quantity / જથ્થો", value=data.get("quantity") or "")
            due_date = st.text_input("Due Date / સમયમર્યાદા", value=data.get("due_date") or "")
            
        with col3:
            amount = st.text_input("Amount / રકમ", value=data.get("amount") or "")
            status_options = ["pending", "completed", "None"]
            current_status = str(data.get("payment_status"))
            status_index = status_options.index(current_status) if current_status in status_options else 2
            payment_status = st.selectbox("Payment Status / પેમેન્ટ સ્થિતિ", options=status_options, index=status_index)
            
        next_action = st.text_area("Next Action Summary / આગળની કાર્યવાહી", value=data.get("next_action") or "", height=80)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Save edited values back to state
        st.session_state.extracted_data = {
            "customer": customer,
            "action": action,
            "quantity": quantity if quantity else None,
            "due_date": due_date if due_date else None,
            "amount": amount if amount else None,
            "payment_status": None if payment_status == "None" else payment_status,
            "next_action": next_action
        }

    # Step 3: Generate confirmation message
    if st.button("✉️ Confirm & Generate WhatsApp Message", type="secondary", use_container_width=True):
        with st.spinner("Generating natural Gujarati communication..."):
            msg = gemma_client.generate_confirmation(st.session_state.extracted_data, api_key=api_key_input)
            st.session_state.generated_message = msg

if st.session_state.generated_message:
    st.markdown("### Step 3: Ready-to-Send Gujarati WhatsApp Message")
    st.info("Copy the message below to send directly to your customer.")
    
    # Output box with HTML styling
    st.markdown(
        f'<div class="output-box">{st.session_state.generated_message}</div>', 
        unsafe_allow_html=True
    )
    
    # Text area for easy copying
    st.text_area("Plain Text (Copy from here):", value=st.session_state.generated_message, height=120)
