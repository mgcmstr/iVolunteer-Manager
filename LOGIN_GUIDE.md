# 📖 登录指南

本工具**不保存你的账号密码**，只保存"登录凭证 Token"（相当于登录状态）。
所有数据只在你自己的电脑上处理，不上传到任何第三方。

## 环境准备（仅需一次）

- Windows + Python 3.10 或更高（`python --version` 检查）
- 没有 Python：到 https://www.python.org/downloads/ 安装，勾选 *Add Python to PATH*

```bash
# 首次安装依赖（需联网，约 2-3 分钟）
setup.bat

# 启动工具
start.bat   # 自动打开 http://localhost:8000
```

---

## 登录步骤（粘贴 Token，唯一登录方式）

**第 1 步**：用浏览器（Edge/Chrome）打开并登录 i志愿管理后台
```
https://www.gdzyz.cn/admin/
```
输入**你自己的组织账号密码**，正常完成图形验证码和滑块。

**第 2 步**：登录成功后，按 **F12** 打开开发者工具

**第 3 步**：点上方 **Console（控制台）** 标签

**第 4 步**：粘贴下面这一行，按回车：
```javascript
decodeURIComponent(document.cookie.split('IZYZ_org_token=')[1].split(';')[0])
```

**第 5 步**：会输出一串字符（Token），**鼠标选中 → 右键复制**

**第 6 步**：回到工具页面（http://localhost:8000），点右上角 **「粘贴 Token」**，
粘贴进去，点「保存 Token」

 完成！工具会自动验证 Token，有效则显示「● 已登录」，然后就能用了。

---

## 替代方法：从 Application 面板复制 Token

如果控制台命令报错（`Cannot read properties of undefined`），用这个方法：

1. F12 后点上方 **Application（应用）** 标签
2. 左侧展开 **Cookies** → 点 `https://www.gdzyz.cn`
3. 找到 **Name 为 `IZYZ_org_token`** 的一行
4. 双击它的 **Value** 列 → Ctrl+C 复制 → 粘贴到工具

---

## Token 过期了怎么办？

Token 有效期不确定（可能几小时到几天），过期后工具会显示「● Token 失效」。

处理：重新做一遍上面**登录步骤**（真实浏览器登录 → 复制新 Token → 粘贴），30 秒搞定。

---

## 安全须知（务必阅读）

1. **Token = 你的登录状态**。`token.json` 不要发给别人、不要提交到公开仓库
2. 工具只在本机运行，数据不上传第三方；请勿在不可信的电脑上使用
3. 每个使用者请用**自己组织的账号**登录（工具只显示你账号权限内的活动）
4. 若怀疑 Token 泄露：登录 i志愿官网 → 修改密码 → 旧的 Token 会失效
5. 离开电脑时建议删除 `token.json`（下次使用时重新粘贴）

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 控制台命令报错 | 用 Application 面板方法复制 Token（见上） |
| 粘贴后提示 Token 无效 | Token 已过期或复制不完整，重新获取粘贴 |
| 打开页面显示「后端未连接」 | 确认 start.bat 的黑窗口还开着，不要关 |
| 活动列表是空的 | 你的账号当前没有符合条件活动，或 Token 权限不足 |
| 端口 8000 被占用 | 关掉其他占用 8000 的程序，或联系管理员改端口 |
