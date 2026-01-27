import streamlit as st
from maseru_health_agent import MaseruHealthSupportSystem

st.set_page_config(
    page_title="Maseru Health Support",
    page_icon="🩺",
    layout="centered",
)

st.title("🩺 Maseru Health Support Assistant")

# ----------------------------
# Language toggle (Sidebar)
# ----------------------------
st.sidebar.title("Settings")
language = st.sidebar.radio("Language", ["English", "Sesotho"], index=0)

caption_en = (
    "A mental health support assistant based in Maseru, Lesotho. "
    "This system provides emotional support and guidance, not medical diagnosis or treatment."
)
caption_st = (
    "Mothusi oa tšehetso ea bophelo ba kelello ea thehiloeng Maseru, Lesotho. "
    "Sisteme ena e fana ka tšehetso le tataiso, eseng tlhahlobo kapa kalafo."
)

st.caption(caption_en if language == "English" else caption_st)

# ----------------------------
# Gentle escalation banner
# ----------------------------
def needs_escalation(text: str) -> bool:
    t = text.lower()
    crisis_terms = [
        "suicide", "kill myself", "self-harm", "hurt myself", "end my life",
        "hopeless", "no reason to live",
        "can't breathe", "chest pain", "severe bleeding", "fainted", "unconscious"
    ]
    return any(term in t for term in crisis_terms)

banner_en = (
    "💛 **If you feel unsafe or this is urgent:** please seek help immediately. "
    "You can go to **Queen ‘Mamohato Memorial Hospital** or your nearest clinic in Maseru."
)
banner_st = (
    "💛 **Haeba u ikutloa u le kotsing kapa taba ena e potlakile:** kopa thuso hang-hang. "
    "E-ea **Sepetlele sa Queen ‘Mamohato Memorial Hospital** kapa tleliniki e haufi Maseru."
)

# ----------------------------
# Initialize agent + chat history
# ----------------------------
if "agent" not in st.session_state:
    st.session_state.agent = MaseruHealthSupportSystem(user_id="patient_001")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Render chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ----------------------------
# Chat input
# ----------------------------
prompt_en = "How are you feeling today?"
prompt_st = "U ikutloa joang kajeno?"

user_input = st.chat_input(prompt_en if language == "English" else prompt_st)

if user_input:
    # Show escalation banner early if needed
    if needs_escalation(user_input):
        st.warning(banner_en if language == "English" else banner_st)

    # Show user message immediately
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Assistant placeholder + response
    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("_Listening and here for you…_" if language == "English" else "_Ke a mamela, ke teng le uena…_")

        # Simple language steering without changing your backend:
        # prepend a short instruction to the user message
        lang_instruction = (
            "Please respond in English.\n\n"
            if language == "English"
            else "Ka kōpo araba ka Sesotho.\n\n"
        )

        try:
            response = st.session_state.agent.chat(lang_instruction + user_input)
        except Exception as e:
            response = (
                "⚠️ I’m having trouble responding right now. Please try again in a moment."
                if language == "English"
                else "⚠️ Ke sitoa ho araba hona joale. Ka kōpo leka hape ka mor’a nakoana."
            )
            st.error(str(e))

        placeholder.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})

# Footer disclaimer
#st.markdown("---")
#footer_en = (
    #"⚠️ **Disclaimer:** This tool does not provide medical advice, diagnosis, or treatment. "
    #"If you are in immediate danger, seek urgent help locally."
#)
#footer_st = (
    #"⚠️ **Tlhokomeliso:** Sesebelisoa sena ha se fane ka keletso ea bongaka, tlhahlobo kapa kalafo. "
    #"Haeba u le kotsing hang-hang, kopa thuso ea tšohanyetso haufi le uena."
#)
#Sst.caption(footer_en if language == "English" else footer_st)
