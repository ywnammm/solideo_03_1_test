from flask import Flask, render_template, jsonify, send_file
from monitor import SystemMonitor
import threading
import time
import os
from datetime import datetime
import json

app = Flask(__name__)

# 전역 변수
monitor = SystemMonitor()
monitoring_active = False
monitoring_thread = None
collected_data = []
monitoring_session_id = None


@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')


@app.route('/api/current')
def get_current_data():
    """실시간 현재 시스템 데이터"""
    try:
        snapshot = monitor.collect_snapshot()
        return jsonify({
            'success': True,
            'data': snapshot
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/start-monitoring', methods=['POST'])
def start_monitoring():
    """5분간 모니터링 시작"""
    global monitoring_active, monitoring_thread, collected_data, monitoring_session_id

    if monitoring_active:
        return jsonify({
            'success': False,
            'message': 'Monitoring already in progress'
        }), 400

    # 새 모니터 인스턴스 생성
    monitoring_session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    collected_data = []
    monitoring_active = True

    def monitoring_worker():
        global monitoring_active, collected_data
        duration = 300  # 5분
        interval = 2    # 2초마다 수집
        end_time = time.time() + duration

        while monitoring_active and time.time() < end_time:
            try:
                snapshot = monitor.collect_snapshot()
                collected_data.append(snapshot)
                time.sleep(interval)
            except Exception as e:
                print(f"Error collecting data: {e}")

        monitoring_active = False

        # 데이터 저장
        filename = f"monitoring_{monitoring_session_id}.json"
        filepath = os.path.join('data', filename)
        os.makedirs('data', exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(collected_data, f, ensure_ascii=False, indent=2)

        print(f"Monitoring completed. Data saved to {filepath}")

    monitoring_thread = threading.Thread(target=monitoring_worker)
    monitoring_thread.start()

    return jsonify({
        'success': True,
        'message': 'Monitoring started',
        'session_id': monitoring_session_id,
        'duration': 300
    })


@app.route('/api/stop-monitoring', methods=['POST'])
def stop_monitoring():
    """모니터링 중지"""
    global monitoring_active

    if not monitoring_active:
        return jsonify({
            'success': False,
            'message': 'No monitoring in progress'
        }), 400

    monitoring_active = False

    return jsonify({
        'success': True,
        'message': 'Monitoring stopped'
    })


@app.route('/api/monitoring-status')
def get_monitoring_status():
    """모니터링 상태 조회"""
    return jsonify({
        'active': monitoring_active,
        'data_points': len(collected_data),
        'session_id': monitoring_session_id
    })


@app.route('/api/download-pdf')
def download_pdf():
    """PDF 리포트 생성 및 다운로드"""
    global collected_data, monitoring_session_id

    if not collected_data:
        return jsonify({
            'success': False,
            'error': 'No data available. Please complete monitoring first.'
        }), 400

    try:
        from pdf_generator import PDFGenerator

        pdf_gen = PDFGenerator(collected_data)
        pdf_filename = f"system_monitor_report_{monitoring_session_id}.pdf"
        pdf_path = os.path.join('data', pdf_filename)

        pdf_gen.generate_report(pdf_path)

        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=pdf_filename,
            mimetype='application/pdf'
        )

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/collected-data')
def get_collected_data():
    """수집된 모든 데이터 조회"""
    return jsonify({
        'success': True,
        'session_id': monitoring_session_id,
        'data_points': len(collected_data),
        'data': collected_data
    })


if __name__ == '__main__':
    # data 디렉토리 생성
    os.makedirs('data', exist_ok=True)

    print("=" * 60)
    print("System Monitor Dashboard")
    print("=" * 60)
    print("Server starting on http://localhost:5000")
    print("Press Ctrl+C to stop")
    print("=" * 60)

    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
