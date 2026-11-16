# Economics-Informed Machine Learning for Corporate Distress and Shadow Credit Risk Prediction in Emerging Bond Markets (EIML-Distress)

[![Target Journal](https://img.shields.io/badge/Target%20Journal-Expert%20Systems%20with%20Applications%20%7C%20IRFA-blue?style=for-the-badge)](https://www.sciencedirect.com/journal/expert-systems-with-applications)
[![Methodology](https://img.shields.io/badge/Methodology-Theory--Informed%20ML%20%2B%20XAI-green?style=for-the-badge)]()
[![Data](https://img.shields.io/badge/Dataset-10%2C800%20Firm--Years%20(2008--2022)-orange?style=for-the-badge)]()
[![Container](https://img.shields.io/badge/Reproducibility-Docker%20%2B%20Compose-purple?style=for-the-badge)]()

---

## 1. Giới thiệu & Định vị Nghiên cứu (Executive Summary)

Dự án này phát triển một khung phương pháp luận đột phá: **Economics-Informed Machine Learning (EIML)** nhằm giải quyết bài toán dự báo nguy cơ kiệt quệ tài chính (Corporate Financial Distress) và mô hình hóa rủi ro tín dụng ngầm (Shadow Credit Risk) cho thị trường trái phiếu doanh nghiệp mới nổi.

### Khoảng trống nghiên cứu (Research Gap):
1. **Sự giằng co giữa Cổ điển và Hiện đại**: 
   * Các mô hình cổ điển (*Altman Z-score 1968, Ohlson O-score 1980, Logistic Regression*) có tính giải thích cao và tuân thủ các nguyên lý kinh tế học nhưng năng lực dự báo hạn chế trước các mối quan hệ phi tuyến tính phức tạp.
   * Các mô hình Học máy hiện đại (*XGBoost, CatBoost, Deep Learning - Barboza et al., 2017*) đạt độ chính xác cao nhưng hoạt động như một "hộp đen" (black-box) và thường xuyên sinh ra các **"ảo giác phi kinh tế" (Economically Inconsistent Predictions)** — ví dụ: dự báo xác suất vỡ nợ giảm ngay cả khi đòn bẩy ngắn hạn tăng vọt và hệ số thanh toán lãi vay rơi xuống dưới ngưỡng an toàn.
2. **Đóng góp đột phá của đề tài**: 
   * Nhúng trực tiếp các tiên đề tài chính cổ điển vào **hàm mất mát (Loss Function)** và **ràng buộc cấu trúc (Monotonicity Constraints)** của thuật toán Học máy.
   * Mô hình AI vừa học được quy luật phức tạp từ dữ liệu thực tế, vừa bị cưỡng chế toán học để **không bao giờ đưa ra dự báo vi phạm nguyên lý kinh tế**.
   * Đánh giá thực nghiệm trên bộ dữ liệu bảng 15 năm (2008–2022) của 721 doanh nghiệp niêm yết Việt Nam, bao quát trọn vẹn 4 cuộc khủng hoảng lớn (GFC 2008, Nợ xấu 2011–2012, COVID-19 2020–2021, và Khủng hoảng thanh khoản Trái phiếu 2022).

---

## 2. Khung Lý thuyết Cổ điển & Ràng buộc Kinh tế (Theoretical Foundation)

Mô hình kế thừa và chuẩn hóa 4 trụ cột tài chính doanh nghiệp kinh điển:

```
                                  4 TRỤ CỘT TÀI CHÍNH CỔ ĐIỂN
          ┌─────────────────────┬─────────────────────┬─────────────────────┐
          ▼                     ▼                     ▼                     ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   THANH KHOẢN    │  │   ĐÒN BẨY & NỢ   │  │    SINH LỜI      │  │     HIỆU QUẢ     │
│   (Liquidity)    │  │    (Solvency)    │  │  (Profitability) │  │   (Efficiency)   │
├──────────────────┤  ├──────────────────┤  ├──────────────────┤  ├──────────────────┤
│ • Current Ratio  │  │ • Debt / Equity  │  │ • ROA, ROE, ROS  │  │ • Asset Turnover │
│ • Quick Ratio    │  │ • Short / Debt   │  │ • Net Profit     │  │ • Inv. Turnover  │
│ • Cash / Asset   │  │ • ICR (EBIT/Int) │  │ • EBIT / Asset   │  │ • Rec. Turnover  │
│ • WC / Asset     │  │ • Cash-to-Debt   │  │ • Retained Earn. │  │ • Operating Exp  │
└──────────────────┘  └──────────────────┘  └──────────────────┘  └──────────────────┘
```

### Các Tiên đề Kinh tế được mã hóa thành Ràng buộc (Economic Axioms):
* **Tiên đề 1 (Đơn điệu về Đòn bẩy & Chi phí lãi vay)**:
  $$\frac{\partial P(\text{Distress})}{\partial (\text{Shortdebt} / \text{Debt})} \ge 0, \quad \frac{\partial P(\text{Distress})}{\partial (\text{ICR})} \le 0$$
  Khi tỷ trọng nợ ngắn hạn tăng hoặc hệ số bao phủ lãi vay ($ICR$) suy giảm, xác suất kiệt quệ tài chính **bắt buộc không được giảm**.
* **Tiên đề 2 (Ranh giới Kiệt quệ Kép - Altman Boundary)**:
  Nếu một doanh nghiệp đồng thời có:
  $$\text{Working Capital} < 0 \quad \text{và} \quad \text{EBIT} < 0 \quad \text{trong 2 năm liên tiếp}$$
  thì xác suất rủi ro dự báo $\hat{y}$ phải thỏa mãn: $\hat{y} \ge \tau_{\text{threshold}}$.

---

## 3. Phương pháp luận: Mô hình Toán & Kiến trúc Lai (Methodology)

### 3.1. Hàm mất mát Định hướng Kinh tế (Economics-Informed Loss Function)

Với mạng nơ-ron sâu hoặc gradient boosting tùy biến, hàm tối ưu hóa có dạng:

$$\min_{\theta} \mathcal{L}_{\text{total}}(\theta) = \mathcal{L}_{\text{data}}(y, \hat{y}) + \lambda_1 \mathcal{R}_{\text{mono}}(\hat{y}, X) + \lambda_2 \mathcal{R}_{\text{boundary}}(\hat{y}, X) + \gamma \|\theta\|_2^2$$

Trong đó:
* $\mathcal{L}_{\text{data}}(y, \hat{y})$: Focal Loss hoặc Weighted Binary Cross-Entropy (xử lý lệch pha nhãn kiệt quệ tài chính).
* $\mathcal{R}_{\text{mono}}(\hat{y}, X) = \sum_{i} \text{ReLU}\left( -\frac{\partial \hat{y}_i}{\partial \text{Leverage}_i} \right) + \sum_{i} \text{ReLU}\left( \frac{\partial \hat{y}_i}{\partial \text{ICR}_i} \right)$: Phạt thẳng vào gradient nếu xuất hiện chiều dốc vi phạm kinh tế học.
* $\mathcal{R}_{\text{boundary}}(\hat{y}, X) = \sum_{i \in \text{SevereDistress}} \text{ReLU}(\tau - \hat{y}_i)^2$: Cưỡng chế ngưỡng rủi ro tối thiểu cho doanh nghiệp mất khả năng thanh toán.
* $\lambda_1, \lambda_2$: Siêu tham số điều tiết mức độ cưỡng chế lý thuyết.

### 3.2. Hệ thống Mô hình Đối chuẩn (Benchmark Matrix)

1. **Nhóm Cổ điển (Traditional Baselines)**:
   * Altman $Z''$-Score (Hiệu chỉnh cho Emerging Markets).
   * Ohlson $O$-Score.
   * Multivariable Logistic Regression.
2. **Nhóm Học máy Thuần túy (Standard Machine Learning)**:
   * Support Vector Machines (SVM) & Random Forest (kế thừa benchmark của *Barboza et al., 2017*).
   * Unconstrained XGBoost, LightGBM, CatBoost.
3. **Nhóm Đề xuất Đột phá (Proposed EIML Models)**:
   * **Mono-LightGBM / Mono-XGBoost**: Cây quyết định tích hợp ràng buộc đơn điệu toán học (`monotone_constraints`).
   * **EINN (Economics-Informed Neural Network)**: Mạng PyTorch tối ưu trực tiếp trên hàm mất mát phạt lý thuyết.
4. **Tầng Giải thích Học máy (Explainable AI - XAI)**:
   * TreeSHAP & Integrated Gradients để so sánh sự ổn định của các nhân tố quan trọng giữa mô hình Black-box và EIML.

---

## 4. Xử lý Dữ liệu & Xây dựng Nhãn (Data Pipeline)

### 4.1. Đặc tả Tập dữ liệu Gốc
* **Tệp dữ liệu**: `data-financial-0601.xls`
* **Quy mô**: 10.800 dòng $\times$ 31 cột (721 mã doanh nghiệp HOSE & HNX $\times$ 15 năm: 2008–2022).
* **Đặc trưng ngành**: 20 phân ngành theo chuẩn ICB2.

### 4.2. Định nghĩa Nhãn Kiệt quệ Tài chính ($Y$)
Doanh nghiệp được gắn nhãn Kiệt quệ ($Y_{i,t+1} = 1$) tại năm $t+1$ dựa trên thông tin năm $t$ nếu thỏa mãn ít nhất một trong các điều kiện thực nghiệm:
1. **Kiệt quệ Dòng tiền Trả nợ (Bond/Debt Default Proxy)**: Hệ số bảo đảm lãi vay $ICR = \frac{\text{EBIT}}{\text{Interest Expense}} < 1.0$ trong 2 năm liên tiếp.
2. **Kiệt quệ Vốn CSH**: Vốn chủ sở hữu âm ($\text{Equity} < 0$) hoặc Lỗ ròng liên tiếp 2 năm ($\text{NetProfit} < 0$).
3. **Chế tài Thị trường**: Bị HOSE/HNX đưa vào diện tạm ngừng giao dịch / hủy niêm yết do lỗ lũy kế.

### 4.3. Chiến lược Chia tập Dữ liệu Chống Rò rỉ (Purged Time-Series Split)
Để phản ánh đúng bản chất chuỗi thời gian và tránh Look-ahead Bias:
* **Train Set**: 2008 – 2017 (10 năm: huấn luyện nhận diện các chu kỳ 2008, 2011–2012).
* **Validation Set**: 2018 – 2019 (2 năm tiền khủng hoảng COVID-19: tinh chỉnh siêu tham số $\lambda_1, \lambda_2$).
* **Out-of-Time Test Set**: 2020 – 2022 (3 năm: kiểm thử khả năng dự báo xuyên qua cú sốc COVID-19 và Khủng hoảng Trái phiếu 2022).

---

## 5. Cấu trúc Thư mục Dự án (Project Structure)

```
09_PAPER_Q1_BOND/
├── data/
│   ├── raw/                           # Dữ liệu gốc
│   │   └── data-financial-0601.xls
│   └── processed/                     # Dữ liệu đã làm sạch & tạo đặc trưng
│       ├── panel_features.parquet
│       └── train_val_test_splits.pkl
├── configs/
│   └── config.yaml                    # Tham số huấn luyện, ngưỡng phạt lý thuyết
├── src/
│   ├── __init__.py
│   ├── data_loader.py                 # Đọc và chuẩn hóa dữ liệu bảng
│   ├── feature_engineering.py         # Tính Altman Z'', Ohlson O, ICR, 4 trụ cột
│   ├── theory_losses.py               # Hàm Loss tùy biến PyTorch (Monotonicity & Boundary)
│   ├── train_traditional.py           # Huấn luyện Altman, Ohlson, Logistic
│   ├── train_ml_baseline.py           # Huấn luyện Random Forest, XGBoost thuần
│   ├── train_eiml.py                  # Huấn luyện mô hình đề xuất EIML & Mono-Trees
│   ├── evaluation.py                  # Đo lường AUC, F1, Brier Score, Economic Consistency
│   └── explainability.py              # Phân tích TreeSHAP & Trực quan hóa
├── notebooks/
│   ├── 01_eda_and_panel_audit.ipynb   # Khám phá dữ liệu và kiểm tra các chu kỳ khủng hoảng
│   ├── 02_model_benchmarking.ipynb    # So sánh các thế hệ mô hình
│   └── 03_xai_and_policy_insights.ipynb # Biểu đồ SHAP và hàm ý thị trường trái phiếu
├── results/
│   ├── figures/                       # Xuất biểu đồ chất lượng cao (300 DPI cho Paper)
│   ├── tables/                        # Bảng kết quả định dạng LaTeX (.tex)
│   └── models/                        # Checkpoints mô hình đã huấn luyện
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── requirements.txt
├── environment.yml
└── README.md
```

---

## 6. Thiết lập Môi trường & Khởi chạy Container (Environment & Docker)

### Cách 1: Chạy trực tiếp bằng Python Virtualenv

Yêu cầu: **Python 3.10+** (đã kiểm tra trên Python 3.12).

```bash
# 1. Tạo môi trường ảo
python -m venv .venv

# 2. Kích hoạt môi trường (Windows PowerShell)
.venv\Scripts\Activate.ps1

# 3. Cài đặt các gói phụ thuộc
pip install --upgrade pip
pip install -r requirements.txt
```

### Cách 2: Chạy cô lập toàn diện qua Docker Container (Được khuyến nghị cho tính Tái lập Q1)

Dự án cung cấp `Dockerfile` và `docker-compose.yml` cấu hình sẵn đầy đủ môi trường tính toán khoa học (PyTorch, LightGBM, XGBoost, CatBoost, SHAP, JupyterLab):

```bash
# Khởi động container nền (bao gồm cả JupyterLab port 8888)
docker compose -f docker/docker-compose.yml up -d --build

# Kiểm tra log hoạt động
docker compose -f docker/docker-compose.yml logs -f

# Mở JupyterLab trên trình duyệt:
# http://localhost:8888 (Token: eiml_q1_bond)
```

---

## 7. Quy trình Vận hành Thực nghiệm (Execution Workflow)

Chạy pipeline từ đầu đến cuối chỉ với 4 lệnh:

```bash
# Bước 1: Tiền xử lý, lọc nhiễu và trích xuất chỉ số lý thuyết cổ điển
python src/feature_engineering.py --config configs/config.yaml

# Bước 2: Chạy huấn luyện các mô hình Baseline (Altman, Logistic, RF, XGBoost chuẩn)
python src/train_ml_baseline.py

# Bước 3: Huấn luyện mô hình đề xuất EIML (Theory-Informed Learning)
python src/train_eiml.py

# Bước 4: Đánh giá toàn diện & Xuất bảng biểu LaTeX cho bài báo
python src/evaluation.py --export-latex
python src/explainability.py --generate-paper-plots
```

---

## 8. Chỉ số Đánh giá (Evaluation Metrics)

Bài báo sẽ đánh giá mô hình trên 2 bình diện:
1. **Năng lực Dự báo Thống kê (Statistical Predictive Performance)**:
   * **AUC-ROC & PR-AUC** (Precision-Recall AUC đặc biệt quan trọng do dữ liệu mất cân bằng nhãn).
   * **Brier Score** (Đo lường độ chuẩn xác của xác suất dự báo - Calibration).
   * **Cost-Sensitive Loss** (Ưu tiên phạt nặng Type II Error - dự báo nhầm doanh nghiệp sắp vỡ nợ thành bình thường).
2. **Năng lực Tuân thủ Kinh tế (Economic Consistency Score - ECS)**:
   * Tỷ lệ vi phạm tiên đề đơn điệu trên tập Test:
     $$\text{Violation Rate} = \frac{1}{N_{\text{test}}} \sum_{i=1}^{N_{\text{test}}} \mathbb{I}\left( \frac{\partial \hat{y}_i}{\partial \text{Leverage}} < 0 \lor \frac{\partial \hat{y}_i}{\partial \text{ICR}} > 0 \right)$$
   * *Mô hình EIML đề xuất hướng tới tỷ lệ vi phạm $\approx 0\%$ trong khi vẫn duy trì AUC vượt trội so với các mô hình cổ điển.*

---

## 9. Định hướng Công bố & Tạp chí Mục tiêu

* **Tạp chí ưu tiên số 1**: *Expert Systems with Applications* (Elsevier - Q1, IF ~7.5, CiteScore ~14.0) — Cùng tạp chí và là sự kế thừa trực tiếp bài kinh điển của Barboza, Kimura & Altman (2017).
* **Tạp chí ưu tiên số 2**: *International Review of Financial Analysis* (Elsevier - Q1, IF ~7.5).
* **Tạp chí ưu tiên số 3**: *Annals of Operations Research* (Springer - Q1, IF ~4.4).
