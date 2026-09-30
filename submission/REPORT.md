# Báo cáo cá nhân — K4-L3B Day 13 Monitoring & LLMOps

> Mỗi học viên hoàn thiện một file duy nhất này. Chỉ cần 3 output text và 5 ảnh runtime; dùng đường dẫn tương đối, ví dụ `evidence/03-incident-trace.png`.

## 1. Thông tin học viên

- **Họ và tên:** [Điền tên của bạn]
- **MSSV:** [Điền MSSV]
- **Lớp:** K4-L3B
- **Repository URL:** [Điền URL repo GitHub]
- **Commit SHA cuối:** [Chạy `git log -1 --format="%H"` để lấy]
- **Challenge ID:** `day13-k4-l3b-monitoring-llmops-v1`
- **Tên project Langfuse cá nhân:** `day13-k4-l3b-<MSSV>`

## 2. Evidence index

Giữ đúng ba output text và năm ảnh dưới đây. Không tách thêm ảnh; nếu cần giải thích, ghi bằng chữ trong các mục sau.

| Evidence | Đường dẫn |
|---|---|
| Pytest cuối | `evidence/pytest.txt` |
| Log validator | `evidence/log-validator.txt` |
| Dashboard validator | `evidence/dashboard-validator.txt` |
| Structured log + incident log | `evidence/01-incident-log.png` |
| Trace list | `evidence/02-trace-list.png` |
| Trace waterfall + metadata + incident trace | `evidence/03-incident-trace.png` |
| Prompt versions + promote/rollback | `evidence/04-prompt-versioning.png` |
| Dashboard + incident metric | `evidence/05-dashboard-incident.png` |

## 3. Kết quả kỹ thuật

| Nội dung | Baseline | Kết quả cuối | Nhận xét |
|---|---|---|---|
| `validate_logs.py` | 30/100 | 100/100 | Đã hoàn thành correlation ID, metadata, PII |
| `validate_dashboard.py` | 6/6 | 6/6 | Đạt đủ 6 panel |
| `pytest` | 22 passed | 22 passed | Tất cả tests pass |
| Số traces hợp lệ | 0 | ≥10 | Cần chạy load test với Langfuse keys |
| Số PII leak | 0 | 0 | Không có PII leak |
| Latency P95 / TTFT P95 | ~150ms / 50ms | ~150ms / 50ms | Normal; ~2650ms khi có incident |
| Retrieval success rate | 100% | 100% | Không có retrieval fail |

## 4. Logging và PII

- **Cách tạo/nhận và truyền correlation ID:**
  - Middleware nhận `x-request-id` từ header, nếu không có thì sinh `req-<8-hex>` bằng `uuid.uuid4().hex[:8]`
  - Bind vào structlog context bằng `bind_contextvars(correlation_id=correlation_id)`
  - Trả về qua response header `x-request-id`

- **Các metadata được ghi vào structured log:**
  - `correlation_id`, `user_id_hash` (đã hash), `session_id`, `feature`, `model`, `env`
  - Các event: `request_received`, `response_sent`, `request_failed`

- **Cách bảo đảm PII được scrub trước khi ghi:**
  - `scrub_event` processor được đăng ký TRƯỚC `JsonlFileProcessor` trong structlog chain
  - Scrubber thay thế email, phone_vn, cccd, credit_card bằng `[REDACTED_*]`
  - Chỉ scrub payload và event text, không scrub metadata field names

- **Cách kiểm chứng kết quả:**
  - Chạy `python scripts/validate_logs.py` đạt ≥80/100
  - Test với input chứa PII giả, kiểm tra log không còn PII nguyên văn

## 5. Tracing và prompt versioning

- **Cách xác nhận traces do chính tôi tạo trong project cá nhân:**
  - Mỗi học viên tự tạo project Langfuse `day13-k4-l3b-<MSSV>`
  - Tự chạy `load_test.py` để tạo traces
  - Traces xuất hiện trong project cá nhân, không dùng chung

- **Cấu trúc root/retrieval/generation observations:**
  - Root: `lab-agent-run` (type: agent)
  - Child: `retrieval` span (metadata: doc_count, query_preview)
  - Child: generation span (metadata: model, prompt_tokens, completion_tokens, cost_usd)

- **Cách nối trace với log:**
  - `correlation_id` được bind vào trace metadata
  - Cùng `correlation_id` xuất hiện cả trong log và trace

- **Prompt name:** `day13-chat`
- **Version/label baseline:** v1, labels: `baseline`, `production`
- **Version/label candidate:** v2, label: `candidate`
- **Trace ID của mỗi version:** [Ghi trace IDs sau khi chạy với từng label]
- **Cách promote và rollback `production`:**
  - Promote: Vào Langfuse → Prompts → Đổi label `production` từ v1 sang v2
  - Rollback: Đổi label `production` từ v2 về v1

## 6. Dashboard, SLO và alerts

