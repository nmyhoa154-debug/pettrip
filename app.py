

import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="PetTrip | Du lịch cùng boss",
    page_icon="🐾",
    layout="wide"
)
# ===== GIAO DIỆN =====
st.markdown("""
<style>
.stApp {
    background-color: #FFF9EF;
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1200px;
}
h1, h2, h3 {
    color: #173B57;
}
.pet-hero {
    background: linear-gradient(120deg, #173B57, #285C70);
    padding: 32px;
    border-radius: 20px;
    color: white;
    margin-bottom: 24px;
}
.pet-hero h1 {
    color: #FFFFFF;
    font-size: 42px;
}
.pet-hero p {
    color: #FFF0D8;
    font-size: 17px;
}
.pet-card {
    background: white;
    padding: 20px;
    border-radius: 16px;
    border: 1px solid #F0DCC4;
    margin-bottom: 12px;
}
div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #F0DCC4;
    padding: 16px;
    border-radius: 14px;
}
.stButton > button {
    background-color: #E67E22;
    color: white;
    border: none;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)


# ===== TIÊU ĐỀ =====
col_logo, col_title = st.columns([1, 4])

with col_logo:
    logo_path = Path(__file__).parent / "logo.png.jpg"
    if logo_path.exists():
        st.image(str(logo_path), width=150)

with col_title:
    st.markdown("""
    <div class="pet-hero">
        <h1>PetTrip 🐾</h1>
        <p><b>ĐI ĐÂU CŨNG ĐƯỢC – MIỄN LÀ CÓ BOSS ĐI CÙNG!</b></p>
        <p>Khám phá chỗ ở, quán ăn và những điểm vui chơi
        thân thiện với thú cưng.</p>
    </div>
    """, unsafe_allow_html=True)

# ===== MENU =====
st.sidebar.title("🐾 PETTRIP")
st.sidebar.caption("Người bạn đồng hành của boss")
menu = [
    "🏠 Trang chủ",
    "📍 Khám phá địa điểm",
    "📄 Chi tiết địa điểm",
    "📊 Dữ liệu"
]

if st.session_state.pop("go_detail", False):
    st.session_state["page_nav"] = "📄 Chi tiết địa điểm"

if st.session_state.pop("go_explore", False):
    st.session_state["page_nav"] = "📍 Khám phá địa điểm"

page = st.sidebar.radio(
    "MENU",
    menu,
    key="page_nav"
)



# ===== ĐỌC EXCEL =====
folder = Path(__file__).parent
excel_files = list(folder.glob("*.xlsx"))

if not excel_files:
    st.error(
        "Không tìm thấy file Excel. "
        "Hãy kiểm tra file .xlsx trong thư mục PetTrip."
    )
    st.stop()

file_path = excel_files[0]

try:
    sheets = pd.read_excel(file_path, sheet_name=None)
except Exception as e:
    st.error(f"Không đọc được file Excel: {e}")
    st.stop()

# Gộp dữ liệu các sheet để thống kê
total_rows = sum(len(df) for df in sheets.values())

# ===== TRANG CHỦ =====
if page == "🏠 Trang chủ":
    st.subheader("🐶 Chào mừng đến với PetTrip!")
    st.write(
        "Lên kế hoạch cho những chuyến đi vui vẻ "
        "cùng người bạn bốn chân của bạn."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("📚 Số danh mục", len(sheets))

    with col2:
        st.metric("📍 Tổng số dòng dữ liệu", total_rows)

    with col3:
        st.metric("🐾 Người bạn đồng hành", "PetTrip")

    st.markdown("### ✨ Các danh mục địa điểm")

    cols = st.columns(2)

    for i, (sheet_name, df) in enumerate(sheets.items()):
        with cols[i % 2]:
            st.markdown(
                f"""
                <div class="pet-card">
                    <h3>🐾 {sheet_name}</h3>
                    <p>Hiện có <b>{len(df)}</b> dòng dữ liệu</p>
                </div>
                """,
                unsafe_allow_html=True
            )



# ===== KHÁM PHÁ ĐỊA ĐIỂM =====
elif page == "📍 Khám phá địa điểm":
    st.subheader("📍 Khám phá cùng boss")
    st.write("Tìm địa điểm phù hợp cho chuyến đi tiếp theo!")

    selected_sheet = st.selectbox(
        "Chọn danh mục địa điểm",
        list(sheets.keys())
    )

    df = sheets[selected_sheet].copy()

    # Chuẩn hóa tên cột để tránh lỗi do khoảng trắng
    df.columns = [str(c).strip() for c in df.columns]

    if df.empty:
        st.info("Danh mục này hiện chưa có dữ liệu.")
    else:
        # Tìm cột theo tên
        name_col = next(
            (c for c in df.columns if c.lower() in ["tên", "ten", "name"]),
            df.columns[0]
        )

        city_col = next(
            (c for c in df.columns
             if "thành phố" in c.lower() or "thanh pho" in c.lower()),
            None
        )

        pet_col = next(
            (c for c in df.columns if "petfriendly" in c.lower()),
            None
        )

        # Tìm các cột giá
        price_cols = [
            c for c in df.columns
            if c.lower().startswith("gia") or c.lower().startswith("giá")
        ]

        st.markdown("### 🔎 Bộ lọc địa điểm")

        # Tìm kiếm theo tên hoặc thông tin
        keyword = st.text_input(
            "Tìm kiếm",
            placeholder="Nhập tên, địa chỉ hoặc từ khóa..."
        )

        # Bộ lọc thành phố
        if city_col:
            cities = sorted(
                df[city_col].dropna().astype(str).str.strip().unique().tolist()
            )
            city_options = ["Tất cả thành phố"] + cities

            selected_city = st.selectbox(
                "📍 Thành phố",
                city_options
            )
        else:
            selected_city = "Tất cả thành phố"

        # Bộ lọc thân thiện với thú cưng
        pet_options = ["Tất cả", "Có", "Không"]
        selected_pet = st.selectbox(
            "🐶 Thân thiện với thú cưng",
            pet_options
        ) if pet_col else "Tất cả"

        # Tạo bản dữ liệu đã lọc
        filtered_df = df.copy()

        if keyword.strip():
            mask = filtered_df.astype(str).apply(
                lambda col: col.str.contains(
                    keyword.strip(),
                    case=False,
                    na=False,
                    regex=False
                )
            ).any(axis=1)

            filtered_df = filtered_df[mask]

        if city_col and selected_city != "Tất cả thành phố":
            filtered_df = filtered_df[
                filtered_df[city_col].astype(str).str.strip() == selected_city
            ]

        if pet_col and selected_pet != "Tất cả":
            pet_values = filtered_df[pet_col].astype(str).str.strip().str.lower()

            if selected_pet == "Có":
                filtered_df = filtered_df[
                    pet_values.isin(["có", "co", "yes", "true", "1", "x"])
                ]
            else:
                filtered_df = filtered_df[
                    pet_values.isin(["không", "khong", "no", "false", "0"])
                ]

        st.caption(f"🐾 Tìm thấy {len(filtered_df)} địa điểm")

        if filtered_df.empty:
            st.warning("Không tìm thấy địa điểm phù hợp. Bà thử đổi bộ lọc nha!")
        else:
            # Hiển thị thành các thẻ địa điểm
            cards_per_row = 3
            for start in range(0, len(filtered_df), cards_per_row):
                cols = st.columns(cards_per_row)

                for col, (row_idx, row) in zip(
                    cols,
                    filtered_df.iloc[start:start + cards_per_row].iterrows()
                ):
                    with col:
                        with st.container(border=True):
                            name = row.get(name_col, "Chưa có tên")

                            st.markdown(
                                f"""
                                <div style="
                                    font-size: 23px;
                                    font-weight: 800;
                                    color: #163A5F;
                                    line-height: 1.4;
                                    margin: 8px 0 15px 0;
                                ">
                                    🐾 {name}
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                            # Hiển thị thông tin địa điểm
                            for field in filtered_df.columns:
                                if field == name_col:
                                    continue

                                value = row[field]

                                if pd.notna(value) and str(value).strip():
                                    st.caption(str(field))
                                    st.write(str(value))

                            if st.button(
                                "Xem chi tiết →",
                                key=f"detail_{selected_sheet}_{row_idx}",
                                use_container_width=True
                            ):
                                st.session_state["selected_sheet"] = selected_sheet
                                st.session_state["selected_index"] = row_idx
                                st.session_state["go_detail"] = True
                                st.rerun()

                            
        # ===== BẢN ĐỒ ĐỊA ĐIỂM =====
        st.markdown("### 🗺️ Bản đồ các địa điểm")

        address_col = next(
            (c for c in filtered_df.columns
             if "địa chỉ" in c.lower() or "dia chi" in c.lower()),
            None
        )

        if address_col and city_col:
            map_rows = filtered_df.dropna(subset=[address_col, city_col])

            if not map_rows.empty:
                import urllib.parse

                for _, place in map_rows.iterrows():
                    place_name = str(place[name_col])
                    address = (
                        str(place[address_col]).strip()
                        + ", "
                        + str(place[city_col]).strip()
                    )

                    with st.expander(f"📍 {place_name}"):
                        st.write(address)
                        map_url = (
                            "https://www.google.com/maps/search/?api=1&query="
                            + urllib.parse.quote(address)
                        )
                        st.link_button(
                            "🗺️ Mở trên Google Maps",
                            map_url
                        )
            else:
                st.info("Chưa có địa chỉ để hiển thị bản đồ.")
        else:
            st.info("Không tìm thấy cột địa chỉ hoặc thành phố.")

# ===== CHI TIẾT ĐỊA ĐIỂM =====
elif page == "📄 Chi tiết địa điểm":
    st.subheader("🐾 Chi tiết địa điểm")

    if (
        "selected_sheet" not in st.session_state
        or "selected_index" not in st.session_state
    ):
        st.info("Bà hãy chọn một địa điểm trong mục Khám phá địa điểm nha!")

    else:
        sheet_name = st.session_state["selected_sheet"]
        row_idx = st.session_state["selected_index"]

        source_df = sheets[sheet_name].copy()
        source_df.columns = [str(c).strip() for c in source_df.columns]

        if st.button("← Quay lại khám phá"):
            st.session_state["go_explore"] = True
            st.rerun()
        if row_idx not in source_df.index:
            st.warning("Không tìm thấy thông tin địa điểm.")
        else:
            place = source_df.loc[row_idx]

            name_col = source_df.columns[0]
            place_name = str(place[name_col])

            st.markdown(
                f"""
                <div style="
                    background: linear-gradient(135deg, #163A5F, #285A7D);
                    padding: 28px;
                    border-radius: 16px;
                    color: white;
                    margin-bottom: 20px;
                ">
                    <div style="font-size: 14px;">
                        🐾 PETTRIP · {sheet_name}
                    </div>
                    <div style="
                        font-size: 30px;
                        font-weight: 800;
                        margin-top: 10px;
                    ">
                        {place_name}
                    </div>
                    <div style="margin-top: 8px;">
                        Khám phá cùng boss của bạn!
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown("### ℹ️ Thông tin địa điểm")

            for field in source_df.columns:
                value = place[field]

                if pd.notna(value) and str(value).strip():
                    if field == name_col:
                        continue

                    st.markdown(f"**{field}**")
                    st.write(str(value))

            # Tìm địa chỉ và thành phố
            address_col = next(
                (
                    c for c in source_df.columns
                    if "địa chỉ" in c.lower()
                    or "dia chi" in c.lower()
                ),
                None
            )

            city_col = next(
                (
                    c for c in source_df.columns
                    if "thành phố" in c.lower()
                    or "thanh pho" in c.lower()
                ),
                None
            )

            address_parts = []

            if address_col and pd.notna(place[address_col]):
                address_parts.append(str(place[address_col]).strip())

            if city_col and pd.notna(place[city_col]):
                address_parts.append(str(place[city_col]).strip())

            address = ", ".join(address_parts)

            if address:
                import urllib.parse

                map_url = (
                    "https://www.google.com/maps/search/?api=1&query="
                    + urllib.parse.quote(address)
                )

                st.link_button(
                    "🗺️ Xem trên Google Maps",
                    map_url,
                    use_container_width=True
                )

# ===== DỮ LIỆU =====
elif page == "📊 Dữ liệu":
    st.subheader("📊 Dữ liệu PetTrip")

    # ===== BIỂU ĐỒ THỐNG KÊ =====
    st.markdown("### 📈 Thống kê địa điểm")

    # Thống kê số lượng địa điểm theo danh mục
    category_data = pd.DataFrame({
        "Danh mục": list(sheets.keys()),
        "Số lượng": [len(df) for df in sheets.values()]
    })

    st.markdown("#### 🐾 Số lượng địa điểm theo danh mục")
    st.bar_chart(
        category_data.set_index("Danh mục"),
        y="Số lượng"
    )

    # Gộp dữ liệu thành phố từ các sheet
    city_counts = {}

    for sheet_name, data in sheets.items():
        data = data.copy()
        data.columns = [str(c).strip() for c in data.columns]

        city_col = next(
            (c for c in data.columns
             if c.lower() in ["thành phố", "thanh pho"]),
            None
        )

        if city_col:
            counts = data[city_col].dropna().astype(str).str.strip()
            for city, count in counts.value_counts().items():
                city_counts[city] = city_counts.get(city, 0) + count

    if city_counts:
        city_data = pd.DataFrame({
            "Thành phố": list(city_counts.keys()),
            "Số lượng": list(city_counts.values())
        }).sort_values("Số lượng", ascending=False)

        st.markdown("#### 📍 Địa điểm theo thành phố")
        st.bar_chart(
            city_data.set_index("Thành phố"),
            y="Số lượng"
        )

    for sheet_name, df in sheets.items():
        with st.expander(
            f"🐾 {sheet_name} — {len(df)} dòng dữ liệu"
        ):
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )
