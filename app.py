import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import streamlit as st

st.set_page_config(page_title="Verdant", page_icon="🍃")

# DEMO PLAYER for the hackathon: typing the nickname "demo" gives a tree that
# already has 29.5 kg, so the judges can watch a whole tree finish with ONE tap.
# It is labelled on the page and NOT counted in the Hong Kong total (it's not real).
DEMO_NAME = "demo"
DEMO_START_KG = 29.5


# Shared mock DB using Streamlit cache
@st.cache_resource
def load_db():
    return {DEMO_NAME: [{"id": "demo-start", "kg": DEMO_START_KG, "date": "2026-09-01"}]}

players = load_db()


# GREEN WALL memory: one shared list of posts for everyone (newest at the end).
# It works just like load_db(), but it's a list instead of a dictionary.
@st.cache_resource
def load_wall():
    return []


wall = load_wall()
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

# NEW: when a tree reaches the LAST stage it is finished. It goes into your
# forest and a new seed is planted. [-1] means "the last thing in the list".
FULL_TREE_KG = TREE_STAGES[-1]["min_kg"]   # = 30

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


# NEW: add up all the kg in a list of actions.
# round(..., 2) stops computer decimal weirdness (29.9999999) from
# stopping a tree from finishing.
def total_kg(action_list):
    total = 0
    for a in action_list:
        total = total + a["kg"]
    return round(total, 2)


# NEW: find the biggest stage this many kg has reached.
def get_stage(kg):
    stage = TREE_STAGES[0]
    for s in TREE_STAGES:
        if kg >= s["min_kg"]:
            stage = s
    return stage


def add_action(user, action):
    user_actions = players[user]
    cur_today = datetime.now(hk_tz).date()

    if count_today_action(user_actions, action["id"], cur_today) >= MAX_PER_DAY:
        return

    # NEW: remember how things were BEFORE the new action...
    kg_before = total_kg(user_actions)

    user_actions.append({"id": action["id"], "kg": action["kg"], "date": cur_today.isoformat()})
    st.toast(f"+{action['kg']} kg CO₂ saved! {action['emoji']}")

    # NEW: ...then compare with AFTER. Did something grow? Celebrate! 🎉
    # //  = how many WHOLE trees fit in.   % = the leftover for the current tree.
    kg_after = total_kg(user_actions)
    trees_before = int(kg_before // FULL_TREE_KG)
    trees_after = int(kg_after // FULL_TREE_KG)
    stage_before = get_stage(kg_before % FULL_TREE_KG)
    stage_after = get_stage(kg_after % FULL_TREE_KG)

    if trees_after > trees_before:
        st.balloons()
        st.toast("🍃 You grew a whole Verdant tree! It's in your forest now, and a new seed is planted.")
    elif stage_after["name"] != stage_before["name"]:
        st.balloons()
        st.toast(f"🎉 Level up! Your tree is now a {stage_after['name']} {stage_after['emoji']}")


# Main UI
st.title("🍃 Verdant")
st.write("Grow your own Verdant tree by saving CO₂ in Hong Kong. Every green thing you do makes it grow!")

# Add up everybody EXCEPT the demo player (its head start isn't real data)
community_total = 0
for name, user_acts in players.items():
    if name != DEMO_NAME:
        community_total = community_total + total_kg(user_acts)
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

if nickname == DEMO_NAME:
    st.caption(f"🎬 Demo player: starts with {DEMO_START_KG} kg so you can watch a tree finish. "
               "Not counted in the Hong Kong total.")
my_kg = total_kg(my_actions)              # everything you have EVER saved
trees = int(my_kg // FULL_TREE_KG)         # NEW: how many whole trees that grew
kg_now = my_kg % FULL_TREE_KG              # NEW: the leftover, growing your CURRENT tree

# Find current and upcoming tree stage (using kg_now, not my_kg)
stage = get_stage(kg_now)
upcoming = next((s for s in TREE_STAGES if s["min_kg"] > kg_now), None)

# NEW: your forest, one 🍃 for every finished tree.
# "🍃" * 3 makes "🍃🍃🍃" (you can multiply text in Python!)
if trees > 0:
    st.success(f"**Your forest:** {TREE_STAGES[-1]['emoji'] * trees} ({trees} grown)")

st.subheader(f"Your tree: {stage['name']}")

if os.path.exists(stage["image"]):
    st.image(stage["image"], width=250)
else:
    st.markdown(
        f"<p style='font-size: 120px; text-align: center; margin: 0'>{stage['emoji']}</p>",
        unsafe_allow_html=True,
    )

st.metric("CO₂ you have saved", f"{my_kg:.2f} kg")

# CHANGED: a finished tree goes to the forest, so the current tree
# always has a next stage. Use kg_now instead of my_kg.
kg_left = upcoming["min_kg"] - kg_now
progress_val = (kg_now - stage["min_kg"]) / (upcoming["min_kg"] - stage["min_kg"])
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


# ---------------------------------------------------------------
# GREEN WALL: share a photo of something green you did
# ---------------------------------------------------------------
st.divider()
st.subheader("📸 Green Wall")
st.caption("Share a photo of something green you did! "
           "Photos of THINGS only: no faces, names, school uniforms or addresses.")

# The choices for the dropdown, e.g. "🚇 MTR instead of a taxi"
choices = []
for action in ACTIONS:
    choices.append(f"{action['emoji']} {action['label']}")

# A form waits until you press the button before anything happens.
# clear_on_submit=True empties the boxes after posting.
with st.form("new_post", clear_on_submit=True):
    photo = st.file_uploader("Your photo", type=["jpg", "jpeg", "png"], max_upload_size=5)
    chosen = st.selectbox("What did you do?", choices)
    caption = st.text_input("Caption", max_chars=100, placeholder="e.g. Took the MTR to school today!")
    posted = st.form_submit_button("Post to the wall 🌿")

if posted:
    if photo is None:
        st.warning("Please add a photo first 📷")
    elif caption.strip() == "":
        st.warning("Please write a short caption ✍️")
    else:
        wall.append({
            "nickname": nickname,
            "action": chosen,
            "caption": caption.strip(),
            "photo": photo.getvalue(),   # the picture itself, stored in memory
            "date": today.isoformat(),
        })
        # Only keep the newest 20 posts, so the server doesn't run out of memory
        if len(wall) > 20:
            wall.pop(0)   # pop(0) removes the OLDEST post (the first one)
        st.success("Posted! 🎉")

if len(wall) == 0:
    st.info("No posts yet. Be the first! 🌱")

# reversed() goes through the list backwards, so the NEWEST post shows first
for post in reversed(wall):
    with st.container(border=True):
        st.markdown(f"**{post['nickname']}** · {post['action']} · {post['date']}")
        st.image(post["photo"], width=300)
        st.write(post["caption"])
