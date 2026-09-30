import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import streamlit as st

st.set_page_config(page_title="Verdant", page_icon="🍃")

DEMO_NAME = "demo"
DEMO_START_KG = 29.5


@st.cache_resource
def load_db():
    return {DEMO_NAME: [{"way": "demo-start", "kg": DEMO_START_KG, "date": "2026-09-01"}]}

players = load_db()


@st.cache_resource
def load_wall():
    return []

wall = load_wall()
hk_tz = ZoneInfo("Asia/Hong_Kong")
today = datetime.now(hk_tz).date()

MAX_PER_DAY = 3

dataparts = [
    {"way": "mtr", "emoji": "🚇", "words": "MTR instead of taxi", "kg": 0.8, "source": "According to PolyU study of MTR data a passenger only produces 55g of Carbon Dioxide while taking a Car produces 137g of Carbon dioxide. Meaning if you took MTR instead of a Car today you would have saved 82g of Carbon dioxide."},
    {"way": "walk", "emoji": "🚶", "words": "Walked instead of taking the minibus", "kg": 1.0, "source": "Walking doesn't create any Carbon dioxide."},
    {"way": "aircon", "emoji": "❄️", "words": "Aircon at 25 degrees celsius", "kg": 0.8, "source": "According to PolyU study of MTR data a passenger only produces 55g of Carbon Dioxide while taking a Car produces 137g of Carbon dioxide. Meaning if you took MTR instead of a Car today you would have saved 82g of Carbon dioxide."},
    {"way": "cup", "emoji": "🥤", "words": "Brought your own cup instead of using a single use one", "kg": 1.0, "source": "According to UN Enviroment cup reports a single use plastic or paper cup usually takes about 17-37 g to manufacture and transport. While a reusable bottle that takes 1000g of CO2 to take you can use 125+ times meaning it's total carbon footprint is 8g per use."},
    {"way": "takeaway", "emoji": "🍱", "words": "No takeaway box or cutlery", "kg": 0.05, "source": "According to waste studies, plastic takeaway boxes and plastic forks take heaps of energy and oil to manufacture in factories just to be thrown away 10 minutes later. Saying no to disposable cutlery stops around 50g of unnecessary carbon dioxide waste!"},
    {"way": "veggie", "emoji": "🥬", "words": "Ate a meat-free meal", "kg": 1.5, "source": "According to food environment research, farm animals like cows and pigs need tons of food, water, and land which creates 3kg to 5kg of carbon dioxide per meal. A tasty vegetarian meal only makes under 1kg, so skipping meat for one meal saves a massive 1.5kg of carbon!"},
    {"way": "lights", "emoji": "💡", "words": "Switched off lights", "kg": 0.1, "source": "According to power company data, leaving light bulbs, gadgets, and TVs turned on when you leave the room wastes electricity from power plants. Turning off 100 watts of stuff for 3 hours stops about 0.1kg of carbon dioxide from being burned into the sky!"},
    {"way": "dryer", "emoji": "👕", "words": "Air-dried my clothes", "kg": 0.9, "source": "According to appliance reports, electric clothes dryers use huge amounts of power (about 2.5 units of electricity per load) to heat up and spin. Hanging your wet clothes on a rack lets the Hong Kong wind dry them for free and saves almost 1kg of carbon!"}
]

tree_stage = [
    {"name": "Seed", "emoji": "🌰", "min_kg": 0, "image": "images/stage1.png"},
    {"name": "Sprout", "emoji": "🌱", "min_kg": 1, "image": "images/stage2.png"},
    {"name": "Sapling", "emoji": "🌿", "min_kg": 5, "image": "images/stage3.png"},
    {"name": "Tree", "emoji": "🌳", "min_kg": 15, "image": "images/stage4.png"},
    {"name": "Verdant", "emoji": "🍃", "min_kg": 30, "image": "images/stage5.png"},
]

FULL_TREE_KG = tree_stage[-1]["min_kg"]

tips = [
    "Ordering food to go? Just say 走餐具 (no cutlery) to skip the extra plastic 🥢",
    "Grab your travel mug before hitting the cha chaan teng for your milk tea fix 🥤",
    "Set your air-con to 25.5 °C and run a fan—it feels just as cool but uses way less power 🌀",
    "Hop on the MTR, tram, or bus instead of grabbing a cab when you're heading out 🚋",
    "Got a short trip? Walk it instead—you might spot some cool local shops along the way 🚶",
    "Try going meat-free once a week. Tons of tasty dim sum dishes are naturally veggie 🥟",
    "Flick the TV switch off at the wall so it isn't secretly sipping power all night 📺",
    "Skip the tumble dryer and let the Hong Kong breeze dry your clothes for free 👕",
    "Keep a refillable bottle in your bag so you don't have to keep buying plastic water 💧",
    "Only going up a floor or two? Take the stairs and beat the lift queue 🪜",
    "Pull the blinds during hot afternoons to stop the sun turning your bedroom into an oven ☀️",
    "Give plastic bottles a quick rinse before tossing them into a GREEN@COMMUNITY bin ♻️",
]


