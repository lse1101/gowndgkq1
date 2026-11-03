import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="PET 해중합 실험 데이터 분석기",
    page_icon="♻️",
    layout="wide"
)

# Published experimental values transcribed from Table 2 of:
# "Viability of Glycolysis for the Chemical Recycling of Highly Coloured
# and Multi-Layered Actual PET Wastes", Polymers (2023).
# Values are reported BHET yields (%), not PET conversion (%).
DATA = [
    # run, comparison_group, time_h, temp_C, material, pet_g, eg_pet_molar_ratio, catalyst_wt_pct, bhet_yield_pct
    ("1a", "반응 시간·온도·반응물 비율 조건", 8, 196, "PET R-CL (투명 기준 PET)", 30, 7.6, 1.0, 67.1),
    ("2",  "반응 시간·온도·반응물 비율 조건", 8, 196, "PET R-CL (투명 기준 PET)", 30, 7.6, 0.0, 56.8),
    ("3",  "반응 시간·온도·반응물 비율 조건", 1, 165, "PET R-CL (투명 기준 PET)", 30, 7.6, 1.0, 39.4),
    ("4",  "반응 시간·온도·반응물 비율 조건", 1, 180, "PET R-CL (투명 기준 PET)", 30, 7.6, 1.0, 66.1),
    ("5",  "반응 시간·온도·반응물 비율 조건", 1, 196, "PET R-CL (투명 기준 PET)", 30, 3.8, 1.0, 54.9),
    ("6",  "반응 시간·온도·반응물 비율 조건", 1, 196, "PET R-CL (투명 기준 PET)", 30, 5.7, 1.0, 66.1),
    ("1b", "PET 원료 종류 비교 (2 h)", 2, 196, "PET R-CL (투명 기준 PET)", 30, 7.6, 1.0, 67.1),
    ("7",  "PET 원료 종류 비교 (2 h)", 2, 196, "PET C-BL (파란색 폐PET)", 30, 7.6, 1.0, 63.9),
    ("8",  "PET 원료 종류 비교 (2 h)", 2, 196, "PET C-GY (회색 폐PET)", 30, 7.6, 1.0, 67.3),
    ("9",  "PET 원료 종류 비교 (2 h)", 2, 196, "PET C-GN (초록색 폐PET)", 30, 7.6, 1.0, 65.8),
    ("10", "PET 원료 종류 비교 (2 h)", 2, 196, "PET C-WH (흰색 폐PET)", 30, 7.6, 1.0, 61.2),
    ("11", "PET 원료 종류 비교 (2 h)", 2, 196, "PET C-AM (호박색 폐PET)", 30, 7.6, 1.0, 67.5),
    ("12", "PET 원료 종류 비교 (2 h)", 2, 196, "PET M-AM (호박색 다층 PET)", 30, 7.6, 1.0, 57.2),
]

COLUMNS = [
    "실험 번호", "비교 그룹", "반응 시간 (h)", "온도 (°C)",
    "PET 원료", "PET 질량 (g)", "EG/PET 몰비",
    "촉매/PET (wt%)", "BHET 수율 (%)"
]
df = pd.DataFrame(DATA, columns=COLUMNS)

st.title("PET 해중합 실험 데이터 분석기")
st.caption("문헌에 보고된 PET 글리콜리시스 실험값을 탐색하고 조건별 BHET 수율을 비교합니다.")

with st.sidebar:
    st.header("데이터 필터")
    group_options = df["비교 그룹"].unique().tolist()
    selected_groups = st.multiselect(
        "분석할 실험 그룹",
        group_options,
        default=group_options
    )
    temp_range = st.slider(
        "온도 범위 (°C)",
        min_value=int(df["온도 (°C)"].min()),
        max_value=int(df["온도 (°C)"].max()),
        value=(int(df["온도 (°C)"].min()), int(df["온도 (°C)"].max()))
    )
    min_yield, max_yield = st.slider(
        "BHET 수율 범위 (%)",
        min_value=0.0,
        max_value=100.0,
        value=(0.0, 100.0),
        step=1.0
    )

filtered = df[
    df["비교 그룹"].isin(selected_groups)
    & df["온도 (°C)"].between(temp_range[0], temp_range[1])
    & df["BHET 수율 (%)"].between(min_yield, max_yield)
].copy()

if filtered.empty:
    st.warning("선택한 조건에 해당하는 데이터가 없습니다. 필터를 조정해 주세요.")
    st.stop()

