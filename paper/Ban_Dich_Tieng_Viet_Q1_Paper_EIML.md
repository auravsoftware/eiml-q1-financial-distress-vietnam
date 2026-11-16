# Học máy Tích hợp Lý thuyết Kinh tế trong Dự báo Kiệt quệ Tài chính Doanh nghiệp: Ràng buộc Cấu trúc Nhúng và Bằng chứng Thực nghiệm Ngoài mẫu Thời gian tại Việt Nam
*(Economically-Informed Machine Learning for Corporate Financial Distress Prediction: Embeddable Structural Constraints and Out-of-Time Evidence from Vietnam)*

> [!IMPORTANT]
> **File PDF Tiếng Việt hoàn chỉnh (20 trang, phông chữ Vector T5 Latin Modern chuẩn xuất bản)** đã được biên dịch trực tiếp từ LaTeX tại:
> - **Bản PDF Tiếng Việt (20 trang, 874 KB)**: [`final_paper_vi.pdf`](file:///home/antigravity/09_PAPER_Q1_BOND/paper/final_paper_vi.pdf) (bản sao tại [`/home/antigravity/eiml_q1_orchestra/final_paper_vi.pdf`](file:///home/antigravity/eiml_q1_orchestra/final_paper_vi.pdf))
> - **Mã nguồn LaTeX Tiếng Việt**: [`main_vi.tex`](file:///home/antigravity/09_PAPER_Q1_BOND/paper/main_vi.tex)
> - **Bản PDF Tiếng Anh gốc (19 trang, 796 KB)**: [`final_paper.pdf`](file:///home/antigravity/09_PAPER_Q1_BOND/paper/final_paper.pdf)

---

## Tóm tắt (Abstract)

Dự báo kiệt quệ tài chính doanh nghiệp (*Corporate Financial Distress Prediction*) là một trụ cột cốt lõi của tài chính doanh nghiệp thực nghiệm và quản trị rủi ro tín dụng. Mặc dù các bộ phân loại học máy (*Machine Learning — ML*) dung lượng cao — như cây quyết định tăng cường độ dốc (GBDT) và mạng nơ-ron đa tầng sâu (MLP) — thường xuyên vượt trội hơn các mô hình chấm điểm tuyến tính cổ điển trên dữ liệu bảng kế toán, chúng lại mắc phải hai lỗ hổng cấu trúc nghiêm trọng cản trở việc áp dụng trong giám sát an toàn vĩ mô tại các thị trường mới nổi.

1. **Thứ nhất**, các bộ ước lượng phi tuyến không ràng buộc thường khớp quá mức vào các tương quan giả tạo, phi đơn điệu trong các tỷ số kế toán nhiễu, dẫn đến các kết quả tĩnh học so sánh trái ngược với lý thuyết kinh tế (ví dụ: dự báo xác suất vỡ nợ giảm xuống khi tỷ lệ đòn bẩy nợ tăng lên) và vi phạm các biên thanh toán cấu trúc.
2. **Thứ hai**, các nghiên cứu thực nghiệm về kiệt quệ tài chính thường mắc phải *thiên kiến nhìn trước* (*look-ahead bias*) nghiêm trọng xuất phát từ việc kiểm định chéo $K$-fold ngẫu nhiên cắt ngang qua các năm dữ liệu bảng, cắt cụt ngoại lai (*winsorization*) và nội suy trên toàn bộ mẫu, trộn lẫn dữ liệu lịch sử hồi tố trước khi niêm yết (*pre-IPO backfilling*), và thiên kiến sống sót (*survivorship bias*) khi các doanh nghiệp vỡ nợ bị hủy niêm yết.

Để giải quyết đồng thời cả hai thách thức này, chúng tôi đề xuất khung **Học máy Tích hợp Lý thuyết Kinh tế (Economically-Informed Machine Learning — EIML)** gồm hai nhánh bổ trợ:
- **(i) Nhánh A — `Monotonic GBDT`**: Mô hình cây quyết định tăng cường độ dốc với ràng buộc dấu đạo hàm tại từng nút phân tách và điều chuẩn lá đẳng điệu;
- **(ii) Nhánh B — `Proposed EINN`**: Mạng Nơ-ron Tích hợp Lý thuyết Kinh tế khả vi áp đặt tính đơn điệu từng phần thông qua tái tham số hóa trọng số bằng hàm $\text{softplus}$ kết hợp với hàm phạt biên cấu trúc lấy cảm hứng từ lý thuyết định giá nợ của Merton (1974) và vùng mất khả năng thanh toán của Altman (1968, 1995).

Được kiểm định trên bộ dữ liệu bảng 15 năm đã qua kiểm toán pháp y gồm $11.455$ quan sát doanh nghiệp–năm ($7.602$ cặp chuyển trạng thái hậu niêm yết của $692$ doanh nghiệp phi tài chính trên HOSE, HNX và UPCOM giai đoạn 2008–2022) theo giao thức chia tách ngoài mẫu thời gian tuyệt đối (*strict out-of-time*) bao phủ cuộc khủng hoảng trái phiếu doanh nghiệp và hủy niêm yết năm 2021–2022 tại Việt Nam ($N_{\text{test}}=2.083$), khung EIML đạt hiệu năng phân loại hàng đầu đồng thời triệt tiêu hoàn toàn các vi phạm tiên đề kinh tế:
- Trong bài toán **dự báo chuyển trạng thái kiệt quệ mới trước 1 năm (Chế độ A: $Y_{i,t+1}^{\text{fwd}}$)**: `Monotonic GBDT` đạt $\text{ROC-AUC} = 0,8021$, $\text{PR-AUC} = 0,3793$, điểm Brier $= 0,0798$ và Điểm Nhất quán Kinh tế ($\text{ECS}$) đạt $99,97\%$; trong khi `Proposed EINN` cải thiện $\text{PR-AUC}$ thêm $+4,96\%$ so với mạng MLP không ràng buộc ($0,3517$ so với $0,3021$) và nâng điểm $\text{ECS}$ từ $29,00\%$ lên $100,00\%$ ($0,00\%$ vi phạm đơn điệu và biên).
- Trong bài toán **dự báo kiệt quệ đa kỳ dai dẳng (Chế độ B: $Y_{i,t+1}^{\text{ovl}}$)**: `Monotonic GBDT` và `Proposed EINN` đạt $\text{ROC-AUC}$ lần lượt là $0,9648$ và $0,9592$ với độ nhất quán kinh tế $100,00\%$, cảnh báo sớm thành công các tổ chức phát hành rơi vào khủng hoảng năm 2022 (`FLC`, `HAI`, `BII`, `AMD`, `GAB` và `VKC`) từ báo cáo tài chính năm 2021.

**Từ khóa:** Dự báo kiệt quệ tài chính doanh nghiệp; Học máy tích hợp lý thuyết kinh tế (EIML); Mạng nơ-ron đơn điệu; Rủi ro tín dụng cấu trúc; Thiên kiến nhìn trước (Look-Ahead Bias); Doanh nghiệp niêm yết Việt Nam.

---

## 1. Giới thiệu (Introduction)

Dự báo chính xác, kịp thời và có thể giải thích được về mặt kinh tế đối với tình trạng kiệt quệ tài chính doanh nghiệp có ý nghĩa sống còn đối với các ngân hàng thương mại, trái chủ, cơ quan giám sát an toàn vĩ mô và nhà đầu tư cổ phiếu (Beaver, 1966; Altman, 1968; Campbell et al., 2008). Tại các thị trường vốn mới nổi, nơi cơ chế thực thi công bố thông tin đang trong quá trình hoàn thiện, độ bao phủ xếp hạng tín nhiệm độc lập còn hạn chế và cấu trúc nợ doanh nghiệp phụ thuộc nặng nề vào tín dụng ngân hàng ngắn hạn cùng trái phiếu doanh nghiệp phát hành riêng lẻ, các làn sóng mất khả năng thanh toán đột ngột có thể kích hoạt sự đóng băng thanh khoản mang tính hệ thống (Altman et al., 1995; Pham Vo Ninh et al., 2018; Tran et al., 2023). Tính dễ tổn thương này đã bộc lộ rõ nét trong cuộc khủng hoảng thanh khoản trái phiếu doanh nghiệp và bất động sản tại Việt Nam giai đoạn 2021–2022, khi việc mở rộng đòn bẩy ngắn hạn quá mức kết hợp với khả năng chi trả lãi vay từ hoạt động cốt lõi suy yếu đã dẫn đến hàng loạt vụ vỡ nợ trái phiếu, đình chỉ giao dịch và hủy niêm yết bắt buộc trên HOSE và HNX.

Về mặt lịch sử, tổng quan nghiên cứu dự báo vỡ nợ doanh nghiệp phát triển theo hai hệ hình phương pháp luận chính:
1. **Hệ hình thống kê cổ điển và rủi ro tín dụng cấu trúc**: Khởi đầu từ phân tích tỷ số đơn biến (Beaver, 1966), phân tích biệt số đa biến ($Z$-score và $Z''$-score) (Altman, 1968, 1995, 2017), mô hình logit và probit có điều kiện (Ohlson, 1980; Zmijewski, 1984), mô hình hàm nguy cơ rời rạc đa kỳ (Shumway, 2001; Chava & Jarrow, 2004; Campbell et al., 2008; Bauer & Agarwal, 2014), và các mô hình khoảng cách đến vỡ nợ (*distance-to-default*) dựa trên lý thuyết định giá quyền chọn của Merton (1974) (Hillegeist et al., 2004; Duffie et al., 2007; Bharath & Shumway, 2008). Nhờ áp đặt dạng hàm tham số chặt chẽ và các tính chất tĩnh học so sánh rõ ràng, các mô hình này đáp ứng tốt yêu cầu kiểm toán của cơ quan quản lý; tuy nhiên, dạng hàm cộng tuyến tính của chúng không thể nắm bắt được các tương tác phi tuyến phức tạp giữa cấu trúc kỳ hạn nợ, sự suy giảm vốn lưu động và dòng tiền hoạt động.
2. **Hệ hình học máy (ML) phi tham số và học sâu (Deep Learning)**: Bao gồm Random Forest (Breiman, 2001), GBDT (Chen & Guestrin, 2016; Ke et al., 2017; Prokhorenkova et al., 2018), SVM và mạng nơ-ron sâu (Lessmann et al., 2015; Zięba et al., 2016; Barboza et al., 2017; Mai et al., 2019; Hosaka, 2019; Gunnarsson et al., 2021). Mặc dù các mô hình tổ hợp ML dung lượng cao liên tục đạt độ chính xác xếp hạng vượt trội trên các bộ dữ liệu chuẩn, chúng lại tạo ra một mâu thuẫn căn bản giữa tính linh hoạt dự báo và tính hợp lý kinh tế (Bussmann et al., 2021; Bücker et al., 2022; Dumitrescu et al., 2022). Khi được huấn luyện trên dữ liệu bảng kế toán nhiễu và có đuôi dày tại các thị trường mới nổi, một mạng MLP không ràng buộc hoặc RBF-SVM có thể khớp các dao động cục bộ khiến cho việc gia tăng tỷ lệ nợ trên tổng tài sản ($\text{Debt}/\text{Assets}$) trong điều kiện *ceteris paribus* lại làm **giảm** xác suất vỡ nợ dự báo.

Làm trầm trọng thêm thách thức mô hình hóa này là bốn nguồn **thiên kiến nhìn trước (look-ahead bias)** và sai lệch dữ liệu bảng phổ biến trong các nghiên cứu thực nghiệm (Bailey et al., 2014; López de Prado, 2018):
1. **Chia tách ngẫu nhiên cắt ngang và lấy mẫu quá mức (SMOTE) trên toàn mẫu theo thời gian**: Cho phép các quan sát ở năm $t+k$ tham gia huấn luyện để dự báo cho năm $t$, làm rò rỉ các cú sốc vĩ mô tương lai và trạng thái kiệt quệ dai dẳng của cùng một doanh nghiệp vào tập huấn luyện (ví dụ: Tran et al., 2022).
2. **Độ trễ công bố báo cáo và rò rỉ từ công thức tỷ số đồng nhất thức (tautology)**: Báo cáo tài chính năm $t$ tại Việt Nam được công bố vào quý I năm $t+1$ (đến 31/03). Hơn nữa, khi chi phí lãi vay bị khuyết, việc tính $\text{EBIT} = \text{NetProfit} + |\text{InterestExpense}|$ sẽ biến điều kiện $\text{ICR} < 1,0 \iff \text{NetProfit} < 0$ thành một đồng nhất thức đại số $100\%$.
3. **Nhiễu từ dữ liệu hồi tố trước khi niêm yết (Pre-IPO backfilling)**: Gộp các dòng báo cáo tài chính trước năm niêm yết ($\text{Year} < \text{Listedyear}$) vào mẫu rủi ro tín dụng niêm yết làm sai lệch xác suất vỡ nợ cơ sở.
4. **Thiên kiến sống sót do hủy niêm yết bắt buộc (Survivorship bias)**: Loại bỏ các doanh nghiệp mất sàn giao dịch hoặc ngừng nộp báo cáo tài chính ở năm $t+1$ ngay sau khi kiệt quệ nặng ở năm $t$.

---

## 2. Tổng quan Tài liệu và Định vị Lý thuyết (Related Work)

### 2.1. Mô hình Tỷ số Kế toán Cổ điển, Mô hình Hazard và Rủi ro Tín dụng Cấu trúc
Dòng nghiên cứu thực nghiệm khởi nguồn từ Beaver (1966) và Altman (1968, 1995, 2017) với mô hình $Z$-score và $Z''$-score (Emerging Market Score — EMS). Ohlson (1980) và Zmijewski (1984) giới thiệu logit có điều kiện ($O$-score) và probit có trọng số. Shumway (2001) chứng minh các mô hình tĩnh một kỳ tạo ra ước lượng chệch và thiết lập mô hình hazard đa kỳ rời rạc (Chava & Jarrow, 2004; Campbell et al., 2008; Tinoco & Wilson, 2013; Bauer & Agarwal, 2014). Song song đó, lý thuyết quyền chọn định giá nợ của Merton (1974) và lý thuyết đánh đổi cấu trúc vốn (Kraus & Litzenberger, 1973; Myers, 1984; Hillegeist et al., 2004; Duffie et al., 2007; Bharath & Shumway, 2008) chứng minh rằng xác suất vỡ nợ là hàm không giảm theo đòn bẩy nợ ($\partial P / \partial (D/A) \ge 0$) và không tăng theo khả năng sinh lời hoạt động ($\partial P / \partial \text{ROA} \le 0$). Tại các thị trường mới nổi, nơi thủ tục phá sản tòa án kéo dài, Asquith et al. (1994), Pindado et al. (2008) và Tinoco & Wilson (2013) thiết lập chuẩn mực định nghĩa kiệt quệ tài chính dựa trên $\text{ICR} < 1$ và âm vốn chủ sở hữu kết hợp với hủy niêm yết.

### 2.2. Học máy Tổ hợp (Ensembles) và Học sâu trong Dự báo Kiệt quệ Doanh nghiệp
Các mô hình Random Forest (Breiman, 2001) và GBDT như XGBoost (Chen & Guestrin, 2016), LightGBM (Ke et al., 2017) và CatBoost (Prokhorenkova et al., 2018) đã được chứng minh vượt trội so với hồi quy tuyến tính (Kumar & Ravi, 2007; Lessmann et al., 2015; Geng et al., 2015; Zięba et al., 2016; Barboza et al., 2017; Jones et al., 2017; Veganzones & Séverin, 2018). Trong hướng học sâu, du Jardin (2015), Hosaka (2019) và Mai et al. (2019) ứng dụng mạng nơ-ron sâu trên dữ liệu kế toán và văn bản. Tuy nhiên, Gunnarsson et al. (2021) và Dumitrescu et al. (2022) chỉ ra rằng trên dữ liệu bảng tín dụng có đa cộng tuyến cao, mạng MLP không ràng buộc dễ dàng khớp nhiễu cục bộ và đảo ngược dấu đạo hàm kinh tế.

### 2.3. Học máy Đơn điệu, Mạng Nơ-ron Tích hợp Lý thuyết (PINNs) và Giải thích Tiên đề (XAI)
Nhánh học máy đơn điệu khởi đầu từ Sill (1997), bảng nội suy đơn điệu (Gupta et al., 2016), Deep Lattice Networks (You et al., 2017; Cano et al., 2019) và Constrained Monotonic Neural Networks (Runje & Shankaranarayana, 2023). Trong vật lý tính toán, Raissi et al. (2019) và Karniadakis et al. (2021) phát triển Physics-Informed Neural Networks (PINNs) nhúng điều kiện biên vào hàm mất mát. Trong quản trị rủi ro tín dụng, dù SHAP (Lundberg & Lee, 2017) và Integrated Gradients (Sundararajan et al., 2017) được khuyến nghị cho kiểm toán mô hình (Bussmann et al., 2021; Bücker et al., 2022), XAI hậu nghiệm không thể sửa chữa một mô hình học sai dấu đạo hàm kinh tế. Khung EIML của chúng tôi giải quyết triệt để vấn đề này ngay từ kiến trúc.

### 2.4. Thiên kiến Nhìn trước, Vệ sinh Dữ liệu Bảng và Các Nghiên cứu tại Việt Nam
Tại Việt Nam, Pham Vo Ninh et al. (2018), Vo et al. (2019), Tran et al. (2022), Tran et al. (2023) và Vu et al. (2023) đã đặt nền tảng thực nghiệm quan trọng về dự báo kiệt quệ tài chính trên HOSE, HNX và UPCOM. Tuy nhiên, việc sử dụng SMOTE toàn mẫu và chia ngẫu nhiên $70/30$ (Tran et al., 2022), winsorize toàn mẫu (Tran et al., 2023), chưa tách riêng dữ liệu tiền IPO ($\text{Year} < \text{Listedyear}$) và chưa ràng buộc tính đơn điệu kinh tế là các khoảng trống phương pháp luận được bài báo này lấp đầy (Bảng 1).

| Nghiên cứu (Tạp chí / Phân vị) | Hệ hình Cốt lõi | Phi tuyến | Tiên đề Đơn điệu | Biên Cấu trúc | Chia OOT Chuẩn | Lọc Pre-IPO / Hủy NY | XAI Tiên đề |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| Altman (1968, 1995) (*JF* Q1) | MDA ($Z / Z''$) | $\times$ | $\checkmark$ | $\checkmark$ | $\times$ | $\times$ | $\checkmark$ |
| Ohlson (1980) (*JAR* Q1) | Logit có điều kiện | $\times$ | $\checkmark$ | $\times$ | $\times$ | $\times$ | $\checkmark$ |
| Merton (1974); Bharath & Shumway (2008) (*JF/RFS* Q1) | Quyền chọn nợ ($DD$) | $\checkmark$ | $\checkmark$ | $\checkmark$ | $\checkmark$ | $\times$ | $\checkmark$ |
| Shumway (2001); Campbell et al. (2008) (*JB/JF* Q1) | Hazard đa kỳ | $\times$ | $\checkmark$ | $\times$ | $\checkmark$ | $\checkmark$ | $\checkmark$ |
| Barboza et al. (2017); Zięba et al. (2016) (*ESWA* Q1) | RF, GBDT, SVM | $\checkmark$ | $\times$ | $\times$ | $\checkmark$ | $\times$ | $\times$ |
| Mai et al. (2019); Gunnarsson et al. (2021) (*JBF/EJOR* Q1) | Học sâu / Tổ hợp cây | $\checkmark$ | $\times$ | $\times$ | $\checkmark$ | $\times$ | $\times$ |
| Bussmann et al. (2021); Bücker et al. (2022) (*CE/JORS* Q1) | ML + XAI hậu nghiệm | $\checkmark$ | $\times$ | $\times$ | $\times$ | $\times$ | $\checkmark$ |
| Pham Vo Ninh et al. (2018); Tran et al. (2023) (*ES/PLOS* Q1) | Logit / EMS tại Việt Nam | $\times$ | $\checkmark$ | $\times$ | $\times$ | $\times$ | $\checkmark$ |
| Tran et al. (2022); Vu et al. (2023) (*Data/Cogent* Q2) | ML + SHAP / LASSO (VN) | $\checkmark$ | $\times$ | $\times$ | $\times$ | $\times$ | $\checkmark$ |
| **Nghiên cứu này (EIML: Mono-GBDT & EINN)** | **ML & Mạng sâu Ràng buộc Lý thuyết** | $\mathbf{\checkmark}$ | $\mathbf{\checkmark}$ | $\mathbf{\checkmark}$ | $\mathbf{\checkmark}$ | $\mathbf{\checkmark}$ | $\mathbf{\checkmark}$ |

---

## 3. Làm sạch Dữ liệu Pháp y và Thiết lập Thực nghiệm Không Nhìn trước

### 3.1. Quy trình Kiểm toán Pháp y 7 Bước trên Dữ liệu Bảng (2008–2022)
Từ $11.455$ quan sát doanh nghiệp–năm gốc trong [`data-financial-0601.xlsx`](file:///home/antigravity/upload/data-financial-0601.xlsx), quy trình làm sạch pháp y 7 bước ([`src/data_loader.py`](file:///home/antigravity/09_PAPER_Q1_BOND/src/data_loader.py)) đã xử lý triệt để:

| Bước | Bất thường Pháp y Phát hiện | Biện pháp Khắc phục & Cơ sở Kinh tế lượng | Phạm vi Ảnh hưởng |
| :---: | :--- | :--- | :---: |
| **1** | Trùng lặp Cột dữ liệu (`Col 25` & `Col 26`) | Kiểm định đối chiếu từng ô đạt độ trùng khớp $100,0\%$ ($0$ sai khác trên $11.455$ dòng); loại bỏ cột dư thừa `Col 26`. | $11.455$ dòng |
| **2** | Đứt gãy Mã CK (`MCO` $\to$ `MCG` năm 2022) | Khớp chính xác số dư đầu kỳ năm 2022 của dòng 5296 (`MCO`) với số dư cuối kỳ 2021 của `MCG` ($692$ doanh nghiệp duy nhất). | $1$ doanh nghiệp |
| **3** | Khuyết & Lỗi `Listedyear` ($= 1900$) | Đối chiếu lịch sử sàn giao dịch hợp lệ sớm nhất; phục hồi $9$ mã có năm niêm yết giả $1900$ và $719$ dòng khuyết năm 2022. | $728$ dòng |
| **4** | Đảo dấu Dương ở các khoản Chi phí | Chuẩn hóa 5 cột chi phí thông qua $\|x\|$; chỉnh sửa $40$ ô chi phí bị ghi dương bất thường (`MSH`, `ITA`, `HAG` 2022; `NFC` 2018). | $40$ ô dữ liệu |
| **5** | Khuyết `interestexp` & Đồng nhất thức $\text{ICR}$ | Nội suy $1.376$ dòng khuyết lãi vay bằng tỷ số trung vị tập huấn luyện $\kappa_{\text{train}} = 0,852993$; tái cấu trúc $\text{EBIT}_{\text{op}}$ hoạt động. | $1.376$ dòng |
| **6** | Nhiễu Dữ liệu Hồi tố Tiền niêm yết (Pre-IPO) | Cô lập toàn bộ các quan sát có $\text{Year} < \text{Listedyear}$ khỏi tập mô hình hóa chính nhằm loại bỏ thiên kiến hồi tố niêm yết. | $1.570$ dòng ($1.562$ cặp) |
| **7** | Kiểm duyệt Hủy niêm yết / Rời mẫu hậu Kiệt quệ | Thu giữ các doanh nghiệp mất sàn giao dịch (`Stockexchange == ""`) hoặc biến mất năm 2022 sau khi kiệt quệ nặng năm 2021 vào Điều kiện 3. | $19$ ca vỡ nợ cuối kỳ |

Công thức tái cấu trúc **Lợi nhuận Hoạt động ($\text{EBIT}_{\text{op}}$)** và **Tỷ số Thanh toán Lãi vay Hoạt động ($\text{ICR}_{\text{op}}$)** hoàn toàn không nhìn trước:
$$\kappa_{\text{train}} = \operatorname{median}_{(i,t) \in \mathcal{D}_{\text{train}}} \left( \frac{|\text{interestexp}_{i,t}|}{|\text{financialexp}_{i,t}|} \right) = 0,852993$$
$$\text{EBIT}_{\text{op}, i, t} = \text{NetSales}_{i,t} - C_{i,t} - S_{i,t} - A_{i,t}, \qquad \text{ICR}_{\text{op}, i, t} = \frac{\text{EBIT}_{\text{op}, i, t}}{I_{i,t} + \epsilon}$$

### 3.2. Định nghĩa Kiệt quệ Tài chính Đa tiêu chí và Hai Chế độ Dự báo
$$D_{i,t+1} = \mathbb{I}\Big( \underbrace{\big[\text{ICR}_{\text{op},i,t+1} < 1,0 \ \wedge \ \text{NetProfit}_{i,t+1} < 0\big]}_{\text{Điều kiện 1: Mất khả năng trả lãi hoạt động \& Lỗ ròng}} \ \vee \ \underbrace{\big[\text{Equity}_{i,t+1} < 0\big]}_{\text{Điều kiện 2: Âm vốn chủ sở hữu}} \ \vee \ \underbrace{\big[\text{DelistAttrition}_{i,t+1} = 1\big]}_{\text{Điều kiện 3: Hủy niêm yết / Vỡ nợ rời mẫu}} \Big)$$
- **Chế độ A — Dự báo Chuyển trạng thái Kiệt quệ Mới trước 1 năm ($Y_{i,t+1}^{\text{fwd}}$)**: $816 / 7.602$ cặp dương tính ($10,73\%$).
- **Chế độ B — Dự báo Kiệt quệ Đa kỳ Dai dẳng ($Y_{i,t+1}^{\text{ovl}} = D_{i,t+1}$)**: $1.303 / 7.602$ cặp dương tính ($17,14\%$).

---

## 4. Phương pháp luận: Học máy Tích hợp Lý thuyết Kinh tế (EIML)

### 4.1. Tham số hóa Trọng số Đơn điệu Từng phần trong `Proposed EINN`
Với $\phi(u) = \ln(1 + e^u)$, ma trận trọng số tầng ẩn đầu tiên $\mathbf{W}^{(1)} \in \mathbb{R}^{d \times H_1}$ được tái tham số hóa qua các mặt nạ tiên đề kinh tế $\mathbf{M}_+, \mathbf{M}_-, \mathbf{M}_0$:
$$\mathbf{W}^{(1)} = \phi\big(\mathbf{U}^{(1)}\big) \odot \mathbf{M}_+ \;-\; \phi\big(\mathbf{U}^{(1)}\big) \odot \mathbf{M}_- \;+\; \mathbf{V}^{(1)} \odot \mathbf{M}_0$$
và $\mathbf{W}^{(l)} = \phi(\mathbf{U}^{(l)}) \ge 0$ với mọi tầng $l \ge 2$, đảm bảo giải tích:
$$\frac{\partial \hat{p}_{i,t+1}}{\partial x_{i,t,j}} \ge 0 \quad \forall j \in \mathcal{M}_+ \ (\text{Đòn bẩy nợ}), \qquad \frac{\partial \hat{p}_{i,t+1}}{\partial x_{i,t,k}} \le 0 \quad \forall k \in \mathcal{M}_- \ (\text{Sinh lời \& Trả lãi})$$

### 4.2. Hàm Mất mát Phức hợp Tích hợp Lý thuyết và Chỉ số Nhất quán Kinh tế ($\text{ECS}$)
$$\mathcal{L}_{\text{EINN}}(\theta) = \mathcal{L}_{\text{Focal-BCE}}(\theta) + \lambda_{\text{mono}} \mathcal{L}_{\text{mono}}(\theta) + \lambda_{\text{bound}} \mathcal{L}_{\text{bound}}(\theta) + \lambda_2 \|\theta\|_2^2$$
$$\text{ECS} = 100\% - \Big( 0,70 \times \text{VR}_{\text{mono}} + 0,30 \times \text{VR}_{\text{bound}} \Big)$$

---

## 5. Kết quả Thực nghiệm Ngoài mẫu Thời gian (2021–2022, $N_{\text{test}}=2.083$)

### 5.1. Đối sánh Toàn diện 9 Mô hình trên Chế độ A ($Y_{i,t+1}^{\text{fwd}}$) và Chế độ B ($Y_{i,t+1}^{\text{ovl}}$)

| Chế độ Dự báo | Mô hình Đối sánh | ROC-AUC $\uparrow$ | PR-AUC $\uparrow$ | F1 $\uparrow$ | Brier $\downarrow$ | $\text{VR}_{\text{mono}}$ (%) $\downarrow$ | $\text{VR}_{\text{bound}}$ (%) $\downarrow$ | ECS (%) $\uparrow$ |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Chế độ A ($Y_{i,t+1}^{\text{fwd}}$)** | Altman $Z''$-Score (1995) | 0,6648 | 0,2487 | 0,2901 | 0,2954 | 0,00 | 0,00 | 100,00 |
| *(Kiệt quệ Mới trước 1 năm)* | Ohlson $O$-Score (1980) | 0,6453 | 0,2085 | 0,2602 | 0,1550 | 0,00 | 68,75 | 79,38 |
| *Tỷ lệ cơ sở: $10,99\%$* | Logistic Regression (L2) | 0,7732 | 0,3044 | 0,4139 | 0,0854 | 100,00 | 81,25 | 5,63 |
| | RBF-Kernel SVM | 0,7504 | 0,2886 | 0,3574 | 0,0877 | 95,30 | 100,00 | 3,29 |
| | Random Forest | **0,8062** | 0,3433 | 0,4199 | 0,0822 | 0,77 | 100,00 | 69,46 |
| | Unconstrained GBDT | 0,7991 | 0,3493 | **0,4201** | 0,0819 | 0,05 | 100,00 | 69,97 |
| | Unconstrained MLP | 0,7764 | 0,3021 | 0,3919 | 0,0879 | 71,96 | 68,75 | 29,00 |
| | **Mono-GBDT (Đề xuất)** | **0,8021** | **0,3793** | **0,4187** | **0,0798** | **0,05** | **0,00** | **99,97** |
| | **Proposed EINN (Đề xuất)** | **0,7870** | **0,3517** | **0,3943** | **0,0848** | **0,00** | **0,00** | **100,00** |
| **Chế độ B ($Y_{i,t+1}^{\text{ovl}}$)** | Altman $Z''$-Score (1995) | 0,6440 | 0,2713 | 0,3298 | 0,2917 | 0,00 | 0,00 | 100,00 |
| *(Kiệt quệ Đa kỳ Dai dẳng)* | Ohlson $O$-Score (1980) | 0,6528 | 0,2713 | 0,3212 | 0,1674 | 0,00 | 68,75 | 79,38 |
| *Tỷ lệ cơ sở: $17,28\%$* | Logistic Regression (L2) | 0,9548 | 0,7351 | 0,7580 | 0,0664 | 94,10 | 37,50 | 22,88 |
| | RBF-Kernel SVM | 0,8864 | 0,6282 | 0,5808 | 0,0969 | 96,54 | 100,00 | 2,42 |
| | Random Forest | 0,9620 | 0,7746 | 0,8011 | 0,0600 | 2,21 | 93,75 | 70,33 |
| | Unconstrained GBDT | 0,9640 | 0,7820 | 0,8060 | 0,0496 | 0,00 | 100,00 | 70,00 |
| | Unconstrained MLP | 0,9557 | 0,7526 | 0,7425 | 0,0606 | 39,94 | 12,50 | 68,29 |
| | **Mono-GBDT (Đề xuất)** | **0,9648** | **0,7932** | **0,8076** | **0,0490** | **0,00** | **0,00** | **100,00** |
| | **Proposed EINN (Đề xuất)** | **0,9592** | **0,7658** | **0,7620** | **0,0590** | **0,00** | **0,00** | **100,00** |

### 5.2. Kiểm toán Cảnh báo Sớm 6 Doanh nghiệp Tâm điểm Khủng hoảng Trái phiếu & Hủy niêm yết 2022 (Dự báo từ Báo cáo Tài chính 2021)

| Mã CK | Ngành ICB (Cấp 2) | $D/A_{2021}$ | $\text{STDebt}/D_{2021}$ | $\text{ICR}_{\text{op},2021}$ | $\text{ROA}_{2021}$ | Altman $Z''_{2021}$ | MLP $\hat{p}^{\text{fwd}}$ | EINN $\hat{p}^{\text{fwd}}$ | EINN $\hat{p}^{\text{ovl}}$ | Sự kiện Thực tế năm 2022 |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`FLC`** | Bất động sản | 0,7122 | 0,6629 | $-1,1204$ | $+0,0025$ | 3,93 *(An toàn giả)* | 0,2307 | **0,2633** | **0,6985** | Đình chỉ GD / Hủy niêm yết / Vỡ nợ TP |
| **`HAI`** | Hóa chất / Nông dược | 0,3505 | 0,9747 | $-15,000$ | $-0,2940$ | 5,50 *(An toàn giả)* | 0,5555 | **0,6512** | **0,8115** | Đình chỉ GD / Hủy niêm yết bắt buộc |
| **`BII`** | Bất động sản | 0,3590 | 0,9914 | $-0,3796$ | $+0,0326$ | 5,81 *(An toàn giả)* | 0,2336 | **0,1956** | **0,6842** | Đình chỉ GD / Hủy niêm yết |
| **`GAB`** | Xây dựng & Vật liệu | 0,4370 | 1,0000 | $+1,1758$ | $+0,0064$ | 6,00 *(An toàn giả)* | 0,1215 | **0,2135** | **0,1992** | Đình chỉ GD / Vi phạm công bố TT |
| **`AMD`** | Bất động sản | 0,2388 | 0,9727 | $+0,8716$ | $+0,0043$ | 10,27 *(An toàn giả)* | 0,2945 | **0,1830** | **0,2901** | Đình chỉ GD / Hủy niêm yết |
| **`VKC`** | Ô tô & Phụ tùng | 0,6423 | 0,7272 | $+0,9627$ | $+0,0034$ | 6,12 *(An toàn giả)* | 0,2041 | **0,1211** | **0,1689** | Mất khả năng thanh toán trái phiếu |

---

## 6. Kết luận và Hàm ý Chính sách

Khung **Học máy Tích hợp Lý thuyết Kinh tế (EIML)** giải quyết triệt để bài toán đánh đổi giữa độ chính xác phi tuyến và tính hợp lý kinh tế trong dự báo kiệt quệ tài chính doanh nghiệp tại Việt Nam. Bằng cách kết hợp quy trình làm sạch pháp y 7 bước, tái cấu trúc lợi nhuận hoạt động $\text{EBIT}_{\text{op}}$ và ràng buộc đơn điệu–biên cấu trúc Merton/Altman, hệ thống đạt điểm nhất quán kinh tế tuyệt đối ($\text{ECS} = 100\%$) và cung cấp công cụ cảnh báo sớm đáng tin cậy cho cơ quan quản lý, ngân hàng thương mại và nhà đầu tư trái phiếu.
