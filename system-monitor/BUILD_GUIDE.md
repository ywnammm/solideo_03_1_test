# System Monitor - EXE 빌드 가이드

이 문서는 System Monitor를 독립 실행 파일(exe)로 빌드하는 방법을 설명합니다.

## 목차
1. [사전 요구사항](#사전-요구사항)
2. [빌드 프로세스](#빌드-프로세스)
3. [배포 방법](#배포-방법)
4. [문제 해결](#문제-해결)

## 사전 요구사항

### Windows
- Python 3.7 이상 설치
- pip 설치
- 최소 500MB 여유 디스크 공간

### Linux/Mac
- Python 3.7 이상 설치
- pip 설치
- 최소 500MB 여유 디스크 공간

## 빌드 프로세스

### 자동 빌드 (권장)

#### Windows

1. **빌드 스크립트 실행**
   ```cmd
   build.bat
   ```

2. **빌드 과정**
   - 가상 환경 생성 (없는 경우)
   - 필요한 패키지 자동 설치
   - 이전 빌드 정리
   - PyInstaller로 exe 생성
   - 필요한 파일 복사

3. **완료**
   - 빌드 완료 메시지 확인
   - `dist/SystemMonitor/` 폴더 생성됨

#### Linux/Mac

1. **빌드 스크립트에 실행 권한 부여**
   ```bash
   chmod +x build.sh
   ```

2. **빌드 스크립트 실행**
   ```bash
   ./build.sh
   ```

3. **완료**
   - 빌드 완료 메시지 확인
   - `dist/SystemMonitor/` 폴더 생성됨

### 수동 빌드

고급 사용자를 위한 수동 빌드 방법:

1. **의존성 설치**
   ```bash
   pip install -r requirements.txt
   ```

2. **PyInstaller로 빌드**
   ```bash
   pyinstaller system_monitor.spec
   ```

3. **데이터 디렉토리 생성**
   ```bash
   mkdir dist/SystemMonitor/data
   ```

4. **문서 복사**
   ```bash
   cp README.md dist/SystemMonitor/
   ```

## 빌드 결과물

빌드가 완료되면 다음과 같은 구조가 생성됩니다:

```
dist/SystemMonitor/
├── SystemMonitor.exe           # 실행 파일 (Windows)
├── SystemMonitor               # 실행 파일 (Linux/Mac)
├── _internal/                  # 내부 라이브러리 및 의존성
│   ├── _bz2.pyd
│   ├── _ctypes.pyd
│   ├── flask/
│   ├── matplotlib/
│   ├── numpy/
│   └── ... (기타 의존성)
├── templates/                  # HTML 템플릿
│   └── index.html
├── static/                     # 정적 파일
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── dashboard.js
├── data/                       # 데이터 저장 폴더
└── README.md                   # 문서
```

### 파일 크기

- **전체 폴더 크기**: 약 150-250 MB
- **실행 파일 크기**: 약 10-20 MB
- **의존성 폴더**: 약 140-230 MB

## 배포 방법

### 1. ZIP 파일로 배포

```bash
# Windows (PowerShell)
Compress-Archive -Path dist\SystemMonitor -DestinationPath SystemMonitor-v1.0.zip

# Linux/Mac
zip -r SystemMonitor-v1.0.zip dist/SystemMonitor/
```

### 2. 설치 프로그램 생성 (선택사항)

고급 사용자는 Inno Setup (Windows) 또는 makeself (Linux)를 사용하여 설치 프로그램을 만들 수 있습니다.

### 3. 사용자에게 전달

사용자는 다음 파일만 있으면 됩니다:
- `SystemMonitor-v1.0.zip`

압축 해제 후 `SystemMonitor.exe`를 실행하면 됩니다.

## 실행 방법

### Windows

1. **방법 1: 직접 실행**
   - `SystemMonitor.exe` 더블클릭
   - 자동으로 브라우저가 열림 (없으면 http://localhost:5000 접속)

2. **방법 2: 런처 사용** (포함된 경우)
   - `START_MONITOR.bat` 실행

### Linux/Mac

1. **터미널에서 실행**
   ```bash
   cd dist/SystemMonitor
   ./SystemMonitor
   ```

2. **브라우저 접속**
   - http://localhost:5000

## 문제 해결

### Windows Defender 경고

**문제**: "Windows에서 PC 보호" 경고 표시

**해결**:
1. "추가 정보" 클릭
2. "실행" 클릭
3. 이는 서명되지 않은 실행 파일에 대한 정상적인 경고입니다

### 빌드 실패

#### 오류: "pyinstaller: command not found"

**해결**:
```bash
pip install pyinstaller
```

#### 오류: "No module named 'psutil'"

**해결**:
```bash
pip install -r requirements.txt
```

#### 오류: 빌드 중 메모리 부족

**해결**:
- 다른 프로그램 종료
- 최소 4GB RAM 권장
- 가상 메모리 늘리기

### 실행 오류

#### 오류: "Failed to execute script"

**해결**:
1. 전체 폴더가 함께 있는지 확인
2. `_internal/` 폴더가 있는지 확인
3. `templates/`, `static/` 폴더가 있는지 확인

#### 오류: 포트 5000 사용 중

**해결**:
1. 다른 프로그램이 5000번 포트를 사용 중
2. 해당 프로그램 종료 또는
3. 소스 코드에서 포트 변경 후 재빌드

#### 오류: PDF 생성 실패

**해결**:
1. `data/` 폴더에 쓰기 권한 확인
2. 디스크 여유 공간 확인

## 빌드 최적화

### 파일 크기 줄이기

1. **spec 파일 수정** (`system_monitor.spec`):
   ```python
   # excludes 섹션에 불필요한 모듈 추가
   excludes=['tkinter', 'test', 'unittest'],
   ```

2. **UPX 압축 활성화**:
   ```python
   upx=True,
   upx_exclude=[],
   ```

### 빌드 속도 향상

1. **이전 빌드 캐시 활용**:
   - `build/` 폴더 유지 (전체 재빌드 불필요시)

2. **병렬 빌드 (Linux/Mac)**:
   ```bash
   pyinstaller --parallel system_monitor.spec
   ```

## 코드 서명 (선택사항)

Windows Defender 경고를 제거하려면 코드 서명이 필요합니다.

### Windows 코드 서명

1. 코드 서명 인증서 구매
2. `signtool` 사용:
   ```cmd
   signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com dist\SystemMonitor\SystemMonitor.exe
   ```

### Mac 코드 서명

1. Apple Developer 계정 필요
2. `codesign` 사용:
   ```bash
   codesign --force --sign "Developer ID Application: Your Name" dist/SystemMonitor/SystemMonitor
   ```

## 버전 관리

빌드 시 버전 정보를 포함하려면:

1. **`system_monitor.spec` 수정**:
   ```python
   exe = EXE(
       pyz,
       a.scripts,
       name='SystemMonitor',
       version='version_info.txt',  # 버전 정보 파일
       ...
   )
   ```

2. **`version_info.txt` 생성** (Windows):
   ```
   VSVersionInfo(
     ffi=FixedFileInfo(
       filevers=(1, 0, 0, 0),
       prodvers=(1, 0, 0, 0),
       ...
     ),
     ...
   )
   ```

## 자동화된 빌드 (CI/CD)

### GitHub Actions 예제

```yaml
name: Build EXE

on:
  push:
    tags:
      - 'v*'

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: pyinstaller system_monitor.spec
      - uses: actions/upload-artifact@v2
        with:
          name: SystemMonitor-Windows
          path: dist/SystemMonitor/
```

## 추가 자료

- [PyInstaller 공식 문서](https://pyinstaller.org/)
- [Flask 배포 가이드](https://flask.palletsprojects.com/en/latest/deploying/)
- [코드 서명 가이드](https://docs.microsoft.com/en-us/windows/win32/seccrypto/signing-code)

## 지원

문제가 발생하면 다음을 확인하세요:
1. Python 버전 (3.7 이상)
2. 모든 의존성 설치 확인
3. 빌드 로그 확인
4. GitHub Issues에 문의

---

**행복한 빌드 되세요!** 🚀
