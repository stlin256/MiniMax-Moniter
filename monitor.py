import time
import collections
import datetime
import csv
import os
from minimax_api import MiniMaxAPI, parse_model_data

class UsageMonitor:
    def __init__(self, api_key: str, model_name: str = "MiniMax-M*", display_mode: str = "Used"):
        self.api = MiniMaxAPI(api_key)
        self.model_name = model_name
        self.display_mode = display_mode
        self.history = collections.deque(maxlen=60) 
        self.current_data = None
        self.error_message = None
        self.csv_file = "usage_history.csv"

    def update_params(self, api_key: str, model_name: str, display_mode: str = "Used"):
        self.api.api_key = api_key
        self.model_name = model_name
        self.display_mode = display_mode

    def log_to_csv(self):
        if not self.current_data:
            return
        
        try:
            file_exists = os.path.exists(self.csv_file)
            key_suffix = self.api.api_key[-6:] if len(self.api.api_key) >= 6 else "N/A"
            
            # Data to log
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            remains = self.current_data.get("current_interval_usage_count", 0)
            total = self.current_data.get("current_interval_total_count", 0)
            rpm = self.get_rpm()
            interval = self.get_interval_str()
            
            with open(self.csv_file, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if not file_exists:
                    # Write header
                    writer.writerow(["Timestamp", "Key_Suffix", "Model", "Remains", "Total", "RPM"])
                
                writer.writerow([timestamp, key_suffix, self.model_name, remains, total, rpm])
        except Exception:
            pass

    def update(self):
        raw_data = self.api.fetch_data()
        if not raw_data or "error" in raw_data:
            self.error_message = raw_data.get("error", "Unknown error") if raw_data else "No data"
            return False
        
        model_data = parse_model_data(raw_data, self.model_name)
        if not model_data:
            if "model_remains" in raw_data and raw_data["model_remains"]:
                model_data = raw_data["model_remains"][0]
                self.model_name = model_data["model_name"]
            else:
                self.error_message = f"Model {self.model_name} not found"
                return False

        self.current_data = model_data
        self.error_message = None
        
        try:
            usage = int(model_data.get("current_interval_usage_count", 0))
            self.history.append((time.time(), usage))
            # Log each successful update to CSV
            self.log_to_csv()
        except Exception:
            pass
            
        return True

    def get_rpm(self) -> int:
        if len(self.history) < 5:
            return 0
        
        start_time, start_usage = self.history[0]
        end_time, end_usage = self.history[-1]
        
        time_diff = end_time - start_time
        if time_diff < 1.0:
            return 0
            
        # usage decreases as it represents remains, so delta is absolute
        usage_diff = abs(end_usage - start_usage)
        rpm = (usage_diff / time_diff) * 60
        return int(round(rpm))

    def get_usage_str(self) -> str:
        if not self.current_data:
            return "N/A"
        # API field is REMAINS
        api_remains = int(self.current_data.get("current_interval_usage_count", 0))
        total = int(self.current_data.get("current_interval_total_count", 0))
        
        if self.display_mode == "Remains":
            return f"{api_remains} / {total}"
        else: # "Used"
            used = max(0, total - api_remains)
            return f"{used} / {total}"

    def get_interval_str(self) -> str:
        if not self.current_data:
            return "N/A"
        start_ms = self.current_data.get("start_time", 0)
        end_ms = self.current_data.get("end_time", 0)
        
        start_dt = datetime.datetime.fromtimestamp(start_ms / 1000)
        end_dt = datetime.datetime.fromtimestamp(end_ms / 1000)
        
        return f"{start_dt.strftime('%H:%M')} - {end_dt.strftime('%H:%M')}"
