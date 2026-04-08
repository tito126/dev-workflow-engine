#!/usr/bin/env node
/**
 * TFS 2018 Client Wrapper
 * 卫宁健康 WINNING-6.0 团队
 *
 * 用于与 TFS 2018 服务器交互的客户端封装
 * 配置文件: ./config/tfs-config.json
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import azureDevOps from 'azure-devops-node-api';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 服务器配置（内置）
const DEFAULT_SERVER_URL = 'http://tfs2018-web.winning.com.cn:8080/tfs/WINNING-6.0';

// 内置项目列表
const PROJECTS = {
  // WINNING-6.0 集合
  'OA4.0': '4150312b-3a53-4da7-a8a7-e2bfe7fd970f',
  'win-cloud': 'b46e3a4d-0b96-4d7b-aa4a-216121a1ef73',
  'WiNEX-Copilot': 'a3f67cbb-d375-4a58-a6c8-da448150c495',
  '售前演示': 'ddbd09b1-59ea-420d-843d-2f70ef9aa8e8',
  'WiNEX-DCP': 'f4e79b7d-13e6-4e47-9a17-570d72d4f6ef',
  'W.in-DEMO': 'fa4a1591-32d3-4e3f-82c2-761005d119a2',
  'WiNEX-PatientInterests': '6a84d2a9-b5ce-44e5-bce0-171ad6cd96e1',
  'W.in-MVP': '8c3c22dc-6d35-49b5-8589-3375adb60a84',
  'WiNEX-MDM': 'aa8c3418-9ec5-4c9e-8209-e229aeda3cfa',
  'HUMANITY': '595b77d4-6f9a-46cf-9aeb-ea2afdef59d6',
  'WiNEX-Cloud': 'd4361d76-6ff9-4fc3-851c-536d9305c40c',
  'WiNEX-MiddlePlatform': '8ef8a81d-59bd-455e-a86c-2687ba9b6e03',
  'WiNEX-Inpatient-2': 'fa2bf9fc-fdc9-4167-ae72-feef8525e1f5',
  'WiNEX-Outpatient': 'e17bb6a1-2677-4695-8202-c3c296bbd05c',
  'WiNEX-General': '250f7599-5c8c-4e93-892c-71157224ae73',
  'WiNEX-Integration': '7c4d1061-6885-4c24-8096-1e1fc9795432',
  'MiddlePlatform': '5c6e7482-f12f-418d-8994-bc5aeaea75a8',
  'WiNEX-CaseHistory': '739645d0-5770-4efc-98d3-33c98e749837',
  'Public Query': 'bad35cc1-f0d6-4f80-8ba0-6f166b3ef6be',
  'WiNEX_WXP': '89f17307-4986-4251-a04f-e534f9a1b99d',
  'UED': '58e8e9b0-5975-48d2-af2d-2719222c7ff0',
  'WiNEX-Inpatient': '9e4a971d-4027-4c9a-b55b-f0b74487afb5',
  'WiNEX-Triage': 'af9ab1c7-72ef-42cf-91a3-ef771be43f5a',
  'WiNEX-Emergency': '5f498025-58dd-4ba0-8137-3fc962e1acaf',
  'WiNEX-Management': 'e92e726a-8dbe-4385-998f-58182a4ddb1c',
  'WiNEX-Taikang': 'af798a82-646e-467a-8f90-8f3b2c9c39a4',
  'WiNEX-BasicInfoService': '7dfa9b49-818c-4765-8aae-aec1304af4e9',
  'WiNEX-Specialized': '8f70e3be-75e3-4969-a3fb-93481dc2c589',
  'WINEX-ConfigManage': '18eb3c40-2667-435f-80df-51ce43b24935',
  'WiNEX-HospitalAdministration': '6dcd7f28-99b5-4f43-8877-82230e999906',
  'WiNEX-MY': '6cdb1969-bbbc-4ea2-818a-ae29389df42e',

  // WN_PH-Platform 集合
  'WiNEX-Platform': 'c47f9976-e1eb-46a6-b09d-5273cfb0ebbb',
  'WIP-DevOps': 'd1d28d68-3d7d-4250-9db4-0e96b57e4cf8',
  'WIP-Gateway': '9d6fc5ab-a07f-4394-9c95-cf6b54c20a32',
  'WIP-Auth': '6b3f6e9d-9a7e-4b29-84d2-236ee3bb0663',
  'WIP-BaseData': '88f6cfa7-1b53-4b60-aa8e-84d41e79cc7e',
  'WIP-Config': 'f9a2b5c8-1a33-4d75-b0f1-3c7f4a1c6d1e',
  'WIP-Interface': 'c9d4e6f8-2b45-4c89-a312-d8e9f3c8b4a7',
  'WIP-Workflow': 'e7b5c7d9-3c56-4d9e-b023-f9e0a4d5c6b8',

  // WN_TECH 集合
  'BIS60': '1d989ffb-59c3-487c-9d09-c0b6362d3a40',
  'UED_TECH': 'f286da57-ca5d-4525-b66d-bf21ff2ed66d',
  'LIS60': '95ce4d88-d5cf-43dd-8c19-cfe57e51cc10',
  'MIIS': 'f596a6ab-558f-491c-8ce5-36f3d908c77f',
  'PACSPLUS_PEM_CLoudView': 'ddd08d7f-71c4-4578-80f5-3440891440a5',
  'TechBookCenter': '748161b2-80d5-48a3-94f3-576b8bc7ea8d',
  'HDIS': 'c7dabbab-5a27-4f8d-b7f3-241116ccb4fc',
  'MIIS_APPLYSHEET': '36b0ae9d-3d92-482c-b99a-c4b5ec5fe0b2',
  'PACS_Viewer': '6cc17d90-ab03-4223-82f3-17563f858bff',
  'COMMON_WJZ': '222b5054-73b7-42f8-bca0-836645c65489',
  'MIIS_BL': 'a48f079b-d20f-4268-a274-a3c1fdcff424',
  'PACSPLUS_Platform': '24291c93-f7e3-4354-bff4-3186a3afab34',
  'HLE': 'aa17466a-99d3-4a4e-a210-d4711b6ecd0d',
  'LIS60_KS': '3dff956f-3f7f-439b-b619-fc121fd6ad38',
  'MIIS_RMC': '7d5e640d-4168-4274-bf3a-344b0f1d70f2',
  'LIS60_WSW': 'd0053b6d-a8ce-4a85-acf9-68b6e065b8d0',
  'PACS_DICOMServer': 'e6101d04-72af-4dd0-855a-89b41b485be1',
  'LIS60_ZK': '20f22ad0-de5c-4904-911c-cb5e64a2efe1',
  'LIS60_LJ': 'c1f6b664-8684-4a87-aa92-7ef982854e5f',
  'LIS60_CG': 'a31c733c-0b73-48d4-9d77-ef5836a26925',
  'CLOUD_RIS': '7e334cd2-6cda-4d53-aaf5-5a68e09ab507',
  'LIS50': '400a0e87-6fab-430b-b488-7f101c994d70',
  'BIS60_SQD': 'c9482856-4442-44f3-8f4c-dfe4ea3e5f91',
  'WiNEX_PACS': '08817ae4-e290-482b-9271-9a20d003409e',
  'COMMON_FRAME': 'ff925c08-2aa3-4a41-aae3-a52ac3dfe0c9',
  'COMMON_WEBREPORT': '8c7489ef-8b3d-4c29-b013-791d793fa6b7',

  // wn_his 集合
  'EAHis': '202b20c2-d536-491f-80cb-75fee0acc1ba',
  'WinningReport': '72a40fda-43c2-40fe-9408-b32aa31419b1',
  'Framework_His': 'c63e4f11-006c-4f13-906d-4311d872138e',
  'DMS': '9154bc39-d8f8-45f4-abe6-c16289a39ea1',
  '传染病疫情监测': 'a9d19e50-f8a3-4f22-80d3-d878d53430ff',
  'WiNEX-HOCC': '97f8d3d0-c949-4ad4-8aef-d0b1de7322b0',
  'ACIS': '2969d9de-1d7a-410f-8d5c-bb39610f6a9d',
  '移动医生站': '7a3c28f2-861f-4046-b79e-6dede52a4d8f',
  'Framework': '76afaec7-fac6-404e-a758-1de96e5c7f72',
  'MDM_HIS': '0ada6b32-9023-4a07-aeb8-0ef0e2c6f021',
  'ConfigTest': '5ef9025e-fa6e-4166-83ce-33611a1d340e',
  'Manage': '5aff193f-ca33-483a-9d62-0a385bbd5e07',
  'CIS': '6330259e-25fe-40a8-949f-e75043742644',
  '体检管理': '995ee813-a3a2-4a87-a998-9dbd55c1bf50',
  'DRG': 'ebb866c7-b321-4e98-adaa-f48965a566d2',
  'ONDS': '5aa95afb-5cbb-4f96-b436-a8e82f3c6b8f',
  '智能导医机器人': 'edb39a45-4c76-4aa9-a5db-0ff197691e15',
  'EC': '65bfb1c1-c22f-442b-96e9-15ce474f475d'
};

// TFS 集合配置
const COLLECTIONS = {
  'WINNING-6.0': {
    url: 'http://tfs2018-web.winning.com.cn:8080/tfs/WINNING-6.0',
    projects: ['OA4.0', 'win-cloud', 'WiNEX-Copilot', '售前演示', 'WiNEX-DCP',
              'W.in-DEMO', 'WiNEX-PatientInterests', 'W.in-MVP', 'WiNEX-MDM',
              'HUMANITY', 'WiNEX-Cloud', 'WiNEX-MiddlePlatform', 'WiNEX-Inpatient-2',
              'WiNEX-Outpatient', 'WiNEX-General', 'WiNEX-Integration', 'MiddlePlatform',
              'WiNEX-CaseHistory', 'Public Query', 'WiNEX_WXP', 'UED',
              'WiNEX-Inpatient', 'WiNEX-Triage', 'WiNEX-Emergency', 'WiNEX-Management',
              'WiNEX-Taikang', 'WiNEX-BasicInfoService', 'WiNEX-Specialized',
              'WINEX-ConfigManage', 'WiNEX-HospitalAdministration', 'WiNEX-MY']
  },
  'WN_PH-Platform': {
    url: 'http://tfs2018-web.winning.com.cn:8080/tfs/WN_PH-Platform',
    projects: ['WiNEX-Platform', 'WIP-DevOps', 'WIP-Gateway', 'WIP-Auth',
              'WIP-BaseData', 'WIP-Config', 'WIP-Interface', 'WIP-Workflow']
  },
  'WN_TECH': {
    url: 'http://tfs2018-web.winning.com.cn:8080/tfs/WN_TECH',
    projects: ['BIS60', 'UED_TECH', 'LIS60', 'MIIS', 'PACSPLUS_PEM_CLoudView',
              'TechBookCenter', 'HDIS', 'MIIS_APPLYSHEET', 'PACS_Viewer',
              'COMMON_WJZ', 'MIIS_BL', 'PACSPLUS_Platform', 'HLE', 'LIS60_KS',
              'MIIS_RMC', 'LIS60_WSW', 'PACS_DICOMServer', 'LIS60_ZK',
              'LIS60_LJ', 'LIS60_CG', 'CLOUD_RIS', 'LIS50', 'BIS60_SQD',
              'WiNEX_PACS', 'COMMON_FRAME', 'COMMON_WEBREPORT']
  },
  'wn_his': {
    url: 'http://tfs2018-web.winning.com.cn:8080/tfs/wn_his',
    projects: ['EAHis', 'WinningReport', 'Framework_His', 'DMS', '传染病疫情监测',
              'WiNEX-HOCC', 'ACIS', '移动医生站', 'Framework', 'MDM_HIS',
              'ConfigTest', 'Manage', 'CIS', '体检管理', 'DRG', 'ONDS',
              '智能导医机器人', 'EC']
  }
};

// 项目到集合的映射
const PROJECT_TO_COLLECTION = {};
for (const [collectionName, collection] of Object.entries(COLLECTIONS)) {
  for (const projectName of collection.projects) {
    PROJECT_TO_COLLECTION[projectName] = collectionName;
  }
}

/**
 * 获取配置文件路径
 */
