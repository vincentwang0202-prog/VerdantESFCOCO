import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import streamlit as st

st.set_page_config(page_title="Verdant", page_icon="🍃")

# --- Constants & State Setup ---
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
        "source": "PolyU MTR study: A passenger produces ~55g CO₂ taking MTR vs 137g driving a car for the same distance.",
    },
    {
        "way": "walk",
        "emoji": "🚶",
        "words": "Walked instead of taking the minibus",
        "kg": 1.0,
        "source": "Zero emission transport mode.",
    },
    {
        "way": "aircon",
        "emoji": "❄️",
        "words": "Aircon set to 25°C",
        "kg": 0.8,
        "source": "HK Electric & CLP guidelines: Raising aircon temperature by 1°C saves ~3% electricity consumption.",
    },
    {
        "way": "cup",
        "emoji": "🥤",
        "words": "Brought reusable cup",
        "kg": 1.0,
        "source": "UNEP reports single-use cup production averages 17-37g CO₂e per unit vs reusable alternatives over long lifespan.",
    },
    {
        "way": "takeaway",
        "emoji": "🍱",
        "words": "Declined takeaway box/cutlery",
        "kg": 0.05,
        "source": "Avoided single-use takeaway plastic manufacturing footprint (~50g CO₂ saved per set).",
    },
    {
        "way": "veggie",
        "emoji": "🥬",
        "words": "Ate a meat-free meal",
        "kg": 1.5,
        "source": "Food carbon footprint studies: Replacing beef/pork meal with vegetarian meal saves 1.5kg-3kg CO₂e.",
    },
    {
        "way": "lights",
        "emoji": "💡",
        "words": "Switched off unused lights",
        "kg": 0.1,
        "source": "Turning off ~100W lighting load for 3 hours saves 0.3kWh (~0.11kg CO₂ based on local grid factor).",
    },
    {
        "way": "dryer",
        "emoji": "👕",
        "words": "Air-dried clothes",
        "kg": 0.9,
        "source": "Avoiding average 2.5kWh dryer cycle saves approx 0.95kg CO₂ (CLP power ratio).",
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
    "Ordering food to go? Just say 走餐具 (no cutlery) to skip the extra plastic.",
    "Grab your travel mug before hitting the cha chaan teng for your milk tea fix.",
    "Set your air-con to 25.5 °C and run a fan—it feels just as cool but uses way less power.",
    "Hop on the MTR, tram, or bus instead of grabbing a cab when heading out.",
    "Got a short trip? Walk it instead—you might spot cool local shops along the way.",
    "Try going meat-free once a week. Tons of local dim sum options are vegetarian.",
    "Flick the TV switch off at the wall so it isn't sipping standby power.",
    "Skip the tumble dryer and let the Hong Kong breeze dry your clothes.",
    "Keep a refillable bottle in your bag so you don't need single-use plastic bottles.",
    "Only going up a floor or two? Take the stairs and skip the lift queue.",
    "Pull the blinds during hot afternoons to block sunlight heat gain.",
    "Give plastic bottles a quick rinse before dropping them at a GREEN@COMMUNITY station.",
]


@st.cache_resource
def get_players():
    return {DEMO_NAME: [{"way": "demo-start", "kg": DEMO_START_KG, "date": "2026-09-01"}]}


@st.cache_resource
def get_wall():
    return []


players = get_players()
wall = get_wall()
today = datetime.now(HK_TZ).date()


# --- Helper Functions ---
def count_today_actions(action_list, act_id, current_date):
    date_str = current_date.isoformat()
    return sum(1 for item in action_list if item["way"] == act_id and item["date"] == date_str)


def calculate_streak(action_list, current_date):
    logged_dates = {item["date"] for item in action_list}
    check_day = current_date

    if check_day.isoformat() not in logged_dates:
        check_day -= timedelta(days=1)

    streak = 0
    while check_day.isoformat() in logged_dates:
        streak += 1
        check_day -= timedelta(days=1)
    return streak


def get_total_kg(action_list):
    return round(sum(item["kg"] for item in action_list), 2)


def resolve_stage(kg):
    current = TREE_STAGES[0]
    for stage in TREE_STAGES:
        if kg >= stage["min_kg"]:
            current = stage
    return current


