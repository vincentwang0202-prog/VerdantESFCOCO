import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import streamlit as st

st.set_page_config(page_title="Verdant", page_icon="🍃")

# Configuration & Constants
DEMO_NAME = "demo"
DEMO_START_KG = 29.5
MAX_PER_DAY = 3
HK_TZ = ZoneInfo("Asia/Hong_Kong")

DATAPARTS = [
    {
        "way": "mtr",
        "emoji": "🚇",
        "words": "MTR instead of taxi",
        "kg": 0.8,
        "source": "PolyU MTR study: ~55g CO₂ taking MTR vs 137g driving for the same distance.",
    },
    {
        "way": "walk",
        "emoji": "🚶",
        "words": "Walked instead of taking minibus",
        "kg": 1.0,
        "source": "Zero emission transport mode.",
    },
    {
        "way": "aircon",
        "emoji": "❄️",
        "words": "Aircon set to 25°C",
        "kg": 0.8,
        "source": "HK Electric / CLP: Raising aircon by 1°C saves ~3% electricity.",
    },
    {
        "way": "cup",
        "emoji": "🥤",
        "words": "Brought reusable cup",
        "kg": 1.0,
        "source": "UNEP: Single-use cups average 17-37g CO₂e per unit.",
    },
    {
        "way": "takeaway",
        "emoji": "🍱",
        "words": "Declined takeaway box/cutlery",
        "kg": 0.05,
        "source": "Avoids single-use plastic production footprint (~50g CO₂).",
    },
    {
        "way": "veggie",
        "emoji": "🥬",
        "words": "Ate a meat-free meal",
        "kg": 1.5,
        "source": "Meat-free meals save between 1.5kg–3kg CO₂e compared to meat.",
    },
    {
        "way": "lights",
        "emoji": "💡",
        "words": "Switched off unused lights",
        "kg": 0.1,
        "source": "Turning off 100W for 3h saves ~0.3kWh (~0.11kg CO₂).",
    },
    {
        "way": "dryer",
        "emoji": "👕",
        "words": "Air-dried clothes",
        "kg": 0.9,
        "source": "Skipping dryer cycle saves ~0.95kg CO₂.",
    },
]

TREE_STAGES = [
    {"name": "Seed", "emoji": "🌰", "min_kg": 0, "image": "images/stage1.png"},
    {"name": "Sprout", "emoji": "🌱", "min_kg": 1, "image": "images/stage2.png"},
    {"name": "Sapling", "emoji": "🌿", "min_kg": 5, "image": "images/stage3.png"},
    {"name": "Tree", "emoji": "🌳", "min_kg": 15, "image": "images/stage4.png"},
    {"name": "Verdant", "emoji": "🍃", "min_kg": 30, "image": "images/stage5.png"},
]

FULL_TREE_KG = TREE_STAGES[-1]["min_kg"]

TIPS = [
    "Ordering food to go? Just say 走餐具 (no cutlery) to skip extra plastic.",
    "Grab your travel mug before hitting the cha chaan teng for milk tea.",
    "Set air-con to 25.5°C and run a fan—it feels just as cool with less power.",
    "Hop on the MTR, tram, or bus instead of grabbing a cab.",
    "Short trip? Walk it instead—you might spot cool local shops along the way.",
    "Try going meat-free once a week. Plenty of dim sum choices are vegetarian.",
    "Flick the TV switch off at the wall so it isn't sipping standby power.",
    "Skip the tumble dryer and let the Hong Kong breeze dry your clothes.",
    "Keep a refillable bottle in your bag so you don't need bottled water.",
    "Only going up a floor or two? Take the stairs and skip the lift queue.",
    "Pull the blinds during hot afternoons to block sunlight heat gain.",
    "Rinse plastic bottles before dropping them at a GREEN@COMMUNITY station.",
]

# Initialize session storage
if "players" not in st.session_state:
    st.session_state.players = {
        DEMO_NAME: [{"way": "demo-start", "kg": DEMO_START_KG, "date": "2026-09-01"}]
    }

if "wall" not in st.session_state:
    st.session_state.wall = []

players = st.session_state.players
wall = st.session_state.wall
today = datetime.now(HK_TZ).date()


# State & Calculation Helpers
def get_total_kg(actions):
    return round(sum(a["kg"] for a in actions), 2)


def get_current_stage(kg):
    for stage in reversed(TREE_STAGES):
        if kg >= stage["min_kg"]:
            return stage
    return TREE_STAGES[0]


def count_today_actions(actions, act_id):
    today_str = today.isoformat()
    return sum(1 for a in actions if a["way"] == act_id and a["date"] == today_str)


def calculate_streak(actions):
    logged_dates = {a["date"] for a in actions}
    check_day = today

    if check_day.isoformat() not in logged_dates:
        check_day -= timedelta(days=1)

    streak = 0
    while check_day.isoformat() in logged_dates:
        streak += 1
        check_day -= timedelta(days=1)
    return streak


