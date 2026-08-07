import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# ------------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Foodie Cart",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

CURRENCY = "₹"

# ------------------------------------------------------------------
# MENU CATALOG — each dish has an emoji, an image-search term, a price,
# a small badge/tag, and a rating, so the menu cards can look richer.
# ------------------------------------------------------------------
MENU_CATALOG = {
    "Burger":         {"emoji": "🍔", "search": "Beef Burger",    "price": 149, "tag": "🔥 Popular",      "rating": 4.5},
    "Pizza":          {"emoji": "🍕", "search": "Pizza",          "price": 299, "tag": "👑 Best Seller",  "rating": 4.7},
    "Dosa":           {"emoji": "🥞", "search": "Dosa",           "price": 99,  "tag": "🌱 Veg Special",  "rating": 4.3},
    "Ramen":          {"emoji": "🍜", "search": "Ramen",          "price": 249, "tag": "🍥 Chef's Pick",  "rating": 4.6},
    "Fried Chicken":  {"emoji": "🍗", "search": "Fried Chicken",  "price": 219, "tag": "🔥 Popular",      "rating": 4.4},
    "Sushi":          {"emoji": "🍣", "search": "Sushi",          "price": 349, "tag": "✨ Premium",      "rating": 4.8},
    "Butter Chicken": {"emoji": "🍛", "search": "Butter Chicken", "price": 279, "tag": "👑 Best Seller",  "rating": 4.9},
    "Tacos":          {"emoji": "🌮", "search": "Tacos",          "price": 189, "tag": "🌶️ Spicy",        "rating": 4.2},
    "Pasta":          {"emoji": "🍝", "search": "Pasta",          "price": 229, "tag": "🧀 Creamy",       "rating": 4.5},
    "Ice Cream":      {"emoji": "🍨", "search": "Ice Cream",      "price": 89,  "tag": "❄️ Cool Treat",   "rating": 4.6},
}

DEFAULT_CUSTOM_PRICE = 150
FALLBACK_COLORS = ["#4f6ef7", "#7b5cff", "#ff6b6b", "#3fbf8f", "#ff9f45", "#3fa5c9"]

# Manually verified photo overrides for dishes the recipe API doesn't reliably
# cover — stable, direct Wikimedia Commons links so the photo always matches.
MANUAL_IMAGE_OVERRIDES = {
    "Burger": "https://commons.wikimedia.org/wiki/Special:FilePath/Hamburger_sandwich.jpg",
    "Dosa": "https://commons.wikimedia.org/wiki/Special:FilePath/Masala_Dosa_(Bengaluru).JPG",
    "Butter Chicken": "https://commons.wikimedia.org/wiki/Special:FilePath/Chicken_makhani.jpg",
}


@st.cache_data(show_spinner=False, ttl=3600)
def fetch_dish_photo(search_term: str):
    try:
        resp = requests.get(
            "https://www.themealdb.com/api/json/v1/1/search.php",
            params={"s": search_term},
            timeout=4,
        )
        data = resp.json()
        meals = data.get("meals")
        if meals:
            return meals[0]["strMealThumb"]
    except Exception:
        pass
    return None


def get_photo_url(item):
    if item in MANUAL_IMAGE_OVERRIDES:
        return MANUAL_IMAGE_OVERRIDES[item]
    search_term = MENU_CATALOG.get(item, {}).get("search", item)
    return fetch_dish_photo(search_term)


def emoji_for(item):
    return MENU_CATALOG.get(item, {}).get("emoji", "🍽️")


def color_for(item):
    return FALLBACK_COLORS[abs(hash(item)) % len(FALLBACK_COLORS)]


def price_for(item):
    if item in MENU_CATALOG:
        return MENU_CATALOG[item]["price"]
    return st.session_state.get("custom_prices", {}).get(item, DEFAULT_CUSTOM_PRICE)