m1, m2, m3 = st.columns(3)
m1.metric("표시된 실험 수", f"{len(filtered)}")
m2.metric("표시 데이터의 평균 BHET 수율", f"{filtered['BHET 수율 (%)'].mean():.1f}%")
best_row = filtered.loc[filtered["BHET 수율 (%)"].idxmax()]
m3.metric("표시 데이터 중 최고 수율", f"{best_row['BHET 수율 (%)']:.1f}%")

tab1, tab2, tab3 = st.tabs(["그래프 분석", "실험 데이터", "해석과 한계"])

with tab1:
    st.subheader("실험별 BHET 수율")
    fig_bar = px.bar(
        filtered,
        x="실험 번호",
        y="BHET 수율 (%)",
        color="비교 그룹",
        hover_data=["반응 시간 (h)", "온도 (°C)", "PET 원료",
                    "EG/PET 몰비", "촉매/PET (wt%)"],
        title="문헌 실험별 BHET 수율"
    )
    fig_bar.update_layout(xaxis_title="논문 실험 번호", yaxis_title="BHET 수율 (%)")
    st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader("온도와 BHET 수율")
    temp_group = filtered.groupby(
        ["비교 그룹", "온도 (°C)"], as_index=False
    )["BHET 수율 (%)"].mean()
    fig_temp = px.scatter(
        temp_group,
        x="온도 (°C)",
        y="BHET 수율 (%)",
        color="비교 그룹",
        hover_data=["BHET 수율 (%)"],
        title="온도별 평균 수율 (서로 다른 실험 조건이 섞일 수 있음)"
    )
    st.plotly_chart(fig_temp, use_container_width=True)
    st.info(
        "주의: 온도별 점은 해당 온도의 데이터 평균입니다. "
        "다른 변수까지 동일하게 통제된 실험만 비교한 것이 아닐 수 있으므로, "
        "이 그래프만으로 온도가 수율 차이의 유일한 원인이라고 결론 내리면 안 됩니다."
    )

with tab2:
    st.subheader("선택된 문헌 데이터")
    st.dataframe(filtered, use_container_width=True, hide_index=True)
    csv = filtered.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "현재 데이터 CSV 다운로드",
        data=csv,
        file_name="pet_glycolysis_selected_data.csv",
        mime="text/csv"
    )

with tab3:
    st.subheader("결과를 해석할 때 확인할 점")
    st.markdown(
        """
        **1. 이 앱의 데이터는 무엇을 나타내나?**  
        표에 기재된 값은 PET의 **전환율이 아니라 BHET 수율(%)**입니다.
        BHET는 PET 글리콜리시스에서 얻을 수 있는 단량체성 생성물입니다.

        **2. 수율이 높으면 PET 전환율도 같은 값인가?**  
        아닙니다. PET가 반응해 전환되더라도 모든 생성물이 BHET로 회수되는 것은 아닙니다.
        전환율과 생성물 수율은 서로 다른 지표입니다.

        **3. 변수의 영향은 어떻게 판단해야 하나?**  
        한 변수를 비교하려면 다른 반응 조건이 동일한 실험끼리 비교해야 합니다.
        서로 다른 조건이 함께 바뀐 실험을 비교하면 원인을 하나로 단정할 수 없습니다.

        **4. 이 데이터의 한계는?**  
        이 앱은 논문 표의 일부 실험값을 옮긴 교육용 분석 도구입니다.
        원자료 전체를 포함한 데이터베이스가 아니며, 측정 오차나 반복 실험의 분산을
        모두 제공하지 않습니다. 회귀선이나 최적 조건을 제시하더라도 이를 보편적인
        산업 공정 조건으로 해석해서는 안 됩니다.
        """
    )

st.divider()
st.subheader("자료 출처")
st.markdown(
    """
    **Viability of Glycolysis for the Chemical Recycling of Highly Coloured and Multi-Layered Actual PET Wastes**  
    *Polymers* (2023), Table 2: Glycolysis reactions with reference PET and post-consumer waste PET.  
    [논문 전문 및 표 확인](https://www.mdpi.com/2073-4360/15/20/4196)
    """
)
st.caption(
    "데이터는 논문 Table 2에 보고된 값에서 옮겼습니다. "
    "앱의 시각화와 필터는 해당 표의 데이터를 재구성한 것이며, 새로운 실험을 수행한 결과가 아닙니다."
)
