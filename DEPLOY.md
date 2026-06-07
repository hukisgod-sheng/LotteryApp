# Streamlit Cloud 部署指南（方案 C）

部署后应用运行在云端，**你的电脑关机也不影响访问**。手机、平板、电脑用浏览器打开链接即可。

## 权限与安全（重要）

### Streamlit ↔ GitHub 授权（你已完成的步骤）

在 Streamlit 连接 GitHub 时，建议：

| 选项 | 建议 |
|------|------|
| 仓库访问范围 | 选 **「Only select repositories / 仅选定仓库」** |
| 选定仓库 | 只勾选 **`ssq-lottery-sandbox`** |
| 私有仓库 | **不要**勾选「All repositories」，避免飞控等私有源码被 Streamlit 访问 |
| 公开仓库 | 本应用为娱乐学习用途，**Public 公开仓库即可**，无需开放私有库 |

Streamlit 默认只需读取**公开仓库**即可部署；不授予私有仓库权限**不影响**本项目的云端部署。

### 本地 GitHub CLI 授权（推送代码用，可选）

若运行 `一键部署到云端.bat`，会要求 `gh auth login`，请使用 **最小权限**：

```
gh auth login --scopes public_repo
```

- `public_repo`：仅能读写**公开**仓库，无法访问私有飞控仓库
- **不要**使用 `--scopes repo`（会包含全部私有仓库权限），除非你有其他需要

### 无需提供的权限

- 不需要把 GitHub 密码 / Token 发给任何人
- 不需要 Streamlit API Token（除非你要全自动 API 部署）
- 不需要开放 GitHub 账号的全部仓库权限

---

## 最快部署方式（推荐）

1. 双击项目根目录 **`一键部署到云端.bat`**
2. 若提示 GitHub 登录：浏览器打开后输入终端里的一次性验证码，授权 **public_repo**
3. 脚本会自动：新建独立仓库 `ssq-lottery-sandbox` → 推送代码 → 打开 Streamlit 部署页
4. 在 Streamlit 页面点击 **Deploy**，等待 2～5 分钟

独立仓库地址将是：`https://github.com/hukisgod-sheng/ssq-lottery-sandbox`（与飞控仓库完全分开）

---

## 一、手动推送到 GitHub（可选）

1. 登录 [GitHub](https://github.com) 并新建仓库 **`ssq-lottery-sandbox`**，选 **Public**。
2. 在本项目目录打开终端，执行：

```bat
cd f:\Dev_LotteryApp
git init
git add .
git commit -m "准备 Streamlit Cloud 部署"
git branch -M main
git remote add origin https://github.com/hukisgod-sheng/ssq-lottery-sandbox.git
git push -u origin main
```

> 若 GitHub 要求登录，按提示使用 Personal Access Token 作为密码。

## 二、部署到 Streamlit Community Cloud

1. 打开 [share.streamlit.io](https://share.streamlit.io)，用 GitHub 账号登录。
2. 点击 **Create app**。
3. 填写：
   - **Repository**：`hukisgod-sheng/ssq-lottery-sandbox`
   - **Branch**：`main`
   - **Main file path**：`app.py`

   或直接打开预填链接：

   `https://share.streamlit.io/deploy?repository=hukisgod-sheng/ssq-lottery-sandbox&branch=main&mainModule=app.py&subdomain=ssq-sandbox`
4. 点击 **Deploy**，等待 2～5 分钟。
5. 成功后得到类似 `https://lotteryapp-xxxx.streamlit.app` 的地址，发给他人即可使用。

## 三、更新版本

改完代码后：

```bat
git add .
git commit -m "更新说明"
git push
```

Streamlit Cloud 会自动重新部署（约 1～3 分钟）。

## 四、注意事项

| 项目 | 说明 |
|------|------|
| 休眠 | 免费版长期无人访问会休眠，再次打开需等待冷启动 |
| 历史数据 | 云端 `data/ssq_history.csv` 在重新部署后可能重置，用户可在「历史开奖」页重新拉取 |
| 免责声明 | 已固定在每页底部，部署后自动生效 |
| 隐私 | 免费版为公开应用；如需私有部署，需自建 VPS 或 Streamlit 付费方案 |

## 五、本地验证（部署前可选）

```bat
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

浏览器打开 `http://localhost:8501`，滚动到页面底部确认免责声明显示正常。
