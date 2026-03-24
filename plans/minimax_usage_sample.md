# MiniMax Usage API Response Sample

## Request
```bash
curl --location 'https://www.minimaxi.com/v1/api/openplatform/coding_plan/remains' \
--header 'Authorization: Bearer <API_KEY>' \
--header 'Content-Type: application/json'
```

## Response JSON
```json
{"model_remains":[{"start_time":1774317600000,"end_time":1774335600000,"remains_time":16148523,"current_interval_total_count":4500,"current_interval_usage_count":4286,"model_name":"MiniMax-M*","current_weekly_total_count":0,"current_weekly_usage_count":0,"weekly_start_time":1774195200000,"weekly_end_time":1774800000000,"weekly_remains_time":480548523},{"start_time":1774281600000,"end_time":1774368000000,"remains_time":48548523,"current_interval_total_count":19000,"current_interval_usage_count":19000,"model_name":"speech-hd","current_weekly_total_count":133000,"current_weekly_usage_count":133000,"weekly_start_time":1774195200000,"weekly_end_time":1774800000000,"weekly_remains_time":480548523},{"start_time":1774281600000,"end_time":1774368000000,"remains_time":48548523,"current_interval_total_count":3,"current_interval_usage_count":3,"model_name":"MiniMax-Hailuo-2.3-Fast-6s-768p","current_weekly_total_count":21,"current_weekly_usage_count":21,"weekly_start_time":1774195200000,"weekly_end_time":1774800000000,"weekly_remains_time":480548523},{"start_time":1774281600000,"end_time":1774368000000,"remains_time":48548523,"current_interval_total_count":3,"current_interval_usage_count":3,"model_name":"MiniMax-Hailuo-2.3-6s-768p","current_weekly_total_count":21,"current_weekly_usage_count":21,"weekly_start_time":1774195200000,"weekly_end_time":1774800000000,"weekly_remains_time":480548523},{"start_time":1774281600000,"end_time":1774368000000,"remains_time":48548523,"current_interval_total_count":7,"current_interval_usage_count":7,"model_name":"music-2.5","current_weekly_total_count":49,"current_weekly_usage_count":49,"weekly_start_time":1774195200000,"weekly_end_time":1774800000000,"weekly_remains_time":480548523},{"start_time":1774281600000,"end_time":1774368000000,"remains_time":48548523,"current_interval_total_count":200,"current_interval_usage_count":200,"model_name":"image-01","current_weekly_total_count":1400,"current_weekly_usage_count":1400,"weekly_start_time":1774195200000,"weekly_end_time":1774800000000,"weekly_remains_time":480548523}],"base_resp":{"status_code":0,"status_msg":"success"}}
```

## Data Analysis

- `model_remains`: 包含各模型用量信息的数组。
- `model_name`: 模型名称 (例如: `MiniMax-M*`)。
- `start_time` / `end_time`: 当前周期的开始/结束时间 (Unix 毫秒时间戳)。
- `remains_time`: 当前周期剩余时间 (毫秒)。
- `current_interval_total_count`: 当前周期总配额。
- `current_interval_usage_count`: 当前周期已使用量。
- `weekly_start_time` / `weekly_end_time`: 周周期的开始/结束时间。
- `current_weekly_total_count` / `current_weekly_usage_count`: 周周期配额及使用情况。

### Interval Check (MiniMax-M*)
- `start_time`: 1774317600000 -> 2026-03-24 10:00:00 (UTC+8)
- `end_time`: 1774335600000 -> 2026-03-24 15:00:00 (UTC+8)
符合 5 小时刷新的描述。
