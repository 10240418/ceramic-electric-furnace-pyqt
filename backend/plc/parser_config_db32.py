# ============================================================
# 文件说明: parser_config_db32.py - DB32 配置驱动数据解析器
# ============================================================
# 功能:
#   1. 根据 YAML 配置文件自动解析 DB32 原始数据
#   2. 支持引用 plc_modules.yaml 中的基础模块定义
#   3. 自动处理不同数据类型 (UDINT, INT, BYTE, BOOL 等)
#   4. 支持位域解析 (offset: 0.0 表示 byte 0 bit 0)
#   5. 红外测距数据解析 (UDInt 类型)
#   6. 蝶阀状态监测 (Byte 类型，每bit对应一个蝶阀开关状态)
# ============================================================

import struct
import yaml
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from datetime import datetime

# 导入转换器
from backend.tools.converter_length import get_length_converter


class ConfigDrivenDB32Parser:
    """配置驱动的 DB32 数据解析器
    
    根据 config_L3_P2_F2_C4_db32.yaml 中的模块定义，
    自动解析 PLC DB32 数据块中的传感器数据。
    """
    
    # 项目根目录
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    
    def __init__(self, 
                 config_path: str = None,
                 modules_path: str = None):
        """初始化解析器
        
        Args:
            config_path: DB32 配置文件路径 (默认 config_L3_P2_F2_C4_db32.yaml)
            modules_path: 基础模块定义文件路径 (默认 plc_modules.yaml)
        """
        self.config_path = Path(config_path) if config_path else \
            self.PROJECT_ROOT / "backend" / "configs" / "config_L3_P2_F2_C4_db32.yaml"
        self.modules_path = Path(modules_path) if modules_path else \
            self.PROJECT_ROOT / "backend" / "configs" / "plc_modules.yaml"
        
        # 配置数据
        self.config: Dict[str, Any] = {}
        self.base_modules: Dict[str, Dict] = {}
        self.db_config: Dict[str, Any] = {}
        self.module_list: List[Dict] = []
        
        self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        # 1. 加载基础模块定义
        with open(self.modules_path, 'r', encoding='utf-8') as f:
            modules_config = yaml.safe_load(f)
            self.base_modules = modules_config.get('modules', {})
            # 如果是列表格式，转为字典
            if isinstance(self.base_modules, list):
                self.base_modules = {m['name']: m for m in self.base_modules}
        
        # 2. 加载 DB32 配置
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # 3. 提取 DB32 配置
        db32 = self.config.get('db32_modbus', {})
        self.db_config = {
            'db_number': db32.get('db_block', 32),
            'db_name': db32.get('name', 'MODBUS_DATA_VALUE'),
            'total_size': db32.get('total_size', 29)
        }
        self.module_list = db32.get('modules', [])
        
        print(f" DB32 配置解析器初始化: DB{self.db_config['db_number']}, "
              f"{len(self.module_list)}个模块, 总大小{self.db_config['total_size']}字节")
    
    def _get_module_definition(self, module_ref: str) -> Optional[Dict]:
        """获取基础模块定义
        
        Args:
            module_ref: 模块引用名 (如 InfraredDistance, PressureSensor)
        
        Returns:
            模块定义字典，或 None
        """
        return self.base_modules.get(module_ref)
    
    def _parse_offset(self, offset: Union[int, float]) -> tuple:
        """解析偏移量 (支持位域)
        
        Args:
            offset: 可以是整数 (如 0) 或浮点数 (如 0.3 表示 byte 0 bit 3)
        
        Returns:
            (byte_offset, bit_offset)
        """
        if isinstance(offset, float):
            byte_offset = int(offset)
            bit_offset = int(round((offset - byte_offset) * 10))
            return (byte_offset, bit_offset)
        return (int(offset), 0)
    
    def _parse_field(self, data: bytes, base_offset: int, field: Dict) -> Any:
        """解析单个字段
        
        Args:
            data: 完整的 DB 块数据
            base_offset: 模块的基础偏移量
            field: 字段定义
        
        Returns:
            解析后的值
        """
        field_offset = field.get('offset', 0)
        field_type = field.get('type', 'WORD').upper()
        # 不再使用 scale 参数，直接返回原始值
        
        # 解析偏移量 (支持位域)
        byte_off, bit_off = self._parse_offset(field_offset)
        abs_offset = base_offset + byte_off
        
        try:
            if field_type == 'BOOL':
                # 位域解析
                if abs_offset >= len(data):
                    return False
                byte_val = data[abs_offset]
                return bool(byte_val & (1 << bit_off))
            
            elif field_type == 'BYTE':
                if abs_offset >= len(data):
                    return 0
                return data[abs_offset]
            
            elif field_type == 'WORD':
                if abs_offset + 2 > len(data):
                    return 0
                raw = struct.unpack('>H', data[abs_offset:abs_offset + 2])[0]
                return raw  # 直接返回原始值
            
            elif field_type == 'INT':
                if abs_offset + 2 > len(data):
                    return 0
                raw = struct.unpack('>h', data[abs_offset:abs_offset + 2])[0]
                return raw  # 直接返回原始值
            
            elif field_type == 'DWORD':
                if abs_offset + 4 > len(data):
                    return 0
                raw = struct.unpack('>I', data[abs_offset:abs_offset + 4])[0]
                return raw  # 直接返回原始值
            
            elif field_type == 'UDINT':
                # 无符号双整数 (4字节, 大端序)
                if abs_offset + 4 > len(data):
                    return 0
                raw = struct.unpack('>I', data[abs_offset:abs_offset + 4])[0]
                return raw  # 直接返回原始值
            
            elif field_type == 'DINT':
                if abs_offset + 4 > len(data):
                    return 0
                raw = struct.unpack('>i', data[abs_offset:abs_offset + 4])[0]
                return raw  # 直接返回原始值
            
            elif field_type == 'REAL':
                if abs_offset + 4 > len(data):
                    return 0.0
                raw = struct.unpack('>f', data[abs_offset:abs_offset + 4])[0]
                return raw  # 直接返回原始值
            
            else:
                print(f" 未知数据类型: {field_type}")
                return 0
                
        except Exception as e:
            print(f" 解析字段失败 @ offset {abs_offset}: {e}")
            return 0
    
    def parse_module(self, data: bytes, module_config: Dict) -> Dict[str, Any]:
        """解析单个模块
        
        Args:
            data: 完整的 DB 块数据
            module_config: 模块配置 (来自 config 的 modules 列表)
        
        Returns:
            解析后的模块数据
        """
        name = module_config.get('name', '')
        module_ref = module_config.get('module_ref', '')
        offset = module_config.get('offset', 0)
        direction = module_config.get('direction', 'READ')
        description = module_config.get('description', '')
        
        # 跳过写入模块
        if direction == 'WRITE':
            return {
                'name': name,
                'module_ref': module_ref,
                'direction': 'WRITE',
                'description': description,
                'skipped': True
            }
        
        # 获取基础模块定义
        base_def = self._get_module_definition(module_ref)
        if not base_def:
            return {
                'name': name,
                'module_ref': module_ref,
                'error': f"未找到模块定义: {module_ref}"
            }
        
        # 解析所有字段
        fields = {}
        for field in base_def.get('fields', []):
            field_name = field.get('name', '')
            value = self._parse_field(data, offset, field)
            fields[field_name] = {
                'value': value,
                'type': field.get('type', 'WORD'),
                'unit': field.get('unit', base_def.get('unit', '')),
                'description': field.get('description', '')
            }
        
        return {
            'name': name,
            'module_ref': module_ref,
            'offset': offset,
            'description': description,
            'unit': base_def.get('unit', ''),
            'fields': fields
        }
    
    def parse_all(self, db32_data: bytes) -> Dict[str, Any]:
        """解析 DB32 所有模块数据
        
        Args:
            db32_data: DB32 完整字节数据
        
        Returns:
            解析后的完整数据结构
        """
        timestamp = datetime.now().isoformat()
        
        result = {
            'timestamp': timestamp,
            'db_block': self.db_config['db_number'],
            'db_name': self.db_config['db_name'],
            'data_size': len(db32_data),
            'modules': {},
            # 按类型分组 (方便前端使用)
            'electrode_depths': {},
            'cooling_pressures': {},
            'cooling_flows': {},
            'valve_status': {}  # 蝶阀状态监测
        }
        
        for module_config in self.module_list:
            name = module_config.get('name', '')
            module_ref = module_config.get('module_ref', '')
            
            parsed = self.parse_module(db32_data, module_config)
            result['modules'][name] = parsed
            
            # 按类型分组
            if module_ref == 'InfraredDistance':
                # UDInt 类型红外测距，直接读取 distance 字段
                fields = parsed.get('fields', {})
                distance_raw = int(fields.get('distance', {}).get('value', 0))
                
                # 有效性校验: 距离值应该在合理范围内 (0-10000mm)
                valid = 0 <= distance_raw <= 10000
                
                result['electrode_depths'][name] = {
                    'distance': distance_raw if valid else None,  # 距离值 (mm)
                    'distance_mm': distance_raw if valid else None,
                    'distance_m': distance_raw / 1000.0 if valid and distance_raw else None,
                    'distance_cm': distance_raw / 10.0 if valid and distance_raw else None,
                    'raw': distance_raw,
                    'unit': 'mm',
                    'valid': valid,
                    'error': None if valid else f'距离值超出范围: {distance_raw}',
                    'description': parsed.get('description', '')
                }
            
            elif module_ref == 'PressureSensor':
                fields = parsed.get('fields', {})
                raw = fields.get('pressure', {}).get('value', 0)
                # PLC 原始值直接使用，不乘以任何系数
                pressure_kpa = int(raw)  # 直接使用原始值
                result['cooling_pressures'][name] = {
                    'pressure': pressure_kpa,  # kPa (原始值)
                    'raw': int(raw),
                    'unit': 'kPa',
                    'description': parsed.get('description', '')
                }
            
            elif module_ref == 'FlowSensor':
                fields = parsed.get('fields', {})
                raw = fields.get('flow', {}).get('value', 0)
                # 原始值 × 0.1 转为 m³/h
                flow = raw * 0.1
                result['cooling_flows'][name] = {
                    'flow': round(flow, 2),
                    'raw': int(raw),
                    'unit': 'm³/h',
                    'description': parsed.get('description', '')
                }
            
            elif module_ref == 'ValveStatusMonitor':
                # 蝶阀状态监测 (Byte类型, 4个阀, 每阀2bit)
                fields = parsed.get('fields', {})
                # 尝试获取 status_byte 字段，如果不存在则尝试直接读取
                if 'status_byte' in fields:
                    status_byte = int(fields.get('status_byte', {}).get('value', 0))
                else:
                    # Fallback: 直接从 offset 读取
                    offset = module_config.get('offset', 20)
                    if offset < len(db32_data):
                        status_byte = db32_data[offset]
                    else:
                        status_byte = 0
                
                # 解析每个蝶阀的状态 (2bit 一组)
                # Valve 1: bit0(关), bit1(开)
                # 状态编码: 00=STOPPED(停止), 01=OPEN(打开), 10=CLOSED(关闭), 11=ERROR(错误)
                valves = {}
                open_count = 0
                
                for i in range(1, 5):  # 蝶阀 1-4
                    base_bit = (i - 1) * 2
                    bit_close = (status_byte >> base_bit) & 0x01       # 偶数位: 关信号
                    bit_open = (status_byte >> (base_bit + 1)) & 0x01  # 奇数位: 开信号
                    
                    # 状态判定 (根据2-bit组合)
                    status_code = f"{bit_open}{bit_close}"  # 高位在前：bit1 bit0
                    
                    if status_code == "01":
                        state = 'OPEN'
                        is_open = True
                        open_count += 1
                    elif status_code == "10":
                        state = 'CLOSED'
                        is_open = False
                    elif status_code == "00":
                        state = 'STOPPED'  # 停止状态
                        is_open = False
                    else:  # "11"
                        state = 'ERROR'  # 错误状态
                        is_open = False
                    
                    valves[f'valve_{i}_state'] = state
                    valves[f'valve_{i}_status_code'] = status_code  # 保存原始编码
                    valves[f'valve_{i}_open'] = is_open
                    # 兼容字段
                    valves[f'valve_{i}'] = is_open

                result['valve_status'] = {
                    'raw_byte': status_byte,  # 原始字节值 (用于队列存储)
                    'status_byte': status_byte,
                    'status_hex': f'16#{status_byte:02X}',
                    **valves,
                    'open_count': open_count,
                    'description': parsed.get('description', '蝶阀状态监测 (2bit每阀: 01=开, 10=关)')
                }
        
        return result
    
    def get_db_number(self) -> int:
        """获取 DB 块号"""
        return self.db_config['db_number']
    
    def get_total_size(self) -> int:
        """获取 DB 块总大小"""
        return self.db_config['total_size']
    
    def get_module_list(self) -> List[Dict]:
        """获取模块列表"""
        return [
            {
                'name': m.get('name', ''),
                'module_ref': m.get('module_ref', ''),
                'offset': m.get('offset', 0),
                'description': m.get('description', '')
            }
            for m in self.module_list
            if m.get('direction', 'READ') != 'WRITE'
        ]


