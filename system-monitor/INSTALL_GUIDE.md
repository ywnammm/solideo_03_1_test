# System Monitor - 설치 가이드

## 목차
1. [시스템 요구사항](#시스템-요구사항)
2. [빠른 설치](#빠른-설치)
3. [문제 해결](#문제-해결)
4. [플랫폼별 가이드](#플랫폼별-가이드)

---

## 시스템 요구사항

### Python 버전
- **권장**: Python 3.11 또는 3.12
- **지원**: Python 3.9 ~ 3.12
- **미지원**: Python 3.14+ (아직 안정 버전 아님)

### 운영체제
- Windows 10/11
- macOS 10.15+
- Linux (Ubuntu 20.04+, CentOS 8+, etc.)

### 디스크 공간
- 최소 500MB (설치 + 데이터)

---

## 빠른 설치

### Windows

#### 방법 1: 권장 방법 (Python 3.11/3.12 사용 시)

```cmd
# 1. Python 버전 확인
python --version

# Python 3.11 또는 3.12인 경우
python -m pip install -r requirements-py311.txt

# Python 3.13 이상인 경우
python -m pip install -r requirements.txt
```

#### 방법 2: Python 3.14 사용 중인 경우

**⚠️ 문제**: Python 3.14는 NumPy 1.26.2의 미리 컴파일된 wheel이 없어서 소스에서 빌드해야 합니다.

**해결책 A - Python 다운그레이드 (권장)**:

1. [Python 3.12.x 다운로드](https://www.python.org/downloads/)
2. 설치 후 재시도

**해결책 B - Visual Studio Build Tools 설치**:

1. [Visual Studio Build Tools 다운로드](https://visualstudio.microsoft.com/downloads/)
2. "Desktop development with C++" 워크로드 설치 (약 7GB)
3. 다시 설치 시도:
   ```cmd
   python -m pip install -r requirements.txt
   ```

**해결책 C - 유연한 버전 사용 (가장 빠름)**:

```cmd
# 이미 수정된 requirements.txt 사용
python -m pip install -r requirements.txt

# 또는 개별 설치
python -m pip install Flask psutil GPUtil matplotlib reportlab numpy Pillow pyinstaller
```

### macOS

```bash
# Homebrew로 Python 설치 (권장)
brew install python@3.12

# 패키지 설치
python3 -m pip install -r requirements.txt
```

### Linux

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3-pip python3-dev

# CentOS/RHEL
sudo yum install python3-pip python3-devel

# 패키지 설치
python3 -m pip install -r requirements.txt
```

---

## 문제 해결

### ❌ 오류: "Unknown compiler(s)" (NumPy 빌드 실패)

**증상**:
```
ERROR: Unknown compiler(s): [['icl'], ['cl'], ['cc'], ['gcc'], ['clang']]
```

**원인**:
- Python 3.14 등 최신 버전 사용
- C 컴파일러 미설치
- NumPy를 소스에서 빌드해야 하는데 도구 없음

**해결**:
1. Python 3.12로 다운그레이드 (권장)
2. 또는 Build Tools 설치 (Windows)
3. 또는 유연한 버전 사용:
   ```cmd
   python -m pip install numpy --only-binary :all:
   ```

---

### ❌ 오류: "ModuleNotFoundError: No module named 'flask'"

**증상**:
```
ModuleNotFoundError: No module named 'flask'
```

**해결**:
```cmd
# 모든 의존성 재설치
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# 또는 수동 설치
python -m pip install Flask
```

---

### ❌ 오류: "Permission denied"

**증상**:
```
ERROR: Could not install packages due to an EnvironmentError: [Errno 13] Permission denied
```

**해결**:
```cmd
# Windows: 관리자 권한으로 실행
# 또는 사용자 디렉토리에 설치
python -m pip install --user -r requirements.txt

# Linux/Mac
sudo pip3 install -r requirements.txt
# 또는
pip3 install --user -r requirements.txt
```

---

### ❌ 오류: "SSL: CERTIFICATE_VERIFY_FAILED"

**증상**:
```
SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]
```

**해결**:
```cmd
# 신뢰할 수 있는 호스트 사용
python -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

---

### ⚠️ 경고: "Ignoring invalid distribution"

**증상**:
```
WARNING: Ignoring invalid distribution -orch (~\site-packages)
```

**해결**:
```cmd
# pip 캐시 정리
python -m pip cache purge

# 손상된 패키지 제거 및 재설치
python -m pip uninstall -y Flask psutil matplotlib numpy
python -m pip install -r requirements.txt
```

---

## 플랫폼별 가이드

### Windows 10/11

#### Python 설치

1. [Python.org](https://www.python.org/downloads/windows/)에서 다운로드
2. **중요**: "Add Python to PATH" 체크
3. 설치 완료 후 확인:
   ```cmd
   python --version
   python -m pip --version
   ```

#### 가상 환경 사용 (권장)

```cmd
# 가상 환경 생성
python -m venv venv

# 활성화
venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt

# 비활성화
deactivate
```

#### 권한 문제 해결

```cmd
# PowerShell 실행 정책 변경 (필요시)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

### macOS

#### Python 설치

```bash
# Homebrew 설치 (없는 경우)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Python 설치
brew install python@3.12

# 확인
python3 --version
pip3 --version
```

#### Xcode Command Line Tools (필요시)

```bash
xcode-select --install
```

---

### Linux (Ubuntu/Debian)

#### 의존성 설치

```bash
# 시스템 업데이트
sudo apt update

# Python 및 개발 도구
sudo apt install python3 python3-pip python3-venv python3-dev

# 추가 라이브러리 (matplotlib용)
sudo apt install pkg-config libfreetype6-dev libpng-dev
```

#### 가상 환경 사용

```bash
# 가상 환경 생성
python3 -m venv venv

# 활성화
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt

# 비활성화
deactivate
```

---

### Linux (CentOS/RHEL)

```bash
# EPEL 저장소 활성화
sudo yum install epel-release

# Python 및 도구
sudo yum install python3 python3-pip python3-devel gcc

# 패키지 설치
pip3 install -r requirements.txt
```

---

## 설치 확인

### 1. Python 패키지 확인

```cmd
python -m pip list
```

필수 패키지 확인:
- Flask
- psutil
- GPUtil
- matplotlib
- reportlab
- numpy
- Pillow
- pyinstaller

### 2. 의존성 검증 스크립트 실행

```cmd
python check_dependencies.py
```

모든 항목이 ✓로 표시되어야 합니다.

### 3. 애플리케이션 실행 테스트

```cmd
python app.py
```

성공 메시지:
```
============================================================
System Monitor Dashboard
============================================================
Server starting on http://localhost:5000
Press Ctrl+C to stop
============================================================
```

---

## 버전별 requirements 파일

### requirements.txt (기본 - 유연한 버전)
- Python 3.13+ 지원
- 최신 호환 버전 자동 선택
- 빌드 도구 필요할 수 있음

### requirements-py311.txt (권장)
- Python 3.11/3.12용
- 미리 컴파일된 wheel 사용
- 빌드 도구 불필요
- **가장 안정적**

### 사용 예:

```cmd
# Python 3.11/3.12 사용자
python -m pip install -r requirements-py311.txt

# Python 3.13+ 사용자
python -m pip install -r requirements.txt
```

---

## 오프라인 설치

### 1. 패키지 다운로드 (인터넷 연결된 PC)

```cmd
pip download -r requirements.txt -d packages
```

### 2. USB로 복사 후 설치 (오프라인 PC)

```cmd
pip install --no-index --find-links=packages -r requirements.txt
```

---

## 가상 환경 권장 이유

### 장점:
- ✅ 시스템 Python 보호
- ✅ 프로젝트별 독립된 패키지
- ✅ 버전 충돌 방지
- ✅ 쉬운 패키지 관리

### 사용법:

```cmd
# 생성
python -m venv venv

# 활성화 (Windows)
venv\Scripts\activate

# 활성화 (Linux/Mac)
source venv/bin/activate

# 설치
pip install -r requirements.txt

# 비활성화
deactivate
```

---

## 추가 도움말

### 로그 확인

설치 중 오류 발생 시 전체 로그 저장:

```cmd
python -m pip install -r requirements.txt > install.log 2>&1
```

### pip 업그레이드

```cmd
python -m pip install --upgrade pip
```

### 캐시 정리

```cmd
python -m pip cache purge
```

### 모든 패키지 제거 (재설치)

```cmd
python -m pip freeze > installed.txt
python -m pip uninstall -r installed.txt -y
```

---

## 문의

설치 중 문제가 발생하면:
1. 이 가이드의 문제 해결 섹션 확인
2. Python 버전 확인 (`python --version`)
3. pip 버전 확인 (`pip --version`)
4. 에러 메시지 전체 복사
5. GitHub Issues에 문의

---

**설치 성공을 기원합니다!** 🚀
