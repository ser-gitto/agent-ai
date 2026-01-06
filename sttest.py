import streamlit as st
from openai import OpenAI

client = OpenAI()
MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = """
Jesteś autonomicznym agentem AI.
Dostajesz CEL użytkownika i realizujesz go krok po kroku.

Zasady:
- Najpierw tworzysz PLAN
- Wykonujesz JEDEN krok naraz
- Po każdym kroku oceniasz, czy cel jest zrealizowany
- Odpowiadasz po polsku
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
        {"role": "user", "content": f"CEL: {goal}\nStwórz plan krok po kroku."}
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
st.title("🤖 Autonomiczny Agent AI")

goal = st.text_area("🎯 Podaj cel dla agenta:")

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
        st.warning("⚠️ Plan wykonany, ale cel może być niepełny")