# i志愿 考勤比对工具

本地运行的辅助工具：登录广东志愿者服务管理平台（www.gdzyz.cn）管理后台，
拉取「活动查询」中的活动，比对**参加人员名单**与**考勤记录**，
帮助管理员快速找出**未签到 / 未签退**的志愿者。

>  这是一个**本地工具**，数据只在你自己的电脑上处理，不上传到任何第三方。

##  功能特性

-  **活动列表**：拉取「活动查询」前 10 个活动，按开始时间排序
-  **考勤比对**：名单 vs 考勤，三态分类
  -  已签到 + 已签退
  -  已签到但未签退（橙色高亮）
  -  未签到（红色高亮）
-  **实时刷新**：签到时段内随时刷新单个活动，跟进最新签到/签退进度
-  **人员检索**：在活动中按姓名/手机号即时搜索，点击候选直接查看该人的
  签到/签退时间、服务时长等完整信息
-  **自动去重**：名单/考勤按唯一标识去重，防止接口重复返回导致人数虚高
-  **导出 Excel**：已签到已签退 / 已签到未签退 / 未签到 / 异常 / 汇总 五个工作表
-  **深色模式**：跟随系统自动切换
-  **界面风格**：对标 i志愿原后台（天蓝 `#41b8de` 主色 + Apple 风格设计）

##  快速开始

### 环境要求

- Windows 10/11
- Python 3.10 或更高（[下载](https://www.python.org/downloads/)，安装时勾选 *Add Python to PATH*）

### 安装与启动

```bash
# 1. 安装依赖（仅首次）
setup.bat

# 2. 启动工具（自动打开 http://localhost:8000）
start.bat
```

### 登录（仅需一次）

工具不保存账号密码，只使用浏览器中的登录凭证 Token（相当于登录状态）：

1. 用浏览器登录 `https://www.gdzyz.cn/admin/`（正常完成图形验证码 + 滑块）
2. 按 **F12** → **Console** → 输入以下命令回车：
   ```javascript
   decodeURIComponent(document.cookie.split('IZYZ_org_token=')[1].split(';')[0])
   ```
3. 复制输出，粘贴到工具右上角 **「粘贴 Token」** 框
4. Token 会保存在本地 `token.json`，下次启动免登录；过期后重新粘贴即可

详细步骤见 [LOGIN_GUIDE.md](LOGIN_GUIDE.md)。

##  技术栈

- 后端：Python + FastAPI + Uvicorn
- 数据：requests（调用 gdzyz 管理后台 API）、openpyxl（Excel 导出）
- 前端：原生 HTML/CSS/JS（无框架，零构建）

##  目录结构

```
├── start.bat          # 一键启动
├── setup.bat          # 首次环境安装
├── app.py             # FastAPI 后端
├── login.py           # 登录模块（Token 管理）
├── api_client.py      # gdzyz API 客户端（含去重工具）
├── compare.py         # 考勤比对逻辑（三态分类）
├── config.py          # 配置
├── requirements.txt   # Python 依赖
├── LOGIN_GUIDE.md     # 登录指南
└── static/            # 前端界面
```

##  安全与隐私

- 工具在本地运行，数据不离开你的电脑
- Token 等同于登录状态，`token.json` 已在 `.gitignore` 中排除，**切勿提交或外泄**
- 请勿在不可信的电脑上使用本工具
- 本工具仅调用你账号权限内的公开管理接口，不进行任何写操作之外的自动化行为

##  免责声明

本工具仅供**个人/组织内部管理辅助**使用，与广东志愿者平台官方无关。
请合理使用，遵守平台使用规范；因使用本工具产生的一切后果由使用者自行承担。
界面中的 i志愿 logo 版权归其平台所有。

##  License

MIT License — 详见 [LICENSE](LICENSE)。
