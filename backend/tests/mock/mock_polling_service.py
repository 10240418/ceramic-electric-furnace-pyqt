#!/usr/bin/env python3
# ============================================================
# 鏂囦欢璇存槑: mock_polling_service.py - 鐢电倝妯℃嫙杞鏈嶅姟
# ============================================================
# 鍔熻兘:
# 1. 妯℃嫙PLC杞锛岀敓鎴愮鍚圖B鍧楃粨鏋勭殑鍘熷鏁版嵁
# 2. 浣跨敤涓庢寮忎唬鐮佺浉鍚岀殑瑙ｆ瀽鍣ㄥ拰杞崲鍣?
# 3. 灏嗘暟鎹啓鍏nfluxDB
# 4. 姣?绉掕疆璇竴娆?
# 5. 妯℃嫙Modbus RTU鏂欎粨閲嶉噺璇诲彇
#
# 浣跨敤鏂规硶:
#   python tests/mock/mock_polling_service.py
#
# 鍋滄鏂规硶:
#   Ctrl+C
# ============================================================

import sys
import os
import asyncio
import signal
from datetime import datetime
from typing import Dict, Any

# 娣诲姞椤圭洰鏍圭洰褰曞埌璺緞
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from backend.tests.mock.mock_data_generator import MockDataGenerator
from backend.config import get_settings
from backend.config import get_settings
from backend.core.influxdb import write_point
from backend.plc.parser_modbus import ModbusDataParser
from backend.plc.parser_status import ModbusStatusParser
from backend.plc.parser_config_db33 import ConfigDrivenDB33Parser
from backend.tools.converter_furnace import FurnaceConverter

settings = get_settings()

# ============================================================
# 閰嶇疆
# ============================================================
POLL_INTERVAL = 5  # 杞闂撮殧 (绉?

# 瑙ｆ瀽鍣ㄥ疄渚?
_modbus_parser = ModbusDataParser()
_status_parser = ModbusStatusParser()
_db33_parser = ConfigDrivenDB33Parser()
_furnace_converter = FurnaceConverter()

# 杩愯鐘舵€?
_is_running = True


def signal_handler(sig, frame):
    """澶勭悊Ctrl+C淇″彿"""
    global _is_running
    print("\n鈴癸笍  鏀跺埌鍋滄淇″彿锛屾鍦ㄩ€€鍑?..")
    _is_running = False


def write_modbus_data_to_influx(parsed_data: Dict[str, Any], timestamp: datetime):
    """鍐欏叆DB32浼犳劅鍣ㄦ暟鎹埌InfluxDB
    
    Args:
        parsed_data: 瑙ｆ瀽鍚庣殑鏁版嵁 (鍖呭惈 electrode_depths, cooling_pressures, cooling_flows, valve_openings)
        timestamp: 鏃堕棿鎴?
    """
    # 1. 绾㈠娴嬭窛 (鐢垫瀬娣卞害)
    for name, value_dict in parsed_data.get('electrode_depths', {}).items():
        write_point(
            measurement="sensor_data",
            tags={
                "device_id": get_settings().device_id,
                "device_type": "electric_furnace",
                "module_type": "infrared_distance",
                "sensor_name": name,
            },
            fields={
                "distance": value_dict.get('distance', 0),
                "high": value_dict.get('high', 0),
                "low": value_dict.get('low', 0),
            },
            timestamp=timestamp
        )
    
    # 2. 鍘嬪姏浼犳劅鍣?
    for name, value_dict in parsed_data.get('cooling_pressures', {}).items():
        write_point(
            measurement="sensor_data",
            tags={
                "device_id": get_settings().device_id,
                "device_type": "electric_furnace",
                "module_type": "pressure",
                "sensor_name": name,
            },
            fields={
                "pressure": value_dict.get('pressure', 0),
                "raw": value_dict.get('raw', 0),
            },
            timestamp=timestamp
        )
    
    # 3. 娴侀噺璁?
    for name, value_dict in parsed_data.get('cooling_flows', {}).items():
        write_point(
            measurement="sensor_data",
            tags={
                "device_id": get_settings().device_id,
                "device_type": "electric_furnace",
                "module_type": "flow_meter",
                "sensor_name": name,
            },
            fields={
                "flow": value_dict.get('flow', 0),
                "raw": value_dict.get('raw', 0),
            },
            timestamp=timestamp
        )
    
    # 4. 铦堕榾
    for name, value_dict in parsed_data.get('valve_openings', {}).items():
        write_point(
            measurement="sensor_data",
            tags={
                "device_id": get_settings().device_id,
                "device_type": "electric_furnace",
                "module_type": "butterfly_valve",
                "sensor_name": name,
            },
            fields={
                "opening": value_dict.get('opening', 0),
            },
            timestamp=timestamp
        )