function getConfigPath() {
  return path.join(__dirname, '../config/tfs-config.json');
}

/**
 * 加载配置
 */
function loadConfig() {
  const configPath = getConfigPath();

  if (!fs.existsSync(configPath)) {
    console.error('配置文件不存在，请先运行配置命令');
    console.error('配置文件路径: ' + configPath);
    console.error('\n配置方法:');
    console.error('1. 打开 TFS 2018 Web 页面');
    console.error('2. 点击头像 -> 安全 -> 个人访问令牌');
    console.error('3. 创建新令牌，复制令牌字符串');
    throw new Error('配置文件不存在');
  }

  const configContent = fs.readFileSync(configPath, 'utf-8');
  const config = JSON.parse(configContent);

  return {
    serverUrl: config.serverUrl || DEFAULT_SERVER_URL,
    pat: config.pat,
    defaultCollection: config.defaultCollection || 'WINNING-6.0'
  };
}

/**
 * 保存配置
 */
function saveConfig(serverUrl, pat, defaultCollection = null) {
  const configPath = getConfigPath();
  const configDir = path.dirname(configPath);

  // 确保目录存在
  if (!fs.existsSync(configDir)) {
    fs.mkdirSync(configDir, { recursive: true });
  }

  const config = {
    serverUrl: serverUrl || DEFAULT_SERVER_URL,
    pat: pat
  };

  // 只有在明确指定时才添加 defaultCollection
  if (defaultCollection) {
    config.defaultCollection = defaultCollection;
  }

  fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
  console.log('配置已保存到:', configPath);
}

