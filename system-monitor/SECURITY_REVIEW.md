# System Monitor - 보안 및 코드 품질 리뷰 리포트

**리뷰 일자**: 2025-11-06
**리뷰 대상**: System Monitor Dashboard v1.0
**리뷰어**: Code Security Analysis

---

## 📋 목차

1. [개요](#개요)
2. [심각도 분류](#심각도-분류)
3. [보안 취약점](#보안-취약점)
4. [코드 품질 문제](#코드-품질-문제)
5. [권장사항](#권장사항)
6. [요약](#요약)

---

## 개요

### 검토 범위
- **백엔드**: app.py, monitor.py, pdf_generator.py
- **프론트엔드**: templates/index.html, static/js/dashboard.js
- **빌드 시스템**: 빌드 스크립트 및 설정 파일

### 전체 보안 등급
**⚠️ 위험 (High Risk)**

현재 애플리케이션은 **프로토타입 또는 개인 로컬 환경 전용**으로만 사용 가능하며, 프로덕션 환경이나 공개 네트워크에 배포 시 심각한 보안 위험이 있습니다.

---

## 심각도 분류

### 심각도 기준
- **🔴 치명적 (Critical)**: 즉각적인 시스템 침해 가능
- **🟠 심각 (High)**: 중요한 보안 위험
- **🟡 중간 (Medium)**: 보안 위험 존재
- **🟢 낮음 (Low)**: 경미한 보안 위험
- **ℹ️ 정보 (Info)**: 개선 권장 사항

---

## 보안 취약점

### 🔴 1. Flask Debug Mode 활성화 (치명적)

**위치**: `app.py:179`

```python
app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
```

**문제점**:
- 프로덕션 환경에서 debug=True는 치명적
- 에러 발생 시 **전체 스택 트레이스와 소스 코드 노출**
- Werkzeug 디버거를 통한 **원격 코드 실행 가능**
- 환경 변수, 시스템 경로 등 민감 정보 노출

**영향**:
- 공격자가 시스템 내부 구조 파악
- 원격 코드 실행을 통한 서버 완전 장악 가능
- 데이터베이스 자격 증명, API 키 등 노출

**CVE 참조**: CVE-2015-5306 (Werkzeug Debug Mode RCE)

---

### 🔴 2. 인증 및 인가 시스템 부재 (치명적)

**위치**: 모든 API 엔드포인트

**문제점**:
- 모든 API 엔드포인트가 **완전히 공개**
- 사용자 인증 없음
- 세션 관리 없음
- 권한 검증 없음

**취약한 엔드포인트**:
```python
@app.route('/api/current')              # 시스템 정보 누구나 접근
@app.route('/api/start-monitoring')     # 누구나 모니터링 시작 가능
@app.route('/api/stop-monitoring')      # 누구나 모니터링 중지 가능
@app.route('/api/collected-data')       # 수집된 데이터 누구나 조회
@app.route('/api/download-pdf')         # PDF 누구나 다운로드
```

**영향**:
- 공격자가 시스템 리소스 정보 수집
- 서비스 거부 공격 (DoS) 가능
- 민감한 시스템 정보 유출
- 네트워크 토폴로지 분석 자료 제공

---

### 🟠 3. CSRF (Cross-Site Request Forgery) 보호 없음 (심각)

**위치**: POST 메서드 엔드포인트

```python
@app.route('/api/start-monitoring', methods=['POST'])
@app.route('/api/stop-monitoring', methods=['POST'])
```

**문제점**:
- CSRF 토큰 검증 없음
- Flask-WTF 또는 유사한 보호 메커니즘 미사용
- 악성 웹사이트에서 요청 위조 가능

**공격 시나리오**:
```html
<!-- 악성 웹사이트 -->
<img src="http://victim-pc:5000/api/start-monitoring" style="display:none">
```

**영향**:
- 사용자 모르게 모니터링 시작/중지
- 시스템 리소스 남용
- 의도하지 않은 PDF 생성 및 디스크 공간 소모

---

### 🟠 4. 민감한 시스템 정보 노출 (심각)

**위치**: `monitor.py` 전체, `app.py:/api/current`

**노출되는 정보**:

1. **프로세스 정보** (monitor.py:203-216)
   ```python
   def get_process_info(self):
       # 실행 중인 모든 프로세스 PID, 이름, CPU/메모리 사용량 노출
   ```

2. **네트워크 정보** (monitor.py:104-154)
   ```python
   def get_network_info(self):
       # IP 주소, 네트워크 인터페이스, 연결 수 노출
       # 'address': addr.address
       # 'netmask': addr.netmask
   ```

3. **디스크 정보** (monitor.py:62-102)
   ```python
   # 파티션 경로, 파일 시스템 타입, 디바이스 정보 노출
   ```

**영향**:
- 공격자가 시스템 구성 파악
- 네트워크 토폴로지 분석
- 실행 중인 보안 소프트웨어 식별
- 타겟팅된 공격 계획 수립에 활용

---

### 🟡 5. XSS (Cross-Site Scripting) 취약점 (중간)

**위치**: `dashboard.js` 여러 곳

**취약한 코드**:

```javascript
// dashboard.js:266-270
document.getElementById('cpuInfo').innerHTML = `
    <strong>Total Usage:</strong> ${data.cpu.usage_total.toFixed(1)}%<br>
    // ... 사용자 데이터 직접 삽입
`;

// dashboard.js:307-313
row.innerHTML = `
    <td>${proc.pid}</td>
    <td>${proc.name}</td>  // 프로세스 이름에 악성 스크립트 포함 가능
`;
```

**문제점**:
- `innerHTML` 사용으로 HTML/JavaScript 인젝션 가능
- 서버에서 받은 데이터를 검증 없이 DOM에 삽입
- 프로세스 이름에 `<script>` 태그 포함 시 실행 가능

**공격 시나리오**:
```python
# 악성 프로세스 이름
process_name = "<img src=x onerror='alert(document.cookie)'>"
```

**영향**:
- 세션 쿠키 탈취
- 사용자 행동 모니터링
- 피싱 페이지로 리다이렉트

**권장**: `textContent` 사용 또는 DOMPurify 라이브러리 사용

---

### 🟡 6. 경로 조작 (Path Traversal) 취약점 (중간)

**위치**: `monitor.py:264`, `app.py:74-79`, `app.py:139`

**취약한 코드**:

```python
# monitor.py:264
def load_data(self, filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        # filepath 검증 없음

# app.py:74-79
filename = f"monitoring_{monitoring_session_id}.json"
filepath = os.path.join('data', filename)
# monitoring_session_id에 "../" 포함 가능성
```

**문제점**:
- 파일 경로 검증 없음
- 상대 경로 (../) 사용 가능
- 임의의 파일 읽기/쓰기 가능

**공격 시나리오**:
```python
# 악의적인 session_id
monitoring_session_id = "../../etc/passwd"
# 결과: data/../../etc/passwd
```

**영향**:
- 시스템 파일 읽기
- 임의 위치에 파일 생성
- 설정 파일 덮어쓰기

---

### 🟡 7. 에러 메시지 정보 노출 (중간)

**위치**: `app.py:34-38`, `app.py:150-154`

**취약한 코드**:

```python
except Exception as e:
    return jsonify({
        'success': False,
        'error': str(e)  # 내부 에러 메시지 직접 노출
    }), 500
```

**문제점**:
- 상세한 에러 메시지 클라이언트에 전달
- 스택 트레이스 정보 포함 가능
- 데이터베이스 구조, 파일 경로 등 노출

**노출 가능 정보**:
- 파일 시스템 구조
- Python 패키지 버전
- 내부 로직 흐름

---

### 🟡 8. Host 바인딩 설정 (중간)

**위치**: `app.py:179`

```python
app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
```

**문제점**:
- `0.0.0.0`은 모든 네트워크 인터페이스에서 접근 허용
- 로컬호스트뿐만 아니라 외부 네트워크에서도 접근 가능
- 방화벽 미설정 시 인터넷 전체에 노출

**영향**:
- 공개 네트워크에서 접근 가능
- 회사 네트워크 내 다른 사용자 접근 가능
- VPN 연결 시 원격 접근 가능

**권장**: 로컬 전용인 경우 `host='127.0.0.1'` 사용

---

### 🟡 9. 리소스 제한 없음 (DoS 취약점) (중간)

**위치**: `app.py:41-91`, `monitor.py:233-248`

**문제점**:

1. **동시 모니터링 세션 제한 없음**
   ```python
   # 하나의 세션만 체크하지만 완료 후 재시작 무제한
   if monitoring_active:
       return jsonify({'success': False, ...}), 400
   ```

2. **데이터 수집량 제한 없음**
   - 5분 동안 무제한 데이터 수집
   - 메모리 사용량 증가

3. **파일 생성 제한 없음**
   ```python
   # 무제한 JSON/PDF 파일 생성 가능
   filepath = os.path.join('data', filename)
   ```

**영향**:
- 메모리 고갈
- 디스크 공간 고갈
- CPU 리소스 독점
- 서비스 거부 (DoS)

---

### 🟡 10. Race Condition (동시성 문제) (중간)

**위치**: `app.py:11-16`, `app.py:44-55`

**취약한 코드**:

```python
# 전역 변수 사용
monitoring_active = False
monitoring_thread = None
collected_data = []
monitoring_session_id = None

# 동시성 보호 없음
def start_monitoring():
    global monitoring_active, monitoring_thread, collected_data
    # Lock 없이 변수 수정
```

**문제점**:
- 스레드 안전성 없음
- 동시 요청 시 데이터 손상 가능
- Race condition 발생 가능

**영향**:
- 데이터 불일치
- 애플리케이션 크래시
- 예측 불가능한 동작

---

### 🟢 11. 외부 CDN 의존성 (낮음)

**위치**: `templates/index.html:8`

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
```

**문제점**:
- 외부 CDN에 의존
- CDN 침해 시 공급망 공격 가능
- 네트워크 없이 오프라인 사용 불가

**영향**:
- 악성 코드 주입 가능 (CDN 침해 시)
- 사용자 추적
- 서비스 중단 (CDN 장애 시)

---

### 🟢 12. 안전하지 않은 파일 권한 (낮음)

**위치**: `app.py:76`, `monitor.py:257`

```python
os.makedirs('data', exist_ok=True)
# 디렉토리 권한 명시 없음 (기본값 사용)

with open(filepath, 'w', encoding='utf-8') as f:
# 파일 권한 명시 없음
```

**문제점**:
- 생성된 파일/디렉토리 권한이 umask에 의존
- 민감한 데이터가 다른 사용자에게 노출 가능

---

### 🟢 13. 하드코딩된 설정 값 (낮음)

**위치**: 여러 곳

```python
duration = 300  # 5분 하드코딩
interval = 2    # 2초 하드코딩
port=5000       # 포트 하드코딩
MAX_DATA_POINTS = 50  # JavaScript
```

**문제점**:
- 설정 변경 시 코드 수정 필요
- 환경별 설정 불가

---

## 코드 품질 문제

### 📊 1. 전역 변수 남용

**위치**: `app.py:11-16`, `dashboard.js:1-19`

```python
# Python
monitoring_active = False
monitoring_thread = None
collected_data = []
monitoring_session_id = None
```

**문제점**:
- 상태 관리의 복잡성
- 테스트 어려움
- 멀티 인스턴스 불가능

---

### 📊 2. 에러 처리 불충분

**위치**: 여러 곳

**문제 예시**:

```python
# monitor.py:207-211
for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
    try:
        processes.append(proc.info)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass  # 에러 로깅 없음
```

**개선 필요**:
- 로깅 시스템 부재
- 에러 추적 불가
- 디버깅 어려움

---

### 📊 3. 하드코딩된 문자열

**위치**: 여러 곳

```python
print(f"Error collecting data: {e}")  # 로거 대신 print
'data'  # 반복적으로 사용되는 디렉토리명
```

**개선 필요**:
- 상수 정의
- 설정 파일 사용
- 다국어 지원 고려

---

### 📊 4. PDF 생성 시 예외 처리 부족

**위치**: `pdf_generator.py:65-96`

```python
def generate_report(self, output_path):
    # 한글 폰트 설정 시도
    try:
        plt.rcParams['font.family'] = 'DejaVu Sans'
    except:
        pass  # 빈 except, 에러 무시
```

**문제점**:
- 일반적인 except 사용 (안티패턴)
- 에러 종류 식별 불가
- 폰트 설정 실패 시 렌더링 문제 발생 가능

---

### 📊 5. 매직 넘버 사용

**위치**: 여러 곳

```javascript
updateInterval = setInterval(updateData, 2000); // 2초가 무엇을 의미하는지 불명확
const MAX_DATA_POINTS = 50; // 50의 근거 없음
```

---

### 📊 6. SQL Injection 위험은 없음 (양호)

현재 코드는 데이터베이스를 사용하지 않아 SQL Injection 위험은 없습니다.

---

### 📊 7. 입력 검증 부재

**위치**: 모든 API 엔드포인트

```python
# 사용자 입력 검증 없음
@app.route('/api/start-monitoring', methods=['POST'])
def start_monitoring():
    # POST 바디 검증 없음
```

---

## 권장사항

### 즉시 조치 필요 (프로덕션 배포 전 필수)

#### 1. Debug Mode 비활성화
```python
# app.py
app.run(debug=False, host='127.0.0.1', port=5000)
```

#### 2. 인증 시스템 추가
```python
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    # 인증 로직 구현
    pass

@app.route('/api/current')
@auth.login_required
def get_current_data():
    # ...
```

#### 3. CSRF 보호 추가
```python
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)
```

#### 4. 에러 메시지 일반화
```python
except Exception as e:
    logger.error(f"Error: {e}")  # 로그에만 기록
    return jsonify({
        'success': False,
        'error': 'An error occurred'  # 일반 메시지
    }), 500
```

#### 5. XSS 방지
```javascript
// textContent 사용
document.getElementById('cpuInfo').textContent = data.cpu.usage_total;

// 또는 DOMPurify 사용
document.getElementById('cpuInfo').innerHTML = DOMPurify.sanitize(html);
```

#### 6. 경로 검증
```python
import os
from pathlib import Path

def validate_path(filepath):
    # 절대 경로로 변환
    abs_path = os.path.abspath(filepath)
    base_path = os.path.abspath('data')

    # data 디렉토리 내부인지 확인
    if not abs_path.startswith(base_path):
        raise ValueError("Invalid path")

    return abs_path
```

---

### 단기 개선 사항 (1-2주 내)

1. **로깅 시스템 구축**
   ```python
   import logging
   logging.basicConfig(level=logging.INFO)
   logger = logging.getLogger(__name__)
   ```

2. **환경 설정 파일 분리**
   ```python
   # config.py
   class Config:
       DEBUG = False
       HOST = '127.0.0.1'
       PORT = 5000
       DATA_DIR = 'data'
   ```

3. **리소스 제한 추가**
   ```python
   from flask_limiter import Limiter

   limiter = Limiter(app, key_func=get_remote_address)

   @app.route('/api/start-monitoring', methods=['POST'])
   @limiter.limit("5 per hour")
   def start_monitoring():
       # ...
   ```

4. **동시성 제어**
   ```python
   from threading import Lock

   monitoring_lock = Lock()

   def start_monitoring():
       with monitoring_lock:
           # ...
   ```

---

### 중기 개선 사항 (1-2개월 내)

1. **HTTPS 지원**
   - SSL/TLS 인증서 적용
   - HTTP → HTTPS 리다이렉트

2. **세션 관리**
   - Flask-Session 사용
   - 세션 타임아웃 설정

3. **감사 로그**
   - 모든 API 호출 기록
   - 사용자 행동 추적

4. **데이터베이스 사용**
   - SQLite 또는 PostgreSQL
   - 모니터링 데이터 영구 저장

5. **API Rate Limiting**
   - 요청 빈도 제한
   - DoS 방지

---

### 장기 개선 사항

1. **마이크로서비스 아키텍처**
   - 모니터링, PDF 생성 분리
   - 확장성 개선

2. **컨테이너화**
   - Docker 이미지 생성
   - 격리된 환경 실행

3. **CI/CD 파이프라인**
   - 자동 보안 스캔
   - 정적 코드 분석

4. **웹 애플리케이션 방화벽 (WAF)**
   - 공격 패턴 탐지
   - 자동 차단

---

## 보안 체크리스트

### 배포 전 필수 확인 사항

- [ ] Debug mode 비활성화
- [ ] 인증 시스템 구현
- [ ] CSRF 보호 활성화
- [ ] XSS 방지 조치
- [ ] 에러 메시지 일반화
- [ ] 경로 검증 추가
- [ ] HTTPS 사용
- [ ] 방화벽 설정
- [ ] 로깅 시스템 구축
- [ ] 보안 헤더 추가
  ```python
  from flask_talisman import Talisman
  Talisman(app)
  ```

---

## 요약

### 현재 상태
- **총 발견 취약점**: 13개
  - 🔴 치명적: 2개
  - 🟠 심각: 2개
  - 🟡 중간: 6개
  - 🟢 낮음: 3개

### 위험도 평가
현재 애플리케이션은 **개인 로컬 환경에서만 사용 가능**하며, 다음 환경에서는 **사용 금지**:
- ❌ 공개 인터넷
- ❌ 회사/조직 네트워크
- ❌ 공유 서버
- ❌ 프로덕션 환경

### 사용 가능 환경
- ✅ 개인 PC의 로컬호스트 (127.0.0.1)
- ✅ 방화벽으로 보호된 개발 환경
- ✅ 오프라인 환경

### 우선순위 수정 사항

**즉시 (배포 전 필수)**:
1. Debug mode 비활성화
2. Host를 127.0.0.1로 변경
3. 기본 인증 추가

**단기 (안정적 운영)**:
1. CSRF 보호
2. XSS 방지
3. 로깅 시스템

**중기 (엔터프라이즈급)**:
1. HTTPS
2. 세션 관리
3. Rate Limiting

---

## 결론

System Monitor Dashboard는 **기능적으로 우수한 프로토타입**이지만, **보안 측면에서는 프로덕션 배포에 부적합**합니다.

현재 상태로는:
- ✅ 개인 학습용으로 적합
- ✅ 로컬 개발 환경에서 사용 가능
- ❌ 프로덕션 환경 부적합
- ❌ 공개 배포 불가

**권장 사용 시나리오**:
- 개인 PC에서 시스템 모니터링 도구로 사용
- 네트워크 연결 없이 로컬에서만 실행
- 학습 및 프로토타입 목적

**프로덕션 배포 시**:
- 위의 모든 보안 조치 필수 구현
- 보안 전문가의 추가 검토 권장
- 침투 테스트 수행 권장

---

**리뷰 완료일**: 2025-11-06
**다음 리뷰 권장일**: 보안 패치 적용 후

---

## 참고 자료

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/latest/security/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)
