#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PDF导出模块 - 负责将分析结果和图表导出为PDF格式
"""

import os
import time
import platform
from datetime import datetime
from typing import List, Dict, Any, Optional

# ReportLab导入
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.platypus import PageBreak
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping


class PDFExporter:
    """
    PDF导出类
    负责将分析结果和图表导出为PDF格式
    """
    
    def __init__(self, output_dir: str = "output"):
        """
        初始化PDF导出器
        
        Args:
            output_dir: 输出目录，默认为"output"
        """
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 注册中文字体
        self._register_fonts()
        
        # 初始化样式
        self.styles = getSampleStyleSheet()
        self._init_custom_styles()
    
    def _register_fonts(self):
        """
        注册中文字体
        根据不同操作系统注册合适的中文字体
        """
        system = platform.system()
        
        # 尝试注册中文字体
        try:
            if system == 'Darwin':  # macOS
                # 注册macOS系统中文字体
                pdfmetrics.registerFont(TTFont('SimSun', '/System/Library/Fonts/STHeiti Light.ttc'))
                pdfmetrics.registerFont(TTFont('SimHei', '/System/Library/Fonts/STHeiti Medium.ttc'))
                pdfmetrics.registerFont(TTFont('Microsoft-YaHei', '/System/Library/Fonts/STHeiti Light.ttc'))
            elif system == 'Windows':
                # 注册Windows系统中文字体
                pdfmetrics.registerFont(TTFont('SimSun', 'C:\\Windows\\Fonts\\simsun.ttc'))
                pdfmetrics.registerFont(TTFont('SimHei', 'C:\\Windows\\Fonts\\simhei.ttf'))
                pdfmetrics.registerFont(TTFont('Microsoft-YaHei', 'C:\\Windows\\Fonts\\msyh.ttc'))
            elif system == 'Linux':
                # 注册Linux系统中文字体
                pdfmetrics.registerFont(TTFont('SimSun', '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc'))
                pdfmetrics.registerFont(TTFont('SimHei', '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'))
            
            # 添加字体映射
            addMapping('SimSun', 0, 0, 'SimSun')  # 常规
            addMapping('SimHei', 0, 0, 'SimHei')  # 常规
            
        except Exception as e:
            print(f"注册字体时出错: {e}")
            # 如果注册失败，将使用默认字体
    
    def _init_custom_styles(self):
        """
        初始化自定义样式
        """
        # 标题样式 - 修改名称为'CustomTitle'避免与内置样式冲突
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontName='SimHei',  # 使用黑体
            fontSize=18,
            alignment=1,  # 居中
            spaceAfter=12,
            encoding='utf-8'
        ))
        
        # 副标题样式
        self.styles.add(ParagraphStyle(
            name='Subtitle',
            parent=self.styles['Heading2'],
            fontName='SimHei',  # 使用黑体
            fontSize=14,
            spaceAfter=10,
            encoding='utf-8'
        ))
        
        # 章节标题样式
        self.styles.add(ParagraphStyle(
            name='Section',
            parent=self.styles['Heading3'],
            fontName='SimHei',  # 使用黑体
            fontSize=12,
            spaceAfter=8,
            encoding='utf-8'
        ))
        
        # 正文样式 - 修改名称为'CustomBodyText'避免与内置样式冲突
        self.styles.add(ParagraphStyle(
            name='CustomBodyText',
            parent=self.styles['Normal'],
            fontName='SimSun',  # 使用宋体
            fontSize=10,
            spaceAfter=6,
            encoding='utf-8'
        ))
        
        # 更新默认样式
        self.styles['Normal'].fontName = 'SimSun'
        self.styles['Normal'].encoding = 'utf-8'
        self.styles['Heading1'].fontName = 'SimHei'
        self.styles['Heading1'].encoding = 'utf-8'
        self.styles['Heading2'].fontName = 'SimHei'
        self.styles['Heading2'].encoding = 'utf-8'
        self.styles['Heading3'].fontName = 'SimHei'
        self.styles['Heading3'].encoding = 'utf-8'
    
    def export_analysis_to_pdf(self, 
                             token_symbol: str, 
                             analysis_text: str, 
                             chart_paths: List[str],
                             metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        将分析结果和图表导出为PDF
        
        Args:
            token_symbol: 代币符号
            analysis_text: 分析文本内容
            chart_paths: 图表文件路径列表
            metadata: 元数据字典（可选）
            
        Returns:
            str: 生成的PDF文件路径
        """
        # 生成PDF文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"{self.output_dir}/{token_symbol}_analysis_{timestamp}.pdf"
        
        # 创建PDF文档
        doc = SimpleDocTemplate(
            pdf_filename,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72,
            encoding='utf-8'  # 设置文档编码为UTF-8
        )
        
        # 准备内容元素
        elements = []
        
        # 添加标题
        title = f"{token_symbol} 加密货币市场分析报告"
        elements.append(Paragraph(title, self.styles['CustomTitle']))
        
        # 添加生成时间
        generation_time = f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        elements.append(Paragraph(generation_time, self.styles['Normal']))
        elements.append(Spacer(1, 0.5 * cm))
        
        # 处理分析文本
        self._add_analysis_text(elements, analysis_text)
        
        # 添加图表
        if chart_paths:
            elements.append(PageBreak())
            elements.append(Paragraph("可视化图表", self.styles['Section']))
            elements.append(Spacer(1, 0.3 * cm))
            self._add_charts(elements, chart_paths)
        
        # 添加元数据（如果有）
        if metadata:
            elements.append(PageBreak())
            elements.append(Paragraph("分析元数据", self.styles['Section']))
            elements.append(Spacer(1, 0.3 * cm))
            self._add_metadata(elements, metadata)
        
        # 构建PDF
        doc.build(elements)
        
        return pdf_filename
    
    def _add_analysis_text(self, elements: List, analysis_text: str):
        """
        添加分析文本到PDF元素列表
        
        Args:
            elements: PDF元素列表
            analysis_text: 分析文本内容
        """
        # 分割文本为段落
        paragraphs = analysis_text.split('\n')
        
        # 标题计数器，用于识别连续的标题行
        title_counter = 0
        
        for paragraph in paragraphs:
            if not paragraph.strip():
                # 空行添加间距
                elements.append(Spacer(1, 0.2 * cm))
                continue
            
            # 清理文本，移除可能的Markdown格式符号
            cleaned_text = paragraph.strip()
            
            # 处理标题 - 支持多种标题格式识别
            if paragraph.startswith('##'):
                # 二级标题
                text = paragraph.replace('##', '').strip()
                elements.append(Paragraph(text, self.styles['Subtitle']))
                title_counter += 1
            elif paragraph.startswith('#'):
                # 一级标题
                text = paragraph.replace('#', '').strip()
                elements.append(Paragraph(text, self.styles['Heading1']))
                title_counter += 1
            elif paragraph.startswith('###'):
                # 三级标题
                text = paragraph.replace('###', '').strip()
                elements.append(Paragraph(text, self.styles['Section']))
                title_counter += 1
            elif paragraph.startswith('-') or paragraph.startswith('*'):
                # 列表项 - 移除列表符号并适当缩进
                text = paragraph.lstrip('-* ').strip()
                # 创建带缩进的段落
                elements.append(Paragraph("• " + text, self.styles['Normal']))
            elif ':' in paragraph and len(paragraph.split(':')[0].split()) <= 3 and title_counter > 0:
                # 识别"标题：内容"格式的行，作为小标题处理
                parts = paragraph.split(':', 1)
                if len(parts) == 2:
                    title = parts[0].strip()
                    content = parts[1].strip()
                    elements.append(Paragraph(title + ":", self.styles['Subtitle']))
                    if content:  # 如果冒号后有内容
                        elements.append(Paragraph(content, self.styles['Normal']))
                else:
                    elements.append(Paragraph(paragraph, self.styles['Normal']))
            else:
                # 普通段落 - 清理可能的Markdown语法
                # 移除Markdown链接格式 [text](url) 只保留text
                import re
                cleaned_text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', paragraph)
                # 移除Markdown强调符号 ** 和 __
                cleaned_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', cleaned_text)
                cleaned_text = re.sub(r'__([^_]+)__', r'\1', cleaned_text)
                # 移除Markdown斜体符号 * 和 _
                cleaned_text = re.sub(r'\*([^*]+)\*', r'\1', cleaned_text)
                cleaned_text = re.sub(r'_([^_]+)_', r'\1', cleaned_text)
                
                elements.append(Paragraph(cleaned_text, self.styles['Normal']))
                title_counter = 0  # 重置标题计数器
    
    def _add_charts(self, elements: List, chart_paths: List[str]):
        """
        添加图表到PDF元素列表
        
        Args:
            elements: PDF元素列表
            chart_paths: 图表文件路径列表
        """
        for i, chart_path in enumerate(chart_paths):
            if os.path.exists(chart_path):
                # 提取图表名称
                chart_name = os.path.basename(chart_path)
                chart_title = chart_name.split('_')[1] if '_' in chart_name else "图表"
                
                # 添加图表标题
                elements.append(Paragraph(f"图表 {i+1}: {chart_title}", self.styles['Normal']))
                
                # 添加图表
                img = Image(chart_path, width=6*inch, height=3*inch)
                elements.append(img)
                elements.append(Spacer(1, 0.5 * cm))
    
    def _add_metadata(self, elements: List, metadata: Dict[str, Any]):
        """
        添加元数据到PDF元素列表
        
        Args:
            elements: PDF元素列表
            metadata: 元数据字典
        """
        # 创建元数据表格
        data = []
        for key, value in metadata.items():
            if isinstance(value, (list, dict)):
                value = str(value)
            data.append([key, value])
        
        if data:
            table = Table(data, colWidths=[2*inch, 3*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'SimHei'),  # 使用黑体替代Helvetica-Bold
                ('FONTNAME', (1, 0), (-1, -1), 'SimSun'),  # 表格内容使用宋体
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(table)