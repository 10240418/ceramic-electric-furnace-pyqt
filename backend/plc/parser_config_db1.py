# ============================================================
# 文件说明: parser_config_db1.py - DB1 Vw_Data 配置驱动数据解析器
# ============================================================
# 功能:
#   1. 根据 config_vw_data_db1.yaml 解析 DB1 数据
#   2. 支持 Int 和 Real 类型字段解析
#   3. 按数据分组返回结果 (电机输出、弧流、弧压、变频电流)
#   4. 自动计算归一化值与比例放大值的组合
# ============================================================

import struct
import yaml
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
from backend.config import get_settings


class ConfigDrivenDB1Parser:
    """配置驱动的 DB1 Vw_Data 数据解析器
    
    根据 config_vw_data_db1.yaml 中的字段定义，
    自动解析 PLC DB1 数据块中的变频器/弧流弧压数据。
    """
    
    # 项目根目录
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    
    def __init__(self, config_path: str = None):
        """初始化解析器
        
        Args:
            config_path: DB1 配置文件路径 (默认 config_vw_data_db1.yaml)
        """
        self.config_path = Path(config_path) if config_path else \
            self.PROJECT_ROOT / "backend" / "configs" / "config_vw_data_db1.yaml"
        
        # 配置数据
        self.config: Dict[str, Any] = {}
        self.db_config: Dict[str, Any] = {}
        self.fields: List[Dict] = []
        self.data_groups: Dict[str, Any] = {}
        
        # 上一次的紧急停电数据（用于变化检测）
        self.last_emergency_data: Optional[Dict[str, Any]] = None
        
        self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # 提取 DB1 配置
        db1 = self.config.get('db1_vw_data', {})
        self.db_config = {
            'db_number': db1.get('db_block', 1),
            'db_name': db1.get('name', 'Vw_Data'),
            'total_size': db1.get('total_size', 182)
        }
        
        # 加载字段定义
        self.fields = db1.get('fields', [])
        
        # 加载数据分组
        self.data_groups = self.config.get('data_groups', {})
        
        print(f" DB1 解析器初始化: DB{self.db_config['db_number']} ({self.db_config['db_name']}), "
              f"{len(self.fields)} 个字段, 总大小 {self.db_config['total_size']} bytes")
    
    def _parse_field(self, data: bytes, field_def: Dict) -> Any:
        """解析单个字段
        
        Args:
            data: 完整的 DB 块数据
            field_def: 字段定义
        
        Returns:
            解析后的值
        """
        offset = field_def.get('offset', 0)
        field_type = field_def.get('type', 'INT').upper()
        
        try:
            if field_type == 'INT':
                # 有符号 16 位整数 (2 bytes, 大端序)
                if offset + 2 > len(data):
                    return 0
                return struct.unpack('>h', data[offset:offset + 2])[0]
            
            elif field_type == 'REAL':
                # 32 位浮点数 (4 bytes, 大端序)
                if offset + 4 > len(data):
                    return 0.0
                return round(struct.unpack('>f', data[offset:offset + 4])[0], 4)
            
            elif field_type == 'WORD':
                # 无符号 16 位整数 (2 bytes, 大端序)
                if offset + 2 > len(data):
                    return 0
                return struct.unpack('>H', data[offset:offset + 2])[0]
            
            elif field_type == 'DWORD' or field_type == 'UDINT':
                # 无符号 32 位整数 (4 bytes, 大端序)
                if offset + 4 > len(data):
                    return 0
                return struct.unpack('>I', data[offset:offset + 4])[0]
            
            elif field_type == 'DINT':
                # 有符号 32 位整数 (4 bytes, 大端序)
                if offset + 4 > len(data):
                    return 0
                return struct.unpack('>i', data[offset:offset + 4])[0]
            
            elif field_type == 'BYTE':
                # 无符号 8 位整数 (1 byte)
                if offset + 1 > len(data):
                    return 0
                return data[offset]
            
            elif field_type == 'BOOL':
                # 布尔值 (支持位偏移)
                if offset + 1 > len(data):
                    return False
                bit = field_def.get('bit', 0)  # 获取位偏移，默认为0
                return bool(data[offset] & (1 << bit))
            
            elif field_type == 'TIME':
                # TIME 类型 (32 位有符号整数, 4 bytes, 大端序)
                # 存储单位: 毫秒 (ms)
                # 范围: -2,147,483,648 ms 到 +2,147,483,647 ms
                if offset + 4 > len(data):
                    return 0
                return struct.unpack('>i', data[offset:offset + 4])[0]
            
            else:
                # 未知类型，静默返回0，不打印警告
                return 0
                
        except Exception as e:
            print(f" 解析字段 {field_def.get('name')} (offset {offset}) 失败: {e}")
            return 0
    
    def parse(self, data: bytes) -> Dict[str, Any]:
        """解析 DB1 原始数据
        
        Args:
            data: PLC DB1 原始字节数据 (190 bytes)
            
        Returns:
            解析后的数据字典
        """
        if len(data) < self.db_config['total_size']:
            return {
                'error': f"数据长度不足: 需要 {self.db_config['total_size']} bytes, "
                        f"实际 {len(data)} bytes",
                'timestamp': datetime.now().isoformat()
            }
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'db_number': self.db_config['db_number'],
            'db_name': self.db_config['db_name'],
            'data_size': len(data),
            'all_fields': {},  # 所有字段的原始值
            # 按分组
            'motor_outputs': {},
            'arc_current': {},
            'arc_voltage': {},
            'vfd_current': {},
            'vw_variables': {},  # Vw 系列变量
            # 新增：死区上下限（独立字段）
            'arc_current_deadzone_upper': 0,
            'arc_current_deadzone_lower': 0,
            # 新增：高压紧急停电数据
            'emergency_stop': {},
        }
        
        try:
            # 解析所有字段
            for field_def in self.fields:
                name = field_def.get('name', '')
                value = self._parse_field(data, field_def)
                result['all_fields'][name] = {
                    'value': value,
                    'type': field_def.get('type', 'INT'),
                    'offset': field_def.get('offset', 0),
                    'unit': field_def.get('unit', ''),
                    'description': field_def.get('description', '')
                }
                
                # 按类型分组（优先判断设定值和死区）
                if name in ['arc_current_setpoint_U', 'arc_current_setpoint_V', 'arc_current_setpoint_W', 'manual_deadzone_percent']:
                    # 设定值和死区百分比放入 vw_variables
                    result['vw_variables'][name] = value
                elif name.startswith('emergency_stop'):
                    # 高压紧急停电数据
                    result['emergency_stop'][name] = value
                elif name.startswith('motor_output'):
                    result['motor_outputs'][name] = value
                elif name.startswith('arc_current'):
                    result['arc_current'][name] = value
                    # 特殊处理：死区上下限作为独立字段
                    if name == 'arc_current_deadzone_upper':
                        result['arc_current_deadzone_upper'] = value
                    elif name == 'arc_current_deadzone_lower':
                        result['arc_current_deadzone_lower'] = value
                elif name.startswith('arc_voltage'):
                    result['arc_voltage'][name] = value
                elif name.startswith('vfd_current'):
                    result['vfd_current'][name] = value
                elif name.startswith('Vw'):
                    result['vw_variables'][name] = value
            
            # 计算弧流弧压的组合值 (归一化 × 比例放大)
            result['arc_combined'] = self._calculate_arc_combined(result)
            
            # 计算变频电流的组合值
            result['vfd_combined'] = self._calculate_vfd_combined(result)
            
            # 检查紧急停电数据是否变化
            result['emergency_stop_changed'] = self._check_emergency_data_changed(result['emergency_stop'])
            
        except Exception as e:
            result['error'] = str(e)
            print(f" 解析 DB1 数据失败: {e}")
        
        return result
    
    def _calculate_arc_combined(self, parsed: Dict) -> Dict[str, float]:
        """计算弧流弧压的实际值
        
        计算公式:
        - 弧压 (V)  = 模拟量输入 × 10 / 27648 × 50
        - 弧流 (kA) = 模拟量输入 × 10 / 27648 × 1
        
        Args:
            parsed: 已解析的数据
            
        Returns:
            计算后的弧流弧压值
        """
        arc_current = parsed.get('arc_current', {})
        arc_voltage = parsed.get('arc_voltage', {})
        
        combined = {}
        
        # 常量
        SCALE_FACTOR = 10.0 / 27648.0
        VOLTAGE_MULTIPLIER = 50.0  # 弧压系数
        CURRENT_MULTIPLIER = 1.0   # 弧流系数 (kA)
        
        # A相弧流 (kA)
        if 'arc_current_A_normalized' in arc_current:
            raw_value = arc_current['arc_current_A_normalized']
            combined['arc_current_A'] = round(raw_value * SCALE_FACTOR * CURRENT_MULTIPLIER, 4)
        
        # A相弧压 (V)
        if 'arc_voltage_A_normalized' in arc_voltage:
            raw_value = arc_voltage['arc_voltage_A_normalized']
            combined['arc_voltage_A'] = round(raw_value * SCALE_FACTOR * VOLTAGE_MULTIPLIER, 2)
        
        # B相弧流 (kA)
        if 'arc_current_B_normalized' in arc_current:
            raw_value = arc_current['arc_current_B_normalized']
            combined['arc_current_B'] = round(raw_value * SCALE_FACTOR * CURRENT_MULTIPLIER, 4)
        
        # B相弧压 (V)
        if 'arc_voltage_B_normalized' in arc_voltage:
            raw_value = arc_voltage['arc_voltage_B_normalized']
            combined['arc_voltage_B'] = round(raw_value * SCALE_FACTOR * VOLTAGE_MULTIPLIER, 2)
        
        # C相弧流 (kA)
        if 'arc_current_C_normalized' in arc_current:
            raw_value = arc_current['arc_current_C_normalized']
            combined['arc_current_C'] = round(raw_value * SCALE_FACTOR * CURRENT_MULTIPLIER, 4)
        
        # C相弧压 (V)
        if 'arc_voltage_C_normalized' in arc_voltage:
            raw_value = arc_voltage['arc_voltage_C_normalized']
            combined['arc_voltage_C'] = round(raw_value * SCALE_FACTOR * VOLTAGE_MULTIPLIER, 2)
        
        # 备用相弧流 (kA)
        if 'arc_current_spare_normalized' in arc_current:
            raw_value = arc_current['arc_current_spare_normalized']
            combined['arc_current_spare'] = round(raw_value * SCALE_FACTOR * CURRENT_MULTIPLIER, 4)
        
        # 备用相弧压 (V)
        if 'arc_voltage_spare_normalized' in arc_voltage:
            raw_value = arc_voltage['arc_voltage_spare_normalized']
            combined['arc_voltage_spare'] = round(raw_value * SCALE_FACTOR * VOLTAGE_MULTIPLIER, 2)
        
        # 弧流给定 (kA)
        if 'arc_current_setpoint_normalized' in arc_current:
            raw_value = arc_current['arc_current_setpoint_normalized']
            combined['arc_current_setpoint'] = round(raw_value * SCALE_FACTOR * CURRENT_MULTIPLIER, 4)
        
        return combined
    
    def _calculate_vfd_combined(self, parsed: Dict) -> Dict[str, float]:
        """计算变频电流的组合值 (归一化 × 比例放大)
        
        Args:
            parsed: 已解析的数据
            
        Returns:
            组合计算后的变频电流值
        """
        vfd = parsed.get('vfd_current', {})
        
        combined = {}
        
        # U相
        if 'vfd_current_U_normalized' in vfd and 'vfd_current_U_scale' in vfd:
            combined['vfd_current_U'] = round(
                vfd['vfd_current_U_normalized'] * vfd['vfd_current_U_scale'], 2
            )
        
        # V相
        if 'vfd_current_V_normalized' in vfd and 'vfd_current_V_scale' in vfd:
            combined['vfd_current_V'] = round(
                vfd['vfd_current_V_normalized'] * vfd['vfd_current_V_scale'], 2
            )
        
        # W相
        if 'vfd_current_W_normalized' in vfd and 'vfd_current_W_scale' in vfd:
            combined['vfd_current_W'] = round(
                vfd['vfd_current_W_normalized'] * vfd['vfd_current_W_scale'], 2
            )
        
        return combined
    
    def _check_emergency_data_changed(self, current_data: Dict[str, Any]) -> bool:
        """检查紧急停电数据是否变化
        
        Args:
            current_data: 当前的紧急停电数据
            
        Returns:
            True 如果数据有变化，False 如果没有变化
        """
        if self.last_emergency_data is None:
            # 第一次读取，记录数据
            self.last_emergency_data = current_data.copy()
            return True
        
        # 比较数据是否变化
        changed = False
        for key, value in current_data.items():
            if key not in self.last_emergency_data or self.last_emergency_data[key] != value:
                changed = True
                break
        
        if changed:
            # 数据有变化，更新记录
            self.last_emergency_data = current_data.copy()
        
        return changed
    
    def parse_all(self, data: bytes) -> Dict[str, Any]:
        """parse 方法的别名，保持与其他解析器一致的接口"""
        return self.parse(data)
    
    def get_db_number(self) -> int:
        """获取 DB 块号"""
        return self.db_config['db_number']
    
    def get_total_size(self) -> int:
        """获取 DB 块总大小"""
        return self.db_config['total_size']
    
    def get_field_list(self) -> List[Dict]:
        """获取字段列表"""
        return [
            {
                'name': f.get('name', ''),
                'offset': f.get('offset', 0),
                'type': f.get('type', 'INT'),
                'description': f.get('description', '')
            }
            for f in self.fields
        ]
    
    def parse_to_influx_point(self, data: bytes, device_id: str = None) -> Dict[str, Any]:
        """解析并转换为 InfluxDB Point 格式
        
        Args:
            data: 原始字节数据
            device_id: 设备ID
            
        Returns:
            InfluxDB Point 格式的字典
        """
        if device_id is None:
            device_id = get_settings().device_id
        parsed = self.parse(data)
        
        if 'error' in parsed:
            return {'error': parsed['error']}
        
        # 提取关键数据作为 fields
        fields = {}
        
        # 电机输出
        for name, value in parsed.get('motor_outputs', {}).items():
            fields[name] = float(value) if isinstance(value, (int, float)) else 0.0
        
        # 弧流弧压组合值
        for name, value in parsed.get('arc_combined', {}).items():
            fields[name] = float(value) if isinstance(value, (int, float)) else 0.0
        
        # 变频电流组合值
        for name, value in parsed.get('vfd_combined', {}).items():
            fields[name] = float(value) if isinstance(value, (int, float)) else 0.0
        
        return {
            'measurement': 'vw_data',
            'tags': {
                'device_id': device_id,
                'device_type': 'electric_furnace',
                'db_number': str(self.db_config['db_number'])
            },
            'fields': fields,
            'time': parsed['timestamp']
        }


