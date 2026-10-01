import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import streamlit as st

st.set_page_config(page_title="Verdant", page_icon="🍃")

MAX_PER_DAY = 3
HK_TZ = ZoneInfo("Asia/Hong_Kong")

DATAPARTS = [
    {"way": "mtr", "emoji": "🚇", "words": "MTR instead of taxi", "kg": 0.8},
    {"way": "walk", "emoji": "🚶", "words": "Walked instead of taking minibus", "kg": 1.0},
    {"way": "aircon", "emoji": "❄️", "words": "Aircon set to 25°C", "kg": 0.8},
    {"way": "cup", "emoji": "🥤", "words": "Brought reusable cup", "kg": 1.0},
    {"way": "takeaway", "emoji": "🍱", "words": "Declined takeaway box/cutlery", "kg": 0.05},
    {"way": "veggie", "emoji": "🥬", "words": "Ate a meat-free meal", "kg": 1.5},
    {"way": "lights", "emoji": "💡", "words": "Switched off unused lights", "kg": 0.1},
    {"way": "dryer", "emoji": "👕", "words": "Air-dried clothes", "kg": 0.9},
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
    "Ordering takeaway ask for no cutlery to save plastic",
    "25.5°C + a fan is fine trust",
    "Take the MTR or bus taxi expensive ",
    "If it's close just walk",
    "Skip the dryer and just hang your clothes out",
    "Keep a water bottle in your bag so you don't need to buy bottled water",
    "Close the curtains on hot days so the room stays cooler",
]

if "players" not in st.session_state:
    st.session_state.players = {}

if "wall" not in st.session_state:
    st.session_state.wall = []

players = st.session_state.players
wall = st.session_state.wall
today = datetime.now(HK_TZ).date()


def totalkgkg(actions):
    return round(sum(a["kg"] for a in actions), 2)


def currenttstage(kg):
    for stage in reversed(TREE_STAGES):
        if kg >= stage["min_kg"]:
            return stage
    return TREE_STAGES[0]


def countdayaction(actions, act_id):
    today_str = today.isoformat()
    return sum(1 for a in actions if a["way"] == act_id and a["date"] == today_str)


def streakcalc(actions):
    logged_dates = {a["date"] for a in actions}
    check_day = today

    if check_day.isoformat() not in logged_dates:
        check_day -= timedelta(days=1)

    streak = 0
    while check_day.isoformat() in logged_dates:
        streak += 1
        check_day -= timedelta(days=1)
    return streak


