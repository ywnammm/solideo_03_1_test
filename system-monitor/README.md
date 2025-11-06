# System Monitor Dashboard

PC 시스템 리소스를 실시간으로 모니터링하고 상세한 PDF 리포트를 생성하는 웹 기반 대시보드입니다.

## 주요 기능

### 📊 실시간 모니터링
- **CPU**: 사용률, 코어 수, 스레드 수, 주파수
- **메모리**: RAM 및 Swap 메모리 사용량
- **디스크**: 파티션별 사용량 및 I/O 통계
- **네트워크**: 전송/수신 데이터, 활성 연결 수
- **GPU**: GPU 사용률, 메모리 사용량, 온도 (가능한 경우)
- **온도**: CPU 및 시스템 온도 센서 (가능한 경우)

### 📈 실시간 시각화
- Chart.js를 사용한 실시간 그래프
- CPU, 메모리, 네트워크 트래픽 시각화
- 모든 리소스 비교 차트
- 상위 10개 프로세스 표시

### ⏱️ 5분 모니터링 세션
- 버튼 클릭으로 5분간 자동 모니터링 시작
- 진행 상황 표시 및 타이머
- 데이터 자동 수집 (2초 간격)

### 📄 PDF 리포트 생성
- 상세한 통계 및 그래프가 포함된 PDF 리포트
- 시스템 구성 정보
- 시간별 리소스 사용 추이
- 통계 요약 및 권장사항

## 시스템 요구사항

- Python 3.7 이상
- 최신 웹 브라우저 (Chrome, Firefox, Edge 등)

## 설치 방법

### 1. 저장소 클론 또는 다운로드

```bash
cd system-monitor
```

### 2. 가상 환경 생성 (권장)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. 필요한 패키지 설치

```bash
pip install -r requirements.txt
```

## EXE 파일로 빌드하기

Python이 설치되지 않은 환경에서도 사용할 수 있도록 독립 실행 파일(exe)을 만들 수 있습니다.

### Windows에서 빌드

**방법 1: 자동 빌드 (가상환경 사용 - 권장)**
```cmd
build.bat
```

**방법 2: 간단 빌드 (가상환경 미사용)**
```cmd
build_simple.bat
```

빌드가 완료되면 `dist/SystemMonitor/` 폴더에 실행 파일이 생성됩니다.

### Linux/Mac에서 빌드

```bash
# 1. 빌드 스크립트에 실행 권한 부여
chmod +x build.sh

# 2. 빌드 스크립트 실행
./build.sh

# 빌드가 완료되면 dist/SystemMonitor/ 폴더에 실행 파일이 생성됩니다
```

### EXE 파일 사용 방법

빌드가 완료되면 `dist/SystemMonitor/` 폴더가 생성됩니다:

```
dist/SystemMonitor/
├── SystemMonitor.exe (또는 Linux/Mac의 경우 SystemMonitor)
├── _internal/          # 필요한 라이브러리들
├── templates/          # HTML 템플릿
├── static/            # CSS, JS 파일
├── data/              # 데이터 저장 폴더
└── README.md          # 문서
```

**실행 방법:**

1. `dist/SystemMonitor/` 폴더 전체를 원하는 위치로 복사
2. `SystemMonitor.exe` (또는 `SystemMonitor`) 실행
3. 브라우저에서 `http://localhost:5000` 접속

**참고:**
- EXE 파일은 Python 설치 없이 독립적으로 실행됩니다
- 폴더 전체를 함께 배포해야 정상 작동합니다
- 첫 실행 시 Windows Defender 경고가 나타날 수 있습니다 (정상)

## 사용 방법 (Python으로 직접 실행)

### 1. 서버 실행

```bash
python app.py
```

서버가 시작되면 다음과 같은 메시지가 표시됩니다:

```
============================================================
System Monitor Dashboard
============================================================
Server starting on http://localhost:5000
Press Ctrl+C to stop
============================================================
```

### 2. 웹 브라우저에서 접속

브라우저를 열고 다음 주소로 이동:

```
http://localhost:5000
```

### 3. 대시보드 사용

1. **실시간 모니터링**: 페이지를 열면 자동으로 시스템 리소스가 실시간으로 표시됩니다.

2. **5분 모니터링 시작**:
   - "Start 5-Minute Monitoring" 버튼 클릭
   - 5분간 자동으로 데이터 수집
   - 진행 상황이 프로그레스 바에 표시됨

3. **모니터링 중지**:
   - 필요시 "Stop Monitoring" 버튼으로 중도 중지 가능

4. **PDF 다운로드**:
   - 모니터링 완료 후 "Download PDF Report" 버튼 클릭
   - 상세한 분석 리포트가 포함된 PDF 다운로드

## 프로젝트 구조

```
system-monitor/
├── app.py                  # Flask 웹 서버
├── monitor.py              # 시스템 모니터링 로직
├── pdf_generator.py        # PDF 리포트 생성
├── requirements.txt        # Python 의존성
├── README.md              # 문서
├── system_monitor.spec    # PyInstaller 설정 파일
├── build.bat              # Windows 빌드 스크립트
├── build.sh               # Linux/Mac 빌드 스크립트
├── START_MONITOR.bat      # Windows 실행 런처
├── .gitignore             # Git 무시 파일
├── static/
│   ├── css/
│   │   └── style.css      # 스타일시트
│   └── js/
│       └── dashboard.js   # 프론트엔드 로직
├── templates/
│   └── index.html         # 메인 페이지
├── data/                  # 수집된 데이터 및 PDF 저장
├── build/                 # 빌드 임시 파일 (생성됨)
└── dist/                  # 빌드 결과물 (생성됨)
    └── SystemMonitor/     # 배포 가능한 실행 파일
```

