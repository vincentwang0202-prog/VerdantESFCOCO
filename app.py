import streamlit as st
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

st.set_page_config(page_title="Verdant", page_icon="🍃")

MAX_PER_DAY = 3
HK_TZ = ZoneInfo("Asia/Hong_Kong")

SEED = {"name": "Seed", "emoji": "🌰", "min_kg": 0, "image": "images/stage1.png"}
SPROUT = {"name": "Sprout", "emoji": "🌱", "min_kg": 1, "image": "images/stage2.png"}
SAPLING = {"name": "Sapling", "emoji": "🌿", "min_kg": 5, "image": "images/stage3.png"}
TREE = {"name": "Tree", "emoji": "🌳", "min_kg": 15, "image": "images/stage4.png"}
VERDANT = {"name": "Verdant", "emoji": "🍃", "min_kg": 30, "image": "images/stage5.png"}

FULL_TREE_KG = VERDANT["min_kg"]

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


def totalkgget(actions):
    total = 0
    for a in actions:
        total = total + a["kg"]
    return round(total, 2)

def currenttreestage(kg):
    if kg >= VERDANT["min_kg"]:
        return VERDANT
    elif kg >= TREE["min_kg"]:
        return TREE
    elif kg >= SAPLING["min_kg"]:
        return SAPLING
    elif kg >= SPROUT["min_kg"]:
        return SPROUT
    else:
        return SEED

def countodayaction(actions, act_id):
    count = 0
    for a in actions:
        if a["way"] == act_id and a["date"] == today.isoformat():
            count += 1
    return count

def streakcalc(actions):
    dates = []
    for a in actions:
        dates.append(a["date"])

    day = today
    if day.isoformat() not in dates:
        day = day - timedelta(days=1)

    streak = 0
    while day.isoformat() in dates:
        streak += 1
        day = day - timedelta(days=1)
    return streak

