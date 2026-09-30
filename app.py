import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import streamlit as st

st.set_page_config(page_title="Verdant", page_icon="🍃")

# Shared mock DB using Streamlit cache
@st.cache_resource
def load_db():
    return {}

players = load_db()
hk_tz = ZoneInfo("Asia/Hong_Kong")
today = datetime.now(hk_tz).date()

MAX_PER_DAY = 3

ACTIONS = [
    {
        
        "id": "mtr",
        "emoji": "🚇",
        "label": "MTR instead of a taxi",
        "kg": 0.8,
        "source": "8 km trip. MTR ≈ 0.055 kg CO₂ per passenger-km vs car ≈ 0.137 "
                  "(To, PolyU study of MTR data). Estimate.",
    },
    {
        "id": "walk",
        "emoji": "🚶",
        "label": "Walked, not a minibus",
        "kg": 0.2,
        "source": "2 km × about 0.1 kg per passenger-km. Buses ≈ 0.08 (same PolyU study); "
                  "minibuses carry fewer people so we guessed a bit higher. ⚠️ Still checking.",
    },
    {
        "id": "aircon",
        "emoji": "❄️",
        "label": "Air-con at 25.5 °C tonight",
        "kg": 0.35,
        "source": "Instead of 22 °C. 1.1 kW air-con × 8 hours = 8.8 kWh. "
                  "CLP says each 1 °C higher saves 3%, so 3.5 °C ≈ 0.92 kWh saved × 0.38 kg per kWh.",
    },
    {
        "id": "cup",
        "emoji": "🥤",
        "label": "Brought my own cup",
        "kg": 0.02,
        "source": "A single-use cup ≈ 17–37 g CO₂, a reusable cup ≈ 8 g per use "
                  "(UN Environment cups report; Scottish Government cup study).",
    },
    {
        "id": "takeaway",
        "emoji": "🍱",
        "label": "No takeaway box or cutlery",
        "kg": 0.05,
        "source": "⚠️ NOT CHECKED YET. This is Vincent's research job!",
    },
    {
        "id": "veggie",
        "emoji": "🥬",
        "label": "Ate a meat-free meal",
        "kg": 1.5,
        "source": "A meat meal ≈ 3–5 kg CO₂, a vegetarian meal ≈ 0.7–1 kg "
                  "(Ernstoff et al. 2019; Portugal meals study 2023). We use a careful 1.5 kg.",
    },
    {
        "id": "lights",
        "emoji": "💡",
        "label": "Switched off lights",
        "kg": 0.1,
        "source": "Lights and devices off when leaving a room. "
                  "About 100 W of things × 3 hours = 0.3 kWh × 0.38 kg per kWh.",
    },
    {
        "id": "dryer",
        "emoji": "👕",
        "label": "Air-dried my clothes",
        "kg": 0.9,
        "source": "A dryer uses about 2.5 kWh per load × 0.38 kg per kWh. ⚠️ Still checking the 2.5.",
    },
]

TREE_STAGES = [
    {"name": "Seed", "emoji": "🌰", "min_kg": 0, "image": "images/stage1.png"},
    {"name": "Sprout", "emoji": "🌱", "min_kg": 1, "image": "images/stage2.png"},
    {"name": "Sapling", "emoji": "🌿", "min_kg": 5, "image": "images/stage3.png"},
    {"name": "Tree", "emoji": "🌳", "min_kg": 15, "image": "images/stage4.png"},
    {"name": "Verdant", "emoji": "🍃", "min_kg": 30, "image": "images/stage5.png"},
]

TIPS = [
    "Ordering takeaway? Say 走餐具 (no cutlery, please) 🥢",
    "Bring your own cup to the cha chaan teng for your milk tea 🥤",
    "Set the air-con to 25.5 °C and turn on a fan too. A fan uses much less electricity 🌀",
    "Take the MTR, tram or bus instead of a taxi 🚋",
    "Short trip? Walk it! You'll discover new shops on the way 🚶",
    "Try one veggie day a week. Lots of dim sum has no meat 🥟",
    "Switch the TV off at the wall, not just with the remote 📺",
    "Hang your clothes to dry instead of using the dryer 👕",
    "Refill your water bottle instead of buying a new one 💧",
    "Going up one or two floors? Take the stairs instead of the lift 🪜",
    "Close the curtains on sunny afternoons so your room stays cooler ☀️",
    "Rinse plastic bottles and recycle them at a GREEN@COMMUNITY point ♻️️",
]


