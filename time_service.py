from datetime import datetime
from typing import Any
import logging
import logging.config

import yaml
from dateutil.relativedelta import relativedelta
from mcp.server.fastmcp import FastMCP

# 禁用 FastMCP 默认尝试加载不可访问的 .env 文件
server = FastMCP(
    name="OrganizationQueryServer"
)



def setup_logging() -> None:
    try:
        with open("conf/logging.yaml", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        logging.config.dictConfig(config)
    except Exception as exc:
        logging.basicConfig(level=logging.INFO)
        logging.getLogger(__name__).warning(
            "加载日志配置失败，使用默认配置: %s", exc
        )


setup_logging()

logger = logging.getLogger(__name__)

# 初始化 MCP 服务器

# 记录启动信息
logger.info("=== 时间服务启动 ===")

# @server.tool()
# def get_current_time() -> dict[str, Any]:
#     """
#     获取当前时间，返回时间戳（毫秒）和格式化的时间字符串。
    
#     :return: 包含时间戳和格式化时间的字典，格式如下：
#         {
#             "timestamp": 1234567890123,  # 毫秒级时间戳
#             "formatted_time": "2023-01-01 12:00:00"  # 格式化的时间字符串
#         }
#     """
#     logger.info("获取当前时间")
#     try:
#         current_time = datetime.now()
#         timestamp_ms = int(time.time() * 1000)
#         formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        
#         result = {
#             "timestamp": timestamp_ms,
#             "formatted_time": formatted_time
#         }
#         logger.info(f"当前时间: {formatted_time}, 时间戳: {timestamp_ms}")
#         return result
#     except Exception as e:
#         error_msg = f"获取当前时间失败: {str(e)}"
#         logger.error(error_msg, exc_info=True)
#         return {"error": error_msg}

@server.tool()
def calculate_relative_time(time_type: str, offset: int = -1) -> dict[str, Any]:
    """
    计算相对时间，返回指定时间范围的开始和结束时间。
    
    :param time_type: 时间类型，支持以下值：
        - day: 按天计算时间范围
        - week: 按周计算时间范围（从周一到周日）
        - month: 按月计算时间范围（从月初1号到月末）
        - year: 按年计算时间范围（从1月1日到12月31日）
    
    :param offset: 时间偏移量，表示相对于当前时间的偏移：
        - offset = 0: 表示当前时间单位（今天、本周、本月、今年）
        - offset < 0: 表示过去的时间（如 -1 表示昨天、上周、上月、去年）
        - offset > 0: 表示未来的时间（如 1 表示明天、下周、下月、明年）
        
        常见时间表述对应的参数示例：
        | 时间表述 | time_type | offset |
        |---------|-----------|--------|
        | 今天     | day       | 0      |
        | 昨天     | day       | -1     |
        | 前天     | day       | -2     |
        | 明天     | day       | 1      |
        | 后天     | day       | 2      |
        | 本周     | week      | 0      |
        | 上周     | week      | -1     |
        | 前两周   | week      | -2     |
        | 下周     | week      | 1      |
        | 本月     | month     | 0      |
        | 上月     | month     | -1     |
        | 前两个月 | month     | -2     |
        | 下个月   | month     | 1      |
        | 今年     | year      | 0      |
        | 去年     | year      | -1     |
        | 前年     | year      | -2     |
        | 明年     | year      | 1      |
    
    :return: 包含开始和结束时间的字典，格式如下：
        {
            "start": {
                "timestamp": 1234567890123,  # 开始时间的毫秒级时间戳
                "formatted_time": "2023-01-01 00:00:00"  # 格式化的开始时间
            },
            "end": {
                "timestamp": 1234654290123,  # 结束时间的毫秒级时间戳
                "formatted_time": "2023-01-01 23:59:59"  # 格式化的结束时间
            },
            "description": "计算时间范围的描述"
        }
    """
    logger.info(f"计算相对时间 - 类型: {time_type}, 偏移量: {offset}")
    
    try:
        now = datetime.now()
        logger.debug(f"当前时间: {now}")
        
        # 根据时间类型计算目标时间
        if time_type == "day":
            target_date = now + relativedelta(days=offset)
            start_time = datetime(target_date.year, target_date.month, target_date.day)
            end_time = start_time + relativedelta(days=1)
        elif time_type == "week":
            # 计算上N周的周一到周日
            target_date = now + relativedelta(weeks=offset)
            start_time = target_date - relativedelta(days=target_date.weekday())
            start_time = datetime(start_time.year, start_time.month, start_time.day)
            end_time = start_time + relativedelta(weeks=1)
        elif time_type == "month":
            # 计算上N个月的第一天到最后一天
            target_date = now + relativedelta(months=offset)
            start_time = datetime(target_date.year, target_date.month, 1)
            end_time = start_time + relativedelta(months=1)
        elif time_type == "year":
            # 计算前N年的第一天到最后一天
            target_date = now + relativedelta(years=offset)
            start_time = datetime(target_date.year, 1, 1)
            end_time = start_time + relativedelta(years=1)
        else:
            error_msg = f"不支持的时间类型: {time_type}"
            logger.error(error_msg)
            return {"error": error_msg}
        
        # 转换为时间戳（毫秒）
        start_timestamp = int(start_time.timestamp() * 1000)
        end_timestamp = int(end_time.timestamp() * 1000)
        
        result = {
            "start": {
                "timestamp": start_timestamp,
                "formatted_time": start_time.strftime("%Y-%m-%d %H:%M:%S")
            },
            "end": {
                "timestamp": end_timestamp,
                "formatted_time": end_time.strftime("%Y-%m-%d %H:%M:%S")
            },
            "description": f"计算{offset}个{time_type}前的时间范围"
        }
        
        logger.info(f"计算完成 - {result['description']}")
        logger.debug(f"详细结果: {result}")
        
        return result
        
    except Exception as e:
        error_msg = f"计算相对时间失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {"error": error_msg}

@server.tool()
def calculate_date_range(start_date: str, end_date: str = None) -> dict[str, Any]:
    """
    计算指定日期或日期范围的开始和结束时间，返回时间范围。
    
    :param start_date: 开始日期，支持以下格式：
        - YYYY-MM-DD：完整的年月日格式，如 "2023-12-31"
        - MM-DD：月日格式（自动使用当前年份），如 "12-31"
    
    :param end_date: 结束日期（可选），格式同 start_date：
        - 如果不提供，则计算 start_date 当天的时间范围（从 00:00:00 到 23:59:59）
        - 如果提供，则计算从 start_date 00:00:00 到 end_date 23:59:59 的时间范围
    
    使用示例：
        1. 查询指定日期：
           calculate_date_range("2023-12-31")
           # 返回 2023-12-31 00:00:00 到 2023-12-31 23:59:59
        
        2. 查询日期范围：
           calculate_date_range("2023-12-01", "2023-12-31")
           # 返回 2023-12-01 00:00:00 到 2023-12-31 23:59:59
        
        3. 使用月日格式（当前年份）：
           calculate_date_range("12-31")
           # 假设当前是2024年，返回 2024-12-31 00:00:00 到 2024-12-31 23:59:59
    
    :return: 包含开始和结束时间的字典，格式如下：
        {
            "start": {
                "timestamp": 1234567890123,  # 开始时间的毫秒级时间戳
                "formatted_time": "2023-12-31 00:00:00"  # 格式化的开始时间
            },
            "end": {
                "timestamp": 1234654290123,  # 结束时间的毫秒级时间戳
                "formatted_time": "2023-12-31 23:59:59"  # 格式化的结束时间
            },
            "description": "计算日期范围的描述"
        }
    """
    logger.info(f"计算日期范围 - 开始日期: {start_date}, 结束日期: {end_date}")
    
    try:
        # 处理日期格式
        def parse_date(date_str: str) -> datetime:
            try:
                # 尝试完整的年月日格式 (YYYY-MM-DD)
                return datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                try:
                    # 尝试月日格式 (MM-DD)，使用当前年份
                    current_year = datetime.now().year
                    return datetime.strptime(f"{current_year}-{date_str}", "%Y-%m-%d")
                except ValueError:
                    raise ValueError(f"无效的日期格式: {date_str}，支持的格式：YYYY-MM-DD 或 MM-DD")

        # 解析开始日期
        start_time = parse_date(start_date)
        start_time = datetime(start_time.year, start_time.month, start_time.day)
        
        # 如果没有提供结束日期，设置为开始日期的最后一秒
        if end_date is None:
            end_time = start_time + relativedelta(days=1, microseconds=-1)
        else:
            # 解析结束日期，设置为当天的最后一秒
            end_time = parse_date(end_date)
            end_time = datetime(end_time.year, end_time.month, end_time.day) + relativedelta(days=1, microseconds=-1)
        
        # 确保开始时间不晚于结束时间
        if start_time > end_time:
            error_msg = f"开始日期 ({start_date}) 不能晚于结束日期 ({end_date})"
            logger.error(error_msg)
            return {"error": error_msg}
        
        # 转换为时间戳（毫秒）
        start_timestamp = int(start_time.timestamp() * 1000)
        end_timestamp = int(end_time.timestamp() * 1000)
        
        result = {
            "start": {
                "timestamp": start_timestamp,
                "formatted_time": start_time.strftime("%Y-%m-%d %H:%M:%S")
            },
            "end": {
                "timestamp": end_timestamp,
                "formatted_time": end_time.strftime("%Y-%m-%d %H:%M:%S")
            },
            "description": f"计算日期范围: {start_date}" + (f" 到 {end_date}" if end_date else "")
        }
        
        logger.info(f"计算完成 - {result['description']}")
        logger.debug(f"详细结果: {result}")
        
        return result
        
    except Exception as e:
        error_msg = f"计算日期范围失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {"error": error_msg}

if __name__ == "__main__":
    logger.info("启动时间服务...")
    try:
        server.run(transport="stdio")
    except Exception:
        logger.exception("时间服务运行异常")
        raise
    finally:
        logger.info("=== 服务结束 ===")