def handle_action_click(user, action):
    user_actions = players[user]
    if count_today_actions(user_actions, action["way"]) >= MAX_PER_DAY:
        return

    prev_kg = get_total_kg(user_actions)
    user_actions.append({"way": action["way"], "kg": action["kg"], "date": today.isoformat()})
    
    st.toast(f"+{action['kg']} kg CO₂ saved! {action['emoji']}")

    new_kg = get_total_kg(user_actions)
    if int(new_kg // FULL_TREE_KG) > int(prev_kg // FULL_TREE_KG):
        st.balloons()
        st.toast(" You grew a whole Verdant tree! A new seed has been planted.")
    elif get_current_stage(new_kg % FULL_TREE_KG)["name"] != get_current_stage(prev_kg % FULL_TREE_KG)["name"]:
        st.balloons()
        new_stage = get_current_stage(new_kg % FULL_TREE_KG)
        st.toast(f"Level up! Your tree is now a {new_stage['name']} {new_stage['emoji']}")


# Main App UI
st.title("🍃 Verdant")
st.write("Grow your tree by saving CO₂ in Hong Kong. Every green habit helps!")

community_total = sum(get_total_kg(acts) for name, acts in players.items() if name != DEMO_NAME)
st.metric("Hong Kong total CO₂ saved", f"{community_total:.1f} kg CO₂", border=True)

nickname = st.text_input(
    "Your nickname",
    max_chars=15,
    placeholder="e.g. dimsumhero",
    help="Use the same nickname to log back in.",
).strip().lower()

if not nickname:
    st.info("Enter a nickname to plant your seed.")
    st.stop()

if len(nickname) < 3:
    st.warning("Nicknames must be at least 3 characters.")
    st.stop()

user_actions = players.setdefault(nickname, [])

if nickname == DEMO_NAME:
    st.caption(f"Demo account (starts at {DEMO_START_KG} kg). Excluded from community total.")

total_saved = get_total_kg(user_actions)
completed_trees = int(total_saved // FULL_TREE_KG)
current_cycle_kg = total_saved % FULL_TREE_KG

current_stage = get_current_stage(current_cycle_kg)
next_stage = next((s for s in TREE_STAGES if s["min_kg"] > current_cycle_kg), None)

if completed_trees:
    st.success(f"**Your forest:** {TREE_STAGES[-1]['emoji'] * completed_trees} ({completed_trees} trees)")

st.subheader(f"Your tree: {current_stage['name']}")

if os.path.exists(current_stage["image"]):
    st.image(current_stage["image"], width=250)
else:
    st.markdown(f"<h1 style='text-align: center; font-size: 80px;'>{current_stage['emoji']}</h1>", unsafe_allow_html=True)

st.metric("CO₂ saved", f"{total_saved:.2f} kg")

if next_stage:
    kg_needed = next_stage["min_kg"] - current_cycle_kg
    progress_val = (current_cycle_kg - current_stage["min_kg"]) / (next_stage["min_kg"] - current_stage["min_kg"])
    st.progress(progress_val, text=f"{kg_needed:.2f} kg remaining until {next_stage['emoji']} {next_stage['name']}")

streak = calculate_streak(user_actions)
c1, c2 = st.columns(2)
c1.metric("Current streak", f"🔥 {streak} day" if streak == 1 else f"🔥 {streak} days")
c2.info(f"**Daily Tip:** {TIPS[today.toordinal() % len(TIPS)]}")

st.subheader("What green action did you take today?")

grid = st.columns(2)
for idx, action in enumerate(DATAPARTS):
    reached_limit = count_today_actions(user_actions, action["way"]) >= MAX_PER_DAY
    suffix = " (maxed)" if reached_limit else f" (+{action['kg']} kg)"

    grid[idx % 2].button(
        f"{action['emoji']} {action['words']}{suffix}",
        key=f"btn_{action['way']}",
        on_click=handle_action_click,
        args=(nickname, action),
        disabled=reached_limit,
        use_container_width=True,
    )

with st.expander("Where do these numbers come from?"):
    for action in DATAPARTS:
        st.markdown(f"**{action['emoji']} {action['words']}: {action['kg']} kg**\n\n{action['source']}")
    st.caption("Electricity calculation standard: CLP Power carbon intensity benchmark (~0.38 kg CO₂/kWh).")

st.divider()

# Community Photo Wall
st.subheader("Green Wall")
st.caption("Share a photo of your green habit! Photos of items/activities only.")

action_options = [f"{item['emoji']} {item['words']}" for item in DATAPARTS]

with st.form("new_post", clear_on_submit=True):
    photo = st.file_uploader("Upload photo", type=["jpg", "jpeg", "png"])
    selected_action = st.selectbox("Action taken", action_options)
    caption_text = st.text_input("Caption", max_chars=100, placeholder="e.g. Took MTR to work today")
    submitted = st.form_submit_button("Post to wall")

if submitted:
    if not photo:
        st.warning("Please upload a photo.")
    elif not caption_text.strip():
        st.warning("Please add a caption.")
    else:
        wall.append({
            "nickname": nickname,
            "action": selected_action,
            "caption": caption_text.strip(),
            "photo": photo.getvalue(),
            "date": today.isoformat(),
        })
        if len(wall) > 20:
            wall.pop(0)
        st.success("Post submitted!")

if not wall:
    st.info("No posts yet. Be the first!")
else:
    for post in reversed(wall):
        with st.container(border=True):
            st.markdown(f"**{post['nickname']}** · {post['action']} · {post['date']}")
            st.image(post["photo"], width=300)
            st.write(post["caption"])