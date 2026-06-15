# monitor.py
import psutil

class SystemMonitor:
    def __init__(self):
        self.net_io = psutil.net_io_counters()
    
    def get_cpu(self):
        return psutil.cpu_percent(interval=0.1)
    
    def get_ram(self):
        mem = psutil.virtual_memory()
        return {
            'percent': round(mem.percent, 1),
            'used': mem.used // (1024**2),
            'total': mem.total // (1024**2)
        }
    
    def get_disk(self):
        disk = psutil.disk_usage('/')
        return {
            'percent': round(disk.percent, 1),
            'used': disk.used // (1024**3),
            'total': disk.total // (1024**3)
        }
    
    def get_network(self):
        net = psutil.net_io_counters()
        bytes_sent = net.bytes_sent - self.net_io.bytes_sent
        bytes_recv = net.bytes_recv - self.net_io.bytes_recv
        self.net_io = net
        return {
            'sent': round(bytes_sent / 1024, 1),   # KB/s
            'recv': round(bytes_recv / 1024, 1)    # KB/s
        }
    
    def get_all_processes(self, limit=300):
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'num_threads', 'status']):
            try:
                processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'] or 'Unknown',
                    'cpu': round(proc.info.get('cpu_percent') or 0, 1),
                    'mem': round(proc.info.get('memory_percent') or 0, 1),
                    'threads': proc.info.get('num_threads') or 0,
                    'status': proc.info.get('status', 'unknown')
                })
            except:
                pass
        return processes[:limit]
    
    def kill_process(self, pid):
        try:
            psutil.Process(pid).kill()
            return True
        except:
            return False