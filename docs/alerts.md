# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert 1: HighLatencyP95

- **Severity:** warning
- **Duration:** 5m
- **Kênh thông báo:** Slack `#k4-l3b-alerts`
- **SLI/SLO liên quan:** latency P95 của `response_sent.latency_ms`
- **Điều kiện và thời gian duy trì:** `p95(latency_ms) > 3000ms` trong 5 phút
- **Ảnh hưởng tới người dùng:** người dùng phải chờ lâu hơn trước khi nhận câu trả lời
- **Ba bước kiểm tra đầu tiên:**
  1. Mở dashboard latency để xác nhận P95/P99 và khoảng thời gian tăng.
  2. Lọc `data/logs.jsonl` trong khoảng đó, lấy một `correlation_id` có `latency_ms` cao.
  3. Mở trace cùng `correlation_id` trên Langfuse, so sánh các span chính để xác định bước nào bất thường.
- **Mitigation tạm thời:** rollback prompt về version ổn định, giảm tải hoặc tắt incident scenario đang bật.
- **Owner:** `student-k4-l3b`

## Alert 2: HighErrorRate

- **Severity:** critical
- **Duration:** 3m
- **Kênh thông báo:** Slack `#k4-l3b-alerts`
- **SLI/SLO liên quan:** error rate `request_failed / request_received`
- **Điều kiện và thời gian duy trì:** `error_rate_pct > 2%` trong 3 phút
- **Ảnh hưởng tới người dùng:** người dùng nhận HTTP 500 thay vì câu trả lời
- **Ba bước kiểm tra đầu tiên:**
  1. Mở dashboard errors để xác nhận error rate và breakdown theo loại lỗi.
  2. Lọc `data/logs.jsonl` với `event == "request_failed"`, lấy một `correlation_id` và xem `error_type`.
  3. Mở trace cùng `correlation_id` trên Langfuse để xem span gây lỗi.
- **Mitigation tạm thời:** kiểm tra `tool_fail` incident, khôi phục vector store hoặc restart service.
- **Owner:** `student-k4-l3b`

## Alert 3: LowRetrievalSuccess

- **Severity:** warning
- **Duration:** 5m
- **Kênh thông báo:** Slack `#k4-l3b-alerts`
- **SLI/SLO liên quan:** retrieval success rate `tool_success == true / tool_success != null`
- **Điều kiện và thời gian duy trì:** `tool_success_rate_pct < 90%` trong 5 phút
- **Ảnh hưởng tới người dùng:** RAG không tìm được context phù hợp, câu trả lời có thể không chính xác
- **Ba bước kiểm tra đầu tiên:**
  1. Mở dashboard errors để xác nhận retrieval success rate giảm.
  2. Lọc `data/logs.jsonl` với `tool_success == false`, lấy `correlation_id` liên quan.
  3. Kiểm tra vector store và RAG service health; xem trace span "retrieval" để xác nhận lỗi timeout.
- **Mitigation tạm thời:** kiểm tra `tool_fail` incident, khôi phục vector store hoặc tắt incident.
- **Owner:** `student-k4-l3b`