def count_today_action(action_list, act_id, current_date):
    today_str = current_date.isoformat()
    return sum(1 for a in action_list if a["id"] == act_id and a["date"] == today_str)


def calc_streak(action_list, current_date):
    dates = {a["date"] for a in action_list}
    check_day = current_date

    if check_day.isoformat() not in dates:
        check_day -= timedelta(days=1)

    count = 0
    while check_day.isoformat() in dates:
        count += 1
        check_day -= timedelta(days=1)
    return count


def add_action(user, action):
    user_actions = players[user]
    cur_today = datetime.now(hk_tz).date()

    if count_today_action(user_actions, action["id"], cur_today) >= MAX_PER_DAY:
        return

    user_actions.append({"id": action["id"], "kg": action["kg"], "date": cur_today.isoformat()})
    st.toast(f"+{action['kg']} kg CO₂ saved! {action['emoji']}")


# Main UI
st.title("🍃 Verdant")
st.write("Grow your own Verdant tree by saving CO₂ in Hong Kong. Every green thing you do makes it grow!")

community_total = sum(sum(a["kg"] for a in user_acts) for user_acts in players.values())
st.metric("🇭🇰 Hong Kong has saved together", f"{community_total:.1f} kg CO₂", border=True)

nickname = st.text_input(
    "Your nickname",
    max_chars=15,
    placeholder="e.g. dimsumhero",
    help="Don't use your real name! Use the same nickname next time to find your tree again.",
).strip().lower()

if not nickname:
    st.info("Type a nickname to plant your seed 🌰")
    st.stop()

if len(nickname) < 3:
    st.warning("Nicknames need 3 to 15 letters.")
    st.stop()

my_actions = players.setdefault(nickname, [])
my_kg = sum(a["kg"] for a in my_actions)

# Find current and upcoming tree stage
stage = [s for s in TREE_STAGES if my_kg >= s["min_kg"]][-1]
upcoming = next((s for s in TREE_STAGES if s["min_kg"] > my_kg), None)

st.subheader(f"Your tree: {stage['name']}")

if os.path.exists(stage["image"]):
    st.image(stage["image"], width=250)
else:
    st.markdown(
        f"<p style='font-size: 120px; text-align: center; margin: 0'>{stage['emoji']}</p>",
        unsafe_allow_html=True,
    )

st.metric("CO₂ you have saved", f"{my_kg:.2f} kg")

if upcoming is None:
    st.success("Your tree is fully Verdant! 🍃 Amazing work!")
else:
    kg_left = upcoming["min_kg"] - my_kg
    progress_val = (my_kg - stage["min_kg"]) / (upcoming["min_kg"] - stage["min_kg"])
    st.progress(
        progress_val,
        text=f"{kg_left:.2f} kg more until {upcoming['emoji']} {upcoming['name']}"
    )

days = calc_streak(my_actions, today)

left, right = st.columns(2)
left.metric("Your streak", f"🔥 {days} day" if days == 1 else f"🔥 {days} days")
right.info(f"💡 **Tip of the day:** {TIPS[today.toordinal() % len(TIPS)]}")

st.subheader("What green thing did you do today?")

cols = st.columns(2)
for idx, action in enumerate(ACTIONS):
    used_up = count_today_action(my_actions, action["id"], today) >= MAX_PER_DAY
    extra = ": max for today ✅" if used_up else f" (+{action['kg']} kg)"
    
    cols[idx % 2].button(
        f"{action['emoji']} {action['label']}{extra}",
        key=action["id"],
        on_click=add_action,
        args=(nickname, action),
        disabled=used_up,
        width="stretch",
    )

with st.expander("📚 Where do these numbers come from?"):
    for action in ACTIONS:
        st.markdown(f"**{action['emoji']} {action['label']}: {action['kg']} kg**  \n{action['source']}")
    st.caption("Electricity numbers use CLP Power's 2024 figure: 0.38 kg of CO₂ for every kWh.")