# ==================== 单例模式 ====================

_parser_instance: Optional[ConfigDrivenDB1Parser] = None


def get_db1_parser() -> ConfigDrivenDB1Parser:
    """获取 DB1 解析器单例"""
    global _parser_instance
    if _parser_instance is None:
        _parser_instance = ConfigDrivenDB1Parser()
    return _parser_instance


def reset_db1_parser():
    """重置 DB1 解析器（用于配置更新后）"""
    global _parser_instance
    _parser_instance = None


# ==================== 便捷函数 ====================

def parse_db1_vw_data(data: bytes) -> Dict[str, Any]:
    """解析 DB1 Vw_Data 数据 (便捷函数)"""
    parser = get_db1_parser()
    return parser.parse(data)


def parse_db1_to_influx(data: bytes, device_id: str = None) -> Dict[str, Any]:
    """解析并转换为 InfluxDB 格式 (便捷函数)"""
    parser = get_db1_parser()
    return parser.parse_to_influx_point(data, device_id)


# ==================== 测试代码 ====================

if __name__ == "__main__":
    import random
    
    print("=" * 60)
    print("DB1 Vw_Data 解析器测试")
    print("=" * 60)
    
    # 创建解析器
    parser = ConfigDrivenDB1Parser()
    
    print(f"\n📋 配置信息:")
    print(f"   DB块: DB{parser.db_config['db_number']}")
    print(f"   名称: {parser.db_config['db_name']}")
    print(f"   大小: {parser.db_config['total_size']} bytes")
    print(f"   字段数: {len(parser.fields)}")
    
    # 生成模拟数据 (190 bytes)
    mock_data = bytearray(190)
    
    # 高压紧急停电数据 (offset 182-189)
    struct.pack_into('>h', mock_data, 182, 8000)  # 弧流上限 8000A
    mock_data[184] = 0x02  # bit 0=0 (未触发), bit 1=1 (已启用)
    struct.pack_into('>i', mock_data, 186, 200)  # 消抖时间 200ms
    
    # 电机输出 (Int, offset 0-7)
    struct.pack_into('>h', mock_data, 0, 1000)   # 第一路电机
    struct.pack_into('>h', mock_data, 2, 500)    # 备用电机
    struct.pack_into('>h', mock_data, 4, 1200)   # 第二路电机
    struct.pack_into('>h', mock_data, 6, 800)    # 第三路电机
    
    # A相弧流 (归一 + 比例)
    struct.pack_into('>f', mock_data, 94, 0.85)   # A相弧流归一
    struct.pack_into('>h', mock_data, 98, 1000)   # A相弧流比例放大
    
    # A相弧压
    struct.pack_into('>f', mock_data, 100, 0.72)  # A相弧压归一
    struct.pack_into('>h', mock_data, 104, 100)   # A相弧压比例放大
    
    # B相弧流弧压
    struct.pack_into('>f', mock_data, 106, 0.80)  # B相弧流归一
    struct.pack_into('>h', mock_data, 110, 1000)  # B相弧流比例放大
    struct.pack_into('>f', mock_data, 112, 0.70)  # B相弧压归一
    struct.pack_into('>h', mock_data, 116, 100)   # B相弧压比例放大
    
    # C相弧流弧压
    struct.pack_into('>f', mock_data, 118, 0.82)  # C相弧流归一
    struct.pack_into('>h', mock_data, 122, 1000)  # C相弧流比例放大
    struct.pack_into('>f', mock_data, 124, 0.75)  # C相弧压归一
    struct.pack_into('>h', mock_data, 128, 100)   # C相弧压比例放大
    
    # 变频电机电流 U/V/W
    struct.pack_into('>f', mock_data, 148, 0.5)   # U相归一
    struct.pack_into('>h', mock_data, 152, 200)   # U相比例
    struct.pack_into('>f', mock_data, 154, 0.48)  # V相归一
    struct.pack_into('>h', mock_data, 158, 200)   # V相比例
    struct.pack_into('>f', mock_data, 160, 0.52)  # W相归一
    struct.pack_into('>h', mock_data, 164, 200)   # W相比例
    
    # 电机输出归一
    struct.pack_into('>f', mock_data, 166, 0.95)  # 第一路
    struct.pack_into('>f', mock_data, 170, 0.88)  # 第二路
    struct.pack_into('>f', mock_data, 174, 0.75)  # 第三路
    struct.pack_into('>f', mock_data, 178, 0.50)  # 备用
    
    print(f"\n📊 模拟数据: {len(mock_data)} bytes")
    
    # 解析数据
    result = parser.parse(bytes(mock_data))
    
    print(f"\n【电机输出】")
    for name, value in result['motor_outputs'].items():
        print(f"   {name}: {value}")
    
    print(f"\n【弧流数据 (原始)】")
    for name, value in result['arc_current'].items():
        print(f"   {name}: {value}")
    
    print(f"\n【弧压数据 (原始)】")
    for name, value in result['arc_voltage'].items():
        print(f"   {name}: {value}")
    
    print(f"\n【弧流弧压组合值 (归一×比例)】")
    for name, value in result['arc_combined'].items():
        print(f"   {name}: {value}")
    
    print(f"\n【变频电流组合值 (归一×比例)】")
    for name, value in result['vfd_combined'].items():
        print(f"   {name}: {value}")
    
    # 测试 InfluxDB 格式
    print(f"\n【InfluxDB Point 格式】")
    influx_point = parser.parse_to_influx_point(bytes(mock_data), "furnace_1")
    print(f"   measurement: {influx_point['measurement']}")
    print(f"   tags: {influx_point['tags']}")
    print(f"   fields 数量: {len(influx_point['fields'])}")
    
    print("\n" + "=" * 60)
    print(" DB1 Vw_Data 解析器测试完成")
    print("=" * 60)
