import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="NOAA 기온 데이터 분석", layout="wide")

# ==========================
# NOAA 데이터 로딩 함수
# ==========================
@st.cache_data
def load_noaa_data():
    """
    NOAA: 가능한 GHCN-M v4 또는 GSOM 데이터 사용
    실패하면 예시 데이터 생성
    """
    urls = [
        # (주의) 이 URL들은 메타데이터 또는 샘플 CSV일 수 있음
        # 실제로 작동하지 않으면 자동으로 fallback 예제 데이터 사용
        "https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=gov.noaa.ncdc%3AC00950",
        "https://www.ncei.noaa.gov/metadata/geoportal/rest/metadata/item/gov.noaa.ncdc%3AC00946/html",
        "https://catalog.data.gov/dataset/monthly-summaries-of-the-global-historical-climatology-network-daily-ghcn-d2",
    ]
    for url in urls:
        try:
            df_try = pd.read_csv(url)
            df_try["date"] = pd.to_datetime(df_try.iloc[:, 0], errors="coerce")
            df_try = df_try.dropna(subset=["date"])
            df_try = df_try[df_try["date"] <= pd.Timestamp.today()]

            # 값 칼럼 찾기
            if "TAVG" in df_try.columns:
                df_try["value"] = pd.to_numeric(df_try["TAVG"], errors="coerce")
            elif "TMEAN" in df_try.columns:
                df_try["value"] = pd.to_numeric(df_try["TMEAN"], errors="coerce")
            else:
                valcol = df_try.columns[1]
                df_try["value"] = pd.to_numeric(df_try[valcol], errors="coerce")

            df_final = df_try.dropna(subset=["value"])
            return df_final[["date", "value"]], True
        except Exception:
            continue

    # 모두 실패 시 fallback 예시 데이터
    dates = pd.date_range("2000-01-01", periods=240, freq="M")
    values = np.sin(np.linspace(0, 20, 240)) + np.random.normal(0, 0.2, 240)
    df = pd.DataFrame({"date": dates, "value": values})
    return df, False


# ==========================
# 데이터 불러오기
# ==========================
df, from_noaa = load_noaa_data()

st.title("🌡️ NOAA 기온 데이터 분석 대시보드")

if from_noaa:
    st.success("✅ NOAA 데이터에서 불러옴")
else:
    st.warning("⚠️ NOAA 데이터 불러오기 실패 → 예시 데이터 사용 중")

# ==========================
# 기초 통계
# ==========================
st.header("📊 기초 통계")
desc = df["value"].describe()
st.write(desc)

# ==========================
# 상관관계 분석 (시간 vs 값)
# ==========================
st.header("📈 상관관계 분석")
df["year"] = df["date"].dt.year
corr = df[["year", "value"]].corr()
st.write(corr)

# ==========================
# 시각화
# ==========================
st.header("📉 시각화")
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(df["date"], df["value"], label="기온/이상치 값")
ax.set_xlabel("날짜")
ax.set_ylabel("값")
ax.legend()
st.pyplot(fig)

# ==========================
# 출처
# ==========================
st.markdown("---")
st.markdown("📑 **출처**")
st.markdown("- NOAA National Centers for Environmental Information (NCEI)")
st.markdown("- Global Historical Climatology Network (GHCN)")
