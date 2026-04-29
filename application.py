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

banner_en = (
    "**You are not alone.** Please consider visiting a nearby clinic or speaking "
    "to a professional."
)
banner_st = (
    "**Ha u mong.** Ka kōpo nahana ka ho etela tleliniki e haufi kapa ho bua "
    "le setsebi."
)

# ----------------------------
# Initialize agent + chat history
# ----------------------------
if "agent" not in st.session_state:
    st.session_state.agent = MaseruHealthSupportSystem(user_id="patient_001")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "risk_assessments" not in st.session_state:
    st.session_state.risk_assessments = []

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
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown(
            "_Listening and here for you..._"
            if language == "English"
            else "_Ke a mamela, ke teng le uena..._"
        )

        lang_instruction = (
            "Please respond in English.\n\n"
            if language == "English"
            else "Ka kōpo araba ka Sesotho.\n\n"
        )

        try:
            response, risk = st.session_state.agent.chat_with_risk(
                lang_instruction + user_input
            )
        except Exception as e:
            risk = st.session_state.agent.assess_risk(user_input)
            response = (
                "⚠️ I'm having trouble responding right now. Please try again in a moment."
                if language == "English"
                else "⚠️ Ke sitoa ho araba hona joale. Ka kōpo leka hape ka mor'a nakoana."
            )
            st.error(str(e))

        if risk["risk_level"] == "HIGH":
            st.warning(banner_en if language == "English" else banner_st)

        placeholder.markdown(response)

    st.session_state.risk_assessments.append(
        {
            "message": user_input,
            "risk_level": risk["risk_level"],
            "confidence_score": risk["probability"],
            "reason": risk["reason"],
            "matched_keywords": ", ".join(risk["matched_keywords"]) or "None",
        }
    )
    st.session_state.messages.append({"role": "assistant", "content": response})
