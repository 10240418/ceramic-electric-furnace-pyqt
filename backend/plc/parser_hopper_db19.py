# ============================================================
# 文件说明: parser_hopper_db19.py - DB19 料仓控制标志解析器
# ============================================================
# 功能:
#   1. 解析 DB19 料仓控制数据块
#   2. 提取本次排料重量待读取标志 (offset 2.3)
# ============================================================

import struct
import yaml
from typing import Dict, Any, Optional
from pathlib import Path


class HopperDB19Parser:
    """DB19 料仓控制标志解析器"""
    
    # 项目根目录
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    
    # 1. 初始化解析器
    def __init__(self, config_path: str = None):
        """
        初始化解析器
        
        Args:
            config_path: DB19 配置文件路径 (默认 hopper_elec_db19.yaml)
        """
        self.config_path = Path(config_path) if config_path else \
            self.PROJECT_ROOT / "backend" / "configs" / "hopper_elec_db19.yaml"
        
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
        
        # 提取 DB19 配置
        db19 = self.config.get('db19_hopper_control', {})
        self.db_config = {
            'db_number': db19.get('db_block', 19),
            'db_name': db19.get('name', 'HOPPER_CONTROL'),
            'total_size': db19.get('total_size', 4)
        }
        self.fields = db19.get('fields', [])
        
        print(f"DB19 配置解析器初始化: DB{self.db_config['db_number']}, "
              f"{len(self.fields)}个字段, 总大小{self.db_config['total_size']}字节")
    
    # 3. 解析 Bool 类型数据
    def _parse_bool(self, data: bytes, offset: int, bit: int) -> bool:
        """
        解析 Bool (位)
        
        Args:
            data: 原始字节数据
            offset: 字节偏移量
            bit: 位偏移量 (0-7)
            
        Returns:
            布尔值
        """
        if offset >= len(data):
            return False
        
        byte_value = data[offset]
        return bool((byte_value >> bit) & 0x01)
    
    # 4. 解析 DB19 数据
    def parse(self, data: bytes) -> Dict[str, Any]:
        """
        解析 DB19 原始数据
        
        Args:
            data: PLC 读取的原始字节数据
            
        Returns:
            解析后的数据字典
        """
        if not data or len(data) < self.db_config['total_size']:
            print(f"DB19 数据长度不足: {len(data) if data else 0} < {self.db_config['total_size']}")
            return {}
        
        result = {}
        
        for field in self.fields:
            field_name = field['name']
            offset = field['offset']
            field_type = field['type']
            
            # 解析 Bool 类型
            if field_type == 'BOOL':
                bit = field.get('bit', 0)
                value = self._parse_bool(data, offset, bit)
                result[field_name] = value
        
        return result
    
    # 5. 获取排料重量待读取标志
    def get_discharge_weight_ready(self, data: bytes) -> bool:
        """
        获取本次排料重量待读取标志
        
        Args:
            data: PLC 读取的原始字节数据
            
        Returns:
            True=有新的排料重量可读取, False=无
        """
        parsed = self.parse(data)
        return parsed.get('discharge_weight_ready', False)
    
    # 6. 获取 DB 编号
    def get_db_number(self) -> int:
        """获取 DB 编号"""
        return self.db_config['db_number']
    
    # 7. 获取总大小
    def get_total_size(self) -> int:
        """获取 DB 总大小"""
        return self.db_config['total_size']