/**
 * 保存默认集合
 */
function saveDefaultCollection(collectionName) {
  const configPath = getConfigPath();
  const configContent = fs.readFileSync(configPath, 'utf-8');
  const config = JSON.parse(configContent);

  config.defaultCollection = collectionName;
  fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
}

/**
 * 解析项目名称，返回项目 ID 和所属集合
 * @param {string} projectName - 项目名称
 * @returns {object} { projectId, collectionName, collectionUrl }
 */
function resolveProject(projectName) {
  const projectId = PROJECTS[projectName];

  if (!projectId) {
    return null;
  }

  // 查找项目所属的集合
  const collectionName = PROJECT_TO_COLLECTION[projectName];
  const collection = COLLECTIONS[collectionName];

  return {
    projectId,
    collectionName,
    collectionUrl: collection?.url
  };
}

/**
 * 格式化日期为 WIQL 格式
 */
function formatDateForWIQL(date) {
  return date.toISOString();
}

/**
 * 延迟函数
 */
function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * TFS 客户端类
 */
class TFSClient {
  // 重试配置
  static MAX_RETRIES = 3;
  static RETRY_DELAY = 1000; // 1秒
  static RETRY_DELAY_MULTIPLIER = 2; // 指数退避

  constructor(collectionName = null) {
    const config = loadConfig();
    // 使用指定的集合或默认集合
    const targetCollection = collectionName || config.defaultCollection || 'WINNING-6.0';
    this.collectionName = targetCollection;
    this.serverUrl = COLLECTIONS[targetCollection]?.url || config.serverUrl;
    this.authHandler = azureDevOps.getPersonalAccessTokenHandler(config.pat);
    this.connection = new azureDevOps.WebApi(this.serverUrl, this.authHandler);
    this.witApi = null;
    this.gitApi = null;
  }

