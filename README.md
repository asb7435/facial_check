# 얼굴 인식 출결 관리 시스템

Flask, OpenCV, dlib을 사용한 얼굴 인식 출결 관리 시스템입니다. 이 시스템을 통해 회원을 등록하고, 회원 정보를 관리하며, 얼굴 인식을 통해 출결을 기록할 수 있습니다.

## 주요 기능

- 얼굴 인식을 통한 회원 등록 및 관리
- 얼굴 인식을 통한 출근 및 퇴근 기록
- 각 회원의 출결 로그 확인
- 출근하지 않은 경우 퇴근할 수 없도록 제한

## 사전 준비

- Python 3.7 이상
- Flask
- OpenCV
- dlib

## 설치 방법

1. 저장소를 클론합니다:

```bash
git clone https://github.com/your-username/face-recognition-attendance-system.git
cd face-recognition-attendance-system

2. 가상 환경을 생성하고 활성화합니다:

```python
python -m venv venv
source venv/bin/activate  # Windows의 경우 `venv\Scripts\activate`

3. 필요한 패키지를 설치합니다:

```bash
pip install -r requirements.txt

4. 필요한 dlib 모델을 다운로드하여 프로젝트 디렉토리에 배치합니다:
shape_predictor_68_face_landmarks.dat
dlib_face_recognition_resnet_model_v1.dat

## 사용 방법
1. Flask 애플리케이션을 실행합니다:

```bash
python app.py

2. 웹 브라우저를 열고 http://127.0.0.1:5000으로 이동합니다.

3. 관리자 계정으로 로그인합니다:

- 사용자 이름: admin
- 비밀번호: admin

4. 관리자 대시보드에서 다음 작업을 수행할 수 있습니다:

- 새로운 회원 등록
- 회원 정보 조회 및 수정
- 각 회원의 출결 로그 조회
- 프로젝트 구조

```csharp

face-recognition-attendance-system/
│
├── app.py                   # 메인 애플리케이션 파일
├── database.py              # 데이터베이스 작업 파일
├── face_recognition.py      # 얼굴 인식 기능 파일
├── templates/               # HTML 템플릿
│   ├── layout.html          # 기본 템플릿
│   ├── index.html           # 홈 페이지
│   ├── admin_login.html     # 관리자 로그인 페이지
│   ├── members.html         # 회원 목록 페이지
│   ├── register.html        # 회원 등록 페이지
│   ├── edit_member.html     # 회원 정보 수정 페이지
│   ├── member_logs.html     # 회원 출결 로그 페이지
│   ├── today_logs.html      # 오늘의 출결 로그 페이지
│
├── static/                  # 정적 파일 (CSS, JS)
│   ├── styles.css           # 사용자 스타일 파일
│
├── requirements.txt         # 필요한 패키지 목록 파일
├── README.md                # 프로젝트 설명 파일
└── ...                      # 기타 파일 및 디렉토리


#### 코드 개요
##### app.py
이 파일은 Flask 애플리케이션의 메인 파일입니다. 로그인, 회원 등록, 출근 및 퇴근, 로그 조회 등의 라우트를 포함하고 있습니다. 주요 기능은 이미지를 처리하고 출결 상태를 확인하는 recognize_face 함수에서 처리됩니다.

##### database.py
이 파일에는 회원을 추가, 수정, 삭제하고 출결 기록을 관리하는 함수가 포함되어 있습니다.

##### face_recognition.py
이 파일에는 이미지를 처리하고 dlib과 OpenCV를 사용하여 얼굴 인식을 수행하는 함수가 포함되어 있습니다.

##### HTML 템플릿
layout.html: 다른 템플릿들이 확장하는 기본 템플릿입니다.
index.html: 출근 및 퇴근을 수행하는 홈 페이지입니다.
admin_login.html: 관리자 로그인 페이지입니다.
members.html: 등록된 회원 목록 페이지입니다.
register.html: 새로운 회원을 등록하는 페이지입니다.
edit_member.html: 회원 정보를 수정하는 페이지입니다.
member_logs.html: 특정 회원의 출결 로그를 조회하는 페이지입니다.
today_logs.html: 오늘의 출결 로그를 조회하는 페이지입니다.
