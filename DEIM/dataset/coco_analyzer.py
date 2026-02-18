#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COCO标签统计与可视化程序
功能：
1. 统计COCO格式JSON文件中的类别数量、名称和索引
2. 统计每个类别的实例数量
3. 可视化分析：
   - 类别实例数量分布
   - 目标中心点分布热力图
   - 目标宽高分布
   - 目标面积分布
   - 宽高比分布
   - 类别共现矩阵

使用方法：
python coco_analyzer.py path/to/your/coco.json

或者在代码中调用：
from coco_analyzer import analyze_coco_annotations
result = analyze_coco_annotations("path/to/your/coco.json", visualize=True)
"""

import json
import os
import sys
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Rectangle
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 设置绘图风格
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 100
plt.rcParams['savefig.dpi'] = 300

def analyze_coco_annotations(json_file_path, visualize=True, output_dir=None):
    """
    分析COCO格式的标注文件
    
    Args:
        json_file_path (str): COCO JSON文件的路径
        visualize (bool): 是否生成可视化图表
        output_dir (str): 图表保存目录，默认为JSON文件所在目录
    
    Returns:
        dict: 包含统计信息的字典，如果失败返回None
    """
    
    # 检查文件是否存在
    if not os.path.exists(json_file_path):
        print(f"错误：文件 {json_file_path} 不存在")
        return None
    
    # 设置输出目录
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(json_file_path), 'coco_analysis')
    
    if visualize and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"创建输出目录: {output_dir}")
    
    try:
        # 读取JSON文件
        with open(json_file_path, 'r', encoding='utf-8') as f:
            coco_data = json.load(f)
        
        print(f"成功读取文件: {json_file_path}")
        print("=" * 50)
        
        # 检查必要的字段
        if 'categories' not in coco_data:
            print("错误：JSON文件中缺少'categories'字段")
            return None
        
        if 'annotations' not in coco_data:
            print("错误：JSON文件中缺少'annotations'字段")
            return None
        
        # 获取图像信息
        images = coco_data.get('images', [])
        image_id_to_info = {img['id']: img for img in images if 'id' in img}
        
        # 1. 统计类别信息
        categories = coco_data['categories']
        num_categories = len(categories)
        
        print(f"1. 类别统计:")
        print(f"   总类别数: {num_categories}")
        print(f"   图像数量: {len(images)}")
        print(f"   类别详情:")
        
        # 创建类别ID到名称的映射
        category_id_to_name = {}
        for category in categories:
            if 'id' not in category or 'name' not in category:
                print("警告：发现格式不完整的类别信息")
                continue
            cat_id = category['id']
            cat_name = category['name']
            category_id_to_name[cat_id] = cat_name
            print(f"   - 索引 {cat_id}: {cat_name}")
        
        print("\n" + "=" * 50)
        
        # 2. 统计每个类别的实例数量和几何信息
        annotations = coco_data['annotations']
        category_instance_count = defaultdict(int)
        
        # 存储几何信息
        center_points = []  # (x, y, category_id)
        bbox_sizes = []     # (width, height, category_id)
        areas = []          # (area, category_id)
        aspect_ratios = []  # (width/height, category_id)
        
        # 每个类别的详细信息
        category_details = defaultdict(lambda: {
            'centers': [],
            'widths': [],
            'heights': [],
            'areas': [],
            'aspect_ratios': []
        })
        
        # 图像级别的类别共现
        image_categories = defaultdict(set)
        
        valid_annotations = 0
        for annotation in annotations:
            if 'category_id' not in annotation or 'bbox' not in annotation:
                continue
            
            category_id = annotation['category_id']
            bbox = annotation['bbox']  # [x, y, width, height]
            image_id = annotation.get('image_id', -1)
            
            if len(bbox) != 4:
                continue
            
            x, y, w, h = bbox
            
            # 获取图像尺寸用于归一化
            img_width = 1.0
            img_height = 1.0
            if image_id in image_id_to_info:
                img_info = image_id_to_info[image_id]
                img_width = img_info.get('width', 1.0)
                img_height = img_info.get('height', 1.0)
            
            # 计算中心点（归一化）
            center_x = (x + w / 2) / img_width
            center_y = (y + h / 2) / img_height
            
            # 计算面积和宽高比
            area = w * h
            aspect_ratio = w / h if h > 0 else 0
            
            # 归一化宽高
            norm_w = w / img_width
            norm_h = h / img_height
            
            # 存储数据
            center_points.append((center_x, center_y, category_id))
            bbox_sizes.append((norm_w, norm_h, category_id))
            areas.append((area, category_id))
            aspect_ratios.append((aspect_ratio, category_id))
            
            # 按类别存储
            category_details[category_id]['centers'].append((center_x, center_y))
            category_details[category_id]['widths'].append(norm_w)
            category_details[category_id]['heights'].append(norm_h)
            category_details[category_id]['areas'].append(area)
            category_details[category_id]['aspect_ratios'].append(aspect_ratio)
            
            # 记录图像中的类别
            image_categories[image_id].add(category_id)
            
            category_instance_count[category_id] += 1
            valid_annotations += 1
        
        print(f"2. 每个类别的实例数量:")
        print(f"   总标注数: {len(annotations)}")
        print(f"   有效标注数: {valid_annotations}")
        print(f"   各类别实例统计:")
        
        # 按类别ID排序显示
        total_instances = 0
        for cat_id in sorted(category_id_to_name.keys()):
            cat_name = category_id_to_name[cat_id]
            instance_count = category_instance_count[cat_id]
            total_instances += instance_count
            print(f"   - {cat_name} (ID: {cat_id}): {instance_count} 个实例")
        
        print(f"\n   验证: 总实例数 = {total_instances}")
        
        # 返回统计结果
        result = {
            'total_categories': num_categories,
            'categories': [(cat['id'], cat['name']) for cat in categories if 'id' in cat and 'name' in cat],
            'total_images': len(images),
            'total_annotations': len(annotations),
            'valid_annotations': valid_annotations,
            'category_instances': dict(category_instance_count),
            'category_names': category_id_to_name,
            'center_points': center_points,
            'bbox_sizes': bbox_sizes,
            'areas': areas,
            'aspect_ratios': aspect_ratios,
            'category_details': dict(category_details),
            'image_categories': dict(image_categories)
        }
        
        # 3. 生成可视化
        if visualize and valid_annotations > 0:
            print("\n" + "=" * 50)
            print("3. 生成可视化图表...")
            generate_visualizations(result, output_dir)
            print(f"   图表已保存到: {output_dir}")
        
        return result
        
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        return None
    except Exception as e:
        print(f"处理文件时发生错误: {e}")
        import traceback
        traceback.print_exc()
        return None

def generate_visualizations(result, output_dir):
    """
    生成所有可视化图表
    """
    
    category_names = result['category_names']
    category_instances = result['category_instances']
    center_points = result['center_points']
    bbox_sizes = result['bbox_sizes']
    areas = result['areas']
    aspect_ratios = result['aspect_ratios']
    category_details = result['category_details']
    image_categories = result['image_categories']
    
    # 颜色映射
    colors = plt.cm.tab20(np.linspace(0, 1, len(category_names)))
    cat_id_to_color = {cat_id: colors[i] for i, cat_id in enumerate(sorted(category_names.keys()))}
    
    # 1. 类别实例数量分布（横向条形图 + 饼图）
    plot_category_distribution(category_names, category_instances, output_dir)
    
    # 2. 目标中心点分布热力图
    plot_center_heatmap(center_points, category_names, output_dir)
    
    # 3. 目标中心点散点图（按类别）
    plot_center_scatter(center_points, category_names, cat_id_to_color, output_dir)
    
    # 4. 目标宽高分布
    plot_size_distribution(bbox_sizes, category_names, cat_id_to_color, output_dir)
    
    # 5. 目标面积分布
    plot_area_distribution(areas, category_names, output_dir)
    
    # 6. 宽高比分布
    plot_aspect_ratio_distribution(aspect_ratios, category_names, output_dir)
    
    # 7. 每个类别的详细统计
    plot_category_statistics(category_details, category_names, output_dir)
    
    # 8. 类别共现矩阵
    plot_cooccurrence_matrix(image_categories, category_names, output_dir)
    
    # 9. 综合统计仪表板
    plot_summary_dashboard(result, output_dir)
    
    print("   所有图表生成完成！")

def plot_category_distribution(category_names, category_instances, output_dir):
    """Plot category instance distribution"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Sort
    sorted_items = sorted(category_instances.items(), key=lambda x: x[1], reverse=True)
    cat_ids = [item[0] for item in sorted_items]
    counts = [item[1] for item in sorted_items]
    labels = [category_names.get(cat_id, f'ID:{cat_id}') for cat_id in cat_ids]
    
    # Horizontal bar chart
    colors_bar = plt.cm.viridis(np.linspace(0.3, 0.9, len(labels)))
    bars = ax1.barh(range(len(labels)), counts, color=colors_bar, edgecolor='black', linewidth=0.5)
    ax1.set_yticks(range(len(labels)))
    ax1.set_yticklabels(labels, fontsize=10)
    ax1.set_xlabel('Number of Instances', fontsize=12, fontweight='bold')
    ax1.set_title('Instance Distribution by Category', fontsize=14, fontweight='bold', pad=15)
    ax1.grid(axis='x', alpha=0.3, linestyle='--')
    
    # Add value labels
    for i, (bar, count) in enumerate(zip(bars, counts)):
        ax1.text(count, i, f' {count}', va='center', fontsize=9, fontweight='bold')
    
    # Pie chart
    colors_pie = plt.cm.Set3(np.linspace(0, 1, len(labels)))
    wedges, texts, autotexts = ax2.pie(counts, labels=labels, autopct='%1.1f%%',
                                         colors=colors_pie, startangle=90,
                                         textprops={'fontsize': 9})
    ax2.set_title('Category Proportion Distribution', fontsize=14, fontweight='bold', pad=15)
    
    # Optimize pie chart text
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '01_category_distribution.png'), bbox_inches='tight')
    plt.close()

