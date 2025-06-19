﻿# 🛡️ SecureScout - 全功能Web安全检测平台

![系统运行截图](SecureScout/frontend/imgs/image.png)

<div align="center">

![SecureScout Logo](https://img.shields.io/badge/SecureScout-Web安全检测平台-blue?style=for-the-badge)

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Vue.js](https://img.shields.io/badge/Frontend-Vue.js-4FC08D?style=flat-square&logo=vue.js)](https://vuejs.org/)
[![Element Plus](https://img.shields.io/badge/UI-Element_Plus-409EFF?style=flat-square&logo=element)](https://element-plus.org/)
[![Tailwind CSS](https://img.shields.io/badge/CSS-Tailwind-38B2AC?style=flat-square&logo=tailwind-css)](https://tailwindcss.com/)
[![Chart.js](https://img.shields.io/badge/Charts-Chart.js-FF6384?style=flat-square&logo=chart.js)](https://www.chartjs.org/)

</div>

SecureScout是一款功能强大的Web安全检测工具，提供美观的浅色主题前端界面和强大的后端扫描功能。它可以帮助你检测网站中的常见安全漏洞，包括SQL注入、XSS跨站脚本、CSRF跨站请求伪造和文件上传漏洞等。

> 🔍 **安全扫描 · 漏洞分析 · 安全评分 · 修复建议**

## ✨ 功能特点

| 🌟 特性 | 📝 描述 |
|---------|--------|
| 🎨 **美观的用户界面** | 现代化浅色主题设计，数据可视化仪表盘，直观易用 |
| 🚀 **强大的扫描引擎** | 支持SQL注入、XSS、CSRF、文件上传等多种常见Web安全漏洞检测 |
| ⚡ **异步任务处理** | 支持并行处理多个扫描任务，高效完成扫描工作 |
| 📊 **详细的报告** | 提供可视化扫描结果和安全建议，包括漏洞分布、安全评分等 |
| ⚙️ **自定义配置** | 允许用户自定义扫描参数和规则，灵活应对不同场景 |
| 📱 **响应式设计** | 完美支持桌面端和移动端，随时随地进行安全检测 |


## 🔧 技术栈

### 🖥️ 后端
- **FastAPI**: 快速高效的API框架
- **aiohttp**: 异步HTTP客户端/服务器
- **BeautifulSoup4**: HTML解析库
- **Uvicorn**: ASGI服务器

### 🎨 前端
- **Vue 3**: 渐进式JavaScript框架
- **Vite**: 现代前端构建工具
- **Element Plus**: UI组件库
- **Tailwind CSS**: 实用优先的CSS框架
- **Chart.js**: 数据可视化库

## 🚀 快速开始

### 📋 环境要求

- Python 3.8+
- Node.js 16+
- npm 8+

### 📥 安装步骤

1. **进入项目仓库**

```bash
cd SecureScout
```

2. **安装后端依赖**

```bash
cd backend
pip install -r requirements.txt
```

3. **安装前端依赖**

```bash
cd frontend
npm install
npm run dev
```

### ▶️ 运行应用

#### 🪟 Windows用户 - 一键启动

只需要双击项目根目录中的 `start.bat` 文件，即可同时启动前端和后端服务！启动脚本会自动:

- ✅ 检查环境依赖是否满足
- ✅ 启动后端API服务
- ✅ 启动前端开发服务器
- ✅ 在浏览器中打开应用

#### 🖱️ 手动启动

1. **启动后端服务**

```bash
cd backend
python run.py
```

2. **启动前端服务**

```bash
cd frontend
npm run dev
```

3. **在浏览器中访问前端页面**

```
http://localhost:3000
```

## 📚 使用指南

### 🏠 仪表盘

仪表盘提供了系统的整体安全状况概览：

- 安全评分和趋势分析
- 已发现漏洞的数量和分布情况
- 最近扫描的记录和结果
- 安全建议和快速操作入口

### 🔍 扫描中心

扫描中心是进行安全检测的核心功能区：

1. 输入目标网站URL
2. 选择扫描模式（快速/标准/深度）
3. 配置扫描参数（并发度、超时设置等）
4. 启动扫描并实时查看进度
5. 扫描完成后查看结果概要

### 📊 报告中心

报告中心提供详细的漏洞分析和安全评估：

- 漏洞类型分布和风险等级
- 详细的漏洞描述和复现步骤
- 修复建议和参考资料
- 报告导出功能（PDF/HTML）

### ⚙️ 设置中心

设置中心允许自定义系统配置：

- 扫描规则和参数调整
- 漏洞库更新
- 通知设置
- 系统偏好设置