## API 엔드포인트

- `GET /`: 메인 대시보드 페이지
- `GET /api/current`: 현재 시스템 상태 조회
- `POST /api/start-monitoring`: 5분 모니터링 시작
- `POST /api/stop-monitoring`: 모니터링 중지
- `GET /api/monitoring-status`: 모니터링 상태 조회
- `GET /api/download-pdf`: PDF 리포트 다운로드
- `GET /api/collected-data`: 수집된 모든 데이터 조회 (JSON)

## 기술 스택

### 백엔드
- **Flask**: 웹 프레임워크
- **psutil**: 시스템 리소스 모니터링
- **GPUtil**: GPU 모니터링
- **matplotlib**: 그래프 생성
- **reportlab**: PDF 생성

### 프론트엔드
- **HTML5/CSS3**: 마크업 및 스타일
- **JavaScript (ES6+)**: 클라이언트 로직
- **Chart.js**: 실시간 그래프 시각화

## 주요 특징

### 실시간 업데이트
- 2초마다 자동으로 시스템 데이터 갱신
- 부드러운 애니메이션과 전환 효과

### 반응형 디자인
- 모바일, 태블릿, 데스크톱 모든 화면 크기 지원
- 그리드 레이아웃으로 자동 조정

### 상세한 정보
- 실시간 통계 카드
- 시간별 추이 그래프
- 프로세스 모니터링
- 시스템 구성 정보

### PDF 리포트
- 5페이지 분량의 상세 리포트
- 다양한 그래프와 차트
- 통계 분석 및 권장사항

## 문제 해결

### EXE 빌드 문제

#### "pyinstaller는 내부 또는 외부 명령이 아닙니다" 오류

**해결 방법:**
1. `build_simple.bat` 사용 (자동으로 해결됨)
2. 또는 수동으로:
   ```cmd
   python -m pip install pyinstaller
   python -m PyInstaller system_monitor.spec
   ```

#### "ModuleNotFoundError: No module named 'flask'" 오류 (실행 시)

이는 빌드된 EXE를 실행할 때 발생하는 오류입니다.

**해결 방법:**
1. **의존성 확인**:
   ```cmd
   python check_dependencies.py
   ```

2. **모든 의존성 재설치**:
   ```cmd
   python -m pip uninstall -y flask werkzeug jinja2 click
   python -m pip install -r requirements.txt
   ```

3. **빌드 폴더 완전 삭제 후 재빌드**:
   ```cmd
   rmdir /s /q build dist
   build_simple.bat
   ```

4. **수동으로 빌드** (더 많은 정보 확인):
   ```cmd
   python -m pip install -r requirements.txt
   python -m PyInstaller --clean system_monitor.spec
   ```

#### 빌드 중 "No module named 'xxx'" 오류

**해결 방법:**
```cmd
python -m pip install -r requirements.txt
```

#### 빌드 완료 후 실행 시 "Failed to execute script" 오류

**해결 방법:**
- `dist/SystemMonitor/` 폴더 전체를 함께 복사했는지 확인
- `_internal/`, `templates/`, `static/` 폴더가 모두 있는지 확인

#### Windows Defender가 EXE를 차단

**해결 방법:**
1. "추가 정보" 클릭
2. "실행" 클릭
3. 서명되지 않은 실행 파일에 대한 정상적인 경고입니다

### GPU 정보가 표시되지 않음
- NVIDIA GPU가 없거나 드라이버가 설치되지 않은 경우 정상입니다.
- GPUtil은 NVIDIA GPU만 지원합니다.

### 온도 정보가 표시되지 않음
- Windows에서는 온도 센서 접근이 제한될 수 있습니다.
- Linux에서는 `lm-sensors` 패키지 설치가 필요할 수 있습니다.

### 권한 오류
- 일부 시스템 정보는 관리자 권한이 필요할 수 있습니다.
- 필요시 관리자 권한으로 실행하세요.

### 포트 충돌
- 5000번 포트가 이미 사용 중인 경우, `app.py`의 포트 번호를 변경하세요:
```python
app.run(debug=True, host='0.0.0.0', port=5001, threaded=True)
```

## 개발 모드

개발 중에는 Flask의 디버그 모드가 자동으로 활성화됩니다:
- 코드 변경 시 자동 재시작
- 상세한 오류 메시지
- 프로덕션 환경에서는 `debug=False`로 설정하세요

## 라이선스

이 프로젝트는 교육 및 개인 사용 목적으로 제공됩니다.

## 기여

버그 리포트, 기능 제안, 풀 리퀘스트를 환영합니다!

## 참고사항

- 모니터링 데이터는 `data/` 디렉토리에 JSON 형식으로 저장됩니다.
- PDF 리포트는 `data/` 디렉토리에 생성됩니다.
- 브라우저를 닫아도 백그라운드 모니터링은 계속됩니다.
- 서버를 종료하면 진행 중인 모니터링도 중지됩니다.

## 연락처

문의사항이나 지원이 필요하면 이슈를 생성해주세요.

---

**즐거운 모니터링 되세요!** 🚀