def actionclickhandling(user, way, kg, emoji):
    user_actions = players[user]
    if countodayaction(user_actions, way) >= MAX_PER_DAY:
        return

    prev_kg = totalkgget(user_actions)
    user_actions.append({"way": way, "kg": kg, "date": today.isoformat()})
    st.toast(f"+{kg} kg carbon dioxide saved! {emoji}")

    new_kg = totalkgget(user_actions)
    if int(new_kg // FULL_TREE_KG) > int(prev_kg // FULL_TREE_KG):
        st.balloons()
        st.toast("You grew a whole Verdant tree! A new seed has been planted.")
    elif currenttreestage(new_kg % FULL_TREE_KG)["name"] != currenttreestage(prev_kg % FULL_TREE_KG)["name"]:
        st.balloons()
        new_stage = currenttreestage(new_kg % FULL_TREE_KG)
        st.toast(f"Level up! Your tree is now a {new_stage['name']} {new_stage['emoji']}")


st.title("🍃 Verdant")
st.write("Grow your tree by saving carbon dioxide in Hong Kong every action helps.")

community_total = 0
for name in players:
    community_total = community_total + totalkgget(players[name])
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

if nickname not in players:
    players[nickname] = []
user_actions = players[nickname]

total_saved = totalkgget(user_actions)
completed_trees = int(total_saved // FULL_TREE_KG)
current_cycle_kg = total_saved % FULL_TREE_KG

current_stage = currenttreestage(current_cycle_kg)
if current_cycle_kg < SPROUT["min_kg"]:
    next_stage = SPROUT
elif current_cycle_kg < SAPLING["min_kg"]:
    next_stage = SAPLING
elif current_cycle_kg < TREE["min_kg"]:
    next_stage = TREE
elif current_cycle_kg < VERDANT["min_kg"]:
    next_stage = VERDANT
else:
    next_stage = None

if completed_trees:
    st.success(f"**Your forest:** {VERDANT['emoji'] * completed_trees} ({completed_trees} trees)")

st.subheader(f"Your tree: {current_stage['name']}")

try:
    st.image(current_stage["image"], width=250)
except:
    st.header(current_stage["emoji"])

st.metric("Carbon dioxide saved", f"{total_saved:.2f} kg")

if next_stage:
    kg_needed = next_stage["min_kg"] - current_cycle_kg
    progress_val = (current_cycle_kg - current_stage["min_kg"]) / (next_stage["min_kg"] - current_stage["min_kg"])
    st.progress(progress_val, text=f"{kg_needed:.2f} kg remaining until {next_stage['emoji']} {next_stage['name']}")

streak = streakcalc(user_actions)
c1, c2 = st.columns(2)
c1.metric("Current streak", f"🔥 {streak} days")
c2.info(f"**Daily Tip:** {TIPS[today.day % len(TIPS)]}")

st.subheader("What green action did you do today?")

# each button typed out, col1 is left and col2 is right
col1, col2 = st.columns(2)

col1.button(
    "🚇 MTR instead of taxi (+0.8 kg)",
    key="btn_mtr",
    on_click=actionclickhandling,
    args=(nickname, "mtr", 0.8, "🚇"),
    disabled=countodayaction(user_actions, "mtr") >= MAX_PER_DAY,
    use_container_width=True,
)
col2.button(
    "🚶 Walked instead of taking minibus (+1.0 kg)",
    key="btn_walk",
    on_click=actionclickhandling,
    args=(nickname, "walk", 1.0, "🚶"),
    disabled=countodayaction(user_actions, "walk") >= MAX_PER_DAY,
    use_container_width=True,
)
col1.button(
    "❄️ Aircon set to 25°C (+0.8 kg)",
    key="btn_aircon",
    on_click=actionclickhandling,
    args=(nickname, "aircon", 0.8, "❄️"),
    disabled=countodayaction(user_actions, "aircon") >= MAX_PER_DAY,
    use_container_width=True,
)
col2.button(
    "🥤 Brought reusable cup (+1.0 kg)",
    key="btn_cup",
    on_click=actionclickhandling,
    args=(nickname, "cup", 1.0, "🥤"),
    disabled=countodayaction(user_actions, "cup") >= MAX_PER_DAY,
    use_container_width=True,
)
col1.button(
    "🍱 Declined takeaway box/cutlery (+0.05 kg)",
    key="btn_takeaway",
    on_click=actionclickhandling,
    args=(nickname, "takeaway", 0.05, "🍱"),
    disabled=countodayaction(user_actions, "takeaway") >= MAX_PER_DAY,
    use_container_width=True,
)
col2.button(
    "🥬 Ate a meat-free meal (+1.5 kg)",
    key="btn_veggie",
    on_click=actionclickhandling,
    args=(nickname, "veggie", 1.5, "🥬"),
    disabled=countodayaction(user_actions, "veggie") >= MAX_PER_DAY,
    use_container_width=True,
)
col1.button(
    "💡 Switched off unused lights (+0.1 kg)",
    key="btn_lights",
    on_click=actionclickhandling,
    args=(nickname, "lights", 0.1, "💡"),
    disabled=countodayaction(user_actions, "lights") >= MAX_PER_DAY,
    use_container_width=True,
)
col2.button(
    "👕 Air-dried clothes (+0.9 kg)",
    key="btn_dryer",
    on_click=actionclickhandling,
    args=(nickname, "dryer", 0.9, "👕"),
    disabled=countodayaction(user_actions, "dryer") >= MAX_PER_DAY,
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

action_options = [
    "🚇 MTR instead of taxi",
    "🚶 Walked instead of taking minibus",
    "❄️ Aircon set to 25°C",
    "🥤 Brought reusable cup",
    "🍱 Declined takeaway box/cutlery",
    "🥬 Ate a meat-free meal"
    ,"💡 Switched off unused lights",
    "👕 Air-dried clothes",
]

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
        st.success("Post submitted!")

if not wall:
    st.info("ADD A POST!")
else:
    for post in reversed(wall):
        with st.container(border=True):
            st.markdown(f"**{post['nickname']}** · {post['action']} · {post['date']}")
            st.image(post["photo"], width=300)
            st.write(post["caption"])