def actclickhandling(user, action):
    user_actions = players[user]
    if countdayaction(user_actions, action["way"]) >= MAX_PER_DAY:
        return

    prev_kg = totalkgkg(user_actions)
    user_actions.append({"way": action["way"], "kg": action["kg"], "date": today.isoformat()})
    
    st.toast(f"+{action['kg']} kg carbon dioxide saved! {action['emoji']}")

    new_kg = totalkgkg(user_actions)
    if int(new_kg // FULL_TREE_KG) > int(prev_kg // FULL_TREE_KG):
        st.balloons()
        st.toast(" You grew a whole Verdant tree! A new seed has been planted.")
    elif currenttstage(new_kg % FULL_TREE_KG)["name"] != currenttstage(prev_kg % FULL_TREE_KG)["name"]:
        st.balloons()
        new_stage = currenttstage(new_kg % FULL_TREE_KG)
        st.toast(f"Level up! Your tree is now a {new_stage['name']} {new_stage['emoji']}")


st.title("🍃 Verdant")
st.write("Grow your tree by saving carbon dioxide in Hong Kong every action helps.")

community_total = sum(totalkgkg(acts) for acts in players.values())
st.metric("Hong Kong total carbon dioxide saved", f"{community_total:.1f} kg carbon dioxide", border=True)

nickname = st.text_input(
    "Your nickname",
    max_chars=15,
    placeholder="something like vincent67",
    help="use the same nickname to log back in.",
).strip().lower()

if not nickname:
    st.info("Enter a nickname to plant your seed.")
    st.stop()

if len(nickname) < 3:
    st.warning("Nicknames must be at least 3 characters.")
    st.stop()

user_actions = players.setdefault(nickname, [])

total_saved = totalkgkg(user_actions)
completed_trees = int(total_saved // FULL_TREE_KG)
current_cycle_kg = total_saved % FULL_TREE_KG

current_stage = currenttstage(current_cycle_kg)
next_stage = next((s for s in TREE_STAGES if s["min_kg"] > current_cycle_kg), None)

if completed_trees:
    st.success(f"**Your forest:** {TREE_STAGES[-1]['emoji'] * completed_trees} ({completed_trees} trees)")

st.subheader(f"Your tree: {current_stage['name']}")

if os.path.exists(current_stage["image"]):
    st.image(current_stage["image"], width=250)
else:
    st.markdown(f"<h1 style='text-align: center; font-size: 80px;'>{current_stage['emoji']}</h1>", unsafe_allow_html=True)

st.metric("Carbon dioxide saved", f"{total_saved:.2f} kg")

if next_stage:
    kg_needed = next_stage["min_kg"] - current_cycle_kg
    progress_val = (current_cycle_kg - current_stage["min_kg"]) / (next_stage["min_kg"] - current_stage["min_kg"])
    st.progress(progress_val, text=f"{kg_needed:.2f} kg remaining until {next_stage['emoji']} {next_stage['name']}")

streak = streakcalc(user_actions)
c1, c2 = st.columns(2)
c1.metric("Current streak", f"🔥 {streak} day" if streak == 1 else f"🔥 {streak} days")
c2.info(f"**Daily Tip:** {TIPS[today.toordinal() % len(TIPS)]}")

st.subheader("What green action did you do today?")

grid = st.columns(2)
for idx, action in enumerate(DATAPARTS):
    reached_limit = countdayaction(user_actions, action["way"]) >= MAX_PER_DAY
    suffix = f" (+{action['kg']} kg)"

    grid[idx % 2].button(
        f"{action['emoji']} {action['words']}{suffix}",
        key=f"btn_{action['way']}",
        on_click=actclickhandling,
        args=(nickname, action),
        disabled=reached_limit,
        use_container_width=True,
    )

with st.expander("Sources"):
    st.markdown("**🚇 MTR instead of taxi**\n\nAccording to a Hong Kong Polytechnic University study, the MTR emitted about 55g carbon dioxide equivalent per passenger-km in 2017, vs about 137g for a private car.")
    st.markdown("**🚶 Walked instead of taking minibus**\n\nAccording to Wikipedia's comparison of transport emissions in Europe, a bus emits about 68g carbon dioxide per passenger-km. Walking emits none.")
    st.markdown("**❄️ Aircon set to 25°C**\n\nAccording to the CLP Power website, raising the aircon by 1°C saves about 3% energy.")
    st.markdown("**🥤 Brought reusable cup**\n\nAccording to the Scottish Government website, one single-use paper cup is about 17g carbon dioxide equivalent.")
    st.markdown("**🍱 Declined takeaway box/cutlery**\n\nAccording to the Zero Waste Scotland website, one single-use polystyrene takeaway box is about 51g carbon dioxide equivalent.")
    st.markdown("**🥬 Ate a meat-free meal**\n\nAccording to a study of Portuguese meals published on Springer, meat dishes average about 4.8kg carbon dioxide equivalent per serving vs about 0.7kg for vegetarian ones.")
    st.markdown("**💡 Switched off unused lights**\n\nAccording to the CLP Power website, its electricity was about 0.38kg carbon dioxide equivalent per kWh in 2024, so turning off 100W for 3h (0.3kWh) saves about 0.11kg.")
    st.markdown("**👕 Air-dried clothes**\n\nAccording to a study on ScienceDirect, an electric dryer uses about 2.42kWh per load. At CLP's 0.38kg per kWh, that's about 0.92kg carbon dioxide equivalent.")
    st.caption("Electricity calculation standard: CLP Power carbon intensity benchmark (~0.38 kg carbon dioxide/kWh).")

st.divider()

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