def plot_center_heatmap(center_points, category_names, output_dir):
    """Plot object center point distribution heatmap"""
    if not center_points:
        return
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    
    # Extract all center points
    all_x = [p[0] for p in center_points]
    all_y = [p[1] for p in center_points]
    
    # Overall heatmap
    ax1 = axes[0]
    heatmap, xedges, yedges = np.histogram2d(all_x, all_y, bins=50, range=[[0, 1], [0, 1]])
    extent = [0, 1, 1, 0]  # Note: y-axis flipped to match image coordinate system
    
    im1 = ax1.imshow(heatmap.T, extent=extent, origin='upper', cmap='hot', aspect='auto', interpolation='bilinear')
    ax1.set_xlabel('Normalized X Coordinate', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Normalized Y Coordinate', fontsize=12, fontweight='bold')
    ax1.set_title(f'Object Center Point Distribution Heatmap (Total: {len(center_points)})', fontsize=14, fontweight='bold', pad=15)
    cbar1 = plt.colorbar(im1, ax=ax1)
    cbar1.set_label('Density', fontsize=11, fontweight='bold')
    ax1.grid(True, alpha=0.3, linestyle='--', color='white')
    
    # Scatter plot overlay
    ax2 = axes[1]
    ax2.hexbin(all_x, all_y, gridsize=30, cmap='YlOrRd', mincnt=1, extent=(0, 1, 0, 1))
    ax2.set_xlabel('Normalized X Coordinate', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Normalized Y Coordinate', fontsize=12, fontweight='bold')
    ax2.set_title('Object Center Point Hexbin Density Map', fontsize=14, fontweight='bold', pad=15)
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    ax2.invert_yaxis()
    ax2.grid(True, alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '02_center_heatmap.png'), bbox_inches='tight')
    plt.close()

def plot_center_scatter(center_points, category_names, cat_id_to_color, output_dir):
    """Plot center point scatter plot grouped by category"""
    if not center_points:
        return
    
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Group by category
    category_points = defaultdict(list)
    for x, y, cat_id in center_points:
        category_points[cat_id].append((x, y))
    
    # Plot each category
    for cat_id, points in sorted(category_points.items()):
        if not points:
            continue
        xs, ys = zip(*points)
        label = category_names.get(cat_id, f'ID:{cat_id}')
        color = cat_id_to_color.get(cat_id, 'gray')
        ax.scatter(xs, ys, alpha=0.6, s=30, c=[color], label=label, edgecolors='black', linewidth=0.3)
    
    ax.set_xlabel('Normalized X Coordinate', fontsize=12, fontweight='bold')
    ax.set_ylabel('Normalized Y Coordinate', fontsize=12, fontweight='bold')
    ax.set_title('Object Center Point Distribution by Category', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.invert_yaxis()
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=9, framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '03_center_scatter_by_category.png'), bbox_inches='tight')
    plt.close()