def record_action(user, action):
    user_actions = players[user]
    cur_today = datetime.now(HK_TZ).date()

    if count_today_actions(user_actions, action["way"], cur_today) >= MAX_PER_DAY:
        return

    prev_kg = get_total_kg(user_actions)
    user_actions.append({"way": action["way"], "kg": action["kg"], "date": cur_today.isoformat()})
    st.toast(f"+{action['kg']} kg CO₂ saved! {action['emoji']}")

    new_kg = get_total_kg(user_actions)
    prev_trees = int(prev_kg // FULL_TREE_KG)
    new_trees = int(new_kg // FULL_TREE_KG)

    prev_stage = resolve_stage(prev_kg % FULL_TREE_KG)
    new_stage = resolve_stage(new_kg % FULL_TREE_KG)

    if new_trees > prev_trees:
        st.balloons()
        st.toast(" You grew a whole Verdant tree! It's in your forest now, and a new seed is planted.")
    elif new_stage["name"] != prev_stage["name"]:
        st.balloons()
        st.toast(f"Level up! Your tree is now a {new_stage['name']} {new_stage['emoji']}")


# --- Application Layout ---
st.title("🍃 Verdant")
st.write("Grow your own Verdant tree by saving CO₂ in Hong Kong. Every green habit helps it grow!")

community_total = sum(get_total_kg(acts) for name, acts in players.items() if name != DEMO_NAME)
st.metric("Hong Kong total CO₂ saved", f"{community_total:.1f} kg CO₂", border=True)

nickname = st.text_input(
    "Your nickname",
    max_chars=15,
    placeholder="e.g. dimsumhero",
    help="Use the same nickname next time to keep tracking your tree progress.",
).strip().lower()

if not nickname:
    st.info("Enter a nickname to plant your seed.")
    st.stop()

if len(nickname) < 3:
    st.warning("Nicknames must be between 3 and 15 characters.")
    st.stop()

user_actions = players.setdefault(nickname, [])

if nickname == DEMO_NAME:
    st.caption(f"Demo account (starts at {DEMO_START_KG} kg). Excluded from community total.")

total_saved = get_total_kg(user_actions)
completed_trees = int(total_saved // FULL_TREE_KG)
current_cycle_kg = total_saved % FULL_TREE_KG

current_stage = resolve_stage(current_cycle_kg)
next_stage = next((s for s in TREE_STAGES if s["min_kg"] > current_cycle_kg), None)

if completed_trees > 0:
    st.success(f"**Your forest:** {TREE_STAGES[-1]['emoji'] * completed_trees} ({completed_trees} trees)")

st.subheader(f"Your tree: {current_stage['name']}")

if os.path.exists(current_stage["image"]):
    st.image(current_stage["image"], width=250)
else:
    st.markdown(
        f"<p style='font-size: 100px; text-align: center; margin: 0'>{current_stage['emoji']}</p>",
        unsafe_allow_html=True,
    )

st.metric("CO₂ saved", f"{total_saved:.2f} kg")

if next_stage:
    kg_needed = next_stage["min_kg"] - current_cycle_kg
    pct = (current_cycle_kg - current_stage["min_kg"]) / (next_stage["min_kg"] - current_stage["min_kg"])
    st.progress(
        pct,
        text=f"{kg_needed:.2f} kg remaining until {next_stage['emoji']} {next_stage['name']}"
    )

streak = calculate_streak(user_actions, today)
c1, c2 = st.columns(2)
c1.metric("Current streak", f"🔥 {streak} day" if streak == 1 else f"🔥 {streak} days")
c2.info(f"**Daily Tip:** {TIPS[today.toordinal() % len(TIPS)]}")

st.subheader("What green action did you take today?")

cols = st.columns(2)
for idx, action in enumerate(DATAPARTS):
    reached_limit = count_today_actions(user_actions, action["way"], today) >= MAX_PER_DAY
    label_suffix = " (max for today)" if reached_limit else f" (+{action['kg']} kg)"

    cols[idx % 2].button(
        f"{action['emoji']} {action['words']}{label_suffix}",
        key=action["way"],
        on_click=record_action,
        args=(nickname, action),
        disabled=reached_limit,
        width="stretch",
    )

with st.expander("Where do these numbers come from?"):
    for action in DATAPARTS:
        st.markdown(f"**{action['emoji']} {action['words']}: {action['kg']} kg**  \n{action['source']}")
    st.caption("Electricity calculation standard: CLP Power carbon intensity benchmark (~0.38 kg CO₂/kWh).")

st.divider()
st.subheader("Green Wall")
st.caption("Share a photo of your green habit! Photos of items/activities only (no personal info or faces).")

action_options = [f"{item['emoji']} {item['words']}" for item in DATAPARTS]

with st.form("new_post", clear_on_submit=True):
    photo = st.file_uploader("Upload photo", type=["jpg", "jpeg", "png"], max_upload_size=5)
    selected_action = st.selectbox("Action taken", action_options)
    caption_text = st.text_input("Caption", max_chars=100, placeholder="e.g. Took MTR to work today")
    submitted = st.form_submit_button("Post to wall")

if submitted:
    if photo is None:
        st.warning("Please select an image file.")
    elif not caption_text.strip():
        st.warning("Please add a short caption.")
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
    st.info("No posts yet. Be the first to post!")

for post in reversed(wall):
    with st.container(border=True):
        st.markdown(f"**{post['nickname']}** · {post['action']} · {post['date']}")
        st.image(post["photo"], width=300)
        st.write(post["caption"])