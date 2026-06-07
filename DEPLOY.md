# Streamlit Cloud 部署指南（方案 C）

部署后应用运行在云端，**你的电脑关机也不影响访问**。手机、平板、电脑用浏览器打开链接即可。

## 一、准备 GitHub 仓库

1. 登录 [GitHub](https://github.com) 并新建仓库（例如 `LotteryApp`），选 **Public**（Streamlit 免费版需公开仓库）。
2. 在本项目目录打开终端，执行：

```bat
cd f:\Dev_LotteryApp
git init
git add .
git commit -m "准备 Streamlit Cloud 部署"
git branch -M main
git remote add origin https://github.com/你的用户名/LotteryApp.git
git push -u origin main
```

> 若 GitHub 要求登录，按提示使用 Personal Access Token 作为密码。

## 二、部署到 Streamlit Community Cloud

1. 打开 [share.streamlit.io](https://share.streamlit.io)，用 GitHub 账号登录。
2. 点击 **Create app**。
3. 填写：
   - **Repository**：选择刚推送的仓库
   - **Branch**：`main`
   - **Main file path**：`app.py`
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
