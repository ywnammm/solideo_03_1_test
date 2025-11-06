import matplotlib
matplotlib.use('Agg')  # GUI 없이 사용
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
from datetime import datetime
import os


class PDFGenerator:
    def __init__(self, monitoring_data):
        self.data = monitoring_data
        self.timestamps = []
        self.cpu_data = []
        self.memory_data = []
        self.disk_data = []
        self.network_sent_data = []
        self.network_recv_data = []
        self.gpu_data = []
        self.temp_data = []

        self._parse_data()

    def _parse_data(self):
        """데이터 파싱"""
        for snapshot in self.data:
            # 타임스탬프
            ts = datetime.fromisoformat(snapshot['timestamp'])
            self.timestamps.append(ts)

            # CPU
            self.cpu_data.append(snapshot['cpu']['usage_total'])

            # 메모리
            self.memory_data.append(snapshot['memory']['virtual']['percent'])

            # 디스크 (첫 번째 파티션)
            if snapshot['disk']['partitions']:
                self.disk_data.append(snapshot['disk']['partitions'][0]['percent'])
            else:
                self.disk_data.append(0)

            # 네트워크
            self.network_sent_data.append(snapshot['network']['sent_mb'])
            self.network_recv_data.append(snapshot['network']['recv_mb'])

            # GPU
            gpu_info = snapshot.get('gpu', [])
            if isinstance(gpu_info, list) and len(gpu_info) > 0:
                self.gpu_data.append(gpu_info[0]['load'])
            else:
                self.gpu_data.append(0)

            # 온도 (첫 번째 센서)
            temp_info = snapshot.get('temperature', {})
            if temp_info and not isinstance(temp_info, dict) or 'error' not in temp_info:
                first_sensor = next(iter(temp_info.values()), [])
                if first_sensor and len(first_sensor) > 0:
                    self.temp_data.append(first_sensor[0]['current'])
                else:
                    self.temp_data.append(0)
            else:
                self.temp_data.append(0)

    def generate_report(self, output_path):
        """PDF 리포트 생성"""
        # 한글 폰트 설정 (시스템에 따라 조정 필요)
        try:
            plt.rcParams['font.family'] = 'DejaVu Sans'
        except:
            pass

        with PdfPages(output_path) as pdf:
            # 페이지 1: 개요 및 시스템 정보
            self._create_overview_page(pdf)

            # 페이지 2: CPU 및 메모리
            self._create_cpu_memory_page(pdf)

            # 페이지 3: 디스크 및 네트워크
            self._create_disk_network_page(pdf)

            # 페이지 4: GPU 및 온도
            self._create_gpu_temp_page(pdf)

            # 페이지 5: 상세 통계
            self._create_statistics_page(pdf)

            # 메타데이터 추가
            d = pdf.infodict()
            d['Title'] = 'System Monitoring Report'
            d['Author'] = 'System Monitor'
            d['Subject'] = 'System Resource Monitoring'
            d['Keywords'] = 'System Monitoring, Performance, Resources'
            d['CreationDate'] = datetime.now()

    def _create_overview_page(self, pdf):
        """개요 페이지"""
        fig = plt.figure(figsize=(11, 8.5))
        fig.suptitle('System Monitoring Report - Overview', fontsize=20, fontweight='bold')

        # 텍스트 정보
        ax = fig.add_subplot(111)
        ax.axis('off')

        if self.data:
            first_snapshot = self.data[0]
            last_snapshot = self.data[-1]

            info_text = f"""
MONITORING SESSION INFORMATION
{'=' * 60}

Start Time: {datetime.fromisoformat(first_snapshot['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}
End Time: {datetime.fromisoformat(last_snapshot['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}
Duration: {len(self.data) * 2} seconds ({len(self.data)} data points)

SYSTEM CONFIGURATION
{'=' * 60}

CPU:
  - Cores: {first_snapshot['cpu']['core_count']}
  - Threads: {first_snapshot['cpu']['thread_count']}
  - Frequency: {first_snapshot['cpu']['frequency']['current']:.2f} MHz

Memory:
  - Total RAM: {first_snapshot['memory']['virtual']['total_gb']} GB
  - Total Swap: {first_snapshot['memory']['swap']['total_gb']} GB

Disk:
  - Partitions: {len(first_snapshot['disk']['partitions'])}
"""

            if first_snapshot['disk']['partitions']:
                for partition in first_snapshot['disk']['partitions']:
                    info_text += f"  - {partition['mountpoint']}: {partition['total_gb']} GB\n"

            network_info = first_snapshot['network']
            info_text += f"\nNetwork:\n"
            info_text += f"  - Active Connections: {network_info['connections']}\n"
            info_text += f"  - Interfaces: {len(network_info['interfaces'])}\n"

            gpu_info = first_snapshot.get('gpu', [])
            if isinstance(gpu_info, list) and len(gpu_info) > 0:
                info_text += f"\nGPU:\n"
                for gpu in gpu_info:
                    info_text += f"  - {gpu['name']}\n"
                    info_text += f"    Memory: {gpu['memory_total']} MB\n"

            ax.text(0.05, 0.95, info_text, transform=ax.transAxes,
                   fontsize=11, verticalalignment='top', fontfamily='monospace',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

    def _create_cpu_memory_page(self, pdf):
        """CPU 및 메모리 페이지"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(11, 8.5))
        fig.suptitle('CPU and Memory Analysis', fontsize=16, fontweight='bold')

        time_indices = range(len(self.timestamps))

        # CPU 사용률 그래프
        ax1.plot(time_indices, self.cpu_data, 'b-', linewidth=2)
        ax1.fill_between(time_indices, self.cpu_data, alpha=0.3)
        ax1.set_title('CPU Usage Over Time')
        ax1.set_xlabel('Time (samples)')
        ax1.set_ylabel('CPU Usage (%)')
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(0, 100)

        # CPU 사용률 히스토그램
        ax2.hist(self.cpu_data, bins=20, color='blue', alpha=0.7, edgecolor='black')
        ax2.set_title('CPU Usage Distribution')
        ax2.set_xlabel('CPU Usage (%)')
        ax2.set_ylabel('Frequency')
        ax2.grid(True, alpha=0.3)

        # 메모리 사용률 그래프
        ax3.plot(time_indices, self.memory_data, 'g-', linewidth=2)
        ax3.fill_between(time_indices, self.memory_data, alpha=0.3, color='green')
        ax3.set_title('Memory Usage Over Time')
        ax3.set_xlabel('Time (samples)')
        ax3.set_ylabel('Memory Usage (%)')
        ax3.grid(True, alpha=0.3)
        ax3.set_ylim(0, 100)

        # 메모리 사용률 히스토그램
        ax4.hist(self.memory_data, bins=20, color='green', alpha=0.7, edgecolor='black')
        ax4.set_title('Memory Usage Distribution')
        ax4.set_xlabel('Memory Usage (%)')
        ax4.set_ylabel('Frequency')
        ax4.grid(True, alpha=0.3)

        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

    def _create_disk_network_page(self, pdf):
        """디스크 및 네트워크 페이지"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(11, 8.5))
        fig.suptitle('Disk and Network Analysis', fontsize=16, fontweight='bold')

        time_indices = range(len(self.timestamps))

        # 디스크 사용률
        ax1.plot(time_indices, self.disk_data, 'r-', linewidth=2)
        ax1.fill_between(time_indices, self.disk_data, alpha=0.3, color='red')
        ax1.set_title('Disk Usage Over Time')
        ax1.set_xlabel('Time (samples)')
        ax1.set_ylabel('Disk Usage (%)')
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(0, 100)

        # 디스크 사용 파이 차트 (평균값)
        if self.data and self.data[0]['disk']['partitions']:
            avg_disk = np.mean(self.disk_data)
            ax2.pie([avg_disk, 100-avg_disk],
                   labels=['Used', 'Free'],
                   autopct='%1.1f%%',
                   startangle=90,
                   colors=['#ff6b6b', '#51cf66'])
            ax2.set_title(f'Average Disk Usage')

        # 네트워크 전송
        ax3.plot(time_indices, self.network_sent_data, 'b-', label='Sent', linewidth=2)
        ax3.plot(time_indices, self.network_recv_data, 'orange', label='Received', linewidth=2)
        ax3.set_title('Network Traffic')
        ax3.set_xlabel('Time (samples)')
        ax3.set_ylabel('Data (MB)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        # 네트워크 누적 데이터
        if len(self.network_sent_data) > 0 and len(self.network_recv_data) > 0:
            total_sent = self.network_sent_data[-1] - self.network_sent_data[0] if len(self.network_sent_data) > 1 else 0
            total_recv = self.network_recv_data[-1] - self.network_recv_data[0] if len(self.network_recv_data) > 1 else 0

            categories = ['Sent', 'Received']
            values = [total_sent, total_recv]

            ax4.bar(categories, values, color=['#4dabf7', '#ffa94d'])
            ax4.set_title('Total Network Data Transfer')
            ax4.set_ylabel('Data (MB)')
            ax4.grid(True, alpha=0.3, axis='y')

            for i, v in enumerate(values):
                ax4.text(i, v, f'{v:.2f} MB', ha='center', va='bottom')

        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

    def _create_gpu_temp_page(self, pdf):
        """GPU 및 온도 페이지"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(11, 8.5))
        fig.suptitle('GPU and Temperature Analysis', fontsize=16, fontweight='bold')

        time_indices = range(len(self.timestamps))

        # GPU 사용률
        if any(self.gpu_data):
            ax1.plot(time_indices, self.gpu_data, 'purple', linewidth=2)
            ax1.fill_between(time_indices, self.gpu_data, alpha=0.3, color='purple')
            ax1.set_title('GPU Usage Over Time')
            ax1.set_xlabel('Time (samples)')
            ax1.set_ylabel('GPU Usage (%)')
            ax1.grid(True, alpha=0.3)
            ax1.set_ylim(0, 100)
        else:
            ax1.text(0.5, 0.5, 'GPU Data Not Available',
                    ha='center', va='center', transform=ax1.transAxes, fontsize=14)
            ax1.set_title('GPU Usage')

        # GPU 통계
        if any(self.gpu_data):
            ax2.hist(self.gpu_data, bins=15, color='purple', alpha=0.7, edgecolor='black')
            ax2.set_title('GPU Usage Distribution')
            ax2.set_xlabel('GPU Usage (%)')
            ax2.set_ylabel('Frequency')
            ax2.grid(True, alpha=0.3)
        else:
            ax2.text(0.5, 0.5, 'GPU Data Not Available',
                    ha='center', va='center', transform=ax2.transAxes, fontsize=14)
            ax2.set_title('GPU Usage Distribution')

        # 온도
        if any(self.temp_data):
            ax3.plot(time_indices, self.temp_data, 'red', linewidth=2)
            ax3.fill_between(time_indices, self.temp_data, alpha=0.3, color='red')
            ax3.set_title('Temperature Over Time')
            ax3.set_xlabel('Time (samples)')
            ax3.set_ylabel('Temperature (°C)')
            ax3.grid(True, alpha=0.3)
        else:
            ax3.text(0.5, 0.5, 'Temperature Data Not Available',
                    ha='center', va='center', transform=ax3.transAxes, fontsize=14)
            ax3.set_title('Temperature')

        # 모든 리소스 종합
        ax4.plot(time_indices, np.array(self.cpu_data), label='CPU', linewidth=2)
        ax4.plot(time_indices, np.array(self.memory_data), label='Memory', linewidth=2)
        if any(self.gpu_data):
            ax4.plot(time_indices, np.array(self.gpu_data), label='GPU', linewidth=2)
        ax4.set_title('Resource Usage Comparison')
        ax4.set_xlabel('Time (samples)')
        ax4.set_ylabel('Usage (%)')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        ax4.set_ylim(0, 100)

        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

    def _create_statistics_page(self, pdf):
        """통계 페이지"""
        fig = plt.figure(figsize=(11, 8.5))
        fig.suptitle('Statistical Summary', fontsize=16, fontweight='bold')

        ax = fig.add_subplot(111)
        ax.axis('off')

        # 통계 계산
        stats_text = "RESOURCE USAGE STATISTICS\n"
        stats_text += "=" * 60 + "\n\n"

        # CPU 통계
        stats_text += "CPU:\n"
        stats_text += f"  Average: {np.mean(self.cpu_data):.2f}%\n"
        stats_text += f"  Minimum: {np.min(self.cpu_data):.2f}%\n"
        stats_text += f"  Maximum: {np.max(self.cpu_data):.2f}%\n"
        stats_text += f"  Std Dev: {np.std(self.cpu_data):.2f}%\n\n"

        # 메모리 통계
        stats_text += "Memory:\n"
        stats_text += f"  Average: {np.mean(self.memory_data):.2f}%\n"
        stats_text += f"  Minimum: {np.min(self.memory_data):.2f}%\n"
        stats_text += f"  Maximum: {np.max(self.memory_data):.2f}%\n"
        stats_text += f"  Std Dev: {np.std(self.memory_data):.2f}%\n\n"

        # 디스크 통계
        if self.disk_data:
            stats_text += "Disk:\n"
            stats_text += f"  Average: {np.mean(self.disk_data):.2f}%\n"
            stats_text += f"  Minimum: {np.min(self.disk_data):.2f}%\n"
            stats_text += f"  Maximum: {np.max(self.disk_data):.2f}%\n"
            stats_text += f"  Std Dev: {np.std(self.disk_data):.2f}%\n\n"

        # 네트워크 통계
        if len(self.network_sent_data) > 1:
            total_sent = self.network_sent_data[-1] - self.network_sent_data[0]
            total_recv = self.network_recv_data[-1] - self.network_recv_data[0]
            stats_text += "Network:\n"
            stats_text += f"  Total Sent: {total_sent:.2f} MB\n"
            stats_text += f"  Total Received: {total_recv:.2f} MB\n"
            stats_text += f"  Total Transfer: {total_sent + total_recv:.2f} MB\n\n"

        # GPU 통계
        if any(self.gpu_data):
            stats_text += "GPU:\n"
            stats_text += f"  Average: {np.mean(self.gpu_data):.2f}%\n"
            stats_text += f"  Minimum: {np.min(self.gpu_data):.2f}%\n"
            stats_text += f"  Maximum: {np.max(self.gpu_data):.2f}%\n"
            stats_text += f"  Std Dev: {np.std(self.gpu_data):.2f}%\n\n"

        # 온도 통계
        if any(self.temp_data):
            stats_text += "Temperature:\n"
            stats_text += f"  Average: {np.mean(self.temp_data):.2f}°C\n"
            stats_text += f"  Minimum: {np.min(self.temp_data):.2f}°C\n"
            stats_text += f"  Maximum: {np.max(self.temp_data):.2f}°C\n"
            stats_text += f"  Std Dev: {np.std(self.temp_data):.2f}°C\n\n"

        # 권장사항
        stats_text += "\n" + "=" * 60 + "\n"
        stats_text += "RECOMMENDATIONS:\n"
        stats_text += "=" * 60 + "\n\n"

        if np.mean(self.cpu_data) > 80:
            stats_text += "! High CPU usage detected. Consider closing unnecessary applications.\n"
        if np.mean(self.memory_data) > 80:
            stats_text += "! High memory usage detected. Consider freeing up RAM.\n"
        if self.disk_data and np.mean(self.disk_data) > 90:
            stats_text += "! Disk space running low. Consider freeing up disk space.\n"
        if not any(self.gpu_data):
            stats_text += "- GPU monitoring not available on this system.\n"
        if not any(self.temp_data):
            stats_text += "- Temperature monitoring not available on this system.\n"

        if (np.mean(self.cpu_data) <= 80 and np.mean(self.memory_data) <= 80 and
            (not self.disk_data or np.mean(self.disk_data) <= 90)):
            stats_text += "System is operating within normal parameters.\n"

        ax.text(0.05, 0.95, stats_text, transform=ax.transAxes,
               fontsize=11, verticalalignment='top', fontfamily='monospace',
               bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))

        pdf.savefig(fig, bbox_inches='tight')
        plt.close()


if __name__ == '__main__':
    # 테스트
    import json
    test_file = 'data/monitoring_data_test.json'

    if os.path.exists(test_file):
        with open(test_file, 'r') as f:
            data = json.load(f)

        pdf_gen = PDFGenerator(data)
        pdf_gen.generate_report('data/test_report.pdf')
        print("Test PDF generated: data/test_report.pdf")
    else:
        print(f"Test file not found: {test_file}")