def write_electricity_data_to_influx(raw_data: Dict[str, float], converted_data: Dict[str, float], timestamp: datetime):
    """鍐欏叆DB33鐢佃〃鏁版嵁鍒癐nfluxDB
    
    Args:
        raw_data: 鍘熷璇绘暟
        converted_data: 杞崲鍚庢暟鎹?(涔樹互CT/PT鍙樻瘮)
        timestamp: 鏃堕棿鎴?
    """
    # 鍚堝苟鎵€鏈夊瓧娈?
    all_fields = {**converted_data}
    all_fields['ct_ratio'] = 20  # 璁板綍鍙樻瘮
    
    write_point(
        measurement="sensor_data",
        tags={
            "device_id": get_settings().device_id,
            "device_type": "electric_furnace",
            "module_type": "electricity_meter",
            "sensor_name": "main_meter",
        },
        fields=all_fields,
        timestamp=timestamp
    )


def write_weight_data_to_influx(weight: int, timestamp: datetime):
    """鍐欏叆鏂欎粨閲嶉噺鏁版嵁鍒癐nfluxDB
    
    Args:
        weight: 鍑€閲?(kg)
        timestamp: 鏃堕棿鎴?
    """
    write_point(
        measurement="sensor_data",
        tags={
            "device_id": "hopper_1",
            "device_type": "hopper",
            "module_type": "weight",
            "sensor_name": "net_weight",
        },
        fields={
            "weight": weight,
        },
        timestamp=timestamp
    )


async def poll_mock_data():
    """妯℃嫙杞涓诲惊鐜?""
    global _is_running
    
    print("=" * 60)
    print("馃殌 鐢电倝妯℃嫙杞鏈嶅姟鍚姩")
    print("=" * 60)
    print(f"馃搳 杞闂撮殧: {POLL_INTERVAL}绉?)
    print(f"馃摝 DB鍧? DB30(鐘舵€?, DB32(浼犳劅鍣?, DB33(鐢佃〃)")
    print(f" InfluxDB: {settings.influx_url}")
    print(f"馃搧 Bucket: {settings.influx_bucket}")
    print("=" * 60)
    print("鎸?Ctrl+C 鍋滄鏈嶅姟")
    print("=" * 60)
    
    # 鍒濆鍖栨暟鎹敓鎴愬櫒
    generator = MockDataGenerator()
    
    poll_count = 0
    
    while _is_running:
        try:
            poll_count += 1
            timestamp = datetime.now()
            
            print(f"\n[{timestamp.strftime('%H:%M:%S')}] 绗?{poll_count} 娆¤疆璇?..")
            
            # 鐢熸垚鎵€鏈塂B鍧楃殑妯℃嫙鏁版嵁
            all_db_data = generator.generate_all_db_data()
            
            # =============== 澶勭悊 DB32 (浼犳劅鍣ㄦ暟鎹? ===============
            db32_raw = all_db_data[32]
            db32_parsed = _modbus_parser.parse(db32_raw)
            write_modbus_data_to_influx(db32_parsed, timestamp)
            print(f"   DB32 (浼犳劅鍣?: 宸插啓鍏?- 鐢垫瀬娣卞害, 鍘嬪姏, 娴侀噺, 铦堕榾")
            
            # =============== 澶勭悊 DB33 (鐢佃〃鏁版嵁) ===============
            db33_raw = all_db_data[33]
            db33_parsed = _db33_parser.parse(db33_raw)
            raw_data = db33_parsed['raw']
            converted_data = _furnace_converter.convert_electricity(raw_data)
            write_electricity_data_to_influx(raw_data, converted_data, timestamp)
            print(f"   DB33 (鐢佃〃): Pt={converted_data['Pt']:.2f}kW, "
                  f"I_0={converted_data['I_0']:.1f}A (CT=20)")
            
            # =============== 澶勭悊 DB30 (鐘舵€佹暟鎹?- 浠呮墦鍗颁笉鍐欏叆) ===============
            db30_raw = all_db_data[30]
            db30_parsed = _status_parser.parse(db30_raw)
            online_count = sum(1 for dev in db30_parsed['devices'] if dev['comm_ok'])
            print(f"  鈩癸笍  DB30 (鐘舵€?: {online_count}/10 璁惧鍦ㄧ嚎")
            
            # =============== 澶勭悊 Modbus RTU (鏂欎粨閲嶉噺) ===============
            hopper_weight = generator.get_hopper_weight()
            write_weight_data_to_influx(hopper_weight, timestamp)
            print(f"   鏂欎粨閲嶉噺: {hopper_weight} kg")
            
            print(f"  馃搳 杞缁熻: 鍏?{poll_count} 娆?)
            
        except Exception as e:
            print(f"   杞閿欒: {e}")
            import traceback
            traceback.print_exc()
        
        # 绛夊緟涓嬫杞
        await asyncio.sleep(POLL_INTERVAL)
    
    print("\n 妯℃嫙杞鏈嶅姟宸插仠姝?)


def main():
    """涓诲叆鍙?""
    # 娉ㄥ唽淇″彿澶勭悊
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 杩愯寮傛杞
    try:
        asyncio.run(poll_mock_data())
    except KeyboardInterrupt:
        print("\n鈴癸笍  鏈嶅姟宸插仠姝?)


if __name__ == "__main__":
    main()
