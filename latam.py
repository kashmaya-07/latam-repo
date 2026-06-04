import streamlit as st
import pandas as pd

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Ingredient Intelligence System",
    layout="wide"
)

# =====================================================
# TITLE
# =====================================================

st.title("Ingredient Intelligence System")

st.markdown("""
Analyze ingredient usage, company overlaps, product intersections, and ingredient intelligence.
""")

# =====================================================
# LOAD DATA
# =====================================================

@st.cache_data
def load_data():

    df = pd.read_excel("latambook.xlsx")

    # Standardize columns based on your file

    rename_dict = {
        "Ingr": "Ingredient",
        "Market": "Country"
    }

    df = df.rename(columns=rename_dict)

    df.columns = df.columns.str.strip()

    df = df.drop_duplicates()

    for col in df.columns:
        df[col] = df[col].astype(str).str.strip()

    return df


master_df = load_data()

# =====================================================
# VALIDATION
# =====================================================

required_cols = [
    "Ingredient",
    "Product",
    "Company",
    "Brand"
]

missing_cols = [
    col for col in required_cols
    if col not in master_df.columns
]

if missing_cols:
    st.error(f"Missing columns: {missing_cols}")
    st.write(master_df.columns.tolist())
    st.stop()

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.header("Ingredient Filters")

all_ingredients = sorted(
    master_df["Ingredient"]
    .dropna()
    .unique()
)

selected_ingredients = st.sidebar.multiselect(
    "Select Ingredients",
    all_ingredients
)

# =====================================================
# INGREDIENT SUMMARY
# =====================================================

st.header("Ingredient Summary")

ingredient_summary = (
    master_df.groupby("Ingredient")
    .agg({
        "Product": "nunique",
        "Company": "nunique",
        "Brand": "nunique"
    })
    .reset_index()
)

ingredient_summary.columns = [
    "Ingredient",
    "Unique Products",
    "Unique Companies",
    "Unique Brands"
]

ingredient_summary = ingredient_summary.sort_values(
    by="Unique Products",
    ascending=False
)

st.dataframe(
    ingredient_summary,
    use_container_width=True
)

# =====================================================
# SINGLE INGREDIENT ANALYSIS
# =====================================================

if len(selected_ingredients) == 1:

    ingredient = selected_ingredients[0]

    temp = master_df[
        master_df["Ingredient"] == ingredient
    ]

    st.divider()

    st.header(f"{ingredient} Analysis")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Products",
        temp["Product"].nunique()
    )

    c2.metric(
        "Companies",
        temp["Company"].nunique()
    )

    c3.metric(
        "Brands",
        temp["Brand"].nunique()
    )

    # Companies

    st.subheader("Companies Using Ingredient")

    companies_df = pd.DataFrame(
        sorted(
            temp["Company"]
            .dropna()
            .unique()
        ),
        columns=["Company"]
    )

    st.dataframe(
        companies_df,
        use_container_width=True
    )

    # Products

    st.subheader("Products Using Ingredient")

    cols_to_show = [
        col for col in [
            "Product",
            "Brand",
            "Company",
            "Category",
            "Sub-Category",
            "Country"
        ]
        if col in temp.columns
    ]

    st.dataframe(
        temp[cols_to_show]
        .drop_duplicates(),
        use_container_width=True
    )

# =====================================================
# MULTI INGREDIENT INTERSECTION
# =====================================================

st.divider()

st.header("Multi Ingredient Intersection")

if len(selected_ingredients) < 2:

    st.info("Select at least 2 ingredients")

else:

    temp = master_df[
        master_df["Ingredient"]
        .isin(selected_ingredients)
    ]

    # Common Products

    product_counts = (
        temp.groupby("Product")["Ingredient"]
        .nunique()
        .reset_index()
    )

    common_products = product_counts[
        product_counts["Ingredient"]
        == len(selected_ingredients)
    ]

    common_product_names = (
        common_products["Product"]
        .unique()
    )

    # Common Companies

    company_counts = (
        temp.groupby("Company")["Ingredient"]
        .nunique()
        .reset_index()
    )

    common_companies = company_counts[
        company_counts["Ingredient"]
        == len(selected_ingredients)
    ]

    # Metrics

    c1, c2 = st.columns(2)

    c1.metric(
        "Common Products",
        len(common_product_names)
    )

    c2.metric(
        "Common Companies",
        len(common_companies)
    )

    # Companies

    st.subheader("Common Companies")

    st.dataframe(
        common_companies,
        use_container_width=True
    )

    # Products

    st.subheader("Common Products")

    common_product_details = temp[
        temp["Product"]
        .isin(common_product_names)
    ]

    cols_to_show = [
        col for col in [
            "Product",
            "Brand",
            "Company",
            "Category",
            "Sub-Category",
            "Country",
            "Ingredient"
        ]
        if col in common_product_details.columns
    ]

    st.dataframe(
        common_product_details[
            cols_to_show
        ].drop_duplicates(),
        use_container_width=True
    )

# =====================================================
# COMPANY → INGREDIENTS USED
# =====================================================

st.divider()

st.header("Company → Ingredients Used")

company_ingr = (
    master_df.groupby("Company")["Ingredient"]
    .unique()
    .reset_index()
)

company_ingr["Ingredient Count"] = (
    company_ingr["Ingredient"]
    .apply(len)
)

company_ingr["Ingredients Used"] = (
    company_ingr["Ingredient"]
    .apply(
        lambda x: ", ".join(sorted(x))
    )
)

company_ingr = company_ingr.drop(
    columns="Ingredient"
)

st.dataframe(
    company_ingr,
    use_container_width=True
)

# =====================================================
# TOP COMPANIES
# =====================================================

st.divider()

st.header("Top Companies")

top_companies = (
    master_df.groupby("Company")
    .agg({
        "Product": "nunique",
        "Ingredient": "nunique"
    })
    .reset_index()
)

top_companies.columns = [
    "Company",
    "Products",
    "Ingredients"
]

top_companies = top_companies.sort_values(
    by="Ingredients",
    ascending=False
)

st.dataframe(
    top_companies,
    use_container_width=True
)

# =====================================================
# DOWNLOAD
# =====================================================

st.divider()

csv = ingredient_summary.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    "Download Ingredient Summary",
    csv,
    "ingredient_summary.csv",
    "text/csv"
)