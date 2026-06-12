# Solution — Day 12 Lab Exercises

> **Học viên:** Lương Đình Bút
> **Ngày hoàn thành:** 12/06/2026

Dưới đây là đáp án cho các Exercise từ Part 1 đến Part 5 theo yêu cầu của bài Lab Day 12.

---

## Part 1: Localhost vs Production

### Exercise 1.1: 5 Anti-patterns trong basic code (`app.py`)

1. **Hardcode secrets/API keys:** Việc lưu trực tiếp `OPENAI_API_KEY` hay `DATABASE_URL` trong mã nguồn rất nguy hiểm. Nếu push lên Git, key sẽ bị lộ. Thay vào đó, cần dùng biến môi trường (Environment Variables).
2. **Hardcode port & host:** Cài đặt cứng `host="localhost"` và `port=8000` khiến ứng dụng chỉ chạy được trên máy tính cục bộ và không thể nhận cấu hình cổng từ nền tảng Cloud (thường truyền qua biến `PORT`).
3. **Bật Debug Mode ở Production:** Sử dụng `reload=True` hay `DEBUG=True` khi deploy thực tế sẽ làm lãng phí tài nguyên và rò rỉ thông tin hệ thống khi có lỗi.
4. **Print thay vì Logging:** Dùng hàm `print()` sẽ khó parse, filter hay monitor trên production. Nên dùng structured logging (JSON format) để dễ dàng tích hợp với Datadog/ELK/...
5. **Thiếu Health Check & Graceful Shutdown:** Không có endpoint để Cloud platform kiểm tra "sức khỏe" của app, và khi tắt app sẽ ngắt kết nối đột ngột, làm rớt các request đang xử lý.

### Exercise 1.3: So sánh Basic vs Advanced

| Feature | Basic | Advanced | Tại sao quan trọng? |
|---------|-------|----------|---------------------|
| **Config** | Hardcode | Env vars | Dễ thay đổi giữa các môi trường (dev/prod), tránh lộ secret keys lên version control (Git). |
| **Health check** | ❌ Không có | ✅ Có | Platform (như K8s, Render, Railway) biết khi nào app đang sống hay chết để tự động restart; cũng như biết khi nào app đã sẵn sàng nhận traffic. |
| **Logging** | Dùng `print()` | JSON logs | Structured logs (JSON) dễ dàng cho việc parse, filter, search và thiết lập alert trên các hệ thống giám sát. |
| **Shutdown** | Đột ngột | Graceful | Giúp ứng dụng hoàn thành các request đang xử lý dở dang và giải phóng connection (db/redis) trước khi bị tắt hẳn, tránh mất mát dữ liệu. |

---

## Part 2: Docker Containerization

### Exercise 2.1: Phân tích Dockerfile cơ bản

1. **Base image là gì?** `python:3.11-slim` (chứa OS Linux rút gọn và Python 3.11 runtime, giúp giảm kích thước image so với bản đầy đủ).
2. **Working directory là gì?** `/app` (thư mục gốc bên trong container nơi chứa mã nguồn ứng dụng).
3. **Tại sao COPY requirements.txt trước?** Để tận dụng cơ chế caching layer của Docker. Nếu danh sách thư viện không đổi, Docker sẽ không cần cài đặt lại (bước tốn thời gian nhất) mà dùng lại cache ở lần build sau.
4. **CMD vs ENTRYPOINT khác nhau thế nào?** `CMD` chứa lệnh mặc định và dễ dàng bị ghi đè khi chạy lệnh `docker run`, trong khi `ENTRYPOINT` là lệnh cứng, khó bị ghi đè hơn và thường được coi như file thực thi chính của container.

### Exercise 2.3: Multi-stage build

- Stage 1 (Builder) chứa các công cụ build như `gcc`, `libpq-dev` để compile thư viện, nhưng những file này không cần thiết khi chạy.
- Stage 2 (Runtime) chỉ copy các package đã compile từ stage 1 sang và chạy ứng dụng. Việc này giúp giảm kích thước Image xuống cực nhỏ (thường < 500MB) và tăng tính bảo mật (loại bỏ compiler khỏi môi trường production).

### Exercise 2.4: Architecture Diagram (Docker Compose Stack)

```text
[Client] 
   │
   ▼ (Port 80/443)
[Nginx (Reverse Proxy / Load Balancer)]
   │
   ├──────────┬──────────┐ (Phân tải traffic)
   ▼          ▼          ▼
[Agent 1]  [Agent 2]  [Agent 3] (Stateless API - port 8000)
   │          │          │
   └──────────┼──────────┘
              ▼
[Redis (Port 6379) - Lưu Cache, Sessions, Rate Limit]
```

---

## Part 3: Cloud Deployment

*(Đã review cấu hình deploy của Render và Railway)*

- **Render (`render.yaml`):** Sử dụng dạng Infrastructure as Code, cấu hình chi tiết thông số CPU/RAM, Auto Deploy khi push Github, và generate tự động biến môi trường.
- **Railway (`railway.toml`):** Nhỏ gọn, tự phát hiện base framework qua Nixpacks và dễ dàng cấu hình lệnh khởi chạy (Start Command) kèm biến `$PORT`.

---

## Part 4: API Security

- **API Key & JWT:** Sử dụng API Key cho giao tiếp Service-to-Service hoặc người dùng nội bộ, trong khi JWT phù hợp cho giao tiếp Stateless từ Client (Web/Mobile), token tự chứa thời gian hết hạn (expiration) và vai trò (role) mà không cần query Database.
- **Rate Limiting:** Sử dụng thuật toán Sliding Window (đếm số request trong cửa sổ thời gian 60s) để ngăn chặn spam. Trả về mã lỗi `429 Too Many Requests`.
- **Cost Guard:** Quản lý chi tiêu cho LLM bằng cách tính toán số Token input/output, sau đó quy ra USD và chặn request (trả về mã lỗi `402 Payment Required` hoặc `503`) nếu vượt qua ngân sách ngày (Daily Budget USD).

---

## Part 5: Scaling & Reliability

- **Health Check (`/health`) & Readiness (`/ready`):** Route traffic linh hoạt. Khi đang load Model (nặng) thì chưa ready, Load Balancer sẽ không đẩy request vào.
- **Graceful Shutdown:** Bắt tín hiệu `SIGTERM`, dừng nhận connection mới và chờ các task cũ xử lý xong rồi mới Exit.
- **Stateless Design:** Đây là lý do kiến trúc Nginx Load Balancer hoạt động tốt. Agent không lưu biến in-memory (như conversation history), mà đẩy toàn bộ context vào **Redis**. Nhờ vậy, User A đang chat với Agent 1, nếu Agent 1 rớt mạng, Agent 2 vẫn có thể đọc lịch sử từ Redis và trả lời liền mạch.

---

## Part 6: Final Project (Production Deployment)

Hệ thống AI Agent (chạy trên Google Gemini với chức năng gọi Tool tự động) đã được tái cấu trúc thành công đạt chuẩn Production (bao gồm Rate Limit, Authentication, Cost Guard, Health Checks và Dockerized). 

**Public API URL (sau khi deploy lên Render/Railway):** 
`[Ghi đường link API public của bạn vào đây]`