def count_today_action(action_list, act_id, current_date):
    return sum(1 for a in action_list if a["way"] == act_id and a["date"] == current_date.isoformat())


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


def total_kg(action_list):
    return round(sum(a["kg"] for a in action_list), 2)


def get_stage(kg):
    stage = tree_stage[0]
    for s in tree_stage:
        if kg >= s["min_kg"]:
            stage = s
    return stage


def add_action(user, action):
    user_actions = players[user]
    cur_today = datetime.now(hk_tz).date()

    if count_today_action(user_actions, action["way"], cur_today) >= MAX_PER_DAY:
        return

    kg_before = total_kg(user_actions)
    user_actions.append({"way": action["way"], "kg": action["kg"], "date": cur_today.isoformat()})
    st.toast(f"+{action['kg']} kg CO₂ saved! {action['emoji']}")

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

community_total = sum(total_kg(user_acts) for name, user_acts in players.items() if name != DEMO_NAME)
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
    st.caption(f"🎬 Demo player: starts with {DEMO_START_KG} kg so you can watch a tree finish. Not counted in the Hong Kong total.")

my_kg = total_kg(my_actions)
trees = int(my_kg // FULL_TREE_KG)
kg_now = my_kg % FULL_TREE_KG

stage = get_stage(kg_now)
upcoming = next((s for s in tree_stage if s["min_kg"] > kg_now), None)

if trees > 0:
    st.success(f"**Your forest:** {tree_stage[-1]['emoji'] * trees} ({trees} grown)")

st.subheader(f"Your tree: {stage['name']}")

if os.path.exists(stage["image"]):
    st.image(stage["image"], width=250)
else:
    st.markdown(
        f"<p style='font-size: 120px; text-align: center; margin: 0'>{stage['emoji']}</p>",
        unsafe_allow_html=True,
    )

st.metric("CO₂ you have saved", f"{my_kg:.2f} kg")

kg_left = upcoming["min_kg"] - kg_now
progress_val = (kg_now - stage["min_kg"]) / (upcoming["min_kg"] - stage["min_kg"])
st.progress(
    progress_val,
    text=f"{kg_left:.2f} kg more until {upcoming['emoji']} {upcoming['name']}"
)

days = calc_streak(my_actions, today)

left, right = st.columns(2)
left.metric("Your streak", f"🔥 {days} day" if days == 1 else f"🔥 {days} days")
right.info(f"💡 **Tip of the day:** {tips[today.toordinal() % len(tips)]}")

st.subheader("What green thing did you do today?")

cols = st.columns(2)
for idx, action in enumerate(dataparts):
    used_up = count_today_action(my_actions, action["way"], today) >= MAX_PER_DAY
    extra = ": max for today ✅" if used_up else f" (+{action['kg']} kg)"

    cols[idx % 2].button(
        f"{action['emoji']} {action['words']}{extra}",
        key=action["way"],
        on_click=add_action,
        args=(nickname, action),
        disabled=used_up,
        width="stretch",
    )

with st.expander("📚 Where do these numbers come from?"):
    for action in dataparts:
        st.markdown(f"**{action['emoji']} {action['words']}: {action['kg']} kg**  \n{action['source']}")
    st.caption("Electricity numbers use CLP Power's figure: 0.38 kg of CO₂ for every kWh.")


# GREEN WALL
st.divider()
st.subheader("📸 Green Wall")
st.caption("Share a photo of something green you did! Photos of THINGS only: no faces, names, school uniforms or addresses.")

choices = [f"{action['emoji']} {action['words']}" for action in dataparts]

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
            "photo": photo.getvalue(),
            "date": today.isoformat(),
        })
        if len(wall) > 20:
            wall.pop(0)
        st.success("Posted! 🎉")

if len(wall) == 0:
    st.info("No posts yet. Be the first! 🌱")

for post in reversed(wall):
    with st.container(border=True):
        st.markdown(f"**{post['nickname']}** · {post['action']} · {post['date']}")
        st.image(post["photo"], width=300)
        st.write(post["caption"])