def dish_image_html(item, height=150, radius="16px 16px 0 0"):
    url = get_photo_url(item)
    if url:
        return f'<img src="{url}" style="width:100%;height:{height}px;object-fit:cover;border-radius:{radius};">'
    color = color_for(item)
    return (
        f'<div style="width:100%;height:{height}px;border-radius:{radius};'
        f'background:{color};display:flex;align-items:center;justify-content:center;font-size:2.6rem;">'
        f'{emoji_for(item)}</div>'
    )


def dish_thumb_html(item, size=52):
    url = get_photo_url(item)
    if url:
        return f'<img src="{url}" style="width:{size}px;height:{size}px;object-fit:cover;border-radius:8px;">'
    color = color_for(item)
    return (
        f'<div style="width:{size}px;height:{size}px;border-radius:8px;background:{color};'
        f'display:flex;align-items:center;justify-content:center;font-size:1.4rem;">{emoji_for(item)}</div>'
    )


def stars_html(rating):
    full = int(rating)
    half = (rating - full) >= 0.5
    stars = "★" * full + ("½" if half else "")
    return f'<span style="color:#ffb400;font-size:.85rem;">{stars}</span> <span style="color:#7b8194;font-size:.8rem;">{rating}</span>'


# ------------------------------------------------------------------
# THEME
# ------------------------------------------------------------------
st.markdown("""
<style>
    .stApp { background: #eef1f8 !important; color: #1e2233 !important; }
    section[data-testid="stSidebar"] { background: #e3e8f5 !important; }
    .stApp h1, .stApp h2, .stApp h3, .stApp h4,
    .stApp p, .stApp span, .stApp label, .stApp li,
    .stApp [data-testid="stMarkdownContainer"],
    .stApp [data-testid="stMarkdownContainer"] *,
    .stApp [data-testid="stWidgetLabel"] p,
    .stApp [data-testid="stCaptionContainer"],
    section[data-testid="stSidebar"] * {
        color: #1e2233 !important;
    }
    .stApp input, .stApp textarea, .stApp select {
        color: #1e2233 !important;
        background: white !important;
    }
    .hero {
        background: linear-gradient(120deg, #4f6ef7 0%, #7b5cff 100%);
        border-radius: 18px;
        padding: 1.8rem 2.2rem;
        margin-bottom: 1.6rem;
    }
    .hero h1, .hero p { color: white !important; margin: 0; }
    .hero p { margin-top: .3rem; opacity: .9; }
    .stat-pill {
        background: white;
        border: 1px solid #d7ddf0;
        border-radius: 14px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 2px 10px rgba(60,70,140,0.08);
    }
    .stat-pill .num { font-size: 1.7rem; font-weight: 700; color: #4f6ef7 !important; }
    .stat-pill .lbl { color: #5b6178 !important; font-size: .85rem; }

    /* ---- Fancy menu card ---- */
    .menu-card {
        position: relative;
        background: white;
        border-radius: 18px;
        overflow: hidden;
        margin-bottom: 1.1rem;
        box-shadow: 0 6px 18px rgba(60,70,140,0.12);
        border: 1px solid #e3e8f5;
        transition: transform .18s ease, box-shadow .18s ease;
    }
    .menu-card:hover { transform: translateY(-5px); box-shadow: 0 12px 26px rgba(79,110,247,0.25); }
    .menu-card-img-wrap { position: relative; }
    .menu-card-img-wrap img { width: 100%; height: 160px; object-fit: cover; display: block; }
    .menu-card-tag {
        position: absolute; top: 10px; left: 10px;
        background: rgba(30,34,51,0.75);
        color: white !important;
        font-size: .72rem; font-weight: 600;
        padding: .25rem .6rem; border-radius: 20px;
        backdrop-filter: blur(2px);
    }
    .menu-card-price {
        position: absolute; bottom: -14px; right: 12px;
        background: linear-gradient(120deg, #4f6ef7, #7b5cff);
        color: white !important;
        font-weight: 700; font-size: .95rem;
        padding: .35rem .8rem; border-radius: 14px;
        box-shadow: 0 4px 10px rgba(79,110,247,0.4);
    }
    .menu-card-body { padding: 1.2rem .9rem .8rem .9rem; }
    .menu-card-title { font-weight: 700; font-size: 1.08rem; color: #1e2233 !important; margin-bottom: .15rem; }

    .cart-row {
        display: flex;
        align-items: center;
        gap: .9rem;
        background: white;
        border: 1px solid #d7ddf0;
        border-radius: 12px;
        padding: .5rem .9rem;
        margin-bottom: .5rem;
        box-shadow: 0 2px 8px rgba(60,70,140,0.06);
    }
    .qty-badge {
        background: #4f6ef7; color: white !important; font-weight: 700; font-size: .8rem;
        border-radius: 20px; padding: .15rem .6rem; min-width: 28px; text-align: center;
    }
    .total-banner {
        background: linear-gradient(120deg, #1e2233, #343a5c);
        color: white !important;
        border-radius: 14px;
        padding: 1rem 1.3rem;
        display: flex; justify-content: space-between; align-items: center;
        margin-top: .8rem;
    }
    .total-banner * { color: white !important; }
    .total-banner .amt { font-size: 1.5rem; font-weight: 800; }

    div.stButton > button {
        border-radius: 10px; font-weight: 600;
        border: 1px solid #4f6ef7; background: white !important; color: #4f6ef7 !important;
    }
    div.stButton > button:hover { background: #4f6ef7 !important; color: white !important; }
    .sidebar-photo { border-radius: 14px; overflow: hidden; margin-bottom: 1rem; border: 1px solid #d7ddf0; }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# STATE
# ------------------------------------------------------------------
if "items" not in st.session_state:
    st.session_state["items"] = {"Burger": 1, "Pizza": 1, "Dosa": 1}
if "history" not in st.session_state:
    st.session_state["history"] = []
if "custom_prices" not in st.session_state:
    st.session_state["custom_prices"] = {}


def log_action(action, item, qty=1):
    st.session_state["history"].append(
        {"time": datetime.now().strftime("%H:%M:%S"), "action": action, "item": item, "qty": qty}
    )


def add_qty(item, qty):
    st.session_state["items"][item] = st.session_state["items"].get(item, 0) + qty
    log_action("Added", item, qty)


def remove_one(item):
    if item in st.session_state["items"]:
        st.session_state["items"][item] -= 1
        log_action("Removed 1", item, 1)
        if st.session_state["items"][item] <= 0:
            del st.session_state["items"][item]


def remove_all(item):
    if item in st.session_state["items"]:
        qty = st.session_state["items"].pop(item)
        log_action("Removed", item, qty)


def total_qty():
    return sum(st.session_state["items"].values())


def order_total():
    return sum(price_for(item) * qty for item, qty in st.session_state["items"].items())


# ------------------------------------------------------------------
# HERO
# ------------------------------------------------------------------
st.markdown("""
<div class="hero">
    <h1>🍽️ Foodie Cart</h1>
    <p>Browse dishes with real photos and prices, set your own quantities, and build your order.</p>
</div>
""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="stat-pill"><div class="num">{total_qty()}</div><div class="lbl">Total Quantity</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="stat-pill"><div class="num">{len(st.session_state["items"])}</div><div class="lbl">Unique Dishes</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="stat-pill"><div class="num">{CURRENCY}{order_total()}</div><div class="lbl">Order Total</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="stat-pill"><div class="num">{len(st.session_state["history"])}</div><div class="lbl">Actions Logged</div></div>', unsafe_allow_html=True)

st.write("")

# ------------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------------
if st.session_state["items"]:
    latest = list(st.session_state["items"].keys())[-1]
    st.sidebar.markdown(
        f'<div class="sidebar-photo">{dish_image_html(latest, height=150, radius="14px")}</div>',
        unsafe_allow_html=True,
    )
    st.sidebar.caption(f"Latest addition: {latest}")

st.sidebar.title("📋 Menu")
menu = st.sidebar.radio(
    "Choose an action",
    ["Browse & Add", "My Order", "Remove Item", "Search Item", "Count Items", "Order History", "Clear List"],
    label_visibility="collapsed",
)
st.sidebar.markdown("---")
st.sidebar.caption("Built with Streamlit ✨")

# ------------------------------------------------------------------
# PAGES
# ------------------------------------------------------------------

def browse_and_add():
    st.subheader("🧑‍🍳 Browse the Menu")
    cols = st.columns(3)
    for i, (item, info) in enumerate(MENU_CATALOG.items()):
        with cols[i % 3]:
            in_cart = st.session_state["items"].get(item, 0)
            cart_note = f"🛒 {in_cart} in cart" if in_cart else "Not in cart yet"
            st.markdown(f"""
            <div class="menu-card">
                <div class="menu-card-img-wrap">
                    {dish_image_html(item, height=160, radius="18px 18px 0 0")}
                    <span class="menu-card-tag">{info['tag']}</span>
                    <span class="menu-card-price">{CURRENCY}{info['price']}</span>
                </div>
                <div class="menu-card-body">
                    <div class="menu-card-title">{info['emoji']} {item}</div>
                    {stars_html(info['rating'])}
                    <div style="margin-top:.35rem;color:#7b8194;font-size:.78rem;">{cart_note}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            qcol, bcol = st.columns([1, 2])
            with qcol:
                qty = st.number_input(
                    "Qty", min_value=1, max_value=20, value=1, step=1,
                    key=f"qty_{item}", label_visibility="collapsed",
                )
            with bcol:
                if st.button(f"＋ Add · {CURRENCY}{info['price'] * qty}", key=f"add_{item}", use_container_width=True):
                    add_qty(item, int(qty))
                    st.success(f"Added {qty} × {item} ({CURRENCY}{info['price'] * qty})")
                    st.rerun()

    st.markdown("---")
    st.caption("Don't see your dish? Add a custom item and set its price:")
    ccol1, ccol2, ccol3, ccol4 = st.columns([2.5, 1, 1, 1.5])
    with ccol1:
        custom = st.text_input("Custom dish name", label_visibility="collapsed", placeholder="e.g. Momos")
    with ccol2:
        custom_qty = st.number_input("Qty", min_value=1, max_value=20, value=1, step=1, key="custom_qty", label_visibility="collapsed")
    with ccol3:
        custom_price = st.number_input(f"Price ({CURRENCY})", min_value=1, max_value=5000, value=DEFAULT_CUSTOM_PRICE, step=10, key="custom_price", label_visibility="collapsed")
    with ccol4:
        if st.button("＋ Add Custom Item", use_container_width=True) and custom.strip():
            name = custom.strip().title()
            st.session_state["custom_prices"][name] = int(custom_price)
            add_qty(name, int(custom_qty))
            st.success(f"Added {custom_qty} × {name} ({CURRENCY}{custom_price} each)")
            st.rerun()


def my_order():
    st.subheader("🧾 My Order")
    if st.session_state["items"]:
        for item, qty in st.session_state["items"].items():
            unit_price = price_for(item)
            row = st.columns([0.6, 2.4, 1.1, 0.8, 0.8, 0.8, 1.2])
            with row[0]:
                st.markdown(dish_thumb_html(item), unsafe_allow_html=True)
            with row[1]:
                st.markdown(f"**{emoji_for(item)} {item}**")
            with row[2]:
                st.caption(f"{CURRENCY}{unit_price} each")
            with row[3]:
                if st.button("−", key=f"minus_{item}"):
                    remove_one(item)
                    st.rerun()
            with row[4]:
                st.markdown(f"<div style='text-align:center;font-weight:700;padding-top:6px;'>{qty}</div>", unsafe_allow_html=True)
            with row[5]:
                if st.button("＋", key=f"plus_{item}"):
                    add_qty(item, 1)
                    st.rerun()
            with row[6]:
                st.markdown(f"<div style='text-align:right;font-weight:700;padding-top:6px;'>{CURRENCY}{unit_price * qty}</div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="total-banner">
            <div>Total ({total_qty()} items)</div>
            <div class="amt">{CURRENCY}{order_total()}</div>
        </div>
        """, unsafe_allow_html=True)

        df = pd.DataFrame([
            {"Item": k, "Quantity": v, "Unit Price": price_for(k), "Subtotal": price_for(k) * v}
            for k, v in st.session_state["items"].items()
        ])
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Order as CSV", csv, "order.csv", "text/csv")
    else:
        st.info("Your order is empty — head to **Browse & Add** to pick some dishes.")


def remove_item():
    st.subheader("🗑️ Remove an Item")
    if st.session_state["items"]:
        item_to_remove = st.selectbox(
            "Select an item to remove:",
            list(st.session_state["items"].keys()),
            format_func=lambda x: f"{emoji_for(x)} {x} (x{st.session_state['items'][x]})",
        )
        st.markdown(dish_image_html(item_to_remove, height=200, radius="14px"), unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Remove 1"):
                remove_one(item_to_remove)
                st.success(f"Removed 1 × {item_to_remove}.")
                st.rerun()
        with col2:
            if st.button("Remove All of This Item"):
                remove_all(item_to_remove)
                st.success(f"Removed all {item_to_remove} from your order.")
                st.rerun()
    else:
        st.info("Your list is empty.")


def search_item():
    st.subheader("🔍 Search for a Dish")
    search = st.text_input("Search for a food item:")
    if st.button("Search") and search.strip():
        matches = [i for i in st.session_state["items"] if search.strip().lower() in i.lower()]
        if matches:
            st.success(f"Found {len(matches)} match(es):")
            for m in matches:
                st.markdown(f"""
                <div class="cart-row">
                    {dish_thumb_html(m)}
                    <div style="flex:1;"><b>{emoji_for(m)} {m}</b></div>
                    <span class="qty-badge">x{st.session_state['items'][m]}</span>
                    <div style="font-weight:700;">{CURRENCY}{price_for(m) * st.session_state['items'][m]}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning(f"'{search}' isn't present in your list.")


def count_items():
    st.subheader("🔢 Item Count")
    st.write(f"Total quantity across all items: **{total_qty()}**")
    st.write(f"Unique dishes: **{len(st.session_state['items'])}**")
    st.write(f"Order total: **{CURRENCY}{order_total()}**")
    if st.session_state["items"]:
        counts = pd.Series(st.session_state["items"])
        st.bar_chart(counts)


def order_history():
    st.subheader("🕒 Order History")
    if st.session_state["history"]:
        st.table(pd.DataFrame(st.session_state["history"])[::-1])
    else:
        st.info("No actions logged yet.")


def clear_list():
    st.subheader("🧹 Clear List")
    st.warning("This will remove all items from your current order.")
    if st.button("Confirm Clear List"):
        st.session_state["items"].clear()
        log_action("Cleared", "All items", 0)
        st.success("Your list has been cleared.")
        st.rerun()


# ------------------------------------------------------------------
# ROUTING
# ------------------------------------------------------------------
if menu == "Browse & Add":
    browse_and_add()
elif menu == "My Order":
    my_order()
elif menu == "Remove Item":
    remove_item()
elif menu == "Search Item":
    search_item()
elif menu == "Count Items":
    count_items()
elif menu == "Order History":
    order_history()
elif menu == "Clear List":
    clear_list()

st.write("---")
st.caption(f"Current List: {st.session_state['items']}")