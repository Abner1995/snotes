# 配置appsettings.json

```json
"Authentication": {
  "SecretKey": "b28f1a6d8c1eac301db2ef745601948e59c0b5d7a40c29f5d0a2c7b6f3d3e8f5",
  "Issuer": "http://localhost:7301",
  "Audience": "webapi"
}
```

**在身份验证和授权领域，配置项 `"Authentication"` 包含的信息通常用于设置 JWT（JSON Web Token）的身份验证策略。以下是对配置项中各个字段的解释：**

## 配置项解释

1. **SecretKey:**
   * **用途**: 用于签名和验证 JWT 的密钥。
   * **描述**: 这是一个秘密字符串，用于加密 JWT 的签名部分。只有持有相同密钥的服务才能验证 JWT 的真实性。
   * **安全**: 这个密钥应该严格保密，不应泄露给未经授权的第三方。
2. **Issuer:**
   * **用途**: 标识 JWT 的签发者。
   * **描述**: 这是一个字符串，通常是一个 URL 或一个标识符，用于指示哪个系统或服务签发了 JWT。在这个例子中，JWT 由 `http://localhost:7301` 发行。
   * **验证**: 当客户端接收到 JWT 时，它可以检查 `issuer` 字段来确认 JWT 的来源是否可信。
3. **Audience**
   * **用途**: 标识 JWT 的接收者或目标系统。
   * **描述**: 这是一个字符串，通常也是一个 URL 或标识符，用于指示 JWT 是为哪个系统或服务生成的。在这个例子中，JWT 的受众是 `webapi`。
   * **验证**: 当 JWT 被发送到某个服务时，该服务可以检查 `audience` 字段来确认 JWT 是否是为自己生成的。