  /**
   * 通用重试包装器
   * @param {Function} fn - 要执行的异步函数
   * @param {string} operationName - 操作名称（用于日志）
   * @param {number} maxRetries - 最大重试次数
   * @returns {Promise<any>}
   */
  async withRetry(fn, operationName = 'API调用', maxRetries = TFSClient.MAX_RETRIES) {
    let lastError;
    let delayMs = TFSClient.RETRY_DELAY;

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        return await fn();
      } catch (error) {
        lastError = error;

        // 判断是否为可重试的错误（网络错误、超时、5xx 服务器错误等）
        const isRetryable = this.isRetryableError(error);

        if (attempt < maxRetries && isRetryable) {
          console.error(`[${operationName}] 第 ${attempt}/${maxRetries} 次尝试失败: ${error.message}`);
          console.error(`  → ${delayMs}ms 后重试...`);
          await delay(delayMs);
          delayMs *= TFSClient.RETRY_DELAY_MULTIPLIER; // 指数退避
        } else {
          // 不可重试或已达到最大重试次数
          break;
        }
      }
    }

    throw lastError;
  }

  /**
   * 判断错误是否可重试
   */
  isRetryableError(error) {
    // 网络错误
    if (error.code === 'ECONNRESET' ||
        error.code === 'ETIMEDOUT' ||
        error.code === 'ENOTFOUND' ||
        error.code === 'ECONNREFUSED' ||
        error.code === 'EHOSTUNREACH') {
      return true;
    }

    // HTTP 状态码错误
    if (error.statusCode) {
      // 5xx 服务器错误可重试
      if (error.statusCode >= 500 && error.statusCode < 600) {
        return true;
      }
      // 429 请求过多可重试
      if (error.statusCode === 429) {
        return true;
      }
    }

    // 超时错误
    if (error.message && (
      error.message.includes('timeout') ||
      error.message.includes('ETIMEDOUT') ||
      error.message.includes('socket hang up')
    )) {
      return true;
    }

    // 默认：对于未知错误也允许重试（TFS 服务不稳定）
    return true;
  }

  /**
   * 获取当前集合名称
   */
  getCollectionName() {
    return this.collectionName;
  }

  /**
   * 切换到指定集合
   */
  switchCollection(collectionName) {
    if (!COLLECTIONS[collectionName]) {
      throw new Error(`集合不存在: ${collectionName}。可用集合: ${Object.keys(COLLECTIONS).join(', ')}`);
    }

    this.collectionName = collectionName;
    this.serverUrl = COLLECTIONS[collectionName].url;
    this.connection = new azureDevOps.WebApi(this.serverUrl, this.authHandler);
    this.witApi = null;
    this.gitApi = null;
  }

  /**
   * 获取工作项跟踪 API
   */
  async getWorkItemApi() {
    if (!this.witApi) {
      this.witApi = await this.withRetry(
        () => this.connection.getWorkItemTrackingApi(),
        '获取工作项API'
      );
    }
    return this.witApi;
  }

  /**
   * 获取 Git API
   */
  async getGitApi() {
    if (!this.gitApi) {
      this.gitApi = await this.withRetry(
        () => this.connection.getGitApi(),
        '获取Git API'
      );
    }
    return this.gitApi;
  }

  /**
   * 按 ID 获取单个工作项
   * API: getWorkItem(id, fields, asOf, expand, project)
   */
  async getWorkItem(id, project = null) {
    return await this.withRetry(async () => {
      const witApi = await this.getWorkItemApi();
      return await witApi.getWorkItem(id, null, null, 'All', project);
    }, `获取工作项 ${id}`);
  }

  /**
   * 批量获取工作项
   * API: getWorkItems(ids, fields, asOf, expand, errorPolicy, project)
   */
  async getWorkItems(ids, project = null) {
    return await this.withRetry(async () => {
      const witApi = await this.getWorkItemApi();
      return await witApi.getWorkItems(ids, null, null, 'All', null, project);
    }, `批量获取工作项 ${ids.length}个`);
  }

  /**
   * 使用 WIQL 查询工作项
   */
  async queryWorkItems(wiql, project = null) {
    return await this.withRetry(async () => {
      const witApi = await this.getWorkItemApi();
      const queryResult = await witApi.queryByWiql({ query: wiql });

      if (!queryResult.workItems || queryResult.workItems.length === 0) {
        return [];
      }

      const ids = queryResult.workItems.map(wi => wi.id);
      return await witApi.getWorkItems(ids, null, null, 'All', null, project);
    }, 'WIQL查询工作项');
  }

  /**
   * 查询分配给我的活动任务
   */
  async getMyTasks(project = null) {
    let wiql = `
      SELECT [System.Id], [System.Title], [System.State], [System.AssignedTo]
      FROM WorkItems
      WHERE [System.WorkItemType] = 'Task'
      AND [System.State] <> 'Closed'
      AND [System.AssignedTo] = @me
    `;

    if (project) {
      wiql += ` AND [System.TeamProject] = '${project}'`;
    }

    wiql += ' ORDER BY [System.ChangedDate] DESC';

    return await this.queryWorkItems(wiql, project);
  }

  /**
   * 查询未关闭的 Bug
   */
  async getOpenBugs(project = null) {
    let wiql = `
      SELECT [System.Id], [System.Title], [System.State], [Microsoft.VSTS.Common.Severity]
      FROM WorkItems
      WHERE [System.WorkItemType] = 'Bug'
      AND [System.State] <> 'Closed'
    `;

    if (project) {
      wiql += ` AND [System.TeamProject] = '${project}'`;
    }

    wiql += ' ORDER BY [System.CreatedDate] DESC';

    return await this.queryWorkItems(wiql, project);
  }

  /**
   * 查询近期已解决/已关闭的工作项
   * @param {string} project - 项目名称，null表示所有项目
   * @param {number} days - 最近天数，默认7天
   * @param {string[]} states - 状态列表，默认 ['Resolved', 'Closed']
   */
  async getRecentResolvedWorkItems(project = null, days = 7, states = ['Resolved', 'Closed']) {
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - days);

    const startDateStr = formatDateForWIQL(startDate);
    const endDateStr = formatDateForWIQL(endDate);

    // TFS 2018 不支持 System.ClosedDate 和 System.ResolvedDate 字段
    // 使用 System.ChangedDate 进行日期过滤
    let wiql = `
      SELECT [System.Id], [System.Title], [System.WorkItemType],
             [System.State], [System.AssignedTo], [System.CreatedDate],
             [System.ChangedDate],
             [System.Description], [Microsoft.VSTS.Common.Priority],
             [Microsoft.VSTS.Common.Severity], [System.Reason]
      FROM WorkItems
      WHERE [System.State] IN (${states.map(s => `'${s}'`).join(', ')})
      AND [System.ChangedDate] >= '${startDateStr}'
      AND [System.ChangedDate] <= '${endDateStr}'
    `;

    if (project) {
      wiql += ` AND [System.TeamProject] = '${project}'`;
    }

    wiql += ' ORDER BY [System.ChangedDate] DESC';

    return await this.queryWorkItems(wiql, project);
  }

  /**
   * 创建工作项
   */
  async createWorkItem(project, workItemType, fields) {
    const witApi = await this.getWorkItemApi();
    const document = [
      { op: 'add', path: '/fields/System.Title', value: fields.title },
      { op: 'add', path: '/fields/System.Description', value: fields.description || '' }
    ];

    if (fields.assignedTo) {
      document.push({
        op: 'add',
        path: '/fields/System.AssignedTo',
        value: fields.assignedTo
      });
    }

    if (fields.priority !== undefined) {
      document.push({
        op: 'add',
        path: '/fields/Microsoft.VSTS.Common.Priority',
        value: String(fields.priority)
      });
    }

    if (fields.parentId) {
      document.push({
        op: 'add',
        path: '/relations/-',
        value: {
          rel: 'System.LinkTypes.Hierarchy-Reverse',
          url: `${this.serverUrl}/_apis/wit/workItems/${fields.parentId}`
        }
      });
    }

    return await witApi.createWorkItem(null, document, project, workItemType);
  }

  /**
   * 更新工作项状态
   */
  async updateWorkItemState(id, newState, comment = null) {
    const witApi = await this.getWorkItemApi();
    const document = [
      { op: 'replace', path: '/fields/System.State', value: newState }
    ];

    if (comment) {
      document.push({
        op: 'add',
        path: '/fields/System.History',
        value: comment
      });
    }

    return await witApi.updateWorkItem(null, document, id);
  }

  /**
   * 添加评论
   */
  async addComment(workItemId, comment) {
    const witApi = await this.getWorkItemApi();
    const document = [
      { op: 'add', path: '/fields/System.History', value: comment }
    ];
    return await witApi.updateWorkItem(null, document, workItemId);
  }

  /**
   * 获取项目的 Git 仓库列表
   */
  async getRepositories(project) {
    return await this.withRetry(async () => {
      const gitApi = await this.getGitApi();
      return await gitApi.getRepositories(project);
    }, `获取仓库列表 ${project}`);
  }

  /**
   * 获取最近的提交记录
   * @param {string} repositoryId - 仓库ID
   * @param {string} project - 项目名称
   * @param {number} top - 返回记录数，默认20
   * @param {number} days - 最近天数，用于客户端日期过滤，默认null（不过滤）
   */
  async getCommits(repositoryId, project, top = 20, days = null) {
    return await this.withRetry(async () => {
      const gitApi = await this.getGitApi();

      // TFS 2018 API 的日期参数可能不工作，需要先获取提交后在客户端过滤
      const commits = await gitApi.getCommits(
        repositoryId,
        project,
        null,  // branch
        null,  // requestorId
        null,  // itemPath
        top,
        null,  // skip
        null,  // includeLinks
        null,  // fromDate - TFS 2018 可能不支持
        null   // toDate - TFS 2018 可能不支持
      );

      // 如果指定了天数，在客户端进行日期过滤
      if (days) {
        const cutoffDate = new Date();
        cutoffDate.setDate(cutoffDate.getDate() - days);

        return commits.filter(commit => {
          const commitDate = new Date(commit.author?.date || commit.committer?.date);
          return commitDate >= cutoffDate;
        });
      }

      return commits;
    }, `获取提交 ${repositoryId?.substring(0,8)}...`);
  }

  /**
   * 检查提交的工作项关联
   */
  async checkCommitWorkItems(repositoryId, projectId, commitId) {
    return await this.withRetry(async () => {
      const gitApi = await this.getGitApi();
      const commit = await gitApi.getCommit(commitId, repositoryId, projectId);

      const workItems = commit.workItems || [];
      return {
        commitId: commitId,
        hasWorkItems: workItems.length > 0,
        workItemCount: workItems.length,
        workItems: workItems.map(wi => ({
          id: wi.id,
          url: wi.url
        }))
      };
    }, `检查提交关联 ${commitId?.substring(0,8)}`);
  }

  /**
   * 获取单个提交详情
   * @param {string} repositoryId - 仓库ID
   * @param {string} commitId - 提交ID
   * @param {string} project - 项目名称或ID
   * @returns {Promise<Object>} 提交详情
   */
  async getCommit(repositoryId, commitId, project = null) {
    return await this.withRetry(async () => {
      const gitApi = await this.getGitApi();
      return await gitApi.getCommit(commitId, repositoryId, project);
    }, `获取提交详情 ${commitId?.substring(0,8)}`);
  }

  /**
   * 获取提交的变更文件列表
   * @param {string} repositoryId - 仓库ID
   * @param {string} commitId - 提交ID
   * @param {string} project - 项目名称
   * @returns {Promise<Array>} 变更文件列表
   */
  async getCommitChanges(repositoryId, commitId, project = null) {
    return await this.withRetry(async () => {
      const gitApi = await this.getGitApi();
      const changes = await gitApi.getChanges(commitId, repositoryId, project);
      return changes.changes || [];
    }, `获取提交变更 ${commitId?.substring(0,8)}`);
  }

  /**
   * 解析 ArtifactLink URL 获取 Git 提交信息
   * URL 格式: vstfs:///Git/Commit/{projectId}%2f{repoId}%2f{commitId}
   * @param {string} artifactUrl - ArtifactLink URL
   * @returns {Object|null} { projectId, repoId, commitId } 或 null
   */
  parseArtifactLinkUrl(artifactUrl) {
    if (!artifactUrl || !artifactUrl.startsWith('vstfs:///Git/Commit/')) {
      return null;
    }

    try {
      // 提取编码后的部分
      const encodedPart = artifactUrl.replace('vstfs:///Git/Commit/', '');
      // URL 解码
      const decodedPart = decodeURIComponent(encodedPart);
      // 按 / 分割
      const parts = decodedPart.split('/');

      if (parts.length >= 3) {
        return {
          projectId: parts[0],
          repoId: parts[1],
          commitId: parts[2]
        };
      }
      return null;
    } catch (error) {
      console.error(`解析 ArtifactLink URL 失败: ${error.message}`);
      return null;
    }
  }

  /**
   * 从工作项的 ArtifactLink 关系中获取关联的 Git 提交
   * @param {Object} workItem - 工作项对象（包含 relations）
   * @returns {Promise<Array>} 提交详情列表
   */
  async getArtifactLinkedCommits(workItem) {
    const commits = [];

    if (!workItem.relations || workItem.relations.length === 0) {
      return commits;
    }

    // 筛选 ArtifactLink 类型的 Git 提交链接
    const gitCommitLinks = workItem.relations.filter(rel =>
      rel.rel === 'ArtifactLink' &&
      rel.url &&
      rel.url.startsWith('vstfs:///Git/Commit/')
    );

    for (const link of gitCommitLinks) {
      const parsed = this.parseArtifactLinkUrl(link.url);
      if (parsed) {
        try {
          const commit = await this.getCommit(parsed.repoId, parsed.commitId);
          if (commit) {
            commits.push({
              commitId: commit.commitId,
              comment: commit.comment,
              author: commit.author,
              committer: commit.committer,
              url: commit.url,
              projectId: parsed.projectId,
              repoId: parsed.repoId,
              source: 'ArtifactLink',
              linkedWorkItemId: workItem.id
            });
          }
        } catch (error) {
          console.error(`获取提交 ${parsed.commitId} 失败: ${error.message}`);
        }
      }
    }

    return commits;
  }

  /**
   * 获取项目 ID
   */
  getProjectId(projectName) {
    return PROJECTS[projectName];
  }

  /**
   * 获取所有项目列表
   */
  getProjects() {
    return { ...PROJECTS };
  }

  /**
   * 检查项目是否存在
   */
  hasProject(projectName) {
    return projectName in PROJECTS;
  }
}

/**
 * 查找项目所在的集合
 * @param {string} projectName - 项目名称
 * @returns {object|null} { collectionName, collectionUrl } 或 null
 */
export function findProjectCollection(projectName) {
  const result = resolveProject(projectName);
  if (result) {
    return {
      collectionName: result.collectionName,
      collectionUrl: result.collectionUrl
    };
  }
  return null;
}

/**
 * 获取所有集合信息
 */
export function getCollections() {
  return { ...COLLECTIONS };
}

/**
 * 获取默认集合名称
 */
export function getDefaultCollection() {
  const config = loadConfig();
  return config.defaultCollection || 'WINNING-6.0';
}

/**
 * 设置默认集合
 */
export function setDefaultCollection(collectionName) {
  if (!COLLECTIONS[collectionName]) {
    throw new Error(`集合不存在: ${collectionName}。可用集合: ${Object.keys(COLLECTIONS).join(', ')}`);
  }
  saveDefaultCollection(collectionName);
}

// 导出
export default TFSClient;
export { loadConfig, saveConfig, PROJECTS, COLLECTIONS, PROJECT_TO_COLLECTION };
