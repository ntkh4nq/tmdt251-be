## Setup
1. Chuyển directory tới project


2. Tạo virtual environment (venv) <br>
python -m venv venv <br>


3. Activate environment (dùng PowerShell) <br>
.\venv\Scripts\Activate.ps1 <br>
Nếu thấy đã có (.venv) như dưới đây là oke, mỗi khi chạy đều phải check xem đã kích hoạt venv chưa. <br>
<img width="389" height="108" alt="image" src="https://github.com/user-attachments/assets/ae954f15-d4ae-4ba8-85cc-814b0a46dc1a" /> <br>


4. Tải các dependency: <br>
pip install -r requirements.txt <br>
Các module cần tải, chi tiết nằm ở trong file requirements.txt <br>


5. Chạy server: <br>
uvicorn app.main:app --reload <br>
http://127.0.0.1:8000/docs để test các api <br>

## Extension nếu dùng VSCode:
Black Formatter <br>
DotENV <br>
isort <br>
PostgreSQL (Chris Kolkman) <br>
Pylance <br>
Python <br>
Python Debugger <br> 
Python Environments <br>

## PostgreSQL:
Set các thông tin server như sau (cho đồng bộ):<br>
Hostname/address: localhost<br>
Port: 5432<br>
Username: postgres<br>
Password: postgres<br>
Tên Database: demo<br>