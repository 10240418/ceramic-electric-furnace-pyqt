# ============================================================
# 文件说明: parser_hopper_db18.py - DB18 料仓电气数据解析器
# ============================================================
# 功能:
#   1. 解析 DB18 WEIGHT_VAR 数据块
#   2. 提取料仓上限值 (offset 40, DInt)
#   3. 提取当前料仓重量、排料重量等数据
# ============================================================

import struct
import yaml
from typing import Dict, Any, Optional
from pathlib import Path


class HopperDB18Parser:
    """DB18 料仓电气数据解析器"""
    
    # 项目根目录
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    
    # 1. 初始化解析器
    def __init__(self, config_path: str = None):
        """
        初始化解析器
        
        Args:
            config_path: DB18 配置文件路径 (默认 hopper_elec_db18.yaml)
        """
        self.config_path = Path(config_path) if config_path else \
            self.PROJECT_ROOT / "backend" / "configs" / "hopper_elec_db18.yaml"
        
        # 配置数据
        self.config: Dict[str, Any] = {}
        self.db_config: Dict[str, Any] = {}
        self.fields: list = []
        
        self._load_config()
    
    # 2. 加载配置文件
    def _load_config(self):
        """加载配置文件"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # 提取 DB18 配置
        db18 = self.config.get('db18_weight_var', {})
        self.db_config = {
            'db_number': db18.get('db_block', 18),
            'db_name': db18.get('name', 'WEIGHT_VAR'),
            'total_size': db18.get('total_size', 48)
        }
        self.fields = db18.get('fields', [])
        
        print(f"DB18 配置解析器初始化: DB{self.db_config['db_number']}, "
              f"{len(self.fields)}个字段, 总大小{self.db_config['total_size']}字节")
    
    # 3. 解析 DInt 类型数据
    def _parse_dint(self, data: bytes, offset: int) -> int:
        """
        解析 DInt (有符号32位整数)
        
        Args:
            data: 原始字节数据
            offset: 偏移量
            
        Returns:
            整数值
        """
        if offset + 4 > len(data):
            return 0
        
        # 大端序 (Big-Endian)
        value = struct.unpack('>i', data[offset:offset+4])[0]
        return value
    
    # 4. 解析 DB18 数据
    def parse(self, data: bytes) -> Dict[str, Any]:
        """
        解析 DB18 原始数据
        
        Args:
            data: PLC 读取的原始字节数据
            
        Returns:
            解析后的数据字典
        """
        if not data or len(data) < self.db_config['total_size']:
            print(f"DB18 数据长度不足: {len(data) if data else 0} < {self.db_config['total_size']}")
            return {}
        
        result = {}
        
        for field in self.fields:
            field_name = field['name']
            offset = field['offset']
            field_type = field['type']
            conversion = field.get('conversion', {})
            factor = conversion.get('factor', 1.0)
            offset_val = conversion.get('offset', 0.0)
            
            # 解析 DInt 类型
            if field_type == 'DINT':
                raw_value = self._parse_dint(data, offset)
                # 应用转换
                converted_value = raw_value * factor + offset_val
                result[field_name] = converted_value
        
        return result
    
    # 5. 获取料仓上限值
    def get_upper_limit(self, data: bytes) -> float:
        """
        获取料仓上限值
        
        Args:
            data: PLC 读取的原始字节数据
            
        Returns:
            料仓上限值 (kg)
        """
        parsed = self.parse(data)
        return parsed.get('upper_limit', 4900.0)
    
    # 6. 获取 DB 编号
    def get_db_number(self) -> int:
        """获取 DB 编号"""
        return self.db_config['db_number']
    
    # 7. 获取总大小
    def get_total_size(self) -> int:
        """获取 DB 总大小"""
        return self.db_config['total_size']

