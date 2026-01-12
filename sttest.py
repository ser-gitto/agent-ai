import streamlit as st
from openai import OpenAI

client = OpenAI()
MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = """
Jesteś autonomicznym agentem AI.Udajesz trenera fitnes. Wypytujesz użytkownika o wiek, wagę i inne parametry potrzebne do stworzenia, diety i planu treningowego.Pytasz go również o cel,np wagę docelową.
Powyższe informacje dostajesz jako  CEL użytkownika i realizujesz go krok po kroku.

Zasady:
- Najpierw tworzysz PLAN ćwiczeń z rozpiską dzień po dniu.
- Wykonujesz JEDEN krok naraz
- Po każdym kroku oceniasz, czy cel jest zrealizowany
- Odpowiadasz po polsku
- następnie przygotowujesz dietę na 4 tygodnie
"""

def call_llm(messages):
    response = client.responses.create(
        model=MODEL,
        input=messages
    )
    return response.output_text.strip()

def create_plan(goal):
    return call_llm([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"CEL: {goal}\nStwórz plan treningowy krok po kroku, a nastepnie diete rozpisaną na kilka tygodni"}
    ])

def execute_step(goal, plan, step):
    return call_llm([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"""
CEL:
{goal}

PLAN:
{plan}

WYKONAJ TEN KROK:
{step}
"""}
    ])

def critic(goal, result):
    return call_llm([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"""
CEL:
{goal}

WYNIK:
{result}

Czy cel został zrealizowany?
Odpowiedz tylko: TAK lub NIE.
"""}
    ])

# ===== STREAMLIT UI =====

st.set_page_config(page_title="Autonomiczny Agent AI", page_icon="🤖")
st.title("🤖 Fit Sergio Trener AI")

goal = st.text_area("🎯 Witaj koleżko opowiedz trochę o sobie i jaki jest twój cel treningowy:")

if st.button("🚀 START") and goal:
    st.subheader("🧠 Planowanie")
    plan = create_plan(goal)
    st.code(plan)

    steps = [s for s in plan.split("\n") if s.strip()]

    st.subheader("▶️ Wykonywanie kroków")

    for i, step in enumerate(steps, 1):
        st.markdown(f"### Krok {i}")
        st.markdown(step)

        result = execute_step(goal, plan, step)
        st.success(result)

        decision = critic(goal, result)
        st.info(f"Ocena agenta: {decision}")

        if "TAK" in decision.upper():
            st.balloons()
            st.success("✅ CEL ZREALIZOWANY")
            break
    else:

        st.warning("⚠️ Plan wykonany, ale by osiągnąć cel potrzebne jest twoje zaangażowanie a nie lecenie w ciula")

