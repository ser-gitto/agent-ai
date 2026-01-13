import streamlit as st
from openai import OpenAI

# ===== OPENAI =====
client = OpenAI()
MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = """
Jesteś trenerem fitness AI.
Prowadzisz użytkownika krok po kroku do osiągnięcia celu.

Zasady:
- Wykonujesz JEDEN krok naraz
- Po każdym kroku czekasz na odpowiedź użytkownika
- Odpowiadasz po polsku
- Nie zgadujesz
"""

# ===== LLM CALL =====
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

1. Najpierw wypytaj o brakujące dane (wiek, wzrost, waga, doświadczenie).
2. Następnie stwórz PLAN treningowy (kroki).
Nie realizuj planu – tylko go zaprojektuj.
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

Zareaguj na odpowiedź i przeprowadź użytkownika dalej.
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

# ===== STREAMLIT UI =====
st.set_page_config(page_title="Fit Sergio AI", page_icon="🤖")
st.title("🤖 Fit Sergio – Trener AI")

# ===== SESSION STATE =====
if "started" not in st.session_state:
    st.session_state.started = False
    st.session_state.goal = ""
    st.session_state.plan = ""
    st.session_state.steps = []
    st.session_state.current_step = 0
    st.session_state.history = []

# ===== START =====
goal = st.text_area("🎯 Opisz siebie i swój cel treningowy:")

if st.button("🚀 START") and goal and not st.session_state.started:
    st.session_state.started = True
    st.session_state.goal = goal
    st.session_state.plan = create_plan(goal)
    st.session_state.steps = [
        s for s in st.session_state.plan.split("\n") if s.strip()
    ]
    st.session_state.current_step = 0
    st.experimental_rerun()

# ===== DISPLAY PLAN =====
if st.session_state.started:
    st.subheader("🧠 Plan działania")
    st.code(st.session_state.plan)

# ===== AGENT LOOP (1 STEP) =====
if st.session_state.started and st.session_state.current_step < len(st.session_state.steps):

    step = st.session_state.steps[st.session_state.current_step]

    st.markdown(f"### 🔹 Krok {st.session_state.current_step + 1}")
    st.markdown(step)

    user_input = st.text_area(
        "✍️ Twoja odpowiedź:",
        key=f"user_input_{st.session_state.current_step}"
    )

    if st.button("➡️ Dalej", key=f"next_{st.session_state.current_step}") and user_input:

        result = execute_step(
            st.session_state.goal,
            st.session_state.plan,
            step,
            user_input
        )

        st.success(result)

        decision = critic(st.session_state.goal, result)
        st.info(f"🧐 Ocena agenta: {decision}")

        if "TAK" in decision.upper():
            st.balloons()
            st.success("✅ CEL ZREALIZOWANY")
            st.stop()

        st.session_state.current_step += 1
        st.experimental_rerun()

elif st.session_state.started:
    st.success("🏁 Plan zakończony – teraz konsekwencja 💪")
