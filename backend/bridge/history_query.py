"""
历史数据查询服务
"""
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone, timedelta
from loguru import logger
from backend.core.influxdb import get_influx_client
from backend.config import get_settings

settings = get_settings()

# 北京时区 (UTC+8)
BEIJING_TZ = timezone(timedelta(hours=8))


class HistoryQueryService:
    
    _instance: Optional['HistoryQueryService'] = None
    
    # 1. 初始化历史查询服务
    def __init__(self):
        self.client = get_influx_client()
        self.query_api = self.client.query_api()
        logger.info("历史数据查询服务已初始化")
    
    # 2. 时间转换工具方法
    @staticmethod
    def _utc_to_beijing(utc_time: datetime) -> str:
        """将 UTC 时间转换为北京时间字符串
        
        Args:
            utc_time: UTC 时间（带时区信息）
            
        Returns:
            北京时间字符串（ISO 格式，如 "2026-02-02T15:30:00+08:00"）
        """
        if utc_time is None:
            return None
        
        # 确保是 UTC 时区
        if utc_time.tzinfo is None:
            utc_time = utc_time.replace(tzinfo=timezone.utc)
        
        # 转换为北京时间
        beijing_time = utc_time.astimezone(BEIJING_TZ)
        return beijing_time.isoformat()
    
    @staticmethod
    def _beijing_to_utc(beijing_time: datetime) -> datetime:
        """将北京时间转换为 UTC 时间
        
        Args:
            beijing_time: 北京时间（可能无时区信息）
            
        Returns:
            UTC 时间（带时区信息）
        """
        if beijing_time is None:
            return None
        
        # 如果是 naive datetime（无时区信息），假设为北京时间
        if beijing_time.tzinfo is None:
            beijing_time = beijing_time.replace(tzinfo=BEIJING_TZ)
        
        # 转换为 UTC
        utc_time = beijing_time.astimezone(timezone.utc)
        return utc_time
    
    # 3. 获取单例实例
    @classmethod
    def get_instance(cls) -> 'HistoryQueryService':
        if cls._instance is None:
            logger.info("创建 HistoryQueryService 单例实例")
            cls._instance = cls()
        return cls._instance
    
    # 4. 查询所有批次号列表（按时间倒序）
    def get_batch_list(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        查询所有批次号列表
        
        Args:
            limit: 返回的最大批次数量
            
        Returns:
            批次列表，每个批次包含：
            - batch_code: 批次号
            - start_time: 开始时间
        """
        try:
            # 只查询弧流数据的批次号，避免类型冲突
            query = f'''
            from(bucket: "{settings.influx_bucket}")
              |> range(start: -90d)
              |> filter(fn: (r) => r["_measurement"] == "sensor_data")
              |> filter(fn: (r) => r["_field"] == "arc_current_U")
              |> filter(fn: (r) => r["batch_code"] != "")
              |> group(columns: ["batch_code"])
              |> first()
            '''
            
            result = self.query_api.query(query)
            
            batches_dict = {}
            
            for table in result:
                for record in table.records:
                    batch_code = record.values.get("batch_code")
                    time_val = record.get_time()
                    
                    if batch_code:
                        if batch_code not in batches_dict:
                            batches_dict[batch_code] = time_val
                        else:
                            # 保留最早的时间
                            if time_val < batches_dict[batch_code]:
                                batches_dict[batch_code] = time_val
            
            # 按时间倒序排序，并转换为北京时间
            batches = [
                {
                    "batch_code": code,
                    "start_time": self._utc_to_beijing(time_val) if time_val else None,
                }
                for code, time_val in sorted(batches_dict.items(), key=lambda x: x[1], reverse=True)
            ]
            
            # 限制数量
            batches = batches[:limit]
            
            logger.info(f"查询到 {len(batches)} 个批次")
            return batches
            
        except Exception as e:
            logger.error(f"查询批次列表失败: {e}")
            return []
    
    # 5. 查询弧流弧压历史数据
    def query_arc_data(
        self, 
        batch_code: str, 
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        interval: str = "1m"
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        查询弧流弧压历史数据
        
        Args:
            batch_code: 批次号
            start_time: 开始时间（可选）
            end_time: 结束时间（可选）
            interval: 聚合间隔（默认1分钟）
            
        Returns:
            包含 arc_current 和 arc_voltage 的字典
        """
        try:
            time_filter = self._build_time_filter(batch_code, start_time, end_time)
            
            query = f'''
            from(bucket: "{settings.influx_bucket}")
              {time_filter}
              |> filter(fn: (r) => r["_measurement"] == "sensor_data")
              |> filter(fn: (r) => r["batch_code"] == "{batch_code}")
              |> filter(fn: (r) => r["_field"] =~ /^arc_current_[UVW]$/ or r["_field"] =~ /^arc_voltage_[UVW]$/)
              |> aggregateWindow(every: {interval}, fn: mean, createEmpty: false)
            '''
            
            result = self.query_api.query(query)
            
            arc_current = {"U": [], "V": [], "W": []}
            arc_voltage = {"U": [], "V": [], "W": []}
            
            for table in result:
                for record in table.records:
                    field = record.get_field()
                    utc_time = record.get_time()
                    beijing_time = self._utc_to_beijing(utc_time)
                    value = record.get_value()
                    
                    if field.startswith("arc_current_"):
                        phase = field.split("_")[-1]
                        arc_current[phase].append({"time": beijing_time, "value": value})
                    elif field.startswith("arc_voltage_"):
                        phase = field.split("_")[-1]
                        arc_voltage[phase].append({"time": beijing_time, "value": value})
            
            return {
                "arc_current": arc_current,
                "arc_voltage": arc_voltage
            }
            
        except Exception as e:
            logger.error(f"查询弧流弧压数据失败: {e}")
            return {"arc_current": {"U": [], "V": [], "W": []}, "arc_voltage": {"U": [], "V": [], "W": []}}
    
    # 6. 查询电极深度历史数据
    def query_electrode_depth(
        self,
        batch_code: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        interval: str = "1m"
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        查询电极深度历史数据
        
        Returns:
            包含三个电极深度的字典
        """
        try:
            time_filter = self._build_time_filter(batch_code, start_time, end_time)
            
            query = f'''
            from(bucket: "{settings.influx_bucket}")
              {time_filter}
              |> filter(fn: (r) => r["_measurement"] == "sensor_data")
              |> filter(fn: (r) => r["batch_code"] == "{batch_code}")
              |> filter(fn: (r) => r["_field"] == "distance_mm")
              |> aggregateWindow(every: {interval}, fn: mean, createEmpty: false)
            '''
            
            result = self.query_api.query(query)
            
            electrode_depth = {"1": [], "2": [], "3": []}
            
            for table in result:
                for record in table.records:
                    sensor = record.values.get("sensor", "")
                    if "electrode_" in sensor:
                        electrode_num = sensor.split("_")[-1]
                        utc_time = record.get_time()
                        beijing_time = self._utc_to_beijing(utc_time)
                        value = record.get_value()
                        electrode_depth[electrode_num].append({"time": beijing_time, "value": value})
            
            logger.info(f"查询到电极深度数据: 1#{len(electrode_depth['1'])}点, 2#{len(electrode_depth['2'])}点, 3#{len(electrode_depth['3'])}点")
            return electrode_depth
            
        except Exception as e:
            logger.error(f"查询电极深度数据失败: {e}")
            return {"1": [], "2": [], "3": []}
    
    # 7. 查询功率能耗历史数据
    def query_power_energy(
        self,
        batch_code: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        interval: str = "1m"
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        查询功率和能耗历史数据
        
        Returns:
            包含 power 和 energy 的字典
        """
        try:
            time_filter = self._build_time_filter(batch_code, start_time, end_time)
            
            query = f'''
            from(bucket: "{settings.influx_bucket}")
              {time_filter}
              |> filter(fn: (r) => r["_measurement"] == "sensor_data")
              |> filter(fn: (r) => r["batch_code"] == "{batch_code}")
              |> filter(fn: (r) => r["_field"] == "power_total" or r["_field"] == "energy_total")
              |> aggregateWindow(every: {interval}, fn: mean, createEmpty: false)
            '''
            
            result = self.query_api.query(query)
            
            power = []
            energy = []
            
            for table in result:
                for record in table.records:
                    field = record.get_field()
                    utc_time = record.get_time()
                    beijing_time = self._utc_to_beijing(utc_time)
                    value = record.get_value()
                    
                    if field == "power_total":
                        power.append({"time": beijing_time, "value": value})
                    elif field == "energy_total":
                        energy.append({"time": beijing_time, "value": value})
            
            logger.info(f"查询到功率能耗数据: 功率{len(power)}点, 能耗{len(energy)}点")
            return {"power": power, "energy": energy}
            
        except Exception as e:
            logger.error(f"查询功率能耗数据失败: {e}")
            return {"power": [], "energy": []}
    
    # 8. 查询料仓历史数据
    def query_hopper_data(
        self,
        batch_code: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        interval: str = "1m"
    ) -> Dict[str, Any]:
        """
        查询料仓历史数据（投料累计曲线）
        
        注意：投料累计数据是阶梯状的，每次投料时才会更新，所以不使用聚合
        
        Returns:
            包含 feeding_total 的字典
        """
        try:
            time_filter = self._build_time_filter(batch_code, start_time, end_time)
            
            # 查询投料累计（不使用聚合，保留所有数据点）
            query_feeding = f'''
            from(bucket: "{settings.influx_bucket}")
              {time_filter}
              |> filter(fn: (r) => r["_measurement"] == "sensor_data")
              |> filter(fn: (r) => r["batch_code"] == "{batch_code}")
              |> filter(fn: (r) => r["module_type"] == "feeding")
              |> filter(fn: (r) => r["device_type"] == "hopper")
              |> filter(fn: (r) => r["_field"] == "feeding_total")
              |> sort(columns: ["_time"])
            '''
            
            result = self.query_api.query(query_feeding)
            
            feeding_total = []
            
            for table in result:
                for record in table.records:
                    utc_time = record.get_time()
                    beijing_time = self._utc_to_beijing(utc_time)
                    value = record.get_value()
                    feeding_total.append({"time": beijing_time, "value": value})
            
            logger.info(f"查询到料仓数据: 投料累计{len(feeding_total)}点")
            return {"feeding_total": feeding_total}
            
        except Exception as e:
            logger.error(f"查询料仓数据失败: {e}")
            return {"feeding_total": []}
    
    # 9. 查询冷却水历史数据
    def query_cooling_water(
        self,
        batch_code: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        interval: str = "1m"
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        查询冷却水历史数据
        
        Returns:
            包含炉皮和炉盖冷却水累计流量的字典
        """
        try:
            time_filter = self._build_time_filter(batch_code, start_time, end_time)
            
            query = f'''
            from(bucket: "{settings.influx_bucket}")
              {time_filter}
              |> filter(fn: (r) => r["_measurement"] == "sensor_data")
              |> filter(fn: (r) => r["batch_code"] == "{batch_code}")
              |> filter(fn: (r) => r["_field"] == "furnace_shell_water_total" or r["_field"] == "furnace_cover_water_total")
              |> aggregateWindow(every: {interval}, fn: mean, createEmpty: false)
            '''
            
            result = self.query_api.query(query)
            
            shell_water = []
            cover_water = []
            
            for table in result:
                for record in table.records:
                    field = record.get_field()
                    utc_time = record.get_time()
                    beijing_time = self._utc_to_beijing(utc_time)
                    value = record.get_value()
                    
                    if field == "furnace_shell_water_total":
                        shell_water.append({"time": beijing_time, "value": value})
                    elif field == "furnace_cover_water_total":
                        cover_water.append({"time": beijing_time, "value": value})
            
            logger.info(f"查询到冷却水数据: 炉皮{len(shell_water)}点, 炉盖{len(cover_water)}点")
            return {"shell_water": shell_water, "cover_water": cover_water}
            
        except Exception as e:
            logger.error(f"查询冷却水数据失败: {e}")
            return {"shell_water": [], "cover_water": []}
    
    # 10. 查询投料记录（详细记录）
    def query_feeding_records(
        self,
        batch_code: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 300
    ) -> List[Dict[str, Any]]:
        """
        查询投料记录（每次投料的详细记录）
        
        Args:
            batch_code: 批次号
            start_time: 开始时间（可选）
            end_time: 结束时间（可选）
            limit: 最大返回记录数
            
        Returns:
            投料记录列表 [{'time': str, 'discharge_weight': float, 'feeding_total': float}, ...]
        """
        try:
            time_filter = self._build_time_filter(batch_code, start_time, end_time)
            
            # 只查询 discharge_weight 字段（每次投料的重量）
            # 注意：不使用 pivot，因为可能导致数据丢失
            query = f'''
            from(bucket: "{settings.influx_bucket}")
              {time_filter}
              |> filter(fn: (r) => r["_measurement"] == "sensor_data")
              |> filter(fn: (r) => r["batch_code"] == "{batch_code}")
              |> filter(fn: (r) => r["module_type"] == "feeding")
              |> filter(fn: (r) => r["device_type"] == "hopper")
              |> filter(fn: (r) => r["_field"] == "discharge_weight")
              |> sort(columns: ["_time"], desc: true)
              |> limit(n: {limit})
            '''
            
            result = self.query_api.query(query)
            
            records = []
            
            for table in result:
                for record in table.records:
                    utc_time = record.get_time()
                    beijing_time = self._utc_to_beijing(utc_time)
                    discharge_weight = record.get_value()
                    
                    # 只返回有效的投料记录（排料重量 > 0）
                    if discharge_weight and discharge_weight > 0:
                        records.append({
                            'time': beijing_time,
                            'discharge_weight': discharge_weight,
                            'feeding_total': 0.0  # 占位，前端不使用
                        })
            
            logger.info(f"查询到 {len(records)} 条投料记录")
            return records
            
        except Exception as e:
            logger.error(f"查询投料记录失败: {e}", exc_info=True)
            return []
    
    # 11. 查询当前批次投料累计历史数据（无聚合，返回 UTC 时间）
    def query_feeding_total_raw(
        self,
        batch_code: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        查询当前批次投料累计历史数据（无聚合）
        
        注意：返回的时间是 UTC 时间（datetime 对象），调用方需要自行转换为北京时间
        
        Args:
            batch_code: 批次号
            start_time: 开始时间（可选）
            end_time: 结束时间（可选）
            
        Returns:
            投料累计数据列表 [{'time': datetime (UTC), 'value': float}, ...]
        """
        try:
            time_filter = self._build_time_filter(batch_code, start_time, end_time)
            
            # 查询投料累计数据
            query = f'''
            from(bucket: "{settings.influx_bucket}")
              {time_filter}
              |> filter(fn: (r) => r["_measurement"] == "sensor_data")
              |> filter(fn: (r) => r["batch_code"] == "{batch_code}")
              |> filter(fn: (r) => r["module_type"] == "feeding")
              |> filter(fn: (r) => r["device_type"] == "hopper")
              |> filter(fn: (r) => r["_field"] == "feeding_total")
              |> sort(columns: ["_time"])
            '''
            
            result = self.query_api.query(query)
            
            feeding_data = []
            
            for table in result:
                for record in table.records:
                    time = record.get_time()  # UTC 时间
                    value = record.get_value()
                    
                    feeding_data.append({
                        'time': time,
                        'value': value
                    })
            
            logger.info(f"查询到 {len(feeding_data)} 条投料累计数据")
            return feeding_data
            
        except Exception as e:
            logger.error(f"查询投料累计数据失败: {e}")
            return []
    
    # 12. 计算最佳聚合间隔
    def calculate_optimal_interval(self, start_time: datetime, end_time: datetime, target_points: int = 100) -> str:
        """
        根据时间跨度计算最佳聚合间隔，确保数据点数量在目标范围内
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            target_points: 目标数据点数量（默认100）
            
        Returns:
            聚合间隔字符串（如 "1m", "5m", "1h"）
        """
        time_span_seconds = (end_time - start_time).total_seconds()
        
        # 计算理想的间隔秒数
        ideal_interval_seconds = time_span_seconds / target_points
        
        # 定义可用的间隔选项（秒数 -> Flux 格式）
        intervals = [
            (10, "10s"),
            (30, "30s"),
            (60, "1m"),
            (120, "2m"),
            (300, "5m"),
            (600, "10m"),
            (900, "15m"),
            (1800, "30m"),
            (3600, "1h"),
            (7200, "2h"),
            (14400, "4h"),
        ]
        
        # 选择最接近的间隔
        best_interval = intervals[0][1]
        min_diff = abs(ideal_interval_seconds - intervals[0][0])
        
        for seconds, flux_format in intervals:
            diff = abs(ideal_interval_seconds - seconds)
            if diff < min_diff:
                min_diff = diff
                best_interval = flux_format
        
        logger.info(f"时间跨度: {time_span_seconds/3600:.1f}小时, 选择聚合间隔: {best_interval}")
        return best_interval
    
    # 13. 构建时间过滤器
    def _build_time_filter(
        self, 
        batch_code: str, 
        start_time: Optional[datetime], 
        end_time: Optional[datetime]
    ) -> str:
        """构建 Flux 查询的时间过滤器
        
        注意：InfluxDB 使用 UTC 时间，需要将本地时间（北京时间 UTC+8）转换为 UTC
        """
        if start_time and end_time:
            # 使用统一的时间转换方法
            start_utc = self._beijing_to_utc(start_time)
            end_utc = self._beijing_to_utc(end_time)
            
            start_iso = start_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
            end_iso = end_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
            
            logger.info(f"时间转换: 北京时间 {start_time} - {end_time} => UTC {start_iso} - {end_iso}")
            return f'|> range(start: {start_iso}, stop: {end_iso})'
        else:
            return '|> range(start: -90d)'
    
    # 14. 查询批次的时间范围（优化版：使用 first + last）
    def query_batch_time_range(self, batch_code: str) -> Tuple[Optional[datetime], Optional[datetime]]:
        """
        查询批次的起始时间和结束时间（第一条和最后一条数据的时间）
        
        优化说明：
        - 优化前：扫描所有数据点，然后排序，非常慢
        - 优化后：使用 first() + last() 只查询首尾两条数据，速度提升 100 倍以上
        
        Args:
            batch_code: 批次号
            
        Returns:
            (start_time, end_time) 元组（北京时间），如果查询失败返回 (None, None)
        """
        try:
            # 查询第一条数据的时间
            query_first = f'''
            from(bucket: "{settings.influx_bucket}")
              |> range(start: -90d)
              |> filter(fn: (r) => r["_measurement"] == "sensor_data")
              |> filter(fn: (r) => r["batch_code"] == "{batch_code}")
              |> filter(fn: (r) => r["_field"] == "arc_current_U")
              |> first()
            '''
            
            # 查询最后一条数据的时间
            query_last = f'''
            from(bucket: "{settings.influx_bucket}")
              |> range(start: -90d)
              |> filter(fn: (r) => r["_measurement"] == "sensor_data")
              |> filter(fn: (r) => r["batch_code"] == "{batch_code}")
              |> filter(fn: (r) => r["_field"] == "arc_current_U")
              |> last()
            '''
            
            first_result = self.query_api.query(query_first)
            last_result = self.query_api.query(query_last)
            
            start_time_utc = None
            end_time_utc = None
            
            # 获取第一条数据的时间
            for table in first_result:
                for record in table.records:
                    start_time_utc = record.get_time()
                    break
            
            # 获取最后一条数据的时间
            for table in last_result:
                for record in table.records:
                    end_time_utc = record.get_time()
                    break
            
            if not start_time_utc or not end_time_utc:
                logger.warning(f"批次 {batch_code} 没有找到数据")
                return (None, None)
            
            # 转换为北京时间
            start_time_beijing = self._utc_to_beijing(start_time_utc)
            end_time_beijing = self._utc_to_beijing(end_time_utc)
            
            # 转换为 datetime 对象（去掉时区信息，保持北京时间）
            from dateutil import parser
            start_time = parser.isoparse(start_time_beijing).replace(tzinfo=None)
            end_time = parser.isoparse(end_time_beijing).replace(tzinfo=None)
            
            logger.info(f"批次 {batch_code} 时间范围: {start_time} - {end_time}")
            return (start_time, end_time)
            
        except Exception as e:
            logger.error(f"查询批次时间范围失败: {e}", exc_info=True)
            return (None, None)
    
    # 15. 查询批次统计数据（用于批次对比）
    def query_batch_statistics(self, batch_code: str) -> Dict[str, Any]:
        """
        查询单个批次的统计数据
        
        Args:
            batch_code: 批次号
            
        Returns:
            {
                'batch_code': str,
                'energy_total': float,      # 累计能耗 (kWh) - 最大值
                'feeding_total': float,     # 累计投料 (kg) - 最大值
                'shell_water_total': float, # 炉皮累计水流量 (m³) - 最大值
                'cover_water_total': float, # 炉盖累计水流量 (m³) - 最大值
                'duration_hours': float,    # 开炉时长 (小时) - 第一个到最后一个数据点的时间差
                'start_time': str,          # 开始时间
                'end_time': str             # 结束时间
            }
        """
        try:
            result = {
                'batch_code': batch_code,
                'energy_total': 0.0,
                'feeding_total': 0.0,
                'shell_water_total': 0.0,
                'cover_water_total': 0.0,
                'duration_hours': 0.0,
                'start_time': None,
                'end_time': None
            }
            
            # 1. 查询累计能耗最大值
            query_energy = f'''
            from(bucket: "{settings.influx_bucket}")
              |> range(start: -90d)
              |> filter(fn: (r) => r["_measurement"] == "sensor_data")
              |> filter(fn: (r) => r["batch_code"] == "{batch_code}")
              |> filter(fn: (r) => r["_field"] == "energy_total")
              |> max()
            '''
            
            energy_result = self.query_api.query(query_energy)
            for table in energy_result:
                for record in table.records:
                    result['energy_total'] = record.get_value() or 0.0
                    break
            
            # 2. 查询累计投料最大值 (使用新标签格式)
            query_feeding = f'''
            from(bucket: "{settings.influx_bucket}")
              |> range(start: -90d)
              |> filter(fn: (r) => r["_measurement"] == "sensor_data")
              |> filter(fn: (r) => r["batch_code"] == "{batch_code}")
              |> filter(fn: (r) => r["module_type"] == "feeding")
              |> filter(fn: (r) => r["device_type"] == "hopper")
              |> filter(fn: (r) => r["_field"] == "feeding_total")
              |> max()
            '''
            
            feeding_result = self.query_api.query(query_feeding)
            for table in feeding_result:
                for record in table.records:
                    result['feeding_total'] = record.get_value() or 0.0
                    break
            
            # 3. 查询炉皮累计水流量最大值
            query_shell = f'''
            from(bucket: "{settings.influx_bucket}")
              |> range(start: -90d)
              |> filter(fn: (r) => r["_measurement"] == "sensor_data")
              |> filter(fn: (r) => r["batch_code"] == "{batch_code}")
              |> filter(fn: (r) => r["_field"] == "furnace_shell_water_total")
              |> max()
            '''
            
            shell_result = self.query_api.query(query_shell)
            for table in shell_result:
                for record in table.records:
                    result['shell_water_total'] = record.get_value() or 0.0
                    break
            
            # 4. 查询炉盖累计水流量最大值
            query_cover = f'''
            from(bucket: "{settings.influx_bucket}")
              |> range(start: -90d)
              |> filter(fn: (r) => r["_measurement"] == "sensor_data")
              |> filter(fn: (r) => r["batch_code"] == "{batch_code}")
              |> filter(fn: (r) => r["_field"] == "furnace_cover_water_total")
              |> max()
            '''
            
            cover_result = self.query_api.query(query_cover)
            for table in cover_result:
                for record in table.records:
                    result['cover_water_total'] = record.get_value() or 0.0
                    break
            
            # 5. 查询开炉时长（使用混合方案：first + last，快速且准确）
            # 优化前：扫描所有数据点，非常慢
            # 优化后：只查询第一条和最后一条数据，速度提升 100 倍以上
            query_first = f'''
            from(bucket: "{settings.influx_bucket}")
              |> range(start: -90d)
              |> filter(fn: (r) => r["_measurement"] == "sensor_data")
              |> filter(fn: (r) => r["batch_code"] == "{batch_code}")
              |> filter(fn: (r) => r["_field"] == "arc_current_U")
              |> first()
            '''
            
            query_last = f'''
            from(bucket: "{settings.influx_bucket}")
              |> range(start: -90d)
              |> filter(fn: (r) => r["_measurement"] == "sensor_data")
              |> filter(fn: (r) => r["batch_code"] == "{batch_code}")
              |> filter(fn: (r) => r["_field"] == "arc_current_U")
              |> last()
            '''
            
            first_result = self.query_api.query(query_first)
            last_result = self.query_api.query(query_last)
            
            start_time = None
            end_time = None
            
            # 获取第一条数据的时间
            for table in first_result:
                for record in table.records:
                    start_time = record.get_time()
                    break
            
            # 获取最后一条数据的时间
            for table in last_result:
                for record in table.records:
                    end_time = record.get_time()
                    break
            
            if start_time and end_time:
                result['start_time'] = self._utc_to_beijing(start_time)
                result['end_time'] = self._utc_to_beijing(end_time)
                
                # 计算时长（小时）
                duration_seconds = (end_time - start_time).total_seconds()
                result['duration_hours'] = duration_seconds / 3600.0
            
            logger.info(f"批次 {batch_code} 统计数据: 能耗={result['energy_total']:.1f}kWh, "
                       f"投料={result['feeding_total']:.1f}kg, "
                       f"炉皮水={result['shell_water_total']:.1f}m³, "
                       f"炉盖水={result['cover_water_total']:.1f}m³, "
                       f"时长={result['duration_hours']:.1f}h")
            
            return result
            
        except Exception as e:
            logger.error(f"查询批次统计数据失败: {e}", exc_info=True)
            return {
                'batch_code': batch_code,
                'energy_total': 0.0,
                'feeding_total': 0.0,
                'shell_water_total': 0.0,
                'cover_water_total': 0.0,
                'duration_hours': 0.0,
                'start_time': None,
                'end_time': None
            }
    
    # 16. 删除指定批次的所有数据
    def delete_batch_data(self, batch_code: str) -> dict:
        """
        删除指定批次的所有数据
        
        Args:
            batch_code: 批次号
            
        Returns:
            {"success": bool, "message": str, "deleted_count": int}
        """
        try:
            delete_api = self.client.delete_api()
            
            # 删除时间范围：过去90天到现在
            start = "1970-01-01T00:00:00Z"
            stop = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
            
            # 删除条件：batch_code 匹配
            predicate = f'batch_code="{batch_code}"'
            
            # 执行删除
            delete_api.delete(
                start=start,
                stop=stop,
                predicate=predicate,
                bucket=settings.influx_bucket,
                org=settings.influx_org
            )
            
            logger.info(f"已删除批次 {batch_code} 的所有数据")
            
            return {
                "success": True,
                "message": f"批次 {batch_code} 的所有数据已删除",
                "batch_code": batch_code
            }
            
        except Exception as e:
            logger.error(f"删除批次数据失败: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"删除失败: {str(e)}",
                "batch_code": batch_code
            }
    
    # 17. 查询报警记录（按报警类型过滤）
    def query_alarm_records(
        self,
        alarm_type: Optional[str] = None,
        param_name: Optional[str] = None,
        level: Optional[str] = None,
        batch_code: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        查询报警记录 (从 alarm_logs measurement)
        
        Args:
            alarm_type: 报警类型过滤 (arc_current/arc_voltage/electrode_depth/cooling_water/filter)
            param_name: 参数名过滤 (如 arc_current_u, cooling_pressure_shell 等)
            level: 报警级别 (warning/alarm)
            batch_code: 批次号过滤
            start_time: 开始时间 (北京时间，可选，默认24小时前)
            end_time: 结束时间 (北京时间，可选，默认当前)
            limit: 最大返回数量
            
        Returns:
            报警记录列表 [{
                'timestamp': str (北京时间),
                'device_id': str,
                'alarm_type': str,
                'level': str,
                'param_name': str,
                'value': float,
                'threshold': float,
                'message': str,
                'phase': str
            }, ...]
        """
        try:
            # 时间处理
            if start_time is None:
                start_time = datetime.now() - timedelta(hours=24)
            if end_time is None:
                end_time = datetime.now()
            
            start_utc = self._beijing_to_utc(start_time)
            end_utc = self._beijing_to_utc(end_time)
            
            start_iso = start_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
            end_iso = end_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
            
            # 构建过滤条件
            filters = ['r["_measurement"] == "alarm_logs"']
            
            if alarm_type:
                filters.append(f'r["alarm_type"] == "{alarm_type}"')
            if level:
                filters.append(f'r["level"] == "{level}"')
            if batch_code:
                filters.append(f'r["batch_code"] == "{batch_code}"')
            
            filter_clause = " and ".join(filters)
            
            query = f'''
            from(bucket: "{settings.influx_bucket}")
              |> range(start: {start_iso}, stop: {end_iso})
              |> filter(fn: (r) => {filter_clause})
              |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
              |> sort(columns: ["_time"], desc: true)
              |> limit(n: {limit})
            '''
            
            result = self.query_api.query(query)
            
            records = []
            for table in result:
                for record in table.records:
                    record_param_name = record.values.get("param_name", "")
                    
                    # 参数名过滤 (模糊匹配)
                    if param_name and param_name not in record_param_name:
                        continue
                    
                    # 提取相位信息
                    phase = self._extract_phase_from_param(record_param_name)
                    
                    utc_time = record.get_time()
                    beijing_time = self._utc_to_beijing(utc_time)
                    
                    records.append({
                        'timestamp': beijing_time,
                        'device_id': record.values.get("device_id", ""),
                        'alarm_type': record.values.get("alarm_type", ""),
                        'level': record.values.get("level", ""),
                        'param_name': record_param_name,
                        'value': record.values.get("value", 0),
                        'threshold': record.values.get("threshold", 0),
                        'message': record.values.get("message", ""),
                        'phase': phase
                    })
            
            logger.info(f"查询到 {len(records)} 条报警记录 (type={alarm_type}, param={param_name})")
            return records
            
        except Exception as e:
            logger.error(f"查询报警记录失败: {e}", exc_info=True)
            return []
    
    # 18. 查询报警统计（按类型分组统计数量）
    def query_alarm_statistics(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, int]:
        """
        查询报警统计数据
        
        Args:
            start_time: 开始时间 (北京时间)
            end_time: 结束时间 (北京时间)
            
        Returns:
            {'arc_current': 5, 'arc_voltage': 2, 'electrode_depth': 1, ...}
        """
        try:
            if start_time is None:
                start_time = datetime.now() - timedelta(hours=24)
            if end_time is None:
                end_time = datetime.now()
            
            start_utc = self._beijing_to_utc(start_time)
            end_utc = self._beijing_to_utc(end_time)
            
            start_iso = start_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
            end_iso = end_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
            
            query = f'''
            from(bucket: "{settings.influx_bucket}")
              |> range(start: {start_iso}, stop: {end_iso})
              |> filter(fn: (r) => r["_measurement"] == "alarm_logs")
              |> filter(fn: (r) => r["_field"] == "value")
              |> group(columns: ["alarm_type"])
              |> count()
            '''
            
            result = self.query_api.query(query)
            
            stats = {}
            for table in result:
                for record in table.records:
                    alarm_type = record.values.get("alarm_type", "unknown")
                    count = record.get_value()
                    stats[alarm_type] = count
            
            return stats
            
        except Exception as e:
            logger.error(f"查询报警统计失败: {e}")
            return {}
    
    # 19. 从参数名中提取相位
    @staticmethod
    def _extract_phase_from_param(param_name: str) -> str:
        """从参数名中提取相位信息"""
        param_lower = param_name.lower()
        if param_lower.endswith("_u") or param_lower.endswith("_1"):
            return "1#"
        elif param_lower.endswith("_v") or param_lower.endswith("_2"):
            return "2#"
        elif param_lower.endswith("_w") or param_lower.endswith("_3"):
            return "3#"
        else:
            return "-"


# 20. 获取历史查询服务单例
def get_history_query_service() -> HistoryQueryService:
    return HistoryQueryService.get_instance()