def plot_size_distribution(bbox_sizes, category_names, cat_id_to_color, output_dir):
    """Plot object width and height distribution"""
    if not bbox_sizes:
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 14))
    
    # Extract data
    widths = [s[0] for s in bbox_sizes]
    heights = [s[1] for s in bbox_sizes]
    
    # 1. Width distribution histogram
    ax1 = axes[0, 0]
    ax1.hist(widths, bins=50, color='skyblue', edgecolor='black', alpha=0.7)
    ax1.set_xlabel('Normalized Width', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Frequency', fontsize=11, fontweight='bold')
    ax1.set_title('Object Width Distribution', fontsize=13, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    ax1.axvline(np.median(widths), color='red', linestyle='--', linewidth=2, label=f'Median: {np.median(widths):.3f}')
    ax1.legend()
    
    # 2. Height distribution histogram
    ax2 = axes[0, 1]
    ax2.hist(heights, bins=50, color='lightcoral', edgecolor='black', alpha=0.7)
    ax2.set_xlabel('Normalized Height', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Frequency', fontsize=11, fontweight='bold')
    ax2.set_title('Object Height Distribution', fontsize=13, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    ax2.axvline(np.median(heights), color='red', linestyle='--', linewidth=2, label=f'Median: {np.median(heights):.3f}')
    ax2.legend()
    
    # 3. Width-height scatter plot (overall)
    ax3 = axes[1, 0]
    ax3.scatter(widths, heights, alpha=0.5, s=20, c='purple', edgecolors='black', linewidth=0.3)
    ax3.set_xlabel('Normalized Width', fontsize=11, fontweight='bold')
    ax3.set_ylabel('Normalized Height', fontsize=11, fontweight='bold')
    ax3.set_title('Object Width-Height Scatter Plot', fontsize=13, fontweight='bold')
    ax3.grid(True, alpha=0.3, linestyle='--')
    ax3.plot([0, 1], [0, 1], 'r--', alpha=0.5, linewidth=2, label='Width=Height')
    ax3.legend()
    
    # 4. Width-height scatter plot by category
    ax4 = axes[1, 1]
    category_sizes = defaultdict(lambda: {'widths': [], 'heights': []})
    for w, h, cat_id in bbox_sizes:
        category_sizes[cat_id]['widths'].append(w)
        category_sizes[cat_id]['heights'].append(h)
    
    for cat_id, sizes in sorted(category_sizes.items()):
        if not sizes['widths']:
            continue
        label = category_names.get(cat_id, f'ID:{cat_id}')
        color = cat_id_to_color.get(cat_id, 'gray')
        ax4.scatter(sizes['widths'], sizes['heights'], alpha=0.6, s=25, 
                   c=[color], label=label, edgecolors='black', linewidth=0.3)
    
    ax4.set_xlabel('Normalized Width', fontsize=11, fontweight='bold')
    ax4.set_ylabel('Normalized Height', fontsize=11, fontweight='bold')
    ax4.set_title('Object Width-Height Distribution by Category', fontsize=13, fontweight='bold')
    ax4.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=8)
    ax4.grid(True, alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '04_size_distribution.png'), bbox_inches='tight')
    plt.close()

def plot_area_distribution(areas, category_names, output_dir):
    """Plot object area distribution"""
    if not areas:
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Extract area data
    area_values = [a[0] for a in areas]
    
    # 1. Area distribution histogram (original)
    ax1 = axes[0, 0]
    ax1.hist(area_values, bins=50, color='lightgreen', edgecolor='black', alpha=0.7)
    ax1.set_xlabel('Area (pixels²)', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Frequency', fontsize=11, fontweight='bold')
    ax1.set_title('Object Area Distribution', fontsize=13, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    
    # 2. Area distribution histogram (logarithmic)
    ax2 = axes[0, 1]
    log_areas = [np.log10(a + 1) for a in area_values]
    ax2.hist(log_areas, bins=50, color='orange', edgecolor='black', alpha=0.7)
    ax2.set_xlabel('log10(Area + 1)', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Frequency', fontsize=11, fontweight='bold')
    ax2.set_title('Object Area Distribution (Log Scale)', fontsize=13, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    
    # 3. Area box plot by category
    ax3 = axes[1, 0]
    category_areas = defaultdict(list)
    for area, cat_id in areas:
        category_areas[cat_id].append(area)
    
    sorted_cats = sorted(category_areas.keys())
    area_data = [category_areas[cat_id] for cat_id in sorted_cats]
    labels = [category_names.get(cat_id, f'ID:{cat_id}') for cat_id in sorted_cats]
    
    bp = ax3.boxplot(area_data, labels=labels, patch_artist=True, vert=False)
    for patch, color in zip(bp['boxes'], plt.cm.Set3(np.linspace(0, 1, len(labels)))):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    ax3.set_xlabel('Area (pixels²)', fontsize=11, fontweight='bold')
    ax3.set_title('Object Area Distribution by Category (Box Plot)', fontsize=13, fontweight='bold')
    ax3.grid(axis='x', alpha=0.3, linestyle='--')
    
    # 4. Area classification statistics (small, medium, large)
    ax4 = axes[1, 1]
    
    # COCO standard: small(<32²), medium(32²~96²), large(>96²)
    small_threshold = 32 * 32
    medium_threshold = 96 * 96
    
    size_categories = {'Small\n(<32²)': 0, 'Medium\n(32²~96²)': 0, 'Large\n(>96²)': 0}
    for area in area_values:
        if area < small_threshold:
            size_categories['Small\n(<32²)'] += 1
        elif area < medium_threshold:
            size_categories['Medium\n(32²~96²)'] += 1
        else:
            size_categories['Large\n(>96²)'] += 1
    
    colors_size = ['#ff9999', '#66b3ff', '#99ff99']
    bars = ax4.bar(size_categories.keys(), size_categories.values(), 
                   color=colors_size, edgecolor='black', linewidth=1.5, alpha=0.8)
    ax4.set_ylabel('Number of Instances', fontsize=11, fontweight='bold')
    ax4.set_title('Object Size Classification Statistics (COCO Standard)', fontsize=13, fontweight='bold')
    ax4.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add values and percentages
    total = sum(size_categories.values())
    for bar, (label, count) in zip(bars, size_categories.items()):
        height = bar.get_height()
        percentage = (count / total * 100) if total > 0 else 0
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{count}\n({percentage:.1f}%)',
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '05_area_distribution.png'), bbox_inches='tight')
    plt.close()

def plot_aspect_ratio_distribution(aspect_ratios, category_names, output_dir):
    """Plot aspect ratio distribution"""
    if not aspect_ratios:
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Extract aspect ratio data (filter outliers)
    ratio_values = [r[0] for r in aspect_ratios if 0 < r[0] < 10]
    
    # 1. Aspect ratio distribution histogram
    ax1 = axes[0, 0]
    ax1.hist(ratio_values, bins=50, color='plum', edgecolor='black', alpha=0.7)
    ax1.set_xlabel('Aspect Ratio (Width/Height)', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Frequency', fontsize=11, fontweight='bold')
    ax1.set_title('Object Aspect Ratio Distribution', fontsize=13, fontweight='bold')
    ax1.axvline(1.0, color='red', linestyle='--', linewidth=2, label='Square (1:1)')
    ax1.axvline(np.median(ratio_values), color='green', linestyle='--', 
               linewidth=2, label=f'Median: {np.median(ratio_values):.2f}')
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    
    # 2. Aspect ratio distribution (log scale)
    ax2 = axes[0, 1]
    ax2.hist(ratio_values, bins=50, color='cyan', edgecolor='black', alpha=0.7)
    ax2.set_xlabel('Aspect Ratio (Width/Height)', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Frequency (Log)', fontsize=11, fontweight='bold')
    ax2.set_title('Object Aspect Ratio Distribution (Log Y-axis)', fontsize=13, fontweight='bold')
    ax2.set_yscale('log')
    ax2.axvline(1.0, color='red', linestyle='--', linewidth=2, label='Square')
    ax2.legend()
    ax2.grid(True, alpha=0.3, linestyle='--')
    
    # 3. Aspect ratio box plot by category
    ax3 = axes[1, 0]
    category_ratios = defaultdict(list)
    for ratio, cat_id in aspect_ratios:
        if 0 < ratio < 10:  # Filter outliers
            category_ratios[cat_id].append(ratio)
    
    sorted_cats = sorted(category_ratios.keys())
    ratio_data = [category_ratios[cat_id] for cat_id in sorted_cats]
    labels = [category_names.get(cat_id, f'ID:{cat_id}') for cat_id in sorted_cats]
    
    bp = ax3.boxplot(ratio_data, labels=labels, patch_artist=True)
    for patch, color in zip(bp['boxes'], plt.cm.Pastel1(np.linspace(0, 1, len(labels)))):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    ax3.set_ylabel('Aspect Ratio', fontsize=11, fontweight='bold')
    ax3.set_title('Object Aspect Ratio Distribution by Category', fontsize=13, fontweight='bold')
    ax3.axhline(1.0, color='red', linestyle='--', linewidth=1.5, alpha=0.5)
    ax3.grid(axis='y', alpha=0.3, linestyle='--')
    plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # 4. Aspect ratio classification statistics
    ax4 = axes[1, 1]
    
    ratio_categories = {
        'Tall\n(<0.5)': 0,
        'Slightly Tall\n(0.5~0.8)': 0,
        'Square\n(0.8~1.2)': 0,
        'Slightly Wide\n(1.2~2.0)': 0,
        'Wide\n(>2.0)': 0
    }
    
    for ratio in ratio_values:
        if ratio < 0.5:
            ratio_categories['Tall\n(<0.5)'] += 1
        elif ratio < 0.8:
            ratio_categories['Slightly Tall\n(0.5~0.8)'] += 1
        elif ratio < 1.2:
            ratio_categories['Square\n(0.8~1.2)'] += 1
        elif ratio < 2.0:
            ratio_categories['Slightly Wide\n(1.2~2.0)'] += 1
        else:
            ratio_categories['Wide\n(>2.0)'] += 1
    
    colors_ratio = ['#ff6b6b', '#feca57', '#48dbfb', '#1dd1a1', '#ee5a6f']
    bars = ax4.bar(ratio_categories.keys(), ratio_categories.values(),
                   color=colors_ratio, edgecolor='black', linewidth=1.5, alpha=0.8)
    ax4.set_ylabel('Number of Instances', fontsize=11, fontweight='bold')
    ax4.set_title('Object Shape Classification Statistics', fontsize=13, fontweight='bold')
    ax4.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add values and percentages
    total = sum(ratio_categories.values())
    for bar, (label, count) in zip(bars, ratio_categories.items()):
        height = bar.get_height()
        percentage = (count / total * 100) if total > 0 else 0
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{count}\n({percentage:.1f}%)',
                ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '06_aspect_ratio_distribution.png'), bbox_inches='tight')
    plt.close()

def plot_category_statistics(category_details, category_names, output_dir):
    """Plot detailed statistics for each category"""
    if not category_details:
        return
    
    sorted_cats = sorted(category_details.keys())
    n_cats = len(sorted_cats)
    
    # Calculate statistics for each category
    stats_data = []
    for cat_id in sorted_cats:
        details = category_details[cat_id]
        if not details['widths']:
            continue
        
        stats_data.append({
            'name': category_names.get(cat_id, f'ID:{cat_id}'),
            'count': len(details['widths']),
            'avg_width': np.mean(details['widths']),
            'avg_height': np.mean(details['heights']),
            'avg_area': np.mean(details['areas']),
            'avg_aspect_ratio': np.mean(details['aspect_ratios'])
        })
    
    if not stats_data:
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(18, 12))
    
    names = [s['name'] for s in stats_data]
    
    # 1. Average width comparison
    ax1 = axes[0, 0]
    avg_widths = [s['avg_width'] for s in stats_data]
    bars1 = ax1.barh(range(len(names)), avg_widths, color=plt.cm.Blues(np.linspace(0.4, 0.9, len(names))),
                     edgecolor='black', linewidth=0.8)
    ax1.set_yticks(range(len(names)))
    ax1.set_yticklabels(names, fontsize=9)
    ax1.set_xlabel('Average Normalized Width', fontsize=11, fontweight='bold')
    ax1.set_title('Average Width by Category', fontsize=13, fontweight='bold')
    ax1.grid(axis='x', alpha=0.3, linestyle='--')
    
    for i, (bar, val) in enumerate(zip(bars1, avg_widths)):
        ax1.text(val, i, f' {val:.3f}', va='center', fontsize=8)
    
    # 2. Average height comparison
    ax2 = axes[0, 1]
    avg_heights = [s['avg_height'] for s in stats_data]
    bars2 = ax2.barh(range(len(names)), avg_heights, color=plt.cm.Oranges(np.linspace(0.4, 0.9, len(names))),
                     edgecolor='black', linewidth=0.8)
    ax2.set_yticks(range(len(names)))
    ax2.set_yticklabels(names, fontsize=9)
    ax2.set_xlabel('Average Normalized Height', fontsize=11, fontweight='bold')
    ax2.set_title('Average Height by Category', fontsize=13, fontweight='bold')
    ax2.grid(axis='x', alpha=0.3, linestyle='--')
    
    for i, (bar, val) in enumerate(zip(bars2, avg_heights)):
        ax2.text(val, i, f' {val:.3f}', va='center', fontsize=8)
    
    # 3. Average area comparison
    ax3 = axes[1, 0]
    avg_areas = [s['avg_area'] for s in stats_data]
    bars3 = ax3.barh(range(len(names)), avg_areas, color=plt.cm.Greens(np.linspace(0.4, 0.9, len(names))),
                     edgecolor='black', linewidth=0.8)
    ax3.set_yticks(range(len(names)))
    ax3.set_yticklabels(names, fontsize=9)
    ax3.set_xlabel('Average Area (pixels²)', fontsize=11, fontweight='bold')
    ax3.set_title('Average Area by Category', fontsize=13, fontweight='bold')
    ax3.grid(axis='x', alpha=0.3, linestyle='--')
    
    for i, (bar, val) in enumerate(zip(bars3, avg_areas)):
        ax3.text(val, i, f' {val:.0f}', va='center', fontsize=8)
    
    # 4. Average aspect ratio comparison
    ax4 = axes[1, 1]
    avg_ratios = [s['avg_aspect_ratio'] for s in stats_data]
    bars4 = ax4.barh(range(len(names)), avg_ratios, color=plt.cm.Purples(np.linspace(0.4, 0.9, len(names))),
                     edgecolor='black', linewidth=0.8)
    ax4.set_yticks(range(len(names)))
    ax4.set_yticklabels(names, fontsize=9)
    ax4.set_xlabel('Average Aspect Ratio', fontsize=11, fontweight='bold')
    ax4.set_title('Average Aspect Ratio by Category', fontsize=13, fontweight='bold')
    ax4.axvline(1.0, color='red', linestyle='--', linewidth=2, alpha=0.5, label='Square')
    ax4.legend()
    ax4.grid(axis='x', alpha=0.3, linestyle='--')
    
    for i, (bar, val) in enumerate(zip(bars4, avg_ratios)):
        ax4.text(val, i, f' {val:.2f}', va='center', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '07_category_statistics.png'), bbox_inches='tight')
    plt.close()

def plot_cooccurrence_matrix(image_categories, category_names, output_dir):
    """Plot category co-occurrence matrix"""
    if not image_categories:
        return
    
    sorted_cats = sorted(category_names.keys())
    n_cats = len(sorted_cats)
    
    # Build co-occurrence matrix
    cooccurrence = np.zeros((n_cats, n_cats))
    
    for img_id, cats in image_categories.items():
        cats_list = list(cats)
        for i, cat1 in enumerate(cats_list):
            for cat2 in cats_list[i:]:
                idx1 = sorted_cats.index(cat1)
                idx2 = sorted_cats.index(cat2)
                cooccurrence[idx1, idx2] += 1
                if idx1 != idx2:
                    cooccurrence[idx2, idx1] += 1
    
    # Plot heatmap
    fig, ax = plt.subplots(figsize=(14, 12))
    
    labels = [category_names.get(cat_id, f'ID:{cat_id}') for cat_id in sorted_cats]
    
    im = ax.imshow(cooccurrence, cmap='YlOrRd', aspect='auto')
    
    # Set ticks
    ax.set_xticks(np.arange(n_cats))
    ax.set_yticks(np.arange(n_cats))
    ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=9)
    ax.set_yticklabels(labels, fontsize=9)
    
    # Add values
    for i in range(n_cats):
        for j in range(n_cats):
            value = int(cooccurrence[i, j])
            if value > 0:
                text_color = 'white' if cooccurrence[i, j] > cooccurrence.max() / 2 else 'black'
                ax.text(j, i, str(value), ha='center', va='center', 
                       color=text_color, fontsize=7, fontweight='bold')
    
    ax.set_title('Category Co-occurrence Matrix (Occurrences in Same Image)', fontsize=14, fontweight='bold', pad=15)
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Co-occurrence Count', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '08_cooccurrence_matrix.png'), bbox_inches='tight')
    plt.close()

def plot_summary_dashboard(result, output_dir):
    """Plot comprehensive statistics dashboard"""
    fig = plt.figure(figsize=(20, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    category_names = result['category_names']
    category_instances = result['category_instances']
    
    # 1. Basic statistics text
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.axis('off')
    
    stats_text = f"""
    Dataset Statistics Summary
    {'='*30}
    
    Total Images: {result['total_images']:,}
    Total Categories: {result['total_categories']}
    Total Annotations: {result['total_annotations']:,}
    Valid Annotations: {result['valid_annotations']:,}
    
    Avg Annotations per Image: {result['valid_annotations']/max(result['total_images'], 1):.2f}
    
    Top Categories by Instances:"""
    
    # Find top 3 categories with most annotations
    sorted_cats = sorted(category_instances.items(), key=lambda x: x[1], reverse=True)[:3]
    for i, (cat_id, count) in enumerate(sorted_cats, 1):
        cat_name = category_names.get(cat_id, f'ID:{cat_id}')
        stats_text += f"\n      {i}. {cat_name}: {count}"
    
    ax1.text(0.1, 0.9, stats_text, transform=ax1.transAxes, fontsize=11,
            verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    # 2. Top-10 categories
    ax2 = fig.add_subplot(gs[0, 1:])
    top_n = min(10, len(category_instances))
    sorted_items = sorted(category_instances.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    cat_ids = [item[0] for item in sorted_items]
    counts = [item[1] for item in sorted_items]
    labels = [category_names.get(cat_id, f'ID:{cat_id}') for cat_id in cat_ids]
    
    colors_top = plt.cm.viridis(np.linspace(0.2, 0.9, len(labels)))
    bars = ax2.barh(range(len(labels)), counts, color=colors_top, edgecolor='black', linewidth=1)
    ax2.set_yticks(range(len(labels)))
    ax2.set_yticklabels(labels, fontsize=10)
    ax2.set_xlabel('Number of Instances', fontsize=11, fontweight='bold')
    ax2.set_title(f'Top {top_n} Categories by Instance Count', fontsize=13, fontweight='bold')
    ax2.grid(axis='x', alpha=0.3, linestyle='--')
    
    for i, (bar, count) in enumerate(zip(bars, counts)):
        ax2.text(count, i, f' {count}', va='center', fontsize=9, fontweight='bold')
    
    # 3. Center point distribution
    ax3 = fig.add_subplot(gs[1, 0])
    center_points = result['center_points']
    if center_points:
        all_x = [p[0] for p in center_points]
        all_y = [p[1] for p in center_points]
        ax3.hexbin(all_x, all_y, gridsize=25, cmap='hot', mincnt=1)
        ax3.set_xlabel('X', fontsize=10, fontweight='bold')
        ax3.set_ylabel('Y', fontsize=10, fontweight='bold')
        ax3.set_title('Center Point Density', fontsize=12, fontweight='bold')
        ax3.set_xlim(0, 1)
        ax3.set_ylim(0, 1)
        ax3.invert_yaxis()
    
    # 4. Area distribution
    ax4 = fig.add_subplot(gs[1, 1])
    areas = result['areas']
    if areas:
        area_values = [a[0] for a in areas]
        ax4.hist(area_values, bins=40, color='lightgreen', edgecolor='black', alpha=0.7)
        ax4.set_xlabel('Area', fontsize=10, fontweight='bold')
        ax4.set_ylabel('Frequency', fontsize=10, fontweight='bold')
        ax4.set_title('Area Distribution', fontsize=12, fontweight='bold')
        ax4.grid(axis='y', alpha=0.3)
    
    # 5. Aspect ratio distribution
    ax5 = fig.add_subplot(gs[1, 2])
    aspect_ratios = result['aspect_ratios']
    if aspect_ratios:
        ratio_values = [r[0] for r in aspect_ratios if 0 < r[0] < 10]
        ax5.hist(ratio_values, bins=40, color='plum', edgecolor='black', alpha=0.7)
        ax5.set_xlabel('Aspect Ratio', fontsize=10, fontweight='bold')
        ax5.set_ylabel('Frequency', fontsize=10, fontweight='bold')
        ax5.set_title('Aspect Ratio Distribution', fontsize=12, fontweight='bold')
        ax5.axvline(1.0, color='red', linestyle='--', linewidth=2)
        ax5.grid(axis='y', alpha=0.3)
    
    # 6. Size classification
    ax6 = fig.add_subplot(gs[2, 0])
    if areas:
        area_values = [a[0] for a in areas]
        small_threshold = 32 * 32
        medium_threshold = 96 * 96
        
        size_cats = {'Small': 0, 'Medium': 0, 'Large': 0}
        for area in area_values:
            if area < small_threshold:
                size_cats['Small'] += 1
            elif area < medium_threshold:
                size_cats['Medium'] += 1
            else:
                size_cats['Large'] += 1
        
        colors_size = ['#ff9999', '#66b3ff', '#99ff99']
        wedges, texts, autotexts = ax6.pie(size_cats.values(), labels=size_cats.keys(),
                                            autopct='%1.1f%%', colors=colors_size,
                                            startangle=90, textprops={'fontsize': 10, 'fontweight': 'bold'})
        ax6.set_title('Object Size Classification', fontsize=12, fontweight='bold')
    
    # 7. Width vs Height scatter
    ax7 = fig.add_subplot(gs[2, 1])
    bbox_sizes = result['bbox_sizes']
    if bbox_sizes:
        widths = [s[0] for s in bbox_sizes]
        heights = [s[1] for s in bbox_sizes]
        ax7.scatter(widths, heights, alpha=0.4, s=15, c='purple', edgecolors='none')
        ax7.set_xlabel('Width', fontsize=10, fontweight='bold')
        ax7.set_ylabel('Height', fontsize=10, fontweight='bold')
        ax7.set_title('Width-Height Scatter Plot', fontsize=12, fontweight='bold')
        ax7.plot([0, 1], [0, 1], 'r--', alpha=0.5, linewidth=2)
        ax7.grid(True, alpha=0.3)
    
    # 8. Category balance
    ax8 = fig.add_subplot(gs[2, 2])
    if category_instances:
        counts_list = list(category_instances.values())
        ax8.boxplot([counts_list], vert=True, patch_artist=True,
                   boxprops=dict(facecolor='lightblue', alpha=0.7))
        ax8.set_ylabel('Instance Count', fontsize=10, fontweight='bold')
        ax8.set_title('Category Balance', fontsize=12, fontweight='bold')
        ax8.set_xticklabels(['All Categories'])
        ax8.grid(axis='y', alpha=0.3)
        
        # Add statistics info
        stats_info = f'Mean: {np.mean(counts_list):.1f}\nMedian: {np.median(counts_list):.1f}'
        ax8.text(0.95, 0.95, stats_info, transform=ax8.transAxes,
                fontsize=9, verticalalignment='top', horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))
    
    plt.suptitle('COCO Dataset Comprehensive Analysis Dashboard', fontsize=16, fontweight='bold', y=0.995)
    plt.savefig(os.path.join(output_dir, '09_summary_dashboard.png'), bbox_inches='tight')
    plt.close()

def main():
    """
    主函数，处理用户输入的文件路径
    """
    print("=" * 60)
    print("COCO标签统计与可视化程序 v2.0")
    print("=" * 60)
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        json_file_path = sys.argv[1]
    else:
        # 交互式输入
        json_file_path = input("请输入COCO JSON文件路径: ").strip()
    
    # 如果路径被引号包围，去除引号
    if json_file_path.startswith('"') and json_file_path.endswith('"'):
        json_file_path = json_file_path[1:-1]
    elif json_file_path.startswith("'") and json_file_path.endswith("'"):
        json_file_path = json_file_path[1:-1]
    
    print(f"\n正在分析文件: {json_file_path}")
    print("=" * 60)
    
    # 分析文件
    result = analyze_coco_annotations(json_file_path, visualize=True)
    
    if result:
        print("\n" + "=" * 60)
        print("✅ 分析完成！")
        print("=" * 60)
    else:
        print("\n❌ 分析失败，请检查文件路径和格式。")

if __name__ == "__main__":
    main()