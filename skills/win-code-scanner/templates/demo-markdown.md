# SMS-医保日志 代码扫描报告

## 📋 扫描概览

| 项目 | 值 |
|------|----|
| 仓库 | SMS-医保日志 |
Git URL | http://tfs2018-web.winning.com.cn:8080/tfs/WN_HIS/His_Service/_git/winning-mis-log |
| 分支 | master |
| 批次进度 | 5/8 批 (用户提前终止) |
| 已扫描文件 | 500 / 767 (65.2%) |
| 耗时 | 207 秒 |
| Token 消耗 | 138,784 (72,076 输入 + 64,000 缓存 + 2,708 输出) |


## 问题统计

| 严重程度 | 数量 |
|----------|------|
| 严重 | 1 |
| 警告 | 45 |
| 提示 | 5 |
| **总计** | **51** |


## 完整问题列表


### QUAL-B011-4

**风险等级**: 🔴 high

**问题类别**: 代码质量

**影响范围**: 7 处

**涉及文件**:
- `winning-log-main/src/main/java/com/winning/mis/tasks/CleanLogDataTaskRunner.java`: 第 81, 83, 85, 106, 108 行
- `winning-log-main/src/main/java/com/winning/mis/service/MgrLogServiceImpl.java`: 第 74, 118 行

**修复步骤**:
1. 识别并定位所有触发 QUAL-B011-4 规则的代码
2. 根据修复建议进行修改（见代码示例）
3. 添加必要的单元测试验证修复

**代码示例**:

❌ **修改前**:
```java
72: return new String(Files.readAllBytes(Paths.get(mgrLogParam.getFilePath())), StandardCharsets.UTF_8);
73: } catch (IOException e) {
>>> 74: e.printStackTrace();
75: }
```

✅ **修改后**:
```java
使用printStackTrace打印异常堆栈,高并发环境下会影响IO性能,且不利于日志集中管理
```

**原理说明**: 使用printStackTrace打印异常堆栈,高并发环境下会影响IO性能,且不利于日志集中管理

### SEC-B001-5

**风险等级**: 🔴 high

**问题类别**: 安全规范

**影响范围**: 2 处

**涉及文件**:
- `winning-log-main/src/main/java/com/winning/mis/controller/MgrLogController.java`: 第 85, 88 行

**修复步骤**:
1. 识别并定位所有触发 SEC-B001-5 规则的代码
2. 根据修复建议进行修改（见代码示例）
3. 添加必要的单元测试验证修复

**代码示例**:

❌ **修改前**:
```java
82: String rootDir = System.getProperty("user.dir");
83: String filePath = mgrLogParam.getFilePath();
84: if (filePath.endsWith(".log")) {
>>> 85: mgrLogParam.setFilePath(rootDir + File.separator + filePath);
86: return mgrLogService.details(mgrLogParam);
```

✅ **修改后**:
```java
直接使用用户输入的filePath参数拼接文件路径,未进行路径规范化验证,存在路径遍历漏洞风险,攻击者可通过../访问任意文件
```

**原理说明**: 直接使用用户输入的filePath参数拼接文件路径,未进行路径规范化验证,存在路径遍历漏洞风险,攻击者可通过../访问任意文件
