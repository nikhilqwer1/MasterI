import streamlit as st
from dotenv import load_dotenv
from rag_engine import DocumentEngine
from lesson_planner import generate_structured_lesson
from audio_engine import generate_scene_audio
from assessment_engine import generate_diagnostic_report

load_dotenv()
st.set_page_config(page_title="AI Teacher Classroom", layout="wide")

# Session State Setup
if "doc_engine" not in st.session_state:
    st.session_state.doc_engine = DocumentEngine()
if "lesson_plan" not in st.session_state:
    st.session_state.lesson_plan = None
if "current_scene_idx" not in st.session_state:
    st.session_state.current_scene_idx = 0
if "checkpoint_status" not in st.session_state:
    st.session_state.checkpoint_status = {}

st.title("🧑‍🏫 AI Teacher: Interactive Video Classroom")

# Left Sidebar: Inputs
with st.sidebar:
    st.header("⚙️ Lesson Configuration")
    uploaded_file = st.file_uploader("Upload PDF / Notes", type=["pdf", "txt"])
    if uploaded_file and st.button("Read Document"):
        with st.spinner("Document read ho raha hai..."):
            msg = st.session_state.doc_engine.process_file(uploaded_file)
            st.success(msg)

    topic = st.text_input("Topic Ka Naam", placeholder="e.g., Binary Search Trees")
    level = st.selectbox("Learner Level", ["Beginner", "Intermediate", "Advanced"])
    duration = st.slider("Time (Minutes)", 5, 45, 15, 5)
    language = st.selectbox("Teaching Language", ["Hinglish", "Hindi", "English"])

    if st.button("Start Lesson 🚀", type="primary"):
        with st.spinner("AI Teacher lesson prepare kar raha hai..."):
            ctx = st.session_state.doc_engine.retrieve_context(topic or "Summary")
            st.session_state.lesson_plan = generate_structured_lesson(
                topic=topic or "Study Material",
                context=ctx,
                level=level,
                time_mins=duration,
                language=language
            )
            st.session_state.current_scene_idx = 0
            st.session_state.checkpoint_status = {}
            st.rerun()

# Center Classroom Interface
if st.session_state.lesson_plan:
    plan = st.session_state.lesson_plan
    scenes = plan.scenes
    idx = st.session_state.current_scene_idx
    scene = scenes[idx]

    st.progress((idx + 1) / len(scenes), text=f"Scene {idx + 1}/{len(scenes)}: {scene.title}")

    col_teacher, col_board = st.columns([1, 1.3])

    with col_teacher:
        st.markdown("### 🎙️ AI Instructor")
        st.image("https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=450&auto=format&fit=crop&q=60", caption="Virtual Teacher")
        audio_file = generate_scene_audio(scene.avatar_speech, plan.language)
        st.audio(audio_file, format="audio/mp3", autoplay=True)
        st.info(f"🗣️ **Teacher Bolega:** {scene.avatar_speech}")

    with col_board:
        st.markdown("### 📋 Chalkboard")
        if scene.visual_type == "code":
            st.code(scene.visual_content, language="python")
        elif scene.visual_type == "formula":
            st.latex(scene.visual_content)
        else:
            st.markdown(scene.visual_content)

    # Checkpoint Question (Agar is scene me ho)
    checkpoints = [cp for cp in plan.checkpoints if cp.trigger_after_scene_id == scene.scene_id]
    can_go_next = True

    if checkpoints:
        cp = checkpoints[0]
        st.divider()
        st.markdown(f"#### ❓ Quick Checkpoint: {cp.question}")
        selected = st.radio("Sahi option chuniye:", cp.options, key=f"cp_{cp.checkpoint_id}")

        if st.button("Answer Submit Karein"):
            if selected == cp.correct_answer:
                st.session_state.checkpoint_status[cp.checkpoint_id] = True
                st.success("🎉 Bilkul Sahi! Agle scene par chalte hain.")
            else:
                st.session_state.checkpoint_status[cp.checkpoint_id] = False
                st.warning(f"💡 Simple Explanation: {cp.explanation_on_fail}")

        if not st.session_state.checkpoint_status.get(cp.checkpoint_id, False):
            can_go_next = False

    # Navigation Buttons
    st.divider()
    b1, b2, _ = st.columns([1, 1, 3])
    with b1:
        if st.button("⬅️ Previous", disabled=(idx == 0)):
            st.session_state.current_scene_idx -= 1
            st.rerun()
    with b2:
        if idx < len(scenes) - 1:
            if st.button("Next ➡️", disabled=not can_go_next):
                st.session_state.current_scene_idx += 1
                st.rerun()
        else:
            if st.button("Lesson Complete 🎉", disabled=not can_go_next):
                st.balloons()
                st.success("Shabash! Aapne poora lesson complete kar liya.")
else:
    st.info("Sidebar me topic enter karein ya PDF upload karein aur **Start Lesson** par click karein.")