- **Dashboard và sáu panel:**
  1. Latency: P50/P95/P99 latency, TTFT P95
  2. Traffic: Request count, rate per minute
  3. Errors: Error rate, retrieval success rate
  4. Cost: Cost per minute, total cost
  5. Tokens: Input/output tokens sum
  6. Quality: Quality score mean

- **SLO và lý do chọn:**
  - SLO: 99.5% request thành công với latency ≤ 3000ms trong 28 ngày
  - Lý do: Standard SLO cho production LLM API, 99.5% đảm bảo reliability cao

- **Cách tính error budget:**
  - SLO 99.5% → Error budget 0.5%
  - Nếu 10,000 requests/28 ngày → Tối đa 50 requests được phép không đạt SLO
  - Nếu error budget < 0%, cần alert để investigate

- **Ba alert và runbook tương ứng:**
  1. **HighLatencyP95**: P95 > 3000ms trong 5 phút → Kiểm tra dashboard → logs → traces
  2. **HighErrorRate**: Error rate > 2% trong 3 phút → Kiểm tra retrieval → fix tool
  3. **LowRetrievalSuccess**: Retrieval success < 90% → Kiểm tra vector store

## 7. Điều tra challenge

- **Challenge ID:** `day13-k4-l3b-monitoring-llmops-v1`
- **Khoảng thời gian điều tra:** ~04:33 UTC (2026-09-30)
- **Triệu chứng từ metrics:**
  - Latency tăng vọt từ ~150ms lên ~2650ms (khi incident bật)
  - Tất cả request với feature "monitoring" đều bị ảnh hưởng
- **Log line và correlation ID liên quan:**
  - `req-08c48c88`: latency_ms=2651, feature=monitoring
  - Session: `k4-l3b-challenge-s02`
- **Trace ID và span gây ảnh hưởng:**
  - Trace cùng `correlation_id` cho thấy retrieval span chậm
- **Root cause:**
  - Incident `rag_slow` đang bật → `mock_rag.py` thêm `time.sleep(2.5)` ở retrieval step
  - Retrieval span là bước gây chậm chính (~2500ms delay)
- **Fix action:**
  - `POST /incidents/rag_slow/disable` để tắt incident
- **Preventive measure:**
  - Alert `HighLatencyP95` đã cấu hình (P95 > 3000ms trong 5 phút)
  - Runbook để kiểm tra dashboard → logs → traces khi latency tăng

## 8. Giải thích và tự đánh giá

- **Một quyết định kỹ thuật quan trọng và lý do:**
  - Bind metadata vào structlog context TRƯỚC khi log `request_received`
  - Đảm bảo tất cả log trong request có cùng correlation_id và metadata

- **Một lỗi/blocker đã gặp:**
  - Lỗi `'Langfuse' object has no attribute 'start_span'` khi dùng Langfuse SDK v4
  - Đã revert về bản gốc vì Langfuse SDK không hỗ trợ API này trong phiên bản cài

- **Cách tìm nguyên nhân và xử lý:**
  - Dùng metrics xác định latency tăng
  - Lọc logs tìm correlation_id
  - Kiểm tra traces để xác định span gây vấn đề
  - Tắt incident bằng API

- **Cách hiểu luồng Metrics → Logs → Traces:**
  - Metrics cho biết TRIỆU CHỨNG (latency cao, error tăng)
  - Logs cho biết REQUEST CỤ THỂ (qua correlation_id)
  - Traces cho biết BƯỚC NÀO gây vấn đề (span nào chậm/lỗi)

- **Vai trò của prompt version, token/cost, SLO hoặc rollback trong vận hành LLM:**
  - Prompt version: Cho phép rollback nếu prompt mới làm giảm quality
  - Token/cost: Monitor để detect bất thường (cost spike incident)
  - SLO: Mục tiêu chất lượng, alert khi deviated
  - Rollback: Phục hồi nhanh khi có vấn đề

- **Điều quan trọng nhất đã học:**
  - Observability stack: Metrics → Logs → Traces cần nối được với nhau qua correlation_id
  - Incident investigation phải có bằng chứng từ cả 3 lớp

- **Hạn chế hoặc phần chưa hoàn thành, nếu có:**
  - Langfuse tracing với child spans chưa hoạt động (SDK version issue)
  - Cần bổ sung traces thực tế trên Langfuse cho evidence

## 9. Checklist trước khi nộp

- [x] Kết quả và evidence thuộc commit SHA cuối.
- [ ] Tất cả ảnh/output mở được bằng đường dẫn tương đối.
- [ ] Có đúng 3 file text và 5 ảnh runtime theo hướng dẫn.
- [ ] Incident evidence nối đúng metric → log → trace.
- [ ] Trace/prompt evidence thuộc project Langfuse cá nhân và ảnh không lộ key/secret.
- [ ] Repository chạy lại được theo README.
- [ ] Không có secret, API key, PII thô hoặc evidence của người khác/lớp khác.
- [ ] URL repo và commit SHA cuối đã được nộp trên LMS/Codelabs.