# ============================================================
# 单例模式
# ============================================================
_parser_instance: Optional[ConfigDrivenDB32Parser] = None


def get_db32_parser() -> ConfigDrivenDB32Parser:
    """获取 DB32 解析器单例"""
    global _parser_instance
    if _parser_instance is None:
        _parser_instance = ConfigDrivenDB32Parser()
    return _parser_instance


# ============================================================
# 测试代码
# ============================================================
if __name__ == "__main__":
    parser = ConfigDrivenDB32Parser()
    
    # 模拟 DB32 数据 (21字节)
    # 根据新的配置结构:
    # - LENTH1 (UDInt, offset 0): 4 bytes
    # - LENTH2 (UDInt, offset 4): 4 bytes
    # - LENTH3 (UDInt, offset 8): 4 bytes
    # - WATER_PRESS_1 (Int, offset 12): 2 bytes
    # - WATER_PRESS_2 (Int, offset 14): 2 bytes
    # - WATER_FLOW_1 (Int, offset 16): 2 bytes
    # - WATER_FLOW_2 (Int, offset 18): 2 bytes
    # - ValveStatus (Byte, offset 20): 1 byte
    test_data = bytes([
        # LENTH1 (offset 0-3): UDInt = 300 (300mm)
        0x00, 0x00, 0x01, 0x2C,
        # LENTH2 (offset 4-7): UDInt = 400 (400mm)
        0x00, 0x00, 0x01, 0x90,
        # LENTH3 (offset 8-11): UDInt = 500 (500mm)
        0x00, 0x00, 0x01, 0xF4,
        # WATER_PRESS_1 (offset 12-13): Int = 50 -> 0.50 MPa
        0x00, 0x32,
        # WATER_PRESS_2 (offset 14-15): Int = 60 -> 0.60 MPa
        0x00, 0x3C,
        # WATER_FLOW_1 (offset 16-17): Int = 1000 -> 10.00 m³/h
        0x03, 0xE8,
        # WATER_FLOW_2 (offset 18-19): Int = 1200 -> 12.00 m³/h
        0x04, 0xB0,
        # ValveStatus (offset 20): Byte = 0b00000101 (蝶阀1和3开启)
        0x05
    ])
    
    result = parser.parse_all(test_data)
    
    print("\n=== DB32 配置驱动解析结果 ===")
    print(f"时间戳: {result['timestamp']}")
    print(f"DB块: {result['db_block']} ({result['db_name']})")
    print(f"数据大小: {result['data_size']} bytes")
    
    print("\n--- 电极深度 (红外测距 UDInt) ---")
    for name, data in result['electrode_depths'].items():
        status = "" if data['valid'] else ""
        print(f"  {status} {name}: {data['distance']} {data['unit']} - {data['description']}")
    
    print("\n--- 冷却水压力 ---")
    for name, data in result['cooling_pressures'].items():
        print(f"  {name}: {data['pressure']} {data['unit']} - {data['description']}")
    
    print("\n--- 冷却水流量 ---")
    for name, data in result['cooling_flows'].items():
        print(f"  {name}: {data['flow']} {data['unit']} - {data['description']}")
    
    print("\n--- 蝶阀状态监测 ---")
    vs = result.get('valve_status', {})
    print(f"  状态字节: {vs.get('status_byte', 0)} ({vs.get('status_hex', '16#00')})")
    print(f"  开启数量: {vs.get('open_count', 0)}/8")
    for i in range(1, 9):
        status = "开启" if vs.get(f'valve_{i}', False) else "关闭"
        print(f"    蝶阀{i}: {status}")
