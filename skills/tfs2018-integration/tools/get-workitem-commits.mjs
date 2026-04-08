#!/usr/bin/env node
/**
 * 获取工作项关联的代码提交（使用仓库缓存）
 * 用法: node get-workitem-commits.mjs <工作项ID> [项目名称]
 */
import TFSClient from './tfs-client.mjs';
import fs from 'fs';
import path, { dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

function getReposCache() {
  const cacheFile = path.join(__dirname, '../config/repos-cache.json');

  if (!fs.existsSync(cacheFile)) {
    console.error('仓库缓存不存在，请先运行: node tools/get-repos-cache.mjs');
    process.exit(1);
  }

  return JSON.parse(fs.readFileSync(cacheFile, 'utf8'));
}

async function getCommitsForWorkItem(workItemId, projectName) {
  const client = new TFSClient();

  // 如果没有指定项目，先从工作项获取项目信息
  if (!projectName) {
    const workItem = await client.getWorkItem(workItemId);
    projectName = workItem.fields['System.TeamProject'];
  }

  console.log(`\n查询工作项 ${workItemId} 在项目 "${projectName}" 中的代码提交...`);

  // 获取仓库缓存
  const cache = getReposCache();
  const repos = Object.values(cache.repositories).filter(r => r.project === projectName);

  if (repos.length === 0) {
    console.error(`\n项目 "${projectName}" 没有找到仓库`);
    console.error('请运行以下命令更新仓库缓存:');
    console.error(`  node tools/get-repos-cache.mjs`);
    return [];
  }

  console.log(`项目有 ${repos.length} 个仓库 (使用缓存)\n`);

  // 创建仓库ID到仓库信息的映射
  const repoMap = {};
  for (const repo of repos) {
    repoMap[repo.id] = repo;
  }

  // 获取最近的提交（一年内）
  console.log('查询最近一年的提交...\n');

  try {
    // 先查询一个仓库获取提交总数估算
    const firstRepo = repos[0];
    const commits = await client.getCommits(firstRepo.id, projectName, 500, 365);

    // 筛选关联到该工作项的提交
    const relatedCommits = commits.filter(commit =>
      commit.workItems && commit.workItems.some(wi => wi.id === workItemId)
    );

    console.log(`在仓库 "${firstRepo.name}" 中找到 ${relatedCommits.length} 个关联提交\n`);

    if (relatedCommits.length > 0) {
      for (const commit of relatedCommits) {
        const shortId = commit.commitId.substring(0, 8);
        const author = commit.author?.displayName || commit.author?.name || '未知';
        const date = new Date(commit.author?.date || commit.commitDate).toLocaleString('zh-CN');
        const comment = commit.comment || '<无评论>';

        console.log(`========== 提交 ${shortId} ==========`);
        console.log(`仓库: ${firstRepo.name}`);
        console.log(`作者: ${author} | 日期: ${date}`);
        console.log(`说明: ${comment}`);

        // 变更文件
        if (commit.changes && commit.changes.length > 0) {
          console.log(`\n变更文件 (${commit.changes.length} 个):`);
          commit.changes.forEach(change => {
            const changeType = change.changeType;
            const path = change.item?.path || 'unknown';
            console.log(`  [${changeType}] ${path}`);
          });
        }
        console.log('');
      }

      console.log('========== 汇总 ==========');
      console.log(`总计: ${relatedCommits.length} 个提交\n`);
      return relatedCommits;
    }

    console.log('\n========== 结果 ==========');
    console.log(`未找到工作项 ${workItemId} 关联的代码提交\n`);
    console.log('可能原因:');
    console.log('  1. 该工作项没有关联代码提交');
    console.log('  2. 代码提交不在最近的一年内');
    console.log('  3. 仓库缓存可能过期，请运行: node tools/get-repos-cache.mjs');
    return [];

  } catch (error) {
    console.error(`\n查询提交时出错: ${error.message}\n`);
    console.log('建议:');
    console.log('  1. 检查网络连接');
    console.log('  2. 更新仓库缓存: node tools/get-repos-cache.mjs');
    return [];
  }
}

// 执行查询
const workItemId = parseInt(process.argv[2]);
const projectName = process.argv[3];

if (!workItemId) {
  console.error('请提供工作项 ID');
  console.log('用法: node get-workitem-commits.mjs <工作项ID> [项目名称]');
  process.exit(1);
}

await getCommitsForWorkItem(workItemId, projectName);
