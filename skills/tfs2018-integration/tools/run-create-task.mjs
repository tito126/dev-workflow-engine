#!/usr/bin/env node
/**
 * 创建 TFS 任务
 */

import { TFSClient } from './tfs-client.mjs';

async function main() {
  const collectionName = 'WINNING-6.0';
  const projectName = 'WiNEX-Inpatient-2';
  const parentId = 1538495;
  const workItemType = 'Task';
  const title = '[AI后端] 出院通知单增加日间手术患者标志数据';
  const description = '[AI-CODING-PLUS] [AI后端] 出院通知单增加日间手术患者标志数据';

  
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
      description: description,
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
