#!/usr/bin/env node
/**
 * 创建 TFS 任务
 */

import { TFSClient } from './tfs-client.mjs';

async function main() {
  if (process.argv.length < 6) {
    console.log('用法: node create-task.mjs <集合名> <项目名> <父需求ID> <任务类型> <标题> [描述] [分配给]');
    console.log('');
    console.log('示例: node create-task.mjs WINNING-6.0 WiNEX-Inpatient-2 1538495 Task "[AI后端] 出院通知单增加日间手术患者标志数据"');
    process.exit(1);
  }

  const collectionName = process.argv[2];
  const projectName = process.argv[3];
  const parentId = process.argv[4];
  const workItemType = process.argv[5];
  const title = process.argv[6];
  const description = process.argv[7] || '';
  const assignedTo = process.argv[8] || '';

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
      assignedTo: assignedTo,
      parentId: parseInt(parentId)
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
