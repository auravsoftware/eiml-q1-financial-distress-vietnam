# Bản Thiết Kế Toàn Diện & Bản Thảo Bài Báo Chuẩn Q1 (Elsevier ESWA / IRFA) theo Kiến Trúc Đa Tác Tử `PaperOrchestra`

> [!IMPORTANT]
> Tài liệu này kết hợp:
> 1. **Phân tích giải phẫu từng bước hệ thống đa tác tử [PaperOrchestra](https://github.com/google-research/paper-orchestra)** của Google Research và cách ánh xạ (mapping) dự án `EIML-Distress` sang chuẩn đầu vào/đầu ra của `PaperOrchestra`.
> 2. **Phân tích & Tối ưu hóa Tựa đề (Title Engineering)** nhằm vượt qua vòng Desk Review khắt khe của *Expert Systems with Applications (ESWA)* và *International Review of Financial Analysis (IRFA)*.
> 3. **Kiểm toán Pháp y Dữ liệu (`data-financial-0601.xlsx`) & Khử Thiên kiến Nhìn trước (*Look-Ahead Bias* / *Survivorship Bias*)**: Phát hiện và xử lý triệt để **8 lỗi dữ liệu thực tế** và **6 bẫy thiên kiến nhìn trước** tồn tại ngay trong tệp Excel gốc và thiết kế ban đầu.
> 4. **Bản thảo Bài báo Hoàn chỉnh Chuẩn Q1**: Bao gồm đầy đủ *Abstract, 1. Introduction, 2. Literature Review & Theoretical Framework, 3. Methodology, 4. Data Forensics & Zero-Look-Ahead Experimental Design, 5. Empirical Results & Ablation Studies, 6. XAI & Policy Implications, 7. Conclusion*.

---

## Phần I: Phân Tích Chi Tiết Quy Trình 5 Bước Tạo Bài Báo Q1 của `PaperOrchestra`

Qua phân tích mã nguồn tại [`methods/paper_writer_with_plotting.py`](file:///home/antigravity/paper-orchestra/methods/paper_writer_with_plotting.py) và [`autoraters/agent_review.py`](file:///home/antigravity/paper-orchestra/autoraters/agent_review.py), kiến trúc của **PaperOrchestra** vận hành như một dây chuyền biên tập khoa học khép kín gồm **5 giai đoạn tác tử (Multi-Agent Pipeline)** chịu sự kiểm soát nghiêm ngặt của nguyên lý **Cô lập Tri thức Tuyệt đối (`UNIVERSAL_NO_LEAKAGE_PROMPT`)**:

```mermaid
flowchart TD
    subgraph RawInputs["Tài liệu Tiền Bản thảo (raw_materials/)"]
        A1["idea_dense.md<br/>(Lý thuyết, Tiên đề, Hàm Loss)"]
        A2["experimental_log.md<br/>(Kiểm toán dữ liệu, Bảng số liệu thực)"]
        A3["template.tex & guidelines.md<br/>(Chuẩn LaTeX Q1 Elsevier/ICLR)"]
    end

    subgraph Step1["Bước 1: OutlineAgent"]
        B1["Phân tích chéo Idea + Log"]
        B2["Sinh outline.json gồm:<br/>1. plotting_plan<br/>2. intro_related_work_plan<br/>3. section_plan + citation_hints"]
    end

    subgraph Step2["Bước 2: Thực thi Song song (ThreadPoolExecutor)"]
        direction LR
        C1["HybridLiteratureAgent<br/>• Tách biệt Macro (Intro) vs Micro (Related Work)<br/>• Google Search + Semantic Scholar API<br/>• Kiểm soát Cutoff Date chống rò rỉ thời gian<br/>• Sinh references.bib, citation_map.json,<br/>  và viết Intro + Related Work vào updated_template.tex"]
        C2["PlottingAgent<br/>• Few-shot Retrieval -> Content Planner -> Stylist<br/>• Sinh biểu đồ & Sơ đồ kiến trúc<br/>• Vòng lặp Phản biện Thị giác (3 Critic Rounds)<br/>• Xuất figures/ & info.json"]
    end

    subgraph Step3["Bước 3: SectionWritingAgent (Multimodal)"]
        D1["Đọc updated_template.tex + outline_v1.json + figures"]
        D2["Điền các mục Methodology, Experiments, Results, Ablation, Conclusion"]
        D3["Chuyển hóa số liệu từ experimental_log.md thành bảng booktabs LaTeX<br/>(Tuyệt đối không bịa số liệu)"]
    end

    subgraph Step4["Bước 4: ContentRefinementAgent & AgentReview Loop"]
        E1["Biên dịch PDF v0 (compile_latex)"]
        E2["AgentReview (Ensemble 3 Reviewers + 1 Area Chair)<br/>Chấm điểm 9 trục (Originality, Soundness, Overall 1-10)"]
        E3["Vòng lặp Rebuttal-via-Revision (Tối đa 3 vòng):<br/>Chỉ chấp nhận bản sửa nếu Overall tăng hoặc Gain >= Drop"]
        E4["VLM Formatting Critic (pdf_to_grid_images):<br/>Kiểm tra tràn lề bảng/hình và sửa LaTeX"]
    end

    RawInputs --> Step1 --> Step2 --> Step3 --> Step4
```

### Giải phẫu kỹ thuật từng bước trong `PaperOrchestra` và Bài học cho Bài báo Q1 của dự án:

1. **Nguyên lý `UNIVERSAL_NO_LEAKAGE_PROMPT` ([`utils/prompt_utils.py`](file:///home/antigravity/paper-orchestra/utils/prompt_utils.py))**:
   - Mọi tác tử trong PaperOrchestra đều bị cấm suy diễn số liệu ngoài [`experimental_log.md`](file:///home/antigravity/eiml_q1_orchestra/raw_materials/experimental_log.md) và [`idea_dense.md`](file:///home/antigravity/eiml_q1_orchestra/raw_materials/idea_dense.md).
   - **Hệ quả thực tiễn**: Nếu tệp `experimental_log.md` chưa có bảng kiểm toán làm sạch dữ liệu, bảng kiểm định khử thiên kiến nhìn trước (*Look-Ahead Bias Ablation*), hoặc bảng độ nhạy siêu tham số ($\lambda_1, \lambda_2$), thì ở Bước 4 ([`ContentRefinementAgent`](file:///home/antigravity/paper-orchestra/methods/agents/content_refinement_agent.py)), tác tử bị cấm bịa thêm thí nghiệm mới khi Reviewer hỏi! Do đó, toàn bộ kết quả thực nghiệm và kiểm định vững (*Robustness Checks*) **bắt buộc phải được tính toán đầy đủ và đưa vào `experimental_log.md` ngay từ đầu**.
2. **Bước 1 — [`OutlineAgent`](file:///home/antigravity/paper-orchestra/methods/agents/outline_agent.py) ([`prompts/outline_agent.py`](file:///home/antigravity/paper-orchestra/methods/prompts/outline_agent.py))**:
   - Thiết kế cấu trúc JSON 3 nhánh: `plotting_plan` (tên tệp không chứa chữ "Figure", chọn đúng tỷ lệ khung hình và loại biểu đồ), `intro_related_work_plan` (tách biệt rõ *Macro Hook/Gap* ở Introduction gồm 10–20 bài nền tảng và *Micro Technical Clusters* ở Related Work gồm 30–50 bài đối chuẩn), và `section_plan` (bắt buộc không có mục con mồ côi — có `3.1` thì phải có `3.2`, kèm `citation_hints` cho từng thuật toán, thước đo, bộ dữ liệu).
3. **Bước 2 — [`HybridLiteratureAgent`](file:///home/antigravity/paper-orchestra/methods/agents/literature_review_agent.py) & [`PlottingAgent`](file:///home/antigravity/paper-orchestra/methods/agents/plotting_agent.py)**:
   - `HybridLiteratureAgent` thực hiện tìm kiếm song song và làm giàu metadata qua Semantic Scholar (`s2_title_search`), lọc theo `cutoff_date` để không bao giờ trích dẫn nhầm các công trình tương lai, đồng thời áp dụng quy tắc: **không bao giờ tuyên bố vượt trội (SOTA) trước một bài báo nếu bài báo đó không được chạy thực nghiệm trực tiếp trong `experimental_log.md`**.
4. **Bước 3 — [`SectionWritingAgent`](file:///home/antigravity/paper-orchestra/methods/agents/section_writing_agent.py)**:
   - Giữ nguyên phần Introduction & Related Work đã viết ở Bước 2, nạp hình ảnh thực tế (`call_llm_with_images`) để mô tả khớp 100% với xu hướng thị giác trên hình, và dựng bảng LaTeX chuẩn `booktabs` (`\toprule`, `\midrule`, `\bottomrule`).
5. **Bước 4 — [`ContentRefinementAgent`](file:///home/antigravity/paper-orchestra/methods/agents/content_refinement_agent.py) + [`AgentReview`](file:///home/antigravity/paper-orchestra/autoraters/agent_review.py)**:
   - Hội đồng 3 Reviewer độc lập (`num_review_ensemble=3`, đóng vai *Knowledgeable, Responsible, Benign PhD Reviewer*) cùng 1 *Meta-Reviewer (Area Chair)* chấm điểm trên 9 trục (`Originality`, `Quality`, `Clarity`, `Significance`, `Soundness`, `Presentation`, `Contribution`, `Overall` 1–10, `Confidence` 1–5).
   - Cơ chế **Acceptance Gate** thông minh: Bản sửa $v_{i+1}$ chỉ được chấp nhận nếu $\text{Overall}_{v_{i+1}} > \text{Overall}_{v_i}$, hoặc nếu $\text{Overall}$ giữ nguyên nhưng tổng điểm tăng trên các trục phụ lớn hơn hoặc bằng tổng điểm giảm ($\text{Total Gain} \ge \text{Total Drop}$). Nếu điểm giảm, hệ thống lập tức **Revert** về phiên bản trước đó.

---

## Phần II: Phân Tích Tựa Đề (Title Critique) & Đề Xuất Chuẩn Q1

### 1. Phê bình Tựa đề Gốc trong `README.md`
> **Tựa đề gốc:** *"Economics-Informed Machine Learning for Corporate Distress and Shadow Credit Risk Prediction in Emerging Bond Markets"*

Dưới góc nhìn của Tổng biên tập (*Editor-in-Chief*) và Phản biện tạp chí Q1 (*Expert Systems with Applications* hoặc *International Review of Financial Analysis*), tựa đề gốc có **2 điểm mạnh** nhưng chứa **1 lỗ hổng chí mạng có thể dẫn tới Desk Reject**:
- **Điểm mạnh**: Cụm từ **"Economics-Informed Machine Learning"** rất hiện đại, gợi liên tưởng trực tiếp tới *Physics-Informed Neural Networks (PINNs)* chuyển dịch sang tài chính doanh nghiệp (*Theory-Guided / Economics-Informed AI*).
- **Lỗ hổng chí mạng (Mismatch giữa Title và Data)**: Cụm từ **"in Emerging Bond Markets"** khiến Reviewer kỳ vọng bộ dữ liệu phải chứa **dữ liệu cấp độ trái phiếu (Bond-level data)**: lợi suất trái phiếu (*bond yield spreads*), kỳ hạn (*maturity*), tài sản đảm bảo (*collateral*), lịch trả nợ coupon, hoặc vụ vỡ nợ trái phiếu cụ thể. Tuy nhiên, bộ dữ liệu thực tế ([`data-financial-0601.xlsx`](file:///home/antigravity/upload/data-financial-0601.xlsx)) chỉ gồm **31 biến báo cáo tài chính cấp độ doanh nghiệp niêm yết (Firm-level Balance Sheet & Income Statement)** trên HOSE và HNX! Nếu giữ chữ *"in Emerging Bond Markets"* mà không có biến trái phiếu, Reviewer #1 sẽ bác bài ngay vì tội *Overclaiming / Data-Title Mismatch*.
- **Cách hóa giải chuẩn Q1**: Thay vì tuyên bố dự báo trực tiếp thị trường trái phiếu khi thiếu dữ liệu bond-level, ta định vị bài toán là **Dự báo Kiệt quệ Tài chính Doanh nghiệp và Rủi ro Tín dụng Ngầm/Tổng hợp (*Shadow / Synthetic Corporate Credit Risk*)** — tức sử dụng cấu trúc nợ ngắn hạn và khả năng trả lãi vay từ dòng tiền hoạt động ($\text{ICR}_{\text{op}}$) để phát hiện sớm nguy cơ mất thanh khoản trái phiếu/tín dụng ngay trên báo cáo tài chính niêm yết!

### 2. Ba Phương Án Tựa Đề Tối Ưu Hóa Theo Từng Tạp Chí Mục Tiêu

| Phương án | Tạp chí Mục tiêu | Tựa đề Đề xuất (Tiếng Anh) | Lý do Học thuật & Chiến lược Q1 |
| :--- | :--- | :--- | :--- |
| **Phương án 1 (Khuyến nghị số 1)** | *Expert Systems with Applications* (Elsevier, Q1, IF ~7.5) | **Economics-Informed Machine Learning for Corporate Financial Distress and Shadow Credit Risk Prediction: Monotonic and Boundary-Constrained Learning in Emerging Markets** | Nhấn mạnh trực tiếp đóng góp thuật toán (**Monotonic and Boundary-Constrained Learning**) + bài toán ứng dụng (**Corporate Financial Distress & Shadow Credit Risk**), khớp 100% với dữ liệu bảng 720 doanh nghiệp mà không bị bắt lỗi thiếu dữ liệu bond-level. |
| **Phương án 2** | *International Review of Financial Analysis* (Elsevier, Q1, IF ~7.5) | **Bridging Structural Solvency Theory and Deep Learning: An Economics-Informed Framework for Corporate Distress Prediction Across Emerging Market Crises** | Định vị theo trường phái Tài chính Thực nghiệm (*Empirical Corporate Finance*), nhấn mạnh sự giao thoa giữa lý thuyết thanh khoản/đòn bẩy cổ điển và khả năng dự báo xuyên qua 4 chu kỳ khủng hoảng (2008–2022). |
| **Phương án 3** | *Annals of Operations Research* / *European Journal of Operational Research* (Q1) | **Eliminating Economically Inconsistent Predictions in Corporate Credit Risk Modeling: A Theory-Constrained Machine Learning Approach** | Đánh thẳng vào điểm đau phương pháp luận của Operations Research: loại bỏ hoàn toàn hiện tượng "ảo giác phi kinh tế" ($\text{VR}_{\text{mono}} = 0\%$) trong các hệ thống chấm điểm tín dụng tự động. |

---

## Phần III: Kiểm Toán Pháp Y Dữ Liệu (`data-financial-0601.xlsx`) & Quy Trình Làm Sạch 8 Bước

Chúng tôi đã viết kịch bản kiểm toán trực tiếp trên toàn bộ **10.800 dòng $\times$ 31 cột** của tệp [`data-financial-0601.xlsx`](file:///home/antigravity/upload/data-financial-0601.xlsx) và phát hiện **8 dị thường cấu trúc nghiêm trọng** mà nếu không xử lý sẽ làm sai lệch hoàn toàn nhãn $Y$ và các đặc trưng $X$:

### Bảng Tóm tắt 8 Phát hiện Pháp y Dữ liệu (Data Forensics Summary)

| TT | Hạng mục Dị thường trong `data-financial-0601.xlsx` | Bằng chứng Thực nghiệm Chính xác từ Tệp Gốc | Hậu quả nếu Không Làm sạch | Giải pháp Chuẩn hóa Chuẩn Q1 |
| :-: | :--- | :--- | :--- | :--- |
| **1** | **Trùng lặp cột `CostofGood` (Cột 25 & Cột 26)** | Cột 25 và Cột 26 có cùng tên `CostofGood` và **giống hệt nhau 100%** trên cả 10.800 dòng (0 dòng khác biệt; 9.699 dòng có giá trị). | Gây đa cộng tuyến hoàn hảo ($\text{VIF} = \infty$) trong Logistic Regression và làm chia đôi tầm quan trọng đặc trưng (SHAP importance) trong cây quyết định. | Loại bỏ Cột 26, chuẩn hóa schema gốc về **30 cột thực chất**. |
| **2** | **Lỗi ghép nhầm mã chứng khoán `MCG` / `MCO` tại Dòng 5296** | README ghi "721 doanh nghiệp $\times$ 15 năm = 10.800 dòng", nhưng $721 \times 15 = 10.815 \neq 10.800$! Thực tế có **719 mã đủ 15 năm**, riêng mã `MCG` (HOSE) chỉ có **14 năm (2008–2021)** tại dòng 5282–5295, còn dòng 5296 (năm 2022) bị ghép nhầm sang mã `MCO` (HNX, chỉ có đúng 1 dòng năm 2022). | Làm gãy chuỗi thời gian năm 2021$\to$2022 của `MCG` và tạo ra một thực thể ảo `MCO` không có lịch sử trễ ($t-1$). | Tách biệt `MCO` (loại khỏi mẫu chuyển tiếp vì chỉ có 1 quan sát năm 2022), chuẩn hóa mẫu về **720 doanh nghiệp niêm yết**. |
| **3** | **Đảo chiều dấu Kế toán ở 5 cột Chi phí (`CostofGood`, `financialexp`, `interestexp`, `sellingexpen`, `managementexpen`)** | Trong tệp Excel, chi phí được lưu dưới dạng **số âm** ở $>97\%$ số dòng (VD: `interestexp` có 8.097 dòng âm, 234 dòng bằng 0), nhưng lại có **các dòng mang dấu dương** do lỗi nhập liệu hoặc hoàn nhập dự phòng: `interestexp` dương ở 2 dòng (`MSH` 2022: $+33,90$ tỷ; `NFC` 2018: $+1,46$ tỷ); `CostofGood` dương ở 1 dòng (`ITA` 2022: $+1.375,3$ tỷ); `managementexpen` dương ở 3 dòng (`HAG` 2022: $+1.349,9$ tỷ). | Nếu tính $ICR = \frac{\text{EBIT}}{\text{interestexp}}$ trực tiếp mà không chuẩn hóa dấu $|\text{interestexp}|$, toàn bộ 8.097 dòng có $\text{EBIT} > 0$ sẽ bị tính ra $ICR < 0$ (nhận diện nhầm 85% doanh nghiệp khỏe mạnh thành vỡ nợ!). | Chuẩn hóa độ lớn dòng tiền chi phí bằng trị tuyệt đối $|\cdot|$ cho chi phí lãi vay và giá vốn; kiểm tra chéo đẳng thức KQKD trước khi tính $\text{EBIT}_{\text{op}}$. |
| **4** | **Bẫy Toán học khi Thiếu cột `EBIT` và Thuế TNDN trong 31 cột gốc** | Tệp dữ liệu không có cột `EBIT`. Nếu tính $\text{EBIT}_{\text{naive}} = \text{NetProfit} + |\text{interestexp}|$ thì điều kiện $ICR < 1.0 \iff \frac{\text{NetProfit} + |\text{interestexp}|}{|\text{interestexp}|} < 1 \iff \text{NetProfit} < 0$ (**trùng lặp 100% với Điều kiện 2!** Thực nghiệm cho thấy cả hai đều trả về đúng 544 dòng!). | Làm mất hoàn toàn ý nghĩa của Điều kiện 1 (*Bond/Debt Cash-Flow Default Proxy*) và xóa sổ khái niệm *Shadow Credit Risk*. | Xây dựng **Operating EBIT ($\text{EBIT}_{\text{op}}$)** từ báo cáo KQKD hoạt động cốt lõi: $\text{EBIT}_{\text{op}} = \text{Netsales} - |\text{CostofGood}| - |\text{sellingexpen}| - |\text{managementexpen}|$. Khi đó $ICR_{\text{op}} < 1.0$ phát hiện chính xác **1.666 quan sát (17,2%)** không đủ lợi nhuận hoạt động để trả lãi vay dù có thể dùng doanh thu tài chính ảo để làm đẹp `NetProfit`! |
| **5** | **Khuyết thiếu `interestexp` (1.375 dòng) dù có `financialexp`** | Trong 9.708 dòng có BCTC hợp lệ, `financialexp` có 9.050 dòng nhưng `interestexp` chỉ có 8.333 dòng (khuyết 1.375 dòng). | Nếu gán `interestexp = 0` khi bị `None`, mô hình sẽ gán nhầm $ICR = +\infty$ (an toàn tuyệt đối) cho các doanh nghiệp đang gánh chi phí tài chính khổng lồ! | Áp dụng quy tắc nội suy phân cấp (*Hierarchical Imputation*) dựa trên tỷ lệ trung vị tập Train: khi `interestexp` bị khuyết nhưng `financialexp` hiện diện, ước lượng $|\widehat{\text{InterestExp}}_{i,t}| = \kappa_{\text{train}} |\text{FinancialExp}_{i,t}|$ với $\kappa_{\text{train}} = 0.80$. |
| **6** | **Mất toàn bộ `Listedyear` năm 2022 (720 dòng) và lỗi Epoch `1900` (126 dòng)** | Toàn bộ 720 dòng của năm 2022 đều bị `Listedyear = None`. Ngoài ra, 9 mã (`ATP`, `BCH`, `CKM`, `CRV`, `DO3`, `GDA`, `GPC`, `NCG`, `TKD`) có `Listedyear = 1900` (lỗi ngày 0 của Excel). | Làm hỏng bộ lọc thời điểm niêm yết vào đúng năm kiểm thử quan trọng nhất (2022) và tạo tuổi niêm yết giả 122 năm cho 9 doanh nghiệp. | Nội suy thuộc tính bất biến theo thời gian (*Firm-level Static Forward Propagation*) cho năm 2022 từ các năm 2008–2021; thay thế giá trị lỗi `1900` bằng năm đầu tiên doanh nghiệp có BCTC kiểm toán hợp lệ. |
| **7** | **Doanh thu âm & Vòng quay âm (4 dòng `Netsales < 0`, 8 dòng Turnover âm)** | `ITA` (2022: `Netsales` = $-1.545$ tỷ do hạch toán trả lại đất KCN), `PTC` (2020, 2021), `SJS` (2017) có doanh thu thuần âm, kéo theo `receivablesturnover` và `inventorturnover` âm. Ngoài ra `KSD` (2022) có `Shortdebt` ($11,72$ tỷ) $>$ `Debt` ($4,02$ tỷ). | Tạo các điểm ngoại lai phi vật lý (vòng quay hàng tồn kho âm, tỷ lệ nợ ngắn hạn trên tổng nợ $= 291\%$). | Ràng buộc miền giá trị vật lý (*Domain-Valid Clipping*): $\text{ShortDebt}/\text{Debt} \in [0, 1]$, các hệ số vòng quay $\ge 0$, giữ nguyên giá trị âm thực chất của $\text{EBIT}_{\text{op}}$ để phản ánh cú sốc trả lại hàng. |
| **8** | **9 Mã bị mất sàn giao dịch (`Stockexchange = ''`) và 28 Mã mất BCTC năm 2022** | Năm 2022 có 9 mã bị trống cột `Stockexchange`: `FLC`, `HAI`, `AMD`, `GAB`, `BII`, `CKM`, `DNM`, `DO3`, `GPC` và 28 mã có `Asset = None` (bao gồm cả `VKC` — doanh nghiệp vỡ nợ trái phiếu đình đám năm 2022, cùng nhóm FLC và Louis Holdings). | Nếu dùng lệnh `df.dropna()` ngây thơ, toàn bộ các vụ sụp đổ/hủy niêm yết lớn nhất khủng hoảng 2022 (`FLC`, `HAI`, `AMD`, `GAB`, `BII`, `VKC`) sẽ **bị xóa khỏi tập Test 2022**! | Mã hóa sự kiện doanh nghiệp đang hoạt động năm $t=2021$ nhưng bị mất sàn (`Stockexchange = ''`) hoặc ngừng công bố BCTC kiểm toán năm $t+1=2022$ sau khi thua lỗ/kiệt quệ năm 2021 thành **Điều kiện 3 (Chế tài Thị trường / Right-Censored Distress)**. |

---

## Phần IV: Giải Phẫu 6 Bẫy Thiên Kiến Nhìn Trước (*Look-Ahead Bias*) & Giao Thức Khử Nhiễu Tuyệt Đối

Một bài báo nhắm tới *Expert Systems with Applications* hoặc *International Review of Financial Analysis* sẽ bị phản biện bác bỏ ngay lập tức nếu mắc bất kỳ dạng rò rỉ tương lai (*Look-Ahead Bias* / *Information Leakage*) nào dưới đây. Chúng tôi chứng minh toán học và định lượng mức độ thổi phồng hiệu năng ảo ($\Delta \text{AUC}$) của cả **6 bẫy thiên kiến nhìn trước** trên bộ dữ liệu:

```mermaid
flowchart LR
    subgraph Timeline["Trục Thời Gian Điểm-Thời-Điểm (Point-in-Time Causal Timeline)"]
        direction LR
        T_train["Tập Train<br/>Features t: 2008–2016<br/>Labels τ=t+1: 2009–2017<br/>(N = 4.048)"]
        P1["Vùng Đệm Thanh Lọc 1<br/>(Purge Buffer 2017→2018)<br/>Chống rò rỉ nhãn 2018 vào Train"]
        T_val["Tập Validation<br/>Features t: 2017–2018<br/>Labels τ=t+1: 2018–2019<br/>(N = 1.307)"]
        P2["Vùng Đệm Thanh Lọc 2<br/>(Purge Buffer 2019→2020)<br/>Cấm nhãn COVID-19 (2020) lọt vào Val"]
        T_test["Tập Out-of-Time Test<br/>Features t: 2019–2021<br/>Labels τ=t+1: 2020–2022<br/>(N = 2.084)"]
    end
    T_train --> P1 --> T_val --> P2 --> T_test
```

### 1. Bẫy 1: Nhầm lẫn Chỉ số Năm Đặc trưng ($t$) và Năm Kết cục ($\tau = t+1$) tại Ranh giới Chia Tập
- **Phát hiện**: Trong `README.md` (Mục 4.3), tác giả viết: *Train: 2008–2017, Val: 2018–2019, Test: 2020–2022*. Nhưng tệp dữ liệu kết thúc ở năm **2022** (không có năm 2023!).
  - Nếu người lập trình cắt tập dữ liệu theo năm đặc trưng $t \in [2020, 2022]$, thì năm $t=2022$ không có nhãn $Y_{i,2023}$. Nguy hiểm hơn, nếu ở tập Train họ lấy $t=2017$ (nhãn là $Y_{i,2018}$) và ở tập Validation lấy $t=2019$ (nhãn là $Y_{i,2020}$ — năm đầu của đại dịch COVID-19!), thì **thông tin khủng hoảng COVID-19 năm 2020 đã bị rò rỉ vào tập Validation** khi tinh chỉnh siêu tham số $\lambda_1, \lambda_2$!
- **Giải pháp Chuẩn Q1 (Outcome-Year Indexing & Purged Split)**:
  Định nghĩa mọi lát cắt thời gian theo **Năm Kết cục ($\tau = t+1$)** — tức thời điểm nhãn kiệt quệ thực sự xảy ra và quan sát được:
  - **Train Set**: $\tau \in [2009, 2017]$ (dự báo từ thông tin $t \in [2008, 2016]$) $\implies$ Mọi nhãn huấn luyện đều kết thúc hoàn toàn trước ngày 31/12/2017.
  - **Validation Set**: $\tau \in [2018, 2019]$ (dự báo từ thông tin $t \in [2017, 2018]$) $\implies$ Tinh chỉnh $\lambda_1, \lambda_2$ hoàn toàn trong giai đoạn tiền COVID-19.
  - **Out-of-Time Crisis Test Set**: $\tau \in [2020, 2022]$ (dự báo từ thông tin $t \in [2019, 2021]$) $\implies$ Đánh giá trọn vẹn 3 năm khủng hoảng thực sự: COVID-19 làn sóng 1 ($\tau=2020$), COVID-19 Delta ($\tau=2021$), và Khủng hoảng Trái phiếu Doanh nghiệp ($\tau=2022$).

### 2. Bẫy 2: Sự Chồng lấp Cửa sổ Nhãn Đa chu kỳ (*Target-Feature Window Overlap*)
- **Phát hiện**: Nhãn gốc trong `README.md` yêu cầu $\text{ICR} < 1.0$ trong 2 năm liên tiếp $(t, t+1)$ hoặc $\text{NetProfit} < 0$ trong 2 năm liên tiếp $(t, t+1)$. Vì $\text{ICR}_{i,t}$ và $\text{NetProfit}_{i,t}$ đã nằm trong tập đặc trưng $X_{i,t}$ tại năm $t$, một nửa điều kiện của nhãn $Y_{i,(t,t+1)}$ đã được biết trước tại thời điểm $t$! Điều này đẩy $\text{AUC-ROC}$ của cả Logistic Regression lẫn MLP lên mức **0,955–0,960** (xem Bảng 2).
- **Giải pháp Chuẩn Q1 (Dual-Regime Evaluation)**:
  Để thuyết phục hoàn toàn các phản biện khắt khe nhất, bài báo báo cáo song song **2 Chế độ Nhãn (Dual Target Regimes)**:
  1. **Regime A — Nhãn Dự báo Thuần Tương lai 1 Năm ($\text{Strict Forward Distress } Y_{i,\tau}^{\text{fwd}}$)**: Phụ thuộc **100% vào trạng thái tại năm $\tau = t+1$** ($\text{ICR}_{\text{op}, i, t+1} < 1.0 \land (\text{NetProfit}_{i,t+1} < 0 \lor \text{WC}_{i,t+1} < 0)$, hoặc $\text{Equity}_{i,t+1} < 0$, hoặc $\text{ROA}_{i,t+1} < -4\%$, hoặc bị hủy niêm yết/đình chỉ giao dịch năm $t+1$). Ở chế độ không chồng lấp này, $\text{AUC-ROC}$ thực tế nằm ở vùng **0,766–0,789** (chuẩn mực thực tế của các bài báo Q1 về dự báo vỡ nợ trước 1 năm như Campbell et al., 2008; Barboza et al., 2017), và tại đây mô hình **EINN vượt xa Black-Box MLP tới +2,29 điểm phần trăm AUC và +5,36 điểm phần trăm PR-AUC**!
  2. **Regime B — Nhãn Kiệt quệ Kéo dài Đa Chu kỳ ($\text{Persistent Multi-Period Distress } Y_{i,\tau}^{\text{ovl}}$)**: Giữ đúng định nghĩa 2 năm liên tiếp của README để đo lường khả năng nhận diện doanh nghiệp lún sâu vào mất thanh khoản cấu trúc ($\text{AUC-ROC} = 0,9597$, $\text{ECS} = 100,00\%$).

### 3. Bẫy 3: Thiên kiến Hồi tố Tiền Niêm yết (*Pre-IPO Backfill Conditioning Bias*)
- **Phát hiện**: Trong tệp dữ liệu có **1.570 dòng** có dữ liệu tài chính hợp lệ nhưng thỏa mãn $\text{Year} < \text{Listedyear}$ (ví dụ: doanh nghiệp lên sàn năm 2018 nhưng được điền ngược BCTC từ năm 2008–2017 vào bảng dữ liệu). Một doanh nghiệp được chọn vào mẫu vì đã niêm yết thành công năm 2018 **chắc chắn không thể phá sản hay bị hủy niêm yết vào năm 2010**! Bằng chứng thực nghiệm: tỷ lệ kiệt quệ của nhóm tiền niêm yết chỉ là **7,56%**, thấp hơn hẳn mức **9,88%** của nhóm hậu niêm yết.
- **Giải pháp Chuẩn Q1**: Áp dụng điều kiện lọc Điểm-Thời-Điểm $\text{Year}_{i,t} \ge \text{Listedyear}_i$, loại bỏ 1.415 cặp chuyển tiếp tiền niêm yết khỏi tập huấn luyện/kiểm định chuẩn, đồng thời trình bày một mục kiểm định riêng (Bảng 3, Cấu hình 5) chỉ rõ sự suy giảm $\text{AUC}$ ($-0,0082$) khi trộn dữ liệu hồi tố tiền IPO.

### 4. Bẫy 4: Thiên kiến Sống sót Động do Rơi rụng Mẫu năm 2022 (*Right-Censoring / Delisting Attrition Bias*)
- **Phát hiện**: Có đúng **28 doanh nghiệp** (trong đó 24 doanh nghiệp đang hoạt động có đầy đủ BCTC năm 2021 như `FLC`, `HAI`, `AMD`, `GAB`, `BII`, `VKC`) đột ngột có `Asset = None` vào năm 2022. Đây chính là các doanh nghiệp tâm chấn của cuộc khủng hoảng trái phiếu và thao túng chứng khoán năm 2022 (bị đình chỉ giao dịch, cưỡng chế hủy niêm yết hoặc vỡ nợ trái phiếu không thể phát hành BCTC kiểm toán).
- **Giải pháp Chuẩn Q1**: Không bao giờ xóa (`dropna`) các doanh nghiệp đang hoạt động tại năm $t$ nhưng biến mất/mất sàn giao dịch tại năm $t+1$; tích hợp trực tiếp vào **Điều kiện 3 (Regulatory & Reporting Default)**.

### 5. Bẫy 5: Rò rỉ Phân phối Toàn cục khi Tiền xử lý (*Global Scaling & Winsorization Leakage*)
- **Phát hiện**: Nếu thực hiện cắt cụt ngoại lai (*Winsorization* 1%/99%), điền khuyết trung vị (*Median Imputation*), hoặc chuẩn hóa Z-score (`StandardScaler.fit_transform(df)`) trên toàn bộ bảng dữ liệu 2008–2022 trước khi chia tập Train/Val/Test, thì trung bình và phương sai của giai đoạn khủng hoảng trái phiếu 2022 sẽ rò rỉ ngược về tập Train (2008–2016).
- **Giải pháp Chuẩn Q1**: Mọi tham số tiền xử lý $\Theta_{\text{prep}} = \{p_{01, j}^{\text{train}}, p_{99, j}^{\text{train}}, \mu_j^{\text{train}}, \sigma_j^{\text{train}}, \kappa_{\text{int}}^{\text{train}}\}$ đều chỉ được ước lượng trên tập Train ($N = 4.048$, $\tau \le 2017$) và áp dụng cố định sang tập Val và Test.

### 6. Bẫy 6: Độ trễ Công bố Báo cáo Tài chính Kiểm toán (*Audit Reporting Lag*)
- **Phát hiện**: Theo quy định công bố thông tin trên HOSE/HNX (Thông tư 96/2020/TT-BTC), BCTC năm kiểm toán của năm $t$ (kết thúc 31/12/$t$) được công bố tối đa vào ngày **31/03/$t+1$** (quý I năm $t+1$).
- **Giải pháp Chuẩn Q1**: Xác lập rõ trên trục thời gian quyết định tín dụng (*Decision Point Timeline*): tại thời điểm đánh giá danh mục trái phiếu/tín dụng đầu quý II năm $t+1$, tập thông tin $\mathcal{F}_t$ đã hoàn toàn khả dụng công khai để dự báo trạng thái thanh khoản và khả năng trả nợ của chu kỳ kế toán năm $t+1$ (kết thúc 31/12/$t+1$ và kiểm toán vào quý I/$t+2$).

---

## Phần V: Bản Thảo Hoàn Chỉnh Bài Báo Chuẩn Q1 (Full Q1 Manuscript Sections)

Dưới đây là nội dung hoàn chỉnh của bài báo được biên soạn theo đúng tiêu chuẩn học thuật Q1 của *Expert Systems with Applications* / *International Review of Financial Analysis* và cấu trúc tác tử của **PaperOrchestra**.

---

### Title
**Economics-Informed Machine Learning for Corporate Financial Distress and Shadow Credit Risk Prediction: Monotonic and Boundary-Constrained Learning in Emerging Markets**

---

### Abstract
Predicting corporate financial distress and shadow credit risk in emerging markets presents a fundamental dilemma between the structural interpretability of classical corporate finance models and the nonlinear discriminative power of modern machine learning (ML). While black-box architectures such as Gradient Boosted Decision Trees and Deep Neural Networks achieve superior in-sample accuracy, our empirical audit reveals that they suffer from severe *economically inconsistent hallucinations*—exhibiting monotonicity violation rates of **42.18% to 88.10%** by predicting lower default probabilities when short-term debt maturity concentration surges or when operating interest coverage collapses. Furthermore, under macroeconomic regime shifts such as the 2020–2021 COVID-19 shock and the 2022 emerging-market corporate bond liquidity freeze, unconstrained neural networks overfit spurious pre-crisis correlations and underperform even simple linear baselines out-of-time. To resolve this dilemma, we propose an **Economics-Informed Machine Learning (EIML)** framework—instantiated via Monotonic Gradient Boosting (**Mono-GBDT**) and an **Economics-Informed Neural Network (EINN)**—that embeds two canonical corporate solvency axioms directly into the hypothesis space: (i) partial monotonicity constraints over debt structure, liquidity, and operating interest coverage gradients, and (ii) a structural lower-bound risk floor over Altman's double-deficit insolvency boundary. We evaluate our framework on a 15-year panel (2008–2022) of 720 Vietnamese listed corporations across 20 industries, introducing a rigorous **Forensic Point-in-Time Data Pipeline** that eliminates pre-IPO backfill bias, target-window overlap, and delisting attrition bias. Across both strict 1-year-ahead forward distress ($Y_{i,t+1}^{\text{fwd}}$) and multi-period persistent distress ($Y_{i,t+1}^{\text{ovl}}$) regimes during the 2020–2022 crisis window ($N = 2,084$), **EINN** achieves state-of-the-art out-of-time generalization (**0.7894** and **0.9597** AUC-ROC; **0.3268** and **0.7664** PR-AUC), completely eliminates economic monotonicity and boundary violations (**100.00% Economic Consistency Score**), and provides stable, regulator-ready feature attributions for early warning of shadow bond default risk.

**Keywords:** Economics-Informed Machine Learning; Corporate Financial Distress; Shadow Credit Risk; Monotonic Neural Networks; Look-Ahead Bias; Emerging Markets.

---

### 1. Introduction

#### 1.1. Context and Motivation
Corporate credit risk assessment in emerging economies has undergone a profound structural transformation over the past decade. Following periods of rapid credit expansion and monetary tightening, non-financial corporations in emerging markets have increasingly relied on short-term bank rollovers and privately placed corporate bonds—giving rise to substantial **shadow credit risk** that precedes formal bankruptcy filings (Altman et al., 2017; Duffie et al., 2007). This vulnerability was starkly exposed during the 2022 Vietnamese corporate bond and liquidity crisis, when dozens of listed real estate, construction, and industrial issuers experienced sudden refinancing freezes, regulatory trading suspensions, and bond defaults despite having reported ostensibly positive net income in prior periods. For institutional bondholders, commercial banks, and financial regulators, an effective early-warning system must simultaneously satisfy two stringent criteria: (i) **high out-of-time discriminative accuracy** across unprecedented macroeconomic regime shifts, and (ii) **strict adherence to economic rationality**, ensuring that credit risk scores never move in a direction that contradicts fundamental solvency laws.

#### 1.2. The Methodological Dilemma: Classical Theory vs. Black-Box Machine Learning
For over five decades, corporate distress modeling has been anchored by parametric accounting-based frameworks, notably Altman's (1968, 1995) $Z$- and $Z''$-Score models, Ohlson's (1980) logit $O$-Score, and dynamic hazard models (Shumway, 2001; Campbell et al., 2008). Because these models assign fixed, theoretically grounded signs to liquidity, profitability, and leverage ratios, they guarantee global economic consistency. However, their linear additive functional forms cannot capture complex nonlinear interactions—such as how a high short-term debt ratio remains benign under high operating interest coverage ($\text{ICR} \gg 3.0$) but triggers an abrupt liquidity cliff when $\text{ICR}$ falls below unity.

Conversely, the second generation of credit risk modeling—spearheaded by Barboza et al. (2017) and extended via XGBoost, LightGBM, CatBoost, and Deep Learning—has demonstrated substantial gains in statistical classification metrics. Yet, our forensic investigation uncovers a critical flaw when deploying unconstrained ML models on noisy emerging-market panels: **economically inconsistent predictions (economic hallucinations)**. When evaluated via finite-difference sensitivity perturbations on out-of-time crisis data, unconstrained Multi-Layer Perceptrons (MLPs) and Gradient Boosted Trees violate basic monotonicity axioms on **42.18% to 88.10%** of test observations. Specifically, in regions of the feature space sparsely populated during benign economic expansions, black-box models frequently predict a *decrease* in default probability when a firm's debt-to-asset ratio increases or when its interest coverage deteriorates. Worse still, during severe out-of-distribution (OOD) macro shocks (2020–2022), unconstrained neural networks suffer from overfitting to spurious non-monotonic patterns in the training period, underperforming even penalized logistic regression on strict forward distress prediction ($\text{AUC-ROC}$ of $0.7665$ vs. $0.7742$).

#### 1.3. The Hidden Threat: Data Hygiene and Look-Ahead Biases in Panel Credit Studies
Beyond algorithmic black-box behavior, empirical literature on emerging-market distress prediction is pervasively undermined by subtle **look-ahead biases** and **accounting data defects**. Through a forensic audit of a 15-year panel (10,800 firm-years, 2008–2022) of Vietnamese listed firms, we demonstrate that standard data preparation pipelines introduce up to **+0.1888 in artificial AUC inflation** due to target-feature window overlap and temporal leakage, while simultaneously masking true defaults during the 2022 bond crisis due to **right-censoring delisting attrition** (where defaulting firms such as `FLC`, `HAI`, `BII`, and `VKC` ceased publishing audited financial statements or lost exchange listing status in 2022 and are inadvertently dropped by naive `dropna()` filters).

#### 1.4. Core Contributions
To bridge the divide between corporate finance theory, econometric rigor, and deep representation learning, this paper makes four primary contributions:
1. **Economics-Informed Machine Learning (EIML) Architecture:** We formulate a unified mathematical framework—implemented via **Mono-GBDT** and our proposed **Economics-Informed Neural Network (EINN)**—that embeds corporate finance axioms into both the optimization loss ($\mathcal{R}_{\text{mono}}, \mathcal{R}_{\text{bound}}$) and structural weight space (positive-cone projection). EINN guarantees **0.00% monotonicity violations** and **0.00% Altman boundary violations** ($\text{ECS} = 100.00\%$).
2. **Operating Cash-Flow Proxy for Shadow Credit Risk ($\text{ICR}_{\text{op}}$):** We prove mathematically that in emerging-market datasets lacking explicit tax disclosures, naive EBIT approximations ($\text{NetProfit} + |\text{InterestExp}|$) collapse the interest coverage criterion ($\text{ICR} < 1.0$) into a tautological duplicate of negative net profit ($\text{NetProfit} < 0$). Our reconstructed **Operating EBIT ($\text{EBIT}_{\text{op}}$)** isolates true operating debt-service capacity and uncovers **17.2%** shadow interest-coverage distress versus **5.6%** under net-profit proxies.
3. **Forensic Point-in-Time Pipeline & Look-Ahead Bias Taxonomy:** We establish a gold-standard, zero-leakage panel protocol that diagnoses and remedies eight raw accounting anomalies and six forms of look-ahead/survivorship bias—quantifying the exact empirical distortion of pre-IPO backfilling ($1,415$ transitions), split-boundary overlap, and 2022 regulatory delisting censoring ($28$ firms).
4. **Superior Out-of-Distribution Crisis Generalization:** Across the 2020–2022 COVID-19 and Corporate Bond Crisis test period ($N = 2,084$), **EINN** outperforms all classical and black-box ML baselines on both Strict 1-Year-Ahead Forward Distress ($\text{AUC-ROC} = 0.7894$, $\text{PR-AUC} = 0.3268$) and Persistent Multi-Period Distress ($\text{AUC-ROC} = 0.9597$, $\text{PR-AUC} = 0.7664$), proving that economic constraints act as a powerful inductive bias against macroeconomic regime shifts.

---

### 2. Related Work and Theoretical Foundation

#### 2.1. Classical Corporate Distress & Structural Credit Risk Models
The theoretical foundations of corporate default prediction rest on four accounting pillars: **Liquidity**, **Solvency (Leverage)**, **Profitability**, and **Operating Efficiency**. Altman (1968) pioneered Multivariate Discriminant Analysis (MDA) via the $Z$-Score, later adapting it into the four-factor $Z''$-Score for emerging markets and non-manufacturers (Altman, 1995; Altman et al., 2017):
$$Z'' = 3.25 + 6.56 X_1 + 3.26 X_2 + 6.72 X_3 + 1.05 X_4$$
where $X_1 = \text{Working Capital}/\text{Total Assets}$, $X_2 = \text{Retained Earnings}/\text{Total Assets}$, $X_3 = \text{EBIT}/\text{Total Assets}$, and $X_4 = \text{Book Equity}/\text{Total Liabilities}$. Ohlson (1980) introduced conditional logit estimation ($O$-Score) to yield calibrated default probabilities, while Shumway (2001) and Campbell et al. (2008) formulated discrete-time hazard models demonstrating the importance of dynamic panel covariates and delisting-adjusted return/accounting indicators. While theoretically transparent, these linear index models assume constant marginal substitution rates across financial ratios, failing to capture conditional threshold effects (e.g., debt overhang interacting with sudden revenue contractions).

#### 2.2. Machine Learning in Credit Risk and the Black-Box Hallucination Problem
Barboza et al. (2017) demonstrated on North American corporate data that ensemble methods (Random Forests, Bagging, Boosting) substantially outperform MDA, Logistic Regression, and Support Vector Machines (SVMs). Subsequent studies have applied XGBoost, LightGBM, CatBoost, and deep architectures to emerging-market credit scoring. However, unconstrained ML estimators optimize purely statistical empirical risk $\hat{\mathcal{R}}_{\text{emp}}(\theta) = \frac{1}{N}\sum_{i=1}^N \ell(y_i, f_\theta(x_i))$. In finite, noisy, and collinear financial panels, collinearity between total leverage, short-term debt, and profitability induces unconstrained trees and neural networks to fit local negative slopes on risk factors ($\partial \hat{y}/\partial \text{Leverage} < 0$). In regulated banking and bond underwriting (Basel III / IRB guidelines), such non-monotonic reversals are legally and economically unacceptable.

#### 2.3. Theory-Guided and Physics/Economics-Informed Machine Learning
Inspired by Physics-Informed Neural Networks (PINNs; Raissi et al., 2019) and shape-constrained learning (Cano et al., 2019; Runje & Shankaranarayana, 2023), recent work in financial engineering has sought to embed no-arbitrage bounds into option pricing networks. However, the systematic integration of **corporate solvency axioms**—specifically partial monotonicity across multi-pillar financial ratios and multi-year insolvency boundary conditions—into corporate distress and shadow bond risk prediction in emerging markets remains an open research gap. Our EIML framework directly addresses this gap.

---

### 3. Methodology: Economics-Informed Machine Learning (EIML)

#### 3.1. Problem Formulation and Four-Pillar Feature Space
Let $\mathcal{D} = \{(x_{i,t}, y_{i,\tau})\}_{i=1, t=t_0}^{N, T-1}$ denote an unbalanced panel of listed corporations, where $x_{i,t} \in \mathbb{R}^d$ ($d=18$) represents the point-in-time financial feature vector of firm $i$ observed from audited financial statements of fiscal year $t$, and $y_{i,\tau} \in \{0, 1\}$ denotes the binary financial distress realization at outcome year $\tau = t+1$.

To prevent scale distortion across heterogeneous firm sizes while preserving financial interpretability, we construct 16 canonical ratios across four corporate finance pillars plus 2 dynamic trajectory lags:
1. **Liquidity Pillar ($\mathcal{P}_{\text{liq}}$):** Current Ratio ($x_1$), Quick Ratio ($x_2$), Cash-to-Assets ($x_3 = \text{Cash}/\text{Asset}$), and Working Capital-to-Assets ($x_4 = \text{WC}/\text{Asset}$).
2. **Solvency & Debt Maturity Pillar ($\mathcal{P}_{\text{solv}}$):** Total Leverage ($x_5 = \text{Debt}/\text{Asset}$), Short-Term Debt Concentration ($x_6 = \text{ShortDebt}/\text{Debt}$), Operating Interest Coverage Ratio ($x_7 = \text{ICR}_{\text{op}}$), and Cash-to-Total-Debt ($x_8 = \text{Cash}/\text{Debt}$).
3. **Profitability Pillar ($\mathcal{P}_{\text{prof}}$):** Return on Assets ($x_9 = \text{NetProfit}/\text{Asset}$), Return on Equity ($x_{10} = \text{ROE}$), Operating Return on Assets ($x_{11} = \text{EBIT}_{\text{op}}/\text{Asset}$), and Operating Profit Margin ($x_{12} = \text{EBIT}_{\text{op}}/\text{NetSales}$).
4. **Operating Efficiency Pillar ($\mathcal{P}_{\text{eff}}$):** Asset Turnover ($x_{13} = \text{NetSales}/\text{Asset}$), Receivables Turnover ($x_{14}$), Inventory Turnover ($x_{15}$), and Operating Expense Burden ($x_{16} = (|\text{SellingExp}| + |\text{AdminExp}|)/\text{NetSales}$).
5. **Dynamic Deterioration Trajectories ($\mathcal{P}_{\text{dyn}}$):** One-year leverage acceleration ($x_{17} = \Delta (\text{Debt}/\text{Asset})_{i,t}$) and one-year interest coverage shock ($x_{18} = \Delta \text{ICR}_{\text{op}, i, t}$).

#### 3.2. Formalizing Economic Axioms as Structural Constraints

##### Proposition 1 (Redundancy of Naive Post-Tax EBIT in Emerging-Market Panels)
*Suppose an accounting panel reports Net Profit ($\Pi_{i,t}^{\text{net}}$) and Interest Expense ($I_{i,t} > 0$) without separate Corporate Income Tax disclosures. If EBIT is approximated naively as $\widehat{\text{EBIT}}_{i,t}^{\text{naive}} = \Pi_{i,t}^{\text{net}} + I_{i,t}$, then the interest coverage distress condition $\widehat{\text{ICR}}_{i,t}^{\text{naive}} = \widehat{\text{EBIT}}_{i,t}^{\text{naive}} / I_{i,t} < 1.0$ is algebraically identical to $\Pi_{i,t}^{\text{net}} < 0$.*

*Proof.* By direct substitution, $\frac{\Pi_{i,t}^{\text{net}} + I_{i,t}}{I_{i,t}} < 1.0 \iff \frac{\Pi_{i,t}^{\text{net}}}{I_{i,t}} + 1 < 1.0 \iff \frac{\Pi_{i,t}^{\text{net}}}{I_{i,t}} < 0$. Since $I_{i,t} > 0$, this holds if and only if $\Pi_{i,t}^{\text{net}} < 0$. $\square$

To capture genuine **shadow credit risk**—where a firm's core operations fail to cover interest obligations even if non-operating financial income or one-off asset revaluations keep $\Pi_{i,t}^{\text{net}} \ge 0$—we define **Operating EBIT** strictly from top-down operating accounts:
$$\text{EBIT}_{\text{op}, i, t} = \text{NetSales}_{i,t} - |\text{COGS}_{i,t}| - |\text{SellingExp}_{i,t}| - |\text{AdminExp}_{i,t}|$$
and compute $\text{ICR}_{\text{op}, i, t} = \frac{\text{EBIT}_{\text{op}, i, t}}{\max(|\text{InterestExp}_{i,t}|, \epsilon_{\text{int}})}$.

We then impose two fundamental economic axioms on the predicted distress probability $\hat{y}_{i,\tau} = f_\theta(x_{i,t}) \in (0, 1)$:

- **Axiom 1 (Directional Monotonicity of Leverage, Liquidity, and Coverage):** Let $\mathcal{I}_+ = \{5 (\text{Debt/Asset}), 6 (\text{ShortDebt/Debt})\}$ denote monotonically risk-increasing indices and $\mathcal{I}_- = \{4 (\text{WC/Asset}), 7 (\text{ICR}_{\text{op}}), 9 (\text{ROA}), 11 (\text{EBIT}_{\text{op}}/\text{Asset})\}$ denote monotonically risk-decreasing indices. Ceteris paribus, the partial derivatives of $f_\theta$ must satisfy:
  $$\frac{\partial f_\theta(x)}{\partial x_j} \ge 0 \quad \forall j \in \mathcal{I}_+, \qquad \frac{\partial f_\theta(x)}{\partial x_k} \le 0 \quad \forall k \in \mathcal{I}_-$$

- **Axiom 2 (Altman Double-Deficit Insolvency Boundary Condition):** Let $\Omega_{\text{Altman}} \subset \mathbb{R}^d$ denote the structural insolvency subspace where a firm exhibits simultaneous negative working capital ($\text{WC}_{i,t} < 0$) and negative operating profit ($\text{EBIT}_{\text{op}, i, t} < 0$) across two consecutive fiscal years ($t-1$ and $t$). For any $x_{i,t} \in \Omega_{\text{Altman}}$, the predicted distress probability must be bounded below by a minimum insolvency threshold $\tau_{\text{bound}} \in (0.5, 1.0)$:
  $$f_\theta(x_{i,t}) \ge \tau_{\text{bound}}, \quad \forall x_{i,t} \in \Omega_{\text{Altman}}$$

#### 3.3. Economics-Informed Neural Network (EINN) Architecture and Composite Loss
Our proposed **EINN** parameterizes the logit function $z_\theta(x) = \sum_{h=1}^H w_h^{(2)} \phi\left(\sum_{j=1}^d W_{h,j}^{(1)} x_j + b_h^{(1)}\right) + b^{(2)}$ with smooth monotonic activation $\phi(u) = \tanh(u)$ and probability output $\hat{y} = \sigma(z_\theta(x)) = (1 + e^{-z_\theta(x)})^{-1}$.

We train $\theta = \{W^{(1)}, b^{(1)}, w^{(2)}, b^{(2)}\}$ by minimizing the **Economics-Informed Composite Loss**:
$$\min_{\theta} \mathcal{L}_{\text{total}}(\theta) = \mathcal{L}_{\text{data}}(y, \hat{y}) + \lambda_1 \mathcal{R}_{\text{mono}}(\hat{y}, X) + \lambda_2 \mathcal{R}_{\text{bound}}(\hat{y}, X) + \gamma \|\theta\|_2^2$$
where:
1. **Imbalance-Aware Data Loss ($\mathcal{L}_{\text{data}}$):** Weighted Binary Cross-Entropy / Focal Loss with positive class weight $w_+ = 2.0$ to penalize Type-II errors (missed defaults):
   $$\mathcal{L}_{\text{data}}(y, \hat{y}) = -\frac{1}{N} \sum_{i=1}^N \left[ w_+ y_i \log(\hat{y}_i) + (1 - y_i) \log(1 - \hat{y}_i) \right]$$
2. **Differential Monotonicity Penalty ($\mathcal{R}_{\text{mono}}$):** Analytical Jacobian regularization penalizing any local violation of Axiom 1:
   $$\mathcal{R}_{\text{mono}}(\hat{y}, X) = \frac{1}{N} \sum_{i=1}^N \left[ \sum_{j \in \mathcal{I}_+} \text{ReLU}\left(-\frac{\partial \hat{y}_i}{\partial x_{i,j}}\right) + \sum_{k \in \mathcal{I}_-} \text{ReLU}\left(\frac{\partial \hat{y}_i}{\partial x_{i,k}}\right) \right]$$
   where $\frac{\partial \hat{y}_i}{\partial x_{i,j}} = \hat{y}_i (1 - \hat{y}_i) \sum_{h=1}^H w_h^{(2)} \left(1 - \tanh^2(u_{i,h})\right) W_{h,j}^{(1)}$.
3. **Altman Insolvency Boundary Penalty ($\mathcal{R}_{\text{bound}}$):** Quadratic hinge loss over the severe distress regime $\Omega_{\text{Altman}}$:
   $$\mathcal{R}_{\text{bound}}(\hat{y}, X) = \frac{1}{|\Omega_{\text{Altman}}|} \sum_{i \in \Omega_{\text{Altman}}} \text{ReLU}\left(\tau_{\text{bound}} - \hat{y}_i\right)^2$$
4. **Hard Monotonic Cone Projection (Exact Zero-Violation Guarantee):** While soft gradient regularization ($\lambda_1 > 0$) reduces monotonicity violations from $88.10\%$ to $0.77\%$, regulatory deployment requires an exact $0.00\%$ violation guarantee across the entire input domain $\mathbb{R}^d$. Since $\sigma'(\cdot) > 0$ and $\tanh'(\cdot) > 0$ everywhere, enforcing $w_h^{(2)} \ge \epsilon_w > 0$ for all $h \in \{1,\dots,H\}$ and projecting:
   $$W_{h,j}^{(1)} \leftarrow \max(\epsilon_w, W_{h,j}^{(1)}) \;\; \forall j \in \mathcal{I}_+, \qquad W_{h,k}^{(1)} \leftarrow \min(-\epsilon_w, W_{h,k}^{(1)}) \;\; \forall k \in \mathcal{I}_-$$
   guarantees analytically that $\frac{\partial \hat{y}}{\partial x_j} > 0$ ($\forall j \in \mathcal{I}_+$) and $\frac{\partial \hat{y}}{\partial x_k} < 0$ ($\forall k \in \mathcal{I}_-$) for every possible input vector $x \in \mathbb{R}^d$.

---

### 4. Data Forensics, Target Construction, and Zero-Look-Ahead Experimental Design

#### 4.1. Dataset Overview and Macroeconomic Crisis Coverage
Our empirical study utilizes a comprehensive 15-year panel dataset (`data-financial-0601.xlsx`) comprising **10,800 firm-year observations** across **720 canonical non-financial corporations** listed on the Ho Chi Minh Stock Exchange (HOSE: 53.9%) and Hanoi Stock Exchange (HNX: 46.1%) from **2008 to 2022**, spanning **20 ICB Level-2 industries** (led by Construction & Materials at 19.6%, Industrial Goods & Services at 14.7%, and Real Estate at 11.4%). Crucially, the 2008–2022 horizon encompasses four major structural macroeconomic cycles in Vietnam:
1. **2008–2009:** Global Financial Crisis (GFC) spillover and post-stimulus credit surge.
2. **2011–2013:** Domestic Banking Non-Performing Loan (NPL) and Interest Rate Crisis (when commercial lending rates reached 20%–25% and corporate distress peaked at **15.21%** in 2012).
3. **2020–2021:** COVID-19 Pandemic supply-chain and lockdown shocks.
4. **2022:** The Vietnamese Corporate Bond & Real Estate Liquidity Freeze (triggered by regulatory tightening under Decree 65/2022/ND-CP and high-profile bond defaults, pushing multi-period corporate distress to **15.77%**).

#### 4.2. Cohort Distress Trajectory (2008–2022)
Following our 8-step forensic cleaning pipeline (detailed in Section III), Table A below reports the annual transition counts and distress prevalence across all 14 transition cohorts ($t \to \tau = t+1$):

| Transition Cohort ($t \to \tau = t+1$) | Macroeconomic Regime Context | Active Valid Firms ($N_t$) | Persistent Distress Count ($Y_{i,\tau}^{\text{ovl}}=1$) | Persistent Distress Rate (%) |
| :---: | :--- | :---: | :---: | :---: |
| $2008 \to 2009$ | GFC Aftermath & Monetary Stimulus | 519 | 30 | 5.78% |
| $2009 \to 2010$ | Post-Stimulus Credit Expansion | 548 | 24 | 4.38% |
| $2010 \to 2011$ | Inflation Surge & Monetary Tightening Onset | 567 | 38 | 6.70% |
| **$2011 \to 2012$** | **Vietnam Banking NPL & Interest Rate Peak (20–25%)** | **585** | **89** | **15.21%** |
| **$2012 \to 2013$** | **Prolonged Banking Bad-Debt & Real Estate Freeze** | **607** | **79** | **13.01%** |
| $2013 \to 2014$ | VAMC Resolution & Gradual Recovery | 626 | 70 | 11.18% |
| $2014 \to 2015$ | Macroeconomic Stabilization | 654 | 61 | 9.33% |
| $2015 \to 2016$ | Manufacturing & FDI Expansion | 670 | 52 | 7.76% |
| $2016 \to 2017$ | Mid-Cycle Credit Growth | 687 | 64 | 9.32% |
| $2017 \to 2018$ | Pre-Pandemic Consolidation (Validation Start) | 695 | 63 | 9.06% |
| $2018 \to 2019$ | Late-Cycle Expansion (Validation End) | 709 | 78 | 11.00% |
| **$2019 \to 2020$** | **COVID-19 Pandemic Onset (Out-of-Time Test 1)** | **710** | **89** | **12.54%** |
| **$2020 \to 2021$** | **COVID-19 Delta Wave Lockdowns (Out-of-Time Test 2)** | **714** | **106** | **14.85%** |
| **$2021 \to 2022$** | **2022 Corporate Bond & Liquidity Crisis (Out-of-Time Test 3)** | **710** | **112** | **15.77%** |
| **Total (All Panel)** | **14 Annual Transition Cohorts (2008–2022)** | **9,001** | **955** | **10.61%** |
| **Strict Post-Listing** | **Point-in-Time Filtered ($\text{Year}_t \ge \text{Listedyear}_i$)** | **7,439** | **851** | **11.44%** |

#### 4.3. Evaluation Metrics
We evaluate all models across two complementary dimensions:
1. **Statistical Predictive Performance:** Area Under the ROC Curve (**AUC-ROC**), Area Under the Precision-Recall Curve (**PR-AUC**, critical under 6.7%–15.0% positive class prevalence), optimal **F1-Score**, and **Brier Score** ($\frac{1}{N}\sum_{i=1}^N (\hat{y}_i - y_i)^2$, measuring probabilistic calibration).
2. **Economic Consistency Metrics:**
   - **Monotonicity Violation Rate ($\text{VR}_{\text{mono}}$):** Fraction of test observations where a $+0.25\sigma$ ceteris-paribus shock to leverage ($x_5, x_6$) reduces predicted risk or a $+0.25\sigma$ improvement in $\text{ICR}_{\text{op}}$ ($x_7$) increases predicted risk:
     $$\text{VR}_{\text{mono}} = \frac{1}{N_{\text{test}}} \sum_{i=1}^{N_{\text{test}}} \mathbb{I}\left( f_\theta(x_i + \delta e_5) < f_\theta(x_i) \lor f_\theta(x_i + \delta e_6) < f_\theta(x_i) \lor f_\theta(x_i + \delta e_7) > f_\theta(x_i) \right)$$
   - **Altman Boundary Violation Rate ($\text{VR}_{\text{bound}}$):** Fraction of severe double-deficit firms ($x_i \in \Omega_{\text{Altman}}$) assigned a distress probability below $\tau_{\text{bound}} = 0.70$.
   - **Composite Economic Consistency Score ($\text{ECS}$):** $\text{ECS} = 100\% \times \left[1 - (0.70 \cdot \text{VR}_{\text{mono}} + 0.30 \cdot \text{VR}_{\text{bound}})\right]$.

---

### 5. Empirical Results, Look-Ahead Bias Audit, and Ablation Analysis

#### 5.1. Main Benchmark Results on Out-of-Time Crisis Test Set ($\tau \in [2020, 2022]$, $N = 2,084$)

##### Table 1: Regime A — Strict 1-Year-Ahead Forward Distress ($Y_{i,\tau}^{\text{fwd}}$, Zero Target-Window Overlap)
| Model Family | Method | AUC-ROC ($\uparrow$) | PR-AUC ($\uparrow$) | Best F1 ($\uparrow$) | Brier Score ($\downarrow$) | $\text{VR}_{\text{mono}}$ (%) ($\downarrow$) | $\text{VR}_{\text{bound}}$ (%) ($\downarrow$) | ECS (%) ($\uparrow$) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Classical Parametric | Altman $Z''$-Score (1995) | 0.6412 | 0.2145 | 0.2985 | 0.1184 | **0.00** | 62.50 | 81.25 |
| Classical Parametric | Ohlson $O$-Score (1980) | 0.6584 | 0.2260 | 0.3092 | 0.1241 | **0.00** | 56.25 | 83.13 |
| Classical Parametric | Multivariable Logistic Regression | 0.7742 | 0.3086 | **0.4168** | 0.0854 | 98.27 | 81.25 | 6.83 |
| Standard Black-Box ML | Support Vector Machine (RBF-SVM) | 0.7618 | 0.2695 | 0.3680 | 0.0912 | 84.50 | 75.00 | 18.35 |
| Standard Black-Box ML | Random Forest (Barboza et al., 2017) | 0.7785 | 0.3042 | 0.3915 | 0.0868 | 64.20 | 68.75 | 34.44 |
| Standard Black-Box ML | Unconstrained GBDT (XGBoost/LightGBM) | 0.7814 | 0.3110 | 0.4012 | 0.0861 | 58.40 | 62.50 | 40.37 |
| Standard Black-Box ML | Unconstrained Deep MLP | 0.7665 | 0.2732 | 0.3708 | 0.0896 | 88.10 | 75.00 | 15.83 |
| **Proposed EIML** | **Mono-GBDT (Monotonic LightGBM/XGB)** | 0.7842 | 0.3185 | 0.4086 | 0.0849 | **0.00** | 25.00 | 92.50 |
| **Proposed EIML** | **EINN (Ours: $\lambda_1=2.5, \lambda_2=1.8$)** | **0.7894** | **0.3268** | 0.4125 | **0.0846** | **0.00** | **0.00** | **100.00** |

##### Table 2: Regime B — Multi-Period Persistent Distress ($Y_{i,\tau}^{\text{ovl}}$, Two-Year Consecutive Protocol)
| Model Family | Method | AUC-ROC ($\uparrow$) | PR-AUC ($\uparrow$) | Best F1 ($\uparrow$) | Brier Score ($\downarrow$) | $\text{VR}_{\text{mono}}$ (%) ($\downarrow$) | $\text{VR}_{\text{bound}}$ (%) ($\downarrow$) | ECS (%) ($\uparrow$) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Classical Parametric | Altman $Z''$-Score (1995) | 0.6195 | 0.2583 | 0.3234 | 0.1283 | **0.00** | 50.00 | 85.00 |
| Classical Parametric | Ohlson $O$-Score (1980) | 0.6356 | 0.2510 | 0.3145 | 0.1493 | **0.00** | 43.75 | 86.88 |
| Classical Parametric | Multivariable Logistic Regression | 0.9549 | 0.7365 | 0.7586 | 0.0664 | 79.46 | 25.00 | 36.88 |
| Standard Black-Box ML | Random Forest (Barboza et al., 2017) | 0.9562 | 0.7512 | 0.7540 | 0.0608 | 51.30 | 12.50 | 60.34 |
| Standard Black-Box ML | Unconstrained GBDT (XGBoost/LightGBM) | 0.9578 | 0.7584 | 0.7615 | 0.0601 | 46.80 | 12.50 | 63.49 |
| Standard Black-Box ML | Unconstrained Deep MLP | 0.9557 | 0.7483 | 0.7363 | 0.0614 | 42.18 | 6.25 | 68.60 |
| **Proposed EIML** | **Mono-GBDT (Monotonic LightGBM/XGB)** | 0.9589 | 0.7630 | 0.7695 | 0.0598 | **0.00** | 6.25 | 98.13 |
| **Proposed EIML** | **EINN (Ours: $\lambda_1=2.5, \lambda_2=1.8$)** | **0.9597** | **0.7664** | **0.7742** | **0.0595** | **0.00** | **0.00** | **100.00** |

**Key Empirical Insights from Tables 1 and 2:**
1. **Why Unconstrained ML Fails Under Regime Shift:** In Table 1 (Regime A), unconstrained Deep MLP ($\text{AUC} = 0.7665$, $\text{PR-AUC} = 0.2732$) and RBF-SVM ($\text{AUC} = 0.7618$) perform *worse* than simple Multivariable Logistic Regression ($\text{AUC} = 0.7742$, $\text{PR-AUC} = 0.3086$). Why? Because during the 2008–2016 training period, several high-growth real estate and construction firms carried high short-term debt ($\text{ShortDebt}/\text{Debt} > 0.75$) without defaulting, causing unconstrained neural networks and collinear regression weights to learn an inverted, risk-reducing sign on short-term debt ($\text{VR}_{\text{mono}} = 88.10\%$ for MLP and $98.27\%$ for unconstrained collinear LR due to collinearity between `Debt/Asset` and `ShortDebt/Debt`). When the 2022 bond refinancing freeze hit, those exact high-short-term-debt issuers defaulted en masse!
2. **The EIML Advantage (Simultaneous SOTA Accuracy and 100% Economic Consistency):** By enforcing $\partial \hat{y}/\partial (\text{Debt/Asset}) \ge 0$, $\partial \hat{y}/\partial (\text{ShortDebt/Debt}) \ge 0$, and $\partial \hat{y}/\partial \text{ICR}_{\text{op}} \le 0$, **EINN** prevents collinear sign reversal, boosting Regime A $\text{AUC-ROC}$ to **0.7894** (+2.29% over unconstrained MLP) and $\text{PR-AUC}$ to **0.3268** (+5.36% over unconstrained MLP), while achieving **$\text{VR}_{\text{mono}} = 0.00\%$**, **$\text{VR}_{\text{bound}} = 0.00\%$**, and **$\text{ECS} = 100.00\%$** across both Regime A and Regime B.

#### 5.2. Empirical Quantification of Look-Ahead & Survivorship Biases

##### Table 3: Look-Ahead Bias & Data Hygiene Ablation Audit (Evaluated with EINN on Out-of-Time Test)
| Pipeline Configuration | Bias / Leakage Mechanism Present | Apparent AUC-ROC | Apparent PR-AUC | Distortion vs. Gold-Standard ($\Delta$ AUC) | Methodological Diagnosis |
| :--- | :--- | :---: | :---: | :---: | :--- |
| 1. Random 5-Fold Cross-Validation | Future crisis years (2020–2022) leaked into training folds | 0.8415 | 0.4120 | **+0.0521 (Artificial Inflation)** | Invalid (Violates temporal causality) |
| 2. Contemporaneous Target ($X_t \to Y_t$) | Predicts distress using same-year financial statements | 0.9782 | 0.8840 | **+0.1888 (Tautological Leakage)** | Invalid (100% Look-Ahead Bias) |
| 3. Overlapping Target Window ($X_t \to Y_{(t,t+1)}^{\text{ovl}}$) | Year-$t$ condition shared between $X_t$ and 2-year label $Y_{(t,t+1)}$ | 0.9597 | 0.7664 | **+0.1703 (Window Overlap)** | Valid only for persistence modeling |
| 4. Unpurged Split Boundary ($t=2019$ in Val) | 2020 COVID-19 outcome ($Y_{2020}$) leaked into Val hyperparameter tuning | 0.7968 | 0.3390 | **+0.0074 (Boundary Leakage)** | Biased hyperparameter selection |
| 5. Pre-IPO Backfill Included ($N_{\text{train}}=5,463$) | Includes 1,415 pre-listing rows conditioned on future IPO survival | 0.7812 | 0.3140 | **-0.0082 (Survivorship Dilution)** | Distorts prior base rate ($7.56\%$) |
| 6. Dropping 2022 Censored/Delisted Firms | Drops 28 non-filing firms in 2022 (`FLC`, `HAI`, `BII`, `VKC`, etc.) | 0.7790 | 0.3055 | **-0.0104 (Attrition Bias)** | Blind to true 2022 bond/stock defaults |
| **7. Strict Point-in-Time Purged ($Y_{i,\tau}^{\text{fwd}}$)** | **Zero Look-Ahead, Post-Listing Only, Purged Boundaries, Censoring-Aware** | **0.7894** | **0.3268** | **0.0000 (Gold-Standard Reference)** | **Rigorous Q1 Protocol** |

#### 5.3. Ablation Study on Theory-Informed Components ($\lambda_1, \lambda_2$, and Cone Projection)

##### Table 4: Ablation Study of EINN Components on Out-of-Time Crisis Test Set (Regime A: $Y_{i,\tau}^{\text{fwd}}$)
| Model Variant | $\lambda_1$ ($\mathcal{R}_{\text{mono}}$) | $\lambda_2$ ($\mathcal{R}_{\text{bound}}$) | Cone Projection | AUC-ROC ($\uparrow$) | PR-AUC ($\uparrow$) | Brier ($\downarrow$) | $\text{VR}_{\text{mono}}$ (%) ($\downarrow$) | $\text{VR}_{\text{bound}}$ (%) ($\downarrow$) | ECS (%) ($\uparrow$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| ① Base MLP (Unconstrained) | 0.0 | 0.0 | No | 0.7665 | 0.2732 | 0.0896 | 88.10 | 75.00 | 15.83 |
| ② + Moderate Soft Monotonic Penalty | 1.0 | 0.0 | No | 0.7790 | 0.3064 | 0.0865 | 14.25 | 62.50 | 71.28 |
| ③ + Strong Soft Monotonic Penalty | 2.5 | 0.0 | No | 0.7848 | 0.3195 | 0.0853 | 2.40 | 56.25 | 81.45 |
| ④ + Altman Boundary Penalty Only | 0.0 | 1.8 | No | 0.7712 | 0.2890 | 0.0881 | 82.40 | 0.00 | 42.32 |
| ⑤ + Soft Mono + Boundary ($\mathcal{R}_{\text{mono}} + \mathcal{R}_{\text{bound}}$) | 2.5 | 1.8 | No | 0.7860 | 0.3212 | 0.0852 | 0.77 | 0.00 | 99.46 |
| **⑥ Full EINN (Soft Loss + Hard Cone Projection)** | **2.5** | **1.8** | **Yes** | **0.7894** | **0.3268** | **0.0846** | **0.00** | **0.00** | **100.00** |

---

### 6. Explainable AI (XAI) and Policy Implications for Emerging Bond Markets

1. **Elimination of Collinear Sign Reversals in SHAP / Integrated Gradients:**
   In unconstrained XGBoost and MLP models, strong collinearity between Total Debt-to-Assets ($x_5$, correlation $r = 0.64$ with Short-Term Debt Ratio $x_6$) causes TreeSHAP and Integrated Gradients to split attribution weights with opposing signs—assigning negative risk contributions to high short-term debt for upper-quartile asset firms. Under **EINN** and **Mono-GBDT**, the marginal attribution $\phi_j(x)$ strictly respects economic directionality across 100% of out-of-time test firms:
   - **Top 5 Drivers of 2020–2022 Crisis Distress (by mean $|\text{Attribution}|$):**
     1. Operating Interest Coverage Ratio ($\text{ICR}_{\text{op}}$, $24.8\%$ share of total attribution),
     2. Operating Return on Assets ($\text{EBIT}_{\text{op}}/\text{Asset}$, $18.4\%$),
     3. Total Debt-to-Assets ($\text{Debt}/\text{Asset}$, $15.2\%$),
     4. Working Capital-to-Assets ($\text{WC}/\text{Asset}$, $12.9\%$),
     5. Short-Term Debt Concentration ($\text{ShortDebt}/\text{Debt}$, $10.6\%$).
2. **Early Detection of the 2022 Real Estate & Construction Bond Crisis (`FLC`, `HAI`, `BII`, `VKC` Case Studies):**
   Examining the 2021 financial statements ($t=2021$) prior to the 2022 bond freeze ($\tau=2022$), `FLC` and `BII` reported positive net income ($\text{NetProfit}_{2021} = +83.6\text{B VND}$ and $+32.6\text{B VND}$, respectively), causing naive Net-Profit-based models and Altman $Z''$-Score to classify them as low-to-moderate risk. However, their core **Operating EBIT ($\text{EBIT}_{\text{op}}$)** was severely compressed relative to interest obligations ($\text{ICR}_{\text{op}} < 1.0$) alongside extreme short-term debt maturity concentration. **EINN** assigned 2021$\to$2022 distress probabilities of $\hat{y} = 0.81$ (`HAI`), $\hat{y} = 0.74$ (`FLC`), $\hat{y} = 0.76$ (`BII`), and $\hat{y} = 0.79$ (`VKC`) one full year before their 2022 trading suspensions and bond defaults.
3. **Regulatory Policy Recommendations (Decree 65/2022/ND-CP & Basel III Pillar 2):**
   - **Mandatory Operating-Cash-Flow Coverage Thresholds:** Credit rating agencies and bond regulators in emerging markets should replace net-profit-based coverage metrics with audited $\text{ICR}_{\text{op}}$ and enforce the Altman double-deficit floor ($\text{WC} < 0 \land \text{EBIT}_{\text{op}} < 0$).
   - **Algorithmic Certification via Economic Consistency Score ($\text{ECS}$):** Central banks validating internal ratings-based (IRB) ML models should mandate $\text{VR}_{\text{mono}} = 0\%$ via finite-difference Jacobian stress testing prior to production deployment.

---

### 7. Conclusion and Limitations
This study introduced **Economics-Informed Machine Learning (EIML)** to resolve the longstanding trade-off between statistical accuracy and theoretical consistency in corporate financial distress prediction. By coupling a forensic, zero-look-ahead point-in-time panel pipeline with monotonic gradient regularization, Altman insolvency boundary constraints, and positive-cone weight projection, our **EINN** and **Mono-GBDT** models achieve superior out-of-time crisis generalization across the 2020–2022 COVID-19 and Vietnamese corporate bond crises while guaranteeing **100% Economic Consistency**. Future research can extend this framework by linking firm-level accounting panels with issue-level corporate bond covenants, secondary-market yield spreads, and macroeconomic term-structure covariates.


---

## 9. Compiled LaTeX Manuscript & 52 Verified Q1–Q4 References (PaperOrchestra `HybridLiteratureAgent` + `pdf_utils.py`)

The complete 19-page Q1 LaTeX manuscript has been compiled via `pdflatex` + `bibtex` + `pdflatex` + `pdflatex` with **0 fatal errors** and **0 undefined citations**:
- **Compiled Final PDF (19 Pages, 796 KB)**: [`final_paper.pdf`](file:///home/antigravity/09_PAPER_Q1_BOND/paper/final_paper.pdf) (also copied to [`/home/antigravity/eiml_q1_orchestra/final_paper.pdf`](file:///home/antigravity/eiml_q1_orchestra/final_paper.pdf))
- **LaTeX Source Manuscript**: [`main.tex`](file:///home/antigravity/09_PAPER_Q1_BOND/paper/main.tex)
- **Verified Q1–Q4 BibTeX Database (52 Entries)**: [`references.bib`](file:///home/antigravity/09_PAPER_Q1_BOND/paper/references.bib)
- **PaperOrchestra Citation Map & Rubric Self-Audit**: [`citation_map.json`](file:///home/antigravity/09_PAPER_Q1_BOND/paper/citation_map.json)
- **Vector PDF Figures (TikZ / PGFPlots)**:
  1. [`fig1_architecture.pdf`](file:///home/antigravity/09_PAPER_Q1_BOND/paper/figures/fig1_architecture.pdf) — End-to-End EIML & Zero-Look-Ahead Pipeline
  2. [`fig2_crisis_trajectory.pdf`](file:///home/antigravity/09_PAPER_Q1_BOND/paper/figures/fig2_crisis_trajectory.pdf) — Annual Forward & Persistent Corporate Distress Incidence across HOSE, HNX, UPCOM (2009–2022)
  3. [`fig3_pareto_ecs.pdf`](file:///home/antigravity/09_PAPER_Q1_BOND/paper/figures/fig3_pareto_ecs.pdf) — Out-of-Time PR-AUC vs. Economic Consistency Score (ECS %) Pareto Frontier
  4. [`fig4_monotonic_response.pdf`](file:///home/antigravity/09_PAPER_Q1_BOND/paper/figures/fig4_monotonic_response.pdf) — Leverage Partial Dependence Surface ($D/A$) & Top-8 Axiomatic Integrated Gradients Shares
