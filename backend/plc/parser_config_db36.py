# ============================================================
# 文件说明: parser_config_db36.py - DB36 furnace_conf_persist 解析器
# ============================================================
# 功能:
#   1. 根据 config_elec_db36.yaml 解析 DB36 数据
#   2. 解析高压紧急停电配置 (弧流上限、消抖时间、使能)
#   3. 返回扁平字典，供 process_db36_data() 合并到 arc_data
# ============================================================

import struct
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime


class ConfigDrivenDB36Parser:
    """配置驱动的 DB36 furnace_conf_persist 数据解析器

    根据 config_elec_db36.yaml 中的字段定义，
    解析 PLC DB36 中的电炉持久化配置数据。
    """

    PROJECT_ROOT = Path(__file__).parent.parent.parent

    def __init__(self, config_path: str = None):
        """初始化解析器

        Args:
            config_path: DB36 配置文件路径 (默认 config_elec_db36.yaml)
        """
        self.config_path = Path(config_path) if config_path else \
            self.PROJECT_ROOT / "backend" / "configs" / "config_elec_db36.yaml"

        self.config: Dict[str, Any] = {}
        self.db_config: Dict[str, Any] = {}
        self.fields = []

        self._load_config()

    # 1. 加载配置
    def _load_config(self):
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        db36 = self.config.get('db36_furnace_conf', {})
        self.db_config = {
            'db_number': db36.get('db_block', 36),
            'db_name': db36.get('name', 'furnace_conf_persist'),
            'total_size': db36.get('total_size', 8),
        }
        self.fields = db36.get('fields', [])

        print(f" DB36 解析器初始化: DB{self.db_config['db_number']} "
              f"({self.db_config['db_name']}), "
              f"{len(self.fields)} 个字段, "
              f"总大小 {self.db_config['total_size']} bytes")

    # 2. 解析单个字段
    def _parse_field(self, data: bytes, field_def: Dict) -> Any:
        offset = field_def.get('offset', 0)
        field_type = field_def.get('type', 'INT').upper()

        try:
            if field_type == 'INT':
                if offset + 2 > len(data):
                    return 0
                return struct.unpack('>h', data[offset:offset + 2])[0]

            elif field_type == 'TIME':
                if offset + 4 > len(data):
                    return 0
                return struct.unpack('>i', data[offset:offset + 4])[0]

            elif field_type == 'BOOL':
                if offset + 1 > len(data):
                    return False
                bit = field_def.get('bit', 0)
                return bool(data[offset] & (1 << bit))

            else:
                return 0

        except Exception as e:
            print(f" 解析字段 {field_def.get('name')} (offset {offset}) 失败: {e}")
            return 0

    # 3. 解析 DB36 全部数据
    def parse(self, data: bytes) -> Dict[str, Any]:
        """解析 DB36 原始数据

        Args:
            data: PLC DB36 原始字节数据 (8 bytes)

        Returns:
            解析后的数据字典，包含 emergency_stop 子字典
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
            'emergency_stop': {},
        }

        try:
            for field_def in self.fields:
                name = field_def.get('name', '')
                value = self._parse_field(data, field_def)
                result['emergency_stop'][name] = value
        except Exception as e:
            print(f" DB36 解析异常: {e}")

        return result

    # 4. 获取 DB 块号
    def get_db_number(self) -> int:
        return self.db_config['db_number']

    # 5. 获取数据总大小
    def get_total_size(self) -> int:
        return self.db_config['total_size']


# ==================== 单例模式 ====================

_db36_parser_instance: Optional[ConfigDrivenDB36Parser] = None


def get_db36_parser() -> ConfigDrivenDB36Parser:
    """获取 DB36 解析器单例"""
    global _db36_parser_instance
    if _db36_parser_instance is None:
        _db36_parser_instance = ConfigDrivenDB36Parser()
    return _db36_parser_instance


def reset_db36_parser():
    """重置 DB36 解析器 (配置更新后调用)"""
    global _db36_parser_instance
    _db36_parser_instance = None
