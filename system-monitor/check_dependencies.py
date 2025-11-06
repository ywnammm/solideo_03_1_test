"""
의존성 검증 스크립트
PyInstaller 빌드 전에 모든 필수 모듈이 설치되어 있는지 확인합니다.
"""

import sys

def check_module(module_name, package_name=None):
    """모듈이 설치되어 있는지 확인"""
    if package_name is None:
        package_name = module_name

    try:
        __import__(module_name)
        print(f"✓ {package_name}")
        return True
    except ImportError:
        print(f"✗ {package_name} - NOT INSTALLED")
        return False

def main():
    print("=" * 60)
    print("의존성 검증 중...")
    print("=" * 60)
    print()

    modules = [
        ('flask', 'Flask'),
        ('werkzeug', 'Werkzeug'),
        ('jinja2', 'Jinja2'),
        ('click', 'Click'),
        ('itsdangerous', 'ItsDangerous'),
        ('markupsafe', 'MarkupSafe'),
        ('psutil', 'psutil'),
        ('matplotlib', 'Matplotlib'),
        ('reportlab', 'ReportLab'),
        ('numpy', 'NumPy'),
        ('PIL', 'Pillow'),
        ('PyInstaller', 'PyInstaller'),
    ]

    # GPUtil은 선택사항
    optional_modules = [
        ('GPUtil', 'GPUtil (optional - for GPU monitoring)'),
    ]

    all_ok = True

    print("필수 모듈:")
    print("-" * 60)
    for module, name in modules:
        if not check_module(module, name):
            all_ok = False

    print()
    print("선택 모듈:")
    print("-" * 60)
    for module, name in optional_modules:
        check_module(module, name)

    print()
    print("=" * 60)

    if all_ok:
        print("✓ 모든 필수 의존성이 설치되어 있습니다!")
        print("=" * 60)
        print()
        print("다음 명령으로 빌드를 시작하세요:")
        print("  Windows: build_simple.bat")
        print("  Linux/Mac: ./build.sh")
        print()
        return 0
    else:
        print("✗ 일부 필수 의존성이 누락되었습니다!")
        print("=" * 60)
        print()
        print("다음 명령으로 설치하세요:")
        print("  python -m pip install -r requirements.txt")
        print()
        return 1

if __name__ == '__main__':
    sys.exit(main())
