# Flask Tiny App

## Thông tin cá nhân

- **Họ tên:** Nguyễn Đinh Trung Nam
- **Mã sinh viên:** 22632561

## Mô tả dự án

Dự án "Flask Tiny App" là một ứng dụng web đơn giản, kết hợp giữa Blog và To Do List được phát triển bằng Flask Framework. Ứng dụng cung cấp các chức năng:

### Chức năng người dùng

- Đăng ký và đăng nhập tài khoản
- Quản lý thông tin cá nhân và avatar
- Tạo, chỉnh sửa và xóa công việc (tasks)
- Phân loại công việc theo danh mục
- Theo dõi trạng thái công việc (pending, in progress, completed)

### Chức năng quản trị (Admin)

- Quản lý người dùng:
  - Xem danh sách người dùng
  - Khóa/mở khóa tài khoản
  - Reset mật khẩu người dùng
  - Cấp/hủy quyền admin
- Quản lý danh mục:
  - Thêm, sửa, xóa danh mục
  - Xem số lượng công việc trong từng danh mục
- Quản lý công việc:
  - Xem tất cả công việc của người dùng
  - Lọc công việc theo người dùng/danh mục
  - Thống kê công việc theo trạng thái

### Công nghệ sử dụng

- **Backend:** Flask (Python)
- **Database:** SQLite với SQLAlchemy ORM
- **Frontend:** HTML, CSS, Bootstrap, JavaScript
- **Authentication:** Flask-Login
- **Form Handling:** Flask-WTF
- **File Upload:** Flask-Upload

## Hướng dẫn cài đặt và chạy

1. **Clone repository:**

   ```bash
   git clone https://github.com/Tnamzxje/ptud-gk-de2.git
   cd ptud-gk-de2
   ```

2. **Tạo và kích hoạt môi trường ảo:**

   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Cài đặt các thư viện cần thiết:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Khởi tạo database:**

   ```bash
   flask db upgrade
   ```

5. **Chạy ứng dụng:**

   ```bash
   flask run
   ```

6. **Truy cập ứng dụng:**
   - Mở trình duyệt và truy cập: http://localhost:5000
   - Tài khoản admin mặc định:
     - Username: admin
     - Password: admin123

## Cấu trúc thư mục

```
flask-tiny-app/
├── app.py              # File chính của ứng dụng
├── requirements.txt    # Các thư viện cần thiết
├── migrations/        # Thư mục chứa các file migration database
├── static/           # Thư mục chứa file tĩnh (CSS, JS, images)
├── templates/        # Thư mục chứa file HTML
└── uploads/          # Thư mục chứa file upload từ người dùng
```

## Người đóng góp

- Nguyễn Đinh Trung Nam (22632561)
