# RAG PDF 系统 Demo 部署说明

## 部署目标

本部署用于实习/求职作品展示，是受控 Demo，不是开放生产 SaaS。

## 公网暴露面

- 前端页面：`https://your-domain.example`
- 后端 API：通过 Nginx 代理到 `/api/v1`

## 私有服务

以下服务不得直接暴露到公网：

- FastAPI 直连端口 `8000`
- MinIO `9000`、`9001`
- RabbitMQ `5672`、`15672`
- Redis `6379`
- Milvus `19530`、`9091`
- Flower `5555`

## Demo 约束

- 关闭公开注册。
- 提供一个受控 Demo 账号。
- 只使用无敏感信息的示例文档。
- 上传大小限制为 `10 MB`。
- 允许上传 `.pdf`、`.txt`、`.md`、`.docx`。
- DashScope API Key 只放在服务器环境变量。
- Demo 账号广泛分享后要轮换密码。

## 服务器清单

推荐最低配置：

- 2 vCPU
- 4 GB RAM 起步，Milvus 场景建议 8 GB
- 40 GB 磁盘
- Ubuntu 22.04 或 24.04
- 已安装 Docker 和 Docker Compose
- 域名 DNS A 记录指向服务器

防火墙：

- 允许 `22/tcp`，最好只允许你的 IP
- 允许 `80/tcp`
- 允许 `443/tcp`
- 拒绝公网直连 `8000`、`9000`、`9001`、`15672`、`19530`、`6379`、`5555`

## 部署命令

```bash
git clone <repo-url> ragPdfSystem
cd ragPdfSystem
cp .env.production.example .env.production
# 在服务器上编辑 .env.production，填入真实密钥和强密码。

cd frontend
npm ci
npm run build
cd ..

docker compose -f docker/docker-compose.prod.yml --env-file .env.production up -d --build
docker compose -f docker/docker-compose.prod.yml --env-file .env.production ps
```

预期：

- `nginx` 正常运行。
- `app` 正常运行。
- `worker` 正常运行。
- `redis`、`rabbitmq`、`minio`、`etcd`、`milvus-standalone` 正常运行。

## 创建 Demo 用户

```bash
export DEMO_USERNAME=demo
export DEMO_EMAIL=demo@example.com
export DEMO_PASSWORD=<strong-password>
python scripts/create_demo_user.py
```

## 分享前验证清单

```bash
curl -I https://your-domain.example
curl https://your-domain.example/api/v1/health
```

手动检查：

- Demo 账号可以登录。
- 公开注册已关闭。
- 未登录不能上传文件。
- 未登录不能访问存储接口。
- 未登录不能调用问答接口。
- 超过 `10 MB` 的文件会被拒绝。
- 不支持的文件类型会被拒绝。
- Demo 文档可以上传并处理完成。
- 知识库问答可以返回来源引用。
- 评估模块可以基于 Demo 数据运行。
- MinIO、RabbitMQ、Redis、Milvus、Flower 端口公网不可访问。
- 浏览器 DevTools 中看不到 DashScope API Key。
- `.env.production` 未被 Git 跟踪。
