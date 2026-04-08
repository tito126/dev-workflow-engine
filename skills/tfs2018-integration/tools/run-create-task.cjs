#!/usr/bin/env node
/**
 * 创建 TFS 任务
 */

const azureDevOps = require('azure-devops-node-api');
const fs = require('fs');
const path = require('path');

// 配置文件路径
const configPath = path.join(__dirname, '../config/tfs-config.json');

// 服务器配置
const COLLECTIONS = {
  'WINNING-6.0': {
    url: 'http://tfs2018-web.winning.com.cn:8080/tfs/WINNING-6.0',
    description: '主集合'
  }
};

// 加载配置
function loadConfig() {
  const config = fs.readFileSync(configPath, 'utf-8');
  return JSON.parse(config);
}

// TFS 客户端类
class TFSClient {
  constructor(collectionName = null) {
    const config = loadConfig();
    const targetCollection = collectionName || config.defaultCollection || 'WINNING-6.0';
    this.collectionName = targetCollection;
    this.serverUrl = COLLECTIONS[targetCollection]?.url || config.serverUrl;
    this.authHandler = azureDevOps.getPersonalAccessTokenHandler(config.pat);
    this.connection = new azureDevOps.WebApi(this.serverUrl, this.authHandler);
    this.witApi = null;
  }

  async getWorkItemApi() {
    if (!this.witApi) {
      this.witApi = await this.connection.getWorkItemTrackingApi();
    }
    return this.witApi;
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
}

async function main() {
  const collectionName = 'WINNING-6.0';
  const projectName = 'WiNEX-Inpatient-2';
  const parentId = 1538495;
  const workItemType = 'Task';
  const title = '[AI后端] 出院通知单增加日间手术患者标志数据';

  console.log(`正在创建任务...`);
  console.log(`  集合: ${collectionName}`);
  console.log(`  项目: ${projectName}`);
  console.log(`  父需求: ${parentId}`);
  console.log(`  类型: ${workItemType}`);
  console.log(`  标题: ${title}`);
  
  const client = new TFSClient(collectionName);
  
  try {
    const workItem = await client.createWorkItem(projectName, workItemType, {
      title: title,
      description: '',
      parentId: parentId
    });
    console.log('✓ 任务创建成功!');
    console.log(`  任务ID: ${workItem.id}`);
    console.log(`  标题: ${workItem.fields['System.Title']}`);
    console.log(`  状态: ${workItem.fields['System.State']}`);
    console.log(`  项目: ${workItem.fields['System.TeamProject']}`);
  } catch (error) {
    console.error('✗ 创建任务失败:', error.message);
    if (error.response) {
      console.error('  详细错误:', JSON.stringify(error.response, null, 2));
    }
    process.exit(1);
  }
}

main();
