import psutil
import time
from datetime import datetime
import json
import os

try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False


class SystemMonitor:
    def __init__(self):
        self.monitoring_data = []
        self.start_time = None
        self.net_io_start = psutil.net_io_counters()

    def get_cpu_info(self):
        """CPU 정보 수집"""
        cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
        cpu_freq = psutil.cpu_freq()

        return {
            'usage_per_core': cpu_percent,
            'usage_total': psutil.cpu_percent(interval=0),
            'core_count': psutil.cpu_count(logical=False),
            'thread_count': psutil.cpu_count(logical=True),
            'frequency': {
                'current': cpu_freq.current if cpu_freq else 0,
                'min': cpu_freq.min if cpu_freq else 0,
                'max': cpu_freq.max if cpu_freq else 0
            }
        }

    def get_memory_info(self):
        """메모리 정보 수집"""
        virtual_mem = psutil.virtual_memory()
        swap_mem = psutil.swap_memory()

        return {
            'virtual': {
                'total': virtual_mem.total,
                'available': virtual_mem.available,
                'used': virtual_mem.used,
                'percent': virtual_mem.percent,
                'total_gb': round(virtual_mem.total / (1024**3), 2),
                'used_gb': round(virtual_mem.used / (1024**3), 2),
                'available_gb': round(virtual_mem.available / (1024**3), 2)
            },
            'swap': {
                'total': swap_mem.total,
                'used': swap_mem.used,
                'free': swap_mem.free,
                'percent': swap_mem.percent,
                'total_gb': round(swap_mem.total / (1024**3), 2),
                'used_gb': round(swap_mem.used / (1024**3), 2)
            }
        }

    def get_disk_info(self):
        """디스크 정보 수집"""
        disk_partitions = psutil.disk_partitions()
        disk_info = []

        for partition in disk_partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_info.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': usage.percent,
                    'total_gb': round(usage.total / (1024**3), 2),
                    'used_gb': round(usage.used / (1024**3), 2),
                    'free_gb': round(usage.free / (1024**3), 2)
                })
            except PermissionError:
                continue

        # 디스크 I/O 통계
        disk_io = psutil.disk_io_counters()
        if disk_io:
            io_info = {
                'read_bytes': disk_io.read_bytes,
                'write_bytes': disk_io.write_bytes,
                'read_count': disk_io.read_count,
                'write_count': disk_io.write_count,
                'read_mb': round(disk_io.read_bytes / (1024**2), 2),
                'write_mb': round(disk_io.write_bytes / (1024**2), 2)
            }
        else:
            io_info = None

        return {
            'partitions': disk_info,
            'io': io_info
        }

    def get_network_info(self):
        """네트워크 정보 수집"""
        net_io = psutil.net_io_counters()
        net_connections = len(psutil.net_connections())

        # 네트워크 인터페이스별 정보
        net_if_addrs = psutil.net_if_addrs()
        net_if_stats = psutil.net_if_stats()

        interfaces = []
        for interface_name, addresses in net_if_addrs.items():
            interface_info = {
                'name': interface_name,
                'addresses': []
            }

            for addr in addresses:
                interface_info['addresses'].append({
                    'family': str(addr.family),
                    'address': addr.address,
                    'netmask': addr.netmask,
                    'broadcast': addr.broadcast
                })

            if interface_name in net_if_stats:
                stats = net_if_stats[interface_name]
                interface_info['is_up'] = stats.isup
                interface_info['speed'] = stats.speed

            interfaces.append(interface_info)

        # 전송 속도 계산 (이전 측정값과 비교)
        bytes_sent_delta = net_io.bytes_sent - self.net_io_start.bytes_sent
        bytes_recv_delta = net_io.bytes_recv - self.net_io_start.bytes_recv

        return {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv,
            'errin': net_io.errin,
            'errout': net_io.errout,
            'dropin': net_io.dropin,
            'dropout': net_io.dropout,
            'sent_mb': round(net_io.bytes_sent / (1024**2), 2),
            'recv_mb': round(net_io.bytes_recv / (1024**2), 2),
            'sent_delta_mb': round(bytes_sent_delta / (1024**2), 2),
            'recv_delta_mb': round(bytes_recv_delta / (1024**2), 2),
            'connections': net_connections,
            'interfaces': interfaces
        }

    def get_temperature_info(self):
        """온도 정보 수집"""
        temps = {}

        try:
            if hasattr(psutil, 'sensors_temperatures'):
                sensors = psutil.sensors_temperatures()
                if sensors:
                    for name, entries in sensors.items():
                        temps[name] = []
                        for entry in entries:
                            temps[name].append({
                                'label': entry.label,
                                'current': entry.current,
                                'high': entry.high,
                                'critical': entry.critical
                            })
        except Exception as e:
            temps['error'] = str(e)

        return temps if temps else {'info': 'Temperature sensors not available'}

    def get_gpu_info(self):
        """GPU 정보 수집"""
        if not GPU_AVAILABLE:
            return {'error': 'GPUtil not available'}

        try:
            gpus = GPUtil.getGPUs()
            gpu_info = []

            for gpu in gpus:
                gpu_info.append({
                    'id': gpu.id,
                    'name': gpu.name,
                    'load': round(gpu.load * 100, 2),
                    'memory_used': gpu.memoryUsed,
                    'memory_total': gpu.memoryTotal,
                    'memory_percent': round((gpu.memoryUsed / gpu.memoryTotal) * 100, 2),
                    'temperature': gpu.temperature,
                    'uuid': gpu.uuid
                })

            return gpu_info if gpu_info else {'info': 'No GPU detected'}
        except Exception as e:
            return {'error': str(e)}

    def get_process_info(self):
        """프로세스 정보 수집 (상위 10개)"""
        processes = []

        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        # CPU 사용량 기준으로 정렬
        processes.sort(key=lambda x: x.get('cpu_percent', 0) or 0, reverse=True)

        return processes[:10]

    def collect_snapshot(self):
        """현재 시점의 모든 시스템 정보 수집"""
        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'cpu': self.get_cpu_info(),
            'memory': self.get_memory_info(),
            'disk': self.get_disk_info(),
            'network': self.get_network_info(),
            'temperature': self.get_temperature_info(),
            'gpu': self.get_gpu_info(),
            'top_processes': self.get_process_info()
        }

        return snapshot

    def start_monitoring(self, duration=300, interval=2):
        """
        지정된 시간 동안 모니터링 시작
        duration: 모니터링 시간 (초), 기본 300초 (5분)
        interval: 데이터 수집 간격 (초), 기본 2초
        """
        self.start_time = datetime.now()
        self.monitoring_data = []

        end_time = time.time() + duration

        while time.time() < end_time:
            snapshot = self.collect_snapshot()
            self.monitoring_data.append(snapshot)
            time.sleep(interval)

        return self.monitoring_data

    def save_data(self, filename=None):
        """수집된 데이터를 JSON 파일로 저장"""
        if filename is None:
            filename = f"monitoring_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        filepath = os.path.join('data', filename)
        os.makedirs('data', exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.monitoring_data, f, ensure_ascii=False, indent=2)

        return filepath

    def load_data(self, filepath):
        """저장된 JSON 데이터 로드"""
        with open(filepath, 'r', encoding='utf-8') as f:
            self.monitoring_data = json.load(f)

        return self.monitoring_data


if __name__ == '__main__':
    # 테스트
    monitor = SystemMonitor()
    print("Starting 30 second test monitoring...")
    data = monitor.start_monitoring(duration=30, interval=2)
    filepath = monitor.save_data()
    print(f"Data saved to: {filepath}")
    print(f"Collected {len(data)} snapshots")
