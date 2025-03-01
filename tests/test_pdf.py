#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试PDF导出功能
"""

from pdf_exporter import PDFExporter

# 创建PDF导出器实例
exporter = PDFExporter("output")

# 测试中文内容
test_content = """
# 测试中文显示

这是一个测试文档，用于验证中文字符是否能够正确显示在PDF中。

## 测试标题

- 测试列表项1
- 测试列表项2

### 小标题

这是正文内容，包含中文字符。
"""

# 导出PDF
pdf_path = exporter.export_analysis_to_pdf(
    "TEST",
    test_content,
    [],  # 无图表
    {"测试键": "测试值", "中文元数据": "这是中文元数据内容"}
)

print(f'PDF已生成: {pdf_path}')