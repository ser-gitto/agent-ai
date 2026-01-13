import streamlit as st
from openai import OpenAI

# =====================
# OPENAI CONFIG
# =====================
client = OpenAI()
MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = """
Jesteś trenerem fitness AI.
Prowadzisz użytkownika krok po kroku do osiągnięcia celu.

Zasady:
- Wykonujesz JEDEN krok naraz
- Po każdym kroku CZEKASZ na odpowiedź użytkownika
- Odpowiadasz po polsku
- Nie zgadujesz
"""

# =====================
# LLM FUNCTIONS
# =====================
def call_llm(messages):
    response = client.responses.create(
        model=MODEL,
        input=messages
    )
    return response.output_text.strip()

def create_plan(goal):
    return call_llm([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"""
CEL UŻYTKOWNIKA:
{goal}

Najpierw wypytaj o brakujące dane (wiek, wzrost, waga, doświadczenie).
Następnie zaprojektuj PLAN krok po kroku.
NIE realizuj planu – tylko go zaprojektuj.
"""}
    ])

def execute_step(goal, plan, step, user_input):
    return call_llm([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"""
CEL:
{goal}

PLAN:
{plan}

AKTUALNY KROK:
{step}

ODPOWIEDŹ UŻYTKOWNIKA:
{user_input}

Zareaguj na odpowiedź i poprowadź użytkownika dalej.
"""}
    ])

def critic(goal, result):
    return call_llm([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"""
CEL:
{goal}

OSTATNI WYNIK:
{result}

Czy cel został zrealizowany?
Odpowiedz TYLKO: TAK lub NIE.
"""}
    ])

# =====================
# STREAMLIT UI
# =====================
st.set_page_config(page_title="Fit Sergio AI", page_icon="🤖")
st.title("🤖 Fit Sergio – Trener AI")

# =====================
# SESSION STATE INIT
# =====================
if "mode" not in st.session_state:
    st.session_state.mode = "init"      # init | wait | process
    st.session_state.started = False
    st.session_state.goal = ""
    st.session_state.plan = ""
    st.session_state.steps = []
    st.session_state.current_step = 0
    st.session_state.user_input = ""

# =====================
# START SCREEN
# =====================
goal = st.text_area("🎯 Opisz siebie i swój cel treningowy:")

if st.button("🚀 START") and goal and not st.session_state.started:
    st.session_state.started = True
    st.session_state.goal = goal
    st.session_state.plan = create_plan(goal)
    st.session_state.steps = [
        s for s in st.session_state.plan.split("\n") if s.strip()
    ]
    st.session_state.current_step = 0
    st.session_state.mode = "wait"

# =====================
# SHOW PLAN
# =====================
if st.session_state.started:
    st.subheader("🧠 Plan działania")
    st.code(st.session_state.plan)

# =====================
# WAIT FOR USER INPUT
# =====================
if st.session_state.started and st.session_state.mode == "wait":

    step = st.session_state.steps[st.session_state.current_step]

    st.markdown(f"### 🔹 Krok {st.session_state.current_step + 1}")
    st.markdown(step)

    st.session_state.user_input = st.text_area(
        "✍️ Twoja odpowiedź:",
        key="user_input_box"
    )

    if st.button("➡️ Wyślij odpowiedź"):
        st.session_state.mode = "process"

# =====================
# PROCESS STEP
# =====================
if st.session_state.started and st.session_state.mode == "process":

    step = st.session_state.steps[st.session_state.current_step]

    result = execute_step(
        st.session_state.goal,
        st.session_state.plan,
        step,
        st.session_state.user_input
    )

    st.success(result)

    decision = critic(st.session_state.goal, result)
    st.info(f"🧐 Ocena agenta: {decision}")

    if "TAK" in decision.upper():
        st.balloons()
        st.success("✅ CEL ZREALIZOWANY")
        st.stop()

    st.session_state.current_step += 1
    st.session_state.user_input = ""
    st.session_state.mode = "wait"
    st.